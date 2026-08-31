# GT7 Garage Assistant — Roadmap

This roadmap tracks the current state, immediate priorities and longer-term direction of the GT7 Garage Assistant.

The guiding principle is to make the user's real Gran Turismo 7 garage easier to manage. The project should answer useful garage decisions rather than collect data simply because it is available.

## Current Status

The project currently supports:

- [x] Raspberry Pi project structure
- [x] SQLite database
- [x] Separate GT7 model and individual owned-car records
- [x] Spare-engine inventory schema
- [x] Initial engine inventory: 23 engines across 18 engine types
- [x] Valuation-history schema
- [x] Engine-swap schema
- [x] Import-history schema
- [x] Database bootstrap script
- [x] Database status script
- [x] Garage CSV importer
- [x] GT7 reference-car-data updater
- [x] Local database and import data excluded from Git
- [x] GitHub repository and Raspberry Pi Git workflow
- [x] Initial phone-video garage capture
- [x] Native PS5 garage capture recorded

## Current Milestone — 374-Car Garage Import

### Goal

Build an accurate initial representation of the complete GT7 garage.

The garage contains **374 individual cars** and is sorted by manufacturer, then alphabetically within each manufacturer.

Known validation anchors:

```text
First:
Abarth - 1500 Biposto Bertone B.A.T 1 '52

Last:
Yangwang - U9 '24
```

### Now

- [ ] Download / receive the native PS5 garage capture
- [ ] Extract stable frames from the recording
- [ ] Detect individual garage rows
- [ ] Read visible car names and attributes
- [ ] Match names against canonical GT7 reference data
- [ ] Preserve duplicate models as separate owned cars
- [ ] Produce `imports/garage.csv`
- [ ] Validate exactly 374 rows
- [ ] Validate first and last car
- [ ] Review uncertain / low-confidence matches
- [ ] Import the validated CSV into SQLite
- [ ] Confirm `Garage cars: 374` in `scripts/status.py`

### Import Fields

The initial import should capture where reliably visible:

- manufacturer
- car name
- favourite marker
- PP
- category
- drivetrain
- power
- weight
- aspiration
- year
- distance driven

The favourite marker is informational only and should not be treated as an automatic keep/sell preference.

## Next — Engine-Swap Compatibility

Populate the local database with current GT7 engine-swap mappings.

- [ ] Identify a reliable maintainable swap-data source
- [ ] Import all current engine types
- [ ] Import compatible recipient cars
- [ ] Record source and GT7 version
- [ ] Match swap recipient names to canonical local car records
- [ ] Cross-reference swaps against the 374-car garage
- [ ] Report which spare engines have an owned compatible recipient
- [ ] Report compatible recipients not currently owned
- [ ] Handle duplicate spare engines correctly

## Next — Swap Ranking

Move from simple compatibility to useful recommendations.

### Performance Metrics

- [ ] Stock recipient power
- [ ] Swapped power
- [ ] Absolute BHP gain
- [ ] Percentage BHP gain
- [ ] Stock / swapped weight
- [ ] Power-to-weight gain
- [ ] PP change where reliable data exists
- [ ] Maximum tuning potential where reliable data exists

### Recommendation Logic

- [ ] Rank biggest transformation
- [ ] Rank best practical swap
- [ ] Prefer stronger uses of scarce one-off engines
- [ ] Be less conservative with duplicate spare engines
- [ ] Warn when an owned compatible car is not the best use of the engine
- [ ] Identify especially useful race / event builds where evidence supports it
- [ ] Keep recommendation reasoning visible rather than returning a black-box score

## Near Term — Garage Intelligence

- [ ] Identify duplicate models
- [ ] Show each duplicate as an individual garage car
- [ ] Highlight different PP / power / mileage between duplicates
- [ ] Infer likely stock vs modified state cautiously
- [ ] Identify cars with very low / zero use
- [ ] Identify cars relevant to current spare engines
- [ ] Add notes / manual keep flags independent of GT7 favourites
- [ ] Support manual corrections to imported garage data

## Near Term — Resale Valuation Tracking

Track GT7 Car Valuation Service prices over time.

### Data Collection

- [ ] Identify whether daily body valuations are available from a maintainable external source
- [ ] Investigate whether GT7 network traffic exposes useful valuation data
- [ ] Investigate community valuation trackers
- [ ] Define a manual / semi-automatic capture fallback
- [ ] Store daily valuation history
- [ ] Distinguish body valuation from tuning valuation where possible

### Analysis

- [ ] Current value
- [ ] Observed 30-day / 90-day high
- [ ] Observed low
- [ ] Current percentile within observed range
- [ ] Rising / falling trend
- [ ] Days since previous high
- [ ] Sell / hold recommendation

