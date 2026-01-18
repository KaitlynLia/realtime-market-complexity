# reporting.py
from __future__ import annotations

import os
from dataclasses import asdict
from typing import List

import matplotlib.pyplot as plt

from profiler import ProfileResult


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def plot_scaling(results: List[ProfileResult], out_dir: str = "artifacts") -> None:
    _ensure_dir(out_dir)

    # group by strategy
    strategies = sorted(set(r.strategy_name for r in results))
    sizes = sorted(set(r.n_ticks for r in results))

    # Runtime plot
    plt.figure()
    for s in strategies:
        ys = [next(r.runtime_seconds for r in results if r.strategy_name == s and r.n_ticks == n) for n in sizes]
        plt.plot(sizes, ys, marker="o", label=s)
    plt.xlabel("Input size (ticks)")
    plt.ylabel("Runtime (seconds)")
    plt.title("Runtime vs Input Size")
    plt.legend()
    plt.savefig(os.path.join(out_dir, "runtime_vs_size.png"), dpi=200, bbox_inches="tight")
    plt.close()

    # Memory plot (skip if -1)
    plt.figure()
    for s in strategies:
        ys = [next(r.peak_memory_mb for r in results if r.strategy_name == s and r.n_ticks == n) for n in sizes]
        if any(y < 0 for y in ys):
            continue
        plt.plot(sizes, ys, marker="o", label=s)
    plt.xlabel("Input size (ticks)")
    plt.ylabel("Peak Memory (MB)")
    plt.title("Peak Memory vs Input Size")
    plt.legend()
    plt.savefig(os.path.join(out_dir, "memory_vs_size.png"), dpi=200, bbox_inches="tight")
    plt.close()


def write_markdown_report(
    results: List[ProfileResult],
    out_path: str = "complexity_report.md",
    runtime_plot_path: str = "artifacts/runtime_vs_size.png",
    memory_plot_path: str = "artifacts/memory_vs_size.png",
) -> None:
    # sort for stable table
    results_sorted = sorted(results, key=lambda r: (r.strategy_name, r.n_ticks))

    lines: List[str] = []
    lines.append("# Complexity Report\n")

    lines.append("## Benchmark Metrics\n")
    lines.append("| Strategy | Ticks | Runtime (s) | Peak Memory (MB) |")
    lines.append("|---|---:|---:|---:|")
    for r in results_sorted:
        lines.append(f"| {r.strategy_name} | {r.n_ticks} | {r.runtime_seconds:.6f} | {r.peak_memory_mb:.2f} |")
    lines.append("")

    lines.append("## Scaling Plots\n")
    lines.append(f"![Runtime vs Size]({runtime_plot_path})\n")
    lines.append(f"![Memory vs Size]({memory_plot_path})\n")

    lines.append("## Big-O Complexity Annotations\n")
    lines.append("- **NaiveMovingAverageStrategy**: per tick **O(n)** time (re-summing full history), **O(n)** space (store full history).\n")
    lines.append("- **WindowedMovingAverageStrategy**: per tick **O(1)** time (running sum + fixed deque), **O(k)** space (window).\n")
    lines.append("- **OptimizedNaiveMovingAverageStrategy**: per tick **O(1)** time (running sum + count), **O(1)** space.\n")

    lines.append("## Notes on Concurrency (from Week2 slides)\n")
    lines.append(
        "- This benchmark is kept **single-threaded** to ensure repeatable profiling results. "
        "If multiple threads share state (e.g., history list, running_sum), you can get **race conditions**; "
        "fixing it requires a lock/critical section, which changes both runtime and profiling hotspots.\n"
    )

    lines.append("## cProfile Hotspots (Top Snippets)\n")
    for r in results_sorted:
        lines.append(f"### {r.strategy_name} @ {r.n_ticks} ticks\n")
        lines.append("```text")
        lines.append(r.cprofile_top.strip())
        lines.append("```\n")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))
