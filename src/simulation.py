"""Antigravity Missile Flight Simulation – Core Engine

Generates ~1600 rows of time‑series trajectory data for four missile classes
(QRSAM, Akash, Prithvi, Agni) using 2‑D Euler integration through three
flight phases: BOOST, MIDCOURSE, TERMINAL.

CSV output columns match the DRDL dataset format exactly.
"""

from __future__ import annotations

import math
import os
import pathlib

import pandas as pd

# Graceful import – works both as a package member and as a standalone script.
try:
    from .constants import G, MISSILE_LIBRARY, get_missile_config
    from .physics import (
        air_density,
        drag_force,
        dynamic_pressure,
        kinetic_energy,
        mach_number,
        g_load,
    )
except ImportError:
    from constants import G, MISSILE_LIBRARY, get_missile_config
    from physics import (
        air_density,
        drag_force,
        dynamic_pressure,
        kinetic_energy,
        mach_number,
        g_load,
    )

# ---------------------------------------------------------------------------
# Column order (must match DRDL dataset)
# ---------------------------------------------------------------------------
CSV_COLUMNS = [
    "Time_s",
    "Missile_Class",
    "Flight_Phase",
    "Altitude_m",
    "Altitude_km",
    "Range_m",
    "Range_km",
    "Speed_ms",
    "Speed_kmh",
    "Absolute_Velocity_ms",
    "Vx_ms",
    "Vy_ms",
    "Ax_ms2",
    "Ay_ms2",
    "Total_Acceleration_ms2",
    "Mach_Number",
    "G_Load",
    "Dynamic_Pressure_Pa",
    "Dynamic_Pressure_kPa",
    "Thrust_N",
    "Thrust_kN",
    "Drag_Force_N",
    "Mass_kg",
    "Kinetic_Energy_J",
    "Kinetic_Energy_MJ",
]

# ---------------------------------------------------------------------------
# Primary simulation driver
# ---------------------------------------------------------------------------

