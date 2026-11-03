"""Uupumus: pakotetun virran huipentuma, jota ei jatketa.

Mekanismi: nopea 15 minuutin liike, jonka huipentumaminuutilla on vuorokauden
poikkeuksellisin volyymi ja aggressiivinen virta liikkeen suuntaan, on usein
pakotettua kauppaa: stoppeja, likvidaatioita ja perässä hyppääjiä. Kun pakotettu
virta loppuu, likviditeetin tarjoajat palauttavat hintaa. Merkki loppumisesta on
seuraavien minuuttien aikana sulkeutuva minuutti, jonka virta on kääntynyt eikä
hinta enää ylitä huipentuman päätöstä.

Odotettu suunta: liikettä vastaan (nousun huipentuman jälkeen alas, laskun jälkeen ylös).

Ei pelkkä volatiliteetin tunnistin: liike ja volyymi ovat vain ehdokkaan
edellytys. Hälytys tulee vasta, kun virta kääntyy eikä hinta jatka, ja suunta
on liikkeelle vastakkainen. Jos liike jatkuu, hälytystä ei tule.
"""

NIMI = "Uupumus"
SELITYS = (
    "15 min liike ≥ k·σ15 ja huipentumaminuutin volyymi ≥ 24 h p99 liikkeen suuntaisella "
    "virralla; 5 min sisällä virta kääntyy eikä hinta ylitä huipentuman päätöstä → vastaan."
)
EHDOT = ("Liike", "Huipentuma", "Kääntö")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {
        "type": "enum",
        "default": "BTC-USDT",
        "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"],
    },
    "cooldown_seconds": {"type": "integer", "default": 1800, "min": 0, "max": 86400},
    "liike_sigma": {
        "type": "enum",
        "default": "2",
        "choices": ["2", "2.5"],
        "label": "15 min liike vähintään × σ15",
    },
}
TARVITSEE = {
    "hinta": {"kind": "series", "field": "close", "step": 60},
    "volyymi": {"kind": "series", "field": "volume", "step": 60},
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "liike": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": 900},
    "vol_raja": {"kind": "percentile", "source": "volyymi", "seconds": 86400, "p": 99},
    "sigma15": {"kind": "sigma", "source": "hinta", "period": 900, "count": 96},
    "kaanto": {"kind": "follow", "seconds": 300},
}


def ehto(ctx):
    if "vol_raja" not in ctx.uudet:
        return None
    hinta = ctx.palikat["hinta"]
    delta = ctx.palikat["delta"]
    liike = ctx.palikat["liike"]
    raja = ctx.luku(ctx.parameters["liike_sigma"]) * ctx.palikat["sigma15"]
    iso = ctx.palikat["volyymi"] >= ctx.palikat["vol_raja"]
    ylos = liike >= raja and iso and delta > 0
    alas = liike <= -raja and iso and delta < 0
    tapahtuma = ylos or alas

    suunta = ctx.state.get("suunta")
    taso = ctx.state.get("taso")
    kaantyi = False
    if suunta == "up" and taso is not None:
        kaantyi = delta < 0 and hinta <= taso
    if suunta == "down" and taso is not None:
        kaantyi = delta > 0 and hinta >= taso

    seuranta = ctx.seuraa("kaanto", tapahtuma, kaantyi)
    viesti = None
    hsuunta = None
    if seuranta.value is True:
        hsuunta = "down" if suunta == "up" else "up"
        viesti = "Uupumus: huipentuman virta kääntyi, hinta ei jatkanut"
    if seuranta.started_ms == ctx.timestamp_ms:
        suunta = "up" if ylos else "down"
        taso = hinta

    return ctx.tulos(
        viesti,
        conditions={
            "Liike": liike >= raja or liike <= -raja,
            "Huipentuma": tapahtuma,
            "Kääntö": seuranta.value,
        },
        state={"kaanto": seuranta.state, "suunta": suunta, "taso": taso},
        direction=hsuunta,
    )
