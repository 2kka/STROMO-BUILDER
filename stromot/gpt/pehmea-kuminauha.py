"""Hypoteesi: Alareunassa loiva myynti palautuu, kun ostajat ottavat pienen etumatkan.
Mekanismi: Jälkilaskun sivuttaisalueella viimeiset myyjät eivät löydä uusia seuraajia. Hinnan pieni irtoaminen pohjasta voi tuoda vastapuolen ostot.
Odotettu suunta: up.
Miksi ei pelkkä volatiliteetin tunnistin: Tässä ei etsitä suurta liikettä vaan hiljaista hintapalautumista.
Mikä kumoaisi: Reuna verrokkeihin ei ylitä LIIGAn ennakkoon lukittua kynnystä tai naapurivariantti ei tue suuntaa.
"""

NIMI = "Pehmeä kuminauha"
SELITYS = "Alareunassa loiva myynti palautuu, kun ostajat ottavat pienen etumatkan."
EHDOT = ("Laskun jalkeinen sivuttaistila", "Suunnallinen rakenne")
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
    "kaupat": {"kind":"series","field":"count","step":60},
    "delta": {"kind":"series","field":"delta","step":60},
    "sigma15": {"kind":"sigma","source":"hinta","period":900,"count":96},
    "huippu4": {"kind":"window","source":"ylin","op":"max","seconds":14400},
    "pohja4": {"kind":"window","source":"alin","op":"min","seconds":14400},
    "huippu24": {"kind":"window","source":"ylin","op":"max","seconds":86400},
    "kaupat5": {"kind":"window","source":"kaupat","op":"sum","seconds":300},
    "kaupatmedia": {"kind":"percentile","source":"kaupat5","seconds":86400,"p":50},
    "virta5": {"kind":"window","source":"delta","op":"sum","seconds":300},
    "muutos2": {"kind":"window","source":"hinta","op":"log_change","seconds":120},
    "muutos15": {"kind":"window","source":"hinta","op":"log_change","seconds":900},
}


def ehto(ctx):
    if "hinta" not in ctx.uudet: return None
    hinta = ctx.palikat["hinta"]
    ylin = ctx.palikat["ylin"]
    alin = ctx.palikat["alin"]
    kaupat = ctx.palikat["kaupat"]
    delta = ctx.palikat["delta"]
    sigma15 = ctx.palikat["sigma15"]
    huippu4 = ctx.palikat["huippu4"]
    pohja4 = ctx.palikat["pohja4"]
    huippu24 = ctx.palikat["huippu24"]
    kaupat5 = ctx.palikat["kaupat5"]
    kaupatmedia = ctx.palikat["kaupatmedia"]
    virta5 = ctx.palikat["virta5"]
    muutos2 = ctx.palikat["muutos2"]
    muutos15 = ctx.palikat["muutos15"]
    if hinta is None or ylin is None or alin is None or kaupat is None or delta is None or sigma15 is None or huippu4 is None or pohja4 is None or huippu24 is None or kaupat5 is None or kaupatmedia is None or virta5 is None or muutos2 is None or muutos15 is None:
        return None
    if hinta <= 0 or sigma15 <= 0:
        return None
    leveys = huippu4 - pohja4
    lasku = (huippu24 - hinta) / hinta >= sigma15 * 4
    sivuttain = leveys > 0 and leveys / hinta <= sigma15 * ctx.luku("3") * ctx.luku(ctx.parameters["tiukkuus"])
    tila = lasku and sivuttain
    rakenne = hinta < pohja4 + leveys * ctx.luku('0.30') and muutos15 < 0 and muutos15 > -sigma15 and muutos2 > 0 and virta5 > 0 and kaupat5 < kaupatmedia
    osuma = tila and rakenne
    return ctx.tulos(
        "Pehmeä kuminauha" if osuma else None,
        conditions={"Laskun jalkeinen sivuttaistila": tila, "Suunnallinen rakenne": rakenne},
        direction="up" if osuma else None,
    )
