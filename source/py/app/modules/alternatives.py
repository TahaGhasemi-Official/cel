"""Alternative formulas for every model that has one.

When a user does not know one of the values of the primary formula, these relations
compute the same quantity (or a related one) from a different set of inputs.

* ``AUX`` lists optional extra inputs a model accepts only for alternative formulas.
  They never change the primary calculation.
* ``SPECS`` lists the alternative relations. Each relation is written as a Python-like
  expression over input keys (field or aux names), evaluated by a restricted AST
  evaluator. No ``eval`` is used.

Expressions may use: + - * / ** parentheses, SQRT3, PI, and the functions in ``FUNCS``.
"""
import ast
import math
import operator
import re

from app.modules.engine import FIELDS, SQRT3, PI

CONSTS = {'SQRT3': SQRT3, 'PI': PI}
FUNCS = {
    'sqrt': math.sqrt, 'acos': math.acos, 'asin': math.asin, 'atan': math.atan,
    'cos': math.cos, 'sin': math.sin, 'tan': math.tan, 'exp': math.exp,
    'log': math.log, 'log10': math.log10, 'radians': math.radians,
    'degrees': math.degrees, 'abs': abs,
}
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow}
_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}


# ---------------------------------------------------------------- safe evaluator

def _parse(expr):
    tree = ast.parse(expr, mode='eval')
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name) and node.func.id in FUNCS) or node.keywords:
                raise ValueError(f"Unsupported function in: {expr}")
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in _BIN:
                raise ValueError(f"Unsupported operator in: {expr}")
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in _UNARY:
                raise ValueError(f"Unsupported operator in: {expr}")
        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError(f"Unsupported constant in: {expr}")
        elif not isinstance(node, (ast.Expression, ast.Name, ast.Load, ast.operator, ast.unaryop)):
            raise ValueError(f"Unsupported syntax in: {expr}")
    return tree


def _names(tree):
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} - set(FUNCS) - set(CONSTS)


def _eval(node, env):
    if isinstance(node, ast.Expression):
        return _eval(node.body, env)
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.Name):
        return CONSTS[node.id] if node.id in CONSTS else env[node.id]
    if isinstance(node, ast.BinOp):
        return _BIN[type(node.op)](_eval(node.left, env), _eval(node.right, env))
    if isinstance(node, ast.UnaryOp):
        return _UNARY[type(node.op)](_eval(node.operand, env))
    if isinstance(node, ast.Call):
        return FUNCS[node.func.id](*[_eval(a, env) for a in node.args])
    raise ValueError("Unsupported expression")


def _pretty(v):
    v = float(v)
    if v.is_integer() and abs(v) < 1e12:
        return int(v)
    return float(f"{v:.6g}")


class _Substitute(ast.NodeTransformer):
    def __init__(self, env):
        self.env = env

    def visit_Name(self, node):
        if node.id in self.env:
            return ast.copy_location(ast.Constant(value=_pretty(self.env[node.id])), node)
        return node


def _substituted_text(expr, env):
    tree = _Substitute(env).visit(ast.parse(expr, mode='eval'))
    ast.fix_missing_locations(tree)
    text = ast.unparse(tree)
    text = re.sub(r'\s*\*\*\s*2\b', '²', text)
    text = text.replace('SQRT3', '√3').replace('PI', 'π').replace('sqrt(', '√(')
    return text


# ---------------------------------------------------------------- data

