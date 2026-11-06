"""Hypoteesi: Kauppojen määrä kiihtyy hiljaisen vartin jälkeen pohjan tuntumassa.
Mekanismi: Ostajat aktivoituvat yhtä aikaa sivuttaisalueen pohjalla. Kasvava kauppatahti ja ostojen enemmistö voivat edeltää nousua.
Odotettu suunta: up.
Miksi ei pelkkä volatiliteetin tunnistin: Signaali vaatii paikallisen hintarakenteen ja suunnallisen kauppatapahtuman.
Mikä kumoaisi: Reuna alittaa LIIGAn kynnyksen tai naapurivariantin reuna ei ole positiivinen.
"""

NIMI = "Tauon jälkeinen osto"
SELITYS = "Kauppojen määrä kiihtyy hiljaisen vartin jälkeen pohjan tuntumassa."
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
    "kaupat": {"kind":"series","field":"count","step":60},
    "delta": {"kind":"series","field":"delta","step":60},
    "sigma15": {"kind":"sigma","source":"hinta","period":900,"count":96},
    "huippu4": {"kind":"window","source":"ylin","op":"max","seconds":14400},
    "pohja4": {"kind":"window","source":"alin","op":"min","seconds":14400},
    "huippu24": {"kind":"window","source":"ylin","op":"max","seconds":86400},
    "kaupat5": {"kind":"window","source":"kaupat","op":"sum","seconds":300},
    "kaupat15": {"kind":"window","source":"kaupat","op":"sum","seconds":900},
    "kaupatkorkea": {"kind":"percentile","source":"kaupat5","seconds":86400,"p":85},
    "vol5": {"kind":"window","source":"vol","op":"sum","seconds":300},
    "virta5": {"kind":"window","source":"delta","op":"sum","seconds":300},
    "muutos5": {"kind":"window","source":"hinta","op":"log_change","seconds":300},
}


def ehto(ctx):
    if "hinta" not in ctx.uudet: return None
    hinta = ctx.palikat["hinta"]
    ylin = ctx.palikat["ylin"]
    alin = ctx.palikat["alin"]
    vol = ctx.palikat["vol"]
    kaupat = ctx.palikat["kaupat"]
    delta = ctx.palikat["delta"]
    sigma15 = ctx.palikat["sigma15"]
    huippu4 = ctx.palikat["huippu4"]
    pohja4 = ctx.palikat["pohja4"]
    huippu24 = ctx.palikat["huippu24"]
    kaupat5 = ctx.palikat["kaupat5"]
    kaupat15 = ctx.palikat["kaupat15"]
    kaupatkorkea = ctx.palikat["kaupatkorkea"]
    vol5 = ctx.palikat["vol5"]
    virta5 = ctx.palikat["virta5"]
    muutos5 = ctx.palikat["muutos5"]
    if hinta is None or ylin is None or alin is None or vol is None or kaupat is None or delta is None or sigma15 is None or huippu4 is None or pohja4 is None or huippu24 is None or kaupat5 is None or kaupat15 is None or kaupatkorkea is None or vol5 is None or virta5 is None or muutos5 is None:
        return None
    if hinta <= 0 or sigma15 <= 0:
        return None
    leveys = huippu4 - pohja4
    lasku = (huippu24 - hinta) / hinta >= sigma15 * 4
    sivuttain = leveys > 0 and leveys / hinta <= sigma15 * ctx.luku("3") * ctx.luku(ctx.parameters["tiukkuus"])
    tila = lasku and sivuttain
    rakenne = hinta < pohja4 + leveys * ctx.luku('0.35') and kaupat5 > kaupatkorkea and kaupat15 - kaupat5 < kaupat5 and virta5 > vol5 * ctx.luku('0.12') and muutos5 >= 0
    osuma = tila and rakenne
    return ctx.tulos("Tauon jälkeinen osto" if osuma else None, conditions={"Markkinatila": tila, "Suuntasignaali": rakenne}, direction="up" if osuma else None)
