from __future__ import annotations

import pandas as pd


def add_ema(df: pd.DataFrame, period: int = 50, price_col: str = "close") -> pd.DataFrame:
    out = df.copy()
    out[f"ema_{period}"] = out[price_col].ewm(span=period, adjust=False).mean()
    return out


def add_ema_slope(df: pd.DataFrame, ema_col: str = "ema_50", periods: int = 1) -> pd.DataFrame:
    out = df.copy()
    out[f"{ema_col}_slope"] = out[ema_col].diff(periods)
    return out


def add_volume_sma(df: pd.DataFrame, period: int = 20, volume_col: str = "volume") -> pd.DataFrame:
    out = df.copy()
    out[f"vol_sma_{period}"] = out[volume_col].rolling(period).mean()
    return out


def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    out = df.copy()
    prev_close = out["close"].shift(1)

    tr_components = pd.concat(
        [
            (out["high"] - out["low"]).abs(),
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    out[f"atr_{period}"] = tr_components.max(axis=1).rolling(period).mean()
    return out


def add_indicators(
    df: pd.DataFrame,
    ema_period: int = 50,
    vol_sma_period: int = 20,
    atr_period: int = 14,
) -> pd.DataFrame:
    out = add_ema(df, period=ema_period)
    out = add_ema_slope(out, ema_col=f"ema_{ema_period}")
    out = add_volume_sma(out, period=vol_sma_period)
    out = add_atr(out, period=atr_period)
    return out
