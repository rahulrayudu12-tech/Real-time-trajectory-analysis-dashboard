# src/physics.py
"""Core physics helper functions used by the simulation.

These functions are deliberately pure (no side‑effects) so they can be unit‑tested
independently and also reused by external code (e.g., a Kalman filter).
"""

from __future__ import annotations

import numpy as np

from .constants import G, RHO_SEA_LEVEL, SCALE_HEIGHT, SPEED_OF_SOUND_SEA

# ---------------------------------------------------------------------------
# Atmospheric model
# ---------------------------------------------------------------------------
def air_density(altitude: float) -> float:
    """Return air density (kg/m³) at *altitude* using an exponential model.

    Parameters
    ----------
    altitude : float
        Altitude above sea level in metres.
    """
    return RHO_SEA_LEVEL * np.exp(-altitude / SCALE_HEIGHT)

# ---------------------------------------------------------------------------
# Aerodynamic calculations
# ---------------------------------------------------------------------------
def dynamic_pressure(rho: float, speed: float) -> float:
    """Return dynamic pressure ``q = 0.5 * rho * v²``.
    """
    return 0.5 * rho * speed ** 2

def drag_force(rho: float, speed: float, cd: float, area: float) -> float:
    """Standard drag equation ``D = q * Cd * A``.
    """
    return dynamic_pressure(rho, speed) * cd * area

def mach_number(speed: float, altitude: float) -> float:
    """Approximate Mach number based on a simple temperature lapse model.

    The speed of sound decreases with altitude roughly as
    ``a = a0 * sqrt(1 - altitude / 44300)`` for altitudes below ~20 km.
    """
    a = SPEED_OF_SOUND_SEA * np.sqrt(max(0.0, 1 - altitude / 44300.0))
    return speed / a if a > 0 else np.inf

# ---------------------------------------------------------------------------
# Kinematics helpers
# ---------------------------------------------------------------------------
def velocity_components(speed: float, launch_angle_deg: float) -> tuple[float, float]:
    """Return horizontal (vx) and vertical (vy) components of *speed*.
    """
    rad = np.deg2rad(launch_angle_deg)
    return speed * np.cos(rad), speed * np.sin(rad)

def kinetic_energy(mass: float, speed: float) -> float:
    """Return translational kinetic energy (J)."""
    return 0.5 * mass * speed ** 2

def g_load(acceleration: float) -> float:
    """Return G‑load experienced (dimensionless)."""
    return 1 + acceleration / G  # 1 g static + additional acceleration
