"""VOLTEX navigation, 100 TG.VL model profiles and extended TG.VX profiles."""

VOLTAGE_GROUPS = [
    {"id":"lv","fa":"برق فشار ضعیف (۰ تا ۱ کیلوولت)","en":"Low Voltage (0–1 kV)","systems":["ac","dc"]},
    {"id":"mv","fa":"برق فشار متوسط (۱ تا ۳۳ کیلوولت)","en":"Medium Voltage (1–33 kV)","systems":["ac"]},
    {"id":"hv","fa":"برق فشار قوی (۳۳ تا ۲۳۰ کیلوولت)","en":"High Voltage (33–230 kV)","systems":["ac"]},
    {"id":"ehv","fa":"برق فشار فوق‌قوی (بیش از ۲۳۰ کیلوولت)","en":"Extra High Voltage (>230 kV)","systems":["ac"]},
]

# Each model is an offline deterministic engineering calculation profile.
_MODEL_ROWS = [
("Ohm's Law","قانون اهم","ohm","V=I×R؛ محاسبه ولتاژ، جریان یا مقاومت"),
("DC Power","توان مدار DC","dc_power","P=V×I"),
("AC Single-phase Power","توان اکتیو تک‌فاز","ac_single","P=V×I×cosφ"),
("AC Three-phase Power","توان اکتیو سه‌فاز","ac_three","P=√3×V×I×cosφ"),
("Apparent Power","توان ظاهری","apparent","S=V×I یا √3×V×I"),
("Reactive Power","توان راکتیو","reactive","Q=P×tanφ"),
("Power Factor","ضریب توان","pf","cosφ=P/S"),
("Energy Consumption","انرژی مصرفی","energy","E=P×t"),
("Cable Voltage Drop DC","افت ولتاژ کابل DC","drop_dc","ΔV=2×L×I×ρ/A"),
("Cable Voltage Drop 1P","افت ولتاژ تک‌فاز","drop_1p","ΔV≈2LI(Rcosφ+Xsinφ)"),
("Cable Voltage Drop 3P","افت ولتاژ سه‌فاز","drop_3p","ΔV≈√3LI(Rcosφ+Xsinφ)"),
("Cable Resistance","مقاومت هادی","resistance","R=ρL/A"),
("Conductor Area","سطح مقطع هادی","area","A=ρL/R"),
("Copper Loss","تلفات مسی","copper_loss","Pcu=I²R"),
("Efficiency","راندمان","efficiency","η=Pout/Pin×100"),
("Transformer Turns Ratio","نسبت تبدیل ترانس","turns","V1/V2=N1/N2"),
("Transformer Secondary Current","جریان ثانویه ترانس","tr_current","I2=S/V2 (تک‌فاز)"),
("Transformer Three-phase Current","جریان ترانس سه‌فاز","tr3_current","I=S/(√3V)"),
("Transformer Regulation","رگولاسیون ترانس","regulation","(Vnl−Vfl)/Vfl×100"),
("Transformer Impedance","امپدانس ترانس","impedance","Z%=Vsc/Vrated×100"),
("Transformer Copper Loss","تلفات مسی ترانس","tr_loss","Pcu=I²R"),
("Transformer Efficiency","راندمان ترانس","tr_eff","Pout/(Pout+losses)×100"),
("Transformer Load","درصد بار ترانس","tr_load","Sload/Srated×100"),
("Transformer Short Circuit","جریان اتصال کوتاه ترانس","tr_short","In×100/Z%"),
("DC Series Circuit","مدار سری DC","series","Req=ΣR"),
("DC Parallel Circuit","مدار موازی DC","parallel","1/Req=Σ(1/R)"),
("Capacitive Reactance","راکتانس خازنی","xc","Xc=1/(2πfC)"),
("Inductive Reactance","راکتانس سلفی","xl","Xl=2πfL"),
("Series RLC Impedance","امپدانس RLC سری","rlc","Z=√(R²+(XL−XC)²)"),
("Resonant Frequency","فرکانس تشدید","resonance","f0=1/(2π√LC)"),
("Capacitor Reactive Power","توان خازنی اصلاح ضریب توان","capacitor","Qc=P(tanφ1−tanφ2)"),
("Capacitance","ظرفیت خازن","capacitance","C=Q/V"),
("Inductor Energy","انرژی سلف","ind_energy","E=½LI²"),
("Capacitor Energy","انرژی خازن","cap_energy","E=½CV²"),
("Motor Input Power","توان ورودی موتور","motor_in","Pin=√3VIcosφ"),
("Motor Output Power","توان خروجی موتور","motor_out","Pout=Pin×η"),
("Motor Rated Current","جریان نامی موتور","motor_current","I=Pout/(√3Vηcosφ)"),
("Motor Slip","لغزش موتور القایی","slip","s=(ns−nr)/ns×100"),
("Synchronous Speed","سرعت سنکرون","sync_speed","ns=120f/P"),
("Motor Torque","گشتاور موتور","torque","T=9550P(kW)/n"),
("Motor Efficiency","راندمان موتور","motor_eff","Pout/Pin×100"),
("Star-Delta Current","جریان راه‌اندازی ستاره مثلث","star_delta","Istar≈IΔ/3"),
("Generator Power","توان ژنراتور سه‌فاز","generator","P=√3VIcosφ"),
("Generator Apparent Power","ظرفیت ژنراتور","gen_kva","S=√3VI/1000"),
("Battery Capacity","ظرفیت باتری","battery","Ah=I×t"),
("Battery Runtime","زمان پشتیبانی باتری","runtime","t=Ah/I"),
("DC-DC Output","خروجی مبدل DC","dc_converter","Pout=VinIinη"),
("Rectifier Average Voltage","ولتاژ متوسط یکسوساز","rectifier","Vdc≈0.9Vac (تمام‌موج)"),
("Diode Power","توان دیود","diode","P=Vf×I"),
("LED Resistor","مقاومت سری LED","led","R=(Vs−Vf)/I"),
("Voltage Divider","تقسیم ولتاژ","divider","Vout=Vin×R2/(R1+R2)"),
("Current Divider","تقسیم جریان","current_div","I1=It×R2/(R1+R2)"),
("RC Time Constant","ثابت زمانی RC","rc","τ=RC"),
("RL Time Constant","ثابت زمانی RL","rl","τ=L/R"),
("Frequency Period","دوره تناوب","period","T=1/f"),
("Angular Frequency","فرکانس زاویه‌ای","omega","ω=2πf"),
("Peak RMS Voltage","تبدیل RMS و پیک","rms","Vp=√2Vrms"),
("Peak RMS Current","تبدیل جریان RMS و پیک","irms","Ip=√2Irms"),
("Three-phase Line Voltage","تبدیل ولتاژ خط و فاز","line_phase","VL=√3Vph (ستاره)"),
("Three-phase Star Current","جریان فاز ستاره","star_current","IL=Iph"),
("Three-phase Delta Current","جریان خط مثلث","delta_current","IL=√3Iph"),
("Fault Level","سطح اتصال کوتاه","fault_level","Ssc=√3VIk"),
("Short Circuit Current","جریان اتصال کوتاه","short_current","Ik=Ssc/(√3V)"),
("Per-unit Impedance","امپدانس پریونیت","pu","Zpu=Zactual/Zbase"),
("Base Impedance","امپدانس مبنا","zbase","Zbase=V²/S"),
("Base Current","جریان مبنا","ibase","Ibase=S/(√3V)"),
("Transformer Inrush Reference","برآورد جریان هجومی ترانس","inrush","وابسته به طراحی؛ نیازمند داده سازنده"),
("Insulation Stress","تنش الکتریکی عایق","stress","E=V/d"),
("Electric Field","شدت میدان الکتریکی","field","E=V/d"),
("Surge Energy","انرژی خازنی موج","surge","E=½CV²"),
("Lightning Impulse","پارامتر موج ضربه‌ای","impulse","محاسبه مرجع؛ نیازمند شکل موج"),
("Corona Concept","بررسی مفهومی کرونا","corona","وابسته به هندسه و شرایط محیطی"),
("Clearance Reference","فاصله عایقی مرجع","clearance","طبق استاندارد و سطح عایقی انتخاب شود"),
("Creepage Reference","فاصله خزشی مرجع","creepage","طبق آلودگی و استاندارد انتخاب شود"),
("Transmission Line Current","جریان خط انتقال","line_current","I=P/(√3Vcosφ)"),
("Transmission Line Power","توان انتقالی","line_power","P=√3VIcosφ"),
("Line Loss","تلفات خط","line_loss","Ploss=3I²R"),
("Line Efficiency","راندمان خط","line_eff","Pout/Pin×100"),
("Receiving Voltage","ولتاژ دریافت‌کننده","receiving","مدل افت ولتاژ ساده‌شده"),
("Sending Voltage","ولتاژ ارسال‌کننده","sending","Vs≈Vr+ΔV"),
("Power Triangle","مثلث توان","triangle","S=√(P²+Q²)"),
("Phase Angle","زاویه فاز","phase","φ=acos(P/S)"),
("Reactive Compensation","جبران‌سازی راکتیو","compensation","Qc=P(tanφ1−tanφ2)"),
("Load Factor","ضریب بار","load_factor","میانگین بار/حداکثر بار"),
("Demand Factor","ضریب تقاضا","demand","حداکثر تقاضا/بار نصب‌شده"),
("Diversity Factor","ضریب همزمانی معکوس","diversity","Σحداکثر تقاضا/حداکثر همزمانی"),
("Utilization Factor","ضریب بهره‌برداری","utilization","حداکثر تقاضا/ظرفیت نامی"),
("Voltage Unbalance","عدم تعادل ولتاژ","unbalance","بیشینه انحراف/میانگین×100"),
("Frequency Deviation","انحراف فرکانس","freq_dev","Δf=f−fn"),
("Grounding Resistance","مقاومت زمین","ground","R=V/I؛ اندازه‌گیری میدانی لازم"),
("Touch Voltage","ولتاژ تماس","touch","نیازمند مدل شبکه زمین و استاندارد"),
("Step Voltage","ولتاژ گام","step","نیازمند مدل شبکه زمین و استاندارد"),
("Fuse Power","توان تلفاتی فیوز","fuse","P=I²R"),
("Breaker Breaking Capacity","ظرفیت قطع کلید","breaker","بر اساس Ik و استاندارد تجهیز"),
("Protection CT Ratio","نسبت تبدیل CT","ct","CTR=Ip/Is"),
("Protection VT Ratio","نسبت تبدیل VT","vt","VTR=Vp/Vs"),
("Relay Pickup","تنظیم جریان رله","relay","وابسته به هماهنگی حفاظتی"),
("Cable Ampacity Check","بررسی جریان مجاز کابل","ampacity","به جدول سازنده و ضرایب تصحیح نیاز دارد"),
("Busbar Current Density","چگالی جریان شینه","busbar","J=I/A"),
("Busbar Voltage Drop","افت ولتاژ شینه","bus_drop","ΔV=IR"),
("Power Factor Correction","اصلاح ضریب توان","pfc","Qc=P(tanφ1−tanφ2)"),
("Electrical Cost","هزینه انرژی","cost","هزینه=انرژی×تعرفه"),
]

