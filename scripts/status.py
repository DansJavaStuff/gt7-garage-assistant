from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "garage.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

def scalar(sql):
    return conn.execute(sql).fetchone()[0]

print("GT7 Garage Assistant")
print("====================")
print(f"Database:       {DB_PATH}")
print()
print(f"Car models:     {scalar('SELECT COUNT(*) FROM cars')}")
print(f"Garage cars:    {scalar('SELECT COUNT(*) FROM garage_cars')}")
print(f"Engine types:   {scalar('SELECT COUNT(*) FROM engine_inventory')}")
print(f"Spare engines:  {scalar('SELECT COALESCE(SUM(quantity),0) FROM engine_inventory')}")
print(f"Engine swaps:   {scalar('SELECT COUNT(*) FROM engine_swaps')}")
print(f"Valuations:     {scalar('SELECT COUNT(*) FROM valuation_history')}")

print("\nEngine inventory")
print("----------------")
for row in conn.execute("""
    SELECT e.name, ei.quantity
    FROM engine_inventory ei
    JOIN engines e ON e.id = ei.engine_id
    ORDER BY e.name
"""):
    print(f"{row['name']:<30} x{row['quantity']}")

conn.close()
