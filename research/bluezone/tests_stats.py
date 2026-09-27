"""
The test battery.

Because the candidate algorithm is specific, the tests can be specific too.
Rather than asking the vague question "is this different from random?", each
test below targets one clause of the exact statement

    s ~ U(0,1)   and   theta ~ U(0,2pi)   and   s independent of theta

with s and theta as defined in `geometry`. Every test returns a `TestResult`
carrying the statistic, a p-value, and a one-line reading in plain language so
that results can go straight into a report without being re-interpreted.

Order matters. Run them in the order listed in `run_battery`: containment first
(it is a hard structural claim and a violation invalidates the definition of s),
then coupling (cheapest decisive test), then the marginals, then terrain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy import stats

from .geometry import TWO_PI, circular_mean_resultant, wrap_pi


@dataclass
class TestResult:
    name: str
    statistic: float
    p_value: float | None
    n: int
    reading: str
    detail: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        p = "n/a" if self.p_value is None else f"{self.p_value:.4g}"
        return f"{self.name:<26} stat={self.statistic:>9.4f}  p={p:>9}  n={self.n:<5}  {self.reading}"


# --------------------------------------------------------------------------- #
# 1. Containment
# --------------------------------------------------------------------------- #


def containment_test(excess: np.ndarray, tol: float = 0.004) -> TestResult:
    """Does the next circle sit entirely inside the previous one?

    `excess` = d - R. Under full containment every value is <= 0 up to
    annotation error. `tol` should be set to your measured circle-fitting error
    (see `cv.validation`), not guessed: a containment "violation" smaller than
    your error bars is a measurement artefact, not a finding.
    """
    n = len(excess)
    violations = int(np.sum(excess > tol))
    frac = violations / n if n else float("nan")
    worst = float(np.max(excess)) if n else float("nan")
    if violations == 0:
        reading = "consistent with full containment"
    else:
        reading = (
            f"{violations}/{n} transitions exceed the containment bound "
            f"(worst {worst:+.4f} map units) - re-check annotation before believing it"
        )
    return TestResult("containment", frac, None, n, reading, {"worst_excess": worst})


# --------------------------------------------------------------------------- #
# 2. Coupling  (the decisive cheap test)
# --------------------------------------------------------------------------- #


def coupling_test(s: np.ndarray, theta: np.ndarray, angle_span: float = TWO_PI) -> TestResult:
    """Test the shared-draw reading of the patent: theta = angle_span * s.

    Under that reading the residual phi = theta - angle_span*s is identically
    zero, so the circular resultant length of phi is 1. Under independent draws
    phi is uniform on the circle and the resultant is ~ 1/sqrt(n).

    The p-value is Rayleigh's, which is accurate for n >= 10 and is what gives
    this test its power at tiny sample sizes: ten clean transitions are enough
    to settle a question that would otherwise be answered by folklore.
    """
    n = len(s)
    phi = wrap_pi(theta - angle_span * s)
    _, rbar = circular_mean_resultant(phi)
    z = n * rbar**2
    p = float(np.exp(-z) * (1 + (2 * z - z**2) / (4 * n))) if n else float("nan")
    p = float(min(max(p, 0.0), 1.0))
    reading = (
        "displacement and bearing are coupled - the shared-draw reading survives, "
        "which would be a major result; re-verify annotation independently"
        if p < 0.01
        else "no coupling; consistent with independent angle and radius draws"
    )
    return TestResult("angle_radius_coupling", rbar, p, n, reading, {"rayleigh_z": z})


# --------------------------------------------------------------------------- #
# 3. Marginals
# --------------------------------------------------------------------------- #


def radial_uniformity_test(s: np.ndarray) -> TestResult:
    """KS test of s = (d/R)^2 against Uniform(0,1).

    Rejection means the centre is not uniform over the admissible disc. The sign
    of the mean shift says which way: s below 0.5 means zones hug the previous
    centre, above 0.5 means they favour the rim.
    """
    n = len(s)
    ks = stats.kstest(s, "uniform")
    mean = float(np.mean(s))
    if ks.pvalue >= 0.05:
        reading = "consistent with centres uniform over the admissible disc"
    else:
        direction = "toward the previous centre" if mean < 0.5 else "toward the rim"
        reading = f"radially non-uniform, biased {direction} (mean s = {mean:.3f} vs 0.5)"
    return TestResult("radial_uniformity_ks", float(ks.statistic), float(ks.pvalue), n, reading,
                      {"mean_s": mean})


def bearing_uniformity_test(theta: np.ndarray) -> TestResult:
    """Rayleigh test for a preferred compass bearing of zone movement.

    A significant result is the "circles drift toward X" claim that every player
    base believes and nobody measures. Note this test only detects a single
    preferred direction; `bearing_kuiper_test` catches multi-modal and
    half-plane structure that Rayleigh is blind to.
    """
    n = len(theta)
    mu, rbar = circular_mean_resultant(theta)
    z = n * rbar**2
    p = float(np.exp(-z) * (1 + (2 * z - z**2) / (4 * n))) if n else float("nan")
    p = float(min(max(p, 0.0), 1.0))
    deg = np.degrees(mu)
    reading = (
        f"directional bias toward bearing {deg:.0f} deg (resultant {rbar:.3f})"
        if p < 0.05
        else "no single preferred bearing"
    )
    return TestResult("bearing_rayleigh", rbar, p, n, reading, {"mean_bearing_deg": float(deg)})


def bearing_kuiper_test(theta: np.ndarray, n_boot: int = 4000, seed: int = 0) -> TestResult:
    """Kuiper's test of theta against the uniform circular distribution.

    Kuiper's V is rotation-invariant, so unlike Rayleigh it detects the
    half-plane reading of the patent (bearings confined to [0, pi)) and any
    multi-modal structure. The null distribution is bootstrapped rather than
    taken from an asymptotic table, which keeps it honest at n < 50.
    """
    n = len(theta)
    rng = np.random.default_rng(seed)

    def V(a: np.ndarray) -> float:
        u = np.sort(a % TWO_PI) / TWO_PI
        i = np.arange(1, len(u) + 1)
        return float(np.max(i / len(u) - u) + np.max(u - (i - 1) / len(u)))

    v = V(theta)
    null = np.array([V(rng.uniform(0, TWO_PI, n)) for _ in range(n_boot)])
    p = float((np.sum(null >= v) + 1) / (n_boot + 1))
    reading = (
        "bearings are not uniform on the circle - check for a half-plane or clustered pattern"
        if p < 0.05
        else "bearings consistent with uniform on the full circle"
    )
    return TestResult("bearing_kuiper", v, p, n, reading)


def independence_test(s: np.ndarray, theta: np.ndarray) -> TestResult:
    """Circular-linear correlation between bearing and normalised displacement.

    Catches softer coupling than `coupling_test`: a tendency for long jumps to
    prefer certain bearings, which is what a terrain whitelist would produce
    once the admissible disc starts clipping the coastline.
    """
    n = len(s)
    c, sn = np.cos(theta), np.sin(theta)
    rxc = float(np.corrcoef(s, c)[0, 1])
    rxs = float(np.corrcoef(s, sn)[0, 1])
    rcs = float(np.corrcoef(c, sn)[0, 1])
    denom = 1 - rcs**2
    r2 = (rxc**2 + rxs**2 - 2 * rxc * rxs * rcs) / denom if abs(denom) > 1e-12 else np.nan
    r2 = float(np.clip(r2, 0.0, 1.0))
    p = float(stats.chi2.sf(n * r2, df=2)) if n > 3 else float("nan")
    reading = (
        "displacement magnitude depends on bearing - look for terrain clipping"
        if p < 0.05
        else "displacement and bearing look independent"
    )
    return TestResult("circular_linear_corr", np.sqrt(r2), p, n, reading)


# --------------------------------------------------------------------------- #
# 4. Phase and terrain structure
# --------------------------------------------------------------------------- #


def phase_homogeneity_test(s: np.ndarray, phase: np.ndarray) -> TestResult:
    """Kruskal-Wallis across phases: is the same rule used at every phase?

    The brief asks whether the algorithm changes between phases. Patch notes for
    the PC title have historically described phase-specific changes (reduced
    probability of extreme zones after the first, a final circle that closes to
    the centre rather than a random spot), so a phase effect is plausible and
    worth isolating before pooling phases in any downstream model.
    """
    groups = [s[phase == p] for p in np.unique(phase) if np.sum(phase == p) >= 5]
    if len(groups) < 2:
        return TestResult("phase_homogeneity", np.nan, None, len(s),
                          "not enough phases with >= 5 observations to test")
    h, p = stats.kruskal(*groups)
    reading = (
        "the radial law differs between phases - fit phases separately"
        if p < 0.05
        else "no phase difference detected in the radial law; pooling phases is defensible"
    )
    return TestResult("phase_homogeneity", float(h), float(p), len(s), reading,
                      {"n_phase_groups": len(groups)})


def terrain_association_test(
    centres: np.ndarray, allowed: np.ndarray, admissible_mass: np.ndarray
) -> TestResult:
    """Binomial test of whether observed centres avoid excluded terrain.

    `allowed[i]` says whether observed centre i fell in the candidate allowed
    region. `admissible_mass[i]` is the fraction of transition i's admissible
    disc that the candidate region covers, i.e. the probability of landing in it
    by chance under the uniform-disc model. Comparing the two is what separates
    "zones avoid water" from "there is not much water inside the disc anyway",
    which is the mistake most published circle analyses make.
    """
    n = len(allowed)
    obs = int(np.sum(allowed))
    exp = float(np.sum(admissible_mass))
    # Poisson-binomial tail via a normal approximation with the exact variance.
    var = float(np.sum(admissible_mass * (1 - admissible_mass)))
    if var <= 0:
        return TestResult("terrain_avoidance", np.nan, None, n,
                          "candidate region covers the whole admissible disc; test is vacuous")
    z = (obs - exp) / np.sqrt(var)
    p = float(2 * stats.norm.sf(abs(z)))
    reading = (
        f"centres favour the candidate region beyond chance ({obs} observed vs {exp:.1f} expected)"
        if p < 0.05 and z > 0
        else f"no terrain preference detected ({obs} observed vs {exp:.1f} expected)"
    )
    return TestResult("terrain_avoidance", z, p, n, reading, {"observed": obs, "expected": exp})


# --------------------------------------------------------------------------- #
# Battery
# --------------------------------------------------------------------------- #


def run_battery(frame: dict[str, np.ndarray], tol: float = 0.004) -> list[TestResult]:
    """Run the full battery on the output of `geometry.transition_frame`."""
    s, th = frame["s"], frame["theta"]
    results = [
        containment_test(frame["excess"], tol=tol),
        coupling_test(s, th),
        coupling_test(s, th, angle_span=np.pi),
        radial_uniformity_test(s),
        bearing_rayleigh := bearing_uniformity_test(th),
        bearing_kuiper_test(th),
        independence_test(s, th),
        phase_homogeneity_test(s, frame["phase"]),
    ]
    results[2].name = "half_span_coupling"
    del bearing_rayleigh
    return results


def format_battery(results: list[TestResult]) -> str:
    return "\n".join(str(r) for r in results)


def verdict(results: list[TestResult]) -> dict:
    """Collapse the battery into a single conclusion, in the order that matters.

    The order is not arbitrary. Containment is a structural claim: if it fails,
    `s` is not even well defined and every test after it is meaningless, so it
    is checked first and short-circuits. Coupling comes next because it is the
    cheapest decisive test. Only once the structure is settled do the marginal
    distribution tests get a say.

    Returns the conclusion plus the evidence it rests on, so that a reader can
    disagree with the reasoning rather than just the answer.
    """
    by = {r.name: r for r in results}

    contain = by.get("containment")
    if contain is not None and contain.statistic > 0.05:
        return {
            "conclusion": "not previous-circle constrained",
            "detail": (
                f"{contain.statistic:.0%} of transitions place the next circle partly "
                "outside the previous one. Either containment does not hold, or the "
                "annotation is wrong. Check annotation before believing this."
            ),
            "rests_on": ["containment"],
            "confident": False,
        }

    # A significant coupling p-value is not sufficient. Under genuine shared-draw
    # coupling the residual is identically zero, so the resultant is 1. But any
    # non-uniform bearing marginal also concentrates the residual: with bearings
    # confined to a half plane and s independent, theta - pi*s is triangular and
    # peaked at zero, which Rayleigh reports as highly significant at a resultant
    # near 0.33. Requiring a near-unit resultant separates a real coupling from
    # that artefact, and lets the half-plane case fall through to the bearing
    # tests where it belongs.
    COUPLED = 0.70

    def coupled(name: str) -> bool:
        r = by.get(name)
        return bool(r and r.p_value is not None and r.p_value < 0.01 and r.statistic >= COUPLED)

    if coupled("angle_radius_coupling"):
        return {
            "conclusion": "shared-draw coupling (patent literal reading)",
            "detail": (
                f"Bearing and normalised displacement are locked together "
                f"(resultant {by['angle_radius_coupling'].statistic:.3f}). This would "
                "make the next centre far more predictable than assumed. Re-annotate "
                "an independent sample before acting on it."
            ),
            "rests_on": ["angle_radius_coupling"],
            "confident": True,
        }

    if coupled("half_span_coupling"):
        return {
            "conclusion": "half-span shared-draw coupling",
            "detail": "Coupling holds against a pi angle span rather than 2*pi.",
            "rests_on": ["half_span_coupling"],
            "confident": True,
        }

    # Family-wise error control. Up to four marginal tests can each raise a flag,
    # and every one is calibrated at alpha on its own. Flagging when ANY fires at
    # 0.05 calls uniform data "non-uniform" far more than 5% of the time —
    # measured at 15.7% over 300 batches of uniform transitions. Bonferroni: each
    # marginal test is judged at alpha / m, which caps the verdict's false-alarm
    # rate at alpha whatever the dependence between the tests.
    FAMILY_ALPHA = 0.05
    marginal = [
        n for n in ("bearing_kuiper", "radial_uniformity_ks", "circular_linear_corr", "phase_homogeneity")
        if n in by and by[n].p_value is not None
    ]
    alpha_each = FAMILY_ALPHA / max(len(marginal), 1)
    flags = [(n, by[n].reading) for n in marginal if by[n].p_value < alpha_each]

    if not flags:
        n = by["radial_uniformity_ks"].n if "radial_uniformity_ks" in by else 0
        return {
            "conclusion": "consistent with uniform over the admissible disc",
            "detail": (
                f"No departure survives testing {len(marginal)} properties at once "
                f"(each judged at {alpha_each:.4f}) at n = {n}. Consult the power table "
                "before reading this as evidence of no effect: a mild radial bias needs "
                "roughly 100-200 transitions to detect."
            ),
            "rests_on": [r.name for r in results],
            "confident": n >= 100,
        }

    return {
        "conclusion": "departs from uniform over the admissible disc",
        "detail": "; ".join(f"{n}: {d}" for n, d in flags),
        "rests_on": [n for n, _ in flags],
        "confident": True,
    }
