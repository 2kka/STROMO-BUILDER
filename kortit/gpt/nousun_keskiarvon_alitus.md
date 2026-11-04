# Nousun lyhyen keskihinnan alitus

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Nousun jälkeen hinta voi aluksi jäädä korkealle, mutta vähittäinen siirtymä 15 minuutin päätöskeskiarvon alle osoittaa lyhyen jakson toteutuneiden hintojen painopisteen ylittyvän alaspäin. Tämä on hitaampi tasapainon menetys kuin välitön kolmen minuutin vastaisku.
- **Suunta:** ▼ (vain alaspäin); pääehdon `suunta` on `down`.
- **Miksi ei pelkkä volatiliteetti:** Käyttää hinta-asemaa suhteessa sulkeutuneiden hintojen keskiarvoon sekä 15 min negatiivista tuottoa, ei vain heilunnan kokoa.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Yhteinen suuri nousu 60 min | `vertailu` | `{     "lahde": "nousu60",     "operaattori": ">=",     "raja": "$nousuraja", }` | tapahtuma | ei | 1800 s |
| Lyhyt keskihinta menetettiin | `vertailu` | `{     "lahde": "close",     "operaattori": "<",     "vastaan": "keski15",     "suunta": "down", }` | ehto | kyllä | – |
| Viidentoista minuutin lasku | `vertailu` | `{     "lahde": "nousu15",     "operaattori": "<=",     "raja": "-0.002", }` | ehto | ei | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `nousu60` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 3600, }` |
| `keski15` | `{     "kind": "window",     "source": "close",     "op": "mean",     "seconds": 900, }` |
| `nousu15` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 900, }` |

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
- **0,6–1,4 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. Keskiarvon alitus ja 15 min negatiivinen tuotto voivat seurata tunninousua jo saman puolen tunnin sisällä.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Alapuolelle siirtymistä seuraava 60 min alas-osuma ei ole parempi kuin σ15-/kellonaikaverrokki tai naapureiden etu katoaa.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Onko keskiarvon alitus riittävän itsenäinen, kun 15 minuutin tuotto on jo negatiivinen?
