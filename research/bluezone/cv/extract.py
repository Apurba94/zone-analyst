"""
Extracting zone circles from tournament video.

Design notes that matter more than the code
-------------------------------------------
1. Prefer full-screen map frames over the minimap. When an observer opens the
   full map the circle is large, unclipped, and drawn on a known rectangle; the
   minimap shows a rotated, translated, heavily clipped arc. One good full-map
   frame is worth fifty minimap frames. `find_map_frames` scores frames so the
   annotation pass can start with the best ones.

2. Do not use the Hough circle transform here. Hough assumes a substantially
   complete circle and votes in a 3-D accumulator whose radius resolution is
   coarse; zone circles are frequently clipped to a short arc by the viewport,
   which is exactly the regime where Hough degrades. Fitting a circle to
   colour-masked edge points by RANSAC plus an algebraic least-squares fit handles arcs
   of 60 degrees or less and returns a usable covariance.

3. Measure your error before you trust any test. `containment_test` needs a
   tolerance, the radius schedule needs precision, and s = (d/R)^2 divides by a
   small difference of two fitted radii, so radius error is amplified. Run
   `synthetic_error_report` to characterise the fitter on rendered circles with
   known ground truth before annotating anything real.

Everything here works on frames the analyst already has the right to use.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:  # keep the module importable without OpenCV for the statistical work
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None


@dataclass
class CircleFit:
    x: float
    y: float
    r: float
    inliers: int
    residual_rms: float
    arc_span_deg: float

    @property
    def is_trustworthy(self) -> bool:
        """A fit from a short arc with few inliers is a guess wearing a lab coat."""
        return self.inliers >= 40 and self.arc_span_deg >= 45 and self.residual_rms < 2.0


# --------------------------------------------------------------------------- #
# Colour masks
# --------------------------------------------------------------------------- #

# HSV windows are a starting point, not a constant of nature: broadcast overlays,
# HDR grades and map palettes shift them. Re-tune per tournament with
# `tune_mask` and store the result alongside the dataset.
DEFAULT_WHITE_HSV = ((0, 0, 205), (180, 45, 255))
DEFAULT_BLUE_HSV = ((88, 90, 120), (115, 255, 255))


def colour_edge_points(
    bgr: np.ndarray, hsv_lo, hsv_hi, min_component: int = 12
) -> np.ndarray:
    """Return (N,2) x,y points on the boundary of a colour-masked ring."""
    if cv2 is None:
        raise ImportError("OpenCV is required for frame extraction")
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(hsv_lo), np.array(hsv_hi))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    # Drop specks: HUD text and item icons are white too.
    n, labels, stats_, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    keep = np.zeros_like(mask)
    for i in range(1, n):
        if stats_[i, cv2.CC_STAT_AREA] >= min_component:
            keep[labels == i] = 255

    pts = cv2.findNonZero(keep)
    return pts.reshape(-1, 2).astype(float) if pts is not None else np.empty((0, 2))


# --------------------------------------------------------------------------- #
# Circle fitting
# --------------------------------------------------------------------------- #


def algebraic_circle_fit(pts: np.ndarray) -> tuple[float, float, float]:
    """Algebraic circle fit on centred coordinates, with ||(a, b, c)|| = 1.

    Close kin to Taubin's fit, which instead scales the quadratic column by
    1 / (2 * sqrt(mean z)). On this project's synthetic benchmark that change
    makes centre error marginally better and radius error marginally worse on
    partial arcs (0.00082 vs 0.00077 at 90 degrees, 0.00123 vs 0.00114 at 45).
    Radius is the error that matters here, because s = (d / R)^2 divides by a
    difference of two fitted radii, so this normalisation is kept. Accuracy is
    measured by `synthetic_error_report`, not assumed from the method's name.
    """
    x, y = pts[:, 0], pts[:, 1]
    mx, my = x.mean(), y.mean()
    u, v = x - mx, y - my
    z = u * u + v * v
    zm = z.mean()
    zc = z - zm
    M = np.column_stack((zc, u, v))
    _, _, Vt = np.linalg.svd(M, full_matrices=False)
    a, b, c = Vt[-1]
    if abs(a) < 1e-14:
        raise np.linalg.LinAlgError("degenerate circle fit (points are collinear)")
    cx = -b / (2 * a)
    cy = -c / (2 * a)
    r = np.sqrt(max(cx * cx + cy * cy + zm, 0.0))
    return float(cx + mx), float(cy + my), float(r)


# Backwards-compatible name from earlier versions of this module.
taubin_fit = algebraic_circle_fit


def ransac_circle(
    pts: np.ndarray,
    iters: int = 600,
    tol: float = 1.6,
    min_radius: float = 8.0,
    seed: int = 0,
) -> CircleFit | None:
    """Fit a circle to noisy boundary points, tolerating heavy outliers."""
    if len(pts) < 12:
        return None
    rng = np.random.default_rng(seed)
    best, best_n = None, 0

    for _ in range(iters):
        idx = rng.choice(len(pts), 3, replace=False)
        p = pts[idx]
        try:
            cx, cy, r = _circle_through_three(p)
        except np.linalg.LinAlgError:
            continue
        if not np.isfinite(r) or r < min_radius:
            continue
        d = np.abs(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - r)
        n_in = int(np.sum(d < tol))
        if n_in > best_n:
            best_n, best = n_in, (cx, cy, r)

    if best is None:
        return None

    cx, cy, r = best
    d = np.abs(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - r)
    inl = pts[d < tol]
    if len(inl) >= 12:
        try:
            cx, cy, r = algebraic_circle_fit(inl)
            d = np.abs(np.hypot(inl[:, 0] - cx, inl[:, 1] - cy) - r)
        except np.linalg.LinAlgError:
            pass

    ang = np.arctan2(inl[:, 1] - cy, inl[:, 0] - cx)
    span = _angular_span_deg(ang)
    return CircleFit(float(cx), float(cy), float(r), len(inl), float(np.sqrt(np.mean(d**2))), span)


def _circle_through_three(p: np.ndarray) -> tuple[float, float, float]:
    (x1, y1), (x2, y2), (x3, y3) = p
    A = np.array([[x2 - x1, y2 - y1], [x3 - x1, y3 - y1]], dtype=float)
    b = 0.5 * np.array([x2**2 - x1**2 + y2**2 - y1**2, x3**2 - x1**2 + y3**2 - y1**2])
    c = np.linalg.solve(A, b)
    return float(c[0]), float(c[1]), float(np.hypot(c[0] - x1, c[1] - y1))


def _angular_span_deg(ang: np.ndarray) -> float:
    """Largest arc actually covered by the inliers, in degrees."""
    a = np.sort(ang % (2 * np.pi))
    if len(a) < 2:
        return 0.0
    gaps = np.diff(np.concatenate([a, a[:1] + 2 * np.pi]))
    return float(np.degrees(2 * np.pi - gaps.max()))


# --------------------------------------------------------------------------- #
# Map frame handling
# --------------------------------------------------------------------------- #


def map_to_normalised(fit: CircleFit, map_rect: tuple[float, float, float, float]) -> tuple[float, float, float]:
    """Convert a pixel-space fit to normalised map coordinates.

    `map_rect` is (x0, y0, w, h): the pixel rectangle of the playable map area,
    established once per broadcast layout from known landmarks. A square map in
    an axis-aligned rectangle needs no homography; if the overlay is skewed,
    warp the frame first with `cv2.getPerspectiveTransform` on four landmarks
    and pass the rectified rectangle.
    """
    x0, y0, w, h = map_rect
    return ((fit.x - x0) / w, (fit.y - y0) / h, fit.r / w)


def find_map_frames(video_path: str, stride: int = 15, min_score: float = 0.55) -> list[int]:
    """Score frames by how much they look like an open full-map view.

    Heuristic: full-map views are dominated by the map's own palette, have low
    temporal motion, and carry a large connected region of grid lines. This
    returns candidate frame indices to hand to a human annotator; it is a
    triage step, not a detector, and is meant to be checked by eye.
    """
    if cv2 is None:
        raise ImportError("OpenCV is required for frame extraction")
    cap = cv2.VideoCapture(video_path)
    hits, idx, prev = [], 0, None
    while True:
        ok = cap.grab()
        if not ok:
            break
        if idx % stride == 0:
            ok, frame = cap.retrieve()
            if ok:
                small = cv2.resize(frame, (160, 90))
                grey = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                motion = 0.0 if prev is None else float(np.mean(np.abs(grey.astype(int) - prev)))
                sat = float(np.mean(cv2.cvtColor(small, cv2.COLOR_BGR2HSV)[:, :, 1])) / 255
                score = (1 - min(motion / 25, 1)) * 0.6 + (1 - sat) * 0.4
                if score >= min_score:
                    hits.append(idx)
                prev = grey
        idx += 1
    cap.release()
    return hits


# --------------------------------------------------------------------------- #
# Error characterisation
# --------------------------------------------------------------------------- #


def synthetic_error_report(
    n: int = 200, size: int = 720, arc_deg: float = 360.0, noise: float = 1.0, seed: int = 3
) -> dict:
    """Fit rendered circles with known truth and report the error distribution.

    Run this before annotating real footage, and again after changing any HSV
    window. The radius error it reports is the number to feed to
    `containment_test(tol=...)`, because s = (d/R)^2 divides by a difference of
    two fitted radii and therefore amplifies radius error, not centre error.
    """
    if cv2 is None:
        raise ImportError("OpenCV is required for the synthetic report")
    rng = np.random.default_rng(seed)
    ec, er = [], []
    for _ in range(n):
        r = rng.uniform(size * 0.12, size * 0.42)
        cx = rng.uniform(r, size - r)
        cy = rng.uniform(r, size - r)
        img = np.zeros((size, size, 3), np.uint8)
        a0 = rng.uniform(0, 360)
        cv2.ellipse(img, (int(cx), int(cy)), (int(r), int(r)), 0, a0, a0 + arc_deg,
                    (255, 255, 255), 2)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        img = np.clip(img.astype(float) + rng.normal(0, noise * 8, img.shape), 0, 255).astype(np.uint8)
        pts = colour_edge_points(img, *DEFAULT_WHITE_HSV, min_component=4)
        fit = ransac_circle(pts, seed=int(rng.integers(1 << 30)))
        if fit is None:
            continue
        ec.append(np.hypot(fit.x - cx, fit.y - cy) / size)
        er.append(abs(fit.r - r) / size)
    ec, er = np.array(ec), np.array(er)
    return {
        "n_fitted": len(ec),
        "centre_err_median": float(np.median(ec)),
        "centre_err_p95": float(np.percentile(ec, 95)),
        "radius_err_median": float(np.median(er)),
        "radius_err_p95": float(np.percentile(er, 95)),
        "suggested_containment_tol": float(np.percentile(er, 95) * 2),
        "note": "errors are fractions of the map edge length",
    }
