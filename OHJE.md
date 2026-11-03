# Stromon tekeminen

Tekninen muoto on [PALIKAT.md](PALIKAT.md): yksi tiedosto, metatiedot
literaaleina, `TARVITSEE`-palikat ja puhdas `ehto(ctx)`. Tämä ohje kertoo,
miten stromo viedään ideasta tulokseen niin, ettei tutkimus huijaa itseään.

## Prosessi

1. **Lähde ilmiöstä, ei datasta.** Kirjoita tiedoston alkuun docstring: kuka
   markkinalla toimii, miksi hinnan pitäisi reagoida, odotettu suunta ja miksi
   stromo ei ole pelkkä volatiliteetin tunnistin.
2. **Lukitse ennen ensimmäistä ajoa:** oletusparametrit ja enintään kaksi
   naapurivarianttia enum-valintoina (ks. `stromot/omistaja/absorptio.py`).
   Uusi variantti tulosten jälkeen on uusi stromo ja kasvattaa testien määrää.
3. **Tarkistus:** omistaja ajaa yhden päivän tarkistuksen (rakenne, parametrit,
   live = replay, hälytyksiä/vrk). Korjaus on sallittu vain ennen ensimmäistä
   täyttä ajoa ja vain, jos tarkistus kaatuu tai stromo ei tee sitä, mitä
   docstring sanoo.
4. **Ajo** BTC-USDT:llä kehitysjaksolla 2025-11-01 – 2026-07-31.
   Koskematon jakso 2026-08-01 – 2026-10-31 on suljettu.
5. **Läpäisy kehitysjaksolla:**
   - vähintään 100 rypästä (alle 60 min välein tulleet hälytykset = yksi rypäs)
   - tavoite ensin -osuus − verrokit ≥ 130/√rypäät prosenttiyksikköä
     (enintään kuusi rinnakkaista testiä; useammalla kynnystä nostetaan)
   - enintään 20 hälytystä vuorokaudessa
   - naapurivariantti samaan suuntaan (ei vain yksi onnekas parametriarvo)
6. **Läpäissyt jatkaa:** validointijakso 2021-09-01 – 2025-10-31 samalla
   kriteerillä → koskematon jakso kerran → varjotila livessä.
7. **Kaupankäyntikelpoinen** vasta, kun osuma ylittää 50 % + kulut/(2σ).

## Tulosmittari 3A (lukittu)

Hälytyshetken hinnasta p asetetaan hälytyksen suuntaan tavoite p·exp(+σ) ja
stop p·exp(−σ). Kumpi kauppahinta osuu ensin 60 minuutin aikana (päätehetki
mukana)? σ on 96 edellisen sulkeutuneen UTC-vartin log-tuottojen
otoskeskihajonta (n−1), sama kuin palikka `sigma15`. Samassa millisekunnissa
molemmat = epäselvä; ei osumaa = ei ratkea. Verrokit ovat satunnaisia hetkiä
samalta jaksolta. Suunnaton stromo (`direction=None`) ei saa osumaprosenttia.

Tulkinta: noin 50 % on kolikonheitto. Reuna on vasta, kun osuus ylittää
verrokit enemmän kuin satunnaisvaihtelu selittää (kynnys yllä).

## Tunnetut tulokset (kehitysjakso, BTC-USDT)

- **Nopea liike** (hinta liikkuu 0,1 % 10 sekunnissa): tavoite ensin 51,2 % vs.
  verrokit 50,7 %. Tunnistaa volatiliteettia, ei suuntaa. Noin 110 hälytystä/vrk.
- **Nopea liike 0,35 % / 180 s:** +3,2 pp verrokkeihin, raja noin 3,0 pp.
  Rajatapaus; naapurivariantit ajamatta.
- **Murto** (1 min päätös yli/alle 60 min korkeimman/matalimman, volyymi- ja
  CVD-vahvistus tai sen puute): ei erottunut verrokeista. Toissijainen havainto:
  murron jälkeen hinta oli murron suuntaan vain 44–46 % kerroista (verrokit ~50 %).

## Hyvä stromo

- Harvinainen ja tarkka, ei yleinen: 1–20 hälytystä vuorokaudessa.
- Ehto, joka kertoo **suunnasta**, ei vain siitä että jotain tapahtuu.
- Kynnykset suhteessa markkinan omaan tilaan (`sigma15`, `percentile`), ei kiinteinä dollareina.
- Ei tulevaisuuteen kurkistamista: päätös vain jo sulkeutuneista näytteistä.
