#!/usr/bin/env python3
"""
Rebuild data.json for this repo from Automation/thonglor_all_months.json
(the pipeline's output, which lives one level up at ../../Automation/).

Run this after every `python3 thonglor_dashboard_pipeline.py`, from this
directory:   python3 build_data_json.py

Why this script exists: index.html's loadBranchGlobals() requires each
branch object to have `available_keys`, `overdue_by_date` and
`overdue_by_month` (NOT a raw `overdue` key) - this is the exact shape
below. Hand-rebuilding data.json without this script has regressed to the
wrong shape twice (missing available_keys entirely breaks the dashboard
on first load, not just branch switching - see git history around
"restore label/year_scanned" and "fix data.json schema regression").

available_keys must sort numerically by (year, month), not as strings -
plain `sorted()` puts "2026-10" before "2026-2" and breaks "default to
the latest month" once a branch has a double-digit month.
"""
import json
import subprocess
import sys


def month_sort_key(k):
    y, m = k.split('-')
    return (int(y), int(m))


def main():
    with open("../../Automation/thonglor_all_months.json", "r", encoding="utf-8") as f:
        payload = json.load(f)

    branches = payload['branches']
    out = {}
    for bkey, bval in branches.items():
        months = bval['months']
        available_keys = sorted(months.keys(), key=month_sort_key)
        overdue = bval.get('overdue', {})
        overdue_by_date = overdue.get('by_date', overdue.get('overdue_by_date', {}))
        overdue_by_month = overdue.get('by_month', overdue.get('overdue_by_month', {}))
        out[bkey] = {
            'key': bkey,
            'label': bval.get('label', bkey.capitalize()),
            'year_scanned': bval.get('year_scanned'),
            'months': months,
            'available_keys': available_keys,
            'overdue_by_date': overdue_by_date,
            'overdue_by_month': overdue_by_month,
        }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

    for bkey, bval in out.items():
        last = bval['available_keys'][-1] if bval['available_keys'] else None
        date_range = bval['months'][last]['date_range'] if last else 'no months'
        print(f"{bkey}: {len(bval['available_keys'])} months, latest = {last} ({date_range})")
    print("data.json rebuilt OK.")


if __name__ == '__main__':
    main()
