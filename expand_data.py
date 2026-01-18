import csv
from datetime import datetime, timedelta

IN_PATH = "market_data.csv"
OUT_PATH = "market_data_big.csv"
TARGET_N = 120_000  # >= 100k

def normalize(name: str) -> str:
    return name.strip().lower().replace("\ufeff", "").replace("\xa0", "")

def parse_ts(s: str) -> datetime:
    return datetime.strptime(s, "%d-%b-%y")

def main():
    with open(IN_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)

        raw_fields = reader.fieldnames or []
        norm_fields = [normalize(n) for n in raw_fields]
        field_map = {norm_fields[i]: raw_fields[i] for i in range(len(raw_fields))}

        required = {"timestamp", "symbol", "price"}
        if not required.issubset(field_map.keys()):
            raise ValueError(f"CSV must contain columns {sorted(required)}. Got: {raw_fields}")

        ts_key = field_map["timestamp"]
        sym_key = field_map["symbol"]
        price_key = field_map["price"]

        rows = []
        for r in reader:
            rows.append({
                "timestamp": r[ts_key],
                "symbol": r[sym_key],
                "price": r[price_key],
            })

    if not rows:
        raise RuntimeError("No rows found in market_data.csv")

    start = parse_ts(rows[0]["timestamp"])
    out_rows = []

    for i in range(TARGET_N):
        base = rows[i % len(rows)]
        ts = start + timedelta(days=i)
        out_rows.append({
            "timestamp": ts.strftime("%d-%b-%y"),
            "symbol": base["symbol"],
            "price": base["price"],
        })

    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "symbol", "price"])
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {TARGET_N} rows to {OUT_PATH}")

if __name__ == "__main__":
    main()
