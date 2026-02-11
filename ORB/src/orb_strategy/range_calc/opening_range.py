from __future__ import annotations

import pandas as pd


def compute_opening_range(
    df: pd.DataFrame,
    tz: str = "America/New_York",
    range_start: str = "09:30",
    range_end: str = "10:00",
) -> pd.DataFrame:
    data = df.copy()
    data["datetime"] = pd.to_datetime(data["datetime"], utc=True)
    data = data.sort_values("datetime").reset_index(drop=True)

    local_dt = data["datetime"].dt.tz_convert(tz)
    data["session_date"] = local_dt.dt.date
    data["local_time"] = local_dt.dt.strftime("%H:%M")

    range_mask = (data["local_time"] >= range_start) & (data["local_time"] < range_end)
    orb = (
        data[range_mask]
        .groupby("session_date")
        .agg(orb_high=("high", "max"), orb_low=("low", "min"))
        .reset_index()
    )

    out = data.merge(orb, on="session_date", how="left")
    return out
