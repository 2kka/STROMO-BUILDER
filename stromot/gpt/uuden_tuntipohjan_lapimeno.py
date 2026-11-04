"""Uuden tuntipohjan läpimeno ▼ (kierros 3, R-stromo). Kortti: kortit/gpt/uuden_tuntipohjan_lapimeno.md"""

NIMI = "Uuden tuntipohjan läpimeno"
SELITYS = "Uusi 60 min alin päätöshinta, aleneva 5 min tuotto ja korkea kauppatapahtumien määrä."
HYPOTEESI = "Kun uusi tunnin alin päätöshinta syntyy lyhyen laskun ja runsaan kaupankäynnin aikana, alemman hinnan hyväksyntä voi jatkua seuraavaan tuntiin. Laskun jatkuminen vaatii hinnan uuden vähimmäistason lisäksi laajaa osallistumista; vain ▼."
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
    "lasku5": {
        "type": "enum",
        "default": "-0.002",
        "choices": ["-0.0015", "-0.002", "-0.0025"],
        "label": "5 min laskun log-raja",
    },
}
TARVITSEE = {
    "close": {
        "kind": "series",
        "field": "close",
        "step": 60,
    },
    "tuntipohja": {
        "kind": "window",
        "source": "close",
        "op": "min",
        "seconds": 3600,
    },
    "lasku5": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 300,
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
    "countp80": {
        "kind": "percentile",
        "source": "count5",
        "seconds": 86400,
        "p": "80",
    },
}
EHDOT = {
    "Uusi 60 min pohjasulku": {
        "palikka": "vertailu",
        "lahde": "close",
        "operaattori": "<=",
        "vastaan": "tuntipohja",
        "suunta": "down",
        "tyyppi": "tapahtuma",
        "voimassa_s": 300,
        "paa": True,
    },
    "Lyhyt lasku": {
        "palikka": "vertailu",
        "lahde": "lasku5",
        "operaattori": "<=",
        "raja": "$lasku5",
        "tyyppi": "ehto",
    },
    "Osallistuminen korkea": {
        "palikka": "vertailu",
        "lahde": "count5",
        "operaattori": ">=",
        "vastaan": "countp80",
        "tyyppi": "ehto",
    },
}
