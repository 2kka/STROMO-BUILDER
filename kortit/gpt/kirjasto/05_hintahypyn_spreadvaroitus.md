# Hintahypyn spreadvaroitus

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Nopea BTC-hintaliike voi houkutella reagoimaan kiireessä. Kun spreadi on samaan aikaan epätavallisen leveä, sekä long- että short-toteutuksen kustannus ja epävarmuus voivat kasvaa. Hälytys muistuttaa tarkistamaan toteutuskelpoisuuden, ei kerro hintasuunnan jatkosta.
- **Suunta:** Kumpikin: varoitus toimii riippumatta hypyn suunnasta ja position puolesta.
- **Miksi ei pelkkä volatiliteetti:** Edellyttää kahta erilaista ilmiötä, hintahypyn ja spreadin levenemisen.
- **Aikajänne:** Hetki ja seuraavat 1–3 min; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Hintahyppy | hintahyppy | ±0,2 % / 30 s | tapahtuma | kyllä | voimassa_s=60 |
| Spread häiriintynyt | spreadi_normaaliin | spread ≥ 3 × oma normaali | tila | ei | hystereesi_s=10 |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Ei muita | — | ei LIIGA-naapureita | Vakioasetukset |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia: kauppavirran hintahyppy ja live-kirjan spreadi.

## Odotettu tiheys
- Arvio 0–5/vrk per pari, koska molempien poikkeamien yhtäaikaisuus on harvinaisempi kuin kumpikin yksin; tunnin cooldown (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Varoitukset eivät käytännössä erotu normaaleista toteutusolosuhteista tai jo saatu varoitus on aina myöhässä toteutustavan arviointiin.

## Avoimet kysymykset
- Spreadin normaali tulee olla pari- ja markkinatilakohtaisesti saatavilla; puuttuvaa kirjaa ei saa tulkita normaaliksi.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "Hintahypyn spreadvaroitus"

SELITYS = "Varoittaa poikkeuksellisen nopeasta hinnasta tilanteessa, jossa spreadi on leventynyt."

HYPOTEESI = "Nopea BTC-hintaliike voi houkutella reagoimaan kiireessä. Kun spreadi on samaan aikaan epätavallisen leveä, sekä long- että short-toteutuksen kustannus ja epävarmuus voivat kasvaa. Hälytys muistuttaa tarkistamaan toteutuskelpoisuuden, ei kerro hintasuunnan jatkosta."

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
}

EHDOT = {
    "Hintahyppy": {
        "palikka": "hintahyppy",
        "suunta": "kumpikin",
        "raja_pct": "0.2",
        "ikkuna_s": 30,
        "tyyppi": "tapahtuma",
        "voimassa_s": 60,
        "paa": True,
    },
    "Spread häiriintynyt": {
        "palikka": "spreadi_normaaliin",
        "vertailu": ">=",
        "kerroin": 3,
        "tyyppi": "tila",
        "hystereesi_s": 10,
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** vain pari
- **Elinkaari:** toistuva seurannan ajan
- **Oletus-cooldown:** 3600 s.
- **Kulta:** Hintahyppy ja leveä spread: älä kiirehdi markkinatilanteen arviointia, tarkista kirja ja riskit.

## Tasojen tulkinta
- **Pronssi:** Hintahyppy näkyy; tarkista, onko kyse piikistä vai pidemmästä liikkeestä.
- **Hopea:** Ei hopeaa kahden ehdon stromolla.
- **Kulta:** Hintahyppy ja leveä spread: älä kiirehdi markkinatilanteen arviointia, tarkista kirja ja riskit.

## Long/short-tulkinta
Varoitus on puolineutraali: nopea nousu haittaa kiireistä short-avausta yhtä lailla kuin nopea lasku voi haitata long-avausta.
