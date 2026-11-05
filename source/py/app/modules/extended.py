"""Extended offline calculators (TG.VX series).

These are added on top of the 100 TG.VL profiles, which keep their IDs unchanged.
Each model defines its input fields (key, label-fa, label-en, unit, default) and a
calculator returning a dict of named outputs. SI units unless the unit is stated.
"""
import math

SQRT3 = math.sqrt(3.0)
PI = math.pi

# Field tuples: (key, label-fa, label-en, unit, default)
EXT_FIELDS = {
    'pct_drop': [
        ('dv', 'افت ولتاژ', 'Voltage drop', 'V', '12'),
        ('vn', 'ولتاژ نامی', 'Nominal voltage', 'V', '230'),
    ],
    'kva_current_1p': [
        ('s', 'توان ظاهری', 'Apparent power', 'kVA', '10'),
        ('v', 'ولتاژ', 'Voltage', 'V', '230'),
    ],
    'kw_hp': [
        ('kw', 'توان مکانیکی', 'Mechanical power', 'kW', '7.5'),
    ],
    'rod_resistance': [
        ('rho', 'مقاومت ویژه خاک', 'Soil resistivity', 'Ω·m', '100'),
        ('l', 'طول میله', 'Rod length', 'm', '2.4'),
        ('d', 'قطر میله', 'Rod diameter', 'm', '0.016'),
    ],
    'isc_3p': [
        ('v', 'ولتاژ خط', 'Line voltage', 'V', '400'),
        ('z', 'امپدانس تا نقطه خطا', 'Impedance to fault', 'Ω', '0.05'),
    ],
    'cap_charge': [
        ('v', 'ولتاژ منبع', 'Supply voltage', 'V', '12'),
        ('r', 'مقاومت سری', 'Series resistance', 'Ω', '1000'),
        ('c', 'ظرفیت', 'Capacitance', 'F', '0.0001'),
        ('t', 'زمان', 'Time', 's', '0.5'),
    ],
    'ripple': [
        ('i', 'جریان بار', 'Load current', 'A', '1'),
        ('f', 'فرکانس ورودی', 'Input frequency', 'Hz', '100'),
        ('c', 'ظرفیت فیلتر', 'Filter capacitance', 'F', '0.001'),
    ],
    'peukert': [
        ('c', 'ظرفیت نامی (در نرخ مرجع)', 'Rated capacity (at reference rate)', 'Ah', '100'),
        ('i', 'جریان تخلیه', 'Discharge current', 'A', '5'),
        ('k', 'ضریب Peukert', 'Peukert exponent', '', '1.2'),
        ('h', 'ساعت مرجع', 'Reference hours', 'h', '20'),
    ],
    'y_delta': [
        ('r', 'مقاومت', 'Resistance', 'Ω', '30'),
    ],
    'wheatstone': [
        ('r1', 'مقاومت R1', 'Resistor R1', 'Ω', '100'),
        ('r2', 'مقاومت R2', 'Resistor R2', 'Ω', '200'),
        ('r3', 'مقاومت R3', 'Resistor R3', 'Ω', '50'),
    ],
    'thd': [
        ('i1', 'هارمونیک اصلی', 'Fundamental current', 'A', '100'),
        ('i3', 'هارمونیک ۳', '3rd harmonic current', 'A', '20'),
        ('i5', 'هارمونیک ۵', '5th harmonic current', 'A', '10'),
        ('i7', 'هارمونیک ۷', '7th harmonic current', 'A', '5'),
    ],
    'cable_loss': [
        ('i', 'جریان خط', 'Line current', 'A', '50'),
        ('r', 'مقاومت هادی', 'Conductor resistance', 'Ω/km', '0.5'),
        ('l', 'طول کابل', 'Cable length', 'm', '200'),
        ('v', 'ولتاژ خط', 'Line voltage', 'V', '400'),
        ('pf', 'ضریب توان', 'Power factor', 'cosφ', '0.85'),
    ],
    'derate': [
        ('ib', 'جریان پایه', 'Base current', 'A', '100'),
        ('kt', 'ضریب تصحیح دما', 'Temperature factor', '', '0.9'),
        ('kg', 'ضریب گروه‌بندی', 'Grouping factor', '', '0.8'),
    ],
    'cap_bank': [
        ('q', 'توان راکتیو بانک', 'Bank reactive power', 'kvar', '50'),
        ('v', 'ولتاژ خط', 'Line voltage', 'V', '400'),
        ('f', 'فرکانس', 'Frequency', 'Hz', '50'),
    ],
    'pf_kw_kvar': [
        ('p', 'توان اکتیو', 'Active power', 'kW', '100'),
        ('q', 'توان راکتیو', 'Reactive power', 'kvar', '50'),
    ],
    'trafo_z_ohm': [
        ('zp', 'امپدانس درصدی', 'Percent impedance', '%', '6'),
        ('vn', 'ولتاژ نامی', 'Rated voltage', 'V', '400'),
        ('sn', 'توان نامی ترانس', 'Rated power', 'kVA', '100'),
    ],
    # bus_drop is TG.VL/100; its inputs and calculator are defined here.
    'bus_drop': [
        ('i', 'جریان', 'Current', 'A', '400'),
        ('r', 'مقاومت شینه', 'Busbar resistance', 'Ω', '0.001'),
    ],
}

