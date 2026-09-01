from pathlib import Path
import csv
import re
import sys
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent.parent

RAW_CSV = ROOT / "imports" / "garage_extracted_raw.csv"
CARS_CSV = ROOT / "data" / "reference" / "cars.csv"
MAKERS_CSV = ROOT / "data" / "reference" / "maker.csv"
OUTPUT_CSV = ROOT / "imports" / "garage.csv"

OVERRIDES = {
    14: ("AMG", "SLS AMG '10"),
    36: ("Audi", "R8 LMS Evo '19"),
    53: ("BMW", "M4 Gr.4"),
    75: ("Citroen", "BX 19 TRS '87"),
    106: ("Ferrari", "FXX K '14"),
    109: ("Ferrari", "812 Superfast '17"),
    140: ("Greening Auto Company", "Maverick"),
    158: ("Honda", "N-ONE RS '22"),
    165: ("Hyundai", "ELANTRA N '23"),
    187: ("Lancia", "Delta HF Integrale Evoluzione '91"),
    190: ("Lexus", "RC F '14"),
    227: ("Mitsubishi", "Lancer Evolution VI GSR T.M. SCP '99"),
    228: ("Mitsubishi", "Lancer Evolution Final '15"),
    241: ("Nissan", "R32 GT-R V-spec II '94"),
    255: ("Nissan", "Qashqai Tekna 190 2wd e-Power '22"),
    260: ("Nissan", "R92CP '92"),
    261: ("Opel", "Corsa GSE Vision Gran Turismo"),
    265: ("Peugeot", "SUV 2008 Allure '21"),
    274: ("Porsche", "911 GT3 (997) '09"),
    301: ("Renault", "R.S.01 '16"),
    329: ("Suzuki", "Suzuki Vision Gran Turismo"),
    330: ("Suzuki", "Jimny Sierra JC '18"),
    344: ("Toyota", "GR Supra RZ '20"),
}

def extract_year_from_name(name):
    match = re.search(r"'(\d{2})\b", name)
    if not match:
        return None

    yy = int(match.group(1))

    if yy <= 30:
        return 2000 + yy

    return 1900 + yy

def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def normalise(text):
    text = clean(text).lower()

    # Make apostrophes/quotes consistent.
    text = (
        text.replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
            .replace("´", "'")
    )

    # OCR commonly loses punctuation in names such as B.A.T.
    text = re.sub(r"[\.\,\:\;\(\)\[\]\{\}]", " ", text)

    # Treat separators similarly.
    text = text.replace("-", " ")

    # Remove manufacturer noise / punctuation noise.
    text = re.sub(r"[^a-z0-9']+", " ", text)

    # Collapse whitespace.
    return " ".join(text.split())


def compact(text):
    return re.sub(r"[^a-z0-9]", "", normalise(text))


def similarity(a, b):
    a_norm = normalise(a)
    b_norm = normalise(b)

    seq = SequenceMatcher(None, a_norm, b_norm).ratio()

    a_compact = compact(a)
    b_compact = compact(b)

    compact_seq = SequenceMatcher(
        None,
        a_compact,
        b_compact
    ).ratio()

    a_tokens = set(a_norm.split())
    b_tokens = set(b_norm.split())

    if a_tokens or b_tokens:
        token_score = (
            len(a_tokens & b_tokens) /
            len(a_tokens | b_tokens)
        )
    else:
        token_score = 0.0

    return (
        seq * 0.50 +
        compact_seq * 0.35 +
        token_score * 0.15
    )


# ------------------------------------------------------------
# Load maker reference
# ------------------------------------------------------------

makers = {}

with MAKERS_CSV.open(
    newline="",
    encoding="utf-8-sig"
) as f:
    for row in csv.DictReader(f):
        makers[int(row["ID"])] = clean(row["Name"])


# ------------------------------------------------------------
# Load canonical GT7 cars
# ------------------------------------------------------------

reference_cars = []

with CARS_CSV.open(
    newline="",
    encoding="utf-8-sig"
) as f:
    for row in csv.DictReader(f):
        try:
            gt7_id = int(row["ID"])
            maker_id = int(row["Maker"])
        except (ValueError, TypeError):
            continue

        manufacturer = makers.get(
            maker_id,
            f"Maker {maker_id}"
        )

        reference_cars.append({
            "gt7_car_id": gt7_id,
            "manufacturer": manufacturer,
            "name": clean(row["ShortName"]),
        })


# Group by manufacturer for much safer fuzzy matching.
cars_by_maker = {}

for car in reference_cars:
    key = normalise(car["manufacturer"])
    cars_by_maker.setdefault(key, []).append(car)


# Small manufacturer aliases where GT7/reference wording
# may differ slightly.
maker_aliases = {
    "mercedes amg": "amg",
    "greening auto company": "greening auto company",
}


# ------------------------------------------------------------
# Load raw garage extraction
# ------------------------------------------------------------

with RAW_CSV.open(
    newline="",
    encoding="utf-8-sig"
) as f:
    raw_rows = list(csv.DictReader(f))


if len(raw_rows) != 374:
    raise SystemExit(
        f"Expected 374 raw rows, found {len(raw_rows)}"
    )


output_rows = []
uncertain = []

def extract_year_from_name(name):
    match = re.search(r"'(\d{2})\b", name)

    if not match:
        return None

    yy = int(match.group(1))

    if yy <= 30:
        return 2000 + yy

    return 1900 + yy

