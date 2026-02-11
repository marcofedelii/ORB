from __future__ import annotations

import os

from orb_strategy.analysis.plots import plot_results
from orb_strategy.backtest.engine import run_backtest, summarize_performance
from orb_strategy.config import StrategyConfig
from orb_strategy.data.openbb_collector import get_data
from orb_strategy.indicators.calculations import add_indicators
from orb_strategy.range_calc.opening_range import compute_opening_range
from orb_strategy.signal.generator import generate_orb_signals


def main() -> None:
    cfg = StrategyConfig()

    df = get_data(
        symbol=cfg.symbol,
        start_date=cfg.start_date,
        end_date=cfg.end_date,
        interval=cfg.timeframe,
        csv_path=cfg.data_csv_path,
        save_csv=True,
    )

    df = add_indicators(
        df,
        ema_period=cfg.ema_period,
        vol_sma_period=cfg.vol_sma_period,
        atr_period=cfg.atr_period,
    )
    df = compute_opening_range(
        df,
        tz=cfg.timezone,
        range_start=cfg.range_start,
        range_end=cfg.range_end,
    )
    df = generate_orb_signals(
        df,
        ema_period=cfg.ema_period,
        vol_sma_period=cfg.vol_sma_period,
        volume_factor=cfg.volume_factor,
        slope_threshold=cfg.slope_threshold,
        tz=cfg.timezone,
        range_end=cfg.range_end,
    )

    trades = run_backtest(
        df,
        tz=cfg.timezone,
        session_end=cfg.session_end,
        atr_period=cfg.atr_period,
        atr_buffer_mult=cfg.atr_buffer_mult,
        fixed_rr=cfg.fixed_rr,
        risk_per_trade_pct=cfg.risk_per_trade_pct,
        initial_equity=cfg.initial_equity,
    )
    stats = summarize_performance(trades, initial_equity=cfg.initial_equity)

    os.makedirs(cfg.output_dir, exist_ok=True)
    trades.to_csv(os.path.join(cfg.output_dir, "trades.csv"), index=False)
    plot_results(trades, cfg.output_dir)

    print("=== ORB DJ30 Backtest ===")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    print(f"Report salvato in: {cfg.output_dir}")


if __name__ == "__main__":
    main()
