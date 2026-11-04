"""Kauppatiheyden nousuliike ▲ (kierros 3, R-stromo). Kortti: kortit/gpt/kauppatiheyden_ostoliike.md"""

NIMI = "Kauppatiheyden nousuliike"
SELITYS = "Viiden minuutin kauppamäärä oman vuorokausijakauman ylähännässä ja 15 min positiivinen hintaliike."
HYPOTEESI = "Poikkeuksellisen monen erillisen kaupan hetkellä positiivinen 15 minuutin hintamuutos voi kertoa laajan osallistujajoukon uudesta hinnanhyväksynnästä. Kauppojen lukumäärän ja hinnan samanaikainen siirtymä ennakoi nousua seuraavan tunnin aikana; vain ▲."
PARAMETRIT = {
    "exchange": {
        "type": "enum",
        "default": "okx",
        "choices": ["okx"],
    },
    "instrument": {
        "type": "enum",
        "default": "BTC-USDT",
        "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"],
    },
    "cooldown_seconds": {
        "type": "integer",
        "default": 5400,
        "min": 0,
        "max": 86400,
    },
    "vauhti15": {
        "type": "enum",
        "default": "0.003",
        "choices": ["0.002", "0.003", "0.004"],
        "label": "15 min nousun log-raja",
    },
}
TARVITSEE = {
    "close": {
        "kind": "series",
        "field": "close",
        "step": 60,
    },
    "nousu15": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 900,
    },
    "count": {
        "kind": "series",
        "field": "count",
        "step": 60,
    },
    "count5": {
        "kind": "window",
        "source": "count",
        "op": "sum",
        "seconds": 300,
    },
    "countp90": {
        "kind": "percentile",
        "source": "count5",
        "seconds": 86400,
        "p": "90",
    },
}
EHDOT = {
    "15 min nousuliike": {
        "palikka": "vertailu",
        "lahde": "nousu15",
        "operaattori": ">=",
        "raja": "$vauhti15",
        "suunta": "up",
        "tyyppi": "ehto",
        "paa": True,
    },
    "Kauppojen huippulukumäärä": {
        "palikka": "vertailu",
        "lahde": "count5",
        "operaattori": ">=",
        "vastaan": "countp90",
        "tyyppi": "ehto",
    },
}
