from pathlib import Path
import csv
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "garage.db"
REF_DIR = ROOT / "data" / "reference"

CARS_CSV = REF_DIR / "cars.csv"
SWAPS_CSV = REF_DIR / "engineswaps.csv"

if not CARS_CSV.exists():
    raise SystemExit(f"Missing {CARS_CSV}")

if not SWAPS_CSV.exists():
    raise SystemExit(f"Missing {SWAPS_CSV}")

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

# Load GT7 car-id -> short name map
car_names = {}

with CARS_CSV.open(newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        try:
            gt7_id = int(row["ID"])
        except (ValueError, TypeError, KeyError):
            continue

        car_names[gt7_id] = row["ShortName"].strip()

# We don't currently have manufacturer names in cars.csv itself,
# so reference-created cars use an empty manufacturer placeholder.
#
# Later, maker.csv can be used to enrich these records properly.
REFERENCE_MANUFACTURER = "GT7 Reference"

with SWAPS_CSV.open(newline="", encoding="utf-8-sig") as f:
    swaps = list(csv.DictReader(f))

try:
    conn.execute("BEGIN")

    # Reference swap data is fully rebuildable.
    conn.execute("DELETE FROM engine_swaps")

    inserted = 0
    skipped = 0

    for row in swaps:
        try:
            recipient_gt7_id = int(row["NewCar"])
            donor_gt7_id = int(row["OriginalCar"])
        except (ValueError, TypeError, KeyError):
            skipped += 1
            continue

        engine_name = row.get("EngineName", "").strip()

        recipient_name = car_names.get(recipient_gt7_id)
        donor_name = car_names.get(donor_gt7_id)

        if not engine_name or not recipient_name:
            print(
                f"Skipping: engine={engine_name!r}, "
                f"recipient={recipient_gt7_id}, "
                f"donor={donor_gt7_id}"
            )
            skipped += 1
            continue

        # Ensure engine exists
        conn.execute(
            """
            INSERT OR IGNORE INTO engines (name, donor_car)
            VALUES (?, ?)
            """,
            (engine_name, donor_name),
        )

        # Fill donor name if the engine already existed without one
        if donor_name:
            conn.execute(
                """
                UPDATE engines
                SET donor_car = COALESCE(donor_car, ?)
                WHERE name = ?
                """,
                (donor_name, engine_name),
            )

        engine_id = conn.execute(
            "SELECT id FROM engines WHERE name = ?",
            (engine_name,),
        ).fetchone()[0]

        # Ensure recipient car exists
        existing = conn.execute(
            """
            SELECT id
            FROM cars
            WHERE gt7_car_id = ?
            """,
            (recipient_gt7_id,),
        ).fetchone()

        if existing:
            car_id = existing[0]
        else:
            conn.execute(
                """
                INSERT INTO cars (
                    gt7_car_id,
                    manufacturer,
                    name
                )
                VALUES (?, ?, ?)
                """,
                (
                    recipient_gt7_id,
                    REFERENCE_MANUFACTURER,
                    recipient_name,
                ),
            )

            car_id = conn.execute(
                """
                SELECT id
                FROM cars
                WHERE gt7_car_id = ?
                """,
                (recipient_gt7_id,),
            ).fetchone()[0]

        conn.execute(
            """
            INSERT OR IGNORE INTO engine_swaps (
                engine_id,
                car_id,
                source,
                source_version
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                engine_id,
                car_id,
                "ddm999/gt7info",
                "current",
            ),
        )

        inserted += 1

    conn.commit()

except Exception:
    conn.rollback()
    raise

swap_count = conn.execute(
    "SELECT COUNT(*) FROM engine_swaps"
).fetchone()[0]

engine_count = conn.execute(
    "SELECT COUNT(*) FROM engines"
).fetchone()[0]

print()
print("Engine swap import complete")
print("===========================")
print(f"Rows processed: {len(swaps)}")
print(f"Rows inserted:  {inserted}")
print(f"Rows skipped:   {skipped}")
print(f"Swap records:   {swap_count}")
print(f"Engine types:   {engine_count}")

print("\nYour spare engines with swap counts")
print("-----------------------------------")

for row in conn.execute(
    """
    SELECT
        e.name,
        ei.quantity,
        COUNT(es.id) AS swap_count
    FROM engine_inventory ei
    JOIN engines e
      ON e.id = ei.engine_id
    LEFT JOIN engine_swaps es
      ON es.engine_id = e.id
    GROUP BY e.id, e.name, ei.quantity
    ORDER BY e.name
    """
):
    print(f"{row[0]:30} x{row[1]}  -> {row[2]} compatible car(s)")

conn.close()
