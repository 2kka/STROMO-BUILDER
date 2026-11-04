"""Nousun tasanteelta irtoaminen ▲ (kierros 3, R-stromo). Kortti: kortit/gpt/nousun_tasanteelta_irtoaminen.md"""

NIMI = "Nousun tasanteelta irtoaminen"
SELITYS = "Suuri 60 min nousu, lähes paikallaan pysyvä 15 min jakso ja uusi 3 min irtautuminen ylöspäin."
HYPOTEESI = "Tunninousun jälkeen hinta pysyy kapeassa 15 minuutin tuottoalueessa, mikä viittaa siihen ettei myynti paina hintaa takaisin. Kun uusi lyhyt nousu alkaa tasanteelta, seuraavan tunnin suunta on ylös; vain ▲."
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
    "nousu15": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 900,
    },
    "nousu3": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 180,
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
    "Tasanne, alaraja": {
        "palikka": "vertailu",
        "lahde": "nousu15",
        "operaattori": ">=",
        "raja": "-0.002",
        "tyyppi": "ehto",
    },
    "Tasanne, yläraja": {
        "palikka": "vertailu",
        "lahde": "nousu15",
        "operaattori": "<=",
        "raja": "0.002",
        "tyyppi": "ehto",
    },
    "Uusi lähtö ylös": {
        "palikka": "vertailu",
        "lahde": "nousu3",
        "operaattori": ">=",
        "raja": "0.0012",
        "suunta": "up",
        "tyyppi": "ehto",
        "paa": True,
    },
}
