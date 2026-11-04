# Tasosulku ostovirran kanssa ▲

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX EEA: käyttäjän valitsema BTC-USDT / BTC-EUR / BTC-USDC

## Hypoteesi
- **Mekanismi:** Tarkkailija on merkinnyt mahdollisen vastustason ennen hälytystä. Viiden minuutin kynttilän sulkeutuminen sen yläpuolelle kertoo, että taso ylitettiin myös hitaammassa tarkastelussa; saman jakson netto-ostovirta kertoo, että aggressiiviset ostajat olivat mukana. Hälytys auttaa arvioimaan vahvistuksen laatua, ei ennusta jatkoa.
- **Suunta:** ▲; vain käyttäjän määrittämän ylärajan ylitys.
- **Miksi ei pelkkä volatiliteetti:** Vaatii juuri valitun hintatason sulkuylityksen ja samanaikaisen positiivisen aggressorideltan, ei pelkkää suurta hintaliikettä.
- **Aikajänne:** Sulkeutumishetki ja seuraavat 5–15 min; ei LIIGAn 3A-testiä.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| 5m-tasosulku | Kynttilä 5m päättyy tason yli | Käyttäjän etukäteen asettama taso; ylöspäin tapahtuva False→True | tapahtuma | kyllä | voimassa_s = 180 s |
| Ostajien enemmyys | sum(delta, 300 s) | 60 s kauppasarja; ostot − myynnit > 0 viimeisellä 5 minuutilla | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Taso | käyttäjä asettaa | — (ei LIIGAa) | Merkityksellinen vastustaso, ei automaattinen optimointi |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Ei uusia: oma 5m-tasoehto ja delta-ikkuna riittävät.

## Odotettu tiheys
- Arvio 0–4 kultahälytystä/vrk per pari ja seurattu taso; tasoylitys on kertaluonteisempi kuin jatkuva virta. Lukittu hiljennys 3600 s. Arvio on testaamaton ja riippuu tasosta.

## Kumoava koe
- Jos tasosulun yhteydessä delta on lähes aina samanmerkkinen eikä yhdistelmä anna enempää päätöskontekstia kuin pelkkä tasosulku, toisen ehdon lisäarvo puuttuu.

## Avoimet kysymykset
- Käyttäjä voi merkitä useita tasoja; määritelläänkö hälytykset tasokohtaisesti, jotta yksi taso ei hiljennä toista?
