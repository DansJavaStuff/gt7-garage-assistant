#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$ROOT/data/reference"

mkdir -p "$DATA_DIR"

echo "Downloading GT7 reference data..."

curl -L \
  https://ddm999.github.io/gt7info/data/db/cars.csv \
  -o "$DATA_DIR/cars.csv"

curl -L \
  https://ddm999.github.io/gt7info/data/db/maker.csv \
  -o "$DATA_DIR/maker.csv"

curl -L \
  https://ddm999.github.io/gt7info/data/db/engineswaps.csv \
  -o "$DATA_DIR/engineswaps.csv"

echo
echo "Downloaded:"
wc -l "$DATA_DIR/cars.csv"
wc -l "$DATA_DIR/maker.csv"
wc -l "$DATA_DIR/engineswaps.csv"
