# Matalan sigman nousupurkaus

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Toteutunut hintavaihtelu voi pysyä vähäisenä, kun markkinan tila on vakaa ja tarjouksia korjataan hitaasti. Uusi selkeä viiden minuutin hinnannousu alhaisen σ15:n yhteydessä voi sysätä hinnan uudelle alueelle.
- **Suunta:** ▲ (vain ylöspäin); pääehdon `suunta` on `up`.
- **Miksi ei pelkkä volatiliteetti:** Edellyttää σ15:n olevan viimeisen vuorokauden oman jakauman alaneljänneksessä ja tämän lisäksi suuntautunutta 5 min nousua.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Viiden minuutin purkaus | `vertailu` | `{     "lahde": "nousu5",     "operaattori": ">=",     "raja": "$purkaus",     "suunta": "up", }` | ehto | kyllä | – |
| Matala suhteellinen sigma | `vertailu` | `{     "lahde": "sigma15",     "operaattori": "<=",     "vastaan": "sigmap25", }` | ehto | ei | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `sigma15` | `{     "kind": "sigma",     "source": "close", }` |
| `sigmap25` | `{     "kind": "percentile",     "source": "sigma15",     "seconds": 86400,     "p": "25", }` |
| `nousu5` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 300, }` |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| `exchange` | `okx` | yksi sallittu arvo | LIIGAn vakioitu pörssi |
| `instrument` | `BTC-USDT` | `BTC-USDT`, `BTC-EUR`, `BTC-USDC` (LIIGA tutkii BTC-USDT:n) | Yhteinen skeema; tutkimuspari on BTC-USDT |
| `cooldown_seconds` | `5400` | ei naapurivarianttia | 90 min tauko rajaa enimmäistiheyden alle 20/vrk |
| `purkaus` | `0.003` | `0.002`, `0.003`, `0.004` | Ennalta lukitut lähellä toisiaan olevat mekanismirajat. |

Yksi oma enum-parametri × kolme ennalta valittua arvoa = kolme LIIGA-varianttia. Parametrin kaikki arvot ovat merkkijonoja.

## Tarvittavat uudet palikat
- ei uusia

## Odotettu tiheys
- **0,5–1,5 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. Pienen σ15:n jaksoja arvioidaan esiintyvän vuorokauden aikana, mutta vähintään 0,3 %:n viiden minuutin nousu rajaa hälytykset.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Vastaavissa kellonaika- ja σ15-verrokeissa purkauksen jälkeinen nousuetumatka ei täytä LIIGAn reunaehtoa.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Pienentääkö σ15:n hitaahko muutos vuorokausipersentiilin erottelukykyä?
