# main.py
from __future__ import annotations

from data_loader import load_market_data_csv
from profiler import benchmark
from reporting import plot_scaling, write_markdown_report
from strategies import (
    MovingAverageConfig,
    NaiveMovingAverageStrategy,
    WindowedMovingAverageStrategy,
    OptimizedNaiveMovingAverageStrategy,
)


def main() -> None:
    ticks = load_market_data_csv("market_data_big.csv", timestamp_format="%d-%b-%y")


    sizes = [1_000, 10_000, 100_000]

    config = MovingAverageConfig(window_size=10, symbol=None)

    factories = {
        "NaiveMovingAverage": lambda: NaiveMovingAverageStrategy(config),
        "WindowedMovingAverage": lambda: WindowedMovingAverageStrategy(config),
        "OptimizedNaive": lambda: OptimizedNaiveMovingAverageStrategy(symbol=None),
    }

    results = benchmark(factories, ticks, sizes)
    plot_scaling(results, out_dir="artifacts")
    write_markdown_report(results, out_path="complexity_report.md")

    print("Done. Generated artifacts/ plots and complexity_report.md")


if __name__ == "__main__":
    main()
