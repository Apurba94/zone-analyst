/**
 * Zone mathematics.
 *
 * A direct port of the model in `bluezone/` (Python) and the published
 * simulator. The generative models come from the centre-selection routine
 * described in Tencent's region-adjustment patent family (US 11,529,559 B2 and
 * continuations): circle radii are fixed per phase, the next circle is
 * contained in the current one, and the new centre is drawn from the disc of
 * radius R = r_prev - r_next.
 *
 * Note on rendering: the desktop version drew a pixel heatmap. That is a bad
 * fit for a phone, and unnecessary. Under every model here the offset
 * distribution is isotropic about the current centre, so the highest-density
 * regions are exactly concentric discs and the survival field depends only on
 * distance from the centre. Both reduce to a one-dimensional curve, which is
 * cheap to compute and renders as a handful of circles rather than 17,000
 * rectangles. Same mathematics, a fraction of the work.
 */

export type Circle = { x: number; y: number; r: number };
export type ZoneModel = 'disc' | 'spiral' | 'half' | 'free';

export const TAU = Math.PI * 2;

export const MODEL_LABELS: Record<ZoneModel, string> = {
  disc: 'Uniform over admissible disc',
  spiral: 'Shared draw (angle/radius coupled)',
  half: 'Half-plane bearings',
  free: 'No containment (null baseline)',
};

/** Draw a centre offset for one phase transition. */
export function sampleOffset(R: number, model: ZoneModel): [number, number] {
  const u = Math.random();
  let th: number;
  let d: number;
  if (model === 'spiral') {
    // The literal reading of the patent: one random number feeds both the
    // angle and the radius, putting every centre on a spiral.
    th = TAU * u;
    d = R * Math.sqrt(u);
  } else if (model === 'half') {
    th = Math.PI * Math.random();
    d = R * Math.sqrt(u);
  } else {
    th = TAU * Math.random();
    d = R * Math.sqrt(u);
  }
  return [d * Math.cos(th), d * Math.sin(th)];
}

const inBand = (x: number, y: number, m: number) =>
  x >= m && x <= 1 - m && y >= m && y <= 1 - m;

/** Radii for each phase, as a fraction of map edge length. */
export function radiusSchedule(r0: number, ratio: number, nPhases: number): number[] {
  const out = [r0];
  for (let i = 1; i < nPhases; i++) out.push(out[i - 1] * ratio);
  return out;
}

/** Generate a complete match: every circle, in order. */
export function makeMatch(
  r0: number,
  ratio: number,
  nPhases: number,
  model: ZoneModel,
  coast: number
): Circle[] {
  const rs = radiusSchedule(r0, ratio, nPhases);
  const lo = rs[0] < 0.5 ? rs[0] : 0.5;
  const hi = rs[0] < 0.5 ? 1 - rs[0] : 0.5;
  const phases: Circle[] = [
    { x: lo + Math.random() * (hi - lo), y: lo + Math.random() * (hi - lo), r: rs[0] },
  ];

  for (let i = 1; i < rs.length; i++) {
    const prev = phases[i - 1];
    let nx = prev.x;
    let ny = prev.y;
    if (model === 'free') {
      const a = rs[i];
      const b = 1 - rs[i];
      nx = b > a ? a + Math.random() * (b - a) : 0.5;
      ny = b > a ? a + Math.random() * (b - a) : 0.5;
    } else {
      const R = Math.max(prev.r - rs[i], 0);
      // The patent caps the whitelist retry loop; so do we.
      for (let t = 0; t < 100; t++) {
        const [dx, dy] = sampleOffset(R, model);
        nx = prev.x + dx;
        ny = prev.y + dy;
        if (coast === 0 || inBand(nx, ny, coast)) break;
      }
    }
    phases.push({ x: nx, y: ny, r: rs[i] });
  }
  return phases;
}

/**
 * Radius of the disc around the current centre that cannot be caught outside.
 *
 * Exact, from the containment constraint alone. Above a shrink ratio of 0.5
 * this is positive and the current centre is always inside it; below 0.5 the
 * guarantee vanishes entirely and centre play stops being free.
 */
export function guaranteedSafeRadius(rNow: number, rFuture: number): number {
  return Math.max(0, 2 * rFuture - rNow);
}

/** Interpolated blue-zone boundary partway through a shrink. */
export function lerpCircle(a: Circle, b: Circle, u: number): Circle {
  const t = Math.min(Math.max(u, 0), 1);
  return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t, r: a.r + (b.r - a.r) * t };
}

