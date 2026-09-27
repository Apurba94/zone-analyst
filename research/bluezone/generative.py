"""
Competing generative models for the next-circle centre.

Each model is a sampler: given the current circle and the next radius, draw
candidate next centres. They are written so that the *only* thing that differs
between hypotheses is how the centre offset is drawn, which is what makes the
model-comparison in `tests_stats` clean.

Origin of the two patent readings
---------------------------------
Tencent's published patent family (US 11,529,559 B2; continuations
US 12,017,144 B2, US 12,515,133 B2; priority CN 201811369245.6) describes, for
an FPS whose description explicitly names PUBG, a safe-region narrowing routine:

  * circle radii per phase are FIXED, decreasing, and circle N is contained in
    circle N-1, so choosing the region reduces to choosing a centre;
  * the admissible centre region is the disc of radius R = r_prev - r_next;
  * a random number r in [0,1] is drawn; an angle of "r*360 (or r*pi)" is
    selected; and a radial offset of sqrt(r) * R is selected;
  * the candidate centre is checked against a *whitelist* of pre-authored map
    regions that exclude terrain unsuitable for combat (sea, mountains,
    cliffs); on failure the draw is repeated, up to about 100 iterations.

The patent text is ambiguous in a way that matters enormously here. It uses the
same symbol `r` for the angle draw and for the radial draw. Two readings:

  READING A (independent):  th ~ U(0,2pi),  u ~ U(0,1),  d = R*sqrt(u)
      -> centres uniform over the admissible disc; s = (d/R)^2 ~ U(0,1);
         s and th independent. This is the standard, and almost certainly
         intended, way to sample a disc uniformly.

  READING B (shared draw):  u ~ U(0,1),  th = 2*pi*u,  d = R*sqrt(u)
      -> centres lie on a one-dimensional spiral inside the disc. Bearing and
         displacement are then *deterministically coupled*: th = 2*pi*s.

Reading B is very probably a drafting artefact. But it is also trivially
falsifiable: under B, a scatter of th against s is a straight line, and roughly
ten clean observations settle it. Test it first and cheaply; the cost of not
testing it is missing a coupling that would be worth an enormous amount to a
competitive team. The angle range ambiguity ("r*360 (or r*pi)") gives a third
variant with bearings confined to a half plane.

A patent describes an embodiment, not necessarily shipped code, and PUBG Mobile
has changed repeatedly since the 2018 priority date. Treat all of this as a
sharp prior to be tested against observation, never as a settled answer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

import numpy as np

from .geometry import Circle, TWO_PI

Mask = Callable[[np.ndarray], np.ndarray]  # (N,2) points -> (N,) bool "allowed"


class ZoneModel(Protocol):
    name: str

    def sample_centres(
        self, prev: Circle, next_radius: float, n: int, rng: np.random.Generator
    ) -> np.ndarray:
        """Return an (n, 2) array of candidate next-circle centres."""
        ...


# --------------------------------------------------------------------------- #
# Baselines and patent readings
# --------------------------------------------------------------------------- #


@dataclass
class UniformMapModel:
    """Hypothesis A from the brief: no dependence on the previous circle.

    The next centre is uniform over all positions keeping the circle inside the
    map. This is the null the whole project exists to reject; it is included so
    that "better than chance" has a defined meaning.
    """

    name: str = "uniform_map"

    def sample_centres(self, prev, next_radius, n, rng):
        lo, hi = next_radius, 1.0 - next_radius
        if hi <= lo:
            return np.tile(np.array([0.5, 0.5]), (n, 1))
        return rng.uniform(lo, hi, size=(n, 2))


@dataclass
class AdmissibleDiscModel:
    """Patent READING A: uniform over the admissible disc.

    Equivalent to Hypothesis B in the brief, with the geometric constraint made
    explicit. `angle_span` = pi reproduces the half-plane reading of the
    patent's "r*360 (or r*pi)".
    """

    name: str = "admissible_disc"
    angle_span: float = TWO_PI

    def sample_centres(self, prev, next_radius, n, rng):
        R = max(prev.r - next_radius, 0.0)
        u = rng.uniform(0.0, 1.0, size=n)
        th = rng.uniform(0.0, self.angle_span, size=n)
        d = R * np.sqrt(u)
        return prev.centre + np.column_stack((d * np.cos(th), d * np.sin(th)))


@dataclass
class CoupledSpiralModel:
    """Patent READING B: one random draw feeds both the angle and the radius.

    Centres fall on the spiral d = R*sqrt(th / angle_span). Included to be
    falsified, not because it is expected to hold.
    """

    name: str = "coupled_spiral"
    angle_span: float = TWO_PI

    def sample_centres(self, prev, next_radius, n, rng):
        R = max(prev.r - next_radius, 0.0)
        u = rng.uniform(0.0, 1.0, size=n)
        th = self.angle_span * u
        d = R * np.sqrt(u)
        return prev.centre + np.column_stack((d * np.cos(th), d * np.sin(th)))


@dataclass
class EdgeBiasedDiscModel:
    """A tunable family for detecting radial bias away from uniform-on-disc.

    s = (d/R)^2 is drawn from Beta(a, b) instead of Uniform(0,1). a = b = 1
    recovers the admissible-disc model exactly, so this nests Reading A and
    gives the likelihood-ratio test something to push against. a < 1 pulls the
    next centre toward the current one ("gentle" zones); b < 1 pushes it to the
    rim ("edge" zones).
    """

    name: str = "beta_disc"
    a: float = 1.0
    b: float = 1.0

    def sample_centres(self, prev, next_radius, n, rng):
        R = max(prev.r - next_radius, 0.0)
        s = rng.beta(self.a, self.b, size=n)
        th = rng.uniform(0.0, TWO_PI, size=n)
        d = R * np.sqrt(s)
        return prev.centre + np.column_stack((d * np.cos(th), d * np.sin(th)))


# --------------------------------------------------------------------------- #
# Whitelist rejection
# --------------------------------------------------------------------------- #


@dataclass
class WhitelistRejection:
    """Wrap any model in the patent's accept/reject loop against a terrain mask.

    The patent rejects a candidate whose centre falls outside a pre-authored
    whitelist region and redraws, capping the loop at roughly 100 iterations and
    accepting whatever it has at that point. That cap is reproduced here because
    it is observable: when the admissible disc barely intersects the whitelist,
    the cap leaks a small amount of probability mass into excluded terrain, and
    that leak is a signature worth looking for in real data.

    The mask is *not* known. `bluezone.whitelist` estimates one from observed
    centres; until then, pass a coarse hand-drawn approximation and treat the
    output as illustrative.
    """

    base: ZoneModel
    mask: Mask
    max_iter: int = 100
    name: str = "whitelist"

    def __post_init__(self):
        self.name = f"{self.base.name}+whitelist"

    def sample_centres(self, prev, next_radius, n, rng):
        out = self.base.sample_centres(prev, next_radius, n, rng)
        pending = ~self.mask(out)
        for _ in range(self.max_iter - 1):
            k = int(pending.sum())
            if k == 0:
                break
            fresh = self.base.sample_centres(prev, next_radius, k, rng)
            out[pending] = fresh
            idx = np.flatnonzero(pending)
            pending = np.zeros_like(pending)
            pending[idx] = ~self.mask(fresh)
        return out  # survivors of the cap are kept, as the patent describes


def coast_band_mask(margin: float) -> Mask:
    """Crude stand-in for the whitelist: exclude a band around the map edge.

    On an island map the dominant excluded terrain is the surrounding sea, so a
    border band captures the first-order effect. It is a placeholder, clearly
    labelled as one. Replace it with an estimated mask as soon as you have
    enough observed centres.
    """

    def mask(points: np.ndarray) -> np.ndarray:
        p = np.atleast_2d(points)
        return np.all((p >= margin) & (p <= 1.0 - margin), axis=1)

    return mask


# --------------------------------------------------------------------------- #
# Radius schedule
# --------------------------------------------------------------------------- #


@dataclass
class RadiusSchedule:
    """Per-phase circle radii in normalised units.

    THESE ARE NOT MEASURED VALUES. The patent states radii are fixed per phase,
    so the schedule is a small table of constants that any team can recover
    exactly from a handful of annotated matches. Until you have done that, treat
    `default_ratio` as a placeholder that propagates into every downstream
    probability. `docs/PROTOCOL.md` describes how to measure it properly.
    """

    r0: float = 0.62
    ratios: tuple[float, ...] | None = None
    default_ratio: float = 0.55
    n_phases: int = 9

    def radii(self) -> np.ndarray:
        rs = [self.r0]
        for i in range(self.n_phases - 1):
            k = self.ratios[i] if self.ratios and i < len(self.ratios) else self.default_ratio
            rs.append(rs[-1] * k)
        return np.array(rs)

    def radius(self, phase: int) -> float:
        rs = self.radii()
        return float(rs[min(max(phase, 0), len(rs) - 1)])

    @classmethod
    def from_observations(cls, transitions) -> "RadiusSchedule":
        """Fit the schedule from annotated transitions by taking phase medians."""
        from collections import defaultdict

        by_phase = defaultdict(list)
        for t in transitions:
            by_phase[t.phase].append(t.prev.r)
            by_phase[t.phase + 1].append(t.next.r)
        phases = sorted(by_phase)
        radii = [float(np.median(by_phase[p])) for p in phases]
        ratios = tuple(radii[i + 1] / radii[i] for i in range(len(radii) - 1))
        return cls(r0=radii[0], ratios=ratios, n_phases=len(radii))


MODEL_REGISTRY: dict[str, ZoneModel] = {
    "uniform_map": UniformMapModel(),
    "admissible_disc": AdmissibleDiscModel(),
    "half_plane_disc": AdmissibleDiscModel(name="half_plane_disc", angle_span=np.pi),
    "coupled_spiral": CoupledSpiralModel(),
    "centre_pulled": EdgeBiasedDiscModel(name="centre_pulled", a=0.6, b=1.0),
    "edge_pulled": EdgeBiasedDiscModel(name="edge_pulled", a=1.0, b=0.6),
}
