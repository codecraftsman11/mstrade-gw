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
    def calc_liquidation_price(cls, side: int, leverage_type: str, entry_price: float, **kwargs) -> Optional[float]:
        volume = kwargs.pop('volume', None)
        mark_price = kwargs.pop('mark_price', None)
        contract_size = kwargs.get('contract_size')
        notional_value = cls.calc_notional_value(volume, mark_price, **kwargs)
        wallet_balance = kwargs.get('wallet_balance')
        maint_margin_sum = kwargs.get('maint_margin_sum')
        unrealised_pnl_sum = kwargs.get('unrealised_pnl_sum')
        maint_margin_rate, maint_amount = cls.filter_leverage_brackets(
            kwargs.get('leverage_brackets'), schema=kwargs.get('schema'),
            volume=volume, notional_value=notional_value,
        )
        try:
            quantity = abs(volume)
            direction = cls.direction_by_side(side)
            if cls._is_margin_coin(**kwargs):
                liquidation_price = (quantity * maint_margin_rate + direction * quantity) / (
                    (wallet_balance - maint_margin_sum + unrealised_pnl_sum + maint_amount) / (
                        contract_size + direction *
                        quantity / entry_price
                    )
                )
            else:
                liquidation_price = (
                    wallet_balance - maint_margin_sum + unrealised_pnl_sum +
                    maint_amount - direction * quantity * entry_price
                ) / (quantity * maint_margin_rate - direction * quantity)
        except (TypeError, ZeroDivisionError):
            liquidation_price = None
        if liquidation_price is not None and liquidation_price < 0:
            liquidation_price = None
        return liquidation_price

    @classmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        result = round(quantity / (wallet_balance * 100 * entry_price) * 100**2, 8)
        return result

    @classmethod
    def filter_leverage_brackets(cls, leverage_brackets: list, **kwargs) -> tuple:
        maint_margin_rate = None
        maint_amount = None
        if cls._is_margin_coin(**kwargs):
            _prefix = 'qty'
            _value = kwargs.get('volume')
        else:
            _prefix = 'notional'
            _value = kwargs.get('notional_value')
        for lb in leverage_brackets:
            if _value is not None and lb[f"{_prefix}_floor"] <= abs(_value) < lb[f"{_prefix}_cap"]:
                maint_margin_rate = lb['maint_margin_ratio']
                maint_amount = lb['cum']
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
    def calc_notional_value(cls, volume: float, mark_price: float, **kwargs) -> Optional[float]:
        try:
            quantity = abs(volume)
            if cls._is_margin_coin(**kwargs):
                contract_size = kwargs.get('contract_size')
                return quantity * contract_size / mark_price
            return quantity * mark_price
        except (TypeError, ZeroDivisionError):
            return None

    @classmethod
    def calc_maint_margin(cls, volume: float, mark_price: float, maint_amount: float, maint_margin_rate: float,
                          **kwargs) -> Optional[float]:
        try:
            if cls._is_margin_coin(**kwargs):
                contract_size = kwargs.get('contract_size')
                return abs(volume) * contract_size * (maint_margin_rate / mark_price) - maint_amount
            return cls.calc_notional_value(volume, mark_price) * maint_margin_rate - maint_amount
        except (TypeError, ZeroDivisionError):
            return None

    @classmethod
    def calc_positions_sum(
        cls, schema: str, leverage_type: str, positions_state: dict, leverage_brackets: dict, contract_size: float
    ) -> Tuple[float, float]:
        maint_margin_sum = 0.0
        unrealised_pnl_sum = 0.0
        if leverage_type.lower() == api.LeverageType.cross:
            for symbol, position_data in positions_state.items():
                if not position_data['volume'] or not position_data['side']:
                    continue
                volume = position_data['volume']
                mark_price = position_data['mark_price']
                notional_value = cls.calc_notional_value(
                    volume, mark_price,
                    schema=schema, symbol=symbol,
                )
                maint_margin_rate, maint_amount = cls.filter_leverage_brackets(
                    leverage_brackets.get(symbol, {}), schema=schema,
                    volume=volume, notional_value=notional_value,
                )
                if maint_margin := cls.calc_maint_margin(
                    volume, mark_price, maint_amount, maint_margin_rate,
                    schema=schema, symbol=symbol, contract_size=contract_size
                ):
                    maint_margin_sum += maint_margin
                if unrealized_pnl := cls.calc_unrealised_pnl_by_side(
                    position_data['entry_price'], mark_price, volume, position_data['side'],
                    schema=schema, symbol=symbol, contract_size=contract_size
                ):
                    unrealised_pnl_sum += unrealized_pnl
        return maint_margin_sum, unrealised_pnl_sum

    @classmethod
    def calc_unrealised_pnl_by_side(cls, entry_price: float, mark_price: float, volume: float, side: int,
                                    **kwargs) -> Optional[float]:
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
