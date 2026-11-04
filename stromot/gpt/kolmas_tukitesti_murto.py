"""Kolmas tukitesti: tuki menetettiin ▼ (kierros 2, R-stromo). Kortti: kortit/gpt/kolmas_tukitesti_vol2_murto.md
Palikat kolmas_tukitesti_vol2 ja tukitestin_ensimmainen_ratkaisu tilataan STROMO4:ään (prompti 31);
siihen asti LIIGA näyttää stromon prospektina tilassa "odottaa palikkaa"."""

NIMI = "Kolmas tukitesti: tuki menetettiin"
SELITYS = "Kolmas erillinen tukitesti tuplavolyymilla ja ensimmäinen ratkaisu sulkuna tuen alle."
HYPOTEESI = (
    "Kolmannen uusintatestin aikana aktivoituvat myyjät, riskirajat ja stopit ylittävät tukialueen ostokysynnän; kolmanteen kosketukseen keskittyvä vähintään kaksinkertainen volyymi ja sitä seuraava ensimmäinen sulku selvästi tuen alapuolella osoittavat tason menetyksen, ja liike jatkuu alas seuraavan tunnin. Vain ▼."
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
        "suunta": "down",
        "tyyppi": "tapahtuma",
        "voimassa_s": 300,
        "paa": True,
    },
    "Tuki menetettiin ▼": {
        "palikka": "tukitestin_ensimmainen_ratkaisu",
        "kosketuskaista_pct": "$kosketuskaista_pct",
        "suunta": "down",
        "tyyppi": "tapahtuma",
        "voimassa_s": 60,
    },
}
