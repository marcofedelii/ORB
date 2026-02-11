from __future__ import annotations

import os
from datetime import timedelta
from typing import Optional

import pandas as pd


REQUIRED_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]
INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}


def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    # Alcuni provider espongono il timestamp sull'indice.
    if isinstance(data.index, pd.DatetimeIndex):
        index_name = data.index.name or "datetime"
        data = data.reset_index().rename(columns={index_name: "datetime"})

    data.columns = [str(c).lower() for c in data.columns]

    col_map = {
        "date": "datetime",
        "timestamp": "datetime",
        "adjclose": "close",
    }
    data = data.rename(columns=col_map)

    missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]
    if missing:
        raise ValueError(f"Dati OHLCV incompleti. Colonne mancanti: {missing}")

    data = data[REQUIRED_COLUMNS].copy()
    data["datetime"] = pd.to_datetime(data["datetime"], utc=True, errors="coerce")
    data = data.dropna(subset=["datetime"])
    data = data.sort_values("datetime").drop_duplicates(subset=["datetime"])
    return data.reset_index(drop=True)


def _adjust_intraday_window(start_date: str, end_date: str, interval: str) -> tuple[str, str]:
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)

    if interval.lower() in INTRADAY_INTERVALS:
        min_start = end_ts - timedelta(days=59)
        if start_ts < min_start:
            start_ts = min_start

    return start_ts.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d")


def load_from_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV non trovato: {path}")
    df = pd.read_csv(path)
    return _normalize_ohlcv(df)


def fetch_from_openbb(symbol: str, start_date: str, end_date: str, interval: str = "5m") -> pd.DataFrame:
    try:
        from openbb import obb
    except Exception as exc:
        raise ImportError("OpenBB non disponibile nell'ambiente.") from exc

    q_start, q_end = _adjust_intraday_window(start_date=start_date, end_date=end_date, interval=interval)

    result = obb.equity.price.historical(
        symbol,
        start_date=q_start,
        end_date=q_end,
        interval=interval,
        provider="yfinance",
    )

    if hasattr(result, "to_df"):
        raw_df = result.to_df()
    else:
        raw_df = pd.DataFrame(result)

    return _normalize_ohlcv(raw_df)


def get_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str,
    csv_path: Optional[str] = None,
    save_csv: bool = True,
) -> pd.DataFrame:
    symbols = [symbol]
    if symbol.upper() == "DJI":
        symbols.extend(["^DJI", "DIA"])

    last_error: Optional[Exception] = None
    for sym in symbols:
        try:
            df = fetch_from_openbb(symbol=sym, start_date=start_date, end_date=end_date, interval=interval)
            if csv_path and save_csv:
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)
                df.to_csv(csv_path, index=False)
            return df
        except Exception as exc:
            last_error = exc

    if csv_path:
        try:
            return load_from_csv(csv_path)
        except Exception as exc:
            if last_error is not None:
                raise RuntimeError(
                    f"Download OpenBB fallito ({last_error}). Fallback CSV fallito ({exc})."
                ) from exc
            raise

    if last_error is not None:
        raise last_error

    raise RuntimeError("Impossibile ottenere dati da OpenBB/CSV.")