def run_simulation(
    missile_class: str,
    dt: float = 0.5,
    total_time: float = 800.0,
) -> pd.DataFrame:
    """Simulate a missile trajectory and return a DataFrame.

    Parameters
    ----------
    missile_class : str
        One of ``'QRSAM'``, ``'Akash'``, ``'Prithvi'``, ``'Agni'``.
    dt : float
        Integration time‑step in seconds (default 0.5 → ~1600 rows).
    total_time : float
        Maximum simulation duration in seconds.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns matching ``CSV_COLUMNS``.
    """
    cfg = get_missile_config(missile_class)

    burn_time = cfg["burn_time"]
    thrust_val = cfg["thrust"]
    mass_initial = cfg["mass_initial"]
    propellant_mass = cfg["propellant_mass"]
    dry_mass = mass_initial - propellant_mass
    cd = cfg["drag_coefficient"]
    area = cfg["reference_area"]
    launch_angle_deg = cfg["launch_angle_deg"]
    launch_angle_rad = math.radians(launch_angle_deg)

    mass_burn_rate = propellant_mass / burn_time if burn_time > 0 else 0.0
    initial_speed = cfg.get("initial_speed", 0.0)

    # State variables
    t = 0.0
    vx = initial_speed * math.cos(launch_angle_rad)
    vy = initial_speed * math.sin(launch_angle_rad)
    x, y = 0.0, 0.0
    mass = mass_initial
    max_altitude = 0.0

    records: list[dict] = []

    while t <= total_time:
        # ----- Determine flight phase -----
        if t < burn_time:
            phase = "BOOST"
        elif vy >= -0.1:
            phase = "MIDCOURSE"
        else:
            phase = "TERMINAL"

        if y > max_altitude:
            max_altitude = y

        # Stop when missile hits ground after ascending
        if y < 0 and max_altitude > 10.0:
            break

        speed = math.sqrt(vx ** 2 + vy ** 2)

        # ----- Thrust -----
        if phase == "BOOST":
            thrust = thrust_val
            mass = max(dry_mass, mass - mass_burn_rate * dt)
            # Thrust direction follows velocity once moving; else launch angle
            angle = math.atan2(vy, vx) if speed > 5.0 else launch_angle_rad
            thrust_x = thrust * math.cos(angle)
            thrust_y = thrust * math.sin(angle)
        else:
            thrust = 0.0
            thrust_x, thrust_y = 0.0, 0.0

        # ----- Gravity (acts on Vy only) -----
        gravity_y = -mass * G

        # ----- Drag (opposite to velocity vector) -----
        rho = air_density(max(y, 0.0))
        drag_val = drag_force(rho, speed, cd, area)

        if speed > 0.1:
            drag_x = -drag_val * (vx / speed)
            drag_y = -drag_val * (vy / speed)
        else:
            drag_x, drag_y = 0.0, 0.0

        # ----- Net force & acceleration -----
        fx = thrust_x + drag_x
        fy = thrust_y + gravity_y + drag_y
        ax = fx / mass
        ay = fy / mass
        total_accel = math.sqrt(ax ** 2 + ay ** 2)

        # ----- Derived quantities -----
        speed_kmh = speed * 3.6
        mach_val = mach_number(speed, max(y, 0.0))
        g_load_val = g_load(total_accel)
        dyn_press = dynamic_pressure(rho, speed)
        ke = kinetic_energy(mass, speed)

        m_class = f"{missile_class}_Class"

        records.append(
            {
                "Time_s": round(t, 4),
                "Missile_Class": m_class,
                "Flight_Phase": phase,
                "Altitude_m": round(y, 4),
                "Altitude_km": round(y / 1000.0, 4),
                "Range_m": round(x, 4),
                "Range_km": round(x / 1000.0, 4),
                "Speed_ms": round(speed, 4),
                "Speed_kmh": round(speed_kmh, 4),
                "Absolute_Velocity_ms": round(speed, 4),
                "Vx_ms": round(vx, 4),
                "Vy_ms": round(vy, 4),
                "Ax_ms2": round(ax, 4),
                "Ay_ms2": round(ay, 4),
                "Total_Acceleration_ms2": round(total_accel, 4),
                "Mach_Number": round(mach_val, 4),
                "G_Load": round(g_load_val, 4),
                "Dynamic_Pressure_Pa": round(dyn_press, 4),
                "Dynamic_Pressure_kPa": round(dyn_press / 1000.0, 4),
                "Thrust_N": round(thrust, 4),
                "Thrust_kN": round(thrust / 1000.0, 4),
                "Drag_Force_N": round(drag_val, 4),
                "Mass_kg": round(mass, 4),
                "Kinetic_Energy_J": round(ke, 2),
                "Kinetic_Energy_MJ": round(ke / 1e6, 4),
            }
        )

        # ----- Euler integration step -----
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt

    df = pd.DataFrame(records)
    # Ensure column order matches DRDL dataset
    for c in CSV_COLUMNS:
        if c not in df.columns:
            df[c] = 0.0
    return df[CSV_COLUMNS]


# ---------------------------------------------------------------------------
# Batch helpers
# ---------------------------------------------------------------------------

def run_all_simulations(dt: float = 0.5, total_time: float = 800.0) -> dict[str, pd.DataFrame]:
    """Run simulations for all four missile classes and return a dict."""
    classes = ["QRSAM", "Akash", "Prithvi", "Agni"]
    return {mc: run_simulation(mc, dt=dt, total_time=total_time) for mc in classes}


def export_to_csv(
    df: pd.DataFrame,
    filename: str,
    output_dir: str = "data",
) -> pathlib.Path:
    """Write *df* to ``<output_dir>/<filename>``."""
    out = pathlib.Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / filename
    df.to_csv(path, index=False)
    return path


def export_all(
    results: dict[str, pd.DataFrame],
    output_dir: str = "data",
) -> list[pathlib.Path]:
    """Export every DataFrame in *results* to its own CSV."""
    paths = []
    for mc, df in results.items():
        p = export_to_csv(df, f"missile_{mc.lower()}_class.csv", output_dir)
        paths.append(p)
    return paths


# ---------------------------------------------------------------------------
# Quick‑run entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    results = run_all_simulations()
    paths = export_all(results)
    for p in paths:
        print(f"Exported → {p}  ({len(pd.read_csv(p))} rows)")
