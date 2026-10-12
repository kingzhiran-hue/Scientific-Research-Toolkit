"""Semi-manual scientific bar-chart digitization, version 0.1.0."""
__version__ = '0.1.0'
from .calibration import AxisCalibration, CalibrationError
from .measure import digitize
