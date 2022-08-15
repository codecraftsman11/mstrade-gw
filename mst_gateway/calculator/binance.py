from typing import Optional, Tuple, Union
from mst_gateway.calculator import FinFactory
from mst_gateway.connector import api


class BinanceFinFactory(FinFactory):

    @classmethod
    def _is_margin_coin(cls, **kwargs) -> bool:
        return kwargs.get('schema', '').lower() == api.OrderSchema.margin_coin

    @classmethod
    def calc_face_price(cls, price: float, **kwargs) -> Optional[float]:
        if cls._is_margin_coin(**kwargs):
            if contract_size := kwargs.get('contract_size'):
                try:
                    return round(contract_size / price, 8)
                except (TypeError, ZeroDivisionError):
                    return None
        return price

    @classmethod
    def calc_price(cls, face_price: float, **kwargs) -> Optional[float]:
        if cls._is_margin_coin(**kwargs):
            if contract_size := kwargs.get('contract_size'):
                try:
                    return round(contract_size / face_price, 8)
                except (TypeError, ZeroDivisionError):
                    return None
        return face_price

    @classmethod
    def _get_leverage_kwargs(cls, schema: str, volume: float, mark_price: float, contract_size: int) -> dict:
        if cls._is_margin_coin(schema=schema):
            return {'volume': volume}
        return {
            'notional_value': cls._calc_notional_value(schema, volume, mark_price, contract_size)
        }

    @classmethod
    def _calc_balance_diff(cls, wallet_balance: float, maint_margin_sum: float, unrealised_pnl_sum: float,
                           both_maint_amount: float, long_maint_amount: float, short_maint_amount: float) -> float:
        try:
            return wallet_balance - maint_margin_sum + unrealised_pnl_sum + both_maint_amount + long_maint_amount + \
                   short_maint_amount
        except TypeError:
            return 0

    @classmethod
    def _calc_volume_sum(cls, both_abs_volume: float, both_maint_margin_rate: float, long_abs_volume: float,
                         long_maint_margin_rate: float, short_abs_volume: float,
                         short_maint_margin_rate: float) -> float:
        try:
            return both_abs_volume * both_maint_margin_rate + long_abs_volume * long_maint_margin_rate + \
                   short_abs_volume * short_maint_margin_rate
        except TypeError:
            return 0

    @classmethod
    def _volume_div_by_price(cls, volume: float, entry_price: float) -> float:
        try:
            return volume / entry_price
        except (TypeError, ZeroDivisionError):
            return 0

    @classmethod
    def _calc_quantity(cls, volume: float, entry_price: float) -> float:
        try:
            return volume * entry_price
        except TypeError:
            return 0

    @classmethod
    def _get_volume_and_price(cls, symbol: str, position_side: str, volume: float, entry_price: float,
                              leverage_type: str, positions_state: dict) -> tuple:
        from mst_gateway.connector.api.stocks.binance import utils

        both_volume = volume
        long_volume = 0
        short_volume = 0
        both_entry_price = entry_price
        long_entry_price = 0
        short_entry_price = 0
        if utils.is_hedge_mode(positions_state):
            symbol = symbol.lower()
            position_side = position_side.lower()
            leverage_type = leverage_type.lower()
            both_position = positions_state.get(symbol, {}).get(api.PositionSide.both, {})
            long_position = positions_state.get(symbol, {}).get(api.PositionSide.long, {})
            short_position = positions_state.get(symbol, {}).get(api.PositionSide.short, {})
            both_volume = both_position.get('volume', 0)
            long_volume = long_position.get('volume', 0)
            short_volume = short_position.get('volume', 0)
            both_entry_price = both_position.get('entry_price', 0)
            long_entry_price = long_position.get('entry_price', 0)
            short_entry_price = short_position.get('entry_price', 0)
            if position_side == api.PositionSide.both:
                both_volume = volume
                both_entry_price = entry_price
            elif position_side == api.PositionSide.long:
                long_volume = volume
                long_entry_price = entry_price
            else:
                short_volume = volume
                short_entry_price = entry_price
            if leverage_type == api.LeverageType.isolated and position_side == api.PositionSide.long:
                short_volume = 0
            if leverage_type == api.LeverageType.isolated and position_side == api.PositionSide.short:
                long_volume = 0
        return both_volume, both_entry_price, long_volume, long_entry_price, short_volume, short_entry_price

    @classmethod
    def calc_liquidation_price(cls, side: int, volume: float, entry_price: float, leverage_type: str,
                               wallet_balance: float, **kwargs) -> Optional[float]:
        # https://www.binance.com/en/support/faq/ceccfcfb4e3a45e3b48b0b1bb1a8ae46
        # https://www.binance.com/en/support/faq/b3c689c1f50a44cabb3a84e663b81d93
        from mst_gateway.connector.api.stocks.binance import utils

        schema = kwargs.get('schema', '')
        symbol = kwargs.get('symbol', '').lower()
        position_side = kwargs.get('position_side', '').lower()
        positions_state = kwargs.get('positions_state', {})
        leverage_brackets = kwargs.get('leverage_brackets', {})
        if position_side in (api.PositionSide.long, api.PositionSide.short):
            side = positions_state.get(symbol, {}).get(api.PositionSide.both, {}).get('side')
        both_direction = cls.direction_by_side(side)
        (both_volume, both_entry_price,
         long_volume, long_entry_price,
         short_volume, short_entry_price) = cls._get_volume_and_price(symbol, position_side, volume, entry_price,
                                                                      leverage_type, positions_state)
        mark_price = kwargs.get('mark_price')

        current_position, symbol_positions, other_positions = utils.split_positions_state(
            positions_state, symbol, position_side
        )
        maint_margin_sum, unrealised_pnl_sum = cls._calc_positions_sum(schema, leverage_type, other_positions,
                                                                       leverage_brackets)
        symbol_leverage_brackets = leverage_brackets.get(symbol, [])
        contract_size = current_position.get('contract_size')
        kwargs = cls._get_leverage_kwargs(schema, both_volume, mark_price, contract_size)
        both_maint_margin_rate, both_maint_amount = cls._filter_leverage_brackets(schema, symbol_leverage_brackets,
                                                                                  **kwargs)
        kwargs = cls._get_leverage_kwargs(schema, long_volume, mark_price, contract_size)
        long_maint_margin_rate, long_maint_amount = cls._filter_leverage_brackets(schema, symbol_leverage_brackets,
                                                                                  **kwargs)
        kwargs = cls._get_leverage_kwargs(schema, short_volume, mark_price, contract_size)
        short_maint_margin_rate, short_maint_amount = cls._filter_leverage_brackets(schema, symbol_leverage_brackets,
                                                                                    **kwargs)
        try:
            both_abs_volume = abs(both_volume)
            long_abs_volume = abs(long_volume)
            short_abs_volume = abs(short_volume)
            if cls._is_margin_coin(schema=schema):
                liquidation_price = (
                    cls._calc_volume_sum(both_abs_volume, both_maint_margin_rate, long_abs_volume,
                                         long_maint_margin_rate, short_abs_volume, short_maint_margin_rate) +
                    both_direction * both_abs_volume + long_abs_volume - short_abs_volume
                ) / (
                    cls._calc_balance_diff(wallet_balance, maint_margin_sum, unrealised_pnl_sum,
                                           both_maint_amount, long_maint_amount, short_maint_amount) / contract_size +
                    both_direction * cls._volume_div_by_price(both_abs_volume, both_entry_price) +
                    cls._volume_div_by_price(long_abs_volume, long_entry_price) -
                    cls._volume_div_by_price(short_abs_volume, short_entry_price)
                )
            else:
                liquidation_price = (
                    cls._calc_balance_diff(wallet_balance, maint_margin_sum, unrealised_pnl_sum,
                                           both_maint_amount, long_maint_amount, short_maint_amount) -
                    both_direction * cls._calc_quantity(both_abs_volume, both_entry_price) -
                    cls._calc_quantity(long_abs_volume, long_entry_price) -
                    cls._calc_quantity(short_abs_volume, short_entry_price)

                ) / (
                    cls._calc_volume_sum(both_abs_volume, both_maint_margin_rate, long_abs_volume,
                                         long_maint_margin_rate, short_abs_volume, short_maint_margin_rate) -
                    both_direction * both_abs_volume - long_abs_volume + short_abs_volume
                )
            if liquidation_price <= 0:
                liquidation_price = None
        except (TypeError, ZeroDivisionError):
            liquidation_price = None
        return liquidation_price

    @classmethod
    def calc_leverage_level(cls, abs_volume: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        result = round(abs_volume / (wallet_balance * 100 * entry_price) * 100**2, 8)
        return result

    @classmethod
    def _filter_leverage_brackets(cls, schema: str, leverage_brackets: list, **kwargs) -> Tuple[float, float]:
        maint_margin_rate = 0
        maint_amount = 0
        if cls._is_margin_coin(schema=schema):
            _prefix = 'qty'
            _value = kwargs.get('volume')
        else:
            _prefix = 'notional'
            _value = kwargs.get('notional_value')
        for lb in leverage_brackets:
            if _value is not None and lb[f"{_prefix}_floor"] <= abs(_value) < lb[f"{_prefix}_cap"]:
                return lb['maint_margin_ratio'], lb['cum']
        return maint_margin_rate, maint_amount

    @classmethod
    def direction_by_side(cls, side: int) -> int:
        if side == api.BUY:
            return 1
        return -1

    @classmethod
    def side_by_direction(cls, direction: int) -> int:
        if direction == 1:
            return api.BUY
        return api.SELL

    @classmethod
    def _calc_notional_value(cls, schema: str, volume: float, mark_price: float,
                             contract_size: Optional[int]) -> Optional[float]:
        try:
            abs_volume = abs(volume)
            if cls._is_margin_coin(schema=schema):
                return abs_volume * contract_size / mark_price
            return abs_volume * mark_price
        except (TypeError, ZeroDivisionError):
            return 0

    @classmethod
    def _calc_maint_margin(cls, schema: str, volume: float, mark_price: float, maint_amount: float,
                           maint_margin_rate: float, contract_size: Optional[int]) -> Optional[float]:
        try:
            if cls._is_margin_coin(schema=schema):
                return abs(volume) * contract_size * (maint_margin_rate / mark_price) - maint_amount
            return cls._calc_notional_value(schema, volume, mark_price, contract_size) * maint_margin_rate - \
                maint_amount
        except (TypeError, ZeroDivisionError):
            return 0

    @classmethod
    def _calc_positions_sum(cls, schema: str, leverage_type: str, positions_state: dict,
                            leverage_brackets: dict) -> Tuple[float, float]:
        maint_margin_sum = 0
        unrealised_pnl_sum = 0
        if leverage_type.lower() == api.LeverageType.cross:
            for symbol, position_data in positions_state.items():
                symbol_leverage_brackets = leverage_brackets.get(symbol, [])
                for position_side, position in position_data.items():
                    if not (volume := position.get('volume')) or not (side := position.get('side')):
                        continue
                    entry_price = position.get('entry_price')
                    mark_price = position.get('mark_price')
                    contract_size = position.get('contract_size')
                    kwargs = cls._get_leverage_kwargs(schema, volume, mark_price, contract_size)
                    maint_margin_rate, maint_amount = cls._filter_leverage_brackets(schema, symbol_leverage_brackets,
                                                                                    **kwargs)
                    if maint_margin := cls._calc_maint_margin(schema, volume, mark_price, maint_amount,
                                                              maint_margin_rate, contract_size):
                        maint_margin_sum += maint_margin
                    if unrealized_pnl := cls.calc_unrealised_pnl_by_side(entry_price, mark_price, volume, side,
                                                                         schema=schema, contract_size=contract_size):
                        unrealised_pnl_sum += unrealized_pnl
        return maint_margin_sum, unrealised_pnl_sum

    @classmethod
    def calc_unrealised_pnl_by_side(cls, entry_price: float, mark_price: float, volume: float, side: int,
                                    **kwargs) -> Optional[float]:
        # https://www.binance.com/en/support/faq/3a55a23768cb416fb404f06ffedde4b2
        if cls._is_margin_coin(**kwargs):
            try:
                contract_size = kwargs.get('contract_size')
                return abs(volume) * cls.direction_by_side(side) * contract_size * (1 / entry_price - 1 / mark_price)
            except (TypeError, ZeroDivisionError):
                return None
        return super().calc_unrealised_pnl_by_side(entry_price, mark_price, volume, side)

    @classmethod
    def calc_unrealised_pnl_by_direction(cls, entry_price: float, mark_price: float, volume: float, direction: int,
                                         **kwargs) -> Optional[float]:
        if cls._is_margin_coin(**kwargs):
            contract_size = kwargs.get('contract_size')
            try:
                return abs(volume) * direction * contract_size * (1 / entry_price - 1 / mark_price)
            except (TypeError, ZeroDivisionError):
                return None
        return super().calc_unrealised_pnl_by_direction(entry_price, mark_price, volume, direction)

    @classmethod
    def calc_mark_price(cls, volume: float, entry_price: float, unrealised_pnl: float, **kwargs) -> Optional[float]:
        if cls._is_margin_coin(**kwargs):
            contract_size = kwargs.get('contract_size')
            try:
                return 1 / (1 / entry_price - (
                    unrealised_pnl / (
                        abs(volume) * cls.direction_by_side(kwargs.get('side')) * contract_size
                    )
                ))
            except (TypeError, ZeroDivisionError):
                return None
        return super().calc_mark_price(volume, entry_price, unrealised_pnl)
