"""Kalman filter for radar track smoothing and prediction.

Provides a constant‑velocity 2‑D Kalman tracker that can be applied to simulated
missile trajectory data to emulate radar measurement noise and subsequent
smoothing — useful for testing radar data fusion pipelines.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class KalmanTracker:
    """2‑D constant‑velocity Kalman filter.

    State vector: ``[x, vx, y, vy]``

    Parameters
    ----------
    dt : float
        Time‑step between updates (s).
    process_noise : float
        Process noise scaling factor (larger → trust model less).
    measurement_noise : float
        Measurement noise standard deviation in metres.
    """

    def __init__(
        self,
        dt: float,
        process_noise: float = 1.0,
        measurement_noise: float = 10.0,
    ):
        self.dt = dt

        # State transition matrix (constant velocity)
        self.F = np.array(
            [
                [1, dt, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, dt],
                [0, 0, 0, 1],
            ],
            dtype=float,
        )

        # Measurement matrix (we observe x and y only)
        self.H = np.array(
            [
                [1, 0, 0, 0],
                [0, 0, 1, 0],
            ],
            dtype=float,
        )

        # Process noise covariance
        q = process_noise
        self.Q = q * np.array(
            [
                [dt ** 4 / 4, dt ** 3 / 2, 0, 0],
                [dt ** 3 / 2, dt ** 2, 0, 0],
                [0, 0, dt ** 4 / 4, dt ** 3 / 2],
                [0, 0, dt ** 3 / 2, dt ** 2],
            ],
            dtype=float,
        )

        # Measurement noise covariance
        self.R = (measurement_noise ** 2) * np.eye(2)

        # Initial state & covariance (will be set on first update)
        self.x = np.zeros(4)
        self.P = np.eye(4) * 500.0
        self._initialized = False

    # ---- Core filter steps ------------------------------------------------

    def predict(self) -> np.ndarray:
        """Predict the next state."""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x.copy()

    def update(self, z: np.ndarray) -> np.ndarray:
        """Update state with measurement ``z = [x_measured, y_measured]``.

        On first call the state is initialised from the measurement.
        """
        z = np.asarray(z, dtype=float)
        if not self._initialized:
            self.x[0] = z[0]
            self.x[2] = z[1]
            self._initialized = True
            return self.x.copy()

        y = z - self.H @ self.x  # innovation
        S = self.H @ self.P @ self.H.T + self.R  # innovation covariance
        K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P
        return self.x.copy()

    def get_state(self) -> np.ndarray:
        """Return current state estimate ``[x, vx, y, vy]``."""
        return self.x.copy()


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

def apply_kalman_filter(
    df: pd.DataFrame,
    process_noise: float = 1.0,
    measurement_noise: float = 10.0,
    seed: int = 42,
) -> pd.DataFrame:
    """Add noisy radar measurements and Kalman‑smoothed tracks to *df*.

    New columns added
    -----------------
    ``Range_Measured``, ``Altitude_Measured`` — simulated radar observations
    ``Range_Smoothed``, ``Altitude_Smoothed`` — Kalman‑filtered estimates

    Parameters
    ----------
    df : pandas.DataFrame
        Simulation output containing at least ``Time_s``, ``Range_m``, and
        ``Altitude_m``.
    process_noise, measurement_noise : float
        Kalman filter tuning knobs.
    seed : int
        Random seed for reproducibility of the additive noise.
    """
    rng = np.random.default_rng(seed)

    dt = df["Time_s"].diff().median()
    kf = KalmanTracker(dt, process_noise, measurement_noise)

    noise_range = rng.normal(0, measurement_noise, size=len(df))
    noise_alt = rng.normal(0, measurement_noise, size=len(df))

    df = df.copy()
    df["Range_Measured"] = df["Range_m"] + noise_range
    df["Altitude_Measured"] = df["Altitude_m"] + noise_alt

    smoothed_range = []
    smoothed_alt = []

    for _, row in df.iterrows():
        kf.predict()
        state = kf.update(np.array([row["Range_Measured"], row["Altitude_Measured"]]))
        smoothed_range.append(state[0])
        smoothed_alt.append(state[2])

    df["Range_Smoothed"] = smoothed_range
    df["Altitude_Smoothed"] = smoothed_alt
    return df
