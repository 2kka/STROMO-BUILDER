# Laskutrendin vastaralli pettää

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Pidempään laskeneessa markkinassa lyhyen nousun ostajat voivat tulla mukaan ilman, että laajempi hinnoittelu muuttuu. Jos 10 minuutin nettonousuun mahtuu jo uusi 3 minuutin lasku, paikallinen palautus voi jäädä lyhyeksi.
- **Suunta:** ▼ (vain alaspäin); pääehdon `suunta` on `down`.
- **Miksi ei pelkkä volatiliteetti:** Sisältää vastakkaiset 120 min ja 10 min log-tuotot sekä tuoreen 3 min laskun; suuri σ15 yksin ei riitä.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Pitkä laskutausta | `vertailu` | `{     "lahde": "lasku120",     "operaattori": "<=",     "raja": "$taustalasku", }` | tapahtuma | ei | 1800 s |
| Vastaralli yhä näkyvissä | `vertailu` | `{     "lahde": "ralli10",     "operaattori": ">=",     "raja": "0.002", }` | ehto | ei | – |
| Vastaralli pettää | `vertailu` | `{     "lahde": "uusi_lasku3",     "operaattori": "<=",     "raja": "-0.001",     "suunta": "down", }` | ehto | kyllä | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `lasku120` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 7200, }` |
| `ralli10` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 600, }` |
| `uusi_lasku3` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 180, }` |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| `exchange` | `okx` | yksi sallittu arvo | LIIGAn vakioitu pörssi |
| `instrument` | `BTC-USDT` | `BTC-USDT`, `BTC-EUR`, `BTC-USDC` (LIIGA tutkii BTC-USDT:n) | Yhteinen skeema; tutkimuspari on BTC-USDT |
| `cooldown_seconds` | `5400` | ei naapurivarianttia | 90 min tauko rajaa enimmäistiheyden alle 20/vrk |
| `taustalasku` | `-0.010` | `-0.008`, `-0.010`, `-0.012` | Ennalta lukitut lähellä toisiaan olevat mekanismirajat. |

Yksi oma enum-parametri × kolme ennalta valittua arvoa = kolme LIIGA-varianttia. Parametrin kaikki arvot ovat merkkijonoja.

## Tarvittavat uudet palikat
- ei uusia

## Odotettu tiheys
- **0,4–1,0 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. 120 minuutin lasku ja 10 minuutin positiivinen vastaralli ovat vastakkaisia ehtoja, mutta 30 minuutin tapahtumaikkuna antaa käänteelle aikaa.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Alassuunnan tunnin etu katoaa volatiliteetti- ja kellonaikatäsmätyissä verrokeissa tai vain yksi taustalaskuraja tuottaa edun.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Onko 10 minuutin nettonousu yhdessä 3 minuutin laskun kanssa riittävä määritelmä vastarallin pettämiselle?
