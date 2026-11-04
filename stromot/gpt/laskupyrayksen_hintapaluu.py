"""Laskupyrähdyksen hintapaluu ▲ (kierros 3, R-stromo). Kortti: kortit/gpt/laskupyrayksen_hintapaluu.md"""

NIMI = "Laskupyrähdyksen hintapaluu"
SELITYS = "Selkeä 30 min laskutapahtuma ja sitä seuraava vähintään 0,2 %:n viiden minuutin hintapaluu."
HYPOTEESI = "Terävän 30 minuutin laskun jälkeen jo pienikin vastakkaissuuntainen hintapaluu voi osoittaa, että uusi ostohinta hyväksytään nopeasti. Pelkkään hinnan ylilyöntiin ja palautuksen alkuun perustuva signaali ennakoi nousua seuraavan tunnin aikana; vain ▲."
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
    "laskuraja": {
        "type": "enum",
        "default": "-0.008",
        "choices": ["-0.006", "-0.008", "-0.010"],
        "label": "30 min laskun log-raja",
    },
}
TARVITSEE = {
    "close": {
        "kind": "series",
        "field": "close",
        "step": 60,
    },
    "lasku30": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 1800,
    },
    "paluu5": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 300,
    },
}
EHDOT = {
    "Terävä 30 min lasku": {
        "palikka": "vertailu",
        "lahde": "lasku30",
        "operaattori": "<=",
        "raja": "$laskuraja",
        "tyyppi": "tapahtuma",
        "voimassa_s": 1800,
    },
    "Viiden minuutin hintapaluu": {
        "palikka": "vertailu",
        "lahde": "paluu5",
        "operaattori": ">=",
        "raja": "0.002",
        "suunta": "up",
        "tyyppi": "ehto",
        "paa": True,
    },
}
