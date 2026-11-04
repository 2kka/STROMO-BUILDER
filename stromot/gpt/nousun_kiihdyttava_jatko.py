"""Nousun kiihtyvä jatko ▲ (kierros 3, R-stromo). Kortti: kortit/gpt/nousun_kiihdyttava_jatko.md"""

NIMI = "Nousun kiihtyvä jatko"
SELITYS = "Suuri 60 min nousu, jota seuraa ripeä 10 min nousu ja minuuttivolyymin vahvistuminen."
HYPOTEESI = "Voimakkaan tunninousun jälkeen välittömän ostokysynnän vahvistuminen näkyy yhtä aikaa uudessa kymmenen minuutin hinnannousussa ja kauppavolyymin kiihtymisessä. Jälkiliike jatkuu ylöspäin seuraavan 60 minuutin aikana; vain ▲."
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
    "nousu10": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 600,
    },
    "vol": {
        "kind": "series",
        "field": "volume",
        "step": 60,
    },
    "vol5": {
        "kind": "window",
        "source": "vol",
        "op": "mean",
        "seconds": 300,
    },
    "vol60": {
        "kind": "window",
        "source": "vol",
        "op": "mean",
        "seconds": 3600,
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
    "Kymmenen minuutin lisänousu": {
        "palikka": "vertailu",
        "lahde": "nousu10",
        "operaattori": ">=",
        "raja": "0.003",
        "suunta": "up",
        "tyyppi": "ehto",
        "paa": True,
    },
    "Volyymi kiihtyy": {
        "palikka": "vertailu",
        "lahde": "vol5",
        "operaattori": ">",
        "vastaan": "vol60",
        "tyyppi": "ehto",
    },
}
