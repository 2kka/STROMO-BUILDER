# Alueen keskikohdan palautus ▲

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA)
**Pari:** OKX BTC-USDT

## Hypoteesi
- **Mekanismi:** Lyhyen kaupankäyntialueen alaosaan jäänyt hinta voi palata kohti alueen keskikohtaa ilman että kyse on voimakkaasta uupumussignaalista. Jos minuutin sulku ylittää aiemman alueen keskipisteen normaalilla tai tavallista pienemmällä volyymilla, yksittäinen voimakas impulssi ei selitä koko palautusta. Hypoteesi koskee alueen sisäistä uudelleenhinnoittelua, ei ääriliikkeen vastakauppaa.
- **Suunta:** ▲; ylitys alapuolelta alueen keskikohdan yläpuolelle.
- **Miksi ei pelkkä volatiliteetti:** Keskeinen tapahtuma sidotaan edeltävän hinta-alueen korkeimman ja matalimman keskiarvoon, eikä vaadita poikkeuksellisen suurta liikettä; volyymille asetetaan yläraja.
- **Aikajänne:** Seuraavat 10–60 min; 3A ratkaisee +sigma15 vastaan −sigma15 ensimmäisen kosketuksen 60 minuutissa.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Alueen keskipisteen ylitys | Uusi: aluekeskipisteen ylitys | Aiemman alue_s:n (2700/3600/5400 s) suljettujen 1 min high/low-hintojen keskipiste; edellinen 1m close ≤ keskipiste ja nykyinen 1m close > sama keskipiste | tapahtuma | kyllä | voimassa_s = 120 s |
| Ei volyymiryöppyä | sum(volume, 300 s) vs percentile | 60 s BTC-volyymi; 5 min summa ≤ saman summalähteen 24 h p75 | ehto | ei | — |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| alue_s | 3600 s | 2700 s, 5400 s | 45–90 min riittää paikallisen vaihtelualueen määrittelyyn ilman päivätrendin tasoa |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- **Aluekeskipisteen ylitys:** laskee edeltävän (laukaisevan minuutin pois jättävän) alue_s:n suljettujen 60 s high-arvojen maksimin ja low-arvojen minimin puolivälin sekä tarkistaa, ylittääkö viimeisin suljettu 1m close sen alhaalta. Käyttää vain historiassakin olevaa kauppavirtaa (close, high, low, UTC-minuutit); ei katso tulevaan. Ei muita uusia palikoita.

## Odotettu tiheys
- Etukäteisarvio 1–8 hälytystä/vrk; keskipisteen alhaalta ylitys on tapahtuma, jota p75-volyymikatto rajaa. Kiinteä cooldown_seconds = 7200 s pitää enimmäismäärän 12:ssa/24 h. LIIGAn ≥ 100 rypään vaatimus jää todistettavaksi.

## Kumoava koe
- Jos keskipisteylityksen jälkeen 3A:n ▲-osuma ei ylitä verrokkeja tai reuna katoaa sigma15-/kellonaikatäsmäyksessä, kyseessä ei ole suunnallisesti käyttökelpoinen palautus. Myös naapurialueiden ≤ 0 reunat kumoavat robustiuden.

## Avoimet kysymykset
- Riittääkö pelkkä edeltävän alueen puoliväli mielekkääksi vertailutasoksi vai onko tapahtumia liian usein sivuttaisliikkeessä? Tätä ei ratkaista katsomalla kehitysdataa ennen lukitusta.
