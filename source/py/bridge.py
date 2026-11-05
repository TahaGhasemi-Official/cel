"""JSON bridge between the browser UI (Pyodide worker) and the VOLTEX Python engine.

Entry point: handle(request_json: str) -> str (JSON). Never raises; errors are returned
as {"ok": false, "error": "..."} so the UI can show them.
"""
import json
import math

from app.modules.engine import FIELDS, calculate, _solve_one_unknown
from app.modules.registry import (ALL_MODELS, VOLTAGE_GROUPS, TOPIC_GROUPS,
                                  DC_MODEL_KEYS, DC_ONLY_KEYS)
from app.modules.alternatives import VARIANTS, AUX, input_fields, evaluate, missing_inputs
from app.modules.web_extra import EXTRA_MODELS, EXTRA_FIELDS, calculate_extra


def _clean(x):
    """Make values JSON-safe: non-finite floats become strings."""
    if isinstance(x, float):
        if math.isnan(x):
            return "NaN"
        if math.isinf(x):
            return "∞" if x > 0 else "-∞"
        return x
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    return x


def _fields_of(key):
    if key in EXTRA_FIELDS:
        return [list(f) for f in EXTRA_FIELDS[key]]
    return [list(f) for f in input_fields(key)]


def _variants_of(key):
    out = []
    for v in VARIANTS.get(key, []):
        out.append({"id": v["id"], "out_en": v["out_en"], "out_fa": v["out_fa"],
                    "unit": v["unit"], "formula": v["shown"], "inputs": v["inputs"]})
    return out


def catalog():
    models = []
    for m in ALL_MODELS + EXTRA_MODELS:
        item = dict(m)
        item["fields"] = _fields_of(m["key"])
        item["variants"] = _variants_of(m["key"]) if m["key"] not in EXTRA_FIELDS else []
        item["optional"] = [a[0] for a in AUX.get(m["key"], [])]
        models.append(item)
    return {
        "ok": True,
        "models": models,
        "groups": VOLTAGE_GROUPS,
        "topic_groups": {k: sorted(v) for k, v in TOPIC_GROUPS.items()},
        "dc_only": sorted(DC_ONLY_KEYS),
        "dc_models": sorted(DC_MODEL_KEYS),
    }


def calc(key, data):
    try:
        if key in EXTRA_FIELDS:
            return {"ok": True, "status": "ok", "results": _clean(calculate_extra(key, data)), "solved": None}
        out = calculate(key, dict(data))
        if out.get("status") == "guidance":
            return {"ok": True, "status": "guidance", "message": out["message"]}
        solved = out.get("solved_unknown")
        return {"ok": True, "status": "ok", "results": _clean(out["results"]),
                "solved": None if solved is None else {"key": solved[0], "value": _clean(solved[1])}}
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    except (ZeroDivisionError, OverflowError, TypeError) as e:
        return {"ok": False, "error": f"Calculation error: {e}"}


def alt(key, data):
    """Evaluate every alternative relation for a model. Ready ones get a result."""
    rows = []
    for v in VARIANTS.get(key, []):
        variant_inputs = v["inputs"]
        missing = [k for k in variant_inputs if str(data.get(k, "")).strip() == ""]
        row = {"id": v["id"], "out_en": v["out_en"], "out_fa": v["out_fa"], "unit": v["unit"],
               "formula": v["shown"], "missing": missing, "ready": not missing,
               "result": None, "error": None}
        if not missing:
            try:
                r = evaluate(v, {k: str(data[k]) for k in variant_inputs})
                row["result"] = _clean(r["value"])
                row["substituted"] = r["substituted"]
            except ValueError as e:
                row["error"] = str(e)
        rows.append(row)
    return {"ok": True, "rows": rows}


def handle(request_json):
    try:
        req = json.loads(request_json)
        op = req.get("op")
        if op == "catalog":
            res = catalog()
        elif op == "calc":
            res = calc(req["key"], req.get("data", {}))
        elif op == "alt":
            res = alt(req["key"], req.get("data", {}))
        else:
            res = {"ok": False, "error": f"Unknown operation: {op}"}
    except Exception as e:  # keep the bridge total
        res = {"ok": False, "error": f"Internal error: {e}"}
    return json.dumps(res, ensure_ascii=False)
