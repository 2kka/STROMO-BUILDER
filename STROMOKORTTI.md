# Stromokortti

Jokainen uusi stromo alkaa kortista. Kortti kirjoitetaan **ennen kuin dataa katsotaan** – se ei kuluta testibudjettia. Vasta hyväksytystä kortista kirjoitetaan stromotiedosto (rakennusmalli v1, ks. [OHJE.md](OHJE.md) ja [PALIKAT.md](PALIKAT.md); deklaratiivinen ehtomuoto päivitetään niihin, kun STROMO4:n 2.H-e on valmis).

Kortit tallennetaan kansioon `kortit/<tekijä>/<nimi>.md` (tekijä: `omistaja`, `claude`, `gpt`). Kortin saa kirjoittaa kuka tahansa malli; omistaja hyväksyy.

## Säännöt (omistaja lukitsi 4.11.2026)

- **Hypoteesi ensin.** Ilman hypoteesia stromo ei mene Try outiin.
- **Vähintään 2 ehtoa.** Pääehto valinnainen; ilman pääehtoa stromolla on vain kulta (ei pronssia/hopeaa). Kahden ehdon stromolla ei hopeaa.
- **Ehdot ovat palikoita** (palikka + asetukset + tyyppi), ei vapaata koodia. Eri raja = eri palikka. Uusi palikkatyyppi tilataan STROMO4:ään Codexilta.
- **Stromo laukeaa, kun kaikki ehdot ovat tosia** (tapahtuma on tosi voimassaoloaikansa).
- **Ei uudelleenkäyttöä karsituista:** kierroksen 1 stromot (Hall of Fame mukaan lukien) jäävät historiaan. Uusi kortti ei saa olla vanhan stromon säätö kehitysdatan tulosten perusteella.
- **Kehitysdataa ei katsota ennen Try outia** (BTC-USDT 2025-11-01 – 2026-07-31). Koskematon jakso 2026-08-01 – 2026-10-31 on suljettu.

## Kortin pohja

```markdown
# <Nimi>

**Tekijä:** omistaja / claude / gpt · **Päivä:** VVVV-KK-PP
**Tyyppi:** tutkimusstromo (LIIGA) / käyttöstromo (live-apu, "kokeilu", ei LIIGAa)
**Pari:** BTC-USDT (tutkimus) / muu

## Hypoteesi
- **Mekanismi:** kuka markkinalla toimii ja miksi hinnan pitäisi reagoida (2–4 lausetta).
- **Suunta:** ▲ / ▼ / kumpikin (miten suunta määräytyy).
- **Miksi ei pelkkä volatiliteetti:** mikä erottaa tämän tilanteen tavallisesta kiivaasta markkinasta.
- **Aikajänne:** minkä ajan kuluessa vaikutuksen pitäisi näkyä (tulosmittari on 60 min, ±σ15).

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| | | | ehto / tapahtuma / tila | kyllä / ei | s |

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|

Enintään kaksi säädettävää, arvot lukitaan ennen ajoa.

## Tarvittavat uudet palikat
- (palikka, mitä se laskee, mistä datasta) – tai "ei uusia".

## Odotettu tiheys
- Hälytyksiä / vrk (arvio ja perustelu, ei datasta katsottu). LIIGA: Try out ≤ 200/vrk, Treenileiri ≤ 20/vrk.

## Kumoava koe
- Mikä tulos osoittaisi, että mekanismia ei ole (esim. "reuna katoaa, kun verrokit täsmätään volatiliteetilla").

## Avoimet kysymykset
-
```

## Kortista stromoksi

1. Kortti `kortit/`-kansioon PR:nä → omistaja hyväksyy (merge).
2. Tarvittavat uudet palikat Codexille yhtenä tehtävänä.
3. Stromotiedosto `stromot/<tekijä>/<nimi>.py` rakennusmallin muodossa, kortin tiedot `HYPOTEESI`-kenttään.
4. Tutkimusstromo → LIIGA. Käyttöstromo → liveen kokeiluna (näkyy kortissa merkinnällä).
