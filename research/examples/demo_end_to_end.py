"""
End-to-end pipeline exercise on synthetic tournaments.

This is not a study of PUBG Mobile. It generates matches from a *known* rule,
pushes them through the whole pipeline exactly as real annotations would go —
CSV on disk, schema validation, transition building, the test battery, the
verdict — and checks that the answer that comes out is the rule that went in.

That is the only way to know the instrument works before pointing it at real
data. A battery that cannot recover a rule it was handed has no business being
trusted on a rule nobody knows.

Run:  python examples/demo_end_to_end.py
"""

from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bluezone.generative import (  # noqa: E402
    AdmissibleDiscModel, CoupledSpiralModel, EdgeBiasedDiscModel,
    RadiusSchedule, UniformMapModel, WhitelistRejection, coast_band_mask,
)
from bluezone.geometry import Circle, guaranteed_safe_radius, transition_frame  # noqa: E402
from bluezone.montecarlo import (  # noqa: E402
    forecast, centre_density, highest_density_regions, probability_point_safe,
)
from bluezone.schema import (  # noqa: E402
    REQUIRED, OPTIONAL, load_circles, match_level_split, to_transitions, validate,
)
from bluezone.strategy import expected_value_map, top_positions  # noqa: E402
from bluezone.tests_stats import format_battery, run_battery, verdict  # noqa: E402

RULE = "=" * 78


def synth_tournament(model, n_matches: int, path: Path, schedule=None, seed=0) -> Path:
    """Write a synthetic tournament to CSV in the real annotation schema."""
    schedule = schedule or RadiusSchedule(r0=0.55, default_ratio=0.62, n_phases=8)
    radii = schedule.radii()
    rng = np.random.default_rng(seed)

    rows = []
    for m in range(n_matches):
        mid = f"SYNTH-D{m // 6 + 1}-M{m % 6 + 1}"
        r0 = radii[0]
        c = rng.uniform(r0, 1 - r0, size=2) if r0 < 0.5 else np.array([0.5, 0.5])
        alive = 64
        for ph in range(len(radii)):
            rows.append({
                "match_id": mid, "map_name": "synthetic", "phase": ph + 1,
                "x": round(float(c[0]), 5), "y": round(float(c[1]), 5),
                "r": round(float(radii[ph]), 5),
                "source": f"synthetic://{model.name}/seed{seed}/m{m}/p{ph+1}",
                "n_alive": alive, "fit_quality": "good",
                "timestamp": "", "notes": "",
            })
            if ph + 1 < len(radii):
                prev = Circle(c[0], c[1], radii[ph])
                c = model.sample_centres(prev, radii[ph + 1], 1, rng)[0]
                alive = max(2, alive - int(rng.integers(4, 12)))

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REQUIRED + OPTIONAL)
        w.writeheader()
        w.writerows(rows)
    return path


