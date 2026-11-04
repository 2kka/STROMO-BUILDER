# TP-alue ja myötäinen kauppapaine – long / short

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Avoimen position tavoitehinta voi lähestyä nopeasti, ja treidaajan on hyvä nähdä, onko aggressiivinen kauppavirta vielä oman position suunnassa. Se auttaa tarkastamaan jo tehdyn exit-suunnitelman, muttei ennusta tavoitteen osumista tai ehdota siirtoa. Longissa myötävirta on ostoa, shortissa myyntiä.
- **Suunta:** Position suunta: long ▲, short ▼ (valitaan positiosta, ei erillisestä oletuksesta).
- **Miksi ei pelkkä volatiliteetti:** Vaatii position oman TP-rajan läheisyyden ja suuntaan sidotun poikkeavan CVD-paineen.
- **Aikajänne:** TP:n lähestymisen seuraavat sekunnit–minuutit; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| TP lähestyy | tp_sl_lahestyy | valitun position TP:n etäisyys ≤ 0,20 %; lähestyy position voiton suuntaan | tapahtuma | kyllä | voimassa_s=180 |
| CVD myötäsuuntainen | cvd_paine | /CVD5/ ≥ p90 ja merkki sama kuin position suunta | tila | ei | hystereesi_s=30 |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| positio | käyttäjän valitsema avoin positio | — | Sisältää long/short, instrumentin ja TP:n |
| tp_lahestyminen_pct | 0,20 % | — | Ennakkohuomio ennen tavoitetta |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia palikoita: TP-lähestyminen on kohde-ehto ja CVD-paine valmis tunnistin. Positiosidonta, myös short-suunta, kuuluu pikastromon elinkaareen.

## Odotettu tiheys
- Arvio 0–2/vrk per positio; TP-lähestyminen on rajattu tapahtuma eikä virraton positio anna kultaa (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Hälytys ei auta käyttäjää tarkastamaan tavoitehintaa ajoissa tai tulkitaan virheellisesti automaattiseksi kehotukseksi venyttää voittoa.

## Avoimet kysymykset
- Jos position TP:tä ei ole määritelty, pohjaa ei voi aktivoida; osittainen TP ja position sulkeminen vaativat elinkaaren päivityksen.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "TP-alue ja myötäinen kauppapaine – long / short"

SELITYS = "Ilmoittaa, kun oman position tavoitehinta lähestyy ja myötäsuuntainen 5m kauppapaine on voimakas."

HYPOTEESI = "Avoimen position tavoitehinta voi lähestyä nopeasti, ja treidaajan on hyvä nähdä, onko aggressiivinen kauppavirta vielä oman position suunnassa. Se auttaa tarkastamaan jo tehdyn exit-suunnitelman, muttei ennusta tavoitteen osumista tai ehdota siirtoa. Longissa myötävirta on ostoa, shortissa myyntiä."

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
    "positio": {
        "type": "position_ref",
        "default": None,
        "required": True,
        "syote": "kayttaja_valitsee",
        "label": "Avoin positio (long tai short)",
    },
    "tp_lahestyminen_pct": {
        "type": "number",
        "default": "0.20",
        "min": "0.01",
        "max": "2.00",
    },
}

EHDOT = {
    "TP lähestyy": {
        "palikka": "tp_sl_lahestyy",
        "positio": "$positio",
        "kohde": "tp",
        "etaisyys_pct": "$tp_lahestyminen_pct",
        "tyyppi": "tapahtuma",
        "voimassa_s": 180,
        "paa": True,
    },
    "CVD myötäsuuntainen": {
        "palikka": "cvd_paine",
        "ikkuna_s": 300,
        "percentile": 90,
        "suunta": "$positio.suunta",
        "tyyppi": "tila",
        "hystereesi_s": 30,
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** avoin positio, jonka **long/short-suunta ja TP** ovat tiedossa; etäisyysrajaa voi muuttaa
- **Elinkaari:** positioon sidottu, lakkaa kun positio suljetaan tai TP poistuu
- **Oletus-cooldown:** 1800 s.
- **Kulta:** TP lähellä ja vahva position myötäinen paine; tarkista suunnitelma ja kirja, älä siirrä TP:tä automaattisesti.

## Tasojen tulkinta
- **Pronssi:** TP tulee lähelle; tarkista alkuperäinen exit-suunnitelma jo tässä vaiheessa.
- **Hopea:** Ei hopeaa kahden ehdon stromolla.
- **Kulta:** TP lähellä ja vahva position myötäinen paine; tarkista suunnitelma ja kirja, älä siirrä TP:tä automaattisesti.

## Long/short-tulkinta
Shortissa TP on yleensä entryn alapuolella ja myötäinen paine on negatiivinen CVD; longissa peilikuva. Positiotietojen lähde on käyttäjän valinta, ei kauppojen automaattinen lähetys.