# Topic groups used by the navigation. Each model key belongs to exactly one topic.
TOPIC_GROUPS = {
    'transformers': {'turns', 'tr_current', 'tr3_current', 'regulation', 'impedance', 'tr_loss', 'tr_eff', 'tr_load', 'tr_short', 'inrush'},
    'motors': {'motor_in', 'motor_out', 'motor_current', 'motor_eff', 'slip', 'sync_speed', 'torque', 'star_delta'},
    'cables': {'drop_dc', 'drop_1p', 'drop_3p', 'resistance', 'area', 'ampacity'},
    'circuits': {'ohm', 'copper_loss', 'dc_power', 'series', 'parallel', 'xc', 'xl', 'rlc', 'resonance', 'capacitance', 'ind_energy', 'cap_energy', 'divider', 'current_div', 'rc', 'rl', 'led', 'diode', 'rectifier', 'dc_converter'},
    'power': {'receiving', 'sending', 'line_phase', 'star_current', 'delta_current', 'efficiency', 'ac_single', 'ac_three', 'apparent', 'reactive', 'pf', 'energy', 'generator', 'gen_kva', 'line_current', 'line_power', 'line_loss', 'line_eff', 'triangle', 'phase', 'load_factor', 'demand', 'diversity', 'utilization', 'unbalance', 'freq_dev', 'compensation', 'capacitor', 'pfc', 'cost', 'busbar', 'bus_drop'},
    'protection': {'fault_level', 'short_current', 'ct', 'vt', 'relay', 'breaker', 'fuse', 'ground', 'touch', 'step', 'pu', 'zbase', 'ibase'},
    'high_voltage': {'stress', 'field', 'surge', 'impulse', 'corona', 'clearance', 'creepage'},
    'energy': {'battery', 'runtime', 'period', 'omega', 'rms', 'irms'},
}

