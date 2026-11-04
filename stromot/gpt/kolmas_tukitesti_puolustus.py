"""Kolmas tukitesti: puolustus ▲ (kierros 2, R-stromo). Kortti: kortit/gpt/kolmas_tukitesti_vol2_puolustus.md
Palikat kolmas_tukitesti_vol2 ja tukitestin_ensimmainen_ratkaisu tilataan STROMO4:ään (prompti 31);
siihen asti LIIGA näyttää stromon prospektina tilassa "odottaa palikkaa"."""

NIMI = "Kolmas tukitesti: puolustus"
SELITYS = "Kolmas erillinen tukitesti tuplavolyymilla ja ensimmäinen ratkaisu sulkuna tuen yläpuolelle."
HYPOTEESI = (
    "Tukitasoa seuranneet ostajat puolustavat sitä kolmannella uusintatestillä; kun viimeisen kosketuksen kokonaisvolyymi on vähintään kaksinkertainen toiseen verrattuna ja ensimmäinen selvä reaktio sulkeutuu tason yläpuolelle, ostajat palautuvat ja hinta jatkaa ylös seuraavan tunnin. Vain ▲."
)
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {"type": "enum", "default": "BTC-USDT", "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"]},
    "cooldown_seconds": {"type": "integer", "default": 14400, "min": 0, "max": 86400},
    "kosketuskaista_pct": {"type": "enum", "default": "0.15", "choices": ["0.10", "0.15", "0.20"],
                           "label": "Kosketuskaista %"},
}
TARVITSEE = {}
EHDOT = {
    "Kolmas tukitesti, 2× volyymi": {
        "palikka": "kolmas_tukitesti_vol2",
        "kosketuskaista_pct": "$kosketuskaista_pct",
        "tyyppi": "tapahtuma",
        "voimassa_s": 300,
        "paa": True,
    },
    "Puolustus vahvistui ▲": {
        "palikka": "tukitestin_ensimmainen_ratkaisu",
        "kosketuskaista_pct": "$kosketuskaista_pct",
        "suunta": "up",
        "tyyppi": "tapahtuma",
        "voimassa_s": 60,
    },
}
