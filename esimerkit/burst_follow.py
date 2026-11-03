"""Testiesimerkki: sekunnin kauppapurske ja 50 % palautumisen seuranta."""

NIMI = "Sekuntipurske ja paluu"
SELITYS = "Kauppamääräpurskeen jälkeen odotetaan hinnan palautumista."
EHDOT = ("Purske", "Paluu")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-EUR", "choices": ["BTC-EUR"]},
    "cooldown_seconds": {"type": "integer", "default": 60, "min": 0, "max": 86400},
    "purske": {"type": "integer", "default": 3, "min": 1, "max": 100000},
    "vertailu": {"type": "integer", "default": 60, "min": 1, "max": 86400},
    "odotus": {"type": "integer", "default": 60, "min": 1, "max": 86400},
    "paluuosuus": {"type": "number", "default": "0.5", "min": "0", "max": "1"},
}
TARVITSEE = {
    "maara": {"kind": "series", "field": "count", "step": 1},
    "hinta": {"kind": "series", "field": "close", "step": 1},
    "huippu": {"kind": "series", "field": "high", "step": 1},
    "pohja": {"kind": "window", "source": "hinta", "op": "min", "seconds": "$vertailu"},
    "paluu": {"kind": "follow", "seconds": "$odotus"},
}


def ehto(ctx):
    tapahtuma = "maara" in ctx.uudet and ctx.palikat["maara"] >= ctx.parameters["purske"]
    tavoite = ctx.state.get("tavoite", 0)
    seuranta = ctx.seuraa("paluu", tapahtuma, ctx.price <= tavoite)
    if seuranta.started_ms == ctx.timestamp_ms:
        huippu = ctx.palikat["huippu"]
        tavoite = huippu - (huippu - ctx.palikat["pohja"]) * ctx.luku(ctx.parameters["paluuosuus"])
    return ctx.tulos(
        "Purske palautui" if seuranta.value is True else None,
        conditions={"Purske": tapahtuma, "Paluu": seuranta.value},
        state={"paluu": seuranta.state, "tavoite": tavoite},
        direction="down",
    )
