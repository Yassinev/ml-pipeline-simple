import json, random
from pathlib import Path

def split(input_path="data/annotated/annotated.jsonl", output_dir="data/processed"):
    records = [json.loads(l) for l in open(input_path) if l.strip()]
    random.seed(42); random.shuffle(records)
    n = len(records)
    splits = {"train": records[:int(n*0.7)], "val": records[int(n*0.7):int(n*0.85)], "test": records[int(n*0.85):]}
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for name, data in splits.items():
        with open(f"{output_dir}/{name}.jsonl", "w") as f:
            for r in data: f.write(json.dumps(r)+"\n")
        print(f"{name}: {len(data)} records")

if __name__ == "__main__":
    split()
