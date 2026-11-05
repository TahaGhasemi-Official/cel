"""Deterministic, offline electrical engineering calculators. SI units unless stated."""
import math

from app.modules.extended import EXT_FIELDS, EXT_CALC

SQRT3 = math.sqrt(3.0)
PI = math.pi

# Field tuples: (key, label-fa, label-en, unit, default)
FIELDS = {
'ohm':[('v','ولتاژ','Voltage','V','12'),('i','جریان','Current','A','2'),('r','مقاومت','Resistance','Ω','6')],
'dc_power':[('v','ولتاژ','Voltage','V','12'),('i','جریان','Current','A','2'),('p','توان خروجی مجهول','Power (optional unknown)','W','')],
'ac_single':[('v','ولتاژ مؤثر','RMS voltage','V','230'),('i','جریان','Current','A','5'),('pf','ضریب توان','Power factor','cosφ','0.9'),('p','توان اکتیو (اختیاری)','Active power (optional)','W','')],
'ac_three':[('v','ولتاژ خط','Line voltage','V','400'),('i','جریان خط','Line current','A','10'),('pf','ضریب توان','Power factor','cosφ','0.85'),('p','توان اکتیو (اختیاری)','Active power (optional)','W','')],
'apparent':[('v','ولتاژ خط/ترمینال','Voltage','V','400'),('i','جریان','Current','A','10'),('three','سه‌فاز؟ 1 بله، 0 خیر','Three phase? 1 yes, 0 no','', '1')],
'reactive':[('p','توان اکتیو','Active power','W','1000'),('pf','ضریب توان','Power factor','cosφ','0.8')],
'pf':[('p','توان اکتیو','Active power','W','1000'),('s','توان ظاهری','Apparent power','VA','1250')],
'energy':[('p','توان','Power','W','1000'),('t','زمان','Time','h','5'),('e','انرژی (اختیاری)','Energy (optional)','Wh','')],
'drop_dc':[('length','طول یک‌طرفه','One-way length','m','20'),('i','جریان','Current','A','10'),('rho','مقاومت ویژه','Resistivity','Ω·mm²/m','0.0175'),('area','سطح مقطع','Area','mm²','2.5')],
'drop_1p':[('length','طول یک‌طرفه','One-way length','m','30'),('i','جریان','Current','A','10'),('r','R هادی در واحد طول','Conductor R per length','Ω/km','7.41'),('x','X در واحد طول','X per length','Ω/km','0.08'),('pf','ضریب توان','Power factor','cosφ','0.9')],
'drop_3p':[('length','طول مسیر','Route length','m','50'),('i','جریان خط','Line current','A','20'),('r','R در واحد طول','R per length','Ω/km','0.8'),('x','X در واحد طول','X per length','Ω/km','0.08'),('pf','ضریب توان','Power factor','cosφ','0.85')],
'resistance':[('rho','مقاومت ویژه','Resistivity','Ω·mm²/m','0.0175'),('length','طول','Length','m','100'),('area','سطح مقطع','Area','mm²','4'),('r','مقاومت (اختیاری)','Resistance (optional)','Ω','')],
'area':[('rho','مقاومت ویژه','Resistivity','Ω·mm²/m','0.0175'),('length','طول','Length','m','50'),('r','مقاومت مجاز','Allowed resistance','Ω','0.2'),('area','سطح مقطع (اختیاری)','Area (optional)','mm²','')],
'copper_loss':[('i','جریان','Current','A','10'),('r','مقاومت','Resistance','Ω','0.5')],
'efficiency':[('out','توان خروجی','Output power','W','900'),('in','توان ورودی','Input power','W','1000')],
'turns':[('v1','ولتاژ اولیه','Primary voltage','V','230'),('v2','ولتاژ ثانویه','Secondary voltage','V','24'),('n1','دور اولیه (اختیاری)','Primary turns (optional)','turn','1000')],
'tr_current':[('s','توان نامی','Rated apparent power','VA','1000'),('v','ولتاژ ثانویه','Secondary voltage','V','24'),('i','جریان ثانویه (اختیاری)','Secondary current (optional)','A','')],
'tr3_current':[('s','توان نامی سه‌فاز','Three-phase rating','VA','100000'),('v','ولتاژ خط','Line voltage','V','400'),('i','جریان خط (اختیاری)','Line current (optional)','A','')],
'regulation':[('vnl','ولتاژ بی‌باری','No-load voltage','V','24'),('vfl','ولتاژ بار کامل','Full-load voltage','V','23')],
'impedance':[('vsc','ولتاژ اتصال کوتاه','Short-circuit voltage','V','20'),('vr','ولتاژ نامی','Rated voltage','V','400')],
'tr_loss':[('i','جریان','Current','A','10'),('r','مقاومت معادل','Equivalent resistance','Ω','0.2')],
'tr_eff':[('out','توان خروجی','Output power','W','950'),('loss','مجموع تلفات','Total losses','W','50')],
'tr_load':[('load','بار مصرفی','Load','kVA','50'),('rated','توان نامی ترانس','Transformer rating','kVA','100')],
'tr_short':[('i','جریان نامی','Rated current','A','144'),('z','امپدانس درصدی','Impedance','%','6')],
'xc':[('f','فرکانس','Frequency','Hz','50'),('c','ظرفیت','Capacitance','F','0.0001')],
'xl':[('f','فرکانس','Frequency','Hz','50'),('l','اندوکتانس','Inductance','H','0.1')],
'rlc':[('r','مقاومت','Resistance','Ω','10'),('xl','راکتانس سلفی','Inductive reactance','Ω','20'),('xc','راکتانس خازنی','Capacitive reactance','Ω','5')],
'resonance':[('l','اندوکتانس','Inductance','H','0.1'),('c','ظرفیت','Capacitance','F','0.0001')],
'capacitor':[('p','توان اکتیو','Active power','W','10000'),('pf1','ضریب توان اولیه','Initial power factor','', '0.75'),('pf2','ضریب توان هدف','Target power factor','', '0.95'),('v','ولتاژ','Voltage','V','400'),('f','فرکانس','Frequency','Hz','50')],
'capacitance':[('q','بار الکتریکی','Charge','C','0.01'),('v','ولتاژ','Voltage','V','100')],
'ind_energy':[('l','اندوکتانس','Inductance','H','0.5'),('i','جریان','Current','A','4')],
'cap_energy':[('c','ظرفیت','Capacitance','F','0.001'),('v','ولتاژ','Voltage','V','100')],
'motor_in':[('v','ولتاژ خط','Line voltage','V','400'),('i','جریان','Current','A','10'),('pf','ضریب توان','Power factor','', '0.85')],
'motor_out':[('pin','توان ورودی','Input power','W','5000'),('eta','راندمان','Efficiency','%', '90'),('pout','توان خروجی (اختیاری)','Output power (optional)','W','')],
'motor_current':[('p','توان خروجی موتور','Motor output power','W','7500'),('v','ولتاژ خط','Line voltage','V','400'),('eta','راندمان','Efficiency','%', '90'),('pf','ضریب توان','Power factor','', '0.85')],
'slip':[('ns','سرعت سنکرون','Synchronous speed','rpm','1500'),('nr','سرعت روتور','Rotor speed','rpm','1440')],
'sync_speed':[('f','فرکانس','Frequency','Hz','50'),('p','تعداد قطب','Number of poles','', '4')],
'torque':[('p','توان مکانیکی','Mechanical power','kW','5'),('n','سرعت','Speed','rpm','1450')],
'generator':[('v','ولتاژ خط','Line voltage','V','400'),('i','جریان خط','Line current','A','20'),('pf','ضریب توان','Power factor','', '0.8')],
'gen_kva':[('v','ولتاژ خط','Line voltage','V','400'),('i','جریان خط','Line current','A','20')],
'battery':[('i','جریان','Current','A','2'),('t','زمان','Time','h','5'),('ah','ظرفیت (اختیاری)','Capacity (optional)','Ah','')],
'runtime':[('ah','ظرفیت باتری','Battery capacity','Ah','100'),('i','بار جریان','Load current','A','5'),('hours','زمان پشتیبانی (اختیاری)','Runtime (optional)','h','')],
'led':[('vs','ولتاژ منبع','Supply voltage','V','12'),('vf','افت LED','LED forward voltage','V','2'),('i','جریان هدف','Target current','A','0.02')],
'divider':[('vin','ولتاژ ورودی','Input voltage','V','12'),('r1','مقاومت R1','Resistor R1','Ω','10000'),('r2','مقاومت R2','Resistor R2','Ω','10000')],
'current_div':[('it','جریان کل','Total current','A','2'),('r1','مقاومت شاخه ۱','Branch 1 resistance','Ω','100'),('r2','مقاومت شاخه ۲','Branch 2 resistance','Ω','200')],
'rc':[('r','مقاومت','Resistance','Ω','10000'),('c','ظرفیت','Capacitance','F','0.0001'),('tau','ثابت زمانی (اختیاری)','Time constant (optional)','s','')],
'rl':[('l','اندوکتانس','Inductance','H','0.5'),('r','مقاومت','Resistance','Ω','100'),('tau','ثابت زمانی (اختیاری)','Time constant (optional)','s','')],
'period':[('f','فرکانس','Frequency','Hz','50'),('period','دوره تناوب (اختیاری)','Period (optional)','s','')],
'omega':[('f','فرکانس','Frequency','Hz','50'),('omega','فرکانس زاویه‌ای (اختیاری)','Angular frequency (optional)','rad/s','')],
'rms':[('v','ولتاژ مؤثر','RMS voltage','V','230')],
'irms':[('i','جریان مؤثر','RMS current','A','5')],
'line_phase':[('v','ولتاژ فاز','Phase voltage','V','230')],
'star_current':[('i','جریان فاز','Phase current','A','10')],
'delta_current':[('i','جریان فاز','Phase current','A','10')],
'fault_level':[('v','ولتاژ خط','Line voltage','kV','20'),('i','جریان اتصال کوتاه','Short-circuit current','kA','10')],
'short_current':[('s','قدرت اتصال کوتاه','Short-circuit power','MVA','350'),('v','ولتاژ خط','Line voltage','kV','20')],
'pu':[('z','امپدانس واقعی','Actual impedance','Ω','0.5'),('zb','امپدانس مبنا','Base impedance','Ω','10')],
'zbase':[('v','ولتاژ مبنا خط','Base line voltage','kV','20'),('s','توان مبنا','Base power','MVA','100')],
'ibase':[('s','توان مبنا','Base power','MVA','100'),('v','ولتاژ مبنا خط','Base line voltage','kV','20')],
'stress':[('v','ولتاژ','Voltage','V','10000'),('d','ضخامت عایق','Insulation thickness','mm','5')],
'field':[('v','اختلاف پتانسیل','Potential difference','V','1000'),('d','فاصله','Distance','m','0.1')],
'line_current':[('p','توان اکتیو','Active power','MW','5'),('v','ولتاژ خط','Line voltage','kV','20'),('pf','ضریب توان','Power factor','', '0.9')],
'line_power':[('v','ولتاژ خط','Line voltage','kV','20'),('i','جریان خط','Line current','A','100'),('pf','ضریب توان','Power factor','', '0.9')],
'line_loss':[('i','جریان فاز','Phase current','A','100'),('r','مقاومت هر فاز','Resistance per phase','Ω','0.5')],
'line_eff':[('out','توان دریافتی','Received power','MW','9.5'),('in','توان ارسالی','Sent power','MW','10')],
'triangle':[('p','توان اکتیو','Active power','kW','10'),('q','توان راکتیو','Reactive power','kvar','5')],
'phase':[('p','توان اکتیو','Active power','kW','10'),('s','توان ظاهری','Apparent power','kVA','12')],
'load_factor':[('avg','بار متوسط','Average load','kW','50'),('max','حداکثر بار','Maximum demand','kW','100')],
'demand':[('max','حداکثر تقاضا','Maximum demand','kW','80'),('installed','بار نصب‌شده','Installed load','kW','100')],
'diversity':[('sum','مجموع حداکثر تقاضاها','Sum of individual maximum demands','kW','120'),('coincident','حداکثر تقاضای همزمان','Coincident maximum demand','kW','100')],
'utilization':[('max','حداکثر تقاضا','Maximum demand','kW','80'),('rated','ظرفیت نامی','Rated capacity','kW','100')],
'unbalance':[('v1','ولتاژ فاز ۱','Phase 1 voltage','V','230'),('v2','ولتاژ فاز ۲','Phase 2 voltage','V','225'),('v3','ولتاژ فاز ۳','Phase 3 voltage','V','235')],
'freq_dev':[('f','فرکانس اندازه‌گیری‌شده','Measured frequency','Hz','49.8'),('fn','فرکانس نامی','Nominal frequency','Hz','50')],
'ground':[('v','ولتاژ آزمون','Test voltage','V','25'),('i','جریان آزمون','Test current','A','1')],
'ct':[('ip','جریان اولیه','Primary current','A','400'),('isec','جریان ثانویه','Secondary current','A','5')],
'vt':[('vp','ولتاژ اولیه','Primary voltage','V','20000'),('vs','ولتاژ ثانویه','Secondary voltage','V','100')],
'busbar':[('i','جریان','Current','A','400'),('area','سطح مقطع','Cross-sectional area','mm²','100')],
'series':[('r1','مقاومت اول','Resistance 1','Ω','10'),('r2','مقاومت دوم','Resistance 2','Ω','20')],
'parallel':[('r1','مقاومت اول','Resistance 1','Ω','10'),('r2','مقاومت دوم','Resistance 2','Ω','20')],
'motor_eff':[('out','توان خروجی','Output power','W','4500'),('in','توان ورودی','Input power','W','5000')],
'star_delta':[('idelta','جریان راه‌اندازی مستقیم','DOL starting current','A','60')],
'dc_converter':[('vin','ولتاژ ورودی','Input voltage','V','24'),('iin','جریان ورودی','Input current','A','5'),('eta','راندمان','Efficiency','%', '90')],
'rectifier':[('vac','ولتاژ AC مؤثر','AC RMS voltage','V','230')],
'diode':[('vf','افت مستقیم دیود','Diode forward drop','V','0.7'),('i','جریان','Current','A','1')],
'surge':[('c','ظرفیت','Capacitance','F','0.000001'),('v','ولتاژ','Voltage','V','10000')],
'receiving':[('vs','ولتاژ ارسال','Sending voltage','V','20000'),('drop','افت ولتاژ','Voltage drop','V','500')],
'sending':[('vr','ولتاژ دریافت','Receiving voltage','V','19500'),('drop','افت ولتاژ','Voltage drop','V','500')],
'compensation':[('p','توان اکتیو','Active power','kW','100'),('pf1','ضریب توان اولیه','Initial power factor','', '0.8'),('pf2','ضریب توان هدف','Target power factor','', '0.95')],
'fuse':[('i','جریان','Current','A','10'),('r','مقاومت فیوز','Fuse resistance','Ω','0.01')],
'cost':[('p','توان متوسط','Average power','kW','2'),('t','زمان','Time','h','8'),('tariff','تعرفه هر kWh','Tariff per kWh','currency/kWh','3000')],
}
FIELDS['pfc'] = FIELDS['capacitor']
FIELDS.update(EXT_FIELDS)

