"""Nousun nopea vastaisku ▼ (kierros 3, R-stromo). Kortti: kortit/gpt/nousun_nopea_vastaisku.md"""

NIMI = "Nousun nopea vastaisku"
SELITYS = "Suuri 60 min nousu ja vähintään 0,3 %:n kolmen minuutin vastaliike vilkastuvalla kauppamäärällä."
HYPOTEESI = "Nousupyrähdyksen jälkeen aggressiivinen kaupankäynti voi siirtyä nopeasti alemmille hinnoille, mikä näkyy kolmen minuutin hintaiskuna ja kauppatapahtumien tihentymisenä. Välitön hintapaluu ennakoi laskua seuraavan tunnin aikana; vain ▼."
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
    "nousu3": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 180,
    },
    "count": {
        "kind": "series",
        "field": "count",
        "step": 60,
    },
    "count3": {
        "kind": "window",
        "source": "count",
        "op": "mean",
        "seconds": 180,
    },
    "count30": {
        "kind": "window",
        "source": "count",
        "op": "mean",
        "seconds": 1800,
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
    "Kolmen minuutin vastaisku": {
        "palikka": "vertailu",
        "lahde": "nousu3",
        "operaattori": "<=",
        "raja": "-0.003",
        "suunta": "down",
        "tyyppi": "ehto",
        "paa": True,
    },
    "Kaupat tihenevät": {
        "palikka": "vertailu",
        "lahde": "count3",
        "operaattori": ">",
        "vastaan": "count30",
        "tyyppi": "ehto",
    },
}