# Models that only make sense for DC systems (hidden under AC).
DC_ONLY_KEYS = {'dc_power', 'drop_dc', 'battery', 'runtime', 'dc_converter', 'rectifier', 'led',
                'divider', 'current_div', 'cap_charge', 'peukert'}

# Keys that may be shown under the DC system.
DC_MODEL_KEYS = {'dc_power', 'drop_dc', 'battery', 'runtime', 'dc_converter', 'rectifier', 'led', 'divider', 'current_div',
                 'ohm', 'resistance', 'area', 'copper_loss', 'efficiency', 'energy', 'capacitance', 'ind_energy', 'cap_energy',
                 'rc', 'rl', 'period', 'omega', 'series', 'parallel', 'fuse', 'cap_charge', 'peukert', 'y_delta', 'wheatstone',
                 'derate', 'pct_drop'}


def topic_of(key):
    for topic, keys in TOPIC_GROUPS.items():
        if key in keys:
            return topic
    return 'general'


def _extended_meta():
    from app.modules.extended import EXT_META
    return EXT_META


MODEL_CATALOG = []
for idx, (en, fa, key, formula) in enumerate(_MODEL_ROWS[:100], 1):
    MODEL_CATALOG.append({"id": f"TG.VL/{idx:03d}", "series": "TG.VL", "name_en": en, "name_fa": fa,
                          "key": key, "formula": formula, "topic": topic_of(key),
                          "description_en": f"Offline deterministic engineering profile: {en}.",
                          "description_fa": f"مدل محاسباتی آفلاین {fa}؛ {formula}."})

