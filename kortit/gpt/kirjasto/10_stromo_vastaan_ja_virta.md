# Oma stromo kääntyy vastaan – long / short

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Treidaaja voi avata position jonkin oman markkinahavainnon perusteella ja jättää huomaamatta, että sama havainto muuttuu myöhemmin vastakkaiseksi. Kun valitun seurattavan stromon suunta kääntyy ja aggressiivinen virta on samalla positioon nähden vastainen, alkuperäisen perustelun ajantasaisuus on syytä tarkastaa. Hälytys ei sulje positiota.
- **Suunta:** Long-positiolle vastainen ▲→▼, short-positiolle ▼→▲; CVD-paine vastakkaiseen suuntaan.
- **Miksi ei pelkkä volatiliteetti:** Vaatii nimenomaan position alkuperäisen seurattavan stromon suunnanvaihdoksen ja erillisen voimakkaan aggressorivirran.
- **Aikajänne:** Suunnanmuutosta seuraavat minuutit; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Seurattu stromo vastaan | stromon_suunta_vastaan | Seurattu stromo vaihtaa suunnan vastakkaiseksi kuin valitun position suunta | tapahtuma | kyllä | voimassa_s=300 |
| Vastainen CVD-paine | cvd_paine | /CVD5/ ≥ p90, merkki vastainen position suunnalle | tila | ei | hystereesi_s=30 |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| positio | avoin positio, long/short | — | Määrittää vastaisen suunnan |
| seurattu_stromo | käyttäjän valitsema suunnallinen stromo | — | Vain käyttäjän seuraaman, suunnallisen havainnon muutos |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia markkinapalikoita. `stromon_suunta_vastaan` on pikastromon valmiiksi kuvattu kohde-ehto; vaatii suuntatiedon ja position viitteen.

## Odotettu tiheys
- Arvio 0–2/vrk per positio; vaatii harvinaisen seurattavan stromon vastaisen käännön ja painetilan, 2 h cooldown (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Seurattu stromo ei säilytä yksiselitteistä long/short-suuntaa tai hälytys ei auta havaitsemaan alkuperäisen position perusteen muutosta.

## Avoimet kysymykset
- Valittava stromo tarvitsee aidosti suunnallisen tilan; kulta/pronssi-tason muutosta ei saa automaattisesti tulkita suunnanvaihdokseksi. Ilman aiempaa suunnallista havaintoa ei laukaisua.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "Oma stromo kääntyy vastaan – long / short"

SELITYS = "Nostaa position vastaisen suunnanmuutoksen tarkistettavaksi, kun myös 5m aggressoripaine on vastakkainen."

HYPOTEESI = "Treidaaja voi avata position jonkin oman markkinahavainnon perusteella ja jättää huomaamatta, että sama havainto muuttuu myöhemmin vastakkaiseksi. Kun valitun seurattavan stromon suunta kääntyy ja aggressiivinen virta on samalla positioon nähden vastainen, alkuperäisen perustelun ajantasaisuus on syytä tarkastaa. Hälytys ei sulje positiota."

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
    "positio": {
        "type": "position_ref",
        "default": None,
        "required": True,
        "syote": "kayttaja_valitsee",
        "label": "Avoin positio (long tai short)",
    },
    "seurattu_stromo": {
        "type": "stromoref",
        "default": None,
        "required": True,
        "syote": "kayttaja_valitsee",
        "label": "Positioon liitetty seurattava suunnallinen stromo",
    },
}

EHDOT = {
    "Seurattu stromo vastaan": {
        "palikka": "stromon_suunta_vastaan",
        "positio": "$positio",
        "seurattu": "$seurattu_stromo",
        "tyyppi": "tapahtuma",
        "voimassa_s": 300,
        "paa": True,
    },
    "Vastainen CVD-paine": {
        "palikka": "cvd_paine",
        "ikkuna_s": 300,
        "percentile": 90,
        "suunta": "$positio.suunta",
        "relaatio": "vastainen",
        "tyyppi": "tila",
        "hystereesi_s": 30,
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** avoin positio ja siihen nimetty **suunnallinen seurattava stromo**
- **Elinkaari:** positioon sidottu, päättyy position sulkeutuessa
- **Oletus-cooldown:** 7200 s.
- **Kulta:** Seurattu stromo ja 5m paine ovat positioon nähden vastaisia; tarkista riski ja alkuperäinen suunnitelma, ei automaattista poistumista.

## Tasojen tulkinta
- **Pronssi:** Seurattu stromo on muuttunut positiota vastaan; selvitä, muuttuiko perustelu vai vain mittarin tila.
- **Hopea:** Ei hopeaa kahden ehdon stromolla.
- **Kulta:** Seurattu stromo ja 5m paine ovat positioon nähden vastaisia; tarkista riski ja alkuperäinen suunnitelma, ei automaattista poistumista.

## Long/short-tulkinta
Longissa vastainen virta on myynti ja shortissa osto. Stromon pronssi–hopea–kulta-taso ei yksin tarkoita suunnanvaihdosta; tarvitaan eksplisiittinen suunta.
