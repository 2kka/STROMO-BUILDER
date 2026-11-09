"""Hypoteesi: Neljän tunnin nousu saa avauksessa lisää aggressiivisia ostoja, mutta hinta ei nouse.
Mekanismi: Passiiviset myyjät ottavat avausostot vastaan. Ostojen huono hinnansiirtokyky voi muuttaa myöhäiset ostajat myyjiksi.
Odotettu suunta: down.
Miksi ei pelkka volatiliteetin tunnistin: Vertaa avauksen aggressiivista ostovirtaa hinnan liikkumattomuuteen.
Mika kumoaisi: 3A-reuna alittaa LIIGAn kynnyksen tai naapurivariantin reuna ei ole positiivinen.
"""

NIMI = "USA osto ei kanna"
SELITYS = "Neljän tunnin nousu saa avauksessa lisää aggressiivisia ostoja, mutta hinta ei nouse."
EHDOT = ("Ennakkotrendi", "Avausvahvistus")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT"]},
    "cooldown_seconds": {"type": "integer", "default": 72000, "min": 0, "max": 86400},
    "kireys": {"type": "enum", "default": "1", "choices": ["1", "1.2"]},
}
TARVITSEE = {
    "hinta": {"kind":"series","field":"close","step":60},
    "ylin": {"kind":"series","field":"high","step":60},
    "alin": {"kind":"series","field":"low","step":60},
    "delta": {"kind":"series","field":"delta","step":60},
    "vol": {"kind":"series","field":"volume","step":60},
    "tuotto4": {"kind":"window","source":"hinta","op":"log_change","seconds":14400},
    "tuotto1": {"kind":"window","source":"hinta","op":"log_change","seconds":3600},
    "sigma15": {"kind":"sigma","source":"hinta","period":900,"count":96},
    "huippu1": {"kind":"window","source":"ylin","op":"max","seconds":3600},
    "pohja1": {"kind":"window","source":"alin","op":"min","seconds":3600},
    "vol5": {"kind":"window","source":"vol","op":"sum","seconds":300},
    "virta5": {"kind":"window","source":"delta","op":"sum","seconds":300},
    "vol10": {"kind":"window","source":"vol","op":"sum","seconds":600},
    "virta10": {"kind":"window","source":"delta","op":"sum","seconds":600},
}


def ehto(ctx):
    if "hinta" not in ctx.uudet: return None
    loppu = ctx.ajat["hinta"]
    paiva = int(loppu / 86400000)
    viikonpaiva = (paiva + 4) % 7
    if viikonpaiva == 0 or viikonpaiva == 6:
        return None
    # Gregoriaaninen paivays ilman kellokirjastoa.
    z = paiva + 719468
    era = int(z / 146097)
    doe = z - era * 146097
    yoe = int((doe - int(doe / 1460) + int(doe / 36524) - int(doe / 146096)) / 365)
    doy = doe - (365 * yoe + int(yoe / 4) - int(yoe / 100))
    mp = int((5 * doy + 2) / 153)
    kuukausi = mp + (3 if mp < 10 else -9)
    pv = doy - int((153 * mp + 2) / 5) + 1
    ekaviikko = (viikonpaiva - (pv - 1) % 7) % 7
    ekasunnuntai = 1 + (7 - ekaviikko) % 7
    kesa = (3 < kuukausi < 11 or
            (kuukausi == 3 and pv >= ekasunnuntai + 7) or
            (kuukausi == 11 and pv < ekasunnuntai))
    avaus = 810 if kesa else 870
    hetki = int((loppu % 86400000) / 60000) - avaus
    if hetki < 0 or hetki > 30:
        return None
    hinta = ctx.palikat["hinta"]
    if hinta is None or hinta <= 0:
        return None
    if hetki == 0:
        if ctx.palikat["hinta"] is None or ctx.palikat["tuotto4"] is None or ctx.palikat["tuotto1"] is None or ctx.palikat["sigma15"] is None or ctx.palikat["huippu1"] is None or ctx.palikat["pohja1"] is None or ctx.palikat["vol5"] is None:
            return None
        if ctx.palikat["sigma15"] <= 0:
            return None
        return ctx.tulos(state={
            "paiva": paiva,
            "nelja": ctx.palikat["tuotto4"],
            "tunti": ctx.palikat["tuotto1"],
            "viite": hinta,
            "sigma": ctx.palikat["sigma15"],
            "huippu": ctx.palikat["huippu1"],
            "pohja": ctx.palikat["pohja1"],
            "prevol": ctx.palikat["vol5"],
            "alaisin": hinta,
            "ylinavaus": hinta,
        })
    if ctx.state.get("paiva") != paiva:
        return None
    alin = ctx.palikat["alin"]
    ylin = ctx.palikat["ylin"]
    if alin is None or ylin is None:
        return None
    nelja = ctx.state.get("nelja")
    tunti = ctx.state.get("tunti")
    viite = ctx.state.get("viite")
    sigma = ctx.state.get("sigma")
    pohja = ctx.state.get("pohja")
    huippu = ctx.state.get("huippu")
    prevol = ctx.state.get("prevol")
    sessiomin = min(ctx.state.get("alaisin", viite), alin)
    sessiomax = max(ctx.state.get("ylinavaus", viite), ylin)
    tila = {
        "paiva": paiva, "nelja": nelja, "tunti": tunti,
        "viite": viite, "sigma": sigma, "pohja": pohja, "huippu": huippu,
        "prevol": prevol, "alaisin": sessiomin, "ylinavaus": sessiomax,
    }
    if hetki < 10 or hetki > 25:
        return ctx.tulos(state=tila)
    vol5 = ctx.palikat["vol5"]
    virta5 = ctx.palikat["virta5"]
    if vol5 is None or virta5 is None:
        return ctx.tulos(state=tila)
    vol10 = ctx.palikat["vol10"]
    virta10 = ctx.palikat["virta10"]
    if vol10 is None or virta10 is None:
        return ctx.tulos(state=tila)
    k = ctx.luku(ctx.parameters["kireys"])
    ennakko = nelja >= sigma * k and tunti >= sigma * k * ctx.luku('0.35')
    vahvistus = virta10 > vol10 * ctx.luku('0.22') and hinta < viite * (1 + sigma * ctx.luku('0.04')) and sessiomax < viite * (1 + sigma * ctx.luku('0.20'))
    osuma = ennakko and vahvistus
    return ctx.tulos(
        "USA osto ei kanna" if osuma else None,
        conditions={"Ennakkotrendi": ennakko, "Avausvahvistus": vahvistus},
        state=tila,
        direction="down" if osuma else None,
    )
