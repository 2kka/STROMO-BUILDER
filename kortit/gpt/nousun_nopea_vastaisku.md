# Nousun nopea vastaisku

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Nousun jälkeen lyhyessä ajassa aktivoituvat myyntitoimeksiannot voivat rikkoa vastapuolen tarjousten varaan syntyneen hetkellisen hintatason. Toteutuneiden kauppojen tihentyminen erottaa vastaiskun passiivisesta hinnan valumisesta.
- **Suunta:** ▼ (vain alaspäin); pääehdon `suunta` on `down`.
- **Miksi ei pelkkä volatiliteetti:** Edellyttää nousun jälkeen negatiivista 3 min log-tuottoa ja kauppojen tiheyden nousua omasta 30 min keskiarvosta.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Yhteinen suuri nousu 60 min | `vertailu` | `{     "lahde": "nousu60",     "operaattori": ">=",     "raja": "$nousuraja", }` | tapahtuma | ei | 1800 s |
| Kolmen minuutin vastaisku | `vertailu` | `{     "lahde": "nousu3",     "operaattori": "<=",     "raja": "-0.003",     "suunta": "down", }` | ehto | kyllä | – |
| Kaupat tihenevät | `vertailu` | `{     "lahde": "count3",     "operaattori": ">",     "vastaan": "count30", }` | ehto | ei | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `nousu60` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 3600, }` |
| `nousu3` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 180, }` |
| `count` | `{     "kind": "series",     "field": "count",     "step": 60, }` |
| `count3` | `{     "kind": "window",     "source": "count",     "op": "mean",     "seconds": 180, }` |
| `count30` | `{     "kind": "window",     "source": "count",     "op": "mean",     "seconds": 1800, }` |

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
- **0,4–0,9 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. Vastaisku nopean tunninousun jälkeen on kapeampi alijoukko nousutapahtumista, mutta 30 min tapahtumaikkuna jättää aikaa vastaliikkeelle.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Alassuuntainen 60 min osumatodennäköisyys ei ylitä saman σ15:n ja kellonajan verrokkeja tai jää alle asetetun LIIGA-rajan.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Tapahtuuko vastaisku riittävän usein yhden puolen 30 minuutin seurantaikkunassa?
