# Tasosulku suunnatun virran kanssa ▲▼

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX EEA: käyttäjän valitsema BTC-USDT / BTC-EUR / BTC-USDC

## Hypoteesi
- **Mekanismi:** Tarkkailija on merkinnyt kiinnostavan tuki- tai vastustason jo ennen hälytystä. Viiden minuutin kynttilän sulkeutuminen sen yläpuolelle (▲) tai alapuolelle (▼) on tarkistuspiste; saman suljetun jakson ostojen tai myyntien nettoylijäämä antaa erillisen havainnon aggressiivisesta osallistumisesta. Hälytys ei ennusta jatkoa eikä tee kauppaa.
- **Suunta:** **▲** kun uusi 5m-sulku siirtyy tason yläpuolelle **ja** saman 5m-jakson delta > 0; **▼** kun uusi 5m-sulku siirtyy tason alapuolelle **ja** saman jakson delta < 0. Sama stromo seuraa molempia, hälytys näyttää ▲/▼.
- **Miksi ei pelkkä volatiliteetti:** Edellyttää juuri käyttäjän merkitsemän tason ylitystä/alitusta sekä samanmerkkistä aggressorivirtaa, ei vain suurta liikettä.
- **Aikajänne:** Sulun jälkeiset 5–15 min; ei LIIGAn 3A-testiä.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| 5m-tasosulku ▲/▼ | Kynttilä 5m päättyy tason yli/alle | Käyttäjän taso; edellinen suljettu 5m-close ≤ taso ja uusi > taso = ▲, tai edellinen ≥ taso ja uusi < taso = ▼. False→True suuntakohtaisesti | tapahtuma | kyllä | voimassa_s = 180 s |
| Virta murron suuntaan | sum(delta, 300 s) | Sulkeutuneen **saman 5m-kynttilän** 60 s delta-summa > 0, jos ▲; < 0, jos ▼ | ehto | ei | — |

**Suunnan sidonta:** Pääehdon tapahtuma tuottaa merkin ▲/▼. Toinen ehto verrataan juuri **tämän tapahtuman** merkkiin ja täsmälleen samaan suljettuun 5m-aikaikkunaan, ei myöhemmin vaihtuvaan deltaan. Jos palikka ei anna suuntaa tai jakson tiedot puuttuvat, ei kultaa. Pronssi = suuntainen tasosulku; kahdella ehdolla ei hopeaa. Kulta näyttää esimerkiksi `Tasosulku ▲ + ostovirta` tai `Tasosulku ▼ + myyntivirta`. Yhteinen 3600 s cooldown koskee kumpaakin suuntaa.

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Taso | käyttäjä asettaa | — (ei LIIGAa) | Merkityksellinen vastustaso, ei automaattinen optimointi |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Ei uutta markkinadatapalikkaa: 5m-tasoehdon yli/alle-vaihtoehdot ja 60 s delta-ikkuna ovat käytössä. 2.H-e:n toteutuksessa pääehdon tapahtumalta on välitettävä sen **suunta ja suljetun jakson tunniste** virtaehtoon sekä hälytystekstiin; jos nykyinen rajapinta ei välitä niitä, tarvitaan vain tämä suunnattu tapahtumasidonta.

## Odotettu tiheys
- Arvio 0–6 kultahälytystä/vrk per pari ja seurattu taso **molemmat suunnat yhteensä**. Tason sulkuvaihdos on tapahtuma; yhteinen cooldown_seconds = 3600 s estää saman alueen jatkuvan piippauksen. Arvio on testaamaton ja riippuu asetetusta tasosta.

## Kumoava koe
- Jos suuntainen 5m-delta ei tuo kummallakaan puolella käyttökelpoista päätöskontekstia verrattuna pelkkään tasosulkuun tai väärän jakson delta tulkitaan vahvistukseksi, yhdistelmä ei vastaa hypoteesia.

## Avoimet kysymykset
- Määritelläänkö hälytyksen cooldown tasokohtaisesti, jos käyttäjä seuraa montaa tasoa? Tason toistuva ylitys ja alitus saman tunnin sisällä eivät saa tuottaa kahta kultaa saman instanssin cooldownin aikana.
