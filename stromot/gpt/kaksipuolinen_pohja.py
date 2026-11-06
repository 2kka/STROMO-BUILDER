"""Hypoteesi: Alalaidassa käydään paljon kauppaa molempiin suuntiin ilman nettovoittajaa.
Mekanismi: Ostajat vastaanottavat alareunan myynnit, ja tarjoukset lakkaavat liikkumasta alas. Vähäinen ostajien etu voi sysätä hinnan takaisin alueen keskelle.
Odotettu suunta: up.
Miksi ei pelkkä volatiliteetin tunnistin: Hälytys vaatii suuren kaksipuolisen vaihtomäärän, ei yksipuolista aggressiota.
Mikä kumoaisi: Reuna verrokkeihin ei ylitä LIIGAn ennakkoon lukittua kynnystä tai naapurivariantti ei tue suuntaa.
"""

NIMI = "Kaksipuolinen pohja"
SELITYS = "Alalaidassa käydään paljon kauppaa molempiin suuntiin ilman nettovoittajaa."
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
    "vol": {"kind":"series","field":"volume","step":60},
    "delta": {"kind":"series","field":"delta","step":60},
    "osto": {"kind":"series","field":"buy_volume","step":60},
    "myynti": {"kind":"series","field":"sell_volume","step":60},
    "sigma15": {"kind":"sigma","source":"hinta","period":900,"count":96},
    "huippu4": {"kind":"window","source":"ylin","op":"max","seconds":14400},
    "pohja4": {"kind":"window","source":"alin","op":"min","seconds":14400},
    "huippu24": {"kind":"window","source":"ylin","op":"max","seconds":86400},
    "vol5": {"kind":"window","source":"vol","op":"sum","seconds":300},
    "volkorkea": {"kind":"percentile","source":"vol5","seconds":86400,"p":85},
    "virta5": {"kind":"window","source":"delta","op":"sum","seconds":300},
    "ostot5": {"kind":"window","source":"osto","op":"sum","seconds":300},
    "myynnit5": {"kind":"window","source":"myynti","op":"sum","seconds":300},
    "muutos5": {"kind":"window","source":"hinta","op":"log_change","seconds":300},
}


def ehto(ctx):
    if "hinta" not in ctx.uudet: return None
    hinta = ctx.palikat["hinta"]
    ylin = ctx.palikat["ylin"]
    alin = ctx.palikat["alin"]
    vol = ctx.palikat["vol"]
    delta = ctx.palikat["delta"]
    osto = ctx.palikat["osto"]
    myynti = ctx.palikat["myynti"]
    sigma15 = ctx.palikat["sigma15"]
    huippu4 = ctx.palikat["huippu4"]
    pohja4 = ctx.palikat["pohja4"]
    huippu24 = ctx.palikat["huippu24"]
    vol5 = ctx.palikat["vol5"]
    volkorkea = ctx.palikat["volkorkea"]
    virta5 = ctx.palikat["virta5"]
    ostot5 = ctx.palikat["ostot5"]
    myynnit5 = ctx.palikat["myynnit5"]
    muutos5 = ctx.palikat["muutos5"]
    if hinta is None or ylin is None or alin is None or vol is None or delta is None or osto is None or myynti is None or sigma15 is None or huippu4 is None or pohja4 is None or huippu24 is None or vol5 is None or volkorkea is None or virta5 is None or ostot5 is None or myynnit5 is None or muutos5 is None:
        return None
    if hinta <= 0 or sigma15 <= 0:
        return None
    leveys = huippu4 - pohja4
    lasku = (huippu24 - hinta) / hinta >= sigma15 * 4
    sivuttain = leveys > 0 and leveys / hinta <= sigma15 * ctx.luku("3") * ctx.luku(ctx.parameters["tiukkuus"])
    tila = lasku and sivuttain
    rakenne = hinta < pohja4 + leveys * ctx.luku('0.22') and vol5 > volkorkea and abs(virta5) < vol5 * ctx.luku('0.12') and muutos5 > 0 and ostot5 > 0 and myynnit5 > 0
    osuma = tila and rakenne
    return ctx.tulos(
        "Kaksipuolinen pohja" if osuma else None,
        conditions={"Laskun jalkeinen sivuttaistila": tila, "Suunnallinen rakenne": rakenne},
        direction="up" if osuma else None,
    )
