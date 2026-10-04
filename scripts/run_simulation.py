#!/usr/bin/env python3
"""CLI entry point for the Antigravity Missile Simulation.

Examples
--------
Run all missile classes::

    python scripts/run_simulation.py

Run a single class with plots::

    python scripts/run_simulation.py --missile QRSAM --plot

Custom time step and duration::

    python scripts/run_simulation.py --missile Agni --dt 0.25 --total-time 1000
"""

from __future__ import annotations

import argparse
import os
import sys

# Allow running from the repo root (``python scripts/run_simulation.py``)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.simulation import run_simulation, run_all_simulations, export_to_csv, export_all


def _plot(results: dict) -> None:
    """Generate plots for every missile class in *results*."""
    from src.visualization import (
        plot_altitude,
        plot_speed,
        plot_range,
        plot_mach,
        plot_dynamic_pressure,
        plot_g_load,
    )

    for mc, df in results.items():
        prefix = mc.lower()
        print(f"  Plotting {mc} ...")
        plot_altitude(df, show=False, filename=f"{prefix}_altitude_vs_time.png")
        plot_speed(df, show=False, filename=f"{prefix}_speed_vs_time.png")
        plot_range(df, show=False, filename=f"{prefix}_range_vs_time.png")
        plot_mach(df, show=False, filename=f"{prefix}_mach_vs_time.png")
        plot_dynamic_pressure(df, show=False, filename=f"{prefix}_dynamic_pressure_vs_time.png")
        plot_g_load(df, show=False, filename=f"{prefix}_g_load_vs_time.png")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Antigravity Missile Flight Simulation",
    )
    parser.add_argument(
        "--missile",
        choices=["QRSAM", "Akash", "Prithvi", "Agni", "all"],
        default="all",
        help="Missile class to simulate (default: all)",
    )
    parser.add_argument("--dt", type=float, default=0.5, help="Time step in seconds")
    parser.add_argument(
        "--total-time", type=float, default=800.0, help="Max simulation time in seconds"
    )
    parser.add_argument(
        "--output-dir", type=str, default="data", help="Output directory for CSVs"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate Matplotlib plots after simulation",
    )

    args = parser.parse_args()

    if args.missile == "all":
        print("Running simulations for ALL missile classes …")
        results = run_all_simulations(dt=args.dt, total_time=args.total_time)
        paths = export_all(results, output_dir=args.output_dir)
        for p in paths:
            print(f"  [OK] {p}")
    else:
        print(f"Running simulation for {args.missile} …")
        df = run_simulation(args.missile, dt=args.dt, total_time=args.total_time)
        p = export_to_csv(
            df, f"missile_{args.missile.lower()}_class.csv", output_dir=args.output_dir
        )
        results = {args.missile: df}
        print(f"  [OK] {p}  ({len(df)} rows)")

    if args.plot:
        print("Generating plots …")
        _plot(results)
        print("  Plots saved to notebooks/")

    print("Done.")


if __name__ == "__main__":
    main()
