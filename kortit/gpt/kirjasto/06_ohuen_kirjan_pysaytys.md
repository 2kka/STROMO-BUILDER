# Ohuen kirjan pysäytys – älä kiirehdi

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Hiljaisessa tai rikkoutuneessa tarjouskirjassa yksittäinen kauppa voi heilauttaa hintaa tavallista enemmän. Jos sekä syvyys on vähentynyt että spread leventynyt, näkyvät toteutusehdot ovat heikentyneet riippumatta ennakkosuunnasta. Hälytys on markkinakelpoisuuden tarkistus.
- **Suunta:** Kumpikin, koskee long- ja short-puolia.
- **Miksi ei pelkkä volatiliteetti:** Kirjan syvyyden ja spreadin havainnot ovat likviditeettimittareita eivätkä hintavolatiliteetin mittareita.
- **Aikajänne:** Hetki ja tila, kunnes kirja palautuu; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Syvyys ohut | syvyys_normaaliin | ±0,5 % kirjan syvyys ≤ 0,5 × normaali | tila | kyllä | hystereesi_s=20 |
| Spread leveä | spreadi_normaaliin | spread ≥ 3 × normaali | tila | ei | hystereesi_s=15 |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Ei muita | — | ei LIIGA-naapureita | Vakioasetukset |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia: live-kirjan syvyys ja spreadi.

## Odotettu tiheys
- Arvio 0–3/vrk per pari; 2 h cooldown vähentää jatkuvaa piippausta samassa ohuessa tilassa (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Hälytys toistuu koko päivän ilman muutosta toimintakelpoisuuden arvioon tai ei erota tavallisesta likviditeetin vaihtelusta.

## Avoimet kysymykset
- Sama syvyysluku voi näyttää eri parilla erilaiselta; vertailu tehdään oman parin normaaliin, eikä book-katkos kelpaa ohuen kirjan signaaliksi.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "Ohuen kirjan pysäytys – älä kiirehdi"

SELITYS = "Nostaa esiin matalan likviditeetin ja samalla poikkeavan spreadin, jolloin uusia päätöksiä kannattaa hidastaa."

HYPOTEESI = "Hiljaisessa tai rikkoutuneessa tarjouskirjassa yksittäinen kauppa voi heilauttaa hintaa tavallista enemmän. Jos sekä syvyys on vähentynyt että spread leventynyt, näkyvät toteutusehdot ovat heikentyneet riippumatta ennakkosuunnasta. Hälytys on markkinakelpoisuuden tarkistus."

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
        "default": 7200,
        "min": 0,
        "max": 86400,
    },
}

EHDOT = {
    "Syvyys ohut": {
        "palikka": "syvyys_normaaliin",
        "kaista_pct": "0.5",
        "vertailu": "<=",
        "kerroin": "0.5",
        "tyyppi": "tila",
        "hystereesi_s": 20,
        "paa": True,
    },
    "Spread leveä": {
        "palikka": "spreadi_normaaliin",
        "vertailu": ">=",
        "kerroin": 3,
        "tyyppi": "tila",
        "hystereesi_s": 15,
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** vain pari
- **Elinkaari:** toistuva seurannan ajan
- **Oletus-cooldown:** 7200 s.
- **Kulta:** Sekä syvyys että spread ovat poikkeavia: priorisoi riskin ja toteutustavan tarkistus, ei uutta automaattista toimea.

## Tasojen tulkinta
- **Pronssi:** Kirjan syvyys on vähentynyt; tarkista spread ja näkyvät hintatasot.
- **Hopea:** Ei hopeaa kahden ehdon stromolla.
- **Kulta:** Sekä syvyys että spread ovat poikkeavia: priorisoi riskin ja toteutustavan tarkistus, ei uutta automaattista toimea.

## Long/short-tulkinta
Short ja long voivat molemmat kärsiä leveästä spreadistä. Palautumisesta normaaliin ei tehdä automaattista vihreää entry-signaalia.
