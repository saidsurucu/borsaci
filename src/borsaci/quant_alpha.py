"""Quant alpha signals and backtesting helpers for BIST OHLCV data.

The implementation is intentionally dependency-free so it can run inside the
existing agent workflow after MCP returns historical prices.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import ast
import json
import math
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class PriceBar:
    """Normalized OHLCV bar."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(frozen=True)
class SignalPoint:
    """Per-bar alpha score with explainable feature contributions."""

    date: str
    close: float
    score: float
    prediction: str
    position: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class BacktestResult:
    """Backtest metrics and curve for a generated alpha signal."""

    ticker: str
    bars: int
    signal_points: list[SignalPoint]
    strategy_equity: list[float]
    benchmark_equity: list[float]
    dates: list[str]
    total_return_pct: float
    benchmark_return_pct: float
    sharpe: float
    max_drawdown_pct: float
    win_rate_pct: float
    prediction_accuracy_pct: float
    trades: int
    last_signal: SignalPoint


def extract_ohlcv_from_text(text: str) -> Optional[list[PriceBar]]:
    """Extract the first valid OHLCV array embedded in LLM/MCP text output."""

    for payload in _iter_possible_arrays(text):
        bars = normalize_price_bars(payload)
        if bars:
            return bars
    return None


def normalize_price_bars(raw: Any) -> list[PriceBar]:
    """Normalize MCP historical-data payloads into sorted price bars."""

    if isinstance(raw, dict):
        for key in ("data", "prices", "historical", "results", "items"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break

    if not isinstance(raw, list):
        return []

    bars: list[PriceBar] = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        try:
            date = _first_present(item, ("date", "datetime", "time", "timestamp"))
            open_price = _to_float(_first_present(item, ("open", "Open", "o")))
            high = _to_float(_first_present(item, ("high", "High", "h")))
            low = _to_float(_first_present(item, ("low", "Low", "l")))
            close = _to_float(_first_present(item, ("close", "Close", "c", "adjClose")))
            volume = _to_float(_first_present(item, ("volume", "Volume", "v"), 0.0))
        except (KeyError, TypeError, ValueError):
            continue

        if min(open_price, high, low, close) <= 0:
            continue

        bars.append(
            PriceBar(
                date=_format_date(date),
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=max(volume, 0.0),
            )
        )

    return sorted(bars, key=lambda bar: bar.date)


def run_bist_alpha_backtest(
    bars: Iterable[PriceBar],
    ticker: str = "BIST",
    entry_threshold: float = 0.35,
    exit_threshold: float = -0.20,
    transaction_cost: float = 0.002,
) -> Optional[BacktestResult]:
    """Run a long-only alpha backtest suitable for BIST cash equities.

    The alpha blends trend and momentum with ICT-inspired liquidity sweeps and
    fair value gaps. Signals are evaluated using next-bar close-to-close returns.
    """

    series = list(bars)
    if len(series) < 20:
        return None

    closes = [bar.close for bar in series]
    highs = [bar.high for bar in series]
    lows = [bar.low for bar in series]
    opens = [bar.open for bar in series]
    volumes = [bar.volume for bar in series]

    slow_period = min(30, max(10, len(series) // 3))
    fast_period = min(10, max(4, slow_period // 2))
    momentum_period = min(20, max(8, slow_period))
    atr_period = min(14, max(5, len(series) // 6))
    rsi_period = min(14, max(7, len(series) // 5))
    volume_period = min(20, max(8, slow_period))
    start_index = max(slow_period, momentum_period, atr_period, rsi_period, volume_period)

    if len(series) - start_index < 5:
        return None

    atr = _atr(series, atr_period)
    rsi = _rsi(closes, rsi_period)
    fast_ma = _sma(closes, fast_period)
    slow_ma = _sma(closes, slow_period)
    volume_z = _rolling_zscore(volumes, volume_period)

    strategy_equity = [1.0]
    benchmark_equity = [1.0]
    equity_dates = [series[start_index].date]
    points: list[SignalPoint] = []
    position = 0
    trades = 0
    trade_returns: list[float] = []
    prediction_hits = 0
    prediction_count = 0

    for i in range(start_index, len(series) - 1):
        score, reasons = _score_bar(
            i=i,
            momentum_window=momentum_period,
            opens=opens,
            highs=highs,
            lows=lows,
            closes=closes,
            atr=atr,
            rsi=rsi,
            fast_ma=fast_ma,
            slow_ma=slow_ma,
            volume_z=volume_z,
        )

        if score >= entry_threshold:
            next_position = 1
        elif score <= exit_threshold or closes[i] < (fast_ma[i] or closes[i]):
            next_position = 0
        else:
            next_position = position

        prediction = "YUKARI" if score >= 0.15 else "ASAGI" if score <= -0.15 else "NOTR"
        next_return = closes[i + 1] / closes[i] - 1.0

        if prediction != "NOTR":
            prediction_count += 1
            if (prediction == "YUKARI" and next_return > 0) or (prediction == "ASAGI" and next_return < 0):
                prediction_hits += 1

        cost = transaction_cost if next_position != position else 0.0
        if next_position != position:
            trades += 1
        strategy_return = next_position * next_return - cost
        benchmark_return = next_return

        strategy_equity.append(strategy_equity[-1] * (1.0 + strategy_return))
        benchmark_equity.append(benchmark_equity[-1] * (1.0 + benchmark_return))
        equity_dates.append(series[i + 1].date)
        if next_position:
            trade_returns.append(strategy_return)

        point = SignalPoint(
            date=series[i].date,
            close=closes[i],
            score=round(score, 4),
            prediction=prediction,
            position=next_position,
            reasons=tuple(reasons[:5]),
        )
        points.append(point)
        position = next_position

    returns = [
        strategy_equity[i] / strategy_equity[i - 1] - 1.0
        for i in range(1, len(strategy_equity))
    ]

    return BacktestResult(
        ticker=ticker.upper(),
        bars=len(series),
        signal_points=points,
        strategy_equity=strategy_equity,
        benchmark_equity=benchmark_equity,
        dates=equity_dates,
        total_return_pct=(strategy_equity[-1] - 1.0) * 100.0,
        benchmark_return_pct=(benchmark_equity[-1] - 1.0) * 100.0,
        sharpe=_sharpe(returns, annualization_factor=_annualization_factor(equity_dates)),
        max_drawdown_pct=_max_drawdown(strategy_equity) * 100.0,
        win_rate_pct=_win_rate(trade_returns) * 100.0,
        prediction_accuracy_pct=(
            prediction_hits / prediction_count * 100.0 if prediction_count else 0.0
        ),
        trades=trades,
        last_signal=points[-1],
    )


def format_backtest_report(result: BacktestResult) -> str:
    """Return a compact Markdown report for the answer agent and PR evidence."""

    last = result.last_signal
    reasons = ", ".join(last.reasons) if last.reasons else "Belirgin bir tetikleyici yok"
    return f"""
## Quant Alpha + ICT Backtest ({result.ticker})

Veri sayisi: {result.bars} OHLCV bar
Son sinyal: {last.prediction} | skor: {last.score:.2f} | kapanis: {last.close:.2f} | tarih: {last.date}
Son sinyal nedenleri: {reasons}

Backtest varsayimlari:
- Long-only BIST nakit hisse mantigi kullanildi; short yerine nakitte kalinir.
- Sinyal gun sonu uretilir, ertesi bar kapanis getirisiyle test edilir.
- Islem maliyeti: her pozisyon degisiminde %0.20.

Sonuclar:
- Alpha toplam getiri: {result.total_return_pct:.2f}%
- Al-tut toplam getiri: {result.benchmark_return_pct:.2f}%
- Sharpe: {result.sharpe:.2f}
- Maksimum dusus: {result.max_drawdown_pct:.2f}%
- Pozisyondaki gun kazanma orani: {result.win_rate_pct:.2f}%
- Yon tahmini isabeti: {result.prediction_accuracy_pct:.2f}%
- Islem sayisi: {result.trades}

Model notu: Skor; trend, momentum/kirilim, RSI, volatilite genislemesi,
ICT likidite supurmesi ve fair value gap sinyallerinin agirlikli bilesimidir.
Bu rapor arastirma amaclidir ve yatirim tavsiyesi degildir.
""".strip()


def create_equity_curve_chart(result: BacktestResult, width: Optional[int] = None, height: Optional[int] = None) -> Optional[str]:
    """Create a terminal equity curve chart for strategy vs buy-and-hold."""

    try:
        import plotext as plt
    except Exception:
        return None

    plt.clear_figure()
    if width and height:
        plt.plot_size(width, height)
    plt.date_form("Y-m-d")
    strategy = [(value - 1.0) * 100.0 for value in result.strategy_equity]
    benchmark = [(value - 1.0) * 100.0 for value in result.benchmark_equity]
    plt.plot(result.dates, strategy, label="Alpha")
    plt.plot(result.dates, benchmark, label="Al-Tut")
    plt.title(f"{result.ticker} Alpha Backtest")
    plt.xlabel("Tarih")
    plt.ylabel("Getiri (%)")
    return plt.build()


def _iter_possible_arrays(text: str) -> Iterable[Any]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "[":
            continue
        candidate = text[index:]
        try:
            payload, _ = decoder.raw_decode(candidate)
            yield payload
            continue
        except json.JSONDecodeError:
            pass

        end = candidate.find("]\n")
        if end == -1:
            end = candidate.find("]")
        if end == -1:
            continue
        try:
            yield ast.literal_eval(candidate[: end + 1])
        except (SyntaxError, ValueError):
            continue


def _score_bar(
    i: int,
    momentum_window: int,
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
    atr: list[Optional[float]],
    rsi: list[Optional[float]],
    fast_ma: list[Optional[float]],
    slow_ma: list[Optional[float]],
    volume_z: list[Optional[float]],
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    if slow_ma[i] and fast_ma[i] and closes[i] > slow_ma[i] and fast_ma[i] > slow_ma[i]:
        score += 0.35
        reasons.append("trend yukari")
    elif slow_ma[i] and fast_ma[i] and closes[i] < slow_ma[i] and fast_ma[i] < slow_ma[i]:
        score -= 0.25
        reasons.append("trend zayif")

    prior_high = max(highs[i - momentum_window : i])
    prior_low = min(lows[i - momentum_window : i])
    if closes[i] > prior_high:
        score += 0.25
        reasons.append(f"{momentum_window} bar kirilim")
    elif closes[i] < prior_low:
        score -= 0.20
        reasons.append(f"{momentum_window} bar asagi kirilim")

    if rsi[i] is not None and rsi[i] < 35 and closes[i] > opens[i]:
        score += 0.15
        reasons.append("RSI toparlanma")
    elif rsi[i] is not None and rsi[i] > 70 and closes[i] < opens[i]:
        score -= 0.15
        reasons.append("RSI yorulma")

    midpoint = (highs[i] + lows[i]) / 2.0
    if lows[i] < prior_low and closes[i] > prior_low and closes[i] > midpoint:
        score += 0.25
        reasons.append("ICT bullish liquidity sweep")
    elif highs[i] > prior_high and closes[i] < prior_high and closes[i] < midpoint:
        score -= 0.25
        reasons.append("ICT bearish liquidity sweep")

    if i >= 2 and lows[i] > highs[i - 2]:
        score += 0.15
        reasons.append("bullish fair value gap")
    elif i >= 2 and highs[i] < lows[i - 2]:
        score -= 0.15
        reasons.append("bearish fair value gap")

    candle_body = abs(closes[i] - opens[i])
    if atr[i] and candle_body > 1.2 * atr[i] and (volume_z[i] or 0.0) > 0:
        if closes[i] > opens[i]:
            score += 0.10
            reasons.append("hacimli bullish displacement")
        else:
            score -= 0.10
            reasons.append("hacimli bearish displacement")

    return max(min(score, 1.0), -1.0), reasons


def _atr(bars: list[PriceBar], period: int) -> list[Optional[float]]:
    true_ranges: list[float] = []
    for i, bar in enumerate(bars):
        previous_close = bars[i - 1].close if i else bar.close
        true_ranges.append(
            max(
                bar.high - bar.low,
                abs(bar.high - previous_close),
                abs(bar.low - previous_close),
            )
        )
    return _sma(true_ranges, period)


def _rsi(values: list[float], period: int) -> list[Optional[float]]:
    result: list[Optional[float]] = [None] * len(values)
    if len(values) <= period:
        return result

    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    result[period] = 100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))

    for i in range(period + 1, len(values)):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        result[i] = 100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))

    return result


def _sma(values: list[float], period: int) -> list[Optional[float]]:
    result: list[Optional[float]] = [None] * len(values)
    if period <= 0:
        return result
    running = 0.0
    for i, value in enumerate(values):
        running += value
        if i >= period:
            running -= values[i - period]
        if i >= period - 1:
            result[i] = running / period
    return result


def _rolling_zscore(values: list[float], period: int) -> list[Optional[float]]:
    result: list[Optional[float]] = [None] * len(values)
    for i in range(period - 1, len(values)):
        window = values[i - period + 1 : i + 1]
        mean = sum(window) / period
        variance = sum((value - mean) ** 2 for value in window) / period
        stdev = math.sqrt(variance)
        result[i] = 0.0 if stdev == 0 else (values[i] - mean) / stdev
    return result


def _sharpe(returns: list[float], annualization_factor: float) -> float:
    if len(returns) < 2:
        return 0.0
    mean = sum(returns) / len(returns)
    variance = sum((item - mean) ** 2 for item in returns) / (len(returns) - 1)
    stdev = math.sqrt(variance)
    if stdev == 0:
        return 0.0
    return mean / stdev * math.sqrt(annualization_factor)


def _annualization_factor(dates: list[str]) -> float:
    parsed_dates = []
    for value in dates:
        try:
            parsed_dates.append(datetime.fromisoformat(value[:10]).date())
        except ValueError:
            continue

    if len(parsed_dates) < 2:
        return 252.0

    deltas = sorted(
        (parsed_dates[i] - parsed_dates[i - 1]).days
        for i in range(1, len(parsed_dates))
        if (parsed_dates[i] - parsed_dates[i - 1]).days > 0
    )
    if not deltas:
        return 252.0

    median_delta = deltas[len(deltas) // 2]
    if median_delta <= 2:
        return 252.0
    if median_delta <= 10:
        return 52.0
    if median_delta <= 40:
        return 12.0
    if median_delta <= 100:
        return 4.0
    return 1.0


def _max_drawdown(equity: list[float]) -> float:
    peak = equity[0]
    max_dd = 0.0
    for value in equity:
        peak = max(peak, value)
        drawdown = value / peak - 1.0
        max_dd = min(max_dd, drawdown)
    return max_dd


def _win_rate(returns: list[float]) -> float:
    if not returns:
        return 0.0
    return sum(1 for item in returns if item > 0) / len(returns)


def _first_present(item: dict[str, Any], keys: tuple[str, ...], default: Any = None) -> Any:
    for key in keys:
        if key in item and item[key] is not None:
            return item[key]
    if default is not None:
        return default
    raise KeyError(keys[0])


def _to_float(value: Any) -> float:
    if isinstance(value, str):
        value = value.replace("%", "").replace(",", ".").strip()
    return float(value)


def _format_date(value: Any) -> str:
    text = str(value)
    if "T" in text:
        text = text.split("T", 1)[0]
    if " " in text:
        text = text.split(" ", 1)[0]
    try:
        return datetime.fromisoformat(text).date().isoformat()
    except ValueError:
        return text[:10]
