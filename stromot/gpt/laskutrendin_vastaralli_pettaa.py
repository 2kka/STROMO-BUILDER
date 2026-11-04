"""Laskutrendin vastaralli pettää ▼ (kierros 3, R-stromo). Kortti: kortit/gpt/laskutrendin_vastaralli_pettaa.md"""

NIMI = "Laskutrendin vastaralli pettää"
SELITYS = "120 min laskutrendi, 10 min vastaralli ja sen sisäinen 3 min uusi lasku."
HYPOTEESI = "Kahden tunnin laskevassa hintarakenteessa lyhyt myönteinen vastaralli voi houkutella ennenaikaisia ostajia, mutta sen sisällä alkava uusi 3 minuutin lasku palauttaa aiemman suunnan. Vastaliikkeen katkeaminen ennakoi laskua seuraavan tunnin aikana; vain ▼."
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
    "taustalasku": {
        "type": "enum",
        "default": "-0.010",
        "choices": ["-0.008", "-0.010", "-0.012"],
        "label": "120 min taustalaskun log-raja",
    },
}
TARVITSEE = {
    "close": {
        "kind": "series",
        "field": "close",
        "step": 60,
    },
    "lasku120": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 7200,
    },
    "ralli10": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 600,
    },
    "uusi_lasku3": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 180,
    },
}
EHDOT = {
    "Pitkä laskutausta": {
        "palikka": "vertailu",
        "lahde": "lasku120",
        "operaattori": "<=",
        "raja": "$taustalasku",
        "tyyppi": "tapahtuma",
        "voimassa_s": 1800,
    },
    "Vastaralli yhä näkyvissä": {
        "palikka": "vertailu",
        "lahde": "ralli10",
        "operaattori": ">=",
        "raja": "0.002",
        "tyyppi": "ehto",
    },
    "Vastaralli pettää": {
        "palikka": "vertailu",
        "lahde": "uusi_lasku3",
        "operaattori": "<=",
        "raja": "-0.001",
        "suunta": "down",
        "tyyppi": "ehto",
        "paa": True,
    },
}