# Keys that deliberately return a design/standard warning instead of pretending to size safety-critical equipment.
GUIDANCE = {
'ampacity': 'برای تعیین جریان مجاز کابل باید روش نصب، دمای محیط، تجمع کابل‌ها، جنس عایق و جدول استاندارد/سازنده مشخص باشد. این مدل به‌تنهایی سایز کابل را تأیید نمی‌کند.',
'breaker': 'ظرفیت قطع کلید باید از جریان اتصال کوتاه محتمل در محل، ولتاژ نامی، منحنی و استاندارد تجهیز انتخاب و توسط مهندس مسئول تأیید شود.',
'relay': 'تنظیم رله نیازمند مطالعه اتصال کوتاه، منحنی CT، هماهنگی حفاظتی و زمان‌بندی شبکه است؛ مقدار عمومی قابل اتکا نیست.',
'touch': 'محاسبه ولتاژ تماس نیازمند مدل دقیق شبکه زمین، زمان قطع، مقاومت ویژه خاک و استاندارد ایمنی مربوط است.',
'step': 'محاسبه ولتاژ گام نیازمند مدل دقیق شبکه زمین، زمان قطع، مقاومت ویژه خاک و استاندارد ایمنی مربوط است.',
'clearance': 'فاصله هوایی تابع سطح عایقی نامی، اضافه‌ولتاژ، ارتفاع از سطح دریا و استاندارد طراحی است؛ از این خروجی برای اجرا استفاده نکنید.',
'creepage': 'فاصله خزشی تابع ولتاژ سیستم، درجه آلودگی، جنس عایق و استاندارد مربوط است.',
'corona': 'ارزیابی کرونا به قطر و آرایش هادی، زبری سطح، ارتفاع، فشار و شرایط جوی نیاز دارد.',
'inrush': 'جریان هجومی به طراحی هسته، شار باقیمانده، زاویه وصل و امپدانس منبع وابسته است؛ مقدار واقعی را از سازنده/مطالعه گذرا بگیرید.',
'impulse': 'برای تحلیل موج ضربه‌ای، شکل موج، دامنه، امپدانس موج و مدل تجهیز لازم است.'}


