# Momentum kohtaa volyymin – long / short

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Liikkeen aikana treidaaja haluaa huomata, tuleeko markkinalle poikkeuksellisen paljon osallistumista samalla kun 15 minuutin liike on jo suuntautunut. Volyymipiikki kertoo aktiivisuudesta eikä siitä, missä seuraava hinta on. Hälytys auttaa tarkistamaan, onko oma skenaario edelleen ajankohtainen.
- **Suunta:** Long vaatii Momentum ▲; short Momentum ▼. Kummallakin volyymipiikki on suunnaton.
- **Miksi ei pelkkä volatiliteetti:** Yhdistää 15m suunnan ja volyymin suhteessa samaan UTC-kellonaikaan; kumpikaan yksin ei riitä.
- **Aikajänne:** Seuraavat 1–15 min; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Suuntainen momentum | momentum | Long: ▲; short: ▼; 15 min vähintään 1 σ15 | tila | kyllä | hystereesi_s=30 |
| Volyymipiikki | volyymi_normaaliin | 1 min ≥ 5× saman UTC-kellonajan 7 vrk normaali | tapahtuma | ei | voimassa_s=120 |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| suunta | käyttäjä valitsee long/short | — | Ei hälytystä vastakkaisesta momentumista |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia: käytetään kahta valmista tunnistinta.

## Odotettu tiheys
- Arvio 1–5/vrk per pari ja suunta; 4 h cooldown rajaa enintään 6/vrk (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Volyymipiikki tulee usein vasta liikkeen jälkeen eikä tuo treidaajan päätökselle käyttökelpoista lisätietoa, tai ilmoituksia kertyy ilman yksilöitävää käyttötarkoitusta.

## Avoimet kysymykset
- Määritelläänkö volyymipiikin suunta edelleen suunnattomanakin, jotta myyntivolyymipiikki ei näyttäisi automaattisesti long-vahvistukselta? Käyttäjän on tarkistettava CVD.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "Momentum kohtaa volyymin – long / short"

SELITYS = "Huomauttaa, kun 15 min momentum ja kellonaikaan suhteutettu volyymipiikki esiintyvät samaan suunniteltuun suuntaan."

HYPOTEESI = "Liikkeen aikana treidaaja haluaa huomata, tuleeko markkinalle poikkeuksellisen paljon osallistumista samalla kun 15 minuutin liike on jo suuntautunut. Volyymipiikki kertoo aktiivisuudesta eikä siitä, missä seuraava hinta on. Hälytys auttaa tarkistamaan, onko oma skenaario edelleen ajankohtainen."

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
        "default": 14400,
        "min": 0,
        "max": 86400,
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
    "Suuntainen momentum": {
        "palikka": "momentum",
        "suunta": "$suunta",
        "kynnys_sigma15": 1,
        "tyyppi": "tila",
        "hystereesi_s": 30,
        "paa": True,
    },
    "Volyymipiikki": {
        "palikka": "volyymi_normaaliin",
        "ikkuna_s": 60,
        "kerroin": 5,
        "normaali": "UTC±30min_7vrk",
        "tyyppi": "tapahtuma",
        "voimassa_s": 120,
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** pari ja **long/short**
- **Elinkaari:** toistuva seurannan ajan
- **Oletus-cooldown:** 14400 s.
- **Kulta:** Momentum ja osallistuminen kohtaavat; tarkista delta/CVD, sijainti suhteessa tasoihin ja likviditeetti.

## Tasojen tulkinta
- **Pronssi:** Suunniteltuun suuntaan on momentum, mutta poikkeavaa osallistumista ei vielä havaittu.
- **Hopea:** Ei hopeaa kahden ehdon stromolla.
- **Kulta:** Momentum ja osallistuminen kohtaavat; tarkista delta/CVD, sijainti suhteessa tasoihin ja likviditeetti.

## Long/short-tulkinta
Volyymipiikki itsessään ei ole osto- eikä myyntisignaali. Short-hälytys käyttää Momentum ▼; aggressorivolyymia ei päätellä piikin pelkästä kokonaismäärästä.
