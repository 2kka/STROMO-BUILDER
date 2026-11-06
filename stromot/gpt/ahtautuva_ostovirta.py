"""Hypoteesi: Vaihteluväli supistuu ostovirran pysyessä plussalla.
Mekanismi: Tarjonnan puute voi ennakoida sivuttaisalueen nousua. Tasainen ostovirta hallitsee ilman suurtakaan hintaliikettä.
Odotettu suunta: up.
Miksi ei pelkkä volatiliteetin tunnistin: Signaali vaatii paikallisen rakenteen ja suunnallisen kauppatapahtuman.
Mikä kumoaisi: Reuna alittaa LIIGAn kynnyksen tai naapurivariantin reuna ei ole positiivinen.
"""

NIMI = "Ahtautuva ostovirta"
SELITYS = "Vaihteluväli supistuu myyntivirran pysyessä miinuksella."
EHDOT = ("Markkinatila", "Suuntasignaali")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT"]},
    "cooldown_seconds": {"type": "integer", "default": 7200, "min": 0, "max": 86400},
    "tiukkuus": {"type": "enum", "default": "1", "choices": ["1", "1.2"]},
}
TARVITSEE = {
    "hinta": {"kind":"series","field":"close","step":60},
    "ylin": {"kind":"series","field":"high","step":60},
    "alin": {"kind":"series","field":"low","step":60},
    "vol": {"kind":"series","field":"volume","step":60},
    "delta": {"kind":"series","field":"delta","step":60},
    "sigma15": {"kind":"sigma","source":"hinta","period":900,"count":96},
    "huippu4": {"kind":"window","source":"ylin","op":"max","seconds":14400},
    "pohja4": {"kind":"window","source":"alin","op":"min","seconds":14400},
    "huippu24": {"kind":"window","source":"ylin","op":"max","seconds":86400},
    "huippu1": {"kind":"window","source":"ylin","op":"max","seconds":3600},
    "pohja1": {"kind":"window","source":"alin","op":"min","seconds":3600},
    "ylin5": {"kind":"window","source":"ylin","op":"max","seconds":300},
    "alin5": {"kind":"window","source":"alin","op":"min","seconds":300},
    "vol15": {"kind":"window","source":"vol","op":"sum","seconds":900},
    "virta15": {"kind":"window","source":"delta","op":"sum","seconds":900},
    "muutos15": {"kind":"window","source":"hinta","op":"log_change","seconds":900},
}


def ehto(ctx):
    if "hinta" not in ctx.uudet: return None
    hinta = ctx.palikat["hinta"]
    ylin = ctx.palikat["ylin"]
    alin = ctx.palikat["alin"]
    vol = ctx.palikat["vol"]
    delta = ctx.palikat["delta"]
    sigma15 = ctx.palikat["sigma15"]
    huippu4 = ctx.palikat["huippu4"]
    pohja4 = ctx.palikat["pohja4"]
    huippu24 = ctx.palikat["huippu24"]
    huippu1 = ctx.palikat["huippu1"]
    pohja1 = ctx.palikat["pohja1"]
    ylin5 = ctx.palikat["ylin5"]
    alin5 = ctx.palikat["alin5"]
    vol15 = ctx.palikat["vol15"]
    virta15 = ctx.palikat["virta15"]
    muutos15 = ctx.palikat["muutos15"]
    if hinta is None or ylin is None or alin is None or vol is None or delta is None or sigma15 is None or huippu4 is None or pohja4 is None or huippu24 is None or huippu1 is None or pohja1 is None or ylin5 is None or alin5 is None or vol15 is None or virta15 is None or muutos15 is None:
        return None
    if hinta <= 0 or sigma15 <= 0:
        return None
    leveys = huippu4 - pohja4
    lasku = (huippu24 - hinta) / hinta >= sigma15 * 4
    sivuttain = leveys > 0 and leveys / hinta <= sigma15 * ctx.luku("3") * ctx.luku(ctx.parameters["tiukkuus"])
    tila = lasku and sivuttain
    rakenne = (ylin5 - alin5) / hinta < sigma15 * ctx.luku('0.40') and (huippu1 - pohja1) / hinta < sigma15 * ctx.luku('1.50') and virta15 > 0 and virta15 < vol15 * ctx.luku('0.35') and muutos15 > 0 and hinta < pohja4 + leveys * ctx.luku('0.65')
    osuma = tila and rakenne
    return ctx.tulos("Ahtautuva ostovirta" if osuma else None, conditions={"Markkinatila": tila, "Suuntasignaali": rakenne}, direction="up" if osuma else None)
