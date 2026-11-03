# STROMO-BUILDER

Julkinen työtila **stromojen** kirjoittamiseen. Stromo on hälytys, joka etsii
BTC:n kauppavirrasta tilanteen, jonka jälkeen hinta liikkuu todennäköisemmin
tiettyyn suuntaan. Stromot kirjoitetaan täällä; ne testataan omistajan
yksityisessä STROMO4-ympäristössä vuoden kauppahistoriaa vasten samalla
moottorilla, joka ajaa niitä livenä.

Kirjoittajia ovat omistaja ja AI-istunnot (Claude, GPT). Tässä repossa ei ole
STROMO4:n sovelluskoodia, palvelimen tietoja eikä dataa.

## Mistä aloittaa

1. [OHJE.md](OHJE.md) – miten stromo viedään ideasta tulokseen huijaamatta itseään.
2. [PALIKAT.md](PALIKAT.md) – tiedoston tekninen muoto ja käytettävissä olevat palikat.
3. [malli.py](malli.py) ja [esimerkit/](esimerkit/) – lyhyet toimivat esimerkit.
4. [stromot/omistaja/](stromot/omistaja/) – kaksi täyttä stromoa (absorptio, pyyhkäisy).

## Rakenne

| Polku | Sisältö |
|---|---|
| `stromot/<tekijä>/` | Kunkin tekijän stromot, yksi tiedosto per stromo |
| `tulokset/<tekijä>/` | Omistajan ajamat tulokset (`summary.md`), vasta lukituksen jälkeen |
| `esimerkit/` | Rakenne-esimerkit; eivät ole tutkittavia stromoja |
| `KILPAILU_KIERROS1.md` | Kilpailun säännöt (kierros 1) |

## Työnkulku

1. Tekijä kirjoittaa stromon omaan haaraansa ja avaa PR:n (`stromot/<tekijä>/nimi.py`).
2. Omistaja mergeää PR:n: **merge-kommitti on lukitus.** Lukitun tiedoston
   parametreja tai logiikkaa ei muuteta; uusi idea = uusi tiedosto.
3. Omistaja ajaa yhden päivän tarkistuksen. Jos tiedosto kaatuu ennen ensimmäistä
   täyttä ajoa, tekijä saa korjata sen kerran (kirjataan PR:ään).
4. Omistaja ajaa kehitysjakson ja tallentaa tuloksen kansioon `tulokset/`.

## Säännöt lyhyesti

- Data: OKX BTC-USDT -kaupat (hinta, määrä, aggressorin puoli, ms-aikaleima). Ei orderbookia.
- Tulosmittari on lukittu (3A): hälytyksen suunnassa ±1σ15, 60 min, kumpi ensin, verrattuna satunnaisiin verrokkihetkiin.
- Koskematon jakso 1.8.–31.10.2026 on suljettu kaikilta; vain omistaja avaa sen kerran lukitulle stromolle.
- Parametreja ei säädetä tulosten perusteella.
