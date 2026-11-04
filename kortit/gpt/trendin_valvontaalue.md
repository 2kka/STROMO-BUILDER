# Nousutrendi saapuu valvonta-alueelle ▲

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX EEA: käyttäjän valitsema BTC-USDT / BTC-EUR / BTC-USDC

## Hypoteesi
- **Mekanismi:** Treidaaja on merkinnyt etukäteen hinnan, jonka lähellä hän haluaa tarkastaa tilanteen. Kun hinta tulee alueelle edelleen vahvan 15 minuutin nousumomentumin aikana ja spreadi pysyy tavanomaisena, tilanne voi olla selkeämmin tulkittava kuin satunnainen tasokosketus. Tämä on huomionkohdistus, ei ostokehotus.
- **Suunta:** ▲ (nousumomentumin konteksti); hälytys ei väitä seuraavan liikkeen suuntaa.
- **Miksi ei pelkkä volatiliteetti:** Yhdistää henkilökohtaisen valvontatason, määritellyn nousumomentumin ja normaalin spreadin; volatiliteetti yksin ei riitä.
- **Aikajänne:** Tason lähestymisestä seuraavat 1–10 min; ei LIIGAn 3A-testiä.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Valvontatason lähestyminen | Hinta lähestyy tasoa | Etäisyys tasosta ≤ 0,15 %; sisäänmeno alueelle False→True | tapahtuma | kyllä | voimassa_s = 120 s |
| Nousumomentum | Momentum ▲ | 15 min nousu ≥ 1 × sigma15 | tila | ei | hystereesi_s = 30 s |
| Spread kunnossa | Spreadi suhteessa normaaliin | Nykyinen spread < 3 × oma normaali | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Taso | käyttäjä asettaa | — (ei LIIGAa) | Vain treidaajan merkitsemä seurattava hinta |
| Lähestymisraja | 0,15 % | — (ei LIIGAa) | Riittävän kapea tarkastusalue ilman tarkkaa osumapakkoa |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Ei uusia: lähestymisehto, Momentum ▲ ja spreadivertailu ovat tarjolla.

## Odotettu tiheys
- Arvio 0–5 kultahälytystä/vrk per pari ja seurattu taso; harvinaisuus syntyy ennalta asetetun tason ja momentumtilan päällekkäisyydestä. Lukittu hiljennys 3600 s; arviota ei ole mitattu.

## Kumoava koe
- Jos hälytykset ovat käytännössä jatkuvia aina hinnan ollessa tason lähellä tai normaalin spreadin ehto ei koskaan muuta huomiotilannetta, yhdistelmä ei kohdenna tarkastelua.

## Avoimet kysymykset
- Lähestymisehto voi täyttyä tason kummalta puolelta tahansa; käyttöliittymässä tulee näyttää nykyinen puoli, ettei tukea tulkita automaattisesti yläpuolelta testatuksi.
