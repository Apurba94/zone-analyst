"""
Turning a probability field into a positioning decision.

The link from forecast to decision is where most zone-prediction work quietly
goes wrong. Two failure modes to avoid:

  * Optimising for P(zone lands here). A team does not need the zone centred on
    them; it needs to be inside it, and to be able to reach the inside of it.
    The right objective uses the survival field and the cost of getting there.

  * Ignoring that everyone else has the same map. Ground that is both very
    likely to be safe and very easy to reach is exactly the ground that will be
    contested. `contention_penalty` makes that explicit instead of pretending
    the map is empty.

Terrain, cover and compound quality are inputs this module does not invent. It
takes them as grids the analyst supplies from their own map knowledge, and it
will run with them set to zero, in which case it is a pure zone-and-distance
model and should be described as one.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .montecarlo import Forecast, survival_field


@dataclass
class TerrainLayers:
    """Analyst-supplied map knowledge, all as (grid, grid) arrays in [0, 1].

    None means "not supplied", which is treated as neutral rather than as good.
    """

    cover: np.ndarray | None = None
    elevation_advantage: np.ndarray | None = None
    compound_quality: np.ndarray | None = None
    traversability: np.ndarray | None = None  # 0 = impassable (water, cliff)
    road_access: np.ndarray | None = None

    def get(self, name: str, grid: int) -> np.ndarray:
        v = getattr(self, name)
        if v is None:
            return np.zeros((grid, grid)) if name != "traversability" else np.ones((grid, grid))
        return v


@dataclass
class Weights:
    """Objective weights. Defaults are a starting point for calibration.

    Calibrate them against your own scrim outcomes rather than accepting these:
    a team with three vehicles and a passive style values rotation cost very
    differently from one that plays contested compounds.
    """

    survival: float = 1.0
    rotation: float = 0.55
    exposure: float = 0.35
    contention: float = 0.30
    cover: float = 0.15
    elevation: float = 0.10


def rotation_cost_field(
    origin: tuple[float, float],
    grid: int,
    layers: TerrainLayers,
    vehicle_speed_ratio: float = 3.0,
) -> np.ndarray:
    """Normalised travel cost from `origin` to every cell.

    A Dijkstra pass over an 8-connected grid whose edge weights come from
    traversability, with road cells cheapened by `vehicle_speed_ratio`. Straight
    line distance is not good enough on maps where a ridge or a river doubles
    the real rotation.
    """
    import heapq

    trav = layers.get("traversability", grid)
    road = layers.get("road_access", grid)
    step_cost = np.where(trav > 0.05, 1.0 / np.maximum(trav, 0.05), np.inf)
    step_cost = step_cost / (1.0 + (vehicle_speed_ratio - 1.0) * road)

    dist = np.full((grid, grid), np.inf)
    sy = int(np.clip(origin[1] * grid, 0, grid - 1))
    sx = int(np.clip(origin[0] * grid, 0, grid - 1))
    dist[sy, sx] = 0.0
    pq = [(0.0, sy, sx)]
    nbrs = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]

    while pq:
        d, y, x = heapq.heappop(pq)
        if d > dist[y, x]:
            continue
        for dy, dx, w in nbrs:
            ny, nx = y + dy, x + dx
            if not (0 <= ny < grid and 0 <= nx < grid):
                continue
            c = step_cost[ny, nx]
            if not np.isfinite(c):
                continue
            nd = d + w * c
            if nd < dist[ny, nx]:
                dist[ny, nx] = nd
                heapq.heappush(pq, (nd, ny, nx))

    finite = dist[np.isfinite(dist)]
    scale = np.percentile(finite, 99) if finite.size else 1.0
    return np.clip(dist / max(scale, 1e-9), 0, 1.5)


def contention_penalty(surv: np.ndarray, rot: np.ndarray, sharpness: float = 6.0) -> np.ndarray:
    """Ground that is obviously good is ground that will be occupied.

    Every surviving team is looking at a similar field, so desirability itself
    predicts traffic. This is a first-order proxy, not a game-theoretic
    equilibrium; `docs/REPORT.md` explains why the full multi-agent version is
    listed as future work rather than shipped here.
    """
    desirability = surv * np.exp(-sharpness * np.clip(rot, 0, 1))
    m = desirability.max()
    return desirability / m if m > 0 else desirability


def expected_value_map(
    fc: Forecast,
    team_position: tuple[float, float],
    layers: TerrainLayers | None = None,
    weights: Weights | None = None,
    grid: int = 160,
    through_all_phases: bool = True,
) -> dict[str, np.ndarray]:
    """Score every cell for "where should we be standing".

    Returns the component layers alongside the score so that a coach can see
    *why* a cell scores well. A single opaque number that nobody can interrogate
    does not survive contact with a team.
    """
    layers = layers or TerrainLayers()
    w = weights or Weights()

    if through_all_phases and fc.centres.shape[1] > 1:
        surv = np.ones((grid, grid))
        for k in range(fc.centres.shape[1]):
            surv = np.minimum(surv, survival_field(fc, grid=grid, step=k))
    else:
        surv = survival_field(fc, grid=grid)

    rot = rotation_cost_field(team_position, grid, layers)
    cont = contention_penalty(surv, rot)
    cover = layers.get("cover", grid)
    elev = layers.get("elevation_advantage", grid)
    trav = layers.get("traversability", grid)
    exposure = 1.0 - cover

    # Survival multiplies rather than adds. With an additive rotation penalty, a
    # team stranded outside the zone scores best by not moving: every reachable
    # cell has survival near zero, so the cell with zero rotation cost wins. That
    # is the opposite of the right answer. Gating on survival means ground you
    # cannot survive on is worth nothing however cheap it is to reach.
    quality = (
        1.0
        - w.exposure * exposure
        - w.contention * cont
        + w.cover * cover
        + w.elevation * elev
    )
    score = w.survival * surv * quality - w.rotation * rot * surv
    score = np.where(trav > 0.05, score, -np.inf)

    return {
        "score": score,
        "survival": surv,
        "rotation_cost": rot,
        "contention": cont,
    }


def top_positions(ev: dict[str, np.ndarray], k: int = 5, min_separation: float = 0.06) -> list[dict]:
    """Best cells, thinned so the list is not five pixels of the same hill."""
    score = ev["score"]
    grid = score.shape[0]
    order = np.argsort(score.ravel())[::-1]
    picks: list[dict] = []
    for flat in order:
        if len(picks) >= k:
            break
        y, x = divmod(int(flat), grid)
        px, py = (x + 0.5) / grid, (y + 0.5) / grid
        if not np.isfinite(score[y, x]):
            continue
        if any(np.hypot(px - p["x"], py - p["y"]) < min_separation for p in picks):
            continue
        picks.append({
            "x": px, "y": py,
            "score": float(score[y, x]),
            "survival": float(ev["survival"][y, x]),
            "rotation_cost": float(ev["rotation_cost"][y, x]),
            "contention": float(ev["contention"][y, x]),
        })
    return picks
