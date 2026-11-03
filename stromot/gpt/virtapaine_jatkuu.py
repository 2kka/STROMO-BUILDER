"""Pitkittynyt aggressiivinen metatilaus jatkaa usein ennen kuin koko toimeksianto on valmis:
sama ostaja- tai myyjäpuoli hallitsee sekä viiden että viidentoista minuutin
kauppavirtaa ja siirtää hintaa hallitusti. Ostopaine ennakoi nousua (up),
myyntipaine laskua (down). Tämä ei ole volatiliteettihälytin, koska osuma
vaatii poikkeavan suunnallisen CVD:n, pitkän virran jatkuvuuden, merkittävän
ostojen/myyntien epätasapainon ja samansuuntaisen mutta rajatun hintavaikutuksen.
"""

NIMI = "Pitkittyva virtapaine"
SELITYS = (
    "5 min poikkeuksellinen aggressorivirta jatkaa 15 min nettovirran suuntaa, "
    "ja hinta reagoi samaan suuntaan muttei rajusti."
)
EHDOT = ("Voimakas virta", "Jatkuvuus", "Hallittu hintavaikutus")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT"]},
    "cooldown_seconds": {"type": "integer", "default": 3600, "min": 0, "max": 86400},
    "virtaraja": {
        "type": "enum", "default": "97", "choices": ["97", "98"],
        "label": "5 minuutin |CVD|, 24 h persentiili",
    },
}
TARVITSEE = {
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "volyymi": {"kind": "series", "field": "volume", "step": 60},
    "hinta": {"kind": "series", "field": "close", "step": 60},
    "virta5": {"kind": "window", "source": "delta", "op": "sum", "seconds": 300},
    "virta15": {"kind": "window", "source": "delta", "op": "sum", "seconds": 900},
    "volyymi5": {"kind": "window", "source": "volyymi", "op": "sum", "seconds": 300},
    "voima5": {"kind": "window", "source": "virta5", "op": "abs", "seconds": 60},
    "raja": {
        "kind": "percentile", "source": "voima5", "seconds": 86400,
        "p": "$virtaraja",
    },
    "tuotto5": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": 300},
    "tuotto1": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": 60},
    "sigma15": {"kind": "sigma", "source": "hinta", "period": 900, "count": 96},
}


def ehto(ctx):
    if "raja" not in ctx.uudet:
        return None
    virta5 = ctx.palikat["virta5"]
    virta15 = ctx.palikat["virta15"]
    volyymi5 = ctx.palikat["volyymi5"]
    voima5 = ctx.palikat["voima5"]
    raja = ctx.palikat["raja"]
    tuotto5 = ctx.palikat["tuotto5"]
    tuotto1 = ctx.palikat["tuotto1"]
    sigma = ctx.palikat["sigma15"]
    if (virta5 is None or virta15 is None or volyymi5 is None
            or voima5 is None or raja is None or tuotto5 is None
            or tuotto1 is None or sigma is None):
        return ctx.tulos(conditions={"Voimakas virta": None,
                                    "Jatkuvuus": None,
                                    "Hallittu hintavaikutus": None})
    suunta = 1 if virta5 > 0 else -1
    vahva = (volyymi5 > 0 and voima5 > raja
             and voima5 * 5 >= volyymi5)
    jatkuva = (virta5 * virta15 > 0
               and abs(virta15) * 2 >= voima5 * 3)
    vaikutus = (sigma > 0 and tuotto5 * suunta * 5 >= sigma
                and tuotto5 * suunta * 20 <= sigma * 17
                and tuotto1 * suunta > 0)
    osuma = vahva and jatkuva and vaikutus
    return ctx.tulos(
        "Pitkittynyt ostovirta jatkuu" if osuma and suunta > 0 else
        "Pitkittynyt myyntivirta jatkuu" if osuma else None,
        conditions={"Voimakas virta": vahva, "Jatkuvuus": jatkuva,
                    "Hallittu hintavaikutus": vaikutus},
        direction=("up" if suunta > 0 else "down") if osuma else None,
    )
