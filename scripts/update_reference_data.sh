#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/data/reference"

echo "Downloading GT7 car reference data..."

curl -L \
  https://raw.githubusercontent.com/ddm999/gt7info/web-new/_data/db/cars.csv \
  -o "$ROOT/data/reference/cars.csv"

echo
echo "Downloaded:"
wc -l "$ROOT/data/reference/cars.csv"
