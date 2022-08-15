from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from mst_gateway.calculator.binance import BinanceFinFactory
from mst_gateway.connector.api.types import LeverageType
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import BinanceSerializer


if TYPE_CHECKING:
    from ... import BinanceWssApi


class BinancePositionSerializer(BinanceSerializer):
    subscription = 'position'

    def __init__(self, wss_api: BinanceWssApi):
        super().__init__(wss_api)

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        return None


class BinanceMarginPositionSerializer(BinancePositionSerializer):

    def __init__(self, wss_api: BinanceWssApi):
        super().__init__(wss_api)
        self.position_state = wss_api.partial_state_data.get(self.subscription, {}).get('position_state', {})
        self.leverage_brackets = wss_api.partial_state_data.get(self.subscription, {}).get('leverage_brackets', {})
        self._item_symbol = None
        self._position_side = None

    @property
    def _initialized(self) -> bool:
        return bool(self.subscription in self._wss_api.subscriptions)

    def _get_wallet_asset(self, position: dict, default: str) -> str:
        return position.get('ma', default).lower()

    def _prefetch(self, message: dict) -> None:
        if not self._initialized:
            return None
        table = message.get('table')
        if table == 'markPriceUpdate':
            for item in message.get('data', []):
                self.update_positions_state(
                    item.get('s', ''),
                    item.get('ps', ''),
                    mark_price=utils.to_float(item.get('p')),
                    action='update'
                )
        if table == 'ACCOUNT_UPDATE':
            for item in message.get('data', []):
                _balances = {}
                for balance in item.get('a', {}).get('B', []):
                    _balances.setdefault(
                        balance.get('a', '').lower(),
                        {
                            'cross_wallet_balance': utils.to_float(balance.get('cw'))
                        }
                    )
                for position in item.get('a', {}).get('P', []):
                    symbol = position.get('s', '')
                    position_side = position.get('ps', '')
                    wallet_asset = self._get_wallet_asset(position, '')
                    volume = utils.to_float(position.get('pa'))
                    side = utils.load_position_side_by_volume(volume)
                    entry_price = utils.to_float(position.get('ep'))
                    unrealised_pnl = utils.to_float(position.get('up'))
                    if state_data := self._wss_api.get_state_data(symbol):
                        contract_size = state_data.get('extra', {}).get('face_price_data', {}).get('contract_size')
                    else:
                        contract_size = None
                    mark_price = BinanceFinFactory.calc_mark_price(
                        volume, entry_price, unrealised_pnl, schema=self._wss_api.schema,
                        side=side, contract_size=contract_size
                    )
                    self.update_positions_state(
                        symbol,
                        position_side,
                        volume=volume,
                        side=side,
                        entry_price=entry_price,
                        mark_price=mark_price,
                        unrealised_pnl=unrealised_pnl,
                        leverage_type=utils.load_ws_futures_position_leverage_type(position.get('mt')),
                        isolated_wallet_balance=utils.to_float(position.get('iw')),
                        cross_wallet_balance=_balances.get(wallet_asset, {}).get('cross_wallet_balance'),
                        action=self.get_position_action(symbol, position_side, volume)
                    )

    def prefetch(self, message: dict) -> None:
        self._prefetch(message)
        if message.get('table') == 'ACCOUNT_CONFIG_UPDATE':
            for item in message.get('data', []):
                self.update_positions_state(
                    item.get('ac', {}).get('s', ''),
                    item.get('ps', ''),
                    leverage=utils.to_float(item.get('ac', {}).get('l'))
                )

    def get_position_action(self, symbol: str, position_side: str, volume: Optional[float]):
        action = 'update'
        try:
            state_volume = self.position_state[symbol.lower()][position_side.lower()]['volume']
            if not bool(state_volume) and volume:
                action = 'create'
            elif bool(state_volume) and not bool(volume):
                action = 'delete'
            elif state_volume and volume and (
                    (state_volume > 0 > volume) or
                    (state_volume < 0 < volume)
            ):
                action = 'reverse'
        except (KeyError, IndexError, AttributeError):
            pass
        return action

    def is_item_valid(self, message: dict, item: dict) -> bool:
        table = message['table']
        if self._initialized:
            self._item_symbol = self._get_item_symbol(table, item)
            try:
                self._position_side = item.get('ps') or item.get('position_side') or item['a']['P'][0]['ps']
            except (IndexError, KeyError):
                self._position_side = None
            if self._item_symbol and self._position_side:
                return self.is_position_exists(self._item_symbol, self._position_side)
        return False

    def _get_item_symbol(self, table: str, item: dict) -> Optional[str]:
        try:
            if table == 'ACCOUNT_UPDATE':
                symbol = item['a']['P'][0]['s']
            elif table == 'ACCOUNT_CONFIG_UPDATE':
                symbol = item['ac']['s']
            elif table == 'markPriceUpdate':
                symbol = item['s']
            else:
                return None
        except (KeyError, ValueError, IndexError):
            return None
        return symbol

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        schema = self._wss_api.schema
        symbol = self._item_symbol.lower()
        position_side = self._position_side.lower()
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(symbol)) is None:
                return None
        current_position, _, _ = utils.split_positions_state(self.position_state, symbol, position_side)
        side = current_position.get('side')
        volume = current_position.get('volume')
        entry_price = current_position.get('entry_price')
        mark_price = current_position.get('mark_price')
        leverage_type = current_position.get('leverage_type')
        wallet_balance = current_position.get('cross_wallet_balance')
        if leverage_type.lower() == LeverageType.isolated:
            wallet_balance = current_position.get('isolated_wallet_balance')
        contract_size = current_position.get('contract_size')
        current_position['liquidation_price'] = BinanceFinFactory.calc_liquidation_price(
            side,
            volume,
            entry_price,
            leverage_type,
            wallet_balance,
            schema=schema,
            symbol=symbol,
            position_side=position_side,
            mark_price=mark_price,
            positions_state=self.position_state,
            leverage_brackets=self.leverage_brackets
        )
        current_position['unrealised_pnl'] = BinanceFinFactory.calc_unrealised_pnl_by_side(
            entry_price, mark_price, volume, side, schema=schema, contract_size=contract_size
        )
        return utils.load_futures_position_ws_data(item, current_position, state_data)

    def is_position_exists(self, symbol: str, position_side: str) -> bool:
        try:
            position = self.position_state.get(symbol.lower(), {}).get(position_side.lower(), {})
            return bool(position['volume']) or position['action'] != 'update'
        except (KeyError, AttributeError):
            return False

    @staticmethod
    def prepare_position_state(symbol: str, position_side: str, data: dict) -> dict:
        position_state = {
            'symbol': symbol.lower(),
            'volume': data.get('volume'),
            'side': data.get('side'),
            'position_side': position_side.lower(),
            'mark_price': data.get('mark_price', 0),
            'entry_price': data.get('entry_price', 0),
            'leverage_type': data.get('leverage_type', LeverageType.cross),
            'leverage': data.get('leverage', 20),
            'isolated_wallet_balance': data.get('isolated_wallet_balance', 0),
            'cross_wallet_balance': data.get('cross_wallet_balance', 0),
            'action': data.get('action', 'update')
        }
        return position_state

    def update_positions_state(self, symbol: str, position_side: str, **fields) -> None:
        symbol = symbol.lower()
        position_side = position_side.lower()
        if not self.position_state.setdefault(symbol, {}).get(position_side):
            self.position_state.setdefault(symbol, {})[position_side] = self.prepare_position_state(
                symbol, position_side, fields
            )
            return None
        if fields.get('side') is None:
            fields.pop('side', None)
        self.position_state[symbol][position_side].update(fields)


