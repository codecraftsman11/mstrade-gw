from __future__ import annotations
from copy import deepcopy
from typing import Optional, Tuple, TYPE_CHECKING
from mst_gateway.calculator.binance import BinanceFinFactory
from mst_gateway.connector.api.types import LeverageType, OrderSchema
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.connector.api.stocks.binance.var import BinancePositionSideMode
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import BinanceSerializer


if TYPE_CHECKING:
    from ... import BinanceWssApi


class BinancePositionSerializer(BinanceSerializer):
    subscription = 'position'

    def __init__(self, wss_api: BinanceWssApi):
        super().__init__(wss_api)
        self.position_state = wss_api.partial_state_data.get(self.subscription, {}).get('position_state', {})
        self.exchange_rates = wss_api.partial_state_data.get(self.subscription, {}).get('exchange_rates', {})
        self._item_symbol = None

    @property
    def _initialized(self) -> bool:
        return bool(self.subscription in self._wss_api.subscriptions)

    @staticmethod
    def get_position_state(positions_state: dict, symbol: str) -> dict:
        return positions_state.get(symbol.lower(), {})

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if self._initialized:
            self._item_symbol = item.get('s', '').lower()
            if self._item_symbol:
                return bool(self.position_state.get(self._item_symbol))
        return False

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(self._item_symbol)) is None:
                return None
        symbol_position_state = self.get_position_state(self.position_state, self._item_symbol)
        if self._wss_api.schema == OrderSchema.exchange:
            return utils.load_exchange_position_ws_data(item, symbol_position_state, state_data, self.exchange_rates)
        if self._wss_api.schema == OrderSchema.margin2:
            return utils.load_margin2_position_ws_data(item, symbol_position_state, state_data, self.exchange_rates)
        return None


