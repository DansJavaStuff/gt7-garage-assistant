from pathlib import Path
import argparse
import csv
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "garage.db"


def clean(value):
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def as_int(value):
    value = clean(value)
    if value is None:
        return None
    value = value.replace(",", "").replace(" BHP", "").replace(" kg", "")
    try:
        return int(float(value))
    except ValueError:
        return None


def as_float(value):
    value = clean(value)
    if value is None:
        return None
    value = value.replace(",", "")
    try:
        return float(value)
    except ValueError:
        return None


parser = argparse.ArgumentParser()
parser.add_argument("csv_file")
parser.add_argument(
    "--replace",
    action="store_true",
    help="Delete existing garage inventory before importing",
)
args = parser.parse_args()

csv_path = Path(args.csv_file)

if not csv_path.exists():
    raise SystemExit(f"File not found: {csv_path}")

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

with csv_path.open(newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

required = {"manufacturer", "name"}

if not rows:
    raise SystemExit("CSV contains no records")

missing = required - set(rows[0].keys())
if missing:
    raise SystemExit(
        "Missing required column(s): " + ", ".join(sorted(missing))
    )

try:
    conn.execute("BEGIN")

    if args.replace:
        conn.execute("DELETE FROM garage_cars")

    imported = 0

    for row in rows:
        manufacturer = clean(row.get("manufacturer"))
        name = clean(row.get("name"))

        if not manufacturer or not name:
            print(f"Skipping incomplete row: {row}")
            continue

        gt7_car_id = as_int(row.get("gt7_car_id"))
        year = as_int(row.get("year"))
        category = clean(row.get("category"))
        drivetrain = clean(row.get("drivetrain"))
        aspiration = clean(row.get("aspiration"))

        car_id = None

        # Prefer matching the existing reference car by GT7 ID.
        if gt7_car_id is not None:
            existing = conn.execute(
                """
                SELECT id
                FROM cars
                WHERE gt7_car_id = ?
                """,
                (gt7_car_id,),
            ).fetchone()

            if existing:
                car_id = existing[0]

                conn.execute(
                    """
                    UPDATE cars
                    SET
                        manufacturer = ?,
                        name = ?,
                        year = COALESCE(?, year),
                        category = COALESCE(?, category),
                        drivetrain = COALESCE(?, drivetrain),
                        aspiration = COALESCE(?, aspiration)
                    WHERE id = ?
                    """,
                    (
                        manufacturer,
                        name,
                        year,
                        category,
                        drivetrain,
                        aspiration,
                        car_id,
                    ),
                )

        # If this model did not already exist, create it.
        if car_id is None:
            conn.execute(
                """
                INSERT INTO cars (
                    gt7_car_id,
                    manufacturer,
                    name,
                    year,
                    category,
                    drivetrain,
                    aspiration
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(manufacturer, name)
                DO UPDATE SET
                    gt7_car_id = COALESCE(
                        excluded.gt7_car_id,
                        cars.gt7_car_id
                    ),
                    year = COALESCE(
                        excluded.year,
                        cars.year
                    ),
                    category = COALESCE(
                        excluded.category,
                        cars.category
                    ),
                    drivetrain = COALESCE(
                        excluded.drivetrain,
                        cars.drivetrain
                    ),
                    aspiration = COALESCE(
                        excluded.aspiration,
                        cars.aspiration
                    )
                """,
                (
                    gt7_car_id,
                    manufacturer,
                    name,
                    year,
                    category,
                    drivetrain,
                    aspiration,
                ),
            )

            car_id = conn.execute(
                """
                SELECT id
                FROM cars
                WHERE manufacturer = ?
                  AND name = ?
                """,
                (manufacturer, name),
            ).fetchone()[0]

        favourite = clean(row.get("favourite"))
        favourite = 1 if favourite in (
            "1", "yes", "true", "True", "Y", "y", "★"
        ) else 0

        conn.execute(
            """
            INSERT INTO garage_cars (
                car_id,
                favourite,
                pp,
                power_bhp,
                weight_kg,
                distance_driven
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                car_id,
                favourite,
                as_float(row.get("pp")),
                as_int(row.get("power_bhp")),
                as_int(row.get("weight_kg")),
                as_float(row.get("distance_driven")),
            ),
        )

        imported += 1

    conn.execute(
        """
        INSERT INTO imports (
            import_type,
            source,
            records,
            notes
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            "garage",
            str(csv_path),
            imported,
            "GT7 garage video import",
        ),
    )

    conn.commit()

except Exception:
    conn.rollback()
    raise


garage_count = conn.execute(
    "SELECT COUNT(*) FROM garage_cars"
).fetchone()[0]

model_count = conn.execute(
    "SELECT COUNT(*) FROM cars"
).fetchone()[0]

duplicate_count = conn.execute(
    """
    SELECT COALESCE(SUM(copies - 1), 0)
    FROM (
        SELECT car_id, COUNT(*) AS copies
        FROM garage_cars
        GROUP BY car_id
        HAVING COUNT(*) > 1
    )
    """
).fetchone()[0]

first = conn.execute(
    """
    SELECT c.manufacturer, c.name
    FROM garage_cars g
    JOIN cars c ON c.id = g.car_id
    ORDER BY g.id
    LIMIT 1
    """
).fetchone()

last = conn.execute(
    """
    SELECT c.manufacturer, c.name
    FROM garage_cars g
    JOIN cars c ON c.id = g.car_id
    ORDER BY g.id DESC
    LIMIT 1
    """
).fetchone()

print()
print("Garage import complete")
print("======================")
print(f"Imported this run: {imported}")
print(f"Garage cars:       {garage_count}")
print(f"Unique models:     {model_count}")
print(f"Duplicate copies:  {duplicate_count}")

if first:
    print(f"\nFirst: {first[0]} - {first[1]}")

if last:
    print(f"Last:  {last[0]} - {last[1]}")

conn.close()
