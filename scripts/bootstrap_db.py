from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "garage.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

conn.executescript("""
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gt7_car_id INTEGER,
    manufacturer TEXT NOT NULL,
    name TEXT NOT NULL,
    year INTEGER,
    category TEXT,
    drivetrain TEXT,
    aspiration TEXT,

    UNIQUE(manufacturer, name)
);

CREATE TABLE IF NOT EXISTS garage_cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,

    favourite INTEGER NOT NULL DEFAULT 0,

    pp REAL,
    power_bhp INTEGER,
    weight_kg INTEGER,
    distance_driven REAL,

    modified INTEGER,
    notes TEXT,

    FOREIGN KEY (car_id) REFERENCES cars(id)
);

CREATE TABLE IF NOT EXISTS engines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    donor_car TEXT
);

CREATE TABLE IF NOT EXISTS engine_inventory (
    engine_id INTEGER PRIMARY KEY,
    quantity INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (engine_id) REFERENCES engines(id)
);

CREATE TABLE IF NOT EXISTS engine_swaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    engine_id INTEGER NOT NULL,
    car_id INTEGER NOT NULL,

    stock_power_bhp INTEGER,
    swapped_power_bhp INTEGER,

    stock_weight_kg INTEGER,
    swapped_weight_kg INTEGER,

    source TEXT,
    source_version TEXT,

    UNIQUE(engine_id, car_id),

    FOREIGN KEY (engine_id) REFERENCES engines(id),
    FOREIGN KEY (car_id) REFERENCES cars(id)
);

CREATE TABLE IF NOT EXISTS valuation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    garage_car_id INTEGER NOT NULL,
    valuation_date TEXT NOT NULL,

    body_value INTEGER,
    tuning_value INTEGER,
    total_value INTEGER,

    UNIQUE(garage_car_id, valuation_date),

    FOREIGN KEY (garage_car_id) REFERENCES garage_cars(id)
);

CREATE TABLE IF NOT EXISTS imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    import_type TEXT NOT NULL,
    source TEXT,
    records INTEGER,
    notes TEXT
);
""")

engines = {
    "Voodoo-5.2L-GT350R": 1,
    "LT5-Corvette-C7": 2,
    "V8-F3500-B": 2,
    "3S-GTE-MR2": 1,
    "B18C-Integra-'98": 1,
    "MDYA-911": 1,
    "RB26DETT-GT-R-R34": 1,
    "M97/80-911": 2,
    "CTR38-CTR3": 2,
    "1LR-GUE-LFA": 1,
    "SE75E-2&4": 1,
    "Coyote-5.0L-Mustang": 1,
    "B58-GR-Supra-'20": 2,
    "HR-414E-NSX": 1,
    "LS7-Rampage": 1,
    "2JZ-GTE-Supra": 1,
    "V8-Suzuki-VGT-Gr.3": 1,
    "M64/03-911": 1,
}

for engine_name, quantity in engines.items():
    conn.execute(
        "INSERT OR IGNORE INTO engines (name) VALUES (?)",
        (engine_name,)
    )

    engine_id = conn.execute(
        "SELECT id FROM engines WHERE name = ?",
        (engine_name,)
    ).fetchone()[0]

    conn.execute(
        """
        INSERT INTO engine_inventory (engine_id, quantity)
        VALUES (?, ?)
        ON CONFLICT(engine_id)
        DO UPDATE SET quantity = excluded.quantity
        """,
        (engine_id, quantity)
    )

conn.commit()

engine_types = conn.execute(
    "SELECT COUNT(*) FROM engine_inventory"
).fetchone()[0]

engine_count = conn.execute(
    "SELECT SUM(quantity) FROM engine_inventory"
).fetchone()[0]

print(f"Database: {DB_PATH}")
print(f"Engine types: {engine_types}")
print(f"Spare engines: {engine_count}")

print("\nEngine inventory:")
for row in conn.execute("""
    SELECT e.name, ei.quantity
    FROM engine_inventory ei
    JOIN engines e ON e.id = ei.engine_id
    ORDER BY e.name
"""):
    print(f"  {row[0]:28} x{row[1]}")

conn.close()
