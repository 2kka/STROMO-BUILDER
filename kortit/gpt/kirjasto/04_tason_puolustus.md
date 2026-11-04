# Tason puolustuksen tarkistus – long / short

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Long-suunnitelmassa tasoa pidetään mahdollisena tukena ja shortissa vastuksena. Kun hinta on käynyt sen lähellä ja 5 minuutin sulku on jälleen suunnitellulla puolella, treidaaja voi tarkistaa, onko taso edelleen hyödyllinen. Samansuuntainen kauppavirta lisää havaintoa mutta ei todista, että taso kestää.
- **Suunta:** Long: tason yläpuolinen 5m sulku ja positiivinen delta; short: tason alapuolinen sulku ja negatiivinen delta.
- **Miksi ei pelkkä volatiliteetti:** Ankkuroituu käyttäjän valitsemaan tuki/vastustasoon, eikä käytä uupumus- tai absorptiosignaalia.
- **Aikajänne:** Tason testin jälkeiset 5–15 min; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Käynti tasoalueella | hinta_lahestyy_tasoa | etäisyys tasoon ≤ 0,10 % | tapahtuma | kyllä | voimassa_s=900 |
| 5m sulku suunnitelmapuolella | kynttila_5m_tason_yli_alle | Long: 5m close > taso / short: 5m close < taso | ehto | ei | — |
| Delta suunnitelmapuolella | window_ja_vertailu | 5m delta-summa long > 0 / short < 0 | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| taso | käyttäjän oma tuki/vastus | — | Ennalta piirretty hintarakenne |
| suunta | long/short | — | Long=tuesta tarkastus, short=vastuksesta |
| lahestyminen_pct | 0,10 % | — | Läheisyys eikä tarkka pohja/huippu |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia laskentapalikoita. Kohde-ehdon kynttiläsulku on tässä jatkuva `ehto` viimeisestä suljetusta 5m kynttilästä; sen tapahtumavaihtoehdon lisäksi tarvitaan jatkuva vertailutila samasta jo saatavasta kynttiläarvosta.

## Odotettu tiheys
- Arvio 0–3/vrk per pari ja taso; tason käyntitapahtuma, 15 min voimassaolo ja 90 min cooldown (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Sama lähellä olevan tason kosketus tuottaa toistuvasti ristiriitaisia sulkuja eikä yhdistelmä auta erottamaan, onko suunniteltu taso edelleen tarkastelun arvoinen.

## Avoimet kysymykset
- Vanhentunut 5m sulku ei saa vahvistaa 15 min vanhaa tason käyntiä; sulku tulee vaatia pääehdon jälkeisestä ensimmäisestä täysin sulkeutuneesta kynttilästä (vaatii tapahtumien aikajärjestysvarmistuksen).

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "Tason puolustuksen tarkistus – long / short"

SELITYS = "Pyytää tarkastamaan, kun ennalta merkityn tukitason/vastuksen läheisyydessä sulku ja kauppavirta ovat suunnitelman mukaisia."

HYPOTEESI = "Long-suunnitelmassa tasoa pidetään mahdollisena tukena ja shortissa vastuksena. Kun hinta on käynyt sen lähellä ja 5 minuutin sulku on jälleen suunnitellulla puolella, treidaaja voi tarkistaa, onko taso edelleen hyödyllinen. Samansuuntainen kauppavirta lisää havaintoa mutta ei todista, että taso kestää."

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
        "default": 5400,
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
        "default": "0.10",
        "min": "0.01",
        "max": "1.00",
    },
}

EHDOT = {
    "Käynti tasoalueella": {
        "palikka": "hinta_lahestyy_tasoa",
        "taso": "$taso",
        "etaisyys_pct": "$lahestyminen_pct",
        "tyyppi": "tapahtuma",
        "voimassa_s": 900,
        "paa": True,
    },
    "5m sulku suunnitelmapuolella": {
        "palikka": "kynttila_5m_tason_yli_alle",
        "taso": "$taso",
        "suunta": "$suunta",
        "jakso": "5m",
        "reuna": "sama_puoli",
        "tyyppi": "ehto",
        "paa": False,
    },
    "Delta suunnitelmapuolella": {
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
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** pari, taso ja **long/short**
- **Elinkaari:** kertakäyttöinen (voimassa korkeintaan 24 h)
- **Oletus-cooldown:** 5400 s.
- **Kulta:** Taso on käyty, suljettu kynttilä ja delta ovat suunnitelman puolella; kyseessä on tarkastuspiste, ei automaattinen käännesignaali.

## Tasojen tulkinta
- **Pronssi:** Hinta on käynyt ennalta valitulla tasolla; älä oleta, että tuki/vastus piti.
- **Hopea:** Taso + sulku tai delta antaa osittaisen havainnon; tarkista puuttuva vahvistus ja liikkuiko hinta jo pois.
- **Kulta:** Taso on käyty, suljettu kynttilä ja delta ovat suunnitelman puolella; kyseessä on tarkastuspiste, ei automaattinen käännesignaali.

## Long/short-tulkinta
Longin tuki ja shortin vastus ovat symmetrisiä vain sääntöjen tasolla. Kauppavirta ja tarjousten likviditeetti pitää silti tulkita sen mukaan, millä puolella käyttäjä oikeasti on.
