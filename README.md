# ORB DJ30: Opening Range Breakout Strategy
## A Research Implementation in Intraday Systematic Trading

**Author**: Marco Fedeli  
**Version**: 0.1.0  
**Last Updated**: February 11, 2026  
**Asset Universe**: DJ30 proxy (`DIA`)  
**Data Source**: OpenBB (provider: yfinance), CSV fallback

---

## Abstract

This repository provides a modular research implementation of an Opening Range Breakout (ORB) strategy on US market open dynamics. The framework uses 5-minute bars, a 30-minute opening range, trend filtering via EMA slope, and volume confirmation. A minimal but explicit risk model is included for controlled experimentation: stop-loss at range midpoint, fixed risk-reward target, and equity-based position sizing.

The objective is research reproducibility and strategy iteration, not production deployment.

---

## 1. Introduction

The opening phase of the US session often concentrates liquidity shocks, directional imbalance, and volatility expansion. ORB frameworks attempt to capture this behavior through breakouts of the initial intraday range.

This implementation is designed to study:
- directional continuation probability after opening-range break;
- effect of trend and volume filters on signal quality;
- impact of fixed-RR exits and percentage risk sizing on equity dynamics.

---

## 2. Methodology

### 2.1 Opening Range Definition

- Session timezone: `America/New_York`
- Opening range window: `09:30` to `10:00`
- `orb_high`: maximum high in range window
- `orb_low`: minimum low in range window

### 2.2 Signal Logic

A breakout is considered only after `10:00`.

- **Long candidate**: close > `orb_high`
- **Short candidate**: close < `orb_low`

Signal filters:
- Trend filter: slope of `EMA(50)` aligned with breakout direction
- Volume filter: `volume > 1.2 * SMA(20, volume)`

Constraint:
- one entry per session (first valid signal only)

### 2.3 Risk Model

Current risk configuration:
- Stop-loss: midpoint of opening range  
  \( SL = (orb\_high + orb\_low) / 2 \)
- Take-profit: fixed risk-reward ratio  
  \( TP = Entry \pm 1.2 \times RiskUnit \)
- Position sizing: equity-based risk budget  
  `risk_per_trade = 0.4%` of current equity

If neither SL nor TP is touched, the position is closed at session end.

---

## 3. Architecture

### 3.1 Repository Layout

```text
ORB/
├── src/
│   ├── main.py
│   └── orb_strategy/
│       ├── config.py
│       ├── data/
│       │   └── openbb_collector.py
│       ├── indicators/
│       │   └── calculations.py
│       ├── range_calc/
│       │   └── opening_range.py
│       ├── signal/
│       │   └── generator.py
│       ├── risk_management/
│       │   └── sizer.py
│       ├── backtest/
│       │   └── engine.py
│       └── analysis/
│           └── plots.py
├── data/
├── outputs/
└── requirements.txt
```

### 3.2 Module Responsibilities

- `src/orb_strategy/data/openbb_collector.py`  
  Data ingestion from OpenBB with CSV fallback.

- `src/orb_strategy/indicators/calculations.py`  
  EMA, EMA slope, volume SMA, ATR.

- `src/orb_strategy/range_calc/opening_range.py`  
  Opening range computation by session.

- `src/orb_strategy/signal/generator.py`  
  Breakout + trend + volume signal generation.

- `src/orb_strategy/risk_management/sizer.py`  
  SL/TP construction and position size from risk budget.

- `src/orb_strategy/backtest/engine.py`  
  Trade lifecycle simulation and equity tracking.

- `src/orb_strategy/analysis/plots.py`  
  Equity curve and return distribution plotting.

---

## 4. Installation & Usage

### 4.1 Requirements

- Python 3.10+
- pandas
- numpy
- matplotlib
- openbb

### 4.2 Install

```bash
pip install -r requirements.txt
```

### 4.3 Run

```bash
python src/main.py
```

Outputs:
- `outputs/trades.csv`
- `outputs/backtest_report.png`

---

## 5. What This Project Tries to Demonstrate

- Whether filtered ORB entries provide measurable directional edge.
- Whether a simple fixed-RR + fixed-risk sizing profile is sufficient for first-pass viability checks.
- How modular decomposition improves research speed and parameter iteration.

---

## 6. What Is Included vs Missing

### Included

- End-to-end pipeline (data -> indicators -> signals -> risk -> backtest -> plots)
- Session-based ORB logic
- Explicit trade-level risk and position sizing
- Reproducible config-driven workflow

### Missing / Not Production-Grade

- Robust transaction cost model (slippage, commissions, spread dynamics)
- Portfolio/multi-asset allocation engine
- Walk-forward optimization and out-of-sample protocol
- Statistical significance and robustness diagnostics
- Broker execution and live monitoring infrastructure
- Hardening, CI tests, and deployment controls

---

## 7. Assumptions and Limitations

- `DIA` is used as a practical proxy for DJ30 intraday testing.
- Intraday history depth may be limited by data provider constraints.
- Same-bar SL/TP collisions use conservative handling in backtest.
- Results are research outputs, not financial advice or live-trading guarantees.

---

## 8. Research References

- Opening range breakout concepts in intraday market microstructure literature and practitioner research.
- Trend-following and momentum foundations:
  - Moskowitz, Ooi, Pedersen (2012), *Time Series Momentum*.
- Volatility/risk reference indicator:
  - Wilder, J. W. (1978), *New Concepts in Technical Trading Systems* (ATR).

---

## 9. Roadmap

- [ ] Add transaction-cost and slippage model
- [ ] Add walk-forward and out-of-sample evaluation
- [ ] Add parameter sweep / sensitivity report
- [ ] Add benchmark comparison (buy & hold / naive ORB)
- [ ] Add unit tests for risk and backtest edge cases
- [ ] Add experiment tracking (config snapshots + run metadata)

---

## 10. License and Usage

Suggested repository policy: **Research/Educational Use** unless replaced by a formal open-source license.

---

## 11. Citation

```bibtex
@software{orb_dj30_2026,
  title={ORB DJ30: Opening Range Breakout Strategy},
  author={Fedeli, Marco},
  year={2026},
  version={0.1.0}
}
```

---

**Status**: Research Framework v0.1.0
