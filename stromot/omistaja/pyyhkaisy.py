"""Pyyhkäisy – lukittu määritelmä 2.11.2026 (1.B'). Ei säädetä tulosten perusteella."""

NIMI = "Pyyhkäisy"
SELITYS = (
    "Sekunnin aggressiivinen purske: saman puolen volyymi ≥ oman puolensa 24 h p99,9 "
    "ja hinta liikkuu purskeen suuntaan ≥ 0,5σ15. Jos hinta palaa ≥ 50 % liikkeestä "
    "60 s:ssa → hälytys vastakkaiseen suuntaan; muuten 60 s kohdalla purskeen suuntaan."
)
EHDOT = ("Purske", "Liike", "Seuranta")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {
        "type": "enum",
        "default": "BTC-USDT",
        "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"],
    },
    "cooldown_seconds": {"type": "integer", "default": 900, "min": 0, "max": 86400},
    "persentiili": {
        "type": "enum",
        "default": "99.9",
        "choices": ["99.9", "99.5"],
        "label": "Purskeraja (24 h persentiili)",
    },
    "liike_sigma": {
        "type": "number", "default": "0.5", "min": "0", "max": "10", "label": "Liike × σ15",
    },
    "paluuosuus": {
        "type": "number", "default": "0.5", "min": "0", "max": "1", "label": "Paluuosuus",
    },
    "odotus": {"type": "integer", "default": 60, "min": 1, "max": 3600, "label": "Seuranta s"},
}
TARVITSEE = {
    "osto": {"kind": "series", "field": "buy_volume", "step": 1},
    "myynti": {"kind": "series", "field": "sell_volume", "step": 1},
    "hinta": {"kind": "series", "field": "close", "step": 1},
    "osto_raja": {"kind": "percentile", "source": "osto", "seconds": 86400, "p": "$persentiili"},
    "myynti_raja": {
        "kind": "percentile", "source": "myynti", "seconds": 86400, "p": "$persentiili",
    },
    "muutos": {"kind": "window", "source": "hinta", "op": "change", "seconds": 1},
    "lmuutos": {"kind": "window", "source": "hinta", "op": "log_change", "seconds": 1},
    "minuutti": {"kind": "series", "field": "close", "step": 60},
    "sigma15": {"kind": "sigma", "source": "minuutti", "period": 900, "count": 96},
    "paluu": {"kind": "follow", "seconds": "$odotus"},
}


def ehto(ctx):
    uusi = "osto_raja" in ctx.uudet
    raja = ctx.luku(ctx.parameters["liike_sigma"]) * ctx.palikat["sigma15"]
    osto = ctx.palikat["osto"]
    myynti = ctx.palikat["myynti"]
    ostopurske = uusi and osto > 0 and osto >= ctx.palikat["osto_raja"]
    myyntipurske = uusi and myynti > 0 and myynti >= ctx.palikat["myynti_raja"]
    ylos = ostopurske and ctx.palikat["lmuutos"] >= raja
    alas = myyntipurske and not ylos and -ctx.palikat["lmuutos"] >= raja
    tapahtuma = ylos or alas

    suunta = ctx.state.get("suunta")
    tavoite = ctx.state.get("tavoite")
    palasi = False
    if suunta == "up" and tavoite is not None:
        palasi = ctx.price <= tavoite
    if suunta == "down" and tavoite is not None:
        palasi = ctx.price >= tavoite

    seuranta = ctx.seuraa("paluu", tapahtuma, palasi)
    viesti = None
    hsuunta = None
    if seuranta.value is True:
        hsuunta = "down" if suunta == "up" else "up"
        viesti = f"Pyyhkäisy palautui ≥ paluuosuuden {ctx.parameters['odotus']} s:ssa → vastaan"
    if seuranta.value is False:
        hsuunta = suunta
        viesti = f"Pyyhkäisy ei palannut {ctx.parameters['odotus']} s:ssa → purskeen suuntaan"
    if seuranta.started_ms == ctx.timestamp_ms:
        # Uusi seuranta: palautumistaso purskesekunnin päätöksestä, ei tulevasta hinnasta.
        suunta = "up" if ylos else "down"
        tavoite = ctx.palikat["hinta"] - ctx.palikat["muutos"] * ctx.luku(
            ctx.parameters["paluuosuus"]
        )

    return ctx.tulos(
        viesti,
        conditions={
            "Purske": ostopurske or myyntipurske,
            "Liike": tapahtuma,
            "Seuranta": seuranta.started_ms is not None,
        },
        state={"paluu": seuranta.state, "suunta": suunta, "tavoite": tavoite},
        direction=hsuunta,
    )
