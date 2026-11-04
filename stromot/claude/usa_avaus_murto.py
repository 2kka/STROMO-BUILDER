"""USA:n avauksen alueen murto (kierros 2, R-stromo). Kortti: kortit/claude/usa_avauksen_alueen_murto.md"""

NIMI = "USA:n avauksen alueen murto"
SELITYS = "Ensimmäinen 1 min sulku USA:n avauksen alueen ulkopuolella, kun 5 min delta tukee suuntaa."
HYPOTEESI = (
    "USA:n osakemarkkinan avaus (9.30 New York) tuo BTC:hen päivän suurimman uuden osallistujajoukon; "
    "kun hinta sulkeutuu avausalueen ulkopuolelle ja aggressiivinen virta tukee suuntaa, liike jatkuu "
    "seuraavan tunnin. Molemmat suunnat; kapea alue suodatetaan."
)
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"]},
    "cooldown_seconds": {"type": "integer", "default": 3600, "min": 0, "max": 86400},
    "alue_min": {"type": "enum", "default": "30", "choices": ["15", "30", "60"], "label": "Avausalue min"},
}
TARVITSEE = {
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "delta5": {"kind": "window", "source": "delta", "op": "sum", "seconds": 300},
}
EHDOT = {
    "Avausalueen murto": {
        "palikka": "aikaikkunan_alue",
        "alku": "09:30",
        "aikavyohyke": "America/New_York",
        "paivat": "ma-pe",
        "paivat_kalenteri": "nyse",
        "pituus_min": "$alue_min",
        "voimassa_min": 180,
        "min_leveys_sigma": "0.5",
        "suunta": None,
        "tyyppi": "tapahtuma",
        "voimassa_s": 60,
        "paa": True,
    },
    "Virta tukee": {
        "palikka": "vertailu",
        "lahde": "delta5",
        "operaattori": ">",
        "raja": "0",
        "suunta": "paa",
    },
}
