# models.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Optional


@dataclass(frozen=True)
class MarketDataPoint:
    timestamp: datetime
    symbol: str
    price: float


@dataclass(frozen=True)
class Signal:
    timestamp: datetime
    symbol: str
    action: str  # "BUY" / "SELL" / "HOLD"
    price: float
    ma: Optional[float] = None


class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        raise NotImplementedError