def _num(d, key):
    if key not in d: raise ValueError(f"Missing input: {key}")
    x=float(d[key])
    if not math.isfinite(x): raise ValueError("Inputs must be finite numbers")
    return x

def _positive(x, name):
    if x <= 0: raise ValueError(f"{name} must be greater than zero")
    return x

def _solve_one_unknown(key, data):
    """Solve one blank field only where a validated algebraic inverse is implemented."""
    fields = FIELDS.get(key, [])
    missing = [item[0] for item in fields if str(data.get(item[0], "")).strip() == ""]
    if not missing:
        return data, None
    if len(missing) != 1:
        raise ValueError("Enter all required values, or leave exactly one field blank to solve for it.")
    u = missing[0]
    d = {k: float(v) for k, v in data.items() if str(v).strip() != ""}
    def v(k):
        if k not in d: raise ValueError("Not enough known values to solve this unknown.")
        x=d[k]
        if not math.isfinite(x): raise ValueError("Inputs must be finite numbers")
        return x
    def div(a,b):
        if b == 0: raise ValueError("Cannot solve: denominator is zero.")
        return a/b
    solve = {
      'ohm': {'v':lambda: v('i')*v('r'), 'i':lambda:div(v('v'),v('r')), 'r':lambda:div(v('v'),v('i'))},
      'dc_power': {'v':lambda:div(v('p'),v('i')), 'i':lambda:div(v('p'),v('v')), 'p':lambda:v('v')*v('i')},
      'ac_single': {'v':lambda:div(v('p'),v('i')*v('pf')), 'i':lambda:div(v('p'),v('v')*v('pf')), 'pf':lambda:div(v('p'),v('v')*v('i')), 'p':lambda:v('v')*v('i')*v('pf')},
      'ac_three': {'v':lambda:div(v('p'),SQRT3*v('i')*v('pf')), 'i':lambda:div(v('p'),SQRT3*v('v')*v('pf')), 'pf':lambda:div(v('p'),SQRT3*v('v')*v('i')), 'p':lambda:SQRT3*v('v')*v('i')*v('pf')},
      'energy': {'p':lambda:div(v('e'),v('t')), 't':lambda:div(v('e'),v('p')), 'e':lambda:v('p')*v('t')},
      'resistance': {'rho':lambda:div(v('r')*v('area'),v('length')), 'length':lambda:div(v('r')*v('area'),v('rho')), 'area':lambda:div(v('rho')*v('length'),v('r')), 'r':lambda:div(v('rho')*v('length'),v('area'))},
      'area': {'rho':lambda:div(v('r')*v('area'),v('length')), 'length':lambda:div(v('r')*v('area'),v('rho')), 'r':lambda:div(v('rho')*v('length'),v('area')), 'area':lambda:div(v('rho')*v('length'),v('r'))},
      'tr_current': {'s':lambda:v('i')*v('v'), 'v':lambda:div(v('s'),v('i')), 'i':lambda:div(v('s'),v('v'))},
      'tr3_current': {'s':lambda:SQRT3*v('i')*v('v'), 'v':lambda:div(v('s'),SQRT3*v('i')), 'i':lambda:div(v('s'),SQRT3*v('v'))},
      'motor_out': {'pin':lambda:div(v('pout')*100,v('eta')), 'eta':lambda:100*div(v('pout'),v('pin')), 'pout':lambda:v('pin')*v('eta')/100},
      'battery': {'i':lambda:div(v('ah'),v('t')), 't':lambda:div(v('ah'),v('i')), 'ah':lambda:v('i')*v('t')},
      'runtime': {'ah':lambda:v('hours')*v('i'), 'i':lambda:div(v('ah'),v('hours')), 'hours':lambda:div(v('ah'),v('i'))},
      'period': {'f':lambda:div(1,v('period')), 'period':lambda:div(1,v('f'))},
      'omega': {'f':lambda:div(v('omega'),2*PI), 'omega':lambda:2*PI*v('f')},
      'rc': {'r':lambda:div(v('tau'),v('c')), 'c':lambda:div(v('tau'),v('r')), 'tau':lambda:v('r')*v('c')},
      'rl': {'l':lambda:v('tau')*v('r'), 'r':lambda:div(v('l'),v('tau')), 'tau':lambda:div(v('l'),v('r'))},
    }
    if key not in solve or u not in solve[key]:
        raise ValueError("A reliable inverse formula is not available for this field. Enter all inputs or choose another calculation model.")
    value=float(solve[key][u]())
    if not math.isfinite(value): raise ValueError("Solved value is outside the valid numeric range.")
    d[u]=value
    return d, (u,value)


