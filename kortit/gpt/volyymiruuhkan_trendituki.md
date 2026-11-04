# Volyymiruuhka nousumomentumin aikana ▲

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** OKX EEA: käyttäjän valitsema BTC-USDT / BTC-EUR / BTC-USDC

## Hypoteesi
- **Mekanismi:** Kun kauppamäärä kohoaa poikkeuksellisesti jo vahvan 15 minuutin nousun aikana, uusi osallistuminen voi tehdä liikkeestä treidaajalle tarkastamisen arvoisen. Tämä tuo näkyviin trendin ja hetkellisen osallistumisen kohtaamisen, mutta ei osoita jatkon todennäköisyyttä.
- **Suunta:** ▲; vain Momentum ▲ -tilassa.
- **Miksi ei pelkkä volatiliteetti:** Volyymipiikki mitataan kyseisen UTC-kellonajan normaaliin nähden ja se vaatii lisäksi noususuuntaisen 15 min tilan.
- **Aikajänne:** Volyymipiikin jälkeiset 1–15 min; ei LIIGAn 3A-testiä.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Poikkeuksellinen osallistuminen | Volyymipiikki | 1 min BTC-volyymi ≥ 5 × saman UTC-kellonajan ±30 min 7 vrk normaali | tapahtuma | kyllä | voimassa_s = 120 s |
| Nouseva jakso | Momentum ▲ | 15 min nousu ≥ 1 × sigma15 | tila | ei | hystereesi_s = 30 s |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| Ei säädettäviä | Valmiiden tunnistimien oletusrajat | — | Ei lisäsäätöä kertaluonteiseen live-kokeiluun |

Enintään kaksi säädettävää; tutkimusstromon naapurit on lukittu ennen yhtään ajoa.

## Tarvittavat uudet palikat
- Ei uusia: valmiit volyymipiikki- ja Momentum ▲ -tunnistimet riittävät.

## Odotettu tiheys
- Arvio 1–6 kultahälytystä/vrk per pari, koska 5 × volyymipiikki on poikkeus ja nousumomentum suodattaa sitä. Hiljennys 5400 s (enintään 16 saman parin hälytystä/24 h). Arvio ei perustu dataan.

## Kumoava koe
- Jos volyymipiikkiä seuraava huomio ei ole käytännössä erilaista kuin pelkkää Momentum ▲ -tilaa tarkkailtaessa tai hälytys peittyy liian tiheään toistoon, yhdistelmä ei auta päätöksentekoa.

## Avoimet kysymykset
- Onko 7 vrk kellonaikanormaali riittävän vakaa juuri BTC-EUR- ja BTC-USDC-pareilla; puuttuva normaali ei saa laukaista hälytystä?
