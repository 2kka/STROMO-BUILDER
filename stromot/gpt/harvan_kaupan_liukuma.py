"""Harvan kaupan hintaliukuma ▼ (kierros 3, R-stromo). Kortti: kortit/gpt/harvan_kaupan_liukuma.md"""

NIMI = "Harvan kaupan hintaliukuma"
SELITYS = "Vähintään määritelty 5 min hinnanlasku, vähäinen kauppatapahtumien määrä ja laskeva 30 min tausta."
HYPOTEESI = "Jos hinta liukuu alaspäin vähillä erillisillä kaupoilla ja pidempi puolen tunnin suunta on jo negatiivinen, hintatasoja voi jäädä ilman aktiivista vastakysyntää. Tällainen harvan kaupankäynnin lasku voi jatkua seuraavan tunnin aikana; vain ▼."
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
    "liukuma5": {
        "type": "enum",
        "default": "-0.0025",
        "choices": ["-0.002", "-0.0025", "-0.003"],
        "label": "5 min liukuman log-raja",
    },
}
TARVITSEE = {
    "close": {
        "kind": "series",
        "field": "close",
        "step": 60,
    },
    "lasku5": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 300,
    },
    "lasku30": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 1800,
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
    "countp25": {
        "kind": "percentile",
        "source": "count5",
        "seconds": 86400,
        "p": "25",
    },
}
EHDOT = {
    "Harvan kaupan 5 min lasku": {
        "palikka": "vertailu",
        "lahde": "lasku5",
        "operaattori": "<=",
        "raja": "$liukuma5",
        "suunta": "down",
        "tyyppi": "ehto",
        "paa": True,
    },
    "Harva kaupankäynti": {
        "palikka": "vertailu",
        "lahde": "count5",
        "operaattori": "<=",
        "vastaan": "countp25",
        "tyyppi": "ehto",
    },
    "Laskeva tausta": {
        "palikka": "vertailu",
        "lahde": "lasku30",
        "operaattori": "<=",
        "raja": "-0.003",
        "tyyppi": "ehto",
    },
}
