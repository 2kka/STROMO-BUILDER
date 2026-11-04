# Harvan kaupan hintaliukuma

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Alenevassa markkinassa vähäinen toteutuvien kauppojen määrä saattaa viitata heikkoon haluun ottaa vastapuolta vastaan nykyisillä hinnoilla. Erityisesti lyhyt lisälasku tällaisessa ympäristössä voi jatkua ilman uutta kaupankäyntiryntäystä.
- **Suunta:** ▼ (vain alaspäin); pääehdon `suunta` on `down`.
- **Miksi ei pelkkä volatiliteetti:** Yhdistää hinnan laskun kaupankäyntitiheyden alaneljännekseen ja 30 minuutin laskevaan taustaan, eikä mittaa vain liikkeen kokoa.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Harvan kaupan 5 min lasku | `vertailu` | `{     "lahde": "lasku5",     "operaattori": "<=",     "raja": "$liukuma5",     "suunta": "down", }` | ehto | kyllä | – |
| Harva kaupankäynti | `vertailu` | `{     "lahde": "count5",     "operaattori": "<=",     "vastaan": "countp25", }` | ehto | ei | – |
| Laskeva tausta | `vertailu` | `{     "lahde": "lasku30",     "operaattori": "<=",     "raja": "-0.003", }` | ehto | ei | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `lasku5` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 300, }` |
| `lasku30` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 1800, }` |
| `count` | `{     "kind": "series",     "field": "count",     "step": 60, }` |
| `count5` | `{     "kind": "window",     "source": "count",     "op": "sum",     "seconds": 300, }` |
| `countp25` | `{     "kind": "percentile",     "source": "count5",     "seconds": 86400,     "p": "25", }` |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| `exchange` | `okx` | yksi sallittu arvo | LIIGAn vakioitu pörssi |
| `instrument` | `BTC-USDT` | `BTC-USDT`, `BTC-EUR`, `BTC-USDC` (LIIGA tutkii BTC-USDT:n) | Yhteinen skeema; tutkimuspari on BTC-USDT |
| `cooldown_seconds` | `5400` | ei naapurivarianttia | 90 min tauko rajaa enimmäistiheyden alle 20/vrk |
| `liukuma5` | `-0.0025` | `-0.002`, `-0.0025`, `-0.003` | Ennalta lukitut lähellä toisiaan olevat mekanismirajat. |

Yksi oma enum-parametri × kolme ennalta valittua arvoa = kolme LIIGA-varianttia. Parametrin kaikki arvot ovat merkkijonoja.

## Tarvittavat uudet palikat
- ei uusia

## Odotettu tiheys
- **0,4–0,8 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. Alhaisen kaupankäyntitiheyden hetkiä on oletettavasti päivittäin; hintaliukuman ja 30 min laskutaustan yhdistelmä suodattaa niiden enemmistön.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- 60 min laskun etumatka häviää σ15- ja kellonaikaverrokeissa tai niukan kaupankäynnin ehto heikentää suuntaosumia.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Tarkoittaako pieni count aina harvaa osallistumista vai myös pörssin toteumaraportoinnin eroja?
