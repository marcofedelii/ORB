from __future__ import annotations

import numpy as np
import pandas as pd


def generate_orb_signals(
    df: pd.DataFrame,
    ema_period: int = 50,
    vol_sma_period: int = 20,
    volume_factor: float = 1.2,
    slope_threshold: float = 0.0,
    tz: str = "America/New_York",
    range_end: str = "10:00",
) -> pd.DataFrame:
    out = df.copy()

    ema_col = f"ema_{ema_period}"
    slope_col = f"{ema_col}_slope"
    vol_sma_col = f"vol_sma_{vol_sma_period}"

    local_dt = out["datetime"].dt.tz_convert(tz)
    out["local_time"] = local_dt.dt.strftime("%H:%M")

    after_range = out["local_time"] >= range_end
    bullish_trend = out[slope_col] > slope_threshold
    bearish_trend = out[slope_col] < -slope_threshold

    vol_confirm = out["volume"] > (volume_factor * out[vol_sma_col])

    breakout_long = out["close"] > out["orb_high"]
    breakout_short = out["close"] < out["orb_low"]

    out["signal"] = np.select(
        [after_range & bullish_trend & vol_confirm & breakout_long, after_range & bearish_trend & vol_confirm & breakout_short],
        [1, -1],
        default=0,
    )

    # Un solo ingresso per sessione: primo segnale utile.
    out["entry_signal"] = 0
    first_signal_idx = out[out["signal"] != 0].groupby("session_date").head(1).index
    out.loc[first_signal_idx, "entry_signal"] = out.loc[first_signal_idx, "signal"]

    return out
