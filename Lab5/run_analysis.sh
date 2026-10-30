#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPORT_DIR="$SCRIPT_DIR/reports"
PYLINTHOME=${PYLINTHOME:-${TMPDIR:-/tmp}/lab5-pylint}
export PYLINTHOME
mkdir -p "$REPORT_DIR"
cd "$SCRIPT_DIR"

if [ ! -f "$SCRIPT_DIR/before/premium_calculator.py" ]; then
    echo "Add the original assigned premium_calculator.py at before/premium_calculator.py to generate baseline reports." >&2
    exit 1
fi

for version in before after; do
    if [ "$version" = "before" ]; then
        target="before/premium_calculator.py"
    else
        target="premium_calculator.py"
    fi
    python -m pylint "$target" > "$REPORT_DIR/${version}_pylint_report.txt" || true
    python -m bandit -r "$target" > "$REPORT_DIR/${version}_bandit_report.txt" || true
    python -m flake8 "$target" > "$REPORT_DIR/${version}_flake8_report.txt" || true
done

echo "Reports saved in $REPORT_DIR"
