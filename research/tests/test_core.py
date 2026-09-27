"""Tests for the properties the whole analysis leans on."""

import numpy as np
import pytest

from bluezone.geometry import Circle, Transition, transition_frame
from bluezone.generative import (
    AdmissibleDiscModel, CoupledSpiralModel, EdgeBiasedDiscModel,
    RadiusSchedule, UniformMapModel, WhitelistRejection, coast_band_mask,
)
from bluezone.montecarlo import (
    forecast, survival_field, centre_density, highest_density_regions,
    probability_point_safe,
)
from bluezone.tests_stats import (
    containment_test, coupling_test, radial_uniformity_test, bearing_kuiper_test,
)


def _transitions(model, n=400, seed=1):
    rng = np.random.default_rng(seed)
    prev = Circle(0.5, 0.5, 0.30)
    r_next = 0.18
    pts = model.sample_centres(prev, r_next, n, rng)
    return [
        Transition("m", "erangel", 1, prev, Circle(p[0], p[1], r_next), source="synthetic")
        for p in pts
    ]


def test_admissible_disc_gives_uniform_s_and_theta():
    f = transition_frame(_transitions(AdmissibleDiscModel(), 2000))
    assert radial_uniformity_test(f["s"]).p_value > 0.01
    assert bearing_kuiper_test(f["theta"], n_boot=300).p_value > 0.01
    assert coupling_test(f["s"], f["theta"]).p_value > 0.01


def test_containment_holds_for_disc_model():
    f = transition_frame(_transitions(AdmissibleDiscModel(), 500))
    res = containment_test(f["excess"], tol=1e-9)
    assert res.statistic == 0.0


def test_uniform_map_model_breaks_containment():
    f = transition_frame(_transitions(UniformMapModel(), 500))
    assert containment_test(f["excess"], tol=1e-6).statistic > 0.5


def test_coupling_test_detects_the_shared_draw_reading_at_n_10():
    f = transition_frame(_transitions(CoupledSpiralModel(), 10, seed=4))
    assert coupling_test(f["s"], f["theta"]).p_value < 0.01


def test_coupling_test_does_not_fire_on_independent_draws():
    f = transition_frame(_transitions(AdmissibleDiscModel(), 200, seed=9))
    assert coupling_test(f["s"], f["theta"]).p_value > 0.05


def test_radial_test_detects_a_centre_pull():
    f = transition_frame(_transitions(EdgeBiasedDiscModel(a=0.45, b=1.0), 200, seed=2))
    r = radial_uniformity_test(f["s"])
    assert r.p_value < 0.01 and r.detail["mean_s"] < 0.5


def test_half_plane_reading_is_caught_by_kuiper_not_rayleigh():
    from bluezone.tests_stats import bearing_uniformity_test
    f = transition_frame(_transitions(AdmissibleDiscModel(angle_span=np.pi), 120, seed=6))
    assert bearing_kuiper_test(f["theta"], n_boot=600).p_value < 0.05
    # Rayleigh has power here too, but only because a half plane has a mean
    # direction; the point is that Kuiper does not depend on that being true.
    assert bearing_uniformity_test(f["theta"]).statistic > 0.2


def test_whitelist_rejection_keeps_samples_inside_the_mask():
    rng = np.random.default_rng(0)
    m = WhitelistRejection(AdmissibleDiscModel(), coast_band_mask(0.30))
    pts = m.sample_centres(Circle(0.5, 0.5, 0.40), 0.10, 3000, rng)
    inside = coast_band_mask(0.30)(pts)
    assert inside.mean() > 0.99


def test_survival_field_matches_pointwise_probability():
    fc = forecast(Circle(0.5, 0.5, 0.30), 1, RadiusSchedule(), steps=1, n_samples=8000, seed=5)
    grid = 120
    field = survival_field(fc, grid=grid)
    for px, py in [(0.5, 0.5), (0.58, 0.47), (0.72, 0.5)]:
        direct = probability_point_safe(fc, (px, py))
        cell = field[int(py * grid), int(px * grid)]
        assert abs(direct - cell) < 0.03, (px, py, direct, cell)


