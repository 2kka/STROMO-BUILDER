# Nousun tasanteelta irtoaminen

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA) · **Pari:** BTC-USDT (tutkimus)

## Hypoteesi
- **Mekanismi:** Nopean nousun jälkeen voittokotiutukset ja uudet ostot voivat tasapainottua hetkeksi ilman suurta palautusta. Lyhyt uusi nousu tämän tasanteen lopussa viittaisi ostajien palaamiseen ennen pidempää jatkoa.
- **Suunta:** ▲ (vain ylöspäin); pääehdon `suunta` on `up`.
- **Miksi ei pelkkä volatiliteetti:** Vaatii rajatun 15 min nettomuutoksen sekä uuden 3 min lähtöliikkeen, ei suurta absoluuttista hintavaihtelua.
- **Aikajänne:** seuraavat 60 min hälytyksestä; LIIGAn mittari on ±σ15, suunnassa tavoite ennen vastatavoitetta.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Yhteinen suuri nousu 60 min | `vertailu` | `{     "lahde": "nousu60",     "operaattori": ">=",     "raja": "$nousuraja", }` | tapahtuma | ei | 1800 s |
| Tasanne, alaraja | `vertailu` | `{     "lahde": "nousu15",     "operaattori": ">=",     "raja": "-0.002", }` | ehto | ei | – |
| Tasanne, yläraja | `vertailu` | `{     "lahde": "nousu15",     "operaattori": "<=",     "raja": "0.002", }` | ehto | ei | – |
| Uusi lähtö ylös | `vertailu` | `{     "lahde": "nousu3",     "operaattori": ">=",     "raja": "0.0012",     "suunta": "up", }` | ehto | kyllä | – |

Kaikki ehdot ovat yhtä aikaa tosia. Tapahtuma säilyy ilmoitetun sekuntimäärän, eikä jälkikäteen katsota tulevia havaintoja.

### TARVITSEE-solmut (riippuvuusjärjestyksessä)
| Solmu | Määrittely |
|---|---|
| `close` | `{     "kind": "series",     "field": "close",     "step": 60, }` |
| `nousu60` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 3600, }` |
| `nousu15` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 900, }` |
| `nousu3` | `{     "kind": "window",     "source": "close",     "op": "log_change",     "seconds": 180, }` |

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
- **0,5–1,0 hälytystä/vrk**, hypoteesipohjainen arvio ilman datan tai tulosten tarkastelua. Rajattu 15 min vaihtelu on nousun jälkeen mahdollinen, mutta 3 min uusi positiivinen lähtö tekee osumasta valikoivan.
- Tavoite vähintään 0,4 erillistä rypästä/vrk (vähintään 100 noin 9 kk:ssa); 5400 sekunnin cooldown rajaa yksittäisen stromon hälytykset alle 20/vrk. Hälytysarvio ei ole empiirinen tulos.

## Kumoava koe
- Tasanteen jälkeen yläsuunta ei ylitä σ15- ja kellonaikavakioituja verrokkeja tai vain yksi nousuraja on positiivinen.
- Kumoavia ovat myös alle 100 rypästä kehitysjaksolla tai se, että muiden naapurivarianttien reuna ei ole positiivinen.

## Avoimet kysymykset
- Onko tasanne 15 minuutin nettotuotolla riittävän erottuva ilmaus tasapainosta?
