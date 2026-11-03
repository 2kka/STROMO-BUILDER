"""Isot liput: poikkeuksellinen nettovirta harvoilla kaupoilla.

Mekanismi: tietoa omaava toimija ostaa tai myy aggressiivisesti isoilla
kerralla, koska hänellä on kiire ennen kuin tieto leviää. Silloin viiden
minuutin nettovirta (osto- miinus myyntivolyymi) on vuorokauden kärkeä, mutta
kauppoja on tavallista vähemmän: virta tulee isoista lapuista eikä monista
pienistä. Hinta on liikkunut virran suuntaan vasta vähän, joten tieto ei ole
vielä hinnassa.

Odotettu suunta: nettovirran suuntaan.

Ei pelkkä volatiliteetin tunnistin: ehto ei vaadi hintaliikettä vaan rajaa sen
pieneksi (0 < liike < σ15 virran suuntaan). Suunta tulee virrasta. Kauppojen
vähäinen määrä erottaa ison toimijan joukkopaniikista, jossa kauppoja on paljon.
Erottuu absorptiosta: absorptiossa hinta ei liiku virran suuntaan ja hälytys on
vastaan, tässä hinta on jo lähtenyt virran suuntaan ja hälytys on myötä.
"""

NIMI = "Isot liput"
SELITYS = (
    "5 min |CVD| ≥ 24 h p95, kauppojen määrä 5 min ≤ 24 h mediaani (tai p35) ja hinta "
    "liikkunut virran suuntaan 0–1 σ15 → virran suuntaan."
)
EHDOT = ("Virta", "Harvat kaupat", "Hinta myötä")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {
        "type": "enum",
        "default": "BTC-USDT",
        "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"],
    },
    "cooldown_seconds": {"type": "integer", "default": 3600, "min": 0, "max": 86400},
    "maara_p": {
        "type": "enum",
        "default": "50",
        "choices": ["50", "35"],
        "label": "Kauppamäärä enintään 24 h persentiili",
    },
}
TARVITSEE = {
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "maara": {"kind": "series", "field": "count", "step": 60},
    "hinta": {"kind": "series", "field": "close", "step": 60},
    "cvd": {"kind": "window", "source": "delta", "op": "sum", "seconds": 300},
    "cvd_abs": {"kind": "window", "source": "cvd", "op": "abs", "seconds": 60},
    "cvd_raja": {"kind": "percentile", "source": "cvd_abs", "seconds": 86400, "p": 95},
    "maara5": {"kind": "window", "source": "maara", "op": "sum", "seconds": 300},
    "maara_raja": {
        "kind": "percentile", "source": "maara5", "seconds": 86400, "p": "$maara_p",
    },
    "liike": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": 300},
    "sigma15": {"kind": "sigma", "source": "hinta", "period": 900, "count": 96},
}


def ehto(ctx):
    if "cvd_raja" not in ctx.uudet:
        return None
    cvd = ctx.palikat["cvd"]
    virta = cvd != 0 and ctx.palikat["cvd_abs"] >= ctx.palikat["cvd_raja"]
    harvat = ctx.palikat["maara5"] <= ctx.palikat["maara_raja"]
    liike = ctx.palikat["liike"] if cvd > 0 else -ctx.palikat["liike"]
    myota = liike > 0 and liike < ctx.palikat["sigma15"]
    osuma = virta and harvat and myota
    hsuunta = None
    viesti = None
    if osuma:
        hsuunta = "up" if cvd > 0 else "down"
        viesti = "Isot liput: vahva nettovirta harvoilla kaupoilla, hinta vasta lähdössä"
    return ctx.tulos(
        viesti,
        conditions={"Virta": virta, "Harvat kaupat": harvat, "Hinta myötä": myota},
        direction=hsuunta,
    )
