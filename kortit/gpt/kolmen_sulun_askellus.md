# Peräkkäisten sulkujen askellus ▲

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA)
**Pari:** OKX BTC-USDT

## Hypoteesi
- **Mekanismi:** Hitaasti ostava osallistuja voi jakaa toimeksiantonsa useaan minuuttierään sen sijaan, että ostaisi yhdellä purskeella. Jos useat peräkkäiset suljetut minuutit päätyvät aina edellistä ylemmäs ja kauppojen määrä on keskimääräistä vilkkaampi, pienet positiiviset hintamuutokset voivat jatkua ilman yksittäistä rajua hyppyä. Tämä on etukäteen asetettu jatkuvuushypoteesi.
- **Suunta:** ▲; jokainen hälytys arvioidaan ylöspäin.
- **Miksi ei pelkkä volatiliteetti:** Vaatii jokaiselta peräkkäiseltä minuutilta positiivisen sulkutuoton (ei vain suuren kokonaisliikkeen) sekä lukumääräisen osallistumisen suhteessa omaan jakaumaan.
- **Aikajänne:** Seuraavat 15–60 min; 3A mittaa 60 minuutin sisällä +sigma15- ja −sigma15-kosketusten järjestyksen.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Yhtämittainen askellus | min(log_change(close, 60 s), askellus_s) | 60 s sulut; jokaisen viimeisen askellus_s-jakson 1 min log-tuotto > 0; askellus_s = 120/180/240 s | tapahtuma | kyllä | voimassa_s = 60 s |
| Osallistuminen | sum(count, askellus_s) vs percentile | 60 s count; viimeisen askellus_s:n kauppojen summa ≥ oman 24 h historian p70 samalla lähteellä | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| askellus_s | 180 s | 120 s, 240 s | 2–4 peräkkäistä minuuttia testaa lyhyttä, mutta ei yksittäiseen tikkiin perustuvaa askellusta |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Ei uusia. Käytetään 60 s close- ja count-sarjoja, window-operaatioita ja 24 h liukuvaa persentiiliä.

## Odotettu tiheys
- Etukäteisarvio 2–12 kultahälytystä/vrk; peräkkäiset positiiviset minuutit ja p70-kauppalukumäärä rajaavat tilanteita. Kiinteä cooldown_seconds = 5400 s antaa enintään 16 hälytystä/24 h (Try out ≤ 200, Treenileiri ≤ 20). Vähintään 100 rypästä 9 kk:ssa on tavoite, ei oletettu tulos.

## Kumoava koe
- Jos 3A-reuna on ≤ 0 satunnaisiin tai sigma15:n ja UTC-kellonajan mukaan täsmättyihin verrokkeihin verrattuna tai 120/240 s -naapurit eivät osoita samaa suuntaa, askellus ei täytä LIIGAn hypoteesia.

## Avoimet kysymykset
- Peräkkäisten sulkujen ehdon False→True pitää arvioida vain uusilla suljetuilla 60 s näytteillä; kesken minuutin kauppahintaa ei saa käyttää.