The project should not assume that a simple upward arrow means "sell now".

## Near Term — Sell / Keep Advisor

Combine garage ownership, swaps and valuation history.

Potential statuses:

- [ ] KEEP
- [ ] KEEP ONE
- [ ] ENGINE-SWAP CANDIDATE
- [ ] SELL NOW
- [ ] WAIT FOR BETTER PRICE

Recommendation factors should include duplicate ownership, whether the individual copy is modified, mileage / usage, spare-engine compatibility, strength of the potential engine swap, rarity / replacement difficulty, current sale value, historical valuation range and manual user notes.

GT7's favourite marker should **not** be treated as a strong preference because favourites were also used for multiplayer car selection.

## Later — Lightweight Web Dashboard

Build a Raspberry Pi-hosted web interface once the underlying data is trustworthy.

Potential views:

- [ ] Dashboard
- [ ] Garage
- [ ] Car Detail
- [ ] Spare Engines
- [ ] Engine Detail
- [ ] Swap Recommendations
- [ ] Duplicates
- [ ] Sell / Hold
- [ ] Valuation History
- [ ] Current Market Opportunities
- [ ] Import / Data Health

The command-line scripts and SQLite database should remain usable independently of the web interface.

## Later — PS5 / GT7 UDP Telemetry

- [ ] Build a Raspberry Pi UDP listener
- [ ] Detect currently driven car ID
- [ ] Map telemetry car IDs to canonical GT7 cars
- [ ] Record driven cars automatically over time
- [ ] Capture speed / RPM / fuel / tyre-temperature data
- [ ] Investigate lap / setup analysis
- [ ] Keep telemetry work separate from core garage inventory

Telemetry should not block garage, engine-swap or resale features.

## Later — Dealership Awareness

- [ ] Track Used Car dealership inventory
- [ ] Track Legend Cars inventory
- [ ] Match available cars against desired engine-swap recipients
- [ ] Flag rare compatible cars when they become available
- [ ] Show whether a missing recipient is currently purchasable
- [ ] Track dealership price where reliable data is available

## Later — Data Refresh Automation

- [ ] Refresh canonical GT7 car data automatically
- [ ] Refresh engine-swap data after GT7 updates
- [ ] Record source / version / update date
- [ ] Detect newly added cars
- [ ] Detect newly added swaps
- [ ] Warn when reference data is stale
- [ ] Avoid silently changing user garage data during reference refresh

## Technical / Maintenance Backlog

- [ ] Add schema migration support
- [ ] Add automated database tests
- [ ] Add importer tests
- [ ] Add swap-matching tests
- [ ] Add valuation-history tests
- [ ] Add structured logging
- [ ] Add backup / restore for `garage.db`
- [ ] Add export to CSV / JSON
- [ ] Add import confidence / correction workflow
- [ ] Keep downloaded reference data out of Git
- [ ] Keep personal garage data out of Git
- [ ] Keep Raspberry Pi setup reproducible
- [ ] Automate GitHub -> Raspberry Pi deployment when useful
- [ ] Keep README and roadmap aligned with implemented behaviour

## Completed Milestones

- [x] Project created as `gt7-garage-assistant`
- [x] Git repository initialised
- [x] Default branch moved to `main`
- [x] Public GitHub repository created
- [x] Raspberry Pi push to GitHub confirmed
- [x] Live SQLite database excluded from source control
- [x] Initial database schema created
- [x] Initial spare-engine inventory loaded
- [x] GT7 reference car data downloading successfully
- [x] Phone-video extraction approach tested
- [x] Native PS5 garage recording captured to improve import quality

## Parking Lot

Useful ideas that are deliberately not current priorities:

- [ ] Full race telemetry dashboard
- [ ] Detailed tuning recommendation database
- [ ] Automatic setup recommendations
- [ ] Lap-time comparison
- [ ] Fuel / tyre strategy tools
- [ ] Public / multi-user deployment
- [ ] Mobile-native app
- [ ] Cloud-hosted database

## Priority Order

1. **Validated 374-car garage import** — current.
2. Engine-swap compatibility data.
3. Swap ranking / recommendation logic.
4. Garage duplicate and modification analysis.
5. Resale valuation tracking.
6. Sell / keep advisor.
7. Raspberry Pi web dashboard.
8. Dealership awareness.
9. Data refresh automation.
10. GT7 UDP telemetry experiments.

The order is intentionally practical: if a GT7 update or a useful data source changes what is easiest or most valuable, priorities can move.

## Development Principle

The assistant should make real GT7 garage decisions faster and more informed.

It should not add complexity merely because more GT7 data can technically be collected.
