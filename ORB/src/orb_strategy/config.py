from dataclasses import dataclass


@dataclass
class StrategyConfig:
    symbol: str = "DIA"
    timeframe: str = "5m"
    timezone: str = "America/New_York"
    range_start: str = "09:30"
    range_end: str = "10:00"
    session_end: str = "16:00"
    ema_period: int = 50
    vol_sma_period: int = 20
    atr_period: int = 14
    atr_buffer_mult: float = 1.0
    volume_factor: float = 1.2
    slope_threshold: float = 0.0
    fixed_rr: float = 1.2
    risk_per_trade_pct: float = 0.004
    initial_equity: float = 100000.0
    start_date: str = "2025-01-01"
    end_date: str = "2026-02-10"
    data_csv_path: str = "data/dj30_m5.csv"
    output_dir: str = "outputs"
