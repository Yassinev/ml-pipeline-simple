import sys, csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

REQUIRED_CSV_COLS = {"id", "text", "label", "source", "confidence_gt"}
VALID_LABELS = {"positive", "negative", "neutral"}
VALID_SOURCES = {"web", "api", "mobile", "synthetic"}

CSV_FILES = [ROOT/"data"/"sample_train.csv", ROOT/"data"/"sample_val.csv"]
JSONL_FILES = [ROOT/"data"/"golden_set.jsonl"]

errors, warnings = [], []

def fail(msg): errors.append(f"  X  {msg}")
def warn(msg):  warnings.append(f"  !  {msg}")

def check_csv(path):
    if not path.exists(): fail(f"{path.name} not found"); return
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = REQUIRED_CSV_COLS - set(reader.fieldnames or [])
        if missing: fail(f"{path.name}: missing columns {missing}"); return
        rows = list(reader)
    if not rows: fail(f"{path.name}: empty"); return
    seen = set()
    for i, row in enumerate(rows, 2):
        rid = row.get("id","").strip()
        if rid in seen: fail(f"{path.name} row {i}: duplicate id '{rid}'")
        seen.add(rid)
        if not row.get("text","").strip(): fail(f"{path.name} row {i}: empty text")
        if row.get("label","").strip() not in VALID_LABELS:
            fail(f"{path.name} row {i}: invalid label '{row.get('label')}'")
        conf = row.get("confidence_gt","").strip()
        if conf:
            try:
                v = float(conf)
                if not 0.0 <= v <= 1.0: fail(f"{path.name} row {i}: confidence_gt out of range")
            except ValueError: fail(f"{path.name} row {i}: confidence_gt not a float")

def check_jsonl(path):
    if not path.exists(): fail(f"{path.name} not found"); return
    records = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line: continue
            try: obj = json.loads(line)
            except: fail(f"{path.name} line {n}: invalid JSON"); continue
            for f in ("id","text","label"):
                if f not in obj: fail(f"{path.name} line {n}: missing '{f}'")
            if obj.get("label") not in VALID_LABELS:
                fail(f"{path.name} line {n}: invalid label")
            records.append(obj)
    if len(records) < 20: fail(f"{path.name}: need >= 20 records, found {len(records)}")

print("=" * 50)
print("Data Contract Validator")
print("=" * 50)
for p in CSV_FILES:   check_csv(p)
for p in JSONL_FILES: check_jsonl(p)

if errors:
    print("\nERRORS:")
    for e in errors: print(e)
    print(f"\nFAILED — {len(errors)} error(s)")
    sys.exit(1)
else:
    print("\nPASSED — all checks OK")
    sys.exit(0)
