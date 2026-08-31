from pathlib import Path
import csv
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: python3 scripts/validate_garage_csv.py imports/garage.csv")

path = Path(sys.argv[1])

if not path.exists():
    raise SystemExit(f"File not found: {path}")

with path.open(newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

print(f"Rows: {len(rows)}")

if rows:
    print(f"First: {rows[0].get('manufacturer')} - {rows[0].get('name')}")
    print(f"Last:  {rows[-1].get('manufacturer')} - {rows[-1].get('name')}")

errors = []

if len(rows) != 374:
    errors.append(f"Expected 374 cars, found {len(rows)}")

if rows:
    if rows[0].get("manufacturer") != "Abarth":
        errors.append("First manufacturer is not Abarth")

    if rows[0].get("name") != "1500 Biposto Bertone B.A.T 1 '52":
        errors.append("First car does not match expected Abarth")

    if rows[-1].get("manufacturer") != "Yangwang":
        errors.append("Last manufacturer is not Yangwang")

    if rows[-1].get("name") != "U9 '24":
        errors.append("Last car does not match expected Yangwang")

print()

if errors:
    print("VALIDATION FAILED")
    print("=================")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("Validation OK")
