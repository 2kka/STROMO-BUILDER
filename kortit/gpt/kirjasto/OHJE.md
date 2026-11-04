# Käyttöstromokirjaston tulkinta- ja käyttöohje

**Tekijä:** gpt · **Päivä:** 2026-11-04

## Perusajatus

Avaa pikastromovalikosta vain ne pohjat, joille on senhetkinen kysymys. Valitse OKX-pari, oma hintataso tarvittaessa ja suunnallisessa pohjassa **long tai short**. Neljä pohjaa (#07–#10) sidotaan valittuun avoimeen positioon ja poistuvat position sulkeutuessa. Kirjasto huomauttaa ihmiselle; se ei avaa, sulje eikä muuta toimeksiantoja. Shortin riskit ja tulos tulevat valitun position tiedoista, vaikka markkinahavainto on spot-kauppavirrasta.

## Tyypilliset yhdistelmät

| Tilanne | Ota käyttöön | Pidä poissa ellei tarvetta |
|---|---|---|
| Päivän valmistelu | #01 omille etukäteen merkityille tuki/vastus-tasoille; yleisriskiksi #06 | Position pohjat, jos positiota ei ole |
| Long- tai short-entryn harkinta | #02 tasosulku **valittuun suuntaan**, tai #04 tason puolustus; yleisvaroitus #05 | Älä käynnistä jokaista entry-pohjaa samaan aikaan |
| Trendipäivä | #03 valittuun suuntaan + #05 toteutusriskille | Samat tasot useana päällekkäisenä pohjana |
| Rauhallinen, kapea markkina | #01 merkityille tasoille, #06 toteutusehtoihin | #03, jos varsinaista momentum-skenaariota ei ole |
| Avoin long | #07 TP, #08 SL, #09 R-palautuma, tarvittaessa #10 alkuperäisen signaalin muutos | Käyttäjän suunta = long vain näissä positioissa |
| Avoin short | Täsmälleen samat #07–#10 **short-position viitteellä**: TP alempana, SL ylempänä, vastainen CVD=ostopaine | Älä tulkitse shortin myötävirraksi positiivista CVD:tä |

Jokaisella pohjalla on oma cooldown; samanaikainen usean pohjan kulta voi silti synnyttää monta ääntä. Pidä yleensä **2–4 aktiivista pohjaa per pari** ja poista vanhentuneet kertakäyttöiset tasot. 24 tunnin kertakäyttöinen pohja päättyy 24 tunnissa tai ensimmäiseen kultaan. Positioon sidottu päättyy position mukana; toistuva jatkuu, kunnes se poistetaan. Jos position suunta tai koko muuttuu olennaisesti, arvioi sidonta uudelleen.

## Pronssi, hopea, kulta ja tapahtumavirta

- **Pronssi (hiljainen):** pääehto on tosi. Se kertoo, mihin katse kannattaa siirtää. Kulta ei ole vielä voimassa.
- **Hopea (hiljainen):** kolmesta ehdosta pääehto sekä yksi muista on tosi. Katso erityisesti **puuttuvaa** ehtoa; sen puute voi olla ratkaiseva. Kahden ehdon pohjissa ei ole hopeaa.
- **Kulta (ääni):** kaikki ehdot ovat tosia samalla voimassaolohetkellä. Avaa kynttilä, CVD, kirja, spread, nykyinen positio ja oma suunnitelma. **Kulta ei ole osto-, myynti- eikä shorttausmääräys.**
- **Virta:** yksittäiset ehtotapahtumat ja stromot ovat aikajärjestyksessä. Aikaisempi pronssi ei todista myöhempää kultaa. Tapahtuma on voimassa `voimassa_s` sekuntia, tilapalikka julkaistaan vasta `hystereesi_s`:n jälkeen.
- **Tuntematon tieto:** puuttuva data, vanha kirjanäkymä tai puuttuva positiosidonta ei vahvista ehtoa. Jos hintataso on jo kaukana tai edellinen 5m-sulku vanha, harkinta palautuu kaavioon.

## Milloin hälytystä ei pidä käyttää entryn tukena?

1. **Ohut / epävakaa kirja:** #05–#06 ovat varoituksia. Kulta #02–#04 ei kumoa kirjan, spreadin tai pörssiyhteyden riskiä.
2. **Väärä markkinatila tai konteksti:** momentumin ja piikkivolyymin yhteisesiintyminen ei ole laadukas entry itsessään. Huomioi regiiimi ja valittu hinta-alue.
3. **Väärä puoli:** long-skenaarion positiivinen CVD ei ole short-vahvistus. Shortissa TP ja SL ovat usein longiin nähden käänteisillä puolilla.
4. **Suunnitelma puuttuu:** ilman etukäteen sovittua riskiä tai stopia R-hälytys #09 on mieletön. Älä rakenna riskitasoa hälytyksestä.
5. **Pelkkä pronssi/hopea:** keskeneräiset ehdot eivät oikeuta kiirehtimään; hopea voi nimenomaan paljastaa ristiriidan.
6. **Kulta position SL:n lähellä:** #08 on lisävaroitus, ei syy siirtää, peruuttaa tai jättää asettamatta oikeaa stopia.

## Viikkotarkastus – mittaa päätösapua, älä väitettyä ennustuskykyä

Kirjaa jokaisesta tarkastetusta hälytyksestä: päivämäärä ja UTC-aika, pari, pohja, long/short tai puolineutraali, mahdollinen taso/position viite (ei tunnistetietoja julkiseen repoon), pronssi/hopea/kulta, puuttuneet ehdot, spread ja kirjan tila, tilanteen tulkinta, tehty **oma** päätös ja havaittu hyöty. Merkitse myös, jäikö hälytys täysin turhaksi, myöhäiseksi tai toistuvaksi.

Viikon lopussa vertaa **pohjittain ja erikseen long/short**:
- Mistä hälytyksistä tarkistit tosiasiallisesti suunnitelmaa, ja mitkä keskeyttivät turhaan?
- Mitkä olivat liian myöhäisiä? Mitkä tulivat vain ohuessa kirjassa?
- Muuttuiko oma päätöksenteko paremmaksi (suunnitelmassa pysyminen, riskin huomiointi) verrattuna vastaaviin tilanteisiin ilman hälytystä?
- Näyttikö pitkä pronssi/hopea oikeaa päätöskontekstia vai pelkkää teknistä osumatilaa?
- Tarvittavat lukumäärät: ehdon yksittäiset osumat, pronssit, hopeat, kullat, aktiiviset tunnit, cooldownin peittämät toistot; erota nämä toisistaan.

Älä päättele muutamasta kaupasta tilastollista ennustuskykyä. Testaamattomia rajoja ei muokata jälkikäteen voitollisten kauppojen mukaan; mahdollinen uusi versio kirjataan uutena ehdotuksena.

## Mitä kirjasto ei tee

Ei väitä ennustavan hintaa, korvaa kauppasuunnitelmaa, hallitse riskiä automaattisesti, laske pörssin todellista toteutusta, seuraa short-vipua spot-feedistä eikä tee kauppoja. Nykyinen `PALIKAT.md` kuvaa vanhan palikkastromon teknistä muotoa; näiden 2.H-e-pohjien sanakirjamuoto on **toivottu deklaratiivinen rajapinta**, jonka toimivuus ja positojen linkitys tulee erikseen hyväksyä ennen live-käyttöä.
