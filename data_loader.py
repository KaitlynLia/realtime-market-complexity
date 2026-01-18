import csv
from datetime import datetime
from typing import List

from models import MarketDataPoint


def load_market_data_csv(path: str, timestamp_format: str = "%d-%b-%y") -> List[MarketDataPoint]:
    data: List[MarketDataPoint] = []

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)

        raw_fields = reader.fieldnames or []
        print("DEBUG raw fieldnames:", raw_fields)

        # normalize headers
        normalized = [name.strip().lower().replace("\ufeff", "") for name in raw_fields]
        print("DEBUG normalized fieldnames:", normalized)

        field_map = {normalized[i]: raw_fields[i] for i in range(len(raw_fields))}
        required = {"timestamp", "symbol", "price"}
        if not required.issubset(field_map.keys()):
            raise ValueError(f"CSV must contain columns {sorted(required)}. Got: {raw_fields}")

        ts_key = field_map["timestamp"]
        sym_key = field_map["symbol"]
        price_key = field_map["price"]

        for row in reader:
            ts = datetime.strptime(row[ts_key], timestamp_format)
            sym = row[sym_key]

            raw_price = (row.get(price_key) or "").strip()
            try:
                price = float(raw_price)
            except ValueError:
                continue

            data.append(MarketDataPoint(timestamp=ts, symbol=sym, price=price))


    return data