for raw in raw_rows:
    position = int(raw["position"])
    raw_maker = clean(raw["manufacturer"])
    raw_name = clean(raw["name"])

    best = None
    best_score = None
    margin = None

    # --------------------------------------------------------
    # Manual overrides for rows where OCR is too damaged
    # --------------------------------------------------------

    override = OVERRIDES.get(position)

    if override:
        override_maker, override_name = override

        matches = [
            car
            for car in reference_cars
            if normalise(car["manufacturer"]) == normalise(override_maker)
            and normalise(car["name"]) == normalise(override_name)
        ]

        if len(matches) != 1:
            raise RuntimeError(
                f"Override at position {position} "
                f"did not resolve uniquely: "
                f"{override_maker} - {override_name}"
            )

        best = matches[0]
        best_score = 1.0
        margin = 1.0

    # --------------------------------------------------------
    # Normal fuzzy matching
    # --------------------------------------------------------

    if best is None:
        maker_key = normalise(raw_maker)

        maker_key = maker_aliases.get(
            maker_key,
            maker_key
        )

        candidates = cars_by_maker.get(
            maker_key,
            []
        )

        maker_fallback = False

        if not candidates:
            candidates = reference_cars
            maker_fallback = True

        scored = []

        raw_year_text = clean(raw.get("year"))
        raw_year = None

        try:
            if raw_year_text:
                raw_year = int(float(raw_year_text))
        except ValueError:
            pass

        for car in candidates:
            score = similarity(
                raw_name,
                car["name"]
            )

            candidate_year = extract_year_from_name(
                car["name"]
            )

            if raw_year and candidate_year:
                if raw_year == candidate_year:
                    score += 0.12
                else:
                    score -= min(
                        abs(
                            raw_year -
                            candidate_year
                        ) * 0.03,
                        0.20,
                    )

            if maker_fallback:
                maker_score = similarity(
                    raw_maker,
                    car["manufacturer"]
                )

                score = (
                    score * 0.80 +
                    maker_score * 0.20
                )

            scored.append(
                (score, car)
            )

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        best_score, best = scored[0]

        second_score = (
            scored[1][0]
            if len(scored) > 1
            else 0.0
        )

        margin = (
            best_score -
            second_score
        )
    review = (
        best_score < 0.55
        or margin < 0.025
    )

    row = {
        "position": position,
        "gt7_car_id": best["gt7_car_id"],
        "manufacturer": best["manufacturer"],
        "name": best["name"],
        "favourite": clean(raw.get("favourite")),
        "pp": clean(raw.get("pp")),
        "category": clean(raw.get("category")),
        "drivetrain": clean(raw.get("drivetrain")),
        "power_bhp": clean(raw.get("power_bhp")),
        "weight_kg": clean(raw.get("weight_kg")),
        "aspiration": clean(raw.get("aspiration")),
        "year": clean(raw.get("year")),
        "distance_driven": clean(
            raw.get("distance_driven")
        ),
        "match_score": f"{best_score:.4f}",
        "match_margin": f"{margin:.4f}",
        "needs_review": "yes" if review else "no",
        "raw_name": raw_name,
        "raw_manufacturer": raw_maker,
    }

    output_rows.append(row)

    if review:
        uncertain.append({
            "position": position,
            "raw": f"{raw_maker} - {raw_name}",
            "match": (
                f"{best['manufacturer']} - "
                f"{best['name']}"
            ),
            "score": best_score,
            "margin": margin,
        })


fieldnames = [
    "position",
    "gt7_car_id",
    "manufacturer",
    "name",
    "favourite",
    "pp",
    "category",
    "drivetrain",
    "power_bhp",
    "weight_kg",
    "aspiration",
    "year",
    "distance_driven",
    "match_score",
    "match_margin",
    "needs_review",
    "raw_name",
    "raw_manufacturer",
]


with OUTPUT_CSV.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(output_rows)


print("Garage canonicalisation complete")
print("================================")
print(f"Raw rows:       {len(raw_rows)}")
print(f"Output rows:    {len(output_rows)}")
print(f"Needs review:   {len(uncertain)}")
print(f"Output:         {OUTPUT_CSV}")

print()

if output_rows:
    first = output_rows[0]
    last = output_rows[-1]

    print(
        "First: "
        f"{first['manufacturer']} - "
        f"{first['name']} "
        f"(GT7 ID {first['gt7_car_id']})"
    )

    print(
        "Last:  "
        f"{last['manufacturer']} - "
        f"{last['name']} "
        f"(GT7 ID {last['gt7_car_id']})"
    )


if uncertain:
    print()
    print("Matches requiring review")
    print("------------------------")

    for item in uncertain:
        print(
            f"{item['position']:3}: "
            f"{item['raw']}"
        )
        print(
            f"     -> {item['match']}"
            f"  score={item['score']:.3f}"
            f"  margin={item['margin']:.3f}"
        )


# Hard validation anchors.
expected_first = (
    "Abarth",
    "1500 Biposto Bertone B.A.T 1 '52",
)

expected_last = (
    "Yangwang",
    "U9 '24",
)

actual_first = (
    output_rows[0]["manufacturer"],
    output_rows[0]["name"],
)

actual_last = (
    output_rows[-1]["manufacturer"],
    output_rows[-1]["name"],
)

if actual_first != expected_first:
    print()
    print("WARNING: first car does not match expected value")
    print(f"Expected: {expected_first}")
    print(f"Actual:   {actual_first}")

if actual_last != expected_last:
    print()
    print("WARNING: last car does not match expected value")
    print(f"Expected: {expected_last}")
    print(f"Actual:   {actual_last}")