def run_case(label: str, model, expect: str, n_matches: int, tmp: Path, seed: int) -> bool:
    print(f"\n{RULE}\nGROUND TRUTH: {label}   ({n_matches} matches)\n{RULE}")

    csv_path = synth_tournament(model, n_matches, tmp / f"{model.name}_{seed}.csv", seed=seed)
    circles = load_circles(csv_path)
    problems = validate(circles)
    print(f"  loaded {len(circles)} circles from {csv_path.name}; "
          f"validation problems: {len(problems)}")
    if problems:
        for p in problems[:3]:
            print(f"    ! {p}")

    transitions = to_transitions(circles)
    frame = transition_frame(transitions)
    print(f"  built {len(transitions)} transitions "
          f"(dropped {int(frame['n_dropped'])} for non-positive shrink)\n")

    results = run_battery(frame)
    print(format_battery(results))

    v = verdict(results)
    ok = v["conclusion"] == expect
    print(f"\n  verdict:  {v['conclusion']}")
    print(f"  expected: {expect}")
    print(f"  -> {'MATCH' if ok else 'MISMATCH'}")
    return ok


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="bluezone-demo-"))
    passed = []

    # --- 1. can the battery recover the rule it was handed? -----------------
    cases = [
        ("uniform over the admissible disc", AdmissibleDiscModel(),
         "consistent with uniform over the admissible disc", 30, 1),
        ("shared-draw spiral (patent literal reading)", CoupledSpiralModel(),
         "shared-draw coupling (patent literal reading)", 2, 2),
        ("strong pull toward the previous centre", EdgeBiasedDiscModel(a=0.4, b=1.0),
         "departs from uniform over the admissible disc", 12, 3),
        ("no containment constraint", UniformMapModel(),
         "not previous-circle constrained", 8, 4),
        ("half-plane bearings", AdmissibleDiscModel(angle_span=np.pi),
         "departs from uniform over the admissible disc", 8, 5),
    ]
    for label, model, expect, n, seed in cases:
        passed.append(run_case(label, model, expect, n, tmp, seed))

    # --- 2. does validation catch a corrupted annotation? -------------------
    print(f"\n{RULE}\nVALIDATION: a deliberately corrupted file\n{RULE}")
    bad = tmp / "corrupted.csv"
    synth_tournament(AdmissibleDiscModel(), 3, bad, seed=9)
    lines = bad.read_text().splitlines()
    del lines[4]                                    # drop a phase mid-match
    lines[6] = lines[6].replace("synthetic", "", 1)  # blank a map name field
    parts = lines[8].split(",")
    parts[4] = "1.7"                                 # y outside [0,1]
    lines[8] = ",".join(parts)
    bad.write_text("\n".join(lines) + "\n")

    problems = validate(load_circles(bad))
    for p in problems:
        print(f"  ! {p}")
    caught = len(problems) >= 2
    print(f"  -> {'CAUGHT' if caught else 'MISSED'} ({len(problems)} problems)")
    passed.append(caught)

    # --- 3. whitelist rejection leaves a visible signature ------------------
    print(f"\n{RULE}\nWHITELIST: does terrain rejection show up in the data?\n{RULE}")
    wl = WhitelistRejection(AdmissibleDiscModel(), coast_band_mask(0.18))
    csv_path = synth_tournament(wl, 25, tmp / "whitelist.csv", seed=6)
    circles = load_circles(csv_path)
    xs = np.array([c["x"] for c in circles])
    ys = np.array([c["y"] for c in circles])
    in_band = np.mean((xs > 0.18) & (xs < 0.82) & (ys > 0.18) & (ys < 0.82))
    print(f"  {len(circles)} centres, {in_band:.1%} inside the allowed band")
    print("  (the excluded band is empty by construction; recovering its *shape*")
    print("   from real data is the whitelist-cartography task in REPORT.md §6)")
    passed.append(in_band > 0.95)

    # --- 4. match-level splitting -------------------------------------------
    print(f"\n{RULE}\nSPLITTING: no match may appear on both sides\n{RULE}")
    ts = to_transitions(load_circles(tmp / "admissible_disc_1.csv"))
    tr, va, te = match_level_split(ts, seed=3)
    ids = [{t.match_id for t in s} for s in (tr, va, te)]
    overlap = (ids[0] & ids[1]) | (ids[0] & ids[2]) | (ids[1] & ids[2])
    print(f"  {len(tr)}/{len(va)}/{len(te)} transitions over "
          f"{len(ids[0])}/{len(ids[1])}/{len(ids[2])} matches; overlap: {overlap or 'none'}")
    passed.append(not overlap)

    # --- 5. forecasting and the exact guarantee -----------------------------
    print(f"\n{RULE}\nFORECAST: probabilities from a live circle\n{RULE}")
    sched = RadiusSchedule(r0=0.55, default_ratio=0.62, n_phases=8)
    phase, r_now = 3, sched.radius(3)
    cur = Circle(0.46, 0.52, r_now)
    print(f"  current circle: centre ({cur.x}, {cur.y}), r = {r_now:.4f}, phase {phase}")

    for steps in (1, 2, 3):
        fc = forecast(cur, phase, sched, steps=steps, n_samples=30000, seed=11)
        hdr = highest_density_regions(centre_density(fc))
        at_centre = probability_point_safe(fc, cur.centre)
        rho = guaranteed_safe_radius(r_now, float(fc.radii[-1]))
        a90 = hdr[0.9]["area_fraction"]
        print(f"    {steps} phase(s) ahead: 90% of centre mass over {a90:6.2%} of the map | "
              f"P(current centre safe) = {at_centre:5.1%} | guaranteed disc r = {rho:.4f}")

    ratios = [0.62, 0.55, 0.50, 0.45]
    print("\n  guaranteed-safe disc vs shrink ratio (exact, no model assumed):")
    for k in ratios:
        print(f"    ratio {k:.2f} -> {guaranteed_safe_radius(r_now, r_now * k):.5f}")
    crossover_ok = (guaranteed_safe_radius(r_now, r_now * 0.55) > 0
                    and guaranteed_safe_radius(r_now, r_now * 0.45) == 0)
    passed.append(crossover_ok)

    # --- 6. strategy layer ---------------------------------------------------
    print(f"\n{RULE}\nSTRATEGY: where should a stranded team go?\n{RULE}")
    fc = forecast(cur, phase, sched, steps=2, n_samples=20000, seed=12)
    team = (0.80, 0.24)
    ev = expected_value_map(fc, team_position=team, grid=140)
    print(f"  team at {team}, zone centred ({cur.x}, {cur.y})")
    for i, p in enumerate(top_positions(ev, k=3), 1):
        print(f"    {i}. ({p['x']:.3f}, {p['y']:.3f})  survival {p['survival']:.1%}  "
              f"rotation {p['rotation_cost']:.2f}  contention {p['contention']:.2f}")
    best = top_positions(ev, k=1)[0]
    moved = np.hypot(best["x"] - team[0], best["y"] - team[1]) > 0.2
    print(f"  -> recommends moving: {moved}")
    passed.append(moved and best["survival"] > 0.3)

    print(f"\n{RULE}")
    print(f"{sum(passed)}/{len(passed)} pipeline checks passed")
    print(RULE)
    return 0 if all(passed) else 1


if __name__ == "__main__":
    raise SystemExit(main())
