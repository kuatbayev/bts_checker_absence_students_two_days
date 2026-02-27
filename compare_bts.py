#!/usr/bin/env python3
"""Compare two BTS exam day files by IIN with class filter 7/8/9."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ALLOWED_CLASSES = {"7", "8", "9"}


@dataclass(frozen=True)
class Record:
    iin: str
    variant: str
    raw_line: str


def parse_line(line: str) -> Record | None:
    text = line.rstrip("\n")
    if len(text) < 19 or not text.startswith("056"):
        return None

    iin = text[3:15]
    variant = text[15:19]
    if not (iin.isdigit() and variant.isdigit()):
        return None
    if variant[2] not in ALLOWED_CLASSES:
        return None

    return Record(iin=iin, variant=variant, raw_line=text)


def load_records(path: Path) -> Tuple[Dict[str, Record], List[str]]:
    by_iin: Dict[str, Record] = {}
    skipped: List[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for idx, line in enumerate(f, start=1):
            parsed = parse_line(line)
            if parsed is None:
                skipped.append(f"{path.name}:{idx}")
                continue
            by_iin[parsed.iin] = parsed
    return by_iin, skipped


def write_lines(path: Path, lines: Iterable[str]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line.rstrip("\n") + "\n")


def build_outputs(day1: Dict[str, Record], day2: Dict[str, Record]) -> Tuple[List[str], List[str]]:
    iins_day1 = set(day1)
    iins_day2 = set(day2)

    both = sorted(iins_day1 & iins_day2)
    one_day = sorted(iins_day1 ^ iins_day2)

    both_lines: List[str] = []
    for iin in both:
        both_lines.append(f"=== IIN {iin} ===")
        both_lines.append(f"DAY1: {day1[iin].raw_line}")
        both_lines.append(f"DAY2: {day2[iin].raw_line}")
        both_lines.append("")

    one_day_lines: List[str] = []
    for iin in one_day:
        if iin in day1:
            one_day_lines.append(f"DAY1_ONLY: {day1[iin].raw_line}")
        else:
            one_day_lines.append(f"DAY2_ONLY: {day2[iin].raw_line}")

    return both_lines, one_day_lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare BTS day files (only classes 7/8/9).")
    parser.add_argument("--day1", default="БТС1.txt", help="Path to day 1 file")
    parser.add_argument("--day2", default="БТС2.txt", help="Path to day 2 file")
    parser.add_argument("--both-out", default="eki_kunde_katyskandar.txt", help="Output for both days")
    parser.add_argument("--one-day-out", default="bir_kun_katyskandar.txt", help="Output for one day only")
    args = parser.parse_args()

    day1_records, day1_skipped = load_records(Path(args.day1))
    day2_records, day2_skipped = load_records(Path(args.day2))

    both_lines, one_day_lines = build_outputs(day1_records, day2_records)
    write_lines(Path(args.both_out), both_lines)
    write_lines(Path(args.one_day_out), one_day_lines)

    both_count = len(set(day1_records) & set(day2_records))
    one_day_count = len(set(day1_records) ^ set(day2_records))

    print(f"Done. Both days: {both_count}")
    print(f"One day only: {one_day_count}")
    print(f"Saved: {args.both_out}")
    print(f"Saved: {args.one_day_out}")
    if day1_skipped or day2_skipped:
        print(f"Skipped rows (invalid/filtered): {len(day1_skipped) + len(day2_skipped)}")


if __name__ == "__main__":
    main()
