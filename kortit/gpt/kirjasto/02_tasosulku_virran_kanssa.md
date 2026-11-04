# Tasosulku ja suuntainen virta – long / short

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Hintatason ylitystä tai alitusta seuraava voi haluta varmistaa, ettei päätös perustu pelkkään yhden sekunnin piikkiin. Suljettu 5 minuutin kynttilä ja saman jakson suuntainen aggressorivirta ovat toisistaan erottuvia havaintoja. Spreadin normaalisuus kertoo, onko tilanteen tarkastelu likviditeetin kannalta järkevää; yhdistelmä ei lupaa jatkoa.
- **Suunta:** Long: 5m sulku tason yläpuolella ja delta > 0. Short: 5m sulku tason alapuolella ja delta < 0.
- **Miksi ei pelkkä volatiliteetti:** Vaatii käyttäjän merkitsemän tason, sulkeutuneen kynttilän, aggressorivolyymin merkin ja spreadin; volatiliteetin voimakkuus ei yksin riitä.
- **Aikajänne:** Sulun jälkeiset 5–20 min; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Sulku tason yli / alle | kynttila_5m_tason_yli_alle | Long: 5m close > taso; short: 5m close < taso; ylitystapahtuma | tapahtuma | kyllä | voimassa_s=180 |
| 5m delta myötäinen | window_ja_vertailu | sum(60 s delta, 300 s) > 0 longissa / < 0 shortissa | ehto | ei | — |
| Spread hallinnassa | spreadi_normaaliin | spread < 3 × normaali | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| taso | käyttäjän taso | — | Oma rakenne/alue ennen hälytystä |
| suunta | long tai short, pakollinen | — | Ylityksen merkki määräytyy suunnitelmasta |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia lähtötietoja: 5m-kohde-ehto, 60 s delta-ikkuna ja vertailu sekä spread. `vertailu_suuntaan` on pohjan valinta (long > 0, short < 0), ei erillinen markkinalaskenta.

## Odotettu tiheys
- Arvio 0–3/vrk per pari ja taso, koska kyse on uuden sulkupuolen tapahtumasta ja cooldown on tunti (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Sulku + delta -yhdistelmä ei tuo perusteltua laadunvarmistusta verrattuna sulun katsomiseen käsin tai hälyttää liian myöhään jo vanhentuneen sulun perusteella.

## Avoimet kysymykset
- Tason ylitys ja delta pitää sitoa samaan suljettuun 5 minuutin jaksoon; puuttuva jakso tekee virtaehdosta tuntemattoman.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "Tasosulku ja suuntainen virta – long / short"

SELITYS = "Vahvistaa ennalta merkityn tason 5 min sulkuylityksen tai -alituksen kauppavirran suunnalla ja normaalilla spreadillä."

HYPOTEESI = "Hintatason ylitystä tai alitusta seuraava voi haluta varmistaa, ettei päätös perustu pelkkään yhden sekunnin piikkiin. Suljettu 5 minuutin kynttilä ja saman jakson suuntainen aggressorivirta ovat toisistaan erottuvia havaintoja. Spreadin normaalisuus kertoo, onko tilanteen tarkastelu likviditeetin kannalta järkevää; yhdistelmä ei lupaa jatkoa."

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
        "syote": "kayttaja_valitsee",
    },
    "cooldown_seconds": {
        "type": "integer",
        "default": 3600,
        "min": 0,
        "max": 86400,
    },
    "taso": {
        "type": "number",
        "default": None,
        "required": True,
        "syote": "kayttaja",
        "label": "Oma hintataso (parin noteerausvaluutassa)",
    },
    "suunta": {
        "type": "enum",
        "choices": ["long", "short"],
        "default": None,
        "required": True,
        "syote": "kayttaja_valitsee",
        "label": "Suunniteltu suunta",
    },
}

EHDOT = {
    "Sulku tason yli / alle": {
        "palikka": "kynttila_5m_tason_yli_alle",
        "taso": "$taso",
        "suunta": "$suunta",
        "jakso": "5m",
        "tyyppi": "tapahtuma",
        "voimassa_s": 180,
        "paa": True,
    },
    "5m delta myötäinen": {
        "palikka": "window_ja_vertailu",
        "sarja": "delta",
        "step_s": 60,
        "op": "sum",
        "ikkuna_s": 300,
        "raja": 0,
        "vertailu_suuntaan": "$suunta",
        "tyyppi": "ehto",
        "paa": False,
    },
    "Spread hallinnassa": {
        "palikka": "spreadi_normaaliin",
        "vertailu": "<",
        "kerroin": 3,
        "tyyppi": "ehto",
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** pari, oma taso, **long tai short** (pakollinen)
- **Elinkaari:** kertakäyttöinen (päättyy ensimmäiseen kultaan tai 24 h jälkeen)
- **Oletus-cooldown:** 3600 s.
- **Kulta:** Sulku, delta ja spread tukevat samaa tarkasteluhetkeä; harkitse omaa etukäteissuunnitelmaa, ei automaattista entryä.

## Tasojen tulkinta
- **Pronssi:** Tasosulku on tapahtunut valittuun suuntaan; tarkasta virta ja spread, älä vielä päättele laadukasta murtoa.
- **Hopea:** Tasosulku + joko suuntainen delta tai normaali spread. Toinen vahvistus puuttuu: huomaa ristiriita.
- **Kulta:** Sulku, delta ja spread tukevat samaa tarkasteluhetkeä; harkitse omaa etukäteissuunnitelmaa, ei automaattista entryä.

## Long/short-tulkinta
Shortin vahvistus ei ole hintatason ylitys vaan alitus ja negatiivinen delta; longin ylitys ja positiivinen delta. Raju vastaliike voi tehdä kummastakin vanhentuneen muutamassa minuutissa.