def test_survival_is_maximal_at_the_current_centre():
    fc = forecast(Circle(0.5, 0.5, 0.30), 1, RadiusSchedule(), steps=1, n_samples=6000, seed=8)
    f = survival_field(fc, grid=100)
    assert np.unravel_index(np.argmax(f), f.shape) == (50, 50) or f[50, 50] > 0.95 * f.max()


def test_hdr_areas_grow_with_confidence_level():
    fc = forecast(Circle(0.5, 0.5, 0.30), 1, RadiusSchedule(), steps=1, n_samples=20000, seed=3)
    hdr = highest_density_regions(centre_density(fc))
    areas = [hdr[l]["area_fraction"] for l in (0.5, 0.75, 0.9, 0.95)]
    assert areas == sorted(areas)


def test_multi_step_forecast_spreads_out():
    sched = RadiusSchedule()
    a = forecast(Circle(0.5, 0.5, 0.30), 1, sched, steps=1, n_samples=6000, seed=1)
    b = forecast(Circle(0.5, 0.5, 0.30), 1, sched, steps=3, n_samples=6000, seed=1)
    spread_a = np.std(a.final_centres, axis=0).mean()
    spread_b = np.std(b.final_centres, axis=0).mean()
    assert spread_b > spread_a


def test_radius_schedule_round_trips_from_observations():
    sched = RadiusSchedule(r0=0.6, default_ratio=0.6, n_phases=5)
    radii = sched.radii()
    ts = [
        Transition("m", "erangel", i + 1, Circle(0.5, 0.5, radii[i]),
                   Circle(0.5, 0.5, radii[i + 1]))
        for i in range(len(radii) - 1)
    ]
    fitted = RadiusSchedule.from_observations(ts)
    assert np.allclose(fitted.radii(), radii, atol=1e-9)


def test_schema_validation_catches_phase_gaps():
    from bluezone.schema import validate
    problems = validate([
        {"match_id": "m", "map_name": "erangel", "phase": 1, "x": .5, "y": .5, "r": .3,
         "source": "vod", "n_alive": None, "fit_quality": "good"},
        {"match_id": "m", "map_name": "erangel", "phase": 3, "x": .5, "y": .5, "r": .1,
         "source": "vod", "n_alive": None, "fit_quality": "good"},
    ])
    assert any("skip" in p for p in problems)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))


def test_guaranteed_safe_disc_is_never_violated():
    from bluezone.geometry import guaranteed_safe_radius
    rng = np.random.default_rng(0)
    r0, r1 = 0.30, 0.18                      # ratio 0.6, above the 0.5 crossover
    rho = guaranteed_safe_radius(r0, r1)
    assert rho > 0
    prev = Circle(0.5, 0.5, r0)
    pts = AdmissibleDiscModel().sample_centres(prev, r1, 20000, rng)
    # every point of the guaranteed disc must sit inside every sampled circle
    for ang in np.linspace(0, 2 * np.pi, 24, endpoint=False):
        p = prev.centre + rho * np.array([np.cos(ang), np.sin(ang)])
        d = np.hypot(pts[:, 0] - p[0], pts[:, 1] - p[1])
        assert d.max() <= r1 + 1e-9


def test_guarantee_disappears_below_the_half_ratio():
    from bluezone.geometry import guaranteed_safe_radius
    assert guaranteed_safe_radius(0.30, 0.15) == 0.0
    assert guaranteed_safe_radius(0.30, 0.14) == 0.0
    assert guaranteed_safe_radius(0.30, 0.16) > 0.0


