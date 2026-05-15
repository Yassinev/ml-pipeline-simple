import json, uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

SAMPLES = [
    ("The product quality exceeded my expectations.", "positive", 0.92),
    ("Delivery was extremely slow and packaging was damaged.", "negative", 0.88),
    ("The item arrived on time and works as described.", "neutral", 0.75),
    ("Absolutely love this purchase, will buy again.", "positive", 0.97),
    ("Not what I expected based on the description.", "negative", 0.81),
]

def generate(output="data/raw/raw_reviews.jsonl", count=50):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    base = datetime(2026, 3, 8, 8, 0, 0, tzinfo=timezone.utc)
    with open(output, "w") as f:
        for i in range(count):
            s = SAMPLES[i % len(SAMPLES)]
            f.write(json.dumps({
                "id": f"rec-{str(i+1).zfill(4)}",
                "input_text": s[0], "label": s[1], "score": s[2],
                "timestamp": (base + timedelta(minutes=i*5)).isoformat().replace("+00:00","Z")
            }) + "\n")
    print(f"Generated {count} records -> {output}")

if __name__ == "__main__":
    generate()
