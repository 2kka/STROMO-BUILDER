# LIIGA

Stromojen karsinta ideasta liveen. Jokainen variantti (stromotiedosto + yksi
enum-valintojen yhdistelmä) etenee vaiheittain; vaihe voi vain karsia, ei säätää.
Säännöt: [liiga/saannot.json](liiga/saannot.json). Valinnat 3.11.2026, eivät lopullisia.

| Vaihe | Mitä mitataan | Läpäisy |
|---|---|---|
| **Try out** | Yhden päivän tarkistus (rakenne, live = replay) | Tarkistus OK ja ≤ 200 hälytystä päivässä (vain räikeä ylitys; harvinaisuutta ei arvioida yhdestä päivästä) |
| ↳ välitarkistus | Treenileirin ensimmäinen kolmannes 2025-11-01 – 2026-01-31 | **Saa vain pudottaa:** rypäitä < 17 (harvinainen), > 40 hälytystä/vrk (tiheä) tai reuna < −25/√rypäät pp (toivoton). Läpäisijät ajetaan koko jaksolle; päätös vain koko jakson tuloksesta. |
| **Treenileiri** | Kehitysjakso 2025-11-01 – 2026-07-31, BTC-USDT, mittari 3A | ≥ 100 rypästä, reuna ≥ 100/√rypäät pp, ≤ 20 hälytystä/vrk, saman stromon muut variantit reuna > 0; jatkoon enintään 5 per arviointi (suurin reuna/kynnys) |
| **Dopingtesti** | Selittyykö reuna volatiliteetilla tai kellonajalla? | Reuna ≥ 100/√rypäät pp verrokkeihin, jotka on täsmätty σ15:n ja kellonajan mukaan |
| **Kuntopuntari** | Kestääkö ajan, markkinatilojen ja kulujen yli? | Molemmat puoliskot > 0; reuna > 0 vähintään puolessa Markkinan tila -nelikentistä (≥ 20 rypästä), mikään tila ei tuota yli 70 %; osuma > 50 % + kulut/(2σ) |
| **Kausi** | Validointi neljällä kaudella 2021-09 – 2025-10 | Yhdistetty reuna ≥ 50·z/√rypäät (z Bonferroni Kaudelle päässeiden määrällä, α 5 %), reuna > 0 vähintään 3/4 kaudesta |
| **Playoffit** | Koskematon jakso 2026-08-01 – 2026-10-31, **vain omistaja ajaa, kerran** | Reuna ≥ 100/√rypäät pp |
| **Näytösottelu** | Hiljainen liveajo samalla mittarilla | Omistajan päätös |
| **Tilastot** | Kaikki tulokset, myös karsitut (append-only) | – |

Aikainen ylennys on kielletty: kesken jakson saa vain karsia, koska aikainen karsinta ei lisää sattumalöytöjä.
Välitarkistuksessa tai Try outissa pudonnut naapurivariantti lasketaan naapurisäännössä "ei plussalla".

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
python3 ~/stromo-builder/liiga/liiga.py paketti uupumus   # tiivistelmä leikepöydälle AI-tarkastukseen
python3 ~/stromo-builder/liiga/liiga.py yo           # aja + raportti + vie yhdellä kertaa
```

**LIIGA 2 – omistaja ohjaa selaimesta (4.11.2026 alkaen):** mergetty stromo on
**prospekti**, kunnes omistaja siirtää sen ajojonoon (liiga.stromo.uk tai `liiga.py siirra
<tekijä/nimi>`). Stromo kulkee kaikkine variantteineen ja ajetaan vain siihen vaiheeseen,
johon se on siirretty: läpäisyn jälkeen se jää odottamaan seuraavaa siirtoa (Try out →
Treenileiri → Dopingtesti (+ Kuntopuntari) → Kausi → Playoffit). Karsinta tapahtuu edelleen
tulosten perusteella, ja kuollut stromo menee hautausmaalle. LIIGA ei käynnisty itsestään:
omistaja painaa Aja (teho kevyt/täysi).

**Seula (omistaja 4.11.2026):** läpäisy lasketaan raakaluvuista voimassa olevalla seulalla
(`liiga.py seula iso_kampa|normaali|tiukka|oma`, `liiga.py seula-arvo <säädin> <arvo>`).
Iso kampa (oletus): ei aikaista karsintaa, Treenileirin raja 1 keskivirhe, min 30 rypästä,
naapurisääntö enemmistö. Normaali = aiempi LIIGA (2 keskivirhettä = 100/√rypäät, min 100,
kaikki naapurit, välitarkistus karsii). Tiukka: 3 keskivirhettä, Kausi α 1 %. Raakaluvut ja
ajon aikainen seula tallentuvat aina; tulosten jälkeen muutettu seula merkitsee tuloksen
"jälkisäädetty". Sattumamittari: testattu N × sattumaläpäisy vs toteutunut. Kiintiö
(max_jatkoon) poistui, koska omistaja siirtää vaiheet käsin. Playoffit eivät ole säädettävissä. Puuttuva palikka palauttaa stromon prospekteihin
("odottaa palikkaa"), eikä se kuole. Yöajo ajaa vain ajojonossa olevat.

**Yöajo:** `liiga/yoajo.sh` (Windowsin tehtävänajastin käynnistää, ks. alla). Se ohittaa
yön, jos jokin ajo on jo käynnissä, ja kirjoittaa lokiin `data/research/liiga/yoajo.log`.

🪟 Windows PowerShell (järjestelmänvalvojana), kerran:

```powershell
$a = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-d Ubuntu -- bash -lc ~/stromo-builder/liiga/yoajo.sh"
$t = New-ScheduledTaskTrigger -Daily -At 22:30
$s = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 10)
Register-ScheduledTask -TaskName "LIIGA yoajo" -Action $a -Trigger $t -Settings $s
```

Tarkista jakelun nimi ensin komennolla `wsl -l -v` (esim. `Ubuntu` tai `Ubuntu-24.04`).

LIIGA tunnistaa valmiit ajot stromon SHA-256:n, parametrien ja jakson perusteella,
joten mitään ei ajeta kahdesti (myös kierroksen 1 `k1-`-ajot kelpaavat Treenileiriksi).
Dopingtesti ja Kuntopuntari odottavat STROMO4:n työkalua `research/tappotestit.py`
(Codex 3.1b); Kausi vaatii 2021–2025 kaupat pelikoneelle.

**Yhteisajo (omistaja 4.11.2026):** saman vaiheen ja jakson ajot (välitarkistus, Treenileiri,
kausi) ajetaan yhtenä `research.replay --batch` -eränä, kun ne kuuluvat samaan rytmiluokkaan
(deklaratiivinen / tunnistin / Python), enintään 60 varianttia. Kaupat luetaan kerran, yhteiset
palikat lasketaan kerran. Tulokset tallentuvat `runs/liiga-era-…/<variantti>/` samassa muodossa
kuin yksittäisajo (STROMO4:n testi: erä = yksittäisajot tavuina).

