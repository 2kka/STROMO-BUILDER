# Trendimomentum saapuu valvonta-alueelle ▲▼

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX EEA: käyttäjän valitsema BTC-USDT / BTC-EUR / BTC-USDC

## Hypoteesi
- **Mekanismi:** Treidaaja merkitsee etukäteen hinnan, jonka läheisyydessä hän haluaa tarkistaa kaavion, CVD:n ja kirjan. Kun hinta saapuu alueelle selvän 15 minuutin nousu- **tai** laskumomentumin aikana ja spread on tavanomainen, tarkasteluhetki rajautuu paremmin kuin pelkällä tasohälytyksellä. Tämä on huomionkohdistus, ei long- eikä short-kehotus.
- **Suunta:** **▲** jos lähestymistapahtuman aikana vahvistunut Momentum ▲ on voimassa; **▼** jos Momentum ▼ on voimassa. Suunta kuvaa markkinamomentumia, ei sitä kummalta puolelta tasoa lähestyttiin. Näytetään hälytyksessä.
- **Miksi ei pelkkä volatiliteetti:** Vaatii käyttäjän oman hintatason lähestymisen, yksiselitteisen suunnallisen momentumtilan ja tavanomaisen spreadin.
- **Aikajänne:** Tason lähestymistä seuraavat 1–10 min; ei LIIGAn 3A-testiä.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Valvontatason lähestyminen | Hinta lähestyy tasoa | Etäisyys tasosta ≤ 0,15 %, sisäänmeno alueelle False→True | tapahtuma | kyllä | voimassa_s = 120 s |
| Momentum ▲/▼ | Momentum | 15 min muutos ≥ +1 × sigma15 = ▲ tai ≤ −1 × sigma15 = ▼; yksiselitteinen suunta | tila | ei | hystereesi_s = 30 s |
| Spread kunnossa | Spreadi suhteessa normaaliin | Spread < 3 × tämän parin normaali | ehto | ei | — |

**Suunnan sidonta:** Pääehto ilmoittaa tason lähestymisen; **Momentum-tilan merkki** määrää lopullisen ▲/▼-hälytyksen. Jos momentumtilaa ei ole tai suunta on epäselvä, ei kultaa. Pronssi = tasoa lähestytään; hopea = pääehto + momentum **tai** normaali spread; kulta = kaikki kolme. Yhteinen cooldown_seconds = 3600 s koskee molempia suuntia.

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Taso | käyttäjä asettaa | — (ei LIIGAa) | Vain treidaajan merkitsemä seurattava hinta |
| Lähestymisraja | 0,15 % | — (ei LIIGAa) | Riittävän kapea tarkastusalue ilman tarkkaa osumapakkoa |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Ei uusia markkinapalikoita: oma lähestymisehto, Momentum ▲/▼ ja spreadivertailu ovat käytettävissä. Hälytyksen ▲/▼-merkki sidotaan Momentum-tilan jo saatavaan suuntaan.

## Odotettu tiheys
- Arvio 0–6 kultahälytystä/vrk per pari ja seurattu taso molemmilla suunnilla yhteensä. Harvinaisuus syntyy oman tasoalueen ja suunnallisen momentumtilan päällekkäisyydestä; yhteinen cooldown_seconds = 3600 s. Arvio on testaamaton.

## Kumoava koe
- Jos hinta on koko ajan lähellä tasoa ja hälytys toistuu ilman uutta sisääntuloa tai momentummerkin näyttäminen ei auta erottamaan long-/short-skenaarion tilannetta, yhdistelmä ei toimi huomionkohdistajana.

## Avoimet kysymykset
- Lähestymisehto voi täyttyä kummalta tahansa puolelta tasoa. Käyttöliittymän tulee näyttää **sekä tason lähestymispuoli että Momentum ▲/▼**; ne eivät ole sama asia.
