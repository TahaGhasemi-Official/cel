"""TG.WX series: practical extra calculators added in the web edition.

Each model: key, names, formula, topic, fields (key, fa, en, unit, default) and a
calculator that takes a getter ``g(key) -> float`` and returns named outputs.
"""
import math


def _pos(x, name):
    if not x > 0:
        raise ValueError(f"{name} must be greater than zero")
    return x


def _bands(g):
    d1, d2, m = g('d1'), g('d2'), g('m')
    for name, d in (('Band 1', d1), ('Band 2', d2)):
        if not (0 <= d <= 9 and float(d).is_integer()):
            raise ValueError(f"{name} must be a digit from 0 to 9")
    if not float(m).is_integer():
        raise ValueError("Multiplier exponent must be an integer")
    r = (10 * d1 + d2) * 10 ** m
    return {'Resistance (Ω)': r, 'Resistance (kΩ)': r / 1e3}


def _tol(g):
    r, t = g('r'), g('tol')
    _pos(r, 'Nominal resistance')
    if t < 0:
        raise ValueError("Tolerance cannot be negative")
    return {'Minimum (Ω)': r * (1 - t / 100), 'Maximum (Ω)': r * (1 + t / 100)}


def _copper(g):
    r1, t1, t2, a = g('r1'), g('t1'), g('t2'), g('alpha')
    if 1 + a * (t2 - t1) <= 0:
        raise ValueError("Temperature out of the valid range for this coefficient")
    return {'Resistance at T2 (Ω)': r1 * (1 + a * (t2 - t1))}


def _cap_series(g):
    c1, c2 = _pos(g('c1'), 'C1'), _pos(g('c2'), 'C2')
    return {'Equivalent C (same unit as input)': c1 * c2 / (c1 + c2)}


def _parallel_n(g):
    n, r = g('n'), g('r')
    if n < 1 or not float(n).is_integer():
        raise ValueError("Number of resistors must be a whole number ≥ 1")
    return {'Equivalent R (Ω)': _pos(r, 'Resistance') / n}


def _dbm_w(g):
    return {'Power (W)': 1e-3 * 10 ** (g('dbm') / 10)}


def _w_dbm(g):
    return {'Power (dBm)': 10 * math.log10(_pos(g('p'), 'Power') / 1e-3)}


def _db_v(g):
    return {'Voltage ratio (dB)': 20 * math.log10(_pos(g('v2'), 'V2') / _pos(g('v1'), 'V1'))}


def _battery_wh(g):
    return {'Energy (Wh)': g('v') * g('ah'), 'Energy (kWh)': g('v') * g('ah') / 1000}


def _crate(g):
    c = _pos(g('crate'), 'C-rate')
    return {'Current (A)': c * _pos(g('ah'), 'Capacity'), 'Runtime at this rate (h)': 1 / c}


# (key, name_fa, name_en, formula, fields, calc)
MODELS = [
    ('resistor_bands', 'کد رنگی مقاومت (۲ حلقه + ضریب)', 'Resistor Color Code (2 digits + multiplier)',
     'R = (10·d1 + d2)·10^m',
     [('d1', 'رقم حلقه ۱', 'Band 1 digit', '', '5'), ('d2', 'رقم حلقه ۲', 'Band 2 digit', '', '6'),
      ('m', 'توان ضریب (m)', 'Multiplier exponent (m)', '', '3')],
     _bands),
    ('tolerance', 'بازه مقاومت با تلرانس', 'Resistance Tolerance Range',
     'Rmin = R(1−t%), Rmax = R(1+t%)',
     [('r', 'مقاومت نامی', 'Nominal resistance', 'Ω', '100'), ('tol', 'تلرانس', 'Tolerance', '%', '5')],
     _tol),
    ('copper_temp', 'مقاومت مس در دمای دیگر', 'Copper Resistance at Another Temperature',
     'R2 = R1·(1 + α(T2 − T1)), α≈0.00393 /°C',
     [('r1', 'مقاومت در T1', 'Resistance at T1', 'Ω', '1'), ('t1', 'دمای T1', 'Temperature T1', '°C', '20'),
      ('t2', 'دمای T2', 'Temperature T2', '°C', '75'), ('alpha', 'ضریب α', 'Coefficient α', '1/°C', '0.00393')],
     _copper),
    ('cap_series', 'ظرفیت معادل دو خازن سری', 'Two Capacitors in Series',
     'Ceq = C1·C2/(C1+C2)',
     [('c1', 'خازن ۱', 'Capacitor C1', 'µF', '10'), ('c2', 'خازن ۲', 'Capacitor C2', 'µF', '22')],
     _cap_series),
    ('parallel_n', 'مقاومت معادل N مقاومت یکسان موازی', 'N Identical Resistors in Parallel',
     'Req = R/N',
     [('r', 'مقاومت هر شاخه', 'Resistance per branch', 'Ω', '100'), ('n', 'تعداد شاخه', 'Number of branches', '', '4')],
     _parallel_n),
    ('dbm_w', 'تبدیل dBm به وات', 'dBm to Watts',
     'P(W) = 1 mW · 10^(dBm/10)',
     [('dbm', 'توان', 'Power', 'dBm', '20')],
     _dbm_w),
    ('w_dbm', 'تبدیل وات به dBm', 'Watts to dBm',
     'dBm = 10·log10(P / 1 mW)',
     [('p', 'توان', 'Power', 'W', '0.1')],
     _w_dbm),
    ('db_v', 'نسبت ولتاژ به دسیبل', 'Voltage Ratio in Decibels',
     'dB = 20·log10(V2/V1)',
     [('v1', 'ولتاژ مرجع V1', 'Reference voltage V1', 'V', '1'), ('v2', 'ولتاژ V2', 'Voltage V2', 'V', '10')],
     _db_v),
    ('battery_wh', 'انرژی باتری (Wh)', 'Battery Energy (Wh)',
     'E(Wh) = V·Ah',
     [('v', 'ولتاژ اسمی', 'Nominal voltage', 'V', '12'), ('ah', 'ظرفیت', 'Capacity', 'Ah', '100')],
     _battery_wh),
    ('c_rate', 'جریان بر اساس C-rate', 'Current from C-rate',
     'I = C·Ah',
     [('ah', 'ظرفیت', 'Capacity', 'Ah', '100'), ('crate', 'نرخ تخلیه C', 'C-rate', 'C', '0.5')],
     _crate),
]

EXTRA_MODELS = []
EXTRA_FIELDS = {}
EXTRA_CALC = {}
for _i, (_key, _fa, _en, _formula, _fields, _fn) in enumerate(MODELS, 1):
    EXTRA_MODELS.append({"id": f"TG.WX/{_i:03d}", "series": "TG.WX", "name_en": _en, "name_fa": _fa,
                         "key": _key, "formula": _formula, "topic": "extra",
                         "description_en": _en + " (web edition extra).",
                         "description_fa": _fa + " (افزونه نسخه وب)."})
    EXTRA_FIELDS[_key] = _fields
    EXTRA_CALC[_key] = _fn


def calculate_extra(key, data):
    values = {}
    for k, _fa, _en, _unit, _default in EXTRA_FIELDS[key]:
        raw = str(data.get(k, "")).strip()
        if raw == "":
            raise ValueError(f"Missing input: {k}")
        try:
            x = float(raw)
        except ValueError:
            raise ValueError(f"Invalid number for {k}")
        if not math.isfinite(x):
            raise ValueError("Inputs must be finite numbers")
        values[k] = x
    return EXTRA_CALC[key](lambda k: values[k])
