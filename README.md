# STROMO-BUILDER

Julkinen työtila **stromojen** kirjoittamiseen. Stromo on hälytys, joka etsii
BTC:n kauppavirrasta tilanteen, jonka jälkeen hinta liikkuu todennäköisemmin
tiettyyn suuntaan. Stromot kirjoitetaan täällä; ne testataan omistajan
yksityisessä STROMO4-ympäristössä vuoden kauppahistoriaa vasten samalla
moottorilla, joka ajaa niitä livenä.

Kirjoittajia ovat omistaja ja AI-istunnot (Claude, GPT). Tässä repossa ei ole
STROMO4:n sovelluskoodia, palvelimen tietoja eikä dataa.

## 🏆 Hall of Fame

<!-- HOF:START -->
| # | Tekijä | Stromo | Variantti | Reuna pp | Kynnys pp | Rypäät | Vaihe |
|---|---|---|---|---:|---:|---:|---|
| 🥇 | claude | likviditeettihaku | jakso 14400 | 4,48 | 2,31 | 1880 | Treenileiri: karsittu: naapuri |
| 🥈 | gpt | virtakaannos | virtaraja 97 | 7,39 | 6,02 | 276 | Dopingtesti: karsittu |
| 🥉 | omistaja | absorptio | ikkuna 600 | 3,73 | 3,39 | 871 | Treenileiri: karsittu: naapuri |
| 4 | claude | isot_liput | maara_p 50 | 4,32 | 5,60 | 319 | Treenileiri: karsittu: reuna |
| 5 | gpt | virtakaannos | virtaraja 95 | 3,35 | 4,34 | 531 | Treenileiri: karsittu: reuna |

Mitattu 13 varianttia. Läpäisy vaatii reunan ≥ kynnyksen (suhde ≥ 1) ja naapurivariantin plussalla. Päivittyy LIIGAn yöajosta.
<!-- HOF:END -->

## Mistä aloittaa

1. [OHJE.md](OHJE.md) – miten stromo viedään ideasta tulokseen huijaamatta itseään.
2. [PALIKAT.md](PALIKAT.md) – tiedoston tekninen muoto ja käytettävissä olevat palikat.
3. [malli.py](malli.py) ja [esimerkit/](esimerkit/) – lyhyet toimivat esimerkit.
4. [stromot/omistaja/](stromot/omistaja/) – kaksi täyttä stromoa (absorptio, pyyhkäisy).

## Rakenne

| Polku | Sisältö |
|---|---|
| `stromot/<tekijä>/` | Kunkin tekijän stromot, yksi tiedosto per stromo |
| `esimerkit/` | Rakenne-esimerkit; eivät ole tutkittavia stromoja |
| `KILPAILU_KIERROS1.md` | Kilpailun säännöt (kierros 1) |
| `LIIGA.md`, `liiga/` | Karsinta Try outista Näytösotteluun ja sen ajuri |
| `tilastot/` | LIIGAn kirjanpito ja raportit (pelikone vie PR:nä) |
| `tyokalut/` | Kierroskohtaiset apuskriptit |

## Työnkulku

1. Tekijä kirjoittaa stromon omaan haaraansa ja avaa PR:n (`stromot/<tekijä>/nimi.py`).
2. Omistaja mergeää PR:n: **merge-kommitti on lukitus.** Lukitun tiedoston
   parametreja tai logiikkaa ei muuteta; uusi idea = uusi tiedosto.
3. Omistaja ajaa yhden päivän tarkistuksen. Jos tiedosto kaatuu ennen ensimmäistä
   täyttä ajoa, tekijä saa korjata sen kerran (kirjataan PR:ään).
4. LIIGA ajaa vaiheet ([LIIGA.md](LIIGA.md)); tulokset kansioon `tilastot/`.

## Säännöt lyhyesti

- Data: OKX BTC-USDT -kaupat (hinta, määrä, aggressorin puoli, ms-aikaleima). Ei orderbookia.
- Tulosmittari on lukittu (3A): hälytyksen suunnassa ±1σ15, 60 min, kumpi ensin, verrattuna satunnaisiin verrokkihetkiin.
- Koskematon jakso 1.8.–31.10.2026 on suljettu kaikilta; vain omistaja avaa sen kerran lukitulle stromolle.
- Parametreja ei säädetä tulosten perusteella.
