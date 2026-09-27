# pubg-zone-research

A grey-box research toolkit for competitive PUBG Mobile blue-zone analysis.

The zone algorithm is not a black box. Tencent holds a published patent family
describing a candidate safe-region narrowing routine in a document that names
PUBG explicitly. That turns an open-ended reverse-engineering problem into a
goodness-of-fit problem with an exact null — and collapses the data requirement
from thousands of matches to tens of annotated transitions for the structural
questions.

**Start with `docs/REPORT.md`.** It separates what the prior evidence
establishes, what this repository computed, and what has not been measured.

## Two computed results, no match data required

- **Power analysis** (`bluezone.power`): the literal reading of the patent's
  centre-selection step is falsifiable at power 1.00 with 10 transitions; a mild
  radial bias needs 100-200.
- **Precision ceiling** (`bluezone.cv.synthetic_error_report`): measurement error
  in the key statistic runs from ±0.012 at phase 1 to ±0.79 at phase 8. The late
  circles that matter most tactically cannot be measured from broadcast video.

## Install and verify

```bash
pip install -r requirements.txt
python -m pytest tests/ -q                 # 21 unit tests
python examples/demo_end_to_end.py         # 10 pipeline checks, exits non-zero on failure
python -m bluezone.power                   # regenerates the power table
```

`examples/demo_end_to_end.py` is the one to run first. It generates synthetic
tournaments from a *known* rule, writes them to CSV in the real annotation
schema, and pushes them through the whole pipeline — validation, transition
building, the test battery, the verdict — checking that the rule that comes out
is the rule that went in. A battery that cannot recover a rule it was handed has
no business being trusted on a rule nobody knows.

## Use

```python
from bluezone import Circle, RadiusSchedule, forecast
from bluezone.montecarlo import survival_field, centre_density, highest_density_regions
from bluezone.strategy import expected_value_map, top_positions

current = Circle(x=0.48, y=0.55, r=0.31)
fc = forecast(current, phase=3, schedule=RadiusSchedule(), steps=2, n_samples=20000)

highest_density_regions(centre_density(fc))    # region mass AND region area
ev = expected_value_map(fc, team_position=(0.62, 0.40))
top_positions(ev, k=5)
```

Analysing your own annotations:

```python
from bluezone.schema import load_circles, validate, to_transitions
from bluezone import transition_frame, run_battery, format_battery

circles = load_circles("data/raw/circles.csv")
assert not validate(circles), validate(circles)
print(format_battery(run_battery(transition_frame(to_transitions(circles)))))
```

## Browser tools

The interactive versions of these models live in the website at the top of the
repository (`../website/`): the zone simulator, the probability chart, combat
math, the playbook, and this report rendered as a page. Open
`../website/index.html` by double-clicking; nothing needs building.

The simulator's statistics are a port of `bluezone/tests_stats.py`, and the two
are cross-checked: 200 tournaments generated in the browser (40 per zone rule),
run back through `load_circles -> run_battery -> verdict` in Python, reach the
same conclusion 199 times. The one split was on uniform data, where the browser
raised a false alarm and Python did not — expected, since each verdict may flag
uniform data up to 5% of the time and they are not identical tests (both judge
each marginal test at 0.05 / m; REPORT §5.2). On every non-uniform rule they
agree without exception. Re-run the check whenever you change either side.

## Layout

```
bluezone/
  geometry.py      normalised frame; the (s, theta) transform everything tests
  generative.py    competing hypotheses as samplers, incl. both patent readings
  tests_stats.py   the battery: containment, coupling, marginals, phase, terrain
  power.py         how many transitions each question needs
  montecarlo.py    forecasting: centre density vs survival field
  strategy.py      EV positioning, Dijkstra rotation cost, contention
  schema.py        dataset spec, validation, match-level splits
  cv/extract.py    RANSAC + algebraic circle fitting, error characterisation
tests/             unit tests (python -m pytest tests/ -q)
examples/          end-to-end pipeline check on synthetic tournaments
data/raw/          annotation template (circles.csv)
docs/
  REPORT.md        the technical report - read this first
  PROTOCOL.md      data collection, in priority order
```

## Scope

Published patents, public tournament footage, and ordinary play only. Nothing
here touches game memory, network traffic, the client binary, or anti-cheat, and
nothing should be added that does. Tournament organisers' restrictions on
analytical use of their footage govern regardless of technical feasibility.

## Not yet built

Whitelist estimation from observed centres, Bayesian per-map posteriors, the
sequential and ML model comparison, and the multi-agent contested-rotation model.
All of them need data first, and their structure depends on what the first
10-30 annotated transitions find. Building them now would be fitting to nothing.
