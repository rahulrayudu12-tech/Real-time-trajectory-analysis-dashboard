# src/constants.py
"""Physical constants and default missile class configurations.

All values are SI units unless otherwise noted.
Values are calibrated to match the DRDL reference datasets.
"""

# ---------------------------------------------------------------------------
# Universal physical constants
# ---------------------------------------------------------------------------
G = 9.80665  # Gravitational acceleration (m/s^2)
RHO_SEA_LEVEL = 1.225  # Air density at sea level (kg/m^3)
SCALE_HEIGHT = 8500.0  # Exponential atmosphere scale height (m)
SPEED_OF_SOUND_SEA = 340.3  # Speed of sound at sea level (m/s)

# ---------------------------------------------------------------------------
# Missile class library – calibrated to DRDL reference CSVs
# ---------------------------------------------------------------------------
# Each entry maps to the initial conditions and parameters observed in the
# reference datasets so that the generated output closely matches them.
#
#   mass_initial    – total launch mass (kg)
#   propellant_mass – mass of propellant consumed during BOOST (kg)
#   burn_time       – BOOST phase duration (s)
#   thrust          – constant thrust during BOOST (N)
#   drag_coefficient – Cd (dimensionless)
#   reference_area  – frontal reference area for drag (m^2)
#   launch_angle_deg – launch elevation (degrees)
#   initial_speed   – launch speed at t=0 (m/s)

MISSILE_LIBRARY = {
    "QRSAM": {
        "mass_initial": 1100.0,
        "propellant_mass": 600.0,     # dry mass = 500 kg
        "burn_time": 10.0,
        "thrust": 55_000.0,
        "drag_coefficient": 0.023,    # Cd * A ~0.0114 → Cd=0.023, A=0.5
        "reference_area": 0.5,
        "launch_angle_deg": 65.0,
        "initial_speed": 600.0,
    },
    "Akash": {
        "mass_initial": 1500.0,
        "propellant_mass": 800.0,     # dry mass = 700 kg
        "burn_time": 15.0,
        "thrust": 80_000.0,
        "drag_coefficient": 0.02,
        "reference_area": 0.6,
        "launch_angle_deg": 70.0,
        "initial_speed": 700.0,
    },
    "Prithvi": {
        "mass_initial": 4600.0,
        "propellant_mass": 2600.0,    # dry mass = 2000 kg
        "burn_time": 25.0,
        "thrust": 180_000.0,
        "drag_coefficient": 0.015,
        "reference_area": 1.0,
        "launch_angle_deg": 72.0,
        "initial_speed": 2200.0,
    },
    "Agni": {
        "mass_initial": 28_000.0,
        "propellant_mass": 20_000.0,  # dry mass = 8000 kg
        "burn_time": 65.0,
        "thrust": 900_000.0,
        "drag_coefficient": 0.012,
        "reference_area": 1.5,
        "launch_angle_deg": 78.0,
        "initial_speed": 4800.0,
    },
}


def get_missile_config(name: str) -> dict:
    """Return a copy of the missile configuration dictionary for *name*.

    Raises
    ------
    KeyError
        If the missile class is unknown.
    """
    cfg = MISSILE_LIBRARY.get(name)
    if cfg is None:
        raise KeyError(
            f"Unknown missile class: {name!r}. "
            f"Available: {', '.join(MISSILE_LIBRARY)}"
        )
    return dict(cfg)
