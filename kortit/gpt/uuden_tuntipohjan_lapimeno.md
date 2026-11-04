# Uuden tuntipohjan läpimeno

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Kun viimeisen tunnin alin päätöshinta osuu juuri syntyneeseen minuuttisulkuun, aiemmat sulkutasot eivät enää kuvaa alarajaa. Samanaikainen lyhyt negatiivinen tuotto ja poikkeava kaupankäyntitiheys voivat tukea uuden hintatason hyväksyntää.
- **Suunta:** ▼ (vain alaspäin); pääehdon `suunta` on `down`.
- **Miksi ei pelkkä volatiliteetti:** Uusi toteutunut alin minuuttisulku ja countin vuorokausipersentiili ovat erillisiä rakenteellisia ehtoja.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Uusi 60 min pohjasulku | `vertailu` | `{     "lahde": "close",     "operaattori": "<=",     "vastaan": "tuntipohja",     "suunta": "down", }` | tapahtuma | kyllä | 300 s |
| Lyhyt lasku | `vertailu` | `{     "lahde": "lasku5",     "operaattori": "<=",     "raja": "$lasku5", }` | ehto | ei | – |
| Osallistuminen korkea | `vertailu` | `{     "lahde": "count5",     "operaattori": ">=",     "vastaan": "countp80", }` | ehto | ei | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `tuntipohja` | `{     "kind": "window",     "source": "close",     "op": "min",     "seconds": 3600, }` |
| `lasku5` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 300, }` |
| `count` | `{     "kind": "series",     "field": "count",     "step": 60, }` |
| `count5` | `{     "kind": "window",     "source": "count",     "op": "sum",     "seconds": 300, }` |
| `countp80` | `{     "kind": "percentile",     "source": "count5",     "seconds": 86400,     "p": "80", }` |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| `exchange` | `okx` | yksi sallittu arvo | LIIGAn vakioitu pörssi |
| `instrument` | `BTC-USDT` | `BTC-USDT`, `BTC-EUR`, `BTC-USDC` (LIIGA tutkii BTC-USDT:n) | Yhteinen skeema; tutkimuspari on BTC-USDT |
| `cooldown_seconds` | `5400` | ei naapurivarianttia | 90 min tauko rajaa enimmäistiheyden alle 20/vrk |
| `lasku5` | `-0.002` | `-0.0015`, `-0.002`, `-0.0025` | Ennalta lukitut lähellä toisiaan olevat mekanismirajat. |

Yksi oma enum-parametri × kolme ennalta valittua arvoa = kolme LIIGA-varianttia. Parametrin kaikki arvot ovat merkkijonoja.

## Tarvittavat uudet palikat
- ei uusia

## Odotettu tiheys
- **0,5–1,3 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. Tunnin uudet pohjasulut syntyvät laskevien jaksojen aikana, mutta lyhyt laskuraja ja 80. persentiilin kauppamäärä karsivat suurimman osan.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Uutta pohjasulkua seuraava alasreuna ei pysy positiivisena saman σ15:n/kellonajan verrokeissa, tai tulos perustuu vain yhteen raja-arvoon.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Syntyykö liian monta saman laskujakson uutta pohjasulkua tapahtuman uudelleenvirittyessä?
