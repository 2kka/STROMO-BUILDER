"""Alueen keskikohdan palautus, kaksisuuntainen (kierros 2, R-stromo). Kortti: kortit/gpt/alueen_keskikohdan_palautus.md"""

NIMI = "Alueen keskikohdan ylitys"
SELITYS = "1 min sulku ylittää edeltävän 45–90 min alueen keskipisteen ilman volyymiryöppyä."
HYPOTEESI = (
    "Lyhyen kaupankäyntialueen toiseen laitaan jäänyt hinta palaa kohti alueen keskikohtaa ja yli sen "
    "rauhallisella volyymilla: alueen sisäinen uudelleenhinnoittelu ilman yksittäistä impulssia. "
    "Molemmat suunnat; volyymille yläraja."
)
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"]},
    "cooldown_seconds": {"type": "integer", "default": 7200, "min": 0, "max": 86400},
    "alue_s": {"type": "enum", "default": "3600", "choices": ["2700", "3600", "5400"], "label": "Alue s"},
}
TARVITSEE = {
    "v": {"kind": "series", "field": "volume", "step": 60},
    "v5": {"kind": "window", "source": "v", "op": "sum", "seconds": 300},
    "v5_p75": {"kind": "percentile", "source": "v5", "seconds": 86400, "p": "75"},
}
EHDOT = {
    "Keskipisteen ylitys": {
        "palikka": "alueen_keskipisteen_ylitys",
        "alue_s": "$alue_s",
        "suunta": None,
        "tyyppi": "tapahtuma",
        "voimassa_s": 120,
        "paa": True,
    },
    "Ei volyymiryöppyä": {
        "palikka": "vertailu",
        "lahde": "v5",
        "operaattori": "<=",
        "vastaan": "v5_p75",
    },
}
