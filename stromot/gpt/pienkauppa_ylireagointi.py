"""Monen pienen aggressiivisen kaupan samansuuntainen ryntäys voi olla
lyhytikäistä seuraamista eikä suuren informoidun ostajan tai myyjän toimeksianto.
Kun kauppojen lukumäärä on poikkeava mutta BTC-määrä ei ja hinta jo liikkuu
ryntäyksen mukana, oletetaan vastaliike: ostoryntäys ennakoi laskua (down),
myyntiryntäys nousua (up). Ehto ei mittaa vain volatiliteettia, sillä se vaatii
lukumäärän ja volyymin erkanemisen sekä suunnallisen aggressoriylivoiman.
"""

NIMI = "Pienten kauppojen ylireagointi"
SELITYS = (
    "Poikkeuksellisen monta kauppatulostetta ilman vastaavaa BTC-volyymia, "
    "selva aggressoriylivoima ja rajattu myotaliike: haetaan vastaliiketta."
)
EHDOT = ("Pientulosteiden parvi", "Yksipuolinen virta", "Myotaliike")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT"]},
    "cooldown_seconds": {"type": "integer", "default": 3600, "min": 0, "max": 86400},
    "kaupparaja": {
        "type": "enum", "default": "92", "choices": ["92", "94"],
        "label": "Kauppalukumaara, 24 h persentiili",
    },
}
TARVITSEE = {
    "lkm": {"kind": "series", "field": "count", "step": 60},
    "volyymi": {"kind": "series", "field": "volume", "step": 60},
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "hinta": {"kind": "series", "field": "close", "step": 60},
    "lukuraja": {"kind": "percentile", "source": "lkm", "seconds": 86400,
                 "p": "$kaupparaja"},
    "volyymiraja": {"kind": "percentile", "source": "volyymi", "seconds": 86400,
                      "p": 90},
    "tuotto1": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": 60},
    "sigma15": {"kind": "sigma", "source": "hinta", "period": 900, "count": 96},
}


def ehto(ctx):
    if "lukuraja" not in ctx.uudet:
        return None
    lkm = ctx.palikat["lkm"]
    volyymi = ctx.palikat["volyymi"]
    delta = ctx.palikat["delta"]
    lukuraja = ctx.palikat["lukuraja"]
    volyymiraja = ctx.palikat["volyymiraja"]
    tuotto1 = ctx.palikat["tuotto1"]
    sigma = ctx.palikat["sigma15"]
    if (lkm is None or volyymi is None or delta is None
            or lukuraja is None or volyymiraja is None
            or tuotto1 is None or sigma is None):
        return ctx.tulos(conditions={"Pientulosteiden parvi": None,
                                    "Yksipuolinen virta": None,
                                    "Myotaliike": None})
    suunta = 1 if delta > 0 else -1
    parvi = (lkm > lukuraja and volyymi > 0
             and volyymi <= volyymiraja)
    ylivoima = abs(delta) * 5 >= volyymi
    myotaliike = (sigma > 0 and tuotto1 * suunta * 10 >= sigma
                  and tuotto1 * suunta * 2 <= sigma)
    osuma = parvi and ylivoima and myotaliike
    return ctx.tulos(
        "Pieni ostoryntays: vastaliike alas" if osuma and suunta > 0 else
        "Pieni myyntiryntays: vastaliike ylos" if osuma else None,
        conditions={"Pientulosteiden parvi": parvi,
                    "Yksipuolinen virta": ylivoima, "Myotaliike": myotaliike},
        direction=("down" if suunta > 0 else "up") if osuma else None,
    )