export const dist = (ax: number, ay: number, bx: number, by: number) =>
  Math.hypot(ax - bx, ay - by);

/** Sample the distance from the current centre to the centre k phases ahead. */
function sampleFinalOffsets(
  rNow: number,
  radii: number[],
  model: ZoneModel,
  n: number
): { dx: Float64Array; dy: Float64Array } {
  const dx = new Float64Array(n);
  const dy = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    let ox = 0;
    let oy = 0;
    let cur = rNow;
    for (let k = 0; k < radii.length; k++) {
      const R = Math.max(cur - radii[k], 0);
      const [a, b] = sampleOffset(R, model);
      ox += a;
      oy += b;
      cur = radii[k];
    }
    dx[i] = ox;
    dy[i] = oy;
  }
  return { dx, dy };
}

/**
 * Distances containing the given share of next-centre probability mass.
 *
 * Because the offset distribution is isotropic, these are radii of concentric
 * circles, and they are exact for a single step: the q-quantile is R*sqrt(q).
 */
export function centreQuantiles(
  rNow: number,
  radii: number[],
  model: ZoneModel,
  levels: number[] = [0.5, 0.75, 0.9, 0.95],
  n = 4000
): number[] {
  if (model === 'free') return levels.map(() => 0.5);
  const { dx, dy } = sampleFinalOffsets(rNow, radii, model, n);
  const d = new Float64Array(n);
  for (let i = 0; i < n; i++) d[i] = Math.hypot(dx[i], dy[i]);
  const sorted = Array.from(d).sort((a, b) => a - b);
  return levels.map((q) => sorted[Math.min(n - 1, Math.floor(q * n))]);
}

/**
 * P(a stationary team at distance `d` from the current centre is still inside
 * the zone), sampled across a range of distances.
 *
 * This is the quantity positioning decisions actually depend on. It is not the
 * same as the centre density: a point well off centre can have high survival
 * probability because it falls inside many of the sampled circles.
 */
export function survivalCurve(
  rNow: number,
  radii: number[],
  model: ZoneModel,
  steps = 48,
  n = 2500
): { d: number[]; p: number[] } {
  const rFinal = radii[radii.length - 1];
  const { dx, dy } = sampleFinalOffsets(rNow, radii, model, n);
  const maxD = Math.max(rNow, rFinal * 2);
  const d: number[] = [];
  const p: number[] = [];
  for (let s = 0; s <= steps; s++) {
    const dd = (maxD * s) / steps;
    let inside = 0;
    for (let i = 0; i < n; i++) {
      if (Math.hypot(dx[i] - dd, dy[i]) <= rFinal) inside++;
    }
    d.push(dd);
    p.push(inside / n);
  }
  return { d, p };
}

// ---------------------------------------------------------------------------
// Test battery — the same statistics as bluezone/tests_stats.py
// ---------------------------------------------------------------------------

export type Transition = { s: number; theta: number; excess: number; phase: number };

export function transitionStats(a: Circle, b: Circle, phase: number): Transition | null {
  const R = a.r - b.r;
  if (R <= 0) return null;
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const d = Math.hypot(dx, dy);
  return {
    s: (d / R) ** 2,
    theta: ((Math.atan2(dy, dx) % TAU) + TAU) % TAU,
    excess: d - R,
    phase,
  };
}

export function matchTransitions(phases: Circle[]): Transition[] {
  const out: Transition[] = [];
  for (let i = 0; i + 1 < phases.length; i++) {
    const t = transitionStats(phases[i], phases[i + 1], i + 1);
    if (t) out.push(t);
  }
  return out;
}

function ksUniformP(s: number[]): number | null {
  const n = s.length;
  if (n < 4) return null;
  const u = [...s].sort((a, b) => a - b);
  let D = 0;
  for (let i = 0; i < n; i++) D = Math.max(D, (i + 1) / n - u[i], u[i] - i / n);
  const lam = (Math.sqrt(n) + 0.12 + 0.11 / Math.sqrt(n)) * D;
  let q = 0;
  for (let k = 1; k <= 100; k++) q += 2 * Math.pow(-1, k - 1) * Math.exp(-2 * k * k * lam * lam);
  return Math.min(Math.max(q, 0), 1);
}

function resultant(ang: number[]): number {
  if (!ang.length) return 0;
  let c = 0;
  let s = 0;
  for (const a of ang) {
    c += Math.cos(a);
    s += Math.sin(a);
  }
  return Math.hypot(c / ang.length, s / ang.length);
}

