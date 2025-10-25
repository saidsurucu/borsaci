"""Terminal chart utilities using plotext for financial visualizations"""

import plotext as plt
from typing import List, Dict, Any, Optional
import json


def create_candlestick_chart(
    dates: List[str],
    open_prices: List[float],
    high_prices: List[float],
    low_prices: List[float],
    close_prices: List[float],
    title: str = "Fiyat Grafiği",
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> str:
    """
    Create candlestick (mum) chart from OHLC data.

    Args:
        dates: List of date strings (YYYY-MM-DD format)
        open_prices: Opening prices
        high_prices: High prices
        low_prices: Low prices
        close_prices: Closing prices
        title: Chart title
        width: Chart width (None = auto)
        height: Chart height (None = auto)

    Returns:
        Rendered chart as string

    Example:
        >>> dates = ['2024-01-01', '2024-01-02', '2024-01-03']
        >>> opens = [100, 102, 98]
        >>> highs = [105, 104, 100]
        >>> lows = [98, 100, 95]
        >>> closes = [102, 98, 99]
        >>> chart = create_candlestick_chart(dates, opens, highs, lows, closes)
    """
    plt.clear_figure()

    # Set size if specified
    if width and height:
        plt.plot_size(width, height)

    # Date formatting
    plt.date_form('Y-m-d')

    # Prepare data in plotext format (dict with keys: Open, High, Low, Close)
    data = {
        "Open": open_prices,
        "High": high_prices,
        "Low": low_prices,
        "Close": close_prices,
    }

    # Create candlestick chart
    plt.candlestick(dates, data)

    # Labels
    plt.title(title)
    plt.xlabel("Tarih")
    plt.ylabel("Fiyat (TL)")

    # Build and return as string
    return plt.build()


def create_comparison_bar_chart(
    labels: List[str],
    values: List[float],
    title: str = "Karşılaştırma",
    ylabel: str = "Değer",
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> str:
    """
    Bar chart for comparing metrics across entities.

    Args:
        labels: Entity labels (company names, fund names, etc.)
        values: Metric values
        title: Chart title
        ylabel: Y-axis label
        width: Chart width (None = auto)
        height: Chart height (None = auto)

    Returns:
        Rendered chart as string

    Example:
        >>> labels = ['GARAN', 'ISCTR', 'AKBNK']
        >>> values = [12.5, 10.2, 11.8]
        >>> chart = create_comparison_bar_chart(labels, values, "Banka Karlılığı", "Net Kâr (M TL)")
    """
    plt.clear_figure()

    # Set size if specified
    if width and height:
        plt.plot_size(width, height)

    # Create bar chart
    plt.bar(labels, values)

    # Labels
    plt.title(title)
    plt.xlabel("Şirket/Varlık")
    plt.ylabel(ylabel)

    # Build and return as string
    return plt.build()


def create_multi_line_chart(
    series_data: Dict[str, List[float]],
    dates: List[str],
    title: str = "Performans Karşılaştırması",
    ylabel: str = "Değişim (%)",
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> str:
    """
    Multi-line chart for performance comparison.

    Args:
        series_data: Dict of {label: values} (e.g., {'ASELS': [0, 2, 5], 'THYAO': [0, -1, 3]})
        dates: List of date strings
        title: Chart title
        ylabel: Y-axis label
        width: Chart width (None = auto)
        height: Chart height (None = auto)

    Returns:
        Rendered chart as string

    Example:
        >>> series_data = {'ASELS': [0, 2.5, 5.1], 'THYAO': [0, -1.2, 3.4]}
        >>> dates = ['2024-01-01', '2024-01-02', '2024-01-03']
        >>> chart = create_multi_line_chart(series_data, dates, "Hisse Performansı")
    """
    plt.clear_figure()

    # Set size if specified
    if width and height:
        plt.plot_size(width, height)

    # Date formatting
    plt.date_form('Y-m-d')

    # Plot each series
    for label, values in series_data.items():
        plt.plot(dates, values, label=label)

    # Labels
    plt.title(title)
    plt.xlabel("Tarih")
    plt.ylabel(ylabel)

    # Build and return as string
    return plt.build()


def create_histogram(
    values: List[float],
    bins: int = 10,
    title: str = "Dağılım",
    xlabel: str = "Değer",
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> str:
    """
    Histogram for distribution analysis.

    Args:
        values: List of values to plot
        bins: Number of bins
        title: Chart title
        xlabel: X-axis label
        width: Chart width (None = auto)
        height: Chart height (None = auto)

    Returns:
        Rendered chart as string

    Example:
        >>> values = [10, 12, 15, 18, 20, 22, 25, 28, 30, 32]
        >>> chart = create_histogram(values, bins=5, title="P/E Dağılımı", xlabel="P/E Oranı")
    """
    plt.clear_figure()

    # Set size if specified
    if width and height:
        plt.plot_size(width, height)

    # Create histogram
    plt.hist(values, bins)

    # Labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frekans")

    # Build and return as string
    return plt.build()


def parse_price_data_for_candlestick(mcp_output: str) -> Optional[Dict[str, List]]:
    """
    Parse MCP get_price_data output to extract OHLC data for candlestick chart.

    Expected format: JSON string or dict with structure:
    [
        {"date": "2024-01-01", "open": 100, "high": 105, "low": 98, "close": 102},
        ...
    ]

    Args:
        mcp_output: MCP tool output (JSON string or dict)

    Returns:
        Dict with 'dates', 'open', 'high', 'low', 'close' lists
        None if parsing fails

    Example:
        >>> mcp_output = '[{"date":"2024-01-01","open":100,"high":105,"low":98,"close":102}]'
        >>> data = parse_price_data_for_candlestick(mcp_output)
        >>> print(data['dates'])
        ['2024-01-01']
    """
    try:
        # Parse JSON if string
        if isinstance(mcp_output, str):
            data = json.loads(mcp_output)
        else:
            data = mcp_output

        # Ensure it's a list
        if not isinstance(data, list):
            return None

        # Extract OHLC data
        return {
            'dates': [item['date'] for item in data],
            'open': [float(item['open']) for item in data],
            'high': [float(item['high']) for item in data],
            'low': [float(item['low']) for item in data],
            'close': [float(item['close']) for item in data],
        }

    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def parse_comparison_data(mcp_output: str, metric_key: str = "value") -> Optional[Dict[str, List]]:
    """
    Parse MCP output for comparison bar chart.

    Expected format: JSON string or dict with structure:
    [
        {"name": "GARAN", "value": 12.5},
        {"name": "ISCTR", "value": 10.2},
        ...
    ]

    Args:
        mcp_output: MCP tool output (JSON string or dict)
        metric_key: Key for metric value in each item (default: "value")

    Returns:
        Dict with 'labels' and 'values' lists
        None if parsing fails
    """
    try:
        # Parse JSON if string
        if isinstance(mcp_output, str):
            data = json.loads(mcp_output)
        else:
            data = mcp_output

        # Ensure it's a list
        if not isinstance(data, list):
            return None

        # Extract labels and values
        return {
            'labels': [item['name'] for item in data],
            'values': [float(item[metric_key]) for item in data],
        }

    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
