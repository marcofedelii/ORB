from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd

from orb_strategy.risk_management.sizer import build_risk_setup, compute_position_size


@dataclass
class Trade:
    session_date: object
    side: int
    entry_time: pd.Timestamp
    entry_price: float
    stop_loss: float
    take_profit: float
    size: float
    risk_amount: float
    exit_time: pd.Timestamp
    exit_price: float
    exit_reason: str
    pnl: float
    ret_pct: float
    equity_before: float
    equity_after: float


def _check_exit(row: pd.Series, side: int, stop_loss: float, take_profit: float) -> tuple[bool, float, str]:
    high = float(row["high"])
    low = float(row["low"])

    if side == 1:
        sl_hit = low <= stop_loss
        tp_hit = high >= take_profit
        if sl_hit and tp_hit:
            return True, stop_loss, "sl_same_bar"
        if sl_hit:
            return True, stop_loss, "sl"
        if tp_hit:
            return True, take_profit, "tp"
    else:
        sl_hit = high >= stop_loss
        tp_hit = low <= take_profit
        if sl_hit and tp_hit:
            return True, stop_loss, "sl_same_bar"
        if sl_hit:
            return True, stop_loss, "sl"
        if tp_hit:
            return True, take_profit, "tp"

    return False, 0.0, ""


def run_backtest(
    df: pd.DataFrame,
    tz: str = "America/New_York",
    session_end: str = "16:00",
    atr_period: int = 14,
    atr_buffer_mult: float = 1.0,
    fixed_rr: float = 1.5,
    risk_per_trade_pct: float = 0.004,
    initial_equity: float = 100000.0,
) -> pd.DataFrame:
    trades: List[Trade] = []
    equity = float(initial_equity)

    atr_col = f"atr_{atr_period}"

    for session_date, day in df.groupby("session_date"):
        day = day.sort_values("datetime").reset_index(drop=True)
        entries = day[day["entry_signal"] != 0]
        if entries.empty:
            continue

        entry_row = entries.iloc[0]
        side = int(entry_row["entry_signal"])
        entry_idx = int(entry_row.name)
        entry_price = float(entry_row["close"])
        entry_time = entry_row["datetime"]

        risk_setup = build_risk_setup(
            entry_price=entry_price,
            side=side,
            orb_high=float(entry_row["orb_high"]),
            orb_low=float(entry_row["orb_low"]),
            atr_value=float(entry_row[atr_col]) if atr_col in entry_row else float("nan"),
            atr_buffer_mult=atr_buffer_mult,
            rr=fixed_rr,
        )
        if risk_setup is None:
            continue

        size = compute_position_size(
            equity=equity,
            risk_pct=risk_per_trade_pct,
            risk_per_unit=risk_setup.risk_per_unit,
        )
        if size <= 0:
            continue

        risk_amount = equity * risk_per_trade_pct

        local_time = day["datetime"].dt.tz_convert(tz).dt.strftime("%H:%M")
        session_slice = day[(local_time <= session_end) & (day.index > entry_idx)]

        exit_price = float(day.iloc[-1]["close"])
        exit_time = day.iloc[-1]["datetime"]
        exit_reason = "session_close"

        for _, row in session_slice.iterrows():
            hit, level_price, reason = _check_exit(
                row=row,
                side=side,
                stop_loss=risk_setup.stop_loss,
                take_profit=risk_setup.take_profit,
            )
            if hit:
                exit_price = level_price
                exit_time = row["datetime"]
                exit_reason = reason
                break
            exit_price = float(row["close"])
            exit_time = row["datetime"]

        pnl = (exit_price - entry_price) * size * side
        ret_pct = pnl / equity if equity > 0 else 0.0
        equity_after = equity + pnl

        trades.append(
            Trade(
                session_date=session_date,
                side=side,
                entry_time=entry_time,
                entry_price=entry_price,
                stop_loss=risk_setup.stop_loss,
                take_profit=risk_setup.take_profit,
                size=size,
                risk_amount=risk_amount,
                exit_time=exit_time,
                exit_price=exit_price,
                exit_reason=exit_reason,
                pnl=pnl,
                ret_pct=ret_pct,
                equity_before=equity,
                equity_after=equity_after,
            )
        )

        equity = equity_after

    if not trades:
        return pd.DataFrame(
            columns=[
                "session_date",
                "side",
                "entry_time",
                "entry_price",
                "stop_loss",
                "take_profit",
                "size",
                "risk_amount",
                "exit_time",
                "exit_price",
                "exit_reason",
                "pnl",
                "ret_pct",
                "equity_before",
                "equity_after",
                "equity_curve",
            ]
        )

    result = pd.DataFrame([t.__dict__ for t in trades])
    result["equity_curve"] = result["equity_after"] / initial_equity
    return result


def summarize_performance(trades: pd.DataFrame, initial_equity: float = 100000.0) -> dict:
    if trades.empty:
        return {
            "num_trades": 0,
            "win_rate": 0.0,
            "avg_return": 0.0,
            "cum_return": 0.0,
            "net_pnl": 0.0,
            "final_equity": initial_equity,
        }

    num_trades = len(trades)
    win_rate = float((trades["pnl"] > 0).mean())
    avg_return = float(trades["ret_pct"].mean())
    net_pnl = float(trades["pnl"].sum())
    final_equity = float(trades.iloc[-1]["equity_after"])
    cum_return = (final_equity / initial_equity) - 1.0

    return {
        "num_trades": num_trades,
        "win_rate": win_rate,
        "avg_return": avg_return,
        "cum_return": cum_return,
        "net_pnl": net_pnl,
        "final_equity": final_equity,
    }
