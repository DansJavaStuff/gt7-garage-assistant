# GT7 Garage Assistant

A personal Gran Turismo 7 garage assistant for tracking owned cars, spare engines, engine-swap compatibility and resale opportunities.

The project is designed around a local Raspberry Pi database containing the user's individual GT7 garage. The aim is not simply to catalogue cars, but to answer practical questions such as which spare engines can be used now, which swaps are most worthwhile, which duplicate cars are safe to sell, and when a car's resale valuation is near the top of its observed range.

## Current Status

The project is in the foundation and data-import stage.

Current capabilities include:

- SQLite garage database on Raspberry Pi
- Separate model-level and individual-owned-car records
- Spare-engine inventory tracking
- Current inventory of 23 spare engines across 18 engine types
- Engine quantities preserved for duplicate spare engines
- Garage status / diagnostics script
- Garage CSV importer
- Reference-data updater for the community GT7 car database
- GitHub repository and Raspberry Pi workflow
- Live personal data excluded from Git

The current development priority is **importing and validating the full 374-car garage from a native PS5 screen recording**.

## Project Goals

The assistant should eventually answer four core questions:

1. **What engines do I have, and which cars can they go into?**
2. **Which compatible cars do I already own?**
3. **Which swap is actually worth doing?**
4. **Which duplicate / unwanted cars should I sell, and when?**

The intent is to build a practical decision-support tool around the user's real GT7 garage rather than a generic car database.

## Garage Data Model

The database deliberately separates the GT7 car model from an individual owned example.

### `cars`

Represents the GT7 model itself.

### `garage_cars`

Represents one specific owned example of that model, including values visible in the GT7 garage such as favourite marker, PP, power, weight and distance driven.

This allows duplicate cars to remain independent. Two copies of the same model can therefore have different PP, power, mileage and tuning state.

## Current Garage Import

The source garage contains **374 individual cars**.

The PS5 garage is sorted by manufacturer and then alphabetically within manufacturer.

Known validation anchors are:

```text
First:
Abarth - 1500 Biposto Bertone B.A.T 1 '52

Last:
Yangwang - U9 '24
```

The visible garage columns are:

- car image
- nationality
- car name
- favourite marker
- manufacturer
- PP
- category
- drivetrain
- power
- weight
- aspiration
- year
- distance driven

The favourite marker is stored as data but is **not** treated as a strong "keep this car" signal, because favourites were also used to make cars easy to select for multiplayer racing.

## Engine Inventory

The initial spare-engine inventory contains **23 engines across 18 engine types**:

- 1LR-GUE-LFA ×1
- 2JZ-GTE-Supra ×1
- 3S-GTE-MR2 ×1
- B18C-Integra-'98 ×1
- B58-GR-Supra-'20 ×2
- CTR38-CTR3 ×2
- Coyote-5.0L-Mustang ×1
- HR-414E-NSX ×1
- LS7-Rampage ×1
- LT5-Corvette-C7 ×2
- M64/03-911 ×1
- M97/80-911 ×2
- MDYA-911 ×1
- RB26DETT-GT-R-R34 ×1
- SE75E-2&4 ×1
- V8-F3500-B ×2
- V8-Suzuki-VGT-Gr.3 ×1
- Voodoo-5.2L-GT350R ×1

## Planned Engine-Swap Advice

A basic compatibility list is not enough. The assistant should rank swap candidates using useful measures such as:

- stock power vs swapped power
- absolute BHP gain
- percentage power gain
- stock vs swapped weight
- power-to-weight improvement
- PP change where available
- tuning potential
- usefulness of the resulting car
- whether the recipient car is already owned
- whether the engine is duplicated or scarce

## Resale / Valuation Direction

The project will also track GT7 Car Valuation Service prices over time.

The eventual goal is to distinguish between:

- **KEEP**
- **KEEP ONE**
- **ENGINE-SWAP CANDIDATE**
- **SELL NOW**
- **WAIT FOR BETTER PRICE**

Resale recommendations should consider duplicate ownership, tuning / modification state, mileage, engine-swap usefulness, rarity / replacement difficulty, current valuation and historical valuation range.

## Data Sources

### Local Garage Data

The user's individual garage and valuation history are stored locally in SQLite on the Raspberry Pi. The live database is intentionally excluded from Git.

### GT7 Reference Car Data

A local reference copy of the GT7 car list is downloaded from the community-maintained `ddm999/gt7info` project.

This is used to normalise car names, validate imported garage data, correct small OCR / transcription errors and provide canonical GT7 car identifiers where available.

Update with:

```bash
./scripts/update_reference_data.sh
```

Reference data is downloaded into `data/reference/` and is not committed to this repository.

### Engine-Swap Compatibility

Engine compatibility and swap-performance data will be sourced from reliable GT7 community datasets and normalised into the local database.

### GT7 UDP Telemetry

GT7 exposes an undocumented local-network UDP telemetry stream while driving. This may be useful later for active-car identification and telemetry, but it does not currently appear to provide the full garage or spare-parts inventory.

## Main Scripts

### `scripts/bootstrap_db.py`

Creates the SQLite schema and seeds the current spare-engine inventory.

```bash
python3 scripts/bootstrap_db.py
```

### `scripts/status.py`

Displays the current database state.

```bash
python3 scripts/status.py
```

### `scripts/import_garage.py`

Imports a structured garage CSV into SQLite while preserving duplicate owned cars as separate records.

```bash
python3 scripts/import_garage.py imports/garage.csv --replace
```

### `scripts/validate_garage_csv.py`

Validates the extracted garage CSV before import. The initial garage import should reconcile to exactly 374 cars and match the known first and last rows.

### `scripts/update_reference_data.sh`

Downloads the current GT7 reference car list into the local reference-data directory.

## Repository Layout

```text
gt7-garage-assistant/
├── app/
├── data/
│   ├── garage.db              # local only / ignored by Git
│   └── reference/             # downloaded / ignored by Git
├── imports/                   # local import material / ignored by Git
├── scripts/
├── .gitignore
├── README.md
└── ROADMAP.md
```

## Raspberry Pi Workflow

```text
Development changes
      ↓
    GitHub
      ↓
Raspberry Pi git pull
      ↓
Local SQLite garage data
      ↓
Future Flask web interface
```

Code and schema belong in GitHub. Personal garage data, imports and valuation history remain local to the Pi unless an explicit backup method is added later.

## Web / User Interface Direction

A lightweight Raspberry Pi web dashboard is planned once the core data is trustworthy.

Potential views include:

- Garage
- Spare Engines
- Engine Swaps
- Swap Recommendations
- Duplicates
- Sell / Hold
- Valuation History
- Current Market Opportunities
- Data / Import Status

The underlying scripts and SQLite data should remain usable without the web interface.

## Development

Development priorities and completed milestones are tracked in [ROADMAP.md](ROADMAP.md).

The current main priority is **completing the validated 374-car garage import from the PS5 screen recording**.

## Repository Principles

- Keep the user's live garage database outside Git.
- Preserve duplicate cars as separate owned objects.
- Prefer canonical GT7 names over raw OCR text.
- Validate imports before changing the live database.
- Keep reference data separate from personal garage data.
- Keep Raspberry Pi deployment lightweight.
- Prefer useful recommendations over simply displaying more data.
- Keep README and roadmap aligned with implemented behaviour.

## Disclaimer

This is a personal hobby project.

It is not affiliated with or endorsed by Sony Interactive Entertainment, Polyphony Digital or Gran Turismo.
