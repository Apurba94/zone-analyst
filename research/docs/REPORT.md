# Blue-Zone Analytics: Methodology, Prior Evidence, and Design Results

Status: instrument built, no match data collected. Every empirical claim below
is labelled with what it rests on. Nothing in this document is a measurement of
PUBG Mobile's live behaviour, because no matches have been annotated yet.

---

## 1. Executive summary

The brief asks for a black-box reverse-engineering programme. That framing
should be revised before any data is collected, because the box is not black.

Tencent — the developer and publisher of PUBG Mobile — holds a published patent
family describing a safe-region narrowing algorithm in a document that names
PUBG explicitly. Patents are public documents; reading one is neither reverse
engineering nor a terms-of-service concern. The patent gives a specific,
implementable candidate for the exact routine this project set out to infer.

That changes the shape of the work in three ways.

**The research question sharpens.** Instead of "what distribution generates the
next circle", the question becomes "does the observed data match *this*
distribution", which is a goodness-of-fit problem with an exact null.

**The data requirement collapses.** The computed power analysis in §7 shows
that the structural questions — is the next circle contained in the previous
one, are bearing and displacement coupled, are bearings confined to a half
plane — are settled at **n ≈ 10–30 annotated transitions**. Subtler questions
about radial bias need 100–200. Nobody needs thousands of matches to start.

**A specific, high-value ambiguity appears.** The patent uses the same symbol
for the angle draw and the radius draw. Read literally, bearing and
displacement are deterministically coupled and the next centre lies on a
one-dimensional spiral — which would make the zone far more predictable than
anyone believes. It is very probably a drafting artefact. It is also falsifiable
with about ten observations, at power 1.00. Test it first.

Separately, §4.1 records an exact result that needs no data whatsoever: whenever
the shrink ratio exceeds 0.5, a disc of radius `2r_{t+1} − r_t` around the
current centre cannot be caught outside the next zone, and below 0.5 that
guarantee disappears entirely. Locating the phase where the schedule crosses 0.5
is the cheapest actionable output in this whole document.

The most important negative result is in §8: at broadcast video resolution,
measurement error in the key statistic grows from ±0.012 at phase 1 to ±0.79 at
phase 8. **The late circles that matter most tactically are the ones that cannot
be measured from VODs.** Any study that pools all phases will be dominated by
noise from exactly the phases it most wants to understand.

---

## 2. What the prior evidence actually says

### 2.1 The patent family

US 11,529,559 B2, assigned to Tencent Technology (Shenzhen), inventor Xin Sun,
from Chinese priority application CN 201811369245.6 (filed 16 Nov 2018), with
continuations US 12,017,144 B2 and US 12,515,133 B2. The description defines
PUBG by name and describes, for a large-map shooter, the following:

1. Zone radii per phase are **fixed constants**, decreasing in order, and
   circle *N* is contained within circle *N−1*. Choosing the next zone therefore
   reduces entirely to choosing a centre.
2. The admissible centre region is the disc of radius `R = r_prev − r_next`,
   concentric with the current circle.