class BinanceMarginCoinPositionSerializer(BinanceMarginPositionSerializer):

    def _get_wallet_asset(self, position: dict, default: str) -> str:
        if state_data := self._wss_api.get_state_data(position.get('s', default).lower()):
            return state_data['pair'][0].lower()
        return default

    def prefetch(self, message: dict) -> None:
        self._prefetch(message)
        if message.get('table') == self.subscription:
            for item in message.get('data', []):
                symbol = item.get('symbol', '')
                position_side = item.get('position_side', '')
                volume = item.get('volume')
                self.update_positions_state(
                    symbol,
                    position_side,
                    volume=volume,
                    side=item.get('side'),
                    entry_price=item.get('entry_price'),
                    mark_price=item.get('mark_price'),
                    leverage=item.get('leverage'),
                    leverage_type=item.get('leverage_type'),
                    unrealised_pnl=item.get('unrealised_pnl'),
                    liquidation_price=item.get('liquidation_price'),
                    action=self.get_position_action(symbol, position_side, volume)
                )

    def _get_item_symbol(self, table: str, item: dict) -> Optional[str]:
        if table == self.subscription:
            try:
                symbol = item['symbol']
            except KeyError:
                symbol = None
        else:
            symbol = super()._get_item_symbol(table, item)
        return symbol

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if message.get('table') == self.subscription:
            if not self.is_item_valid(message, item):
                return None
            symbol = self._item_symbol.lower()
            position_side = self._position_side.lower()
            state_data = None
            if self._wss_api.register_state:
                if (state_data := self._wss_api.get_state_data(symbol)) is None:
                    return None
            current_position, _, _ = utils.split_positions_state(self.position_state, symbol, position_side)
            return utils.load_futures_position_ws_data(item, current_position, state_data)
        return await super()._load_data(message, item)
