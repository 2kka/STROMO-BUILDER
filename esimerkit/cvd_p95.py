"""Testiesimerkki: CVD-ikkuna ylittää 24 tunnin p95:n."""

NIMI = "CVD-ikkuna yli p95"
SELITYS = "Minuuttinäytteiden CVD-summa ylittää oman 24 h p95:n."
EHDOT = ("CVD",)
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-EUR", "choices": ["BTC-EUR"]},
    "cooldown_seconds": {"type": "integer", "default": 300, "min": 0, "max": 86400},
    "ikkuna": {"type": "integer", "default": 300, "min": 60, "max": 86400},
    "takajakso": {"type": "integer", "default": 86400, "min": 60, "max": 86400},
    "persentiili": {"type": "number", "default": "95", "min": "0", "max": "100"},
}
TARVITSEE = {
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "cvd": {"kind": "window", "source": "delta", "op": "sum", "seconds": "$ikkuna"},
    "p95": {"kind": "percentile", "source": "cvd", "seconds": "$takajakso", "p": "$persentiili"},
}


def ehto(ctx):
    if "p95" not in ctx.uudet:
        return None
    if ctx.palikat["cvd"] is None:
        return ctx.tulos(conditions={"CVD": None})
    osuma = ctx.palikat["cvd"] > ctx.palikat["p95"]
    return ctx.tulos(
        "CVD yli 24 h p95" if osuma else None, conditions={"CVD": osuma}, direction="up"
    )
