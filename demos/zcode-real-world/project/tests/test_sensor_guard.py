import unittest

from src.sensor_guard import classify_temperature


class TemperatureClassificationTests(unittest.TestCase):
    def test_normal_temperature(self):
        self.assertEqual(classify_temperature(60.0), "normal")

    def test_warning_lower_boundary(self):
        self.assertEqual(classify_temperature(75.0), "warning")

    def test_warning_temperature(self):
        self.assertEqual(classify_temperature(80.0), "warning")

    def test_critical_boundary(self):
        self.assertEqual(classify_temperature(85.0), "critical")

    def test_critical_temperature(self):
        self.assertEqual(classify_temperature(90.0), "critical")


if __name__ == "__main__":
    unittest.main()
