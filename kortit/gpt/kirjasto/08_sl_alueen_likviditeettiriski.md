# SL-alueen likviditeettiriski – long / short

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX: BTC-USDT / BTC-EUR / BTC-USDC (käyttäjä valitsee)

## Hypoteesi
- **Mekanismi:** Kun hinta lähestyy etukäteen määriteltyä riskirajaa, syvyyden heikkous voi korostaa toteutusepävarmuutta. Tämä lisähälytys auttaa kohdistamaan huomion orderbookiin mutta ei saa korvata erillistä stop-tilausta tai SL-tason tavallista ilmoitusta. Shortin riskiraja sijaitsee tyypillisesti ylempänä ja longin alempana.
- **Suunta:** Position vastainen liike: longille alaspäin, shortille ylöspäin.
- **Miksi ei pelkkä volatiliteetti:** Vaatii position oman SL:n lähestymisen ja erillisen likviditeetin heikkenemisen.
- **Aikajänne:** SL-alueen lähestyminen ja välitön riskiseuranta; ei LIIGAn 3A-tulosmittaria.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| SL lähestyy | tp_sl_lahestyy | SL:n etäisyys ≤ 0,30 % position riskisuunnassa | tapahtuma | kyllä | voimassa_s=240 |
| Kirjasyvyys heikko | syvyys_normaaliin | ±0,5 % syvyys ≤ 0,5 × normaali | tila | ei | hystereesi_s=10 |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| positio | avoin positio, jossa on SL | — | Pakollinen riskirajan yksilöimiseksi |
| sl_lahestyminen_pct | 0,30 % | — | Varoitus ennen mahdollista tasokosketusta |

Ei LIIGA-parametrivariantteja: pikastromon syötteet käyttäjä valitsee luotaessa.

## Tarvittavat uudet palikat
- Ei uusia: SL-lähestymiskohde ja live-kirjan syvyys. Vaatii luotettavan position SL-tiedon.

## Odotettu tiheys
- Arvio 0–2/vrk per positio; harvinaista on sekä SL-läheisyys että kirjan heikkous (suunnitteluarvio, ei mitattu).

## Kumoava koe
- Hälytys tulee vasta SL:n jo osuttua tai käyttäjä tulkitsee kultaa vaativan yhdistelmän perusteeksi jättää tavallisen SL-valvonnan pois.

## Avoimet kysymykset
- Tämä ei saa olla ainoa SL-muistutus: tavallinen TP/SL-saavutettu -hälytys ja pörssin riskijärjestely pysyvät itsenäisinä, vaikka kirjaehto olisi epätosi.

## Deklaratiivinen määrittely (2.H-e, suunniteltu muoto)
Tämä on ehdollisen pikastromon deklaratiivinen määrittely, ei nykyisen `PALIKAT.md`:n ajettavaa `TARVITSEE/ehto(ctx)`-Pythonia. `EHDOT` on tilattu uusi muoto; rakennusmallin toteutus ja tuki kohde-/positiopalikoille vahvistetaan STROMO4:ssä. `$...` viittaa saman pohjan parametriin. `suunta`-asetus valitsee long-/short-haaran luonnissa, ei jälkikäteen kaupankäynnin mukaan.

```python

NIMI = "SL-alueen likviditeettiriski – long / short"

SELITYS = "Nostaa erityisen riskivarauksen, kun position stop-taso lähestyy ja näkyvä kirjasyvyys on heikko."

HYPOTEESI = "Kun hinta lähestyy etukäteen määriteltyä riskirajaa, syvyyden heikkous voi korostaa toteutusepävarmuutta. Tämä lisähälytys auttaa kohdistamaan huomion orderbookiin mutta ei saa korvata erillistä stop-tilausta tai SL-tason tavallista ilmoitusta. Shortin riskiraja sijaitsee tyypillisesti ylempänä ja longin alempana."

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
        "default": 900,
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
    "sl_lahestyminen_pct": {
        "type": "number",
        "default": "0.30",
        "min": "0.01",
        "max": "2.00",
    },
}

EHDOT = {
    "SL lähestyy": {
        "palikka": "tp_sl_lahestyy",
        "positio": "$positio",
        "kohde": "sl",
        "etaisyys_pct": "$sl_lahestyminen_pct",
        "tyyppi": "tapahtuma",
        "voimassa_s": 240,
        "paa": True,
    },
    "Kirjasyvyys heikko": {
        "palikka": "syvyys_normaaliin",
        "kaista_pct": "0.5",
        "vertailu": "<=",
        "kerroin": "0.5",
        "tyyppi": "tila",
        "hystereesi_s": 10,
        "paa": False,
    },
}

```

## Pikastromovalikko
- **Käyttäjän syöte:** avoin positio, suunta ja määritelty **SL** (molemmat short/long)
- **Elinkaari:** positioon sidottu, päättyy position sulkeutuessa
- **Oletus-cooldown:** 900 s.
- **Kulta:** SL lähellä ja kirja ohut; toteutusepävarmuus on tavallista suurempi, mutta hälytys ei muuta riskirajaa.

## Tasojen tulkinta
- **Pronssi:** SL lähestyy; tarkista riski heti riippumatta kirjan syvyydestä.
- **Hopea:** Ei hopeaa kahden ehdon stromolla.
- **Kulta:** SL lähellä ja kirja ohut; toteutusepävarmuus on tavallista suurempi, mutta hälytys ei muuta riskirajaa.

## Long/short-tulkinta
Longissa tappioraja on tyypillisesti alhaalla ja shortissa ylhäällä. Pörssissä oleva stop toimii tästä lisähälytyksestä riippumatta.