def test_ev_map_does_not_recommend_standing_still_outside_the_zone():
    """A team far from the zone must be told to move, not to save rotation cost."""
    from bluezone.strategy import expected_value_map, top_positions
    from bluezone.generative import RadiusSchedule as RS

    sched = RS(r0=0.30, default_ratio=0.62, n_phases=4)
    fc = forecast(Circle(0.30, 0.30, 0.30), 0, sched, steps=1, n_samples=6000, seed=2)
    stranded = (0.88, 0.88)
    ev = expected_value_map(fc, team_position=stranded, grid=100)
    best = top_positions(ev, k=1)[0]
    assert np.hypot(best["x"] - stranded[0], best["y"] - stranded[1]) > 0.2
    assert best["survival"] > 0.5


def test_forecast_warns_when_radius_contradicts_the_schedule():
    import warnings
    from bluezone.generative import RadiusSchedule as RS
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        forecast(Circle(0.5, 0.5, 0.31), 3, RS(), steps=1, n_samples=200, seed=0)
        assert any("disagrees with the schedule" in str(x.message) for x in w)


def _battery(model, n, seed):
    from bluezone.tests_stats import run_battery
    ts = _transitions(model, n, seed=seed)
    # spread across phases so phase_homogeneity has something to chew on
    for i, t in enumerate(ts):
        object.__setattr__(t, "phase", (i % 6) + 1)
    return run_battery(transition_frame(ts))


def test_verdict_recovers_each_generating_rule():
    from bluezone.tests_stats import verdict
    cases = [
        (AdmissibleDiscModel(), 210, 1, "consistent with uniform over the admissible disc"),
        (CoupledSpiralModel(), 14, 2, "shared-draw coupling (patent literal reading)"),
        (EdgeBiasedDiscModel(a=0.4, b=1.0), 84, 3, "departs from uniform over the admissible disc"),
        (UniformMapModel(), 56, 4, "not previous-circle constrained"),
    ]
    for model, n, seed, expect in cases:
        got = verdict(_battery(model, n, seed))["conclusion"]
        assert got == expect, f"{model.name}: got {got!r}, expected {expect!r}"


def test_half_plane_bearings_are_not_reported_as_coupling():
    """A non-uniform bearing marginal concentrates the coupling residual.

    theta ~ U(0, pi) with independent s makes theta - pi*s triangular and peaked
    at zero, which Rayleigh calls significant at a resultant near 0.33. The
    verdict must not read that as a shared draw.
    """
    from bluezone.tests_stats import verdict
    res = _battery(AdmissibleDiscModel(angle_span=np.pi), 56, 5)
    v = verdict(res)
    assert "coupling" not in v["conclusion"], v
    assert v["conclusion"] == "departs from uniform over the admissible disc"
    assert "bearing_kuiper" in v["rests_on"]


def test_verdict_controls_the_family_wise_false_alarm_rate():
    """Several marginal tests run at once; the verdict must not flag at 0.05 each.

    Judged individually at 0.05, four tests flagged uniform data as non-uniform
    in 15.7% of batches. The verdict now applies Bonferroni (alpha / m), so a
    p-value of 0.03 on one test no longer carries it, while 0.005 still does.
    """
    from bluezone.tests_stats import TestResult, verdict

    def battery(radial_p):
        base = [
            TestResult("containment", 0.0, None, 100, ""),
            TestResult("angle_radius_coupling", 0.05, 0.5, 100, ""),
            TestResult("half_span_coupling", 0.05, 0.5, 100, ""),
            TestResult("bearing_kuiper", 0.1, 0.5, 100, ""),
            TestResult("circular_linear_corr", 0.1, 0.5, 100, ""),
            TestResult("phase_homogeneity", 1.0, 0.5, 100, ""),
        ]
        return base + [TestResult("radial_uniformity_ks", 0.2, radial_p, 100, "radially non-uniform")]

    assert verdict(battery(0.03))["conclusion"].startswith("consistent")
    assert verdict(battery(0.005))["conclusion"].startswith("departs")
