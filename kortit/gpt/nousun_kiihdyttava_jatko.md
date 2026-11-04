# Nousun kiihtyvä jatko

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Nousun jälkeen osa ostajista nostaa hintatasoaan viiveellä, jolloin uusi 10 minuutin positiivinen tuotto syntyy kiihtyvällä toteutuneella volyymilla. Kysynnän ajallinen porrastus voi jatkaa liikettä eikä välttämättä purkaudu heti.
- **Suunta:** ▲ (vain ylöspäin); pääehdon `suunta` on `up`.
- **Miksi ei pelkkä volatiliteetti:** Nousutapahtuman lisäksi vaaditaan tuore nousutuotto ja volyymin 5/60 minuutin suhteellinen vahvistuminen, ei pelkkä suuri σ15.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Yhteinen suuri nousu 60 min | `vertailu` | `{     "lahde": "nousu60",     "operaattori": ">=",     "raja": "$nousuraja", }` | tapahtuma | ei | 1800 s |
| Kymmenen minuutin lisänousu | `vertailu` | `{     "lahde": "nousu10",     "operaattori": ">=",     "raja": "0.003",     "suunta": "up", }` | ehto | kyllä | – |
| Volyymi kiihtyy | `vertailu` | `{     "lahde": "vol5",     "operaattori": ">",     "vastaan": "vol60", }` | ehto | ei | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `nousu60` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 3600, }` |
| `nousu10` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 600, }` |
| `vol` | `{     "kind": "series",     "field": "volume",     "step": 60, }` |
| `vol5` | `{     "kind": "window",     "source": "vol",     "op": "mean",     "seconds": 300, }` |
| `vol60` | `{     "kind": "window",     "source": "vol",     "op": "mean",     "seconds": 3600, }` |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| `exchange` | `okx` | yksi sallittu arvo | LIIGAn vakioitu pörssi |
| `instrument` | `BTC-USDT` | `BTC-USDT`, `BTC-EUR`, `BTC-USDC` (LIIGA tutkii BTC-USDT:n) | Yhteinen skeema; tutkimuspari on BTC-USDT |
| `cooldown_seconds` | `5400` | ei naapurivarianttia | 90 min tauko rajaa enimmäistiheyden alle 20/vrk |
| `nousuraja` | `0.008` | `0.006`, `0.008`, `0.010` | Saman 60 min nousurajan lievä, ennalta lukittu herkkyysmuutos. |

Yksi oma enum-parametri × kolme ennalta valittua arvoa = kolme LIIGA-varianttia. Parametrin kaikki arvot ovat merkkijonoja.

## Tarvittavat uudet palikat
- ei uusia

## Odotettu tiheys
- **0,5–1,2 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. 0,8 %:n tunninousun alitettuakin alkaneita jaksoja on oletettavasti useita viikossa; uusi 10 min nousu ja volyymin kiihtyminen karsivat osan.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Saman σ15:n ja kellonajan verrokeissa ylöspäin suuntautuva 60 min osuma ei eroa verrokeista tai reuna kääntyy negatiiviseksi naapurirajoilla.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Eroaako kiihtyvä osuus pelkästä tunninousun jälkeisestä satunnaisliikkeestä?