function rayleighP(rbar: number, n: number): number | null {
  if (n < 4) return null;
  const z = n * rbar * rbar;
  return Math.min(Math.max(Math.exp(-z) * (1 + (2 * z - z * z) / (4 * n)), 0), 1);
}

function kuiperP(ang: number[]): number | null {
  const n = ang.length;
  if (n < 5) return null;
  const u = ang.map((a) => (((a % TAU) + TAU) % TAU) / TAU).sort((a, b) => a - b);
  let dp = 0;
  let dm = 0;
  for (let i = 0; i < n; i++) {
    dp = Math.max(dp, (i + 1) / n - u[i]);
    dm = Math.max(dm, u[i] - i / n);
  }
  const V = dp + dm;
  const lam = (Math.sqrt(n) + 0.155 + 0.24 / Math.sqrt(n)) * V;
  let q = 0;
  for (let k = 1; k <= 100; k++) q += 2 * (4 * k * k * lam * lam - 1) * Math.exp(-2 * k * k * lam * lam);
  return Math.min(Math.max(q, 0), 1);
}

const wrapPi = (a: number) => (((a + Math.PI) % TAU) + TAU) % TAU - Math.PI;

export type Battery = {
  n: number;
  violFrac: number;
  meanS: number;
  ksP: number | null;
  kuiperP: number | null;
  coupRes: number;
  coupP: number | null;
  halfRes: number;
  halfP: number | null;
};

export function runBattery(data: Transition[]): Battery | null {
  const n = data.length;
  if (n < 5) return null;
  const s = data.map((d) => d.s);
  const th = data.map((d) => d.theta);
  const cRes = resultant(th.map((t, i) => wrapPi(t - TAU * s[i])));
  const hRes = resultant(th.map((t, i) => wrapPi(t - Math.PI * s[i])));
  return {
    n,
    violFrac: data.filter((d) => d.excess > 1e-9).length / n,
    meanS: s.reduce((a, b) => a + b, 0) / n,
    ksP: ksUniformP(s),
    kuiperP: kuiperP(th),
    coupRes: cRes,
    coupP: rayleighP(cRes, n),
    halfRes: hRes,
    halfP: rayleighP(hRes, n),
  };
}

/**
 * Collapse the battery into a conclusion.
 *
 * The 0.70 resultant floor is load-bearing. A significant coupling p-value is
 * not sufficient on its own: with bearings confined to a half plane and s drawn
 * independently, theta - pi*s is triangular and peaked at zero, which Rayleigh
 * calls highly significant at a resultant near 0.33. Requiring a near-unit
 * resultant separates a real coupling from that artefact.
 */
const COUPLED = 0.7;

export function verdict(b: Battery | null): { title: string; detail: string } {
  if (!b) return { title: 'No data yet', detail: 'Play a match or run a batch to accumulate transitions.' };
  if (b.violFrac > 0.05)
    return {
      title: 'Not previous-circle constrained',
      detail: `${(b.violFrac * 100).toFixed(0)}% of transitions place the next circle partly outside the previous one.`,
    };
  if (b.coupP !== null && b.coupP < 0.01 && b.coupRes >= COUPLED)
    return {
      title: 'Shared-draw coupling detected',
      detail: `Bearing and displacement are locked together (resultant ${b.coupRes.toFixed(3)}). Ten transitions are enough to see this.`,
    };
  if (b.halfP !== null && b.halfP < 0.01 && b.halfRes >= COUPLED)
    return {
      title: 'Half-span shared-draw coupling',
      detail: `Coupling holds against a pi span (resultant ${b.halfRes.toFixed(3)}).`,
    };
  const f: string[] = [];
  // Two marginal tests, each calibrated alone; judging each at 5% flagged uniform
  // data 10% of the time. Bonferroni keeps the verdict's false-alarm rate at 5%.
  const ALPHA_EACH = 0.05 / 2;
  if (b.kuiperP !== null && b.kuiperP < ALPHA_EACH) f.push('bearings are not uniform on the circle');
  if (b.ksP !== null && b.ksP < ALPHA_EACH)
    f.push(
      `radially biased ${b.meanS < 0.5 ? 'toward the previous centre' : 'toward the rim'} (mean s = ${b.meanS.toFixed(3)})`
    );
  if (f.length)
    return { title: 'Departs from uniform over the admissible disc', detail: f.join('; ') + '.' };
  return {
    title: 'Consistent with uniform over the admissible disc',
    detail: `No departure at n = ${b.n}, with each of the two tests judged at 2.5% so false alarms stay at 5%. A mild radial bias needs roughly 100-200 transitions, so this is not yet evidence of no effect.`,
  };
}
