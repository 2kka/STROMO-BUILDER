"""Matalan sigman nousupurkaus ▲ (kierros 3, R-stromo). Kortti: kortit/gpt/matalan_sigman_purkaus.md"""

NIMI = "Matalan sigman nousupurkaus"
SELITYS = "Vuorokauden omaan jakaumaan nähden pieni σ15 sekä vähintään määritelty 5 min nousu."
HYPOTEESI = "Pitkään rauhallisena pysyneessä hintaympäristössä uusi viiden minuutin nousu voi kertoa uuden hinnanasettajan ilmaantumisesta ennen kuin muut ehtivät mukaan. Purkaus jatkuu ylöspäin seuraavan tunnin aikana; vain ▲."
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
    "purkaus": {
        "type": "enum",
        "default": "0.003",
        "choices": ["0.002", "0.003", "0.004"],
        "label": "5 min nousupurkauksen log-raja",
    },
}
TARVITSEE = {
    "close": {
        "kind": "series",
        "field": "close",
        "step": 60,
    },
    "sigma15": {
        "kind": "sigma",
        "source": "close",
    },
    "sigmap25": {
        "kind": "percentile",
        "source": "sigma15",
        "seconds": 86400,
        "p": "25",
    },
    "nousu5": {
        "kind": "window",
        "source": "close",
        "op": "log_change",
        "seconds": 300,
    },
}
EHDOT = {
    "Viiden minuutin purkaus": {
        "palikka": "vertailu",
        "lahde": "nousu5",
        "operaattori": ">=",
        "raja": "$purkaus",
        "suunta": "up",
        "tyyppi": "ehto",
        "paa": True,
    },
    "Matala suhteellinen sigma": {
        "palikka": "vertailu",
        "lahde": "sigma15",
        "operaattori": "<=",
        "vastaan": "sigmap25",
        "tyyppi": "ehto",
    },
}