class BinanceFuturesPositionSerializer(BinancePositionSerializer):

    def __init__(self, wss_api: BinanceWssApi):
        super().__init__(wss_api)
        self.leverage_brackets = wss_api.partial_state_data.get(self.subscription, {}).get('leverage_brackets', {})

    def _get_wallet_asset(self, position: dict, default: str) -> str:
        return position.get('ma', default).lower()

    def _prefetch(self, message: dict) -> None:
        if not self._initialized:
            return None
        table = message.get('table')
        if table == 'markPriceUpdate':
            for item in message.get('data', []):
                if symbol := item.get('s'):
                    self.update_positions_state(
                        symbol,
                        mark_price=utils.to_float(item.get('p')),
                        action='update'
                    )
        if table == 'ACCOUNT_UPDATE':
            for item in message.get('data', []):
                _balances = {}
                for balance in item['a'].get('B', []):
                    _balances.setdefault(
                        balance['a'].lower(),
                        {
                            'cross_wallet_balance': utils.to_float(balance['cw'])
                        }
                    )
                for position in item['a'].get('P', []):
                    if (symbol := position.get('s')) and position.get('ps') == BinancePositionSideMode.BOTH:
                        _wallet_asset = self._get_wallet_asset(position, '')
                        volume = utils.to_float(position.get('pa'))
                        side = utils.load_position_side_by_volume(volume)
                        entry_price = utils.to_float(position.get('ep'))
                        unrealised_pnl = utils.to_float(position.get('up'))
                        mark_price = BinanceFinFactory.calc_mark_price(
                            volume, entry_price, unrealised_pnl,
                            schema=self._wss_api.schema, symbol=symbol, side=side,
                        )
                        self.update_positions_state(
                            symbol,
                            volume=volume,
                            side=side,
                            entry_price=entry_price,
                            mark_price=mark_price,
                            unrealised_pnl=unrealised_pnl,
                            leverage_type=utils.load_ws_futures_position_leverage_type(position.get('mt')),
                            isolated_wallet_balance=utils.to_float(position.get('iw')),
                            cross_wallet_balance=_balances.get(_wallet_asset, {}).get('cross_wallet_balance'),
                            action=self.get_position_action(symbol, volume)
                        )

    def prefetch(self, message: dict) -> None:
        self._prefetch(message)
        if message.get('table') == 'ACCOUNT_CONFIG_UPDATE':
            for item in message.get('data', []):
                if symbol := item.get('ac', {}).get('s'):
                    self.update_positions_state(
                        symbol,
                        leverage=utils.to_float(item['ac'].get('l'))
                    )

    def get_position_action(self, symbol: str, volume: Optional[float]):
        action = 'update'
        try:
            state_volume = self.position_state[symbol.lower()]['volume']
            if not bool(state_volume) and bool(volume):
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
            if self._item_symbol:
                return self.is_position_exists(self._item_symbol)
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

    @staticmethod
    def split_positions_state(position_state: dict, symbol: str) -> Tuple[dict, dict]:
        positions_state = deepcopy(position_state)
        symbol_position_state = positions_state.pop(symbol.lower(), {})
        return symbol_position_state, positions_state

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        symbol = self._item_symbol.lower()
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(symbol)) is None:
                return None
        symbol_position_state, other_positions_state = self.split_positions_state(self.position_state, symbol)
        maint_margin_sum, unrealised_pnl_sum = BinanceFinFactory.calc_positions_sum(
            self._wss_api.schema,
            symbol_position_state['leverage_type'],
            other_positions_state,
            self.leverage_brackets,
        )
        entry_price = symbol_position_state['entry_price']
        mark_price = symbol_position_state['mark_price']
        volume = symbol_position_state['volume']
        side = symbol_position_state['side']
        wallet_balance = self.get_wallet_balance(
            symbol_position_state['leverage_type'],
            symbol_position_state['isolated_wallet_balance'],
            symbol_position_state['cross_wallet_balance'],
        )
        symbol_position_state['liquidation_price'] = BinanceFinFactory.calc_liquidation_price(
            entry_price=entry_price,
            mark_price=mark_price,
            volume=volume,
            side=side,
            leverage_type=symbol_position_state['leverage_type'],
            wallet_balance=wallet_balance,
            leverage_brackets=self.leverage_brackets.get(symbol, {}),
            maint_margin_sum=maint_margin_sum,
            unrealised_pnl_sum=unrealised_pnl_sum,
            schema=self._wss_api.schema, symbol=symbol
        )
        symbol_position_state['unrealised_pnl'] = BinanceFinFactory.calc_unrealised_pnl_by_side(
            entry_price, mark_price, volume, side,
            schema=self._wss_api.schema, symbol=symbol
        )
        return utils.load_futures_position_ws_data(item, symbol_position_state, state_data, self.exchange_rates)

    @staticmethod
    def get_wallet_balance(leverage_type: str, isolated_balance: float, cross_balance: float) -> Optional[float]:
        leverage_type = leverage_type.lower()
        if leverage_type == LeverageType.isolated:
            return isolated_balance
        if leverage_type == LeverageType.cross:
            return cross_balance
        return None

    def is_position_exists(self, symbol: str) -> bool:
        try:
            position = self.get_position_state(self.position_state, symbol)
            return bool(position['volume']) or position['action'] != 'update'
        except (KeyError, AttributeError):
            return False

    @staticmethod
    def prepare_position_state(symbol: str, data: dict) -> dict:
        position_state = {
            'symbol': symbol.lower(),
            'volume': data.get('volume'),
            'side': data.get('side'),
            'mark_price': data.get('mark_price', 0),
            'entry_price': data.get('entry_price', 0),
            'leverage_type': data.get('leverage_type', LeverageType.cross),
            'leverage': data.get('leverage', 20),
            'isolated_wallet_balance': data.get('isolated_wallet_balance', 0),
            'cross_wallet_balance': data.get('cross_wallet_balance', 0),
            'action': data.get('action', 'update')
        }
        return position_state

    def update_positions_state(self, symbol: str, **fields) -> None:
        symbol = symbol.lower()
        if symbol not in self.position_state:
            self.position_state[symbol] = self.prepare_position_state(symbol, fields)
            return None
        if fields.get('side') is None:
            fields.pop('side', None)
        self.position_state[symbol].update(fields)


class BinanceFuturesCoinPositionSerializer(BinanceFuturesPositionSerializer):

    def _get_wallet_asset(self, position: dict, default: str) -> str:
        if state_data := self._wss_api.get_state_data(position.get('s')):
            return state_data['pair'][0].lower()
        return default

    def prefetch(self, message: dict) -> None:
        self._prefetch(message)
        if message.get('table') == self.subscription:
            for item in message.get('data', []):
                if symbol := item.get('symbol'):
                    volume = item.get('volume')
                    self.update_positions_state(
                        symbol,
                        volume=volume,
                        side=item.get('side'),
                        entry_price=item.get('entry_price'),
                        mark_price=item.get('mark_price'),
                        leverage=item.get('leverage'),
                        leverage_type=item.get('leverage_type'),
                        unrealised_pnl=item.get('unrealised_pnl'),
                        liquidation_price=item.get('liquidation_price'),
                        action=self.get_position_action(symbol, volume)
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
            symbol = self._item_symbol
            state_data = None
            if self._wss_api.register_state:
                if (state_data := self._wss_api.get_state_data(symbol)) is None:
                    return None
            symbol_position_state = self.get_position_state(self.position_state, symbol)
            return utils.load_futures_position_ws_data(item, symbol_position_state, state_data, self.exchange_rates)
        return await super()._load_data(message, item)
