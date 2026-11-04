# UTC-päivänvaihteen osallistuminen ▲

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA)
**Pari:** OKX BTC-USDT

## Hypoteesi
- **Mekanismi:** UTC-vuorokauden vaihdos on yhteinen aikaraja, jota osa kaupankäynti- ja kirjanpitojärjestelmistä voi käyttää erien ajoittamiseen. Jos uuden UTC-päivän alkupuolen hinta on viidessä minuutissa nousussa ja kauppojen määrä on ainakin tavanomainen, samanaikaiset ajastetut toimet saattavat tukea lyhyttä jatkoa. Tämä on kokeiltava ajoitushypoteesi, ei havaittu markkinaetu.
- **Suunta:** ▲; vain positiivinen suljettu 5 min hintamuutos.
- **Miksi ei pelkkä volatiliteetti:** Yhdistelmä vaatii tietyn UTC-vuorokauden vaihtumisen, hinnan suunnan ja vähintään mediaanitason kauppamäärän; voimakas hintavaihtelu yksin ei laukaise sitä.
- **Aikajänne:** Uuden UTC-päivän alkua seuraavat 15–60 min; 3A mittaa 60 min ja ±sigma15.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| UTC-päivänvaihde | Uusi: UTC-aikaikkunan alkaminen | Suljettujen 60 s näytteiden kauppa-aikaleima; kerran vuorokaudessa UTC 00:00 avautuva ikkuna, kesto alkuikkuna_min (20/30/40 min) | tapahtuma | kyllä | voimassa_s = alkuikkuna_min × 60 s |
| Hinta lähtee ylöspäin | log_change(close, 300 s) | 60 s suljettujen close-hintojen 5 min log-tuotto > 0 | ehto | ei | — |
| Kaupat osallistuvat | sum(count, 300 s) vs percentile | 60 s count; 5 min summa ≥ oman 24 h historian p50 | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| alkuikkuna_min | 30 min | 20 min, 40 min | Lähellä päivärajaa pysyvä, mutta täsmäsekunnin ajoitukselle epäherkkä ikkuna |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- **UTC-aikaikkunan alkaminen:** tunnistaa suljettujen 60 s kauppanäytteiden UTC-aikaleimasta vuorokauden 00:00-rajan ja muodostaa sen jälkeen määräajan voimassa olevan tapahtuman. Jos data puuttuu rajalta, se ei saa keksiä tapahtumaa takautuvasti. Käyttää pelkkää historiassa ja livessä olevaa kauppojen aikaleimaa; ei seinäkelloa tai kirjaa.

## Odotettu tiheys
- Etukäteisarvio 0–1 hälytystä/vrk; kunkin päivän ensimmäinen kaikki ehdot täyttävä osuma kuuluu enintään yhteen UTC-ikkunaan. Kiinteä cooldown_seconds = 86400 s rajaa myös voimassaolojakson aikana yhteen; 9 kk:ssa ≥ 100 rypästä on mahdollinen mutta epävarma.

## Kumoava koe
- Jos samaan UTC-kellonaikaan ja sigma15-tasoon täsmättyjen verrokkien 3A-osuma on yhtä hyvä tai parempi, päivänvaihteen osallistumisella ei ole erillistä suunnallista lisäarvoa. Naapuri-ikkunoiden epäpositiivinen reuna kumoaa myös robustiuden.

## Avoimet kysymykset
- Päivänvaihteen voi havaita myöhässä katkon vuoksi; tapahtuma tulee jättää väliin eikä jälkikäteisellä näytteellä saa antaa vanhaa hälytystä.
