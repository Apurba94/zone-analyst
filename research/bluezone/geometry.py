"""
Normalised zone geometry and the canonical transition transform.

Everything in this project lives in a normalised map frame:

    x, y in [0, 1]   (0,0) = north-west map corner, y increasing south
    r    in [0, 1]   radius as a fraction of the map edge length

A zone observation is a circle C_t = (x_t, y_t, r_t).

The single most important object in this codebase is the transform that turns a
*pair* of consecutive circles into two scalars whose distribution under the
documented candidate algorithm is known exactly:

    R   = r_t - r_{t+1}                 maximum admissible centre displacement
    d   = |c_{t+1} - c_t|               observed centre displacement
    s   = (d / R)^2                     normalised squared displacement
    th  = atan2(dy, dx) mod 2*pi        displacement bearing

Under the "independent draws, uniform over the admissible disc" reading of the
Tencent region-adjustment patent (US 11,529,559 B2, and continuations
US 12,017,144 / US 12,515,133), and in the absence of whitelist rejection:

    s  ~ Uniform(0, 1)
    th ~ Uniform(0, 2*pi)
    s and th independent

That is an exact, distribution-free target. Every hypothesis test in
`bluezone.tests_stats` is a test of some component of that statement, which is
why a decisive experiment needs tens rather than thousands of observations.

Nothing in this module assumes the patent is what actually ships. It only makes
the comparison cheap.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Sequence

import numpy as np

TWO_PI = 2.0 * np.pi


@dataclass(frozen=True)
class Circle:
    """A zone circle in normalised map coordinates."""

    x: float
    y: float
    r: float

    @property
    def centre(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)

    def contains_point(self, p: Sequence[float]) -> bool:
        p = np.asarray(p, dtype=float)
        return bool(np.hypot(*(p - self.centre)) <= self.r)

    def contains_circle(self, other: "Circle", tol: float = 1e-9) -> bool:
        """True if `other` lies entirely inside this circle."""
        gap = self.r - other.r
        if gap < -tol:
            return False
        return bool(np.hypot(*(other.centre - self.centre)) <= gap + tol)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Transition:
    """One observed zone transition, C_t -> C_{t+1}, tagged with its context."""

    match_id: str
    map_name: str
    phase: int
    prev: Circle
    next: Circle
    n_alive: int | None = None
    source: str = ""

    # --- derived quantities -------------------------------------------------

    @property
    def R(self) -> float:
        """Maximum admissible centre displacement under full containment."""
        return self.prev.r - self.next.r

    @property
    def delta(self) -> np.ndarray:
        return self.next.centre - self.prev.centre

    @property
    def d(self) -> float:
        return float(np.hypot(*self.delta))

    @property
    def s(self) -> float:
        """Normalised squared displacement. Uniform(0,1) under the patent model."""
        if self.R <= 0:
            return np.nan
        return float((self.d / self.R) ** 2)

    @property
    def theta(self) -> float:
        """Displacement bearing in [0, 2*pi)."""
        dy, dx = self.delta[1], self.delta[0]
        return float(np.arctan2(dy, dx) % TWO_PI)

    @property
    def contained(self) -> bool:
        return self.prev.contains_circle(self.next)

    @property
    def containment_excess(self) -> float:
        """d - R. Positive means the new circle pokes outside the old one."""
        return self.d - self.R


def transition_frame(transitions: Iterable[Transition]) -> dict[str, np.ndarray]:
    """Vectorise a collection of transitions into arrays for the test battery.

    Transitions with R <= 0 (a non-shrinking or mis-annotated phase) are dropped
    and reported, rather than silently producing NaNs downstream.
    """
    ts = list(transitions)
    keep = [t for t in ts if t.R > 0]
    dropped = len(ts) - len(keep)
    if not keep:
        raise ValueError("no transitions with a positive shrink gap R = r_t - r_{t+1}")

    return {
        "s": np.array([t.s for t in keep]),
        "theta": np.array([t.theta for t in keep]),
        "d": np.array([t.d for t in keep]),
        "R": np.array([t.R for t in keep]),
        "phase": np.array([t.phase for t in keep]),
        "prev_x": np.array([t.prev.x for t in keep]),
        "prev_y": np.array([t.prev.y for t in keep]),
        "next_x": np.array([t.next.x for t in keep]),
        "next_y": np.array([t.next.y for t in keep]),
        "excess": np.array([t.containment_excess for t in keep]),
        "map_name": np.array([t.map_name for t in keep], dtype=object),
        "match_id": np.array([t.match_id for t in keep], dtype=object),
        "n_dropped": np.array(dropped),
    }


def admissible_disc(prev: Circle, next_radius: float) -> tuple[np.ndarray, float]:
    """Centre and radius of the disc of admissible next-circle centres.

    Full containment of the next circle inside the current one restricts the new
    centre to a disc concentric with the current circle, of radius r_t - r_{t+1}.
    """
    return prev.centre, max(prev.r - next_radius, 0.0)


def circular_mean_resultant(angles: np.ndarray) -> tuple[float, float]:
    """Mean bearing and resultant length Rbar in [0, 1] for circular data."""
    c, s = np.cos(angles).mean(), np.sin(angles).mean()
    return float(np.arctan2(s, c) % TWO_PI), float(np.hypot(c, s))


def wrap_pi(a: np.ndarray | float) -> np.ndarray | float:
    """Wrap angles to (-pi, pi]."""
    return (np.asarray(a) + np.pi) % TWO_PI - np.pi


def guaranteed_safe_radius(r_now: float, r_future: float) -> float:
    """Radius of the disc around the current centre that CANNOT fall outside the zone.

    An exact consequence of the containment constraint alone, with no
    distributional assumption and no data required.

    The future centre can move at most `r_now - r_future` from the current one,
    so a point at distance `rho` from the current centre is inside the future
    circle for *every* admissible draw when

        rho + (r_now - r_future) <= r_future     i.e.   rho <= 2*r_future - r_now

    Two things follow that matter tactically:

    * When the shrink ratio r_future / r_now exceeds 0.5, this radius is
      positive: there is a disc of ground around the current centre that is
      guaranteed safe next phase. The current centre itself is always in it.
    * When the ratio drops below 0.5, the guarantee vanishes entirely and centre
      play stops being risk-free. Where that crossover sits per phase is decided
      by the radius schedule, which is why measuring the schedule is the first
      data-collection priority.

    For a k-phase horizon, pass the radius at phase t+k: the bound on total
    centre drift telescopes to r_now - r_{t+k}, so the same formula applies.
    """
    return max(0.0, 2.0 * r_future - r_now)
