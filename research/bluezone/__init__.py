"""Blue-zone analytics: a grey-box research toolkit for competitive PUBG Mobile.

The project treats the zone algorithm as a *grey* box, not a black one. Tencent's
published patent family describes a specific candidate centre-selection routine,
which turns an open-ended reverse-engineering problem into a small number of
sharp, falsifiable tests on a modest hand-annotated dataset.

Read docs/REPORT.md first. It states what is evidence, what is hypothesis, and
what has not been measured yet.
"""

from .geometry import Circle, Transition, transition_frame
from .generative import (
    AdmissibleDiscModel,
    CoupledSpiralModel,
    EdgeBiasedDiscModel,
    RadiusSchedule,
    UniformMapModel,
    WhitelistRejection,
    MODEL_REGISTRY,
)
from .montecarlo import forecast, survival_field, centre_density, highest_density_regions
from .tests_stats import run_battery, format_battery

__version__ = "0.1.0"
__all__ = [
    "Circle", "Transition", "transition_frame",
    "AdmissibleDiscModel", "CoupledSpiralModel", "EdgeBiasedDiscModel",
    "UniformMapModel", "WhitelistRejection", "RadiusSchedule", "MODEL_REGISTRY",
    "forecast", "survival_field", "centre_density", "highest_density_regions",
    "run_battery", "format_battery",
]
