mport sys, csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CSV_FILES = [ROOT/"data"/"sample_train.csv", ROOT/"data"/"sample_val.csv"]
JSONL_FILES = [ROOT/"data"/"golden_set.jsonl"]
VALID_LABELS = {"positive", "negative", "neutral"}
REQUIRED_COLS = {"id", "text", "label", "source", "confidence_gt"}
errors = []

def fail(m): errors.append(m)

def check_csv(p):
    if not p.exists(): fail(f"{p.name} not found"); return
    with open(p, newline="") as f:
        r = csv.DictReader(f)
        missing = REQUIRED_COLS - set(r.fieldnames or [])
        if missing: fail(f"{p.name}: missing columns {missing}"); return
        for i, row in enumerate(r, 2):
            if not row.get("text","").strip(): fail(f"{p.name} row {i}: empty text")
            if row.get("label","") not in VALID_LABELS: fail(f"{p.name} row {i}: bad label")

def check_jsonl(p):
    if not p.exists(): fail(f"{p.name} not found"); return
    recs = []
    with open(p) as f:
        for n, line in enumerate(f, 1):
            if not line.strip(): continue
            try: recs.append(json.loads(line))
            except: fail(f"{p.name} line {n}: bad JSON")
    if len(recs) < 20: fail(f"{p.name}: need >= 20 records, got {len(recs)}")

for p in CSV_FILES: check_csv(p)
for p in JSONL_FILES: check_jsonl(p)

if errors:
    print("FAILED:"); [print(" -", e) for e in errors]; sys.exit(1)
else:
    print("PASSED - all checks OK"); sys.exit(0)
