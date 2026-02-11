from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class RiskSetup:
    stop_loss: float
    take_profit: float
    risk_per_unit: float


def build_risk_setup(
    entry_price: float,
    side: int,
    orb_high: float,
    orb_low: float,
    atr_value: float,
    atr_buffer_mult: float,
    rr: float,
) -> RiskSetup | None:
    range_mid = (orb_high + orb_low) / 2.0

    if side == 1:
        stop_loss = float(range_mid)
        risk_per_unit = entry_price - stop_loss
        if risk_per_unit <= 0:
            return None
        take_profit = entry_price + (rr * risk_per_unit)
    else:
        stop_loss = float(range_mid)
        risk_per_unit = stop_loss - entry_price
        if risk_per_unit <= 0:
            return None
        take_profit = entry_price - (rr * risk_per_unit)

    return RiskSetup(
        stop_loss=stop_loss,
        take_profit=take_profit,
        risk_per_unit=float(risk_per_unit),
    )


def compute_position_size(equity: float, risk_pct: float, risk_per_unit: float) -> float:
    if risk_per_unit <= 0 or equity <= 0 or risk_pct <= 0:
        return 0.0
    risk_amount = equity * risk_pct
    return risk_amount / risk_per_unit
