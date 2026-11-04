# Tason lähestymisvahti – long / short

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Treidaaja merkitsee jo valmistelussa hinnan, jolla hän haluaa pysähtyä tarkistamaan kynttilän, CVD:n ja kirjan. Lähestymisvaroitus poistaa tarpeen tuijottaa ruutua koko ajan; normaali spread vähentää turhia huomioita huonossa likviditeetissä. Tasolle pääseminen ei itsessään tarkoita entryä.
- **Suunta:** Kumpikin: käyttäjä ilmoittaa suunnitelman long/short; se on tulkintatieto, ei ennuste. Longissa tarkistetaan tyypillisesti tuki, shortissa vastus.
- **Miksi ei pelkkä volatiliteetti:** Hälytys sidotaan etukäteen asetettuun tasoon ja spreadin laatuun, ei hintavaihtelun nopeuteen.
- **Aikajänne:** Tason lähestyminen ja seuraavat 1–10 min; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Lähestyy tasoa | hinta_lahestyy_tasoa | /hinta−taso//taso ≤ $lahestyminen_pct; False→True | tapahtuma | kyllä | voimassa_s=180 |
| Spread tavanomainen | spreadi_normaaliin | spread < 3 × saman parin normaali; jos normaali puuttuu, ei kultaa | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| taso | käyttäjän oma taso | ei LIIGA-naapureita | Treidaajan ennen tilannetta valitsema |
| suunta | käyttäjä valitsee long/short | — | Sama hälytys pitää tulkita positiosuunnassa |
| lahestyminen_pct | 0,15 % | — | Riittävä ennakkovaroitus ilman millintarkkaa osumaa |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia. Tason lähestyminen on kohde-ehto; normaalia spreadiä vertaillaan käänteisellä operaattorilla.

## Odotettu tiheys
- Arvio 0–3/vrk per pari ja seurattu taso; tasolähestyminen on sisäänmenotapahtuma, lisäksi 30 min cooldown (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Viikon käytössä suurin osa hälytyksistä ei johda edes tarkoitukselliseen tason tarkastamiseen tai sama taso piippaa jatkuvasti, vaikka sitä ei lähestytä uudestaan.

## Avoimet kysymykset
- Kun hinta on tason väärällä puolella, hälytys kertoo vain läheisyydestä; käyttäjän pitää tarkistaa lähestymissuunta kaaviosta.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "Tason lähestymisvahti – long / short"

SELITYS = "Nostaa ennalta merkityn hinnan tarkasteluun, kun tasoa lähestytään ja spreadi ei ole poikkeuksellisen leveä."

HYPOTEESI = "Treidaaja merkitsee jo valmistelussa hinnan, jolla hän haluaa pysähtyä tarkistamaan kynttilän, CVD:n ja kirjan. Lähestymisvaroitus poistaa tarpeen tuijottaa ruutua koko ajan; normaali spread vähentää turhia huomioita huonossa likviditeetissä. Tasolle pääseminen ei itsessään tarkoita entryä."

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
        "default": 1800,
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
    "lahestyminen_pct": {
        "type": "number",
        "default": "0.15",
        "min": "0.01",
        "max": "2.00",
        "label": "Lähestymisraja (%)",
    },
}

EHDOT = {
    "Lähestyy tasoa": {
        "palikka": "hinta_lahestyy_tasoa",
        "taso": "$taso",
        "etaisyys_pct": "$lahestyminen_pct",
        "tyyppi": "tapahtuma",
        "voimassa_s": 180,
        "paa": True,
    },
    "Spread tavanomainen": {
        "palikka": "spreadi_normaaliin",
        "vertailu": "<",
        "kerroin": 3,
        "normaali": "oma",
        "tyyppi": "ehto",
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** pari, taso ja **long/short** sekä haluttaessa lähestymisraja
- **Elinkaari:** kertakäyttöinen (automaattinen päättyminen enintään 24 h)
- **Oletus-cooldown:** 1800 s.
- **Kulta:** Taso lähestyy ja spread on tavanomainen: tarkista myös rakenne ja heatmap ennen omaa päätöstä.

## Tasojen tulkinta
- **Pronssi:** Taso on lähestymisalueella; avaa kaavio, älä tulkitse sitä vahvistukseksi.
- **Hopea:** Ei hopeaa kahden ehdon stromolla.
- **Kulta:** Taso lähestyy ja spread on tavanomainen: tarkista myös rakenne ja heatmap ennen omaa päätöstä.

## Long/short-tulkinta
Long-suunnitelmassa valvottava taso voi olla tuki; short-suunnitelmassa vastus. Kumpikaan ei määritä kaupankäyntitoimea, eikä hälytys päättele automaattisesti lähestymispuolta.
