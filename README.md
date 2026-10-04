# Antigravity Missile Flight Simulation Agent

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)
![NumPy](https://img.shields.io/badge/NumPy-%E2%9C%93-green.svg)
![Pandas](https://img.shields.io/badge/Pandas-%E2%9C%93-green.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%E2%9C%93-green.svg)
![SciPy](https://img.shields.io/badge/SciPy-optional-lightgrey.svg)

## Overview

A physics‑based simulator for missile flight dynamics.  It generates **~1600+ rows** of time‑series trajectory data per run, covering three flight phases: **BOOST → MIDCOURSE → TERMINAL**.

The output CSV format is **identical to DRDL datasets**, making it suitable for downstream radar simulation, data‑fusion testing, and analytics dashboards.

## Supported Missile Classes

| Class | Mass (kg) | Burn Time (s) | Thrust (kN) | Launch Angle |
|-------|-----------|---------------|-------------|-------------|
| **QRSAM** | 600 | 15 | 150 | 45° |
| **Akash** | 2 500 | 30 | 400 | 40° |
| **Prithvi** | 8 000 | 45 | 900 | 35° |
| **Agni** | 12 000 | 60 | 1 200 | 30° |

## Flight Phases

1. **BOOST** — Motor active; thrust accelerates the missile along the launch vector. Propellant mass decreases linearly.
2. **MIDCOURSE** — Motor off; missile coasts under gravity and aerodynamic drag. Altitude may still be increasing.
3. **TERMINAL** — Missile descends; gravity and drag dominate. Simulation ends when altitude returns to zero.

## Repository Structure

```
.
├── README.md                     ← This file
├── requirements.txt              ← Python dependencies
├── .gitignore
├── src/
│   ├── __init__.py               ← Package init
│   ├── constants.py              ← Physical constants & missile library
│   ├── physics.py                ← Core physics helper functions
│   ├── simulation.py             ← Trajectory integration engine
│   ├── kalman.py                 ← Kalman filter for track smoothing
│   ├── export.py                 ← CSV export utility
│   └── visualization.py          ← Matplotlib plotting utilities
├── scripts/
│   └── run_simulation.py         ← CLI entry point
├── data/                         ← Generated CSV files (gitignored)
├── notebooks/                    ← Jupyter notebooks & saved plots
└── tests/
    ├── __init__.py
    └── test_physics.py           ← Unit tests for physics module
```

## Installation

```bash
git clone https://github.com/rahulrayudu12-tech/misssile-dataset.git
cd misssile-dataset
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Generate data for ALL missile classes
python scripts/run_simulation.py

# Single missile with plots
python scripts/run_simulation.py --missile QRSAM --plot

# Custom time‑step and duration
python scripts/run_simulation.py --missile Agni --dt 0.25 --total-time 1000

# Specify output directory
python scripts/run_simulation.py --output-dir my_output
```

### As a Python Library

```python
from src.simulation import run_simulation, export_to_csv

# Run QRSAM simulation
df = run_simulation("QRSAM", dt=0.5, total_time=800.0)
export_to_csv(df, "qrsam_output.csv")

print(df.head())
print(f"Total rows: {len(df)}")
```

### Batch Run (All Classes)

```python
from src.simulation import run_all_simulations, export_all

results = run_all_simulations()
export_all(results)  # Exports to data/ folder
```

### Kalman Filter (Optional)

```python
from src.simulation import run_simulation
from src.kalman import apply_kalman_filter

df = run_simulation("QRSAM")
df_smoothed = apply_kalman_filter(df, process_noise=1.0, measurement_noise=10.0)

# New columns: Range_Measured, Altitude_Measured, Range_Smoothed, Altitude_Smoothed
print(df_smoothed[["Range_m", "Range_Measured", "Range_Smoothed"]].head())
```

## Output CSV Columns

| Column | Unit | Description |
|--------|------|-------------|
| `Time_s` | s | Simulation time |
| `Missile_Class` | — | Missile class identifier |
| `Flight_Phase` | — | BOOST / MIDCOURSE / TERMINAL |
| `Altitude_m` | m | Altitude above sea level |
| `Altitude_km` | km | Altitude in kilometres |
| `Range_m` | m | Horizontal range |
| `Range_km` | km | Range in kilometres |
| `Speed_ms` | m/s | Scalar speed |
| `Speed_kmh` | km/h | Speed in km/h |
| `Absolute_Velocity_ms` | m/s | Absolute velocity magnitude |
| `Vx_ms` | m/s | Horizontal velocity component |
| `Vy_ms` | m/s | Vertical velocity component |
| `Ax_ms2` | m/s² | Horizontal acceleration |
| `Ay_ms2` | m/s² | Vertical acceleration |
| `Total_Acceleration_ms2` | m/s² | Acceleration magnitude |
| `Mach_Number` | — | Mach number |
| `G_Load` | g | G‑load |
| `Dynamic_Pressure_Pa` | Pa | Dynamic pressure |
| `Dynamic_Pressure_kPa` | kPa | Dynamic pressure in kPa |
| `Thrust_N` | N | Thrust force |
| `Thrust_kN` | kN | Thrust in kN |
| `Drag_Force_N` | N | Aerodynamic drag |
| `Mass_kg` | kg | Current missile mass |
| `Kinetic_Energy_J` | J | Kinetic energy |
| `Kinetic_Energy_MJ` | MJ | Kinetic energy in MJ |

## Physics Model

- **Atmospheric density**: Exponential model — `ρ = 1.225 × exp(−h / 8500)`
- **Drag**: Standard drag equation — `D = ½ ρ v² Cd A`
- **Thrust**: Constant during BOOST phase; zero in MIDCOURSE and TERMINAL
- **Gravity**: Constant `g = 9.80665 m/s²`, acting vertically downward
- **Mass**: Linear decrease during BOOST at rate `propellant_mass / burn_time`
- **Integration**: Explicit Euler method with configurable time‑step
- **Mach number**: `M = v / a`, where `a = 340.3 × √(1 − h/44300)`

## License

MIT License

## Author

**rahulrayudu12-tech** — [GitHub](https://github.com/rahulrayudu12-tech)
