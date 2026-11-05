# Likviditeettihaku 4 h (R-stromo, Claude, 5.11.2026)

**Hypoteesi:** stop- ja breakout-toimeksiannot kasautuvat edellisen 4 h ääripään taakse. Kun minuutin korkein/matalin ylittää 4 h ääripään vähintään 0,1·σ15 ja hinta sulkeutuu 5 minuutin sisällä takaisin rajan sisäpuolelle, ylitys oli likviditeetin haku eikä aito murto → hinta jatkaa pyyhkäisyä vastaan seuraavan tunnin.

**Suunta:** pyyhkäisyä vastaan (yläpään haun jälkeen ▼, alapään haun jälkeen ▲).

**Miksi ei pelkkä volatiliteetti:** vaatii epäonnistuneen ylityksen nimenomaisen tason yli; ylitys, joka pitää, ei hälytä.

**Alkuperä ja rehellisyys:** löytyi kehitysdatalla (11/2025–7/2026) alkuperäisen likviditeettihaun varianttina jakso = 14400: Treenileiri reuna +4,48 pp, 1 880 rypästä, z 2,70 (paritettu viikkoklusteri-SE). Naapurisääntö tappoi sen (24 h -variantti toivoton). Kehitysdatan vaiheet (Treenileiri, Dopingtesti) eivät ole tälle riippumaton näyttö. **Ainoa varsinainen testi on Kausi 2021-09–2025-10**, ja se lasketaan testibudjettiin yhdeksi testiksi. Monitestauksen huomio: ~65 testatun variantin paras z on sattumaltakin tyypillisesti 2,3–2,5.

**Parametrit:** jakso lukittu 14400 s, ei naapureita. Ei uusia palikoita.

**Kumoava koe:** Kausi-datalla reuna ≤ 0 tai alle Kauden rajan (Bonferroni-α oikealla keskivirheellä) → hylätään lopullisesti.