# Optional extra inputs per model: (key, label-fa, label-en, unit, '')
AUX = {
    'dc_power': [('r', 'مقاومت', 'Resistance', 'Ω', '')],
    'ac_single': [('s', 'توان ظاهری', 'Apparent power', 'VA', '')],
    'ac_three': [('s', 'توان ظاهری', 'Apparent power', 'VA', '')],
    'reactive': [('s', 'توان ظاهری', 'Apparent power', 'VA', '')],
    'pf': [('q', 'توان راکتیو', 'Reactive power', 'var', '')],
    'drop_dc': [('vn', 'ولتاژ نامی', 'Nominal voltage', 'V', ''),
                ('r', 'مقاومت هادی', 'Conductor resistance', 'Ω/km', '')],
    'drop_1p': [('rho', 'مقاومت ویژه', 'Resistivity', 'Ω·mm²/m', ''),
                ('area', 'سطح مقطع', 'Area', 'mm²', ''),
                ('vn', 'ولتاژ نامی', 'Nominal voltage', 'V', '')],
    'drop_3p': [('rho', 'مقاومت ویژه', 'Resistivity', 'Ω·mm²/m', ''),
                ('area', 'سطح مقطع', 'Area', 'mm²', ''),
                ('vn', 'ولتاژ نامی', 'Nominal voltage', 'V', '')],
    'resistance': [('sigma', 'هدایت ویژه', 'Conductivity', 'MS/m', ''),
                   ('rkm', 'مقاومت هادی', 'Resistance per km', 'Ω/km', '')],
    'area': [('rkm', 'مقاومت هادی', 'Resistance per km', 'Ω/km', ''),
             ('sigma', 'هدایت ویژه', 'Conductivity', 'MS/m', ''),
             ('d', 'قطر هادی', 'Conductor diameter', 'mm', '')],
    'copper_loss': [('ploss', 'تلفات توان', 'Loss power', 'W', '')],
    'efficiency': [('loss', 'تلفات', 'Losses', 'W', '')],
    'turns': [('n2', 'دور ثانویه', 'Secondary turns', 'turn', '')],
    'tr_current': [('skva', 'توان نامی', 'Rated power', 'kVA', '')],
    'tr3_current': [('skva', 'توان نامی', 'Rated power', 'kVA', '')],
    'impedance': [('z', 'امپدانس', 'Impedance', 'Ω', ''),
                  ('sn', 'توان نامی', 'Rated power', 'kVA', '')],
    'tr_eff': [('pin', 'توان ورودی', 'Input power', 'W', '')],
    'tr_load': [('v', 'ولتاژ', 'Voltage', 'V', ''),
                ('i', 'جریان', 'Current', 'A', '')],
    'tr_short': [('v', 'ولتاژ', 'Voltage', 'V', ''),
                 ('zohm', 'امپدانس اهمی', 'Ohmic impedance', 'Ω', '')],
    'xc': [('omega', 'فرکانس زاویه‌ای', 'Angular frequency', 'rad/s', ''),
           ('v', 'ولتاژ', 'Voltage', 'V', ''), ('i', 'جریان', 'Current', 'A', '')],
    'xl': [('omega', 'فرکانس زاویه‌ای', 'Angular frequency', 'rad/s', ''),
           ('v', 'ولتاژ', 'Voltage', 'V', ''), ('i', 'جریان', 'Current', 'A', '')],
    'rlc': [('v', 'ولتاژ', 'Voltage', 'V', ''), ('i', 'جریان', 'Current', 'A', '')],
    'resonance': [('omega', 'فرکانس زاویه‌ای تشدید', 'Resonant angular frequency', 'rad/s', ''),
                  ('tp', 'دوره تشدید', 'Resonant period', 's', '')],
    'capacitance': [('e', 'انرژی', 'Energy', 'J', '')],
    'ind_energy': [('e', 'انرژی', 'Energy', 'J', '')],
    'cap_energy': [('e', 'انرژی', 'Energy', 'J', '')],
    'surge': [('e', 'انرژی', 'Energy', 'J', '')],
    'motor_in': [('s', 'توان ظاهری', 'Apparent power', 'VA', '')],
    'motor_current': [('hp', 'توان خروجی', 'Output power', 'HP', '')],
    'slip': [('f', 'فرکانس', 'Frequency', 'Hz', ''), ('p', 'تعداد قطب', 'Poles', '', '')],
    'sync_speed': [('sl', 'لغزش', 'Slip', '%', '')],
    'torque': [('pw', 'توان مکانیکی', 'Mechanical power', 'W', '')],
    'motor_eff': [('loss', 'تلفات', 'Losses', 'W', '')],
    'generator': [('s', 'توان ظاهری', 'Apparent power', 'VA', '')],
    'gen_kva': [('p', 'توان اکتیو', 'Active power', 'kW', ''), ('pf', 'ضریب توان', 'Power factor', '', '')],
    'battery': [('wh', 'انرژی', 'Energy', 'Wh', ''), ('vb', 'ولتاژ باتری', 'Battery voltage', 'V', ''),
                ('dod', 'عمق تخلیه', 'Depth of discharge', '%', '')],
    'runtime': [('dod', 'عمق تخلیه مجاز', 'Allowed depth of discharge', '%', '')],
    'led': [('nled', 'تعداد LED سری', 'LEDs in series', '', '')],
    'divider': [('vout', 'ولتاژ خروجی', 'Output voltage', 'V', '')],
    'current_div': [('i1', 'جریان شاخه ۱', 'Branch 1 current', 'A', '')],
    'period': [('omega', 'فرکانس زاویه‌ای', 'Angular frequency', 'rad/s', '')],
    'omega': [('tp', 'دوره تناوب', 'Period', 's', '')],
    'rms': [('vp', 'ولتاژ پیک', 'Peak voltage', 'V', '')],
    'irms': [('ip', 'جریان پیک', 'Peak current', 'A', '')],
    'line_phase': [('vl', 'ولتاژ خط', 'Line voltage', 'V', '')],
    'delta_current': [('il', 'جریان خط', 'Line current', 'A', '')],
    'fault_level': [('z', 'امپدانس', 'Impedance', 'Ω', '')],
    'short_current': [('z', 'امپدانس', 'Impedance', 'Ω', '')],
    'pu': [('zpu', 'امپدانس پریونیت', 'Per-unit impedance', 'pu', '')],
    'zbase': [('zb', 'امپدانس مبنا', 'Base impedance', 'Ω', '')],
    'ibase': [('zb', 'امپدانس مبنا', 'Base impedance', 'Ω', '')],
    'stress': [('e', 'تنش مجاز', 'Allowed stress', 'V/mm', '')],
    'field': [('e', 'شدت میدان', 'Field strength', 'V/m', '')],
    'line_current': [('s', 'توان ظاهری', 'Apparent power', 'MVA', '')],
    'line_power': [('s', 'توان ظاهری', 'Apparent power', 'MVA', '')],
    'line_loss': [('ploss', 'تلفات خط', 'Line loss', 'W', '')],
    'line_eff': [('loss', 'تلفات خط', 'Line loss', 'MW', '')],
    'triangle': [('s', 'توان ظاهری', 'Apparent power', 'kVA', '')],
    'phase': [('q', 'توان راکتیو', 'Reactive power', 'kvar', '')],
    'load_factor': [('energy', 'انرژی مصرفی', 'Energy consumed', 'kWh', ''),
                    ('hours', 'بازه زمانی', 'Period', 'h', '')],
    'demand': [('df', 'ضریب تقاضا', 'Demand factor', '%', '')],
    'diversity': [('df', 'ضریب همزمانی', 'Diversity factor', '', '')],
    'utilization': [('uf', 'ضریب بهره‌برداری', 'Utilization factor', '%', '')],
    'ct': [('ctr', 'نسبت CT', 'CT ratio', '', '')],
    'vt': [('vtr', 'نسبت VT', 'VT ratio', '', '')],
    'busbar': [('J', 'چگالی جریان', 'Current density', 'A/mm²', '')],
    'bus_drop': [('rho', 'مقاومت ویژه', 'Resistivity', 'Ω·mm²/m', ''),
                 ('length', 'طول شینه', 'Busbar length', 'm', ''),
                 ('area', 'سطح مقطع', 'Area', 'mm²', '')],
    'series': [('req', 'مقاومت معادل', 'Equivalent resistance', 'Ω', '')],
    'parallel': [('req', 'مقاومت معادل', 'Equivalent resistance', 'Ω', '')],
    'dc_converter': [('pout', 'توان خروجی', 'Output power', 'W', '')],
    'rectifier': [('vp', 'ولتاژ پیک', 'Peak voltage', 'V', '')],
    'receiving': [('pct', 'درصد افت', 'Voltage drop percent', '%', '')],
    'sending': [('pct', 'درصد افت', 'Voltage drop percent', '%', '')],
    'cost': [('energy', 'انرژی', 'Energy', 'kWh', '')],
}

