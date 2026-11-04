# Laskupyrähdyksen hintapaluu

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Nopeassa hintapudotuksessa kaupat voivat siirtyä hetkeksi alemmille tasoille ilman, että siellä oleva hinnoittelu pysyy vakaana. Viiden minuutin myönteinen muutos pudotustapahtuman jälkeen osoittaa hinnan palaavan kohti aiempia tasoja.
- **Suunta:** ▲ (vain ylöspäin); pääehdon `suunta` on `up`.
- **Miksi ei pelkkä volatiliteetti:** Vaatii erikseen 30 min negatiivisen log-tuoton tapahtumana ja palauttavan 5 min positiivisen log-tuoton, ei vain suuren volatiliteetin.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Terävä 30 min lasku | `vertailu` | `{     "lahde": "lasku30",     "operaattori": "<=",     "raja": "$laskuraja", }` | tapahtuma | ei | 1800 s |
| Viiden minuutin hintapaluu | `vertailu` | `{     "lahde": "paluu5",     "operaattori": ">=",     "raja": "0.002",     "suunta": "up", }` | ehto | kyllä | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `lasku30` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 1800, }` |
| `paluu5` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 300, }` |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| `exchange` | `okx` | yksi sallittu arvo | LIIGAn vakioitu pörssi |
| `instrument` | `BTC-USDT` | `BTC-USDT`, `BTC-EUR`, `BTC-USDC` (LIIGA tutkii BTC-USDT:n) | Yhteinen skeema; tutkimuspari on BTC-USDT |
| `cooldown_seconds` | `5400` | ei naapurivarianttia | 90 min tauko rajaa enimmäistiheyden alle 20/vrk |
| `laskuraja` | `-0.008` | `-0.006`, `-0.008`, `-0.010` | Ennalta lukitut lähellä toisiaan olevat mekanismirajat. |

Yksi oma enum-parametri × kolme ennalta valittua arvoa = kolme LIIGA-varianttia. Parametrin kaikki arvot ovat merkkijonoja.

## Tarvittavat uudet palikat
- ei uusia

## Odotettu tiheys
- **0,5–1,2 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. Terävä 30 min lasku on harvahko mutta palautumiseen on 30 min aikaa; viiden minuutin nousu rajaa tilannetta.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Hintapaluuta seuraava 60 min yläsuunta ei läpäise σ15:n ja kellonajan mukaan täsmättyjä verrokkeja tai naapurirajat ovat erisuuntaisia.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Palaako hinta jo 5 minuutin aikana niin pitkälle, että 60 min lisäetu jää olemattomaksi?