EXTENDED_CATALOG = []
for idx, m in enumerate(_extended_meta(), 1):
    EXTENDED_CATALOG.append({"id": f"TG.VX/{idx:03d}", "series": "TG.VX", "name_en": m["en"], "name_fa": m["fa"],
                             "key": m["key"], "formula": m["formula"], "topic": m["topic"],
                             "description_en": m["desc_en"], "description_fa": m["desc_fa"]})

ALL_MODELS = MODEL_CATALOG + EXTENDED_CATALOG
DC_MODEL_KEYS |= {m["key"] for m in EXTENDED_CATALOG if m["key"] in DC_MODEL_KEYS}

MODULES = [
    {"id":"voltage","icon":"⚡","title_key":"voltage","description_key":"voltage_desc"},
    {"id":"models","icon":"TG","title_key":"models","description_key":"models_desc"},
    {"id":"formulas","icon":"ƒ","title_key":"formulas","description_key":"formulas_desc"},
    {"id":"transformers","icon":"TR","title_key":"transformers","description_key":"transformers_desc"},
    {"id":"motors","icon":"M","title_key":"motors","description_key":"motors_desc"},
    {"id":"circuits","icon":"Ω","title_key":"circuit","description_key":"circuit_desc"},
    {"id":"power","icon":"P","title_key":"power","description_key":"power_desc"},
    {"id":"settings","icon":"⚙","title_key":"settings","description_key":"settings_desc"},
]
