#!/usr/bin/env bash
# Fetch all LC problem JSONs for a given rating band via the LC GraphQL API.
#
# Usage:
#   ./fetch_band.sh <min_rating> <max_rating> [band_tag]
#
# Example:
#   ./fetch_band.sh 2600 2700 2600_2699
#   → creates problem-content-cache/band_2600_2699/ and fills it.
#
# Idempotent: skips problems already cached.

set -e

if [ $# -lt 2 ]; then
  echo "Usage: $0 <min_rating> <max_rating> [band_tag]"
  echo "Example: $0 2600 2700 2600_2699"
  exit 1
fi

MIN_R="$1"
MAX_R="$2"
BAND_TAG="${3:-${MIN_R}_$((MAX_R - 1))}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RATINGS_TSV="$ROOT/ratings.tsv"
CACHE_DIR="$ROOT/problem-content-cache/band_${BAND_TAG}"
SLUGS_FILE="$ROOT/slugs/all_${MIN_R}_slugs.txt"

if [ ! -f "$RATINGS_TSV" ]; then
  echo "ratings.tsv not found at $RATINGS_TSV"
  exit 1
fi

mkdir -p "$CACHE_DIR" "$(dirname "$SLUGS_FILE")"

# Extract slugs for this band (column 5 in ratings.tsv)
awk -F'\t' -v lo="$MIN_R" -v hi="$MAX_R" \
  'NR>1 && $1 >= lo && $1 < hi { print $5 }' \
  "$RATINGS_TSV" | sort -u > "$SLUGS_FILE"

TOTAL=$(wc -l < "$SLUGS_FILE")
echo "Band ${BAND_TAG}: $TOTAL problems to fetch into $CACHE_DIR"

i=0
while IFS= read -r slug; do
  i=$((i + 1))
  if [ ! -f "$CACHE_DIR/${slug}.json" ]; then
    resp=$(curl -s -X POST https://leetcode.com/graphql/ \
      -H 'Content-Type: application/json' \
      -H 'Referer: https://leetcode.com/problems/' \
      -d "{\"query\":\"query { question(titleSlug: \\\"${slug}\\\") { questionId title content difficulty } }\",\"variables\":{}}")
    echo "$resp" > "$CACHE_DIR/${slug}.json"
    sleep 0.15
    if [ $((i % 20)) -eq 0 ]; then
      echo "  fetched $i/$TOTAL"
    fi
  fi
done < "$SLUGS_FILE"

CACHED=$(ls "$CACHE_DIR" | wc -l | tr -d ' ')
echo "Done. $CACHED files in $CACHE_DIR"

# Auto-run extractor if available
EXTRACTOR="$ROOT/scripts/extract_all.py"
TSV_OUT="$ROOT/content-tsv/all_${MIN_R}_with_content.tsv"
if [ -f "$EXTRACTOR" ]; then
  mkdir -p "$(dirname "$TSV_OUT")"
  python3 "$EXTRACTOR" "$CACHE_DIR" "$RATINGS_TSV" "$MIN_R" "$MAX_R" > "$TSV_OUT"
  echo "Content TSV written to $TSV_OUT"
fi
