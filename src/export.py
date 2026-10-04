"""CSV export utilities for the Antigravity Simulation.

The module provides a thin wrapper around ``pandas.DataFrame.to_csv`` so the
output location is centralised and can be customised in the future (e.g.,
cloud storage)."""

from __future__ import annotations

import pathlib
import pandas as pd

def export_to_csv(df: pd.DataFrame, filename: str = "missile_flight.csv") -> pathlib.Path:
    """Write *df* to ``data/<filename>``.

    Parameters
    ----------
    df : pandas.DataFrame
        The simulation result.
    filename : str, optional
        Desired CSV filename.  The function creates the ``data`` directory if it
        does not exist.
    """
    data_dir = pathlib.Path("data")
    data_dir.mkdir(exist_ok=True)
    out_path = data_dir / filename
    df.to_csv(out_path, index=False)
    return out_path
