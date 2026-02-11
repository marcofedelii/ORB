from __future__ import annotations

import os

import matplotlib.pyplot as plt
import pandas as pd


def plot_results(trades: pd.DataFrame, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    if trades.empty:
        return

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    axes[0].plot(pd.to_datetime(trades["session_date"]), trades["equity_curve"], linewidth=2)
    axes[0].set_title("Equity Curve")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Equity")
    axes[0].grid(True, alpha=0.3)

    axes[1].hist(trades["ret_pct"] * 100.0, bins=30)
    axes[1].set_title("Distribuzione Rendimenti per Trade (%)")
    axes[1].set_xlabel("Rendimento %")
    axes[1].set_ylabel("Frequenza")

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "backtest_report.png"), dpi=150)
    plt.close(fig)
