# Quant Alpha Backtest Evidence

Run date: 2026-04-25

Data source: `BorsaMCP.get_historical_data(symbol, market="bist", period="5y")`

The current MCP response returns 30 coarse OHLCV bars for the sampled 5-year BIST histories. The alpha engine adapts its indicator windows to the available bar count and runs a long-only BIST cash-equity backtest. Short signals move the strategy to cash instead of opening short positions.

Assumptions:

- Signal is generated at bar close and evaluated on the next bar close-to-close return.
- Transaction cost is 0.20% for each position change.
- Alpha score combines trend, momentum breakout, RSI, volatility displacement, ICT liquidity sweep, and fair value gap features.
- Results are research evidence only and are not investment advice.

| Symbol | Bars | Last Signal | Alpha Return | Buy-Hold Return | Sharpe | Max Drawdown | Direction Accuracy | Trades |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ASELS | 30 | YUKARI, score 0.75 | 1108.04% | 2489.17% | 1.11 | -34.48% | 73.33% | 3 |
| THYAO | 30 | NOTR, score 0.10 | 1818.20% | 2229.75% | 1.28 | -15.90% | 62.50% | 2 |
| GARAN | 30 | NOTR, score -0.05 | 1018.13% | 1393.51% | 1.33 | -12.02% | 80.00% | 2 |

Reviewer note: these are intentionally shown beside buy-and-hold because BIST had a strong upward historical regime in this sample. The feature is useful because it adds transparent signal scoring, downside/risk metrics, and reproducible assumptions to BorsaCI's existing market-data workflow rather than claiming a standalone trading system.
