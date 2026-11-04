# Kauppatiheyden nousuliike

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Uudet tai aktivoituvat osallistujat voivat synnyttää paljon erillisiä toteumia, jolloin hintamuutos leviää usean toimeksiannon yli. Tuoreen nousutuoton kanssa kauppojen lukumäärähuippu voi poiketa yhden suuren kaupan aiheuttamasta hintasiirtymästä.
- **Suunta:** ▲ (vain ylöspäin); pääehdon `suunta` on `up`.
- **Miksi ei pelkkä volatiliteetti:** Edellyttää 5 min kauppamäärän 90. persentiilin ylitystä ja erillistä 15 min positiivista tuottoa; ei perustu σ15:n kasvuun.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| 15 min nousuliike | `vertailu` | `{     "lahde": "nousu15",     "operaattori": ">=",     "raja": "$vauhti15",     "suunta": "up", }` | ehto | kyllä | – |
| Kauppojen huippulukumäärä | `vertailu` | `{     "lahde": "count5",     "operaattori": ">=",     "vastaan": "countp90", }` | ehto | ei | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `nousu15` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 900, }` |
| `count` | `{     "kind": "series",     "field": "count",     "step": 60, }` |
| `count5` | `{     "kind": "window",     "source": "count",     "op": "sum",     "seconds": 300, }` |
| `countp90` | `{     "kind": "percentile",     "source": "count5",     "seconds": 86400,     "p": "90", }` |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| `exchange` | `okx` | yksi sallittu arvo | LIIGAn vakioitu pörssi |
| `instrument` | `BTC-USDT` | `BTC-USDT`, `BTC-EUR`, `BTC-USDC` (LIIGA tutkii BTC-USDT:n) | Yhteinen skeema; tutkimuspari on BTC-USDT |
| `cooldown_seconds` | `5400` | ei naapurivarianttia | 90 min tauko rajaa enimmäistiheyden alle 20/vrk |
| `vauhti15` | `0.003` | `0.002`, `0.003`, `0.004` | Ennalta lukitut lähellä toisiaan olevat mekanismirajat. |

Yksi oma enum-parametri × kolme ennalta valittua arvoa = kolme LIIGA-varianttia. Parametrin kaikki arvot ovat merkkijonoja.

## Tarvittavat uudet palikat
- ei uusia

## Odotettu tiheys
- **0,6–1,6 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. 90. persentiili valitsee arviolta osan aktiivisista minuuteista; positiivinen 15 min hinnanmuutos karsii tästä osan.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Lisäosuma ylöspäin ei eroa saman σ15:n/kellonajan verrokeista tai on positiivinen vain yhdessä kolmesta tuottorajasta.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Erotteleeko count osallistumisen vai yhden pörssin raportointitavan muutokset?
