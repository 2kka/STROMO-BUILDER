"""Pitkä aggressiivinen myynti- tai ostojakso voi ehtyä, kun vastapuolen
toimeksiannot alkavat hallita seuraavia kahta minuuttia. Kun nettokauppavirran
merkki ja hinta kääntyvät yhdessä aiempaa 18 minuutin painetta vastaan,
odotetaan uuden ostovirran jälkeen nousua (up) tai myyntivirran jälkeen
laskua (down). Pelkkä volatiliteetti ei riitä: sekä vanhan ja uuden
aggressorivirran että hintaliikkeiden on oltava vastakkaismerkkisiä.
"""

NIMI = "Aggressorivirran suunnanvaihto"
SELITYS = (
    "18 minuutin vallitsevaa aggressorivirtaa seuraa poikkeuksellinen "
    "kahden minuutin vastavirta; myös hinta vaihtaa suuntaa."
)
EHDOT = ("Uusi vastavirta", "Vanha paine", "Hinnan kaannos")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT"]},
    "cooldown_seconds": {"type": "integer", "default": 3600, "min": 0, "max": 86400},
    "virtaraja": {
        "type": "enum", "default": "95", "choices": ["95", "97"],
        "label": "2 minuutin |CVD|, 24 h persentiili",
    },
}
TARVITSEE = {
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "volyymi": {"kind": "series", "field": "volume", "step": 60},
    "hinta": {"kind": "series", "field": "close", "step": 60},
    "virta2": {"kind": "window", "source": "delta", "op": "sum", "seconds": 120},
    "virta20": {"kind": "window", "source": "delta", "op": "sum", "seconds": 1200},
    "volyymi2": {"kind": "window", "source": "volyymi", "op": "sum", "seconds": 120},
    "voima2": {"kind": "window", "source": "virta2", "op": "abs", "seconds": 60},
    "raja": {
        "kind": "percentile", "source": "voima2", "seconds": 86400,
        "p": "$virtaraja",
    },
    "tuotto2": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": 120},
    "tuotto20": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": 1200},
    "sigma15": {"kind": "sigma", "source": "hinta", "period": 900, "count": 96},
}


def ehto(ctx):
    if "raja" not in ctx.uudet:
        return None
    virta2 = ctx.palikat["virta2"]
    virta20 = ctx.palikat["virta20"]
    volyymi2 = ctx.palikat["volyymi2"]
    voima2 = ctx.palikat["voima2"]
    raja = ctx.palikat["raja"]
    tuotto2 = ctx.palikat["tuotto2"]
    tuotto20 = ctx.palikat["tuotto20"]
    sigma = ctx.palikat["sigma15"]
    if (virta2 is None or virta20 is None or volyymi2 is None
            or voima2 is None or raja is None or tuotto2 is None
            or tuotto20 is None or sigma is None):
        return ctx.tulos(conditions={"Uusi vastavirta": None,
                                    "Vanha paine": None,
                                    "Hinnan kaannos": None})
    suunta = 1 if virta2 > 0 else -1
    vanha_virta = virta20 - virta2
    vanha_tuotto = tuotto20 - tuotto2
    uusi = (volyymi2 > 0 and voima2 > raja
            and voima2 * 5 >= volyymi2)
    vanha = (vanha_virta * virta2 < 0
             and abs(vanha_virta) * 2 >= voima2 * 3)
    kaannos = (sigma > 0 and vanha_tuotto * suunta * 3 <= -sigma
               and tuotto2 * suunta * 5 >= sigma
               and tuotto2 * suunta * 2 <= sigma * 3)
    osuma = uusi and vanha and kaannos
    return ctx.tulos(
        "Ostajat ottivat aloitteen" if osuma and suunta > 0 else
        "Myyjat ottivat aloitteen" if osuma else None,
        conditions={"Uusi vastavirta": uusi, "Vanha paine": vanha,
                    "Hinnan kaannos": kaannos},
        direction=("up" if suunta > 0 else "down") if osuma else None,
    )