# Alternative relations: (out label fa, out label en, unit, expression, display formula)
SPECS = {
    'ohm': [
        (('توان', 'Power'), 'W', 'i**2*r', 'P = I²·R'),
        (('توان', 'Power'), 'W', 'v**2/r', 'P = V²/R'),
    ],
    'dc_power': [
        (('توان', 'Power'), 'W', 'i**2*r', 'P = I²·R'),
        (('توان', 'Power'), 'W', 'v**2/r', 'P = V²/R'),
    ],
    'ac_single': [
        (('توان اکتیو', 'Active power'), 'W', 's*pf', 'P = S·cosφ'),
        (('توان ظاهری', 'Apparent power'), 'VA', 'v*i', 'S = V·I'),
        (('ضریب توان', 'Power factor'), '', 'p/s', 'cosφ = P/S'),
        (('جریان', 'Current'), 'A', 's/v', 'I = S/V'),
    ],
    'ac_three': [
        (('توان اکتیو', 'Active power'), 'W', 's*pf', 'P = S·cosφ'),
        (('توان ظاهری', 'Apparent power'), 'VA', 'SQRT3*v*i', 'S = √3·V·I'),
        (('ضریب توان', 'Power factor'), '', 'p/s', 'cosφ = P/S'),
        (('جریان خط', 'Line current'), 'A', 's/(SQRT3*v)', 'I = S/(√3·V)'),
    ],
    'reactive': [
        (('توان راکتیو', 'Reactive power'), 'var', 'sqrt(s**2-p**2)', 'Q = √(S² − P²)'),
    ],
    'pf': [
        (('ضریب توان', 'Power factor'), '', 'p/sqrt(p**2+q**2)', 'cosφ = P/√(P² + Q²)'),
    ],
    'drop_dc': [
        (('افت ولتاژ', 'Voltage drop'), 'V', '2*length/1000*i*r', 'ΔV = 2·(L/1000)·I·R'),
        (('درصد افت ولتاژ', 'Voltage drop'), '%', '2*length*i*rho/area/vn*100', 'ΔV% = ΔV / Vn × 100'),
        (('مقاومت هادی', 'Conductor resistance'), 'Ω/km', 'rho*1000/area', 'R = ρ·1000 / A'),
    ],
    'drop_1p': [
        (('افت ولتاژ', 'Voltage drop'), 'V', '2*(length/1000)*i*((rho*1000/area)*pf+x*sqrt(1-pf**2))',
         'ΔV = 2·(L/1000)·I·(R·cosφ + X·sinφ),  R = ρ·1000/A'),
        (('مقاومت هادی', 'Conductor resistance'), 'Ω/km', 'rho*1000/area', 'R = ρ·1000 / A'),
        (('درصد افت ولتاژ', 'Voltage drop'), '%', '2*(length/1000)*i*(r*pf+x*sqrt(1-pf**2))/vn*100',
         'ΔV% = ΔV / Vn × 100'),
    ],
    'drop_3p': [
        (('افت ولتاژ', 'Voltage drop'), 'V', 'SQRT3*(length/1000)*i*((rho*1000/area)*pf+x*sqrt(1-pf**2))',
         'ΔV = √3·(L/1000)·I·(R·cosφ + X·sinφ),  R = ρ·1000/A'),
        (('مقاومت هادی', 'Conductor resistance'), 'Ω/km', 'rho*1000/area', 'R = ρ·1000 / A'),
        (('درصد افت ولتاژ', 'Voltage drop'), '%', 'SQRT3*(length/1000)*i*(r*pf+x*sqrt(1-pf**2))/vn*100',
         'ΔV% = ΔV / Vn × 100'),
    ],
    'resistance': [
        (('مقاومت', 'Resistance'), 'Ω', 'length/(sigma*area)', 'R = L / (σ·A)'),
        (('مقاومت', 'Resistance'), 'Ω', 'rkm*length/1000', 'R = R_km · L / 1000'),
    ],
    'area': [
        (('سطح مقطع', 'Area'), 'mm²', 'rho*1000/rkm', 'A = ρ·1000 / R_km'),
        (('سطح مقطع', 'Area'), 'mm²', 'length/(sigma*r)', 'A = L / (σ·R)'),
        (('سطح مقطع', 'Area'), 'mm²', 'PI*d**2/4', 'A = π·d² / 4'),
    ],
    'copper_loss': [
        (('جریان', 'Current'), 'A', 'sqrt(ploss/r)', 'I = √(P_cu / R)'),
    ],
    'efficiency': [
        (('راندمان', 'Efficiency'), '%', 'out/(out+loss)*100', 'η = Pout / (Pout + losses) × 100'),
    ],
    'turns': [
        (('دور اولیه', 'Primary turns'), 'turn', 'n2*v1/v2', 'N1 = N2 · V1 / V2'),
    ],
    'tr_current': [
        (('جریان ثانویه', 'Secondary current'), 'A', 'skva*1000/v', 'I2 = S(kVA)·1000 / V2'),
    ],
    'tr3_current': [
        (('جریان خط', 'Line current'), 'A', 'skva*1000/(SQRT3*v)', 'I = S(kVA)·1000 / (√3·V)'),
    ],
    'regulation': [
        (('رگولاسیون (نسبت به بی‌باری)', 'Regulation (no-load based)'), '%', '(vnl-vfl)/vnl*100',
         'ΔV% = (Vnl − Vfl) / Vnl × 100'),
    ],
    'impedance': [
        (('امپدانس', 'Impedance'), '%', 'z*sn*1000/vr**2*100', 'Z% = Z·S / V² × 100'),
    ],
    'tr_eff': [
        (('راندمان', 'Efficiency'), '%', 'out/pin*100', 'η = Pout / Pin × 100'),
    ],
    'tr_load': [
        (('بار مصرفی', 'Load'), 'kVA', 'SQRT3*v*i/1000', 'S = √3·V·I / 1000'),
    ],
    'tr_short': [
        (('جریان اتصال کوتاه', 'Short-circuit current'), 'A', 'v/(SQRT3*zohm)', 'Isc = V / (√3·Z)'),
    ],
    'xc': [
        (('راکتانس خازنی', 'Capacitive reactance'), 'Ω', '1/(omega*c)', 'Xc = 1 / (ω·C)'),
        (('راکتانس خازنی', 'Capacitive reactance'), 'Ω', 'v/i', 'Xc = V / I'),
    ],
    'xl': [
        (('راکتانس سلفی', 'Inductive reactance'), 'Ω', 'omega*l', 'Xl = ω·L'),
        (('راکتانس سلفی', 'Inductive reactance'), 'Ω', 'v/i', 'Xl = V / I'),
    ],
    'rlc': [
        (('امپدانس', '|Z|'), 'Ω', 'v/i', '|Z| = V / I'),
        (('زاویه فاز', 'Phase angle'), '°', 'degrees(atan((xl-xc)/r))', 'φ = atan((XL − XC) / R)'),
    ],
    'resonance': [
        (('فرکانس تشدید', 'Resonant frequency'), 'Hz', 'omega/(2*PI)', 'f0 = ω0 / (2π)'),
        (('فرکانس تشدید', 'Resonant frequency'), 'Hz', '1/tp', 'f0 = 1 / T'),
    ],
    'capacitor': [
        (('توان خازنی', 'Capacitor power'), 'kvar', 'p*(tan(acos(pf1))-tan(acos(pf2)))/1000',
         'Qc = P·(tanφ1 − tanφ2) / 1000'),
    ],
    'pfc': [
        (('توان خازنی', 'Capacitor power'), 'kvar', 'p*(tan(acos(pf1))-tan(acos(pf2)))/1000',
         'Qc = P·(tanφ1 − tanφ2) / 1000'),
    ],
    'capacitance': [
        (('ظرفیت', 'Capacitance'), 'F', '2*e/v**2', 'C = 2E / V²'),
    ],
    'ind_energy': [
        (('اندوکتانس', 'Inductance'), 'H', '2*e/i**2', 'L = 2E / I²'),
    ],
    'cap_energy': [
        (('ظرفیت', 'Capacitance'), 'F', '2*e/v**2', 'C = 2E / V²'),
        (('ولتاژ', 'Voltage'), 'V', 'sqrt(2*e/c)', 'V = √(2E / C)'),
    ],
    'motor_in': [
        (('توان ورودی', 'Input power'), 'W', 's*pf', 'Pin = S·cosφ'),
        (('توان ظاهری', 'Apparent power'), 'VA', 'SQRT3*v*i', 'S = √3·V·I'),
    ],
    'motor_out': [
        (('توان خروجی', 'Output power'), 'HP', 'pin*eta/100/745.7', 'Pout(HP) = Pin·η / 745.7'),
    ],
    'motor_current': [
        (('جریان موتور', 'Motor current'), 'A', 'hp*745.7/(SQRT3*v*eta/100*pf)',
         'I = Pout(HP)·745.7 / (√3·V·η·cosφ)'),
    ],
    'slip': [
        (('لغزش', 'Slip'), '%', '(120*f/p-nr)/(120*f/p)*100', 's = (ns − nr) / ns × 100,  ns = 120f/P'),
    ],
    'sync_speed': [
        (('سرعت روتور', 'Rotor speed'), 'rpm', '120*f/p*(1-sl/100)', 'nr = ns·(1 − s)'),
    ],
    'torque': [
        (('گشتاور', 'Torque'), 'N·m', 'pw/(2*PI*n/60)', 'T = P / ω,  ω = 2πn / 60'),
    ],
    'motor_eff': [
        (('راندمان', 'Efficiency'), '%', 'out/(out+loss)*100', 'η = Pout / (Pout + losses) × 100'),
    ],
    'generator': [
        (('توان ظاهری', 'Apparent power'), 'VA', 'SQRT3*v*i', 'S = √3·V·I'),
        (('توان اکتیو', 'Active power'), 'W', 's*pf', 'P = S·cosφ'),
    ],
    'gen_kva': [
        (('ظرفیت', 'Capacity'), 'kVA', 'p/pf', 'S = P / cosφ'),
    ],
    'battery': [
        (('ظرفیت', 'Capacity'), 'Ah', 'wh/vb', 'Ah = Wh / V'),
        (('ظرفیت قابل استفاده', 'Usable capacity'), 'Ah', 'ah*dod/100', 'Ah_usable = Ah · DoD'),
    ],
    'runtime': [
        (('زمان پشتیبانی', 'Runtime'), 'h', 'ah*dod/100/i', 't = Ah · DoD / I'),
    ],
    'led': [
        (('مقاومت سری', 'Series resistance'), 'Ω', '(vs-nled*vf)/i', 'R = (Vs − N·Vf) / I'),
    ],
    'divider': [
        (('ولتاژ ورودی', 'Input voltage'), 'V', 'vout*(r1+r2)/r2', 'Vin = Vout · (R1 + R2) / R2'),
        (('مقاومت R1', 'Resistor R1'), 'Ω', 'r2*(vin/vout-1)', 'R1 = R2 · (Vin / Vout − 1)'),
    ],
    'current_div': [
        (('جریان شاخه ۲', 'Branch 2 current'), 'A', 'it-i1', 'I2 = It − I1'),
    ],
    'rc': [
        (('فرکانس قطع', 'Cutoff frequency'), 'Hz', '1/(2*PI*r*c)', 'fc = 1 / (2π·R·C)'),
    ],
    'rl': [
        (('فرکانس قطع', 'Cutoff frequency'), 'Hz', 'r/(2*PI*l)', 'fc = R / (2π·L)'),
    ],
    'period': [
        (('دوره تناوب', 'Period'), 's', '2*PI/omega', 'T = 2π / ω'),
    ],
    'omega': [
        (('فرکانس زاویه‌ای', 'Angular frequency'), 'rad/s', '2*PI/tp', 'ω = 2π / T'),
    ],
    'rms': [
        (('ولتاژ مؤثر', 'RMS voltage'), 'V', 'vp/sqrt(2)', 'Vrms = Vp / √2'),
    ],
    'irms': [
        (('جریان مؤثر', 'RMS current'), 'A', 'ip/sqrt(2)', 'Irms = Ip / √2'),
    ],
    'line_phase': [
        (('ولتاژ فاز', 'Phase voltage'), 'V', 'vl/SQRT3', 'Vph = VL / √3'),
    ],
    'delta_current': [
        (('جریان فاز', 'Phase current'), 'A', 'il/SQRT3', 'Iph = IL / √3'),
    ],
    'fault_level': [
        (('سطح اتصال کوتاه', 'Fault level'), 'MVA', 'v**2/z', 'Ssc = V² / Z'),
    ],
    'short_current': [
        (('جریان اتصال کوتاه', 'Short-circuit current'), 'kA', 'v/(SQRT3*z)', 'Ik = V / (√3·Z)'),
    ],
    'pu': [
        (('امپدانس واقعی', 'Actual impedance'), 'Ω', 'zpu*zb', 'Z = Zpu · Zb'),
    ],
    'zbase': [
        (('توان مبنا', 'Base power'), 'MVA', 'v**2/zb', 'S = V² / Zb'),
    ],
    'ibase': [
        (('جریان مبنا', 'Base current'), 'kA', 'v/(SQRT3*zb)', 'Ibase = V / (√3·Zb)'),
    ],
    'stress': [
        (('ولتاژ', 'Voltage'), 'V', 'e*d', 'V = E · d'),
    ],
    'field': [
        (('اختلاف پتانسیل', 'Potential difference'), 'V', 'e*d', 'V = E · d'),
    ],
    'line_current': [
        (('جریان خط', 'Line current'), 'A', 's*1e6/(SQRT3*v*1000)', 'I = S·10⁶ / (√3·V·10³)'),
    ],
    'line_power': [
        (('توان اکتیو', 'Active power'), 'MW', 's*pf', 'P = S·cosφ'),
    ],
    'line_loss': [
        (('جریان فاز', 'Phase current'), 'A', 'sqrt(ploss/(3*r))', 'I = √(Ploss / (3R))'),
    ],
    'line_eff': [
        (('راندمان خط', 'Line efficiency'), '%', 'out/(out+loss)*100', 'η = Pout / (Pout + Ploss) × 100'),
    ],
    'triangle': [
        (('توان راکتیو', 'Reactive power'), 'kvar', 'sqrt(s**2-p**2)', 'Q = √(S² − P²)'),
        (('ضریب توان', 'Power factor'), '', 'p/s', 'cosφ = P / S'),
    ],
    'phase': [
        (('زاویه فاز', 'Phase angle'), '°', 'degrees(atan(q/p))', 'φ = atan(Q / P)'),
    ],
    'load_factor': [
        (('ضریب بار', 'Load factor'), '%', 'energy/(max*hours)*100', 'LF = E / (Pmax · T) × 100'),
    ],
    'demand': [
        (('حداکثر تقاضا', 'Maximum demand'), 'kW', 'df*installed/100', 'Dmax = DF · P_inst / 100'),
    ],
    'diversity': [
        (('حداکثر همزمان', 'Coincident demand'), 'kW', 'sum/df', 'Pc = ΣPi / DF'),
    ],
    'utilization': [
        (('ظرفیت نامی', 'Rated capacity'), 'kW', 'max/(uf/100)', 'P = Dmax / UF'),
    ],
    'freq_dev': [
        (('انحراف فرکانس', 'Frequency deviation'), '%', '(f-fn)/fn*100', 'Δf% = (f − fn) / fn × 100'),
    ],
    'ct': [
        (('جریان اولیه', 'Primary current'), 'A', 'ctr*isec', 'Ip = CTR · Is'),
    ],
    'vt': [
        (('ولتاژ اولیه', 'Primary voltage'), 'V', 'vtr*vs', 'Vp = VTR · Vs'),
    ],
    'busbar': [
        (('جریان', 'Current'), 'A', 'J*area', 'I = J · A'),
    ],
    'bus_drop': [
        (('افت ولتاژ شینه', 'Busbar voltage drop'), 'V', 'i*rho*length/area', 'ΔV = I · ρ · L / A'),
    ],
    'series': [
        (('مقاومت دوم', 'Resistance 2'), 'Ω', 'req-r1', 'R2 = Req − R1'),
    ],
    'parallel': [
        (('مقاومت دوم', 'Resistance 2'), 'Ω', 'r1*req/(r1-req)', 'R2 = R1 · Req / (R1 − Req)'),
    ],
    'dc_converter': [
        (('جریان ورودی', 'Input current'), 'A', 'pout/(vin*eta/100)', 'Iin = Pout / (Vin · η)'),
    ],
    'rectifier': [
        (('ولتاژ متوسط (از پیک، تمام‌موج)', 'Average DC (full-wave, from peak)'), 'V', '2*vp/PI',
         'Vdc = 2·Vp / π'),
        (('ولتاژ متوسط (نیم‌موج)', 'Average DC (half-wave)'), 'V', '0.45*vac', 'Vdc ≈ 0.45·Vac'),
    ],
    'surge': [
        (('ظرفیت', 'Capacitance'), 'F', '2*e/v**2', 'C = 2E / V²'),
    ],
    'receiving': [
        (('ولتاژ دریافتی', 'Receiving voltage'), 'V', 'vs*(1-pct/100)', 'Vr = Vs · (1 − ΔV% / 100)'),
    ],
    'sending': [
        (('ولتاژ ارسالی', 'Sending voltage'), 'V', 'vr*(1+pct/100)', 'Vs = Vr · (1 + ΔV% / 100)'),
    ],
    'cost': [
        (('هزینه', 'Cost'), 'واحد پول', 'energy*tariff', 'Cost = E · tariff'),
    ],
}


