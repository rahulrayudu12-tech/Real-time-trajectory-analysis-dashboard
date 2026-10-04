# src/visualization.py
"""Plotting utilities for the missile simulation.

Supports both standard and DRDL column namings (e.g. 'Time_s' or 'Time').
Each function receives the simulation ``DataFrame`` and optionally saves the
figure to ``notebooks/``.
"""

from __future__ import annotations

import pathlib
import matplotlib.pyplot as plt
import pandas as pd


def _save_fig(fig, filename: str) -> pathlib.Path:
    out_path = pathlib.Path("notebooks") / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    return out_path


def _get_col(df: pd.DataFrame, *candidates: str) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"None of {candidates} found in columns: {list(df.columns)}")


def plot_altitude(df: pd.DataFrame, show: bool = False, filename: str = "altitude_vs_time.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    t_col = _get_col(df, "Time_s", "Time")
    alt_col = _get_col(df, "Altitude_m", "Altitude")
    ax.plot(df[t_col], df[alt_col], label="Altitude (m)", color="navy", lw=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("Altitude vs. Time")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    _save_fig(fig, filename)
    if show:
        plt.show()
    plt.close(fig)


def plot_speed(df: pd.DataFrame, show: bool = False, filename: str = "speed_vs_time.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    t_col = _get_col(df, "Time_s", "Time")
    speed_col = _get_col(df, "Speed_ms", "Speed")
    ax.plot(df[t_col], df[speed_col], label="Speed (m/s)", color="crimson", lw=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Speed (m/s)")
    ax.set_title("Speed vs. Time")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    _save_fig(fig, filename)
    if show:
        plt.show()
    plt.close(fig)


def plot_range(df: pd.DataFrame, show: bool = False, filename: str = "range_vs_time.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    t_col = _get_col(df, "Time_s", "Time")
    rng_col = _get_col(df, "Range_m", "Range")
    ax.plot(df[t_col], df[rng_col], label="Range (m)", color="green", lw=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Range (m)")
    ax.set_title("Range vs. Time")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    _save_fig(fig, filename)
    if show:
        plt.show()
    plt.close(fig)


def plot_mach(df: pd.DataFrame, show: bool = False, filename: str = "mach_vs_time.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    t_col = _get_col(df, "Time_s", "Time")
    mach_col = _get_col(df, "Mach_Number", "MachNumber", "Mach")
    ax.plot(df[t_col], df[mach_col], label="Mach Number", color="darkorange", lw=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Mach")
    ax.set_title("Mach Number vs. Time")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    _save_fig(fig, filename)
    if show:
        plt.show()
    plt.close(fig)


def plot_dynamic_pressure(df: pd.DataFrame, show: bool = False, filename: str = "dynamic_pressure_vs_time.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    t_col = _get_col(df, "Time_s", "Time")
    dp_col = _get_col(df, "Dynamic_Pressure_Pa", "DynamicPressure")
    ax.plot(df[t_col], df[dp_col], label="Dynamic Pressure (Pa)", color="purple", lw=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Dynamic Pressure (Pa)")
    ax.set_title("Dynamic Pressure vs. Time")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    _save_fig(fig, filename)
    if show:
        plt.show()
    plt.close(fig)


def plot_g_load(df: pd.DataFrame, show: bool = False, filename: str = "g_load_vs_time.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    t_col = _get_col(df, "Time_s", "Time")
    if "G_Load" in df.columns:
        g_load_vals = df["G_Load"]
    else:
        acc_col = _get_col(df, "Total_Acceleration_ms2", "Acceleration")
        g_load_vals = 1 + df[acc_col] / 9.80665
    ax.plot(df[t_col], g_load_vals, label="G-load", color="teal", lw=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("G-load (g)")
    ax.set_title("G-load vs. Time")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    _save_fig(fig, filename)
    if show:
        plt.show()
    plt.close(fig)
