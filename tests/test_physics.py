"""Unit tests for src.physics helper functions."""

import math
import unittest

# Allow running from the repo root
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.physics import (
    air_density,
    dynamic_pressure,
    drag_force,
    mach_number,
    velocity_components,
    kinetic_energy,
    g_load,
)


class TestAirDensity(unittest.TestCase):
    def test_sea_level(self):
        self.assertAlmostEqual(air_density(0), 1.225, places=3)

    def test_scale_height(self):
        # At H=8500 m, density should be ~1.225/e ≈ 0.4506
        self.assertAlmostEqual(air_density(8500), 1.225 / math.e, places=3)

    def test_high_altitude(self):
        # Very high altitude → near zero
        self.assertLess(air_density(100_000), 0.001)


class TestDynamicPressure(unittest.TestCase):
    def test_known_values(self):
        # q = 0.5 * 1.225 * 100^2 = 6125
        self.assertAlmostEqual(dynamic_pressure(1.225, 100), 6125.0, places=1)

    def test_zero_speed(self):
        self.assertEqual(dynamic_pressure(1.225, 0), 0.0)


class TestDragForce(unittest.TestCase):
    def test_known_values(self):
        # D = 0.5 * rho * v^2 * Cd * A
        # D = 0.5 * 1.225 * 100^2 * 0.3 * 1.0 = 1837.5
        self.assertAlmostEqual(drag_force(1.225, 100, 0.3, 1.0), 1837.5, places=1)


class TestMachNumber(unittest.TestCase):
    def test_sea_level(self):
        # Speed of sound at sea level ≈ 340.3 m/s → Mach 1
        self.assertAlmostEqual(mach_number(340.3, 0), 1.0, places=2)

    def test_subsonic(self):
        self.assertLess(mach_number(200, 0), 1.0)


class TestVelocityComponents(unittest.TestCase):
    def test_zero_degrees(self):
        vx, vy = velocity_components(100, 0)
        self.assertAlmostEqual(vx, 100, places=3)
        self.assertAlmostEqual(vy, 0, places=3)

    def test_90_degrees(self):
        vx, vy = velocity_components(100, 90)
        self.assertAlmostEqual(vx, 0, places=3)
        self.assertAlmostEqual(vy, 100, places=3)

    def test_45_degrees(self):
        vx, vy = velocity_components(100, 45)
        expected = 100 / math.sqrt(2)
        self.assertAlmostEqual(vx, expected, places=3)
        self.assertAlmostEqual(vy, expected, places=3)


class TestKineticEnergy(unittest.TestCase):
    def test_known(self):
        # KE = 0.5 * 10 * 20^2 = 2000
        self.assertAlmostEqual(kinetic_energy(10, 20), 2000.0, places=1)


class TestGLoad(unittest.TestCase):
    def test_zero_accel(self):
        # At rest: 1 g from gravity only
        self.assertAlmostEqual(g_load(0), 1.0, places=3)

    def test_one_g(self):
        # Additional 9.80665 m/s² → 2 g total
        self.assertAlmostEqual(g_load(9.80665), 2.0, places=3)


if __name__ == "__main__":
    unittest.main()
