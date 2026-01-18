# profiler.py
from __future__ import annotations

import cProfile
import io
import pstats
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from models import MarketDataPoint, Strategy

try:
    from memory_profiler import memory_usage
except ImportError:  # allow import even if not installed
    memory_usage = None


@dataclass
class ProfileResult:
    n_ticks: int
    strategy_name: str
    runtime_seconds: float
    peak_memory_mb: float
    cprofile_top: str


def run_strategy(strategy: Strategy, ticks: List[MarketDataPoint]) -> int:
    """
    Execute the strategy over ticks.
    Return number of signals generated (for sanity checks).
    Time: depends on strategy; we treat this as the workload function.
    """
    count = 0
    for t in ticks:
        sigs = strategy.generate_signals(t)
        count += len(sigs)
    return count


def profile_once(strategy_factory: Callable[[], Strategy], ticks: List[MarketDataPoint], top_k: int = 20) -> Tuple[float, str]:
    """
    cProfile the run. Return runtime and formatted top stats.
    """
    pr = cProfile.Profile()
    pr.enable()
    start = time.perf_counter()
    run_strategy(strategy_factory(), ticks)
    end = time.perf_counter()
    pr.disable()

    s = io.StringIO()
    stats = pstats.Stats(pr, stream=s).sort_stats("tottime")
    stats.print_stats(top_k)
    return (end - start, s.getvalue())


def peak_memory_mb(strategy_factory: Callable[[], Strategy], ticks: List[MarketDataPoint]) -> float:
    """
    Peak memory measured by memory_profiler.
    If memory_profiler isn't installed, return -1.
    """
    if memory_usage is None:
        return -1.0

    def _work():
        run_strategy(strategy_factory(), ticks)

    mem = memory_usage((_work, ), interval=0.05, timeout=None, max_usage=True)
    # memory_usage(..., max_usage=True) returns a float (MB)
    return float(mem)


def benchmark(strategy_factories: Dict[str, Callable[[], Strategy]], ticks: List[MarketDataPoint], sizes: List[int]) -> List[ProfileResult]:
    results: List[ProfileResult] = []

    for n in sizes:
        subset = ticks[:n]
        for name, factory in strategy_factories.items():
            runtime, prof_txt = profile_once(factory, subset)
            peak_mb = peak_memory_mb(factory, subset)

            results.append(ProfileResult(
                n_ticks=n,
                strategy_name=name,
                runtime_seconds=runtime,
                peak_memory_mb=peak_mb,
                cprofile_top=prof_txt
            ))
    return results
