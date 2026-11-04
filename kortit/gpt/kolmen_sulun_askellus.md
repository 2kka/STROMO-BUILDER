# Peräkkäisten sulkujen askellus ▲▼

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA)
**Pari:** OKX BTC-USDT

## Hypoteesi
- **Mekanismi:** Hitaasti ostava tai myyvä osallistuja voi jakaa toimeksiantonsa peräkkäisiin minuuttieriin yhden purskeen sijasta. Usean suljetun minuutin johdonmukainen nousu (▲) tai lasku (▼) yhdessä tavanomaista suuremman kauppatapahtumien määrän kanssa voi kuvata jatkuvaa osallistumista ilman yksittäistä hintahyppyä. Kyse on etukäteen muodostetusta jatkuvuushypoteesista, ei tunnetusta ennusteesta.
- **Suunta:** **▲** kun kaikki peräkkäiset 1 minuutin log-tuotot ovat > 0; **▼** kun kaikki ovat < 0. Merkki lasketaan pääehdosta ja annetaan jokaiselle hälytykselle, ei erillistä long-/short-parametria.
- **Miksi ei pelkkä volatiliteetti:** Vaatii samanmerkkisten peräkkäisten minuuttisulkujen sarjan sekä 24 h omaan jakaumaan verratun kauppalukumäärän; suuri kokonaisliike ei yksin riitä.
- **Aikajänne:** Seuraavat 15–60 min; 3A mittaa ▲-hälytyksestä +sigma15 ennen −sigma15 ja ▼-hälytyksestä −sigma15 ennen +sigma15, 60 minuutissa.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Yhtämittainen askellus ▲/▼ | min ja max 1m log-tuottoikkunasta; suunnattu tapahtuma | Suljetut 60 s close-arvot; `r = log_change(close, 60 s)`. Viimeisen askellus_s:n (120/180/240 s) `min(r) > 0` = ▲, **tai** `max(r) < 0` = ▼. Merkki tunnistetaan False→True-muutoksesta suuntakohtaisesti. | tapahtuma | kyllä | voimassa_s = 60 s |
| Osallistuminen | sum(count, askellus_s) vs percentile | 60 s count; viimeisen askellus_s:n summa ≥ saman summalähteen 24 h p70, sama kynnys kummallekin merkille | ehto | ei | — |

**Suunnan sidonta ja LIIGA:** Pääehto palauttaa ▲/▼ yksikäsitteisesti; min > 0 ja max < 0 eivät voi olla samanaikaisesti tosia. Kulta tarvitsee osallistumisehdon lisäksi **tämän** pääehdon suunnan; 3A arvioidaan tapahtumamerkin suuntaan. Yhteinen cooldown_seconds = 5400 s koskee molempia, ei kahta erillistä stromo-instanssia. Naapurit 120/240 s ovat samat sekä ▲- että ▼-puolella; raportoi kummankin suunta erikseen ilman tulosten perusteella tapahtuvaa puolen valintaa.

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| askellus_s | 180 s | 120 s, 240 s | 2–4 peräkkäistä minuuttia testaa lyhyttä, mutta ei yksittäiseen tikkiin perustuvaa askellusta |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Uutta kauppadatasarjaa ei tarvita: 60 s close/count, `log_change`, `min`, `max`, `sum` ja `percentile` riittävät. **Suunnattu askellustapahtuma** on näistä koostettava pieni kaksisuuntainen vertailupalikka (tai 2.H-e:n suunnattu OR-kooste), joka palauttaa merkin ▲/▼ ja False→True-tapahtuman. Jos deklaratiivinen moottori ei tue suunnan palautusta olemassa olevista palikoista, tämä johdettu palikka on lisättävä; lasketaan vain suljetuista kauppaminuuteista.

## Odotettu tiheys
- Etukäteisarvio 3–14 kultahälytystä/vrk molemmat suunnat yhteensä; peräkkäiset samanmerkkiset minuutit ja p70-kauppalukumäärä rajaavat tapauksia. Yhteinen cooldown_seconds = 5400 s rajaa enintään 16 kultaan/24 h (Try out ≤ 200, Treenileiri ≤ 20). LIIGAn ≥ 100 rypästä 9 kk:ssa on tavoite, ei oletettu tulos.

## Kumoava koe
- Jos 3A:n molempiin suuntiin oikein merkitty yhdistetty reuna on ≤ 0 satunnaisiin tai sigma15-/kellonaikatäsmättyihin verrokkeihin nähden, jatkuvuushypoteesi ei saa tukea. Jos 120/240 s -naapurit eivät pysy samaan suuntaan tai toinen hälytyssuunta heikentää tulosta, sitä ei saa jälkikäteen poistaa saman testin puitteissa.

## Avoimet kysymykset
- Tarkista, että False→True muodostuu vain **uusista suljetuista 60 s** minuuteista, eikä sama 60 s tapahtuma säily vanhana seuraavaan päätökseen. Suuntien tulosten erittely on diagnostiikkaa, ei peruste muuttaa lukittua kaksisuuntaista korttia.
