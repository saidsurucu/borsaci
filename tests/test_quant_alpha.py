import json
import unittest
from datetime import date, timedelta

from borsaci.quant_alpha import (
    PriceBar,
    extract_ohlcv_from_text,
    format_backtest_report,
    run_bist_alpha_backtest,
)


def make_bars(count=90):
    bars = []
    price = 100.0
    start = date(2025, 1, 1)
    for day in range(count):
        drift = 0.35 if day > 25 else 0.05
        if day in (45, 70):
            drift = -2.0
        price += drift
        open_price = price - 0.2
        close = price + (0.5 if day in (46, 71) else 0.1)
        high = max(open_price, close) + 0.7
        low = min(open_price, close) - (2.0 if day in (45, 70) else 0.5)
        bars.append(
            PriceBar(
                date=(start + timedelta(days=day)).isoformat(),
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=1_000_000 + day * 10_000,
            )
        )
    return bars


class QuantAlphaTests(unittest.TestCase):
    def test_extracts_ohlcv_from_embedded_json(self):
        payload = [
            {
                "date": "2025-01-01",
                "open": 10,
                "high": 11,
                "low": 9,
                "close": 10.5,
                "volume": 1000,
            }
        ]

        bars = extract_ohlcv_from_text(f"MCP sonucu:\n{json.dumps(payload)}")

        self.assertIsNotNone(bars)
        self.assertEqual(bars[0].date, "2025-01-01")
        self.assertEqual(bars[0].close, 10.5)

    def test_backtest_returns_metrics_and_latest_signal(self):
        result = run_bist_alpha_backtest(make_bars(), ticker="ASELS")

        self.assertIsNotNone(result)
        self.assertEqual(result.ticker, "ASELS")
        self.assertGreater(result.bars, 45)
        self.assertGreaterEqual(result.prediction_accuracy_pct, 0)
        self.assertLessEqual(result.prediction_accuracy_pct, 100)
        self.assertGreater(len(result.strategy_equity), 1)
        self.assertIn(result.last_signal.prediction, {"YUKARI", "ASAGI", "NOTR"})

    def test_report_contains_pr_ready_backtest_metrics(self):
        result = run_bist_alpha_backtest(make_bars(), ticker="THYAO")
        report = format_backtest_report(result)

        self.assertIn("Quant Alpha + ICT Backtest", report)
        self.assertIn("Alpha toplam getiri", report)
        self.assertIn("Yon tahmini isabeti", report)
        self.assertIn("yatirim tavsiyesi degildir", report)

    def test_insufficient_history_returns_none(self):
        self.assertIsNone(run_bist_alpha_backtest(make_bars(15), ticker="GARAN"))


if __name__ == "__main__":
    unittest.main()
