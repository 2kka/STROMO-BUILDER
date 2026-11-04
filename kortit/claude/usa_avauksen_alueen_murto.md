# USA:n avauksen alueen murto ▲▼

**Tekijä:** claude · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA)
**Pari:** OKX BTC-USDT

## Hypoteesi
- **Mekanismi:** Yhdysvaltain osakemarkkinan avaus (9.30 New Yorkin aikaa) tuo BTC:hen päivän suurimman yksittäisen uuden osallistujajoukon: spot-ETF-virrat ja niiden kattaminen, osakemarkkinan riskiasenteen siirtyminen kryptoon, makrouutisten jälkeinen uudelleenhinnoittelu. Avauksen ensimmäisellä jaksolla markkina etsii hintaa ja muodostaa alueen. Kun hinta sulkeutuu alueen ulkopuolelle samalla kun aggressiivinen virta tukee suuntaa, avauksen osallistujien enemmistö on valinnut puolensa, ja suunta jatkuu tyypillisesti seuraavan tunnin ajan. Tämä on intraday-treidaajien "opening range breakout", sovitettuna siihen hetkeen, jolloin BTC:n osallistujarakenne muuttuu eniten.
- **Suunta:** ▲ ylärajan murrossa, ▼ alarajan murrossa. Vain ensimmäinen murto per päivä.
- **Miksi ei pelkkä volatiliteetti:** Laukaisu on sidottu yhteen kalenterihetkeen (USA:n avaus, kesäajat huomioiden) ja sen jälkeen syntyneeseen alueeseen, ei mihin tahansa suureen liikkeeseen. Lisäksi vaaditaan, että aggressiivinen virta (delta) on samaan suuntaan kuin murto, eli liike ei synny pelkästä ohuesta kirjasta. Kumoava koe täsmää verrokit samaan kellonaikaan ja volatiliteettiin.
- **Aikajänne:** Murrosta seuraavat 60 min (tulosmittari 3A, ±σ15).

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Avausalueen murto | Uusi: aikaikkunan alueen murto | Ikkuna alkaa 9.30 America/New_York (arkipäivät ma–pe), pituus `alue_min`; alue = ikkunan suljettujen 1 min high-maksimi ja low-minimi. Murto = ensimmäinen ikkunan jälkeinen suljettu 1 min close > ylä tai < ala, viimeistään 180 min avauksesta. Suunta murron mukaan. Kerran päivässä. | tapahtuma | kyllä | voimassa_s = 60 |
| Virta tukee | window sum(delta, 300 s) | 60 s delta; viimeisen 5 min summa > 0 ▲-murrossa, < 0 ▼-murrossa (sama suunta kuin murto) | ehto | ei | – |
| Alue ei ole kohinaa | Uusi (osa samaa palikkaa): alueen leveys / σ15 | Alueen leveys (ylä − ala) / alarajan hinta ≥ 0,5 × σ15 avaushetkellä | ehto | ei | – |

Laukeaa, kun kaikki kolme ovat tosia. Pronssi = murto, hopea = murto + toinen kahdesta.

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| alue_min | 30 | 15, 60 | 15–60 min on ORB:n vakiintunut vaihteluväli; 30 min kattaa avauksen ensimmäisen hinnanetsinnän |

Yksi säädettävä parametri; arvot lukitaan ennen ajoa.

## Tarvittavat uudet palikat
- **Aikaikkunan alueen murto** (yleiskäyttöinen, käy myös muihin istuntoihin kuten Lontoon tai Aasian avaukseen): parametrit `alku` (kellonaika), `aikavyohyke` (IANA, esim. America/New_York, kesäaika automaattisesti), `paivat` (ma–pe), `pituus_min`, `voimassa_min`. Laskee ikkunan suljettujen 1 min high/low-arvojen ylä- ja alarajan, julkaisee murron ensimmäisestä ikkunan jälkeisestä 1 min sulusta rajan ulkopuolella (suunta mukana) ja alueen leveyden. Käyttää vain suljettuja kauppaminuutteja; jos ikkunassa on katko, alue on tuntematon eikä murtoa synny sinä päivänä. Toimii historiassa ja livessä samoin.
- GPT:n kortin "UTC-aikaikkunan alkaminen" voi olla saman palikan erikoistapaus (pituus 0, ei aluetta), joten yksi palikka riittää molempiin.

## Odotettu tiheys
- Enintään 1 hälytys arkipäivää kohti, arviolta 0,5–0,8 per arkipäivä (kaikkina päivinä alue ei murru 3 tunnin sisällä, virta ei aina tue, kapea alue suodattuu). Treenileiri 11/2025–7/2026 ≈ 190 arkipäivää → arviolta 100–150 rypästä. Rajalla, mutta kaksisuuntaisuus ja arkipäivien määrä riittävät todennäköisesti 100 rypään vaatimukseen. Tiheysraja ≤ 20/vrk ei koskaan ylity.

## Kumoava koe
- Täsmää verrokit **samaan kellonaikaan (avausta seuraavat 3 h) ja σ15-tasoon**. Jos murron 3A-osuma ei ylitä täsmättyjä verrokkeja, reuna on pelkkää avauksen volatiliteettia eikä alueen murron informaatiota.
- Peilikoe: sama palikka Aasian avaukseen (esim. 9.00 Asia/Tokyo). Jos reuna on yhtä suuri kellonajasta riippumatta, mekanismi ei liity USA:n osallistujiin vaan yleiseen murtoon, jolloin hypoteesi on väärä, vaikka tulos olisi hyvä.
- Naapurit 15 ja 60 min samaan suuntaan; muuten tulos on yksittäisen parametrin onnea.

## Avoimet kysymykset
- USA:n pyhäpäivät (pörssi kiinni): suodatetaanko kiinteällä pörssikalenterilla vai hyväksytäänkö niiden kohina? Ehdotus: kiinteä NYSE-kalenteri palikan asetuksena, lukitaan ennen ajoa.
- Kausidata 2021–2023: spot-ETF:t alkoivat 1/2024, joten mekanismin osa (ETF-virrat) puuttuu varhaisilta kausilta. Kausitestin pitäisi näyttää heikompi reuna ennen 2024 kuin sen jälkeen, mikä on itsessään testattava ennuste (ei tulosten perusteella tehty selitys).
