# R-voiton palautus – long / short

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Avoimen position suurin nähty voitto voi tehdä treidaajasta huomaamattaan liian odottavan. Kun voittoa on ensin kertynyt mutta se on osittain valunut takaisin, on hyödyllistä tarkistaa, mitä alkuperäinen positionhoitosuunnitelma sanoo. Sama sääntö koskee shortin alas liikkuvaa voittoa ja longin ylös liikkuvaa voittoa.
- **Suunta:** Position suunta long/short, mutta hälytys koskee **voiton palautumista**, ei uutta hintasuuntaennustetta.
- **Miksi ei pelkkä volatiliteetti:** Perustuu käyttäjän riskin R-yksikköön ja position omasta P&L:stä mitattuun palautumaan, ei pelkkään market-volatiliteettiin.
- **Aikajänne:** Avoimen position hoito, ei 60 min suuntaosuma; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Voitto palautunut | voitto_valuu_huipusta | Avoin nettovoitto on pudonnut ≥ 25 % suurimmasta avoimesta voitosta position alusta | tapahtuma | kyllä | voimassa_s=600 |
| Vielä positiivinen R | position_r | Nykyinen position R ≥ 1,5 R | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| positio | avoin positio, jossa entry ja alkuperäinen riski R | — | R on poistettava automaattisesta signaalista, jos riski ei ole tiedossa |
| min_r | 1,5 R | — | Jäljelläkin on mielekästä avoinna olevaa voittoa |
| palautus_pct | 25 % huipun voitosta | — | Havaitsee selvän palautuman, ei jokaista pientä vaihtelua |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia: `voitto valuu x % huipusta` ja `position R ≥ n` ovat ilmoitettuja kohde-ehtoja. Palkkiokulujen sisältyminen tulokseen varmistetaan positiointegraatiossa.

## Odotettu tiheys
- Arvio 0–2/vrk per positio; palautuma laukeaa vasta positiossa, jossa on aiempaa voittoa (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Varoitukset johtavat toistuvasti oman suunnitelman vastaisiin hätäpäätöksiin tai suurinta voittoa ei saada luotettavasti seurattua position alusta.

## Avoimet kysymykset
- R tulee laskea alkuperäisen entry–SL-riskin perusteella; jos SL muuttuu, alkuperäistä R-nimittäjää ei vaihdeta kesken position ilman näkyvää merkintää.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "R-voiton palautus – long / short"

SELITYS = "Muistuttaa tarkastamaan position voittosuunnitelman, kun positio on yhä yli 1,5 R voitolla mutta on luovuttanut 25 % parhaasta avoimesta voitostaan."

HYPOTEESI = "Avoimen position suurin nähty voitto voi tehdä treidaajasta huomaamattaan liian odottavan. Kun voittoa on ensin kertynyt mutta se on osittain valunut takaisin, on hyödyllistä tarkistaa, mitä alkuperäinen positionhoitosuunnitelma sanoo. Sama sääntö koskee shortin alas liikkuvaa voittoa ja longin ylös liikkuvaa voittoa."

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
    "positio": {
        "type": "position_ref",
        "default": None,
        "required": True,
        "syote": "kayttaja_valitsee",
        "label": "Avoin positio (long tai short)",
    },
    "min_r": {
        "type": "number",
        "default": "1.5",
        "min": "0.1",
        "max": "10",
    },
    "palautus_pct": {
        "type": "number",
        "default": "25",
        "min": "1",
        "max": "90",
    },
}

EHDOT = {
    "Voitto palautunut": {
        "palikka": "voitto_valuu_huipusta",
        "positio": "$positio",
        "pudotus_pct": "$palautus_pct",
        "mitta": "avoimen_voiton_huippu",
        "tyyppi": "tapahtuma",
        "voimassa_s": 600,
        "paa": True,
    },
    "Vielä positiivinen R": {
        "palikka": "position_r",
        "positio": "$positio",
        "vertailu": ">=",
        "raja": "$min_r",
        "tyyppi": "ehto",
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** avoin positio (entry, **long/short**, alkuperäinen stop/R); valinnainen min_R ja palautumaprosentti
- **Elinkaari:** positioon sidottu, päättyy position sulkeutuessa
- **Oletus-cooldown:** 3600 s.
- **Kulta:** Voitto on palautunut ≥25 % huipusta mutta jäljellä on ≥1,5 R; tarkista ennalta sovittu exit-/trail-sääntö, ei automaattista sulkua.

## Tasojen tulkinta
- **Pronssi:** Voitto on jo palautunut huipusta; vertaile sitä omaan positionhoitosuunnitelmaan.
- **Hopea:** Ei hopeaa kahden ehdon stromolla.
- **Kulta:** Voitto on palautunut ≥25 % huipusta mutta jäljellä on ≥1,5 R; tarkista ennalta sovittu exit-/trail-sääntö, ei automaattista sulkua.

## Long/short-tulkinta
Shortissa kasvanut avoin voitto syntyy laskevasta markkinasta ja sen palautuma nousevasta vastaliikkeestä. Longissa päinvastoin. Mittari on position P&L, ei pelkkä hinnan prosenttimuutos.
