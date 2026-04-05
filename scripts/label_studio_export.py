import json, argparse
from pathlib import Path

def convert(input_path, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(input_path) as f, open(output_path, "w") as out:
        for line in f:
            line = line.strip()
            if line:
                out.write(line + "\n")
                count += 1
    print(f"Exported {count} records -> {output_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", default="simulate")
    p.add_argument("--input", default="data/raw/raw_reviews.jsonl")
    p.add_argument("--output", default="data/annotated/annotated.jsonl")
    args = p.parse_args()
    convert(args.input, args.output)
