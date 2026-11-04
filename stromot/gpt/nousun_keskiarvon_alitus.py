"""Nousun lyhyen keskihinnan alitus ▼ (kierros 3, R-stromo). Kortti: kortit/gpt/nousun_keskiarvon_alitus.md"""

NIMI = "Nousun lyhyen keskihinnan alitus"
SELITYS = "Suuri 60 min nousu, 15 min laskeva nettotuotto ja sulku 15 min päätöskeskiarvon alapuolella."
HYPOTEESI = "Jos nousun jälkeen viimeisen 15 minuutin päätöshintojen keskiarvo menetetään ja 15 minuutin nettotuotto on negatiivinen, aiemman nousun jälkeinen tasapaino on siirtynyt alemmas. Tämän hitaamman rakenteellisen menetyksen pitäisi ennakoida laskua seuraavan tunnin aikana; vain ▼."
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
    "nousuraja": {
        "type": "enum",
        "default": "0.008",
        "choices": ["0.006", "0.008", "0.010"],
        "label": "60 min suuren nousun log-raja",
    },
}
TARVITSEE = {
    "close": {
        "kind": "series",
        "field": "close",
        "step": 60,
    },
    "nousu60": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 3600,
    },
    "keski15": {
        "kind": "window",
        "source": "close",
        "op": "mean",
        "seconds": 900,
    },
    "nousu15": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 900,
    },
}
EHDOT = {
    "Yhteinen suuri nousu 60 min": {
        "palikka": "vertailu",
        "lahde": "nousu60",
        "operaattori": ">=",
        "raja": "$nousuraja",
        "tyyppi": "tapahtuma",
        "voimassa_s": 1800,
    },
    "Lyhyt keskihinta menetettiin": {
        "palikka": "vertailu",
        "lahde": "close",
        "operaattori": "<",
        "vastaan": "keski15",
        "suunta": "down",
        "tyyppi": "ehto",
        "paa": True,
    },
    "Viidentoista minuutin lasku": {
        "palikka": "vertailu",
        "lahde": "nousu15",
        "operaattori": "<=",
        "raja": "-0.002",
        "tyyppi": "ehto",
    },
}
