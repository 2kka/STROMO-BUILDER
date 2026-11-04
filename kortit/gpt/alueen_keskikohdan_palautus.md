# Alueen keskikohdan palautus ▲▼

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA)
**Pari:** OKX BTC-USDT

## Hypoteesi
- **Mekanismi:** Lyhyen kaupankäyntialueen reunapuolelle siirtynyt hinta voi palata alueen keskikohdan yli tai ali, kun hinta arvioidaan uudelleen ilman voimakasta yksittäistä volyymiryöppyä. Suljetun minuutin keskipisteen ylitys alhaalta tai alitus ylhäältä on selkeä, molemmille puolille samaa logiikkaa noudattava tapahtuma. Hypoteesi koskee alueen sisäistä uudelleenhinnoittelua, ei kierroksen 1 uupumusstromon uudelleensäätöä.
- **Suunta:** **▲** jos 1m close ylittää aiemman alueen keskikohdan alhaalta, **▼** jos se alittaa sen ylhäältä. Pääehdon murtosuunta kirjataan kullekin hälytykselle; molemmat kuuluvat samaan stromoon ja samoihin parametritesteihin.
- **Miksi ei pelkkä volatiliteetti:** Vertailutaso on vain menneistä high/low-hinnoista laskettu keskipiste ja 5m volyymille asetetaan yläraja; suuren liikkeen tunnistin ei riitä.
- **Aikajänne:** Seuraavat 10–60 min; 3A vertailee suunnassa ▲ (+sigma15 ennen −sigma15) tai suunnassa ▼ (−sigma15 ennen +sigma15) 60 minuutin sisällä.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Aluekeskipisteen ylitys/alitus ▲/▼ | Uusi: kaksisuuntainen aluekeskipisteen leikkaus | Edeltävän alue_s:n (2700/3600/5400 s) suljettujen 1m high/low-minuuttien keskipiste **M** (laukaiseva minuutti pois). ▲: edellinen 1m close ≤ M ja uusi > M. ▼: edellinen ≥ M ja uusi < M. Molemmissa **sama ennen laukaisua lukittu M**. | tapahtuma | kyllä | voimassa_s = 120 s |
| Ei volyymiryöppyä | sum(volume, 300 s) vs percentile | 60 s BTC-volyymi; 5 min summa ≤ saman summalähteen 24 h p75, sama ehto molemmille suunnille | ehto | ei | — |

**Suunnan sidonta ja LIIGA:** Leikkaustapahtuma tuottaa ▲/▼, jonka 3A saa samasta hälytyksestä; se ei saa merkitä kaikkia hälytyksiä ▲:ksi eikä valita jälkikäteen parempaa puolta. Ehtoarvot otetaan viimeisistä suljetuista näytteistä, eikä `M` muutu kesken yhden ylityksen/alituksen tarkistuksen. Kaksisuuntaisuus ei kaksinkertaista yhden instanssin cooldown-kiintiötä: cooldown_seconds = 7200 s on yhteinen. Raportoi myös suuntien tulokset erikseen, mutta arvioi sama etukäteen lukittu stromo ja naapurit LIIGAn sääntöjen mukaan.

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| alue_s | 3600 s | 2700 s, 5400 s | 45–90 min riittää paikallisen vaihtelualueen määrittelyyn ilman päivätrendin tasoa |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- **Kaksisuuntainen aluekeskipisteen leikkaus:** laskee laukaisua edeltävän `alue_s`-jakson 60 s high-maksimin ja low-minimin puolivälin `M`. Vertaa edellistä ja juuri sulkeutunutta 1m closea **samaan M-arvoon** ja julkaisee ensimmäisestä leikkauksesta suunnan ▲/▼. Käyttää vain historiassa ja livessä olevaa kauppavirtaa (close/high/low, UTC-minuutit); ei tulevia tietoja. Tämä laajentaa alkuperäisen yksisuuntaisen palikkatarpeen kaksisuuntaiseksi; ei muita uusia palikoita.

## Odotettu tiheys
- Etukäteisarvio 2–12 hälytystä/vrk **molemmat suunnat yhteensä**; keskipisteen leikkaus ja p75-volyymikatto rajaavat osumia. Yhteinen cooldown_seconds = 7200 s rajaa enintään noin 12 kultaan/24 h. LIIGAn ≥ 100 rypään vaatimus 9 kuukaudessa jää todistettavaksi.

## Kumoava koe
- Jos 3A:n suunnan mukainen ▲/▼-osumien yhdistetty reuna ei ylitä satunnaisia tai sigma15-/kellonaikatäsmättyjä verrokkeja, hypoteesi ei saa tukea. Jos toinen suunta on systemaattisesti negatiivinen tai 2700/5400 s naapurit eivät ole samansuuntaisesti positiivisia, kaksisuuntaisuuden perusteltavuutta pitää arvioida ilman jälkikäteistä puolen valikointia.

## Avoimet kysymykset
- Riittääkö edeltävän alueen puoliväli, vai syntyykö liikaa sahaavia leikkauksia? Kumpaakin suuntaa tarkastellaan saman ennalta lukitun määrittelyn osana; kehitysdataa ei käytetä puolten tai rajojen valintaan.