# Extended calculators: fn(g) -> dict, where g(key) returns a validated float.
def _positive(x, name):
    if not x > 0:
        raise ValueError(f"{name} must be greater than zero")
    return x

EXT_CALC = {
    'pct_drop': lambda g: {'Voltage drop (%)': 100 * g('dv') / _positive(g('vn'), 'Nominal voltage')},
    'kva_current_1p': lambda g: {'Current (A)': g('s') * 1000 / _positive(g('v'), 'Voltage')},
    'kw_hp': lambda g: {'Power (HP)': g('kw') / 0.746},
    'rod_resistance': lambda g: _rod(g),
    'isc_3p': lambda g: {'Fault current (A)': g('v') / (SQRT3 * _positive(g('z'), 'Impedance'))},
    'cap_charge': lambda g: _cap_charge(g),
    'ripple': lambda g: {'Peak-to-peak ripple (V)': g('i') / (2 * _positive(g('f'), 'Frequency') * _positive(g('c'), 'Capacitance'))},
    'peukert': lambda g: _peukert(g),
    'y_delta': lambda g: {'Equivalent star resistor (Ω) = R/3': g('r') / 3, 'Equivalent delta resistor (Ω) = 3R': 3 * g('r')},
    'wheatstone': lambda g: {'Rx (Ω) = R2×R3/R1': g('r2') * g('r3') / _positive(g('r1'), 'R1')},
    'thd': lambda g: {'THD (%)': 100 * math.sqrt(g('i3') ** 2 + g('i5') ** 2 + g('i7') ** 2) / _positive(g('i1'), 'Fundamental current')},
    'cable_loss': lambda g: _cable_loss(g),
    'derate': lambda g: {'Derated current (A)': g('ib') * g('kt') * g('kg')},
    'cap_bank': lambda g: _cap_bank(g),
    'pf_kw_kvar': lambda g: _pf(g),
    'trafo_z_ohm': lambda g: {'Impedance (Ω)': g('zp') / 100 * _positive(g('vn'), 'Rated voltage') ** 2 / (_positive(g('sn'), 'Rated power') * 1000)},
    'bus_drop': lambda g: {'Busbar voltage drop (V)': g('i') * g('r')},
}


def _rod(g):
    rho, l, d = g('rho'), _positive(g('l'), 'Rod length'), _positive(g('d'), 'Rod diameter')
    if 4 * l / d <= math.e:  # ln(4L/d) − 1 must be positive for the Dwight formula
        raise ValueError("Rod is too short for its diameter (need 4L/d greater than e)")
    return {'Rod resistance (Ω)': rho / (2 * PI * l) * (math.log(4 * l / d) - 1)}


def _cap_charge(g):
    tau = _positive(g('r') * g('c'), 'R×C')
    t = g('t')
    return {'Capacitor voltage (V)': g('v') * (1 - math.exp(-t / tau)), 'Time constant τ (s)': tau}


def _peukert(g):
    c, i, k, h = _positive(g('c'), 'Capacity'), _positive(g('i'), 'Current'), g('k'), _positive(g('h'), 'Reference hours')
    if k < 1:
        raise ValueError("Peukert exponent must be at least 1")
    return {'Runtime (h)': h * (c / (i * h)) ** k}