3. A random number `r ∈ [0,1]` is drawn. An angle of `r·360` (the text adds "or
   `r·π`") is selected, and a radial offset of `√r · R`.
4. The candidate centre is checked against a **whitelist** of pre-authored map
   regions that exclude terrain unsuitable for combat — the text names sea,
   mountains and cliffs. A candidate outside the whitelist is redrawn, capped at
   about 100 iterations.
5. A distribution map from tens of thousands of internal trials shows: zero
   probability in a border region, low probability in an edge transition band,
   and **equal probability between the map's central and peripheral regions**.

Point 5 is worth dwelling on. It is a direct statement that there is no radial
pull toward the map centre — a belief widespread in player communities. It also
means the observable non-uniformity, if any, comes from the whitelist and the
containment geometry, not from a centre-seeking term.

### 2.2 The three readings of step 3

| Reading | Angle | Radius | Implication for `s = (d/R)²` and bearing `θ` |
|---|---|---|---|
| A — independent draws | `θ ~ U(0, 2π)` | `d = R√u`, `u ~ U(0,1)` | `s ~ U(0,1)`, `θ ~ U(0,2π)`, independent |
| B — shared draw, literal | `θ = 2πu` | `d = R√u`, same `u` | `θ = 2πs` exactly; centres on a spiral |
| C — half span | `θ = πu` | `d = R√u` | bearings confined to a half plane |

Reading A is the textbook way to sample a disc uniformly and is almost certainly
what is implemented. Readings B and C are cheap to eliminate and expensive to
have missed.

### 2.3 What the patent does *not* establish

A patent describes an embodiment, not shipped code, and the priority date is
2018. PUBG Mobile has changed repeatedly since. Publicly documented changes to
the PC title over the same period include a reduced probability of "extreme"
zones far from the previous centre after the first phase, a final circle that
closes to the centre rather than to a random point, and an increasing preference
for land over water toward the end of a match — all of which are phase-dependent
departures from the plain patent model. Whether any of them apply to the Mobile
codebase, which is a separate implementation, is unknown and is precisely what
the data collection is for.

Treat the patent as a sharp prior. Do not cite it as a finding.

### 2.4 Source quality warning

Searches on this topic return a large volume of SEO content carrying confident,
mutually contradictory numbers for zone damage and timings, including
figures that contradict each other within the same site. Several such pages were
encountered while preparing this document. **No zone timing or damage value has
been entered into the phase table in §3 from those sources.** The table is
mostly empty on purpose.

---

## 3. Phase model

The brief asks for a phase-by-phase table and instructs that values must not be
invented. Accordingly:

| Phase | Prev radius | New radius | Shrink time | Wait time | Centre movement | Damage | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | — | — | — | — | ≤ `r₁ − r₂` | — | not measured |
| 2 | — | — | — | — | ≤ `r₂ − r₃` | — | not measured |
| 3–9 | — | — | — | — | ≤ `rₜ − rₜ₊₁` | — | not measured |

The only entries that can be filled without measurement are the maximum centre
displacements, which follow from the containment constraint and are exact *if*
containment holds — itself the first thing to test.

Radii are constants per phase and per map, so this table is cheap to complete
properly: `RadiusSchedule.from_observations()` recovers the whole schedule from
a handful of annotated matches, and the result is reusable indefinitely. Timings
and damage are best measured directly in custom rooms rather than scraped.

Everything downstream — every probability the dashboard reports — is a function
of this table. Until it is filled with measured values, the placeholder shrink
ratio propagates into every number the system produces. This is the single
highest-leverage piece of data collection in the project.

---

## 4. Coordinate system

Normalised map frame: `x, y ∈ [0,1]` with the origin at the north-west corner,
`r` as a fraction of map edge length. Maps of different physical sizes then share
a frame, which is what makes cross-map comparison meaningful.

Each transition reduces to two scalars:

```
R  = r_t − r_{t+1}                  admissible displacement bound
d  = |c_{t+1} − c_t|                observed displacement
s  = (d / R)²                       normalised squared displacement
θ  = atan2(Δy, Δx) mod 2π           bearing
```

The squaring is what makes `s` uniform under Reading A: it is the area-measure
transform for a uniform disc. Comparing raw displacement `d` across phases —
which is what most community analyses do — mixes the radius schedule into the
statistic and destroys the comparison.

### 4.1 An exact consequence: the guaranteed-safe disc

One useful result falls out of the containment constraint alone, with no
distributional assumption and no data at all.

The next centre can move at most `R = r_t − r_{t+1}` from the current one. So a
point at distance `ρ` from the current centre is inside the next circle for
*every* admissible draw when

```
ρ + (r_t − r_{t+1}) ≤ r_{t+1}      ⟺      ρ ≤ 2·r_{t+1} − r_t
```

Two things follow.

**Above a shrink ratio of 0.5, there is a disc of ground that cannot be caught
outside.** Its radius is `2r_{t+1} − r_t`, and the current circle's centre is
always inside it. Dead centre is not merely a good bet at those ratios; it is
risk-free with respect to the zone.

**Below 0.5 the guarantee vanishes completely.** The circle can shrink past its
own centre, and no ground is safe. The phase at which the schedule crosses 0.5
is therefore the phase at which centre play stops being free — and locating that
crossover is a pure measurement of the radius schedule, needing no zone
observations at all beyond the radii themselves.

Because total centre drift telescopes, the same formula extends to a `k`-phase
horizon by substituting `r_{t+k}`. The disc shrinks quickly with `k`, which is
the exact sense in which a long-horizon guarantee is unavailable.

This is implemented as `geometry.guaranteed_safe_radius` and verified in the
test suite by checking that no point of the disc ever falls outside 20,000
sampled circles. It is drawn as the dotted inner ring on the interactive chart.

---

## 5. Hypothesis set

The brief's hypotheses A–H map onto this frame as follows.

| Brief | Restated as a testable claim | Test | Implemented as |
|---|---|---|---|
| A uniform random | containment fails; `d > R` occurs | `containment_test` | `UniformMapModel` |
| B previous-circle constrained | `s ~ U(0,1)`, `θ ~ U(0,2π)`, independent | `radial_uniformity_test` | `AdmissibleDiscModel` |
| C weighted random | `s ~ Beta(a,b)`, `a,b ≠ 1` | `radial_uniformity_test` | `EdgeBiasedDiscModel` |
| D terrain-aware | centres avoid excluded terrain beyond disc geometry | `terrain_association_test` | `WhitelistRejection` |
| E water-aware | special case of D | `terrain_association_test` | mask parameter |
| F map-geometry-aware | edge band with zero density | whitelist estimation | `coast_band_mask` |
| G phase-dependent | `s` distribution differs by phase | `phase_homogeneity_test` | per-phase fitting |
| H hybrid | B ∧ D ∧ G | full battery | composed models |
| — (new) patent literal | `θ = 2πs` exactly | `coupling_test` | `CoupledSpiralModel` |
| — (new) half span | `θ` confined to a half plane | `bearing_kuiper_test` | `angle_span = π` |

Hypothesis D deserves a note on how it is tested, because the usual version of
this test is wrong. Asking "do zone centres land on land more often than water?"
compares against the wrong baseline — the admissible disc may barely contain any
water in the first place. `terrain_association_test` compares the observed rate
against the *disc-restricted* expected rate, transition by transition, using a
Poisson-binomial null. That is the difference between measuring the algorithm
and measuring the map.

### 5.1 A confound found by running the battery against itself

Running the pipeline on synthetic data generated from a known rule caught a
false-positive mode that would have produced a spectacular wrong answer on real
data.

The coupling test asks whether the residual `φ = θ − span·s` concentrates. Under
genuine shared-draw coupling `φ ≡ 0` and the circular resultant is 1. But *any*
non-uniform bearing marginal also concentrates `φ`: with bearings confined to a
half plane and `s` drawn independently, `θ − π·s` is triangular and peaked at
zero, and Rayleigh reports it as highly significant at a resultant near 0.33.

So a significant coupling p-value is not evidence of coupling. The resultant has
to be near 1. `verdict()` requires ≥ 0.70 for that reason, and the half-plane
case now falls through to the bearing tests where it belongs.

The general lesson applies beyond this one test: several tests in the battery
share the same inputs, and a departure in one marginal leaks into tests aimed at
something else. Read the whole battery before drawing a conclusion, never one
line of it.

### 5.2 A second one: testing several things at once

Rendering the simulator during packaging surfaced a related problem. For data
generated by the uniform-disc rule, the verdict reported "departs from uniform"
in about one batch in ten.

No single test was at fault. Each marginal test is calibrated on its own — on
uniform data the radial KS test fired 5.4% of the time and Kuiper 5.0%, against
a nominal 5%. But the verdict flagged a departure when *any* of them fired, and
the chance that at least one of several independent 5% tests fires is well
above 5%. Measured on uniform data:

| Verdict | Marginal tests | False alarms before | After Bonferroni |
|---|---|---|---|
| Simulator and app | 2 | 10.1% (2,000 batches) | 4.8% |
| Python battery | 4 | 15.7% (300 batches) | 4.0% |

The verdict now judges each of the *m* marginal tests at 0.05 / *m*, which caps
its false-alarm rate at 5% whatever the dependence between the tests. The cost
in power is small: at 25 matches the simulator still identifies every non-uniform
rule 100% of the time, and the Python verdict still detects a *mild* pull toward
the previous centre (Beta(0.7, 1)) in 88.7% of 175-transition batches.

The power table in §7 is unaffected — it describes each test on its own at 0.05.
A conclusion drawn from the verdict needs slightly more data than that table
implies, because the verdict is deliberately stricter than any one test.

---

## 6. Whitelist cartography

The whitelist is the one component of the model with genuine reconstruction
value, because it is map-specific authored content rather than a formula.

Its signature is regions where centres never land despite the geometry
permitting it. With enough observed centres and their admissible discs, the
whitelist can be estimated: for each map cell, compare the number of times a
centre landed there against the number of times a centre *could* have landed
there. Cells with high opportunity and zero landings are excluded terrain.

This is a coverage-limited estimate — cells that rarely fall inside any
admissible disc will stay unknown for a long time — and the estimate should
carry per-cell confidence rather than being rendered as a hard boundary. The
rejection cap noted in §2.1 also means the exclusion is not absolute: when the
admissible disc barely intersects the whitelist, a small amount of probability
leaks into excluded terrain. That leak is itself a testable signature.

Not implemented yet. It needs data first, and its structure depends on what
§7's tests find.

---

## 7. Computed result: how much data is needed

Simulated power of the battery at α = 0.05, 400 trials per cell. Data are
generated from each scenario; the figure is the fraction of trials where the
test correctly rejects.

| Scenario | Test | n=10 | n=20 | n=30 | n=50 | n=100 | n=200 | n=400 |
|---|---|---|---|---|---|---|---|---|
| shared-draw spiral (patent literal reading) | coupling | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| half-plane bearings | kuiper | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| mild pull toward previous centre | radial | 0.16 | 0.24 | 0.28 | 0.55 | 0.81 | 0.98 | 1.00 |
| strong pull toward previous centre | radial | 0.54 | 0.76 | 0.94 | 0.99 | 1.00 | 1.00 | 1.00 |
| mild pull toward the rim | radial | 0.15 | 0.24 | 0.34 | 0.47 | 0.77 | 0.98 | 1.00 |
| no previous-circle constraint | radial | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| true uniform disc (false-positive rate) | radial | 0.04 | 0.05 | 0.04 | 0.04 | 0.04 | 0.04 | 0.03 |

The false-positive row confirms the battery is calibrated: 0.03–0.05 against a
nominal 0.05.

Reading this as an annotation budget:

- **10 transitions** settle containment, coupling, and the half-plane reading.
  That is roughly two matches. Do this before anything else.
- **30 transitions** detect a strong radial bias at 94% power.
- **100–200 transitions** are needed for a mild bias, and this is the regime any
  realistic departure from the patent model probably lives in.
- Beyond 400, the marginal return on more of the *same* measurement is small.
  Effort is better spent on phase-stratified sampling and on cross-map coverage.

Because a mild bias needs ~200 transitions and each match yields at most 8, a
per-map, per-phase analysis needs on the order of 25–30 matches per map for the
pooled tests, and considerably more to stratify by phase. Plan for that shape,
not for "as many as possible".

---

## 8. Computed result: the measurement precision ceiling

The RANSAC + algebraic circle fitter was characterised against rendered circles
with known ground truth, 150 trials per condition. Errors are fractions of map
edge length.

| Condition | Centre error (median) | Centre p95 | Radius error (median) | Radius p95 |
|---|---|---|---|---|
| Full circle | 0.00110 | 0.00203 | 0.00081 | 0.00147 |
| 90° arc | 0.00113 | 0.00188 | 0.00077 | 0.00172 |
| 45° arc | 0.00180 | 0.00499 | 0.00114 | 0.00432 |

On an 8×8 km map, 0.0011 map units is about 9 metres. The fitter holds up well
on clipped arcs down to 90°, which matters because minimap views rarely show a
complete circle.

Now propagate that into `s`. Since `s = (d/R)²` divides by a *difference* of two
fitted radii, the error is amplified as the circles get small:

| Phase | `R` | Relative error in `R` | Error in `s` at `s = 0.5` |
|---|---|---|---|
| 1 | 0.2790 | 0.4% | ±0.012 |
| 2 | 0.1535 | 0.7% | ±0.022 |
| 3 | 0.0844 | 1.4% | ±0.040 |
| 4 | 0.0464 | 2.5% | ±0.072 |
| 5 | 0.0255 | 4.5% | ±0.131 |
| 6 | 0.0140 | 8.1% | ±0.238 |
| 7 | 0.0077 | 14.8% | ±0.434 |
| 8 | 0.0042 | 26.9% | ±0.788 |

(Using the placeholder radius schedule; the qualitative pattern is
schedule-independent, since `R` shrinks geometrically whatever the ratios are.)

`s` lives on [0,1]. By phase 7 the measurement uncertainty covers nearly half
that range, and by phase 8 it covers the whole of it. **Phases 1–4 carry
essentially all of the usable signal available from broadcast footage.**

Three consequences:

1. Do not pool phases. A pooled test is dominated by noise contributed by the
   phases with the least information.
2. Community claims about late-circle patterns are, at the precision anyone
   outside the studio actually has, unfalsifiable. Treat them accordingly.
3. If late phases must be studied, the measurement method has to change:
   full-screen map captures at native resolution, custom rooms where the
   observer controls the camera, or frame-averaging across many frames of a
   static circle. Not minimap fits from a 1080p stream.

---

## 9. What the system will and will not tell an analyst

The forecast engine produces two distinct fields, and conflating them is the
most common error in this genre:

- **Centre density** — where the next circle's centre will be. This is what
  every community heatmap shows.
- **Survival field** — the probability that a team standing at a point is still
  inside the zone. This is what positioning decisions actually depend on.

They differ substantially. A point well off-centre can have high survival
probability because it falls inside many sampled circles, while a point at the
mode of the centre density gains little if the circle is large. The strategy
layer scores positions on the survival field, penalised by rotation cost from a
Dijkstra pass over a traversability grid, and by a contention term that reflects
the obvious fact that every other team is looking at the same map.

Multi-phase lookahead compounds uncertainty at the rate the game does. The
three-step field is close to flat, which is the correct answer, and the system
reports it as such rather than manufacturing a confident-looking mode.

The honest form of an output is: *"Region A holds an estimated 34% of the
next-centre probability mass and covers 9% of the map; region B holds 21% over
6%."* An estimate that spreads 90% of the mass over 60% of the map is not a
prediction, and `highest_density_regions` reports region area alongside every
probability so that this cannot be hidden.

---

## 10. Player distribution

The brief asks whether player positions influence future zones. Two things must
be separated.

**Zone centre selection.** The patent's routine takes no player-position input.
If the shipped implementation matches, player distribution cannot influence
where the circle goes, and any apparent correlation is either coincidence,
selection effect, or reverse causation — players rotate toward where they
*expect* the zone, so surviving players cluster near zone centres by their own
choice. This confound is severe and is the reason essentially every community
claim on this topic is uninterpretable.

**Zone timing and damage.** Separately, the PC title has documented "dynamic
blue zone" behaviour keyed to survivor count on some maps. That is a real
player-count dependency, but it acts on timing and damage, not on location.

Conflating the two produces the widespread belief that "the circle follows
players". Test them as separate claims with separate data.

The only clean test of the location claim available without studio access is a
custom room with players deliberately clustered in a known region, repeated
enough times to compare the centre distribution against the disc-uniform null.
That is feasible and cheap, and it is the recommended way to settle this.

---

## 11. Validation plan

Split by match, never by transition — transitions within a match share a first
circle and a radius schedule, so a random split leaks. `schema.match_level_split`
enforces this.

Because the model is a probability distribution rather than a point predictor,
evaluate it as one:

- **Log score** of the observed centre under the predicted density, against the
  disc-uniform baseline. Positive mean improvement is the only meaningful sense
  in which the model "beats chance".
- **PIT calibration** on `s`: transform each observed value through the
  predicted CDF and test the result for uniformity. A model can rank well and
  still be badly calibrated, and calibration is what makes a stated 34% mean 34%.
- **Coverage** of the stated 50/75/90/95% regions on held-out matches, reported
  with region area.
- **Cross-map and cross-tournament** held-out sets, since whitelist geometry is
  map-specific by construction and patch-specific in practice.

A model that improves the log score on training matches but not on unseen ones
has fitted the annotation, not the algorithm.

---

## 12. Limitations

- No match data has been collected. Nothing here is a measurement of live
  behaviour.
- The radius schedule is a placeholder and propagates into every probability.
- The whitelist is unknown; the coast-band mask is a crude stand-in, labelled as
  such in code.
- Late-phase measurement is precision-limited as quantified in §8.
- The patent may not describe shipped code, and may be out of date.
- Esports rooms may use different zone parameters from public matches; this is
  untested and would invalidate pooling the two.
- The contention term in the strategy layer is a heuristic proxy, not a
  game-theoretic equilibrium.

---

## 13. Recommended sequence

1. Fill the radius schedule from ~5 annotated matches per map. Everything else
   depends on it.
2. Annotate 10 transitions. Run containment, coupling, and Kuiper. This is a
   day's work and eliminates or confirms three hypotheses outright.
3. Characterise your own annotation error on your own footage before trusting
   any tolerance.
4. Extend to ~200 transitions on one map, phases 1–4 only, and test for radial
   and phase structure.
5. Only then begin whitelist estimation, and only on the map with the best
   coverage.
6. Custom-room experiments for the player-distribution question and for late
   phases, where VOD precision runs out.

---

## 14. Ethics and scope

Everything in this project uses published patent documents, publicly broadcast
tournament footage, and observations made by playing the game normally. No
component touches game memory, network traffic, the client binary, or anti-cheat
systems, and none should be added. If a tournament organiser restricts
analytical use of their VODs, that restriction governs regardless of what is
technically possible.

---

## Sources

- US 11,529,559 B2, "Method and device for adjusting region, storage medium, and
  electronic device", Tencent Technology (Shenzhen), inventor Xin Sun; priority
  CN 201811369245.6, 16 Nov 2018. Continuations US 12,017,144 B2 and
  US 12,515,133 B2.
- PUBG Corp. patch notes describing blue-zone changes to the PC title (reduced
  probability of extreme safe zones after the first, final circle closing to the
  centre, increased land preference late in a match).
- PUBG community wiki, on dynamic blue-zone behaviour keyed to survivor count.

Power and precision figures in §7 and §8 were computed by `bluezone.power` and
`bluezone.cv.synthetic_error_report` in this repository and are reproducible with
`python -m bluezone.power`.
