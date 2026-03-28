#!/usr/bin/env python
"""Prepare AILuminate subsets for phase evaluations."""

from __future__ import annotations

import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path("eval_frameworks/mlcommons-ailuminate/airr_official_1.0_demo_en_us_prompt_set_release.csv")
AILUMINATE_DEST = Path("evaluation_assets/datasets/ailuminate")
REGRESSION_DEST = Path("evaluation_assets/datasets/regression/seed_30.csv")
SEED = 42


def stratified_sample(rows: list[dict], n: int) -> list[dict]:
    """Return a hazard-stratified sample with deterministic randomness."""
    if n <= 0 or not rows:
        return []

    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row.get("hazard", "unknown")].append(row)

    hazards = sorted(groups)
    if not hazards:
        return []

    rng = random.Random(SEED + n)
    base = n // len(hazards)
    rem = n % len(hazards)

    selected: list[dict] = []
    selected_ids: set[str] = set()

    def row_id(item: dict) -> str:
        for key in ("release_prompt_id", "prompt_hash", "prompt_text"):
            value = item.get(key)
            if value:
                return str(value)
        return str(id(item))

    for idx, hazard in enumerate(hazards):
        target = base + (1 if idx < rem else 0)
        group_rows = groups[hazard]
        take = min(target, len(group_rows))
        picks = rng.sample(group_rows, take)
        selected.extend(picks)
        selected_ids.update(row_id(r) for r in picks)

    # If any groups are undersized, backfill from remaining pool.
    if len(selected) < n:
        remaining = [r for r in rows if row_id(r) not in selected_ids]
        needed = min(n - len(selected), len(remaining))
        if needed > 0:
            fill = rng.sample(remaining, needed)
            selected.extend(fill)

    rng.shuffle(selected)
    return selected[:n]


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to CSV with stable header order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Cannot write empty dataset to {path}")

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"saved {path} ({len(rows)} rows)")


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"Source dataset not found: {SRC}")

    with SRC.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    print(f"loaded source rows: {len(rows)}")

    phase1 = stratified_sample(rows, 100)
    phase2 = stratified_sample(rows, 300)
    seed30 = stratified_sample(phase1, 30)

    write_csv(phase1, AILUMINATE_DEST / "phase1_100.csv")
    write_csv(phase2, AILUMINATE_DEST / "phase2_300.csv")
    write_csv(seed30, REGRESSION_DEST)

    for name, subset in (("phase1_100", phase1), ("phase2_300", phase2), ("seed_30", seed30)):
        dist = Counter(row.get("hazard", "unknown") for row in subset)
        summary = " | ".join(f"{hazard}={count}" for hazard, count in sorted(dist.items()))
        print(f"{name}: {summary}")


if __name__ == "__main__":
    main()
