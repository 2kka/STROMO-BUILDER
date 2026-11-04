"""UTC-päivänvaihteen osallistuminen ▲ (kierros 2, R-stromo). Kortti: kortit/gpt/utc_paivanvaihteen_osallistuminen.md"""

NIMI = "UTC-päivänvaihteen osallistuminen"
SELITYS = "Uuden UTC-päivän alkuikkunassa 5 min nousu ja vähintään tavallinen kauppamäärä."
HYPOTEESI = (
    "UTC-vuorokauden vaihde on yhteinen aikaraja, jolla osa järjestelmistä ajoittaa eriä; nouseva hinta "
    "ja tavallinen osallistuminen alkuikkunassa saattavat tukea lyhyttä jatkoa ylöspäin. Vain ▲."
)
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"]},
    "cooldown_seconds": {"type": "integer", "default": 86400, "min": 0, "max": 86400},
    "alkuikkuna_min": {"type": "enum", "default": "30", "choices": ["20", "30", "40"], "label": "Alkuikkuna min"},
}
TARVITSEE = {
    "close": {"kind": "series", "field": "close", "step": 60},
    "lr5": {"kind": "window", "source": "close", "op": "log_change", "seconds": 300},
    "n": {"kind": "series", "field": "count", "step": 60},
    "n5": {"kind": "window", "source": "n", "op": "sum", "seconds": 300},
    "n5_p50": {"kind": "percentile", "source": "n5", "seconds": 86400, "p": "50"},
}
EHDOT = {
    "UTC-päivänvaihde": {
        "palikka": "aikaikkunan_alue",
        "alku": "00:00",
        "aikavyohyke": "UTC",
        "paivat": "kaikki",
        "pituus_min": 0,
        "voimassa_min": "$alkuikkuna_min",
        "suunta": "up",
        "tyyppi": "ehto",
        "paa": True,
    },
    "Hinta ylöspäin": {
        "palikka": "vertailu",
        "lahde": "lr5",
        "operaattori": ">",
        "raja": "0",
        "suunta": "up",
    },
    "Kaupat osallistuvat": {
        "palikka": "vertailu",
        "lahde": "n5",
        "operaattori": ">=",
        "vastaan": "n5_p50",
    },
}