def _cable_loss(g):
    i, r, l = g('i'), g('r'), g('l')
    v, pf = _positive(g('v'), 'Line voltage'), g('pf')
    if not 0 < pf <= 1:
        raise ValueError("Power factor must be in (0, 1]")
    p_loss = 3 * i ** 2 * r * (l / 1000)
    p_load = SQRT3 * v * i * pf
    return {'Cable loss (W)': p_loss, 'Loss (% of delivered power)': 100 * p_loss / _positive(p_load, 'Load power')}


def _cap_bank(g):
    q, v, f = g('q') * 1000, _positive(g('v'), 'Line voltage'), _positive(g('f'), 'Frequency')
    w = 2 * PI * f
    c_delta = q / (3 * w * v * v) * 1e6
    c_star = q / (w * v * v) * 1e6
    return {'Capacitance per phase, Δ (µF)': c_delta, 'Capacitance per phase, Y (µF)': c_star}


def _pf(g):
    p, q = g('p'), g('q')
    s = math.hypot(p, q)
    if s == 0:
        raise ValueError("Power triangle is empty")
    return {'Power factor': abs(p) / s, 'Apparent power (kVA)': s}


EXT_META = [
    {'key': 'pct_drop', 'en': 'Voltage Drop Percentage', 'fa': 'درصد افت ولتاژ', 'topic': 'cables',
     'formula': 'ΔV% = ΔV / Vn × 100', 'desc_en': 'Voltage drop as a percentage of nominal voltage.', 'desc_fa': 'افت ولتاژ به‌صورت درصدی از ولتاژ نامی.'},
    {'key': 'kva_current_1p', 'en': 'Single-phase Current from kVA', 'fa': 'جریان تک‌فاز از کیلوولت‌آمپر', 'topic': 'power',
     'formula': 'I = S(kVA)×1000 / V', 'desc_en': 'Current of a single-phase load from its apparent power.', 'desc_fa': 'جریان بار تک‌فاز از روی توان ظاهری.'},
    {'key': 'kw_hp', 'en': 'kW to Horsepower', 'fa': 'تبدیل kW به اسب بخار', 'topic': 'motors',
     'formula': 'HP = kW / 0.746', 'desc_en': 'Converts mechanical power from kW to horsepower.', 'desc_fa': 'تبدیل توان مکانیکی از کیلووات به اسب بخار.'},
    {'key': 'rod_resistance', 'en': 'Ground Rod Resistance', 'fa': 'مقاومت میله زمین', 'topic': 'protection',
     'formula': 'R = ρ/(2πL)·[ln(4L/d) − 1]', 'desc_en': 'Resistance of a vertical ground rod (Dwight form).', 'desc_fa': 'مقاومت یک میله زمین عمودی (رابطه Dwight).'},
    {'key': 'isc_3p', 'en': 'Three-phase Fault Current from Impedance', 'fa': 'جریان اتصال کوتاه سه‌فاز از امپدانس', 'topic': 'protection',
     'formula': 'Isc = V / (√3·Z)', 'desc_en': 'Bolted three-phase fault current for a known loop impedance.', 'desc_fa': 'جریان اتصال کوتاه سه‌فاز برای امپدانس معلوم تا نقطه خطا.'},
    {'key': 'cap_charge', 'en': 'RC Charging Voltage', 'fa': 'ولتاژ شارژ خازن RC', 'topic': 'circuits',
     'formula': 'Vc(t) = V(1 − e^(−t/RC))', 'desc_en': 'Capacitor voltage during charging through a resistor.', 'desc_fa': 'ولتاژ خازن در حین شارژ از طریق مقاومت.'},
    {'key': 'ripple', 'en': 'Full-wave Rectifier Ripple', 'fa': 'ریپل یکسوساز تمام‌موج', 'topic': 'circuits',
     'formula': 'Vr(pp) = I / (2fC)', 'desc_en': 'Peak-to-peak ripple of a capacitor-filtered full-wave rectifier.', 'desc_fa': 'ریپل قله‌به‌قله یکسوساز تمام‌موج با فیلتر خازنی.'},
    {'key': 'peukert', 'en': 'Battery Runtime (Peukert)', 'fa': 'زمان تخلیه باتری (Peukert)', 'topic': 'energy',
     'formula': 't = H·(C / (I·H))^k', 'desc_en': 'Runtime corrected for discharge rate with the Peukert exponent.', 'desc_fa': 'زمان تخلیه باتری با اصلاح نرخ تخلیه (ضریب Peukert).'},
    {'key': 'y_delta', 'en': 'Star–Delta Resistor Equivalent', 'fa': 'معادل ستاره/مثلث مقاومت', 'topic': 'circuits',
     'formula': 'R_Y = R_Δ/3 ؛ R_Δ = 3·R_Y', 'desc_en': 'Equivalent resistor values for Y and Δ networks.', 'desc_fa': 'مقادیر معادل مقاومت در شبکه ستاره و مثلث.'},
    {'key': 'wheatstone', 'en': 'Wheatstone Bridge Balance', 'fa': 'تعادل پل وتستون', 'topic': 'circuits',
     'formula': 'Rx = R2·R3 / R1', 'desc_en': 'Unknown resistance at balance of a Wheatstone bridge.', 'desc_fa': 'مقاومت مجهول در حالت تعادل پل وتستون.'},
    {'key': 'thd', 'en': 'Total Harmonic Distortion', 'fa': 'اعوجاج هارمونیکی کل (THD)', 'topic': 'power',
     'formula': 'THD = √(I3²+I5²+I7²) / I1 × 100', 'desc_en': 'Current THD from the fundamental and odd harmonic amplitudes.', 'desc_fa': 'THD جریان از دامنه هارمونیک اصلی و فرد.'},
    {'key': 'cable_loss', 'en': 'Three-phase Cable Loss', 'fa': 'تلفات کابل سه‌فاز', 'topic': 'cables',
     'formula': 'Ploss = 3·I²·R·L/1000', 'desc_en': 'Conductor loss of a three-phase cable run.', 'desc_fa': 'تلفات هادی در یک مسیر کابل سه‌فاز.'},
    {'key': 'derate', 'en': 'Derated Cable Current', 'fa': 'جریان کاهش‌یافته کابل', 'topic': 'cables',
     'formula': 'Iadj = Ib · kt · kg', 'desc_en': 'Applies user-supplied correction factors. Factors must come from the applicable standard table.', 'desc_fa': 'اعمال ضرایب تصحیح وارد‌شده. ضرایب باید از جدول استاندارد مربوط باشد.'},
    {'key': 'cap_bank', 'en': 'Three-phase Capacitor Bank Sizing', 'fa': 'محاسبه خازن بانک سه‌فاز', 'topic': 'power',
     'formula': 'C_Δ = Q/(3ωV²) ؛ C_Y = Q/(ωV²)', 'desc_en': 'Capacitance per phase for Δ and Y connected banks.', 'desc_fa': 'ظرفیت هر فاز برای بانک خازنی به‌صورت Δ و Y.'},
    {'key': 'pf_kw_kvar', 'en': 'Power Factor from kW and kvar', 'fa': 'ضریب توان از kW و kvar', 'topic': 'power',
     'formula': 'pf = P / √(P² + Q²)', 'desc_en': 'Power factor and apparent power from active and reactive power.', 'desc_fa': 'ضریب توان و توان ظاهری از توان اکتیو و راکتیو.'},
    {'key': 'trafo_z_ohm', 'en': 'Transformer Impedance in Ohms', 'fa': 'امپدانس ترانس بر حسب اهم', 'topic': 'transformers',
     'formula': 'Z(Ω) = Z% / 100 · V² / S', 'desc_en': 'Converts percent impedance to ohms on the referred voltage side.', 'desc_fa': 'تبدیل امپدانس درصدی به اهم در سمت ولتاژ مرجع.'},
    {'key': 'pfc', 'en': 'Power Factor Correction', 'fa': 'اصلاح ضریب توان', 'topic': 'power',
     'formula': 'Qc = P(tanφ1 − tanφ2)', 'desc_en': 'Reactive compensation needed to raise power factor to a target value.', 'desc_fa': 'توان راکتیو لازم برای رسیدن ضریب توان به مقدار هدف.'},
    {'key': 'cost', 'en': 'Electrical Cost', 'fa': 'هزینه انرژی الکتریکی', 'topic': 'power',
     'formula': 'Cost = E × tariff', 'desc_en': 'Energy cost from average power, time and tariff per kWh.', 'desc_fa': 'هزینه انرژی از توان متوسط، زمان و تعرفه هر کیلووات‌ساعت.'},
]
