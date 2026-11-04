"""Peräkkäisten sulkujen askellus, kaksisuuntainen (kierros 2, R-stromo). Kortti: kortit/gpt/kolmen_sulun_askellus.md"""

NIMI = "Peräkkäisten sulkujen askellus"
SELITYS = "2–4 peräkkäistä samansuuntaista minuuttisulkua ja tavallista vilkkaampi kaupankäynti."
HYPOTEESI = (
    "Hitaasti toimiva osallistuja jakaa toimeksiantonsa useaan minuuttierään; peräkkäiset samansuuntaiset "
    "sulut vilkkaalla kauppamäärällä jatkuvat ilman yksittäistä hyppyä. Molemmat suunnat."
)
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"]},
    "cooldown_seconds": {"type": "integer", "default": 5400, "min": 0, "max": 86400},
    "askellus_s": {"type": "enum", "default": "180", "choices": ["120", "180", "240"], "label": "Askellus s"},
}
TARVITSEE = {
    "n": {"kind": "series", "field": "count", "step": 60},
    "n_sum": {"kind": "window", "source": "n", "op": "sum", "seconds": "$askellus_s"},
    "n_p70": {"kind": "percentile", "source": "n_sum", "seconds": 86400, "p": "70"},
}
EHDOT = {
    "Askellus": {
        "palikka": "perakkaiset_sulut",
        "ikkuna_s": "$askellus_s",
        "suunta": None,
        "tyyppi": "tapahtuma",
        "voimassa_s": 60,
        "paa": True,
    },
    "Osallistuminen": {
        "palikka": "vertailu",
        "lahde": "n_sum",
        "operaattori": ">=",
        "vastaan": "n_p70",
    },
}
