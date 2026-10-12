"""Deterministic linear/log calibration with explicitly separate broken-axis segments."""
from dataclasses import dataclass
import numpy as np

class CalibrationError(ValueError):
    pass

@dataclass(frozen=True)
class Segment:
    name: str
    kind: str
    slope: float
    intercept: float
    y_min: float
    y_max: float
    residual: float

    def value(self, y):
        if not np.isfinite(y) or not self.y_min <= y <= self.y_max:
            raise CalibrationError('Coordinate outside calibrated segment; extrapolation is disabled')
        v = self.slope * y + self.intercept
        return float(10 ** v if self.kind == 'log10' else v)

class AxisCalibration:
    def __init__(self, definitions):
        if not definitions:
            raise CalibrationError('Provide at least one calibrated axis segment')
        self.segments = {}
        for d in definitions:
            name = str(d.get('id', 'main'))
            if name in self.segments:
                raise CalibrationError('Duplicate axis segment id')
            kind = d.get('scale', 'linear')
            if kind not in ('linear', 'log10'):
                raise CalibrationError('Supported scales: linear, log10')
            points = np.asarray([[p['pixel_y'], p['value']] for p in d['ticks']], dtype=float)
            if points.ndim != 2 or points.shape[0] < 2 or points.shape[1] != 2 or not np.isfinite(points).all():
                raise CalibrationError('At least two finite tick coordinates/values required')
            y, v = points[:, 0], points[:, 1]
            if len(set(y)) != len(y) or len(set(v)) != len(v):
                raise CalibrationError('Duplicate tick position/value')
            ordered = v[np.argsort(y)]
            if not (np.all(np.diff(ordered) > 0) or np.all(np.diff(ordered) < 0)):
                raise CalibrationError('Tick values must be strictly monotonic')
            if kind == 'log10' and np.any(v <= 0):
                raise CalibrationError('Logarithmic tick values must be positive')
            target = np.log10(v) if kind == 'log10' else v
            slope, intercept = np.linalg.lstsq(np.column_stack((y, np.ones(len(y)))), target, rcond=None)[0]
            residual = float(np.max(np.abs(slope*y+intercept-target)))
            if residual > float(d.get('max_residual', 0.02 * np.ptp(target))):
                raise CalibrationError('Tick calibration residual exceeds configured tolerance')
            limits = d.get('pixel_range', [float(min(y)), float(max(y))])
            if len(limits) != 2 or limits[0] > limits[1] or limits[0] < min(y) or limits[1] > max(y):
                raise CalibrationError('Segment range must lie within supplied ticks')
            self.segments[name] = Segment(name, kind, float(slope), float(intercept), *map(float, limits), residual)
        segs = list(self.segments.values())
        for i, a in enumerate(segs):
            for b in segs[i+1:]:
                if max(a.y_min,b.y_min) <= min(a.y_max,b.y_max):
                    raise CalibrationError('Broken-axis segments must not overlap')

    def value(self, y, segment=None):
        if segment is not None:
            if segment not in self.segments:
                raise CalibrationError('Unknown axis segment')
            return self.segments[segment].value(float(y))
        matching = [s for s in self.segments.values() if s.y_min <= y <= s.y_max]
        if len(matching) != 1:
            raise CalibrationError('Coordinate lies in an axis break or outside calibrated ticks')
        return matching[0].value(float(y))

    def span(self, first_y, second_y, first_segment=None, second_segment=None):
        """Convert endpoints separately. Never interpolate through an axis break."""
        return abs(self.value(first_y, first_segment)-self.value(second_y, second_segment))