# ---------------------------------------------------------------- building

def _build():
    out = {}
    for model, specs in SPECS.items():
        base_fields = {f[0] for f in FIELDS.get(model, [])}
        aux_keys = {a[0] for a in AUX.get(model, [])}
        if base_fields & aux_keys:
            raise ValueError(f"{model}: aux inputs clash with primary inputs")
        allowed = base_fields | aux_keys
        items = []
        for n, (label, unit, expr, shown) in enumerate(specs, 1):
            tree = _parse(expr)
            names = sorted(_names(tree))
            unknown = [x for x in names if x not in allowed]
            if unknown:
                raise ValueError(f"{model}: unknown inputs {unknown} in '{expr}'")
            items.append({
                'id': f'{model}#{n}', 'model': model,
                'out_fa': label[0], 'out_en': label[1], 'unit': unit,
                'expr': expr, 'shown': shown, 'inputs': names,
            })
        out[model] = items
    return out


VARIANTS = _build()


def variants_for(model_key):
    """Alternative relations defined for a model (empty list when none)."""
    return VARIANTS.get(model_key, [])


def input_fields(model_key):
    """Primary fields followed by optional alternative-only inputs."""
    return list(FIELDS.get(model_key, [])) + list(AUX.get(model_key, []))


def field_label(model_key, key, fa=True):
    for item in input_fields(model_key):
        if item[0] == key:
            return item[1] if fa else item[2], item[3]
    return key, ''


def missing_inputs(variant, values):
    """Input keys of a relation that the user has not entered yet."""
    return [k for k in variant['inputs'] if str(values.get(k, '')).strip() == '']


def evaluate(variant, values):
    """Evaluate one relation. ``values`` maps input key -> text. Raises ValueError."""
    missing = missing_inputs(variant, values)
    if missing:
        raise ValueError('missing: ' + ', '.join(missing))
    env = {}
    for k in variant['inputs']:
        x = float(values[k])
        if not math.isfinite(x):
            raise ValueError("Inputs must be finite numbers")
        env[k] = x
    result = _eval(_parse(variant['expr']), env)
    if isinstance(result, complex) or not math.isfinite(float(result)):
        raise ValueError("Result is outside the valid numeric range")
    return {
        'value': float(result),
        'formula': variant['shown'],
        'substituted': _substituted_text(variant['expr'], env) + ' = ' + f'{float(result):.6g}',
        'out_fa': variant['out_fa'],
        'out_en': variant['out_en'],
        'unit': variant['unit'],
        'inputs': env,
    }
