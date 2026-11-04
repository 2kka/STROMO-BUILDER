# Volyymiruuhka suuntamomentumin aikana ▲▼

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX EEA: käyttäjän valitsema BTC-USDT / BTC-EUR / BTC-USDC

## Hypoteesi
- **Mekanismi:** Kun 1 minuutin kauppavolyymi kasvaa poikkeuksellisesti 15 minuutin nousun tai laskun aikana, lisääntynyt osallistuminen voi tehdä tilanteesta treidaajalle tarkistamisen arvoisen. Volyymipiikki itsessään on suunnaton eikä kerro aggressiivisen virran puolta; momentum antaa markkinan havaitun suunnan. Tämä ei osoita jatkon todennäköisyyttä.
- **Suunta:** **▲** jos volyymipiikin aikana Momentum ▲ on vahvistuneena tilana; **▼** jos Momentum ▼ on vahvistuneena tilana. Molemmat ovat saman stromon mahdollisia hälytyksiä; suunta näkyy äänihälytyksessä ja tapahtumavirrassa.
- **Miksi ei pelkkä volatiliteetti:** Volyymipiikki suhteutetaan samaan UTC-kellonaikaan 7 päivän otoksessa, ja mukaan vaaditaan erillinen 15 minuutin suunnallinen momentumtila.
- **Aikajänne:** Volyymipiikin jälkeiset 1–15 min; ei LIIGAn 3A-testiä.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Poikkeuksellinen osallistuminen | Volyymipiikki | 1 min BTC-volyymi ≥ 5 × saman UTC-kellonajan ±30 min / 7 vrk normaali, kumpaan hintasuuntaan tahansa | tapahtuma | kyllä | voimassa_s = 120 s |
| Suuntamomentum ▲/▼ | Momentum | 15 min ≥ +1 × sigma15 = ▲, tai ≤ −1 × sigma15 = ▼ | tila | ei | hystereesi_s = 30 s |

**Suunnan sidonta:** Volyymipiikillä **ei** ole ▲/▼-merkkiä. Kulta perii suunnan vain samanaikaisesta vahvistuneesta Momentum ▲/▼ -tilasta; ellei sellaista ole, ei kultaa. Pronssi = volyymipiikki; kahden ehdon stromolla ei hopeaa. Yhteinen cooldown_seconds = 5400 s koskee molempia suuntia. Älä tulkitse ▼-momentumia automaattisesti myyntivolyymiksi ilman CVD:n tarkistusta.

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Ei säädettäviä | Valmiiden tunnistimien oletusrajat | — | Ei lisäsäätöä kertaluonteiseen live-kokeiluun |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Ei uusia: volyymipiikki- ja Momentum ▲/▼ -tunnistimet riittävät. Hälytyksen suunta on Momentum-palikan suunnan välitys, ei volyymipiikin merkki.

## Odotettu tiheys
- Arvio 1–8 kultahälytystä/vrk per pari molemmat suunnat yhteensä; 5 × volyymipiikki on poikkeustapahtuma ja momentum suodattaa sitä. Yhteinen cooldown_seconds = 5400 s (enintään 16/24 h per pari). Arvio ei perustu dataan.

## Kumoava koe
- Jos piikin ja momentumin samanaikaisuus ei tuo kummankaan suunnan tilanteeseen hyödyllistä tarkastushetkeä verrattuna pelkkään momentumiin tai tuottaa hälytyksiä ilman selkeää toimintakontekstia, yhdistelmä ei täytä tarkoitustaan.

## Avoimet kysymykset
- Onko 7 vrk kellonaikanormaali vakaa BTC-EUR- ja BTC-USDC-pareilla? Puuttuva normaali ei saa laukaista hälytystä. Käyttöliittymän on näytettävä ▲/▼-momentumi erillään suunnattomasta volyymipiikistä.
