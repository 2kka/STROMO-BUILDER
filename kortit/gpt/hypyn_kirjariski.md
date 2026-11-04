# Hintahypyn kirjariski ⚠

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX EEA: käyttäjän valitsema BTC-USDT / BTC-EUR / BTC-USDC

## Hypoteesi
- **Mekanismi:** Nopea hinnan muutos voi saada treidaajan kiirehtimään. Jos samalla spreadi kasvaa ja ±0,5 %:n tarjouskirjasyvyys pienenee, näkyvä likviditeetti tukee toteutusta tavallista heikommin. Hälytys on varoitus mahdollisesta toteutusriskistä, ei hintasuunnan ennuste.
- **Suunta:** Kumpikin; sama hälytys koskee sekä ylös- että alaspäin tehtyä hintahyppyä, eikä ehdota kauppasuuntaa.
- **Miksi ei pelkkä volatiliteetti:** Hinnan nopeus ei riitä: lisäksi kaksi erillistä, vain livessä mitattavaa kirjan laadun poikkeamaa.
- **Aikajänne:** Heti, seuraavat sekunnit–minuutit; ei LIIGAn 3A-testiä.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Hintahyppy | Hintahyppy ± | Hinta muuttuu ≥ 0,2 % kumpaan tahansa suuntaan 30 sekunnissa | tapahtuma | kyllä | voimassa_s = 90 s |
| Leventynyt spread | Spreadi suhteessa normaaliin | Spread ≥ 3 × normaali | tila | ei | hystereesi_s = 10 s |
| Vetäytynyt syvyys | Kirjasyvyys suhteessa normaaliin | Keskihinnan ±0,5 %:n syvyys ≤ 0,5 × normaali | tila | ei | hystereesi_s = 10 s |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Ei säädettäviä | Valmiit normaalirajat | — | Yhtenäinen varoitustaso kaikille seurattaville pareille |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Ei uusia: hintahyppy, spreadin normaali ja syvyyden normaali ovat käytettävissä.

## Odotettu tiheys
- Arvio 0–3 kultahälytystä/vrk per pari tavanomaisessa seurannassa; kahden kirjahäiriön yhtäaikaisuus rajaa määrää. Hiljennys 3600 s. Stressipäivinä enemmänkin on mahdollista; arviota ei ole testattu.

## Kumoava koe
- Jos spreadi ja syvyys eivät hälytyshetkellä eroa merkityksellisesti normaalista tai niiden samanaikaisuus ei auta käyttäjää tunnistamaan toteutusriskiä, varoituksen peruste ei toteudu.

## Avoimet kysymykset
- Kirjan normaaliarvot ja niiden saatavuus on varmistettava live-parikohtaisesti; historiallista LIIGA-testia ei voi tehdä ilman book-historiaa.
