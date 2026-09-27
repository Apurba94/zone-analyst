"""
Monte Carlo forecasting.

Two outputs matter, and they are not the same thing:

  centre density   P(the next circle's centre lands here)
  survival field   P(a team standing here is still inside the zone after k more
                   phases, without moving)

Analysts ask for the first and act on the second. A point can sit in a
low-density part of the map and still have high survival probability because it
is inside many of the sampled circles; the centre-density heatmap that every
community "circle prediction" post shows is the wrong quantity for positioning.

Sampling is recursive: draw phase t+1 centres from the current circle, then draw
phase t+2 centres from each of those, and so on. Uncertainty compounds the way
it does in the real game, which is why the k=3 field is nearly flat and why
claiming a three-circles-ahead read is usually bluster.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .generative import AdmissibleDiscModel, RadiusSchedule, ZoneModel
from .geometry import Circle


@dataclass
class Forecast:
    """Result of a k-phase forward simulation."""

    centres: np.ndarray  # (n_samples, k, 2) centre of each sampled future circle
    radii: np.ndarray  # (k,) radius at each future phase
    start: Circle
    model_name: str

    @property
    def final_centres(self) -> np.ndarray:
        return self.centres[:, -1, :]

    @property
    def n_samples(self) -> int:
        return self.centres.shape[0]


def forecast(
    start: Circle,
    phase: int,
    schedule: RadiusSchedule,
    model: ZoneModel | None = None,
    steps: int = 1,
    n_samples: int = 20000,
    seed: int | None = None,
) -> Forecast:
    """Simulate `steps` future zones from `start`."""
    model = model or AdmissibleDiscModel()
    rng = np.random.default_rng(seed)
    radii = np.array([schedule.radius(phase + k) for k in range(1, steps + 1)])

    # A start radius that contradicts the schedule at this phase silently
    # produces a huge admissible disc and a tiny target circle, and every
    # downstream probability collapses toward zero without any error. Catch it.
    expected_r = schedule.radius(phase)
    if expected_r > 0 and not (0.7 * expected_r <= start.r <= 1.4 * expected_r):
        import warnings

        warnings.warn(
            f"start radius {start.r:.4f} disagrees with the schedule for phase "
            f"{phase} ({expected_r:.4f}). Either the phase label or the radius "
            f"schedule is wrong; probabilities from this forecast are not "
            f"meaningful until they agree.",
            stacklevel=2,
        )

    centres = np.empty((n_samples, steps, 2))
    cur_centres = np.tile(start.centre, (n_samples, 1))
    cur_r = start.r

    for k in range(steps):
        nxt_r = radii[k]
        out = np.empty((n_samples, 2))
        # The sampler is vectorised per starting circle; group identical starts
        # at k = 0 and sample individually thereafter, in chunks to stay fast.
        if k == 0:
            out = model.sample_centres(Circle(*start.centre, cur_r), nxt_r, n_samples, rng)
        else:
            R = max(cur_r - nxt_r, 0.0)
            # For disc-type models the offset distribution is identical for every
            # sample, so draw offsets once and add them to each parent centre.
            offs = model.sample_centres(Circle(0.0, 0.0, cur_r), nxt_r, n_samples, rng)
            out = cur_centres + offs
            del R
        centres[:, k, :] = out
        cur_centres = out
        cur_r = nxt_r

    return Forecast(centres=centres, radii=radii, start=start,
                    model_name=getattr(model, "name", "model"))


# --------------------------------------------------------------------------- #
# Fields
# --------------------------------------------------------------------------- #


def centre_density(fc: Forecast, grid: int = 160, step: int = -1) -> np.ndarray:
    """2-D histogram of sampled centres, normalised to sum to 1."""
    pts = fc.centres[:, step, :]
    H, _, _ = np.histogram2d(pts[:, 1], pts[:, 0], bins=grid, range=[[0, 1], [0, 1]])
    total = H.sum()
    return H / total if total else H


def survival_field(fc: Forecast, grid: int = 160, step: int = -1) -> np.ndarray:
    """P(point is inside the sampled circle at `step`), on a grid.

    Implemented by stamping each sampled disc into a difference array and taking
    a prefix sum: O(n_samples * disc_rows) instead of O(grid^2 * n_samples).
    """
    pts = fc.centres[:, step, :]
    r = float(fc.radii[step])
    acc = np.zeros((grid, grid + 1), dtype=np.int32)
    rr = r * grid

    cx = pts[:, 0] * grid
    cy = pts[:, 1] * grid
    y0 = np.maximum(np.ceil(cy - rr).astype(int), 0)
    y1 = np.minimum(np.floor(cy + rr).astype(int), grid - 1)

    for i in range(len(pts)):
        if y1[i] < y0[i]:
            continue
        rows = np.arange(y0[i], y1[i] + 1)
        dy = (rows + 0.5) - cy[i]
        half = np.sqrt(np.maximum(rr * rr - dy * dy, 0.0))
        xs = np.maximum(np.ceil(cx[i] - half).astype(int), 0)
        xe = np.minimum(np.floor(cx[i] + half).astype(int) + 1, grid)
        valid = xe > xs
        np.add.at(acc, (rows[valid], xs[valid]), 1)
        np.add.at(acc, (rows[valid], xe[valid]), -1)

    field = np.cumsum(acc[:, :grid], axis=1).astype(float) / fc.n_samples
    return field


def highest_density_regions(density: np.ndarray, levels=(0.5, 0.75, 0.9, 0.95)) -> dict:
    """Smallest-area regions containing the given probability mass.

    Returns, per level, the density threshold and the region's area as a
    fraction of the map. Area is the number that tells an analyst whether a
    "90% confident" claim is worth anything: 90% mass spread over 60% of the map
    is not a prediction.
    """
    flat = np.sort(density.ravel())[::-1]
    cum = np.cumsum(flat)
    out = {}
    n_cells = density.size
    for lv in levels:
        idx = int(np.searchsorted(cum, lv))
        idx = min(idx, len(flat) - 1)
        out[lv] = {
            "threshold": float(flat[idx]),
            "area_fraction": float((idx + 1) / n_cells),
        }
    return out


def probability_in_circle(fc: Forecast, centre, radius: float, step: int = -1) -> float:
    """P(next centre falls within `radius` of `centre`) - for region questions."""
    pts = fc.centres[:, step, :]
    d = np.hypot(pts[:, 0] - centre[0], pts[:, 1] - centre[1])
    return float(np.mean(d <= radius))


def probability_point_safe(fc: Forecast, point, step: int = -1) -> float:
    """P(a stationary team at `point` is inside the zone at `step`)."""
    pts = fc.centres[:, step, :]
    d = np.hypot(pts[:, 0] - point[0], pts[:, 1] - point[1])
    return float(np.mean(d <= fc.radii[step]))


def probability_point_safe_through(fc: Forecast, point) -> float:
    """P(inside the zone at *every* future phase simulated) - the honest version.

    Surviving phase t+3 is worth little if you were caught outside at t+1.
    """
    p = np.asarray(point, dtype=float)
    inside = np.ones(fc.n_samples, dtype=bool)
    for k in range(fc.centres.shape[1]):
        d = np.hypot(fc.centres[:, k, 0] - p[0], fc.centres[:, k, 1] - p[1])
        inside &= d <= fc.radii[k]
    return float(np.mean(inside))
