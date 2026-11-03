# LIIGA

Stromojen karsinta ideasta liveen. Jokainen variantti (stromotiedosto + yksi
enum-valintojen yhdistelmä) etenee vaiheittain; vaihe voi vain karsia, ei säätää.
Säännöt: [liiga/saannot.json](liiga/saannot.json). Valinnat 3.11.2026, eivät lopullisia.

| Vaihe | Mitä mitataan | Läpäisy |
|---|---|---|
| **Try out** | Yhden päivän tarkistus (rakenne, live = replay) | Tarkistus OK |
| **Treenileiri** | Kehitysjakso 2025-11-01 – 2026-07-31, BTC-USDT, mittari 3A | ≥ 100 rypästä, reuna ≥ 100/√rypäät pp, ≤ 20 hälytystä/vrk, saman stromon muut variantit reuna > 0; jatkoon enintään 5 per arviointi (suurin reuna/kynnys) |
| **Dopingtesti** | Selittyykö reuna volatiliteetilla tai kellonajalla? | Reuna ≥ 100/√rypäät pp verrokkeihin, jotka on täsmätty σ15:n ja kellonajan mukaan |
| **Kuntopuntari** | Kestääkö ajan, markkinatilojen ja kulujen yli? | Molemmat puoliskot > 0; reuna > 0 vähintään puolessa Markkinan tila -nelikentistä (≥ 20 rypästä), mikään tila ei tuota yli 70 %; osuma > 50 % + kulut/(2σ) |
| **Kausi** | Validointi neljällä kaudella 2021-09 – 2025-10 | Yhdistetty reuna ≥ 50·z/√rypäät (z Bonferroni Kaudelle päässeiden määrällä, α 5 %), reuna > 0 vähintään 3/4 kaudesta |
| **Playoffit** | Koskematon jakso 2026-08-01 – 2026-10-31, **vain omistaja ajaa, kerran** | Reuna ≥ 100/√rypäät pp |
| **Näytösottelu** | Hiljainen liveajo samalla mittarilla | Omistajan päätös |
| **Tilastot** | Kaikki tulokset, myös karsitut (append-only) | – |

Kirjoittajat (AI-istunnot) näkevät Treenileirin luvut, myöhemmistä vaiheista vain läpi / karsittu.

## Ajaminen (pelikone, STROMO4-tutkimuskansio)

```bash
cd ~/stromo4-tutkimus
git -C ~/stromo-builder pull -q
python3 ~/stromo-builder/liiga/liiga.py tila         # tilanne
python3 ~/stromo-builder/liiga/liiga.py aja --kuiva  # mitä ajettaisiin
python3 ~/stromo-builder/liiga/liiga.py aja          # ajaa jonon (Try outit ensin)
python3 ~/stromo-builder/liiga/liiga.py raportti     # aamuraportti
python3 ~/stromo-builder/liiga/liiga.py vie          # tilastot/ ja raportti haaraan tulokset/…
```

LIIGA tunnistaa valmiit ajot stromon SHA-256:n, parametrien ja jakson perusteella,
joten mitään ei ajeta kahdesti (myös kierroksen 1 `k1-`-ajot kelpaavat Treenileiriksi).
Dopingtesti ja Kuntopuntari odottavat STROMO4:n työkalua `research/tappotestit.py`
(Codex 3.1b); Kausi vaatii 2021–2025 kaupat pelikoneelle.
