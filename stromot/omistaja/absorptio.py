"""Absorptio – lukittu määritelmä 2.11.2026 (1.B'). Ei säädetä tulosten perusteella."""

NIMI = "Absorptio"
SELITYS = (
    "Aggressiivinen virta ei liikuta hintaa: |CVD| W minuutissa ≥ oma 24 h p95, "
    "mutta hinta on liikkunut CVD:n suuntaan enintään 0,25σ15. Hälytys CVD:tä vastaan "
    "(ostot imeytyvät → alas, myynnit imeytyvät → ylös). Arvioidaan minuutin sulkeutuessa."
)
EHDOT = ("CVD", "Hinta paikallaan")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {
        "type": "enum",
        "default": "BTC-USDT",
        "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"],
    },
    "cooldown_seconds": {"type": "integer", "default": 1800, "min": 0, "max": 86400},
    "ikkuna": {
        "type": "enum",
        "default": "600",
        "choices": ["600", "300", "1200"],
        "label": "CVD-ikkuna s (W 10 / 5 / 20 min)",
    },
    "persentiili": {
        "type": "number", "default": "95", "min": "50", "max": "100", "label": "|CVD| persentiili",
    },
    "hinta_sigma": {
        "type": "number", "default": "0.25", "min": "0", "max": "5", "label": "Hinta enintään × σ15",
    },
}
TARVITSEE = {
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "cvd": {"kind": "window", "source": "delta", "op": "sum", "seconds": "$ikkuna"},
    "cvd_abs": {"kind": "window", "source": "cvd", "op": "abs", "seconds": 60},
    "raja": {"kind": "percentile", "source": "cvd_abs", "seconds": 86400, "p": "$persentiili"},
    "hinta": {"kind": "series", "field": "close", "step": 60},
    "lmuutos": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": "$ikkuna"},
    "sigma15": {"kind": "sigma", "source": "hinta", "period": 900, "count": 96},
}


def ehto(ctx):
    if "raja" not in ctx.uudet:
        return None
    cvd = ctx.palikat["cvd"]
    vahva = cvd != 0 and ctx.palikat["cvd_abs"] >= ctx.palikat["raja"]
    liike = ctx.palikat["lmuutos"] if cvd > 0 else -ctx.palikat["lmuutos"]
    paikallaan = liike <= ctx.luku(ctx.parameters["hinta_sigma"]) * ctx.palikat["sigma15"]
    osuma = vahva and paikallaan
    suunta = None
    viesti = None
    if osuma:
        suunta = "down" if cvd > 0 else "up"
        viesti = f"Absorptio: CVD {cvd:+.2f} BTC / {ctx.parameters['ikkuna']} s, hinta paikallaan"
    return ctx.tulos(
        viesti,
        conditions={"CVD": vahva, "Hinta paikallaan": paikallaan},
        direction=suunta,
    )
