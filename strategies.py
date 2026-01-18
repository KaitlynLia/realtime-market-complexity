# strategies.py
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional

from models import MarketDataPoint, Signal, Strategy


@dataclass
class MovingAverageConfig:
    window_size: int = 10
    symbol: Optional[str] = None  # if set, only trade this symbol


class NaiveMovingAverageStrategy(Strategy):
    """
    Recompute moving average from scratch using full history.

    Per tick time: O(n) where n = number of ticks seen so far (sum over history each time)
    Space: O(n) because we store all past prices.
    """

    def __init__(self, config: MovingAverageConfig):
        self.config = config
        self.prices: List[float] = []
        self.last_symbol: Optional[str] = None

    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        if self.config.symbol is not None and tick.symbol != self.config.symbol:
            return []

        self.prices.append(tick.price)  # amortized O(1)

        # O(n) sum over all history each tick
        avg = sum(self.prices) / len(self.prices)

        action = "HOLD"
        if tick.price > avg:
            action = "BUY"
        elif tick.price < avg:
            action = "SELL"

        return [Signal(timestamp=tick.timestamp, symbol=tick.symbol, action=action, price=tick.price, ma=avg)]


class WindowedMovingAverageStrategy(Strategy):
    """
    Maintain a fixed-size window and update average incrementally.

    Per tick time: O(1) (deque append/pop + O(1) arithmetic)
    Space: O(k) where k = window size
    """

    def __init__(self, config: MovingAverageConfig):
        if config.window_size <= 0:
            raise ValueError("window_size must be positive")
        self.config = config
        self.window: Deque[float] = deque(maxlen=config.window_size)
        self.running_sum: float = 0.0

    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        if self.config.symbol is not None and tick.symbol != self.config.symbol:
            return []

        # If deque is full, maxlen will drop the oldest element automatically after append.
        # But we need the value to keep running_sum correct, so handle it explicitly.
        if len(self.window) == self.window.maxlen:
            oldest = self.window[0]
            self.running_sum -= oldest

        self.window.append(tick.price)
        self.running_sum += tick.price

        avg = self.running_sum / len(self.window)  # O(1)

        action = "HOLD"
        if tick.price > avg:
            action = "BUY"
        elif tick.price < avg:
            action = "SELL"

        return [Signal(timestamp=tick.timestamp, symbol=tick.symbol, action=action, price=tick.price, ma=avg)]


class OptimizedNaiveMovingAverageStrategy(Strategy):
    """
    Refactor NaiveMovingAverageStrategy to reduce time/space.

    Idea: Keep only (running_sum, count) rather than full price history.
    Per tick time: O(1)
    Space: O(1)

    Note: This computes the average of ALL prices so far (same as naive),
    but does not store the entire history.
    """

    def __init__(self, symbol: Optional[str] = None):
        self.symbol = symbol
        self.running_sum: float = 0.0
        self.count: int = 0

    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        if self.symbol is not None and tick.symbol != self.symbol:
            return []

        self.running_sum += tick.price  # O(1)
        self.count += 1                 # O(1)
        avg = self.running_sum / self.count

        action = "HOLD"
        if tick.price > avg:
            action = "BUY"
        elif tick.price < avg:
            action = "SELL"

        return [Signal(timestamp=tick.timestamp, symbol=tick.symbol, action=action, price=tick.price, ma=avg)]
