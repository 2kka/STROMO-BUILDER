"""Kopioi uudeksi tiedostoksi kansioon stromot/<tekijä>/ ja muokkaa."""

NIMI = "Volyymi-ikkuna (malli)"
SELITYS = "Hälyttää sulkeutuneen volyymi-ikkunan ylittäessä parametrikynnyksen."
EHDOT = ("Volyymi",)
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {
        "type": "enum",
        "default": "BTC-EUR",
        "choices": ["BTC-EUR", "BTC-USDT", "BTC-USDC"],
    },
    "cooldown_seconds": {"type": "integer", "default": 60, "min": 0, "max": 86400},
    "ikkuna": {"type": "integer", "default": 10, "min": 1, "max": 86400},
    "kynnys": {"type": "number", "default": "1", "min": "0", "max": "10000"},
}
TARVITSEE = {
    "volyymi": {"kind": "series", "field": "volume", "step": 1},
    "summa": {"kind": "window", "source": "volyymi", "op": "sum", "seconds": "$ikkuna"},
}


def ehto(ctx):
    if "summa" not in ctx.uudet:
        return None
    osuma = ctx.palikat["summa"] > ctx.luku(ctx.parameters["kynnys"])
    return ctx.tulos("Volyymi ylittää kynnyksen" if osuma else None, conditions={"Volyymi": osuma})
