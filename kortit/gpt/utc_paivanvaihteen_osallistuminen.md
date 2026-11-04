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
| UTC-päivänvaihde | Aikaikkunan alueen murto (alkuhetki-erikoistapaus) | UTC 00:00, joka päivä; pituus_min=0, ei aluetta/murtoa; tapahtuma voimassa alkuikkuna_min (20/30/40 min), vain suljetut 60 s havainnot | tapahtuma | kyllä | voimassa_s = alkuikkuna_min × 60 s |
| Hinta lähtee ylöspäin | log_change(close, 300 s) | 60 s suljettujen close-hintojen 5 min log-tuotto > 0 | ehto | ei | — |
| Kaupat osallistuvat | sum(count, 300 s) vs percentile | 60 s count; 5 min summa ≥ oman 24 h historian p50 | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| alkuikkuna_min | 30 min | 20 min, 40 min | Lähellä päivärajaa pysyvä, mutta täsmäsekunnin ajoitukselle epäherkkä ikkuna |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- **Ei erillistä uutta UTC-alkupalikkaa.** Käytetään Clauden kortissa [`kortit/claude/usa_avauksen_alueen_murto.md`](../claude/usa_avauksen_alueen_murto.md) kuvattua yleiskäyttöistä **aikaikkunan alueen murto** -palikkaa **alkuhetki-erikoistapauksena**, kuten Claude kortissaan ehdottaa: `alku=00:00`, `aikavyohyke=UTC`, `paivat=ma–su`, `pituus_min=0`, **ei aluetta eikä murtoehtoa**, `voimassa_min=alkuikkuna_min` (20/30/40). Palikka julkaisee UTC-ikkunan alun tapahtumana, jonka voimassaolo kattaa alkuikkunan; ▼-haaraa ei lisätä, koska tämä kortti pysyy **▲**.
- Jos yhteinen palikka ei vielä tue nollapituista aluetta, sen **samaan palikkaan** toteutetaan eksplisiittinen `alkuhetki`-toimintatapa. Nollaleveyksistä hinta-aluetta ei saa käsitellä vale-murtona. Vain kaupankäynnin UTC-aikaleimat ja suljetut 60 s näytteet; datakatko 00:00-rajalla estää takautuvan tapahtuman. Näin yksi toteutus palvelee molempia kortteja.

## Odotettu tiheys
- Etukäteisarvio 0–1 hälytystä/vrk; kunkin päivän ensimmäinen kaikki ehdot täyttävä osuma kuuluu enintään yhteen UTC-ikkunaan. Kiinteä cooldown_seconds = 86400 s rajaa myös voimassaolojakson aikana yhteen; 9 kk:ssa ≥ 100 rypästä on mahdollinen mutta epävarma.

## Kumoava koe
- Jos samaan UTC-kellonaikaan ja sigma15-tasoon täsmättyjen verrokkien 3A-osuma on yhtä hyvä tai parempi, päivänvaihteen osallistumisella ei ole erillistä suunnallista lisäarvoa. Naapuri-ikkunoiden epäpositiivinen reuna kumoaa myös robustiuden.

## Avoimet kysymykset
- Päivänvaihteen havainto voi puuttua katkon vuoksi; silloin yhteisen aikaikkunapalikan on jätettävä kyseisen päivän aloitustapahtuma tekemättä eikä se saa laukaista vanhaa hälytystä katkon jälkeen. Tarkistettava, että Clauden palikan `pituus_min=0` / `alkuhetki`-tila toteutetaan **ilman hintarajan murtovaatimusta** ja että tämän kortin suunta pysyy vain ▲.