def calculate(key, d):
    if key in GUIDANCE:
        return {"status":"guidance", "message":GUIDANCE[key]}
    d, solved = _solve_one_unknown(key, d)
    g=lambda k:_num(d,k)
    out={}
    if key in EXT_CALC: out=EXT_CALC[key](g)
    elif key=='ohm':
        v,i,r=g('v'),g('i'),g('r')
        if v==0 and i!=0: out['V']=i*r
        elif i==0 and r!=0: out['I']=v/r
        elif r==0 and i!=0: out['R']=v/i
        else: out.update({'V = I×R (V)':i*r,'I = V/R (A)':v/r if r else float('inf'),'R = V/I (Ω)':v/i if i else float('inf')})
    elif key=='dc_power': out={'P (W)':g('v')*g('i')}
    elif key in ('ac_single','motor_in','generator'): out={'P (W)':g('v')*g('i')*g('pf')}
    elif key=='ac_three': out={'P (W)':SQRT3*g('v')*g('i')*g('pf')}
    elif key=='apparent': out={'S (VA)':g('v')*g('i')*(SQRT3 if g('three') else 1)}
    elif key=='reactive':
        pf=g('pf'); _positive(pf,'Power factor')
        if pf>1: raise ValueError('Power factor must be between 0 and 1')
        out={'Q (var)':g('p')*math.tan(math.acos(pf))}
    elif key=='pf': out={'Power factor':g('p')/_positive(g('s'),'Apparent power')}
    elif key=='energy': out={'Energy (Wh)':g('p')*g('t'),'Energy (kWh)':g('p')*g('t')/1000}
    elif key in ('drop_dc','drop_1p','drop_3p'):
        L,I=g('length'),g('i'); _positive(L,'Length'); _positive(g('area') if key=='drop_dc' else g('r'),'Area/resistance')
        if key=='drop_dc': dv=2*L*I*g('rho')/g('area')
        else:
            phi=math.acos(max(-1,min(1,g('pf')))); factor=2 if key=='drop_1p' else SQRT3
            dv=factor*(L/1000)*I*(g('r')*math.cos(phi)+g('x')*math.sin(phi))
        out={'Voltage drop (V)':dv}
    elif key=='resistance': out={'R (Ω)':g('rho')*g('length')/g('area')}
    elif key=='area': out={'A (mm²)':g('rho')*g('length')/g('r')}
    elif key in ('copper_loss','tr_loss'): out={'Loss (W)':g('i')**2*g('r')}
    elif key in ('efficiency','motor_eff'): out={'Efficiency (%)':100*g('out')/g('in')}
    elif key=='turns': out={'Turns ratio N1/N2':g('v1')/g('v2'),'Secondary turns N2':g('n1')*g('v2')/g('v1')}
    elif key=='tr_current': out={'Secondary current (A)':g('s')/g('v')}
    elif key=='tr3_current': out={'Line current (A)':g('s')/(SQRT3*g('v'))}
    elif key=='regulation': out={'Voltage regulation (%)':100*(g('vnl')-g('vfl'))/g('vfl')}
    elif key=='impedance': out={'Impedance (%)':100*g('vsc')/g('vr')}
    elif key=='tr_eff': out={'Efficiency (%)':100*g('out')/(g('out')+g('loss'))}
    elif key=='tr_load': out={'Loading (%)':100*g('load')/g('rated')}
    elif key=='tr_short': out={'Estimated symmetrical short-circuit current (A)':g('i')*100/g('z')}
    elif key=='xc': out={'Xc (Ω)':1/(2*PI*g('f')*g('c'))}
    elif key=='xl': out={'Xl (Ω)':2*PI*g('f')*g('l')}
    elif key=='rlc': out={'|Z| (Ω)':math.sqrt(g('r')**2+(g('xl')-g('xc'))**2)}
    elif key=='resonance': out={'Resonant frequency (Hz)':1/(2*PI*math.sqrt(g('l')*g('c')))}
    elif key in ('capacitor','pfc'):
        p,pf1,pf2=g('p'),g('pf1'),g('pf2')
        if not (0<pf1<=1 and 0<pf2<=1): raise ValueError('Power factors must be in (0, 1]')
        q=max(0,p*(math.tan(math.acos(pf1))-math.tan(math.acos(pf2))))
        out={'Required compensation (var)':q,'Capacitance 1-phase (F)':q/(2*PI*g('f')*g('v')**2)}
    elif key=='capacitance': out={'C (F)':g('q')/g('v')}
    elif key=='ind_energy': out={'Stored energy (J)':0.5*g('l')*g('i')**2}
    elif key=='cap_energy': out={'Stored energy (J)':0.5*g('c')*g('v')**2}
    elif key=='motor_out': out={'Output power (W)':g('pin')*g('eta')/100}
    elif key=='motor_current': out={'Line current (A)':g('p')/(SQRT3*g('v')*(g('eta')/100)*g('pf'))}
    elif key=='slip': out={'Slip (%)':100*(g('ns')-g('nr'))/g('ns')}
    elif key=='sync_speed': out={'Synchronous speed (rpm)':120*g('f')/g('p')}
    elif key=='torque': out={'Torque (N·m)':9550*g('p')/g('n')}
    elif key=='gen_kva': out={'Apparent power (kVA)':SQRT3*g('v')*g('i')/1000}
    elif key=='battery': out={'Capacity (Ah)':g('i')*g('t')}
    elif key=='runtime': out={'Ideal runtime (h)':g('ah')/g('i')}
    elif key=='led': out={'Series resistance (Ω)':(g('vs')-g('vf'))/g('i'),'Resistor power (W)':(g('vs')-g('vf'))*g('i')}
    elif key=='divider': out={'Output voltage (V)':g('vin')*g('r2')/(g('r1')+g('r2'))}
    elif key=='current_div': out={'Branch 1 current (A)':g('it')*g('r2')/(g('r1')+g('r2')),'Branch 2 current (A)':g('it')*g('r1')/(g('r1')+g('r2'))}
    elif key=='rc': out={'Time constant τ (s)':g('r')*g('c')}
    elif key=='rl': out={'Time constant τ (s)':g('l')/g('r')}
    elif key=='period': out={'Period (s)':1/g('f')}
    elif key=='omega': out={'Angular frequency (rad/s)':2*PI*g('f')}
    elif key=='rms': out={'Peak voltage (V)':math.sqrt(2)*g('v')}
    elif key=='irms': out={'Peak current (A)':math.sqrt(2)*g('i')}
    elif key=='line_phase': out={'Line voltage (V), star':SQRT3*g('v')}
    elif key=='star_current': out={'Line current (A), star':g('i')}
    elif key=='delta_current': out={'Line current (A), delta':SQRT3*g('i')}
    elif key=='fault_level': out={'Short-circuit level (MVA)':SQRT3*g('v')*g('i')}
    elif key=='short_current': out={'Short-circuit current (kA)':g('s')/(SQRT3*g('v'))}
    elif key=='pu': out={'Per-unit impedance':g('z')/_positive(g('zb'),'Base impedance')}
    elif key=='zbase': out={'Base impedance (Ω)':(g('v')**2)/g('s')}
    elif key=='ibase': out={'Base current (A)':g('s')/(SQRT3*g('v'))}
    elif key=='stress': out={'Average electric stress (V/mm)':g('v')/g('d')}
    elif key=='field': out={'Electric field (V/m)':g('v')/g('d')}
    elif key=='line_current': out={'Line current (A)':g('p')*1e6/(SQRT3*g('v')*1e3*g('pf'))}
    elif key=='line_power': out={'Active power (MW)':SQRT3*g('v')*g('i')*g('pf')/1000}
    elif key=='line_loss': out={'Three-phase copper loss (W)':3*g('i')**2*g('r')}
    elif key=='line_eff': out={'Line efficiency (%)':100*g('out')/g('in')}
    elif key=='triangle': out={'Apparent power (kVA)':math.sqrt(g('p')**2+g('q')**2),'Power factor':g('p')/math.sqrt(g('p')**2+g('q')**2)}
    elif key=='phase': out={'Phase angle (degrees)':math.degrees(math.acos(max(-1,min(1,g('p')/g('s')))))}
    elif key=='load_factor': out={'Load factor (%)':100*g('avg')/g('max')}
    elif key=='demand': out={'Demand factor (%)':100*g('max')/g('installed')}
    elif key=='diversity': out={'Diversity factor':g('sum')/g('coincident')}
    elif key=='utilization': out={'Utilization factor (%)':100*g('max')/g('rated')}
    elif key=='unbalance':
        vals=[g('v1'),g('v2'),g('v3')]; avg=sum(vals)/3
        out={'Voltage unbalance (%)':100*max(abs(x-avg) for x in vals)/avg}
    elif key=='freq_dev': out={'Frequency deviation (Hz)':g('f')-g('fn')}
    elif key=='ground': out={'Measured resistance (Ω)':g('v')/g('i')}
    elif key=='ct': out={'CT ratio':g('ip')/g('isec')}
    elif key=='vt': out={'VT ratio':g('vp')/g('vs')}
    elif key=='busbar': out={'Current density (A/mm²)':g('i')/g('area')}
    elif key=='series': out={'Equivalent resistance (Ω)':g('r1')+g('r2')}
    elif key=='parallel': out={'Equivalent resistance (Ω)':1/(1/g('r1')+1/g('r2'))}
    elif key=='star_delta': out={'Approximate star starting current (A)':g('idelta')/3}
    elif key=='dc_converter': out={'Estimated output power (W)':g('vin')*g('iin')*g('eta')/100}
    elif key=='rectifier': out={'Average full-wave DC voltage (V)':0.9*g('vac')}
    elif key=='diode': out={'Diode dissipation (W)':g('vf')*g('i')}
    elif key=='surge': out={'Stored capacitor energy (J)':0.5*g('c')*g('v')**2}
    elif key=='receiving': out={'Approximate receiving voltage (V)':g('vs')-g('drop')}
    elif key=='sending': out={'Approximate sending voltage (V)':g('vr')+g('drop')}
    elif key=='compensation': out={'Required compensation (kvar)':g('p')*(math.tan(math.acos(g('pf1')))-math.tan(math.acos(g('pf2'))))}
    elif key=='fuse': out={'Resistive power dissipation (W)':g('i')**2*g('r')}
    elif key=='cost': out={'Energy (kWh)':g('p')*g('t'),'Estimated cost':g('p')*g('t')*g('tariff')}
    else: raise ValueError('This profile is a reference model and does not yet expose a numerical solver.')
    if any(not math.isfinite(float(v)) for v in out.values()): raise ValueError('Calculation is outside the valid numeric range')
    return {"status":"ok", "results":out, "solved_unknown": solved}
