from __future__ import annotations
from copy import deepcopy
from typing import Optional, Tuple, TYPE_CHECKING
from mst_gateway.calculator.binance import BinanceFinFactory
from mst_gateway.connector.api.types import LeverageType
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.connector.api.stocks.binance.var import BinancePositionSideMode
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import BinanceSerializer


if TYPE_CHECKING:
    from ... import BinanceWssApi


class BinanceFuturesPositionSerializer(BinanceSerializer):
    subscription = "position"

    def __init__(self, wss_api: BinanceWssApi):
        super().__init__(wss_api)
        self._initialized = bool(self.subscription in self._wss_api.subscriptions)
        self._position_state = wss_api.partial_state_data[self.subscription].get('position_state', {})
        self._leverage_brackets_state = wss_api.partial_state_data[self.subscription].get('leverage_brackets', {})
        self._item_symbol = None

    def prefetch(self, message: dict) -> None:
        if not self._initialized:
            return None
        table = message.get("table")
        if table == "markPriceUpdate":
            for item in message.get("data", []):
                if symbol := item.get("s"):
                    self.update_positions_state(
                        symbol,
                        mark_price=utils.to_float(item.get('p')),
                        action='update'
                    )
        if table == "ACCOUNT_UPDATE":
            for item in message.get("data", []):
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
                        _wallet_asset = position.get('ma', '').lower()
                        volume = utils.to_float(position.get('pa'))
                        entry_price = utils.to_float(position.get('ep'))
                        unrealised_pnl = utils.to_float(position.get('up'))
                        self.update_positions_state(
                            symbol,
                            volume=volume,
                            side=utils.load_position_side_by_volume(volume),
                            entry_price=entry_price,
                            mark_price=BinanceFinFactory.calc_mark_price(volume, entry_price, unrealised_pnl),
                            unrealised_pnl=unrealised_pnl,
                            leverage_type=utils.load_ws_futures_position_leverage_type(position.get('mt')),
                            isolated_wallet_balance=utils.to_float(position.get('iw')),
                            cross_wallet_balance=_balances.get(_wallet_asset, {}).get('cross_wallet_balance'),
                            action=self.get_position_action(symbol, volume)
                        )
        if table == "ACCOUNT_CONFIG_UPDATE":
            for item in message.get("data", []):
                if symbol := item.get("ac", {}).get("s"):
                    self.update_positions_state(
                        symbol,
                        leverage=utils.to_float(item["ac"].get("l"))
                    )

    def get_position_action(self, symbol: str, volume: Optional[float]):
        action = 'update'
        try:
            state_volume = self._position_state[symbol.lower()]['volume']
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
            if table == "ACCOUNT_UPDATE":
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

    def split_positions_state(self, symbol: str) -> Tuple[dict, dict]:
        positions_state = deepcopy(self._position_state)
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

        symbol_position_state, positions_state = self.split_positions_state(symbol)
        other_positions_maint_margin, other_positions_unrealised_pnl = self.calc_other_positions_sum(
            symbol_position_state['leverage_type'], self._leverage_brackets_state, positions_state)

        entry_price = symbol_position_state['entry_price']
        mark_price = symbol_position_state['mark_price']
        volume = symbol_position_state['volume']
        side = symbol_position_state['side']
        position_margin = self.position_margin(
            symbol_position_state['leverage_type'],
            symbol_position_state['isolated_wallet_balance'],
            symbol_position_state['cross_wallet_balance']
        )

        symbol_position_state['liquidation_price'] = self.calc_liquidation_price(
            entry_price=entry_price,
            mark_price=mark_price,
            volume=volume,
            side=side,
            leverage_type=symbol_position_state['leverage_type'],
            position_margin=position_margin,
            leverage_brackets=self._leverage_brackets_state.get(symbol, {}),
            other_positions_maint_margin=other_positions_maint_margin,
            other_positions_unrealised_pnl=other_positions_unrealised_pnl
        )
        symbol_position_state['unrealised_pnl'] = BinanceFinFactory.calc_unrealised_pnl_by_side(
            entry_price, mark_price, volume, side
        )
        return utils.load_futures_position_ws_data(item, symbol_position_state, state_data)

    @staticmethod
    def calc_liquidation_price(entry_price, mark_price, volume, side, leverage_type, position_margin,
                               leverage_brackets, other_positions_maint_margin,
                               other_positions_unrealised_pnl) -> Optional[float]:
        liquidation_price = None
        if None not in (side, mark_price, entry_price, position_margin):
            params = {
                'volume': volume,
                'mark_price': mark_price,
                'position_margin': position_margin,
                'unrealised_pnl': other_positions_unrealised_pnl,
                'leverage_brackets': leverage_brackets,
            }
            direction = BinanceFinFactory.direction_by_side(side)
            if leverage_type == LeverageType.isolated:
                liquidation_price = BinanceFinFactory.calc_liquidation_isolated_price(
                    entry_price, other_positions_maint_margin, direction, **params
                )
            if leverage_type == LeverageType.cross:
                liquidation_price = BinanceFinFactory.calc_liquidation_cross_price(
                    entry_price, other_positions_maint_margin, direction, **params
                )
        if liquidation_price and liquidation_price < 0:
            liquidation_price = None
        return liquidation_price

    @staticmethod
    def calc_other_positions_sum(leverage_type: str, leverage_brackets_state: dict,
                                 other_positions_state: dict) -> Tuple[float, float]:
        maint_margin_sum = 0.0
        unrealised_pnl_sum = 0.0
        if leverage_type == LeverageType.cross:
            for position_symbol, position_data in other_positions_state.items():
                if not position_data['volume'] or not position_data['side']:
                    continue
                mark_price = position_data['mark_price']
                leverage_bracket = leverage_brackets_state.get(position_symbol, {})
                if mark_price is not None and leverage_bracket:
                    volume = abs(position_data['volume'])
                    notional_value = volume * mark_price
                    maint_margin_rate, maint_amount = BinanceFinFactory.filter_leverage_brackets(
                        leverage_bracket, notional_value
                    )
                    if maint_margin_rate is not None and maint_amount is not None:
                        maint_margin = notional_value * maint_margin_rate - maint_amount
                        maint_margin_sum += maint_margin

                    unrealized_pnl = BinanceFinFactory.calc_unrealised_pnl_by_side(
                        position_data['entry_price'], mark_price, volume, position_data['side']
                    )
                    unrealised_pnl_sum += unrealized_pnl
        return maint_margin_sum, unrealised_pnl_sum

    @staticmethod
    def position_margin(leverage_type: str, isolated_balance: float, cross_balance: float) -> Optional[float]:
        if leverage_type == LeverageType.isolated:
            return isolated_balance
        if leverage_type == LeverageType.cross:
            return cross_balance
        return None

    def is_position_exists(self, symbol: str) -> bool:
        try:
            position = self._position_state[symbol.lower()]
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
        if symbol not in self._position_state:
            self._position_state[symbol] = self.prepare_position_state(symbol, fields)
            return None
        if fields.get('side') is None:
            fields.pop('side', None)
        self._position_state[symbol].update(fields)
