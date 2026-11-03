> Kopio STROMO4:n tiedostosta `stromot/PALIKAT.md` (versio c9e6d47, 3.11.2026). Tekstin `_malli.py` on tässä repossa `malli.py` ja testiesimerkit kansiossa `esimerkit/`. Tarkistus- ja tutkimustyökalut ajetaan omistajan omassa ympäristössä; tässä repossa niitä ei ole.

# Stromon kirjoittaminen palikoista

Stromo on yksi Python-tiedosto. Aloita kopioimalla `_malli.py` ja muokkaa nimeä,
parametreja, `TARVITSEE`-sanakirjaa ja `ehto(ctx)`-funktiota. Mallin alaviiva
estää sen lataamisen liveen. Tutkimussivun luonnokset säilyvät ajohakemiston
`.drafts/`-kansiossa, eivät `stromot/`-kansiossa. Luonnoksen voi kirjoittaa
tekstikenttään tai avata paikallisesta tiedostosta, tarkistaa ja ajaa.

Stromo tarvitsee nämä viisi metatietoa ja funktion:

- `NIMI`: käyttöliittymän nimi, epätyhjä teksti.
- `SELITYS`: mitä tapahtumaa etsitään, epätyhjä teksti.
- `PARAMETRIT`: parametrien skeema alla.
- `EHDOT`: yksilölliset ehtolamppujen nimet, esimerkiksi `("Volyymi", "Paluu")`.
- `TARVITSEE`: nimetyt palikat riippuvuusjärjestyksessä, lähde ennen käyttäjää.
- `def ehto(ctx)`: palauttaa `None`, viestin tai `ctx.tulos(...)`-tuloksen.

**Palikkastromossa ei ole importteja.** Metatiedot ovat Python-literaaleja.
Ehtofunktiossa saa käyttää paikallisia muuttujia, if/return-lauseita, vertailuja,
laskutoimituksia (+ − × / %), sanakirjoja, listoja, tupleja ja f-merkkijonoja.
Sallitut tavalliset funktiot: `abs`, `min`, `max`, `len`, `int`, `bool`.
Sanakirjan `.get()` on sallittu. Silmukat, comprehensions, omat apufunktiot,
rekursio, potenssioperaattori, importit, tiedostot, verkko, kellon lukeminen,
introspektio ja kontekstin muuttaminen hylätään. Muoto on sama tarkistuksessa,
tutkimuksessa ja palikkastromon live-latauksessa. Vanhat stromot käyttävät
edelleen aiempaa luotetun Pythonin latauspolkua.

## Parametrit

Pakolliset: `exchange`, `instrument`, `cooldown_seconds`. Markkina on aina
(pörssi, instrumentti); eri markkinoiden tilat eivät sekoitu.

```python
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {
        "type": "enum",
        "default": "BTC-EUR",
        "choices": ["BTC-EUR", "BTC-USDT", "BTC-USDC"],
    },
    "cooldown_seconds": {"type": "integer", "default": 60, "min": 0, "max": 86400},
    "ikkuna": {"type": "integer", "default": 10, "min": 1, "max": 86400},
    "kynnys": {"type": "number", "default": "1.5", "min": "0", "max": "10000"},
}
```

`integer` palautuu kontekstiin int-lukuna, `number` desimaaliluvun tekstinä,
`enum` valittuna tekstinä. `label` on vapaaehtoinen lomakkeen otsikko.
Muunna desimaaliparametri laskentaan `ctx.luku(ctx.parameters["kynnys"])`.
Älä vertaa hintaa tai volyymia suoraan desimaaliparametrin tekstiin.

Palikan asetuksen `"$ikkuna"` tarkoittaa parametrin arvoa. Käytä parametriviitteitä
stromon säädettäviin ikkunoihin ja kynnyksiin. Vakiot 1/60 (näyteväli) ja valmiin
σ15:n 900/96 ovat laskentamääritelmiä. Jokainen ikkuna on 1–86400 sekuntia ja
oman lähteensä näytevälin monikerta. Peräkkäisten ikkunoiden kokonaislämmitys
voi ylittää vuorokauden. Parametriyhdistelmä tarkistetaan myös muutettaessa.

## Konteksti ja tulos

`ctx.price` on juuri nähty kauppahinta (Decimal), `ctx.timestamp_ms` sen Unix-ms.
`ctx.previous_price` on aiempi tunnettu kauppahinta tai None. `exchange` ja
`instrument` nimeävät markkinan. Kaikki palikkastromot käyttävät kauppalähdettä.
`ctx.parameters` ja `ctx.state` ovat muuttumattomia sanakirjoja.

`ctx.palikat["nimi"]` on viimeisin sulkeutunut näytearvo (Decimal) tai None.
`ctx.ajat["nimi"]` on sen jakson loppu Unix-ms:nä; esimerkiksi 12.00 minuutti
sulkeutuu 12.01. `ctx.uudet` sisältää tällä kaupalla päivittyneiden palikoiden
nimet. Käytä `if "nimi" not in ctx.uudet: return None`, kun ehto arvioidaan vain
uusista näytteistä. Arvo voi päivittyä samaksi kuin edellinen.

Näytteet muodostetaan laiskasti seuraavan kaupan saapuessa. Jos välissä on
useita kaupattomia jaksoja, ne kaikki viedään ketjun läpi aikajärjestyksessä.
Ehto arvioidaan **nykyisen kaupan hetkellä**, ei jälkikäteen menneille jaksoille.
`ctx.ajat` kertoo näytteen ajan; hälytyksen aika on havaintohetki. Seurannan Y
tarkistetaan jokaisella nähdyllä kaupalla. Live ja replay käyttävät samaa koodia;
eivät seinäkelloa tai tulevaa kauppaa päätöksen tekemiseen.

```python
return ctx.tulos(
    "Volyymi ylitti rajan" if osuma else None,
    conditions={"Volyymi": osuma},
    state={"edellinen": ctx.palikat["summa"]},
    direction="up",
)
```

`message` on teksti tai None, `direction` on `"up"`, `"down"` tai None. Tunnettua
suuntaa tarvitaan suunnallisessa tulosmittarissa. `conditions` antaa nimetyille
lampuille True/False/None (vihreä/punainen/harmaa). `state` korvaa edellisen
tilan; jätä pois, jos haluat säilyttää sen. Tila saa sisältää lukuja, tekstiä,
None-arvoja ja sisäkkäisiä sanakirjoja/listoja. Cooldown rajoittaa hälytyksiä,
ei tilan tai seurannan päivittymistä.

## Kauppasarja: series

```python
"v": {"kind": "series", "field": "volume", "step": 1}
```

`step` on 1 sekunti tai 60 sekuntia. Jaksot ovat UTC-epookkiin sidottuja
puoliavoimia välejä `[alku, loppu)`; tasan rajalla oleva kauppa kuuluu uuteen
jaksoon. Arvo julkaistaan vasta sulkeuduttua. Kentät:

| field | Palautus |
|---|---|
| `close`, `high`, `low` | Jakson päätös, korkein ja matalin kauppahinta |
| `volume` | BTC-määrien summa, ei quote-valuuttaa |
| `buy_volume`, `sell_volume` | Aggressiivisten ostojen/myyntien BTC-määrät |
| `delta` | Jakson osto−myyntivolyymi |
| `cvd` | Kumulatiivinen osto−myyntivolyymi tunnetun kauppajakson alusta |
| `count` | Kauppatapahtumien määrä (Decimal); aggregoitua määrää ei kerrota countilla |

Kaupattomalla, tunnetulla jaksolla määrät, delta ja count ovat 0, hinnat ovat
edellinen päätös, kumulatiivinen CVD säilyy. Ensimmäinen osittainen jakso on
None; ensimmäinen kokonainen jakso tarvitaan. Katkon ajalta arvot ovat None,
eivät nollia. Katkon jälkeen CVD alkaa uudesta tunnetusta jaksosta; käytä
`delta`-summaa, kun tarvitset rajatun CVD-ikkunan.

Esimerkki: osto 2 BTC, myynti 3 BTC → volume=5, delta=−1, count=2.

## Liukuva ikkuna: window

```python
"cvd": {"kind": "window", "source": "delta", "op": "sum", "seconds": "$ikkuna"}
```

Lähde voi olla mikä tahansa aiempi näytepalikka, myös toinen ikkuna, sigma tai
persentiili. `sum`, `mean`, `min`, `max` käyttävät N=seconds/lähteen_näyteväli
viimeisintä näytettä: `(t−seconds, t]`. Palautus on Decimal.
`change` = arvo(t)−arvo(t−seconds), `log_change` = ln(arvo(t)/arvo(t−seconds));
nämä tarvitsevat N+1 näytettä. Log-muutos on None myös, jos kumpikaan päätepiste
ei ole positiivinen. Kaikki operaatiot palauttavat None, jos tarvittavia
näytteitä ei ole tai yksikin niistä puuttuu. Esimerkiksi sarjan 1,2,3 kolmen
näytteen summa on 6 ja keskiarvo 2; kolmen näytevälin muutos vaatii neljännen.

Itseisarvo `abs` käyttää täsmälleen yhtä näytettä: `seconds` = lähteen
näyteväli ja N=1. Palautus on |viimeisin näyte| tai None, jos näyte puuttuu.
Useamman näytteen abs-ikkuna hylätään. Esimerkiksi absorptio voi verrata
|CVD_W|:tä sen omaan 24 h persentiiliin näin (ikkunat ja p parametreista):

```python
TARVITSEE = {
    "delta": {"kind": "series", "field": "delta", "step": 60},
    "cvd_w": {"kind": "window", "source": "delta", "op": "sum", "seconds": "$ikkuna"},
    "voimakkuus": {"kind": "window", "source": "cvd_w", "op": "abs", "seconds": 60},
    "p95": {
        "kind": "percentile",
        "source": "voimakkuus",
        "seconds": "$takajakso",
        "p": "$persentiili",
    },
}
```

Esimerkin `takajakso`-parametrin oletus on 86400 ja `persentiili`-parametrin 95.
Persentiilin lähteenä on itseisarvosarja, joten molempien suuntien CVD:t
vertautuvat samaan voimakkuusjakaumaan. Esimerkiksi CVD_W=−3 → voimakkuus=3.
Kun vertaat nykyistä voimakkuutta p95:een, odota myös voimakkuuden omaa
valmistumista: persentiili voi jo olla saatavilla, vaikka CVD_W on vielä None.

## Volatiliteetti: sigma

```python
"close": {"kind": "series", "field": "close", "step": 60},
"sigma15": {"kind": "sigma", "source": "close"},
# Sama eksplisiittisesti: period=900, count=96.
```

`period` (sekuntia) on lähteen näytevälin monikerta, `count` vähintään 2,
period×count enintään 24 h. Hinnat otetaan sulkeutuneilta UTC-jaksorajoilta.
σ = log-tuottojen otoskeskihajonta, jakaja n−1. Takajakso tarvitsee
count+1 päätöspaikkaa. Puuttuvaan tai
epäpositiiviseen päätökseen koskevat tuotot ohitetaan; aukon yli ei lasketa
tuottoa. Vaaditaan vähintään 90 % nimellisistä tuotoista ja vähintään kaksi
tuottoa, muuten None. Jakaja on läsnä olevien tuottojen n−1. σ15:ssä tarvitaan
vähintään 87/96 tuottoa. Ilman puuttuvia tulos säilyy bitilleen ennallaan.
Rajahetkellä t käytetään vain hintaa kaupoista <t.
Log-tuotto lasketaan kerran; pitkän ikkunan momentit päivittyvät tarkoilla
rationaalisummilla ilman liukuvan varianssin kumoutumisvirhettä.
Arvo pysyy seuraavaan UTC-jaksorajaan. Esimerkiksi 100→110→99 antaa tuotot
ln(1.1), ln(0.9), joiden otoskeskihajonta on |ln(1.1)−ln(0.9)|/√2.

Valmis `sigma15` on 96 menneen UTC-vartin σ: sama Decimal-ratio, ln ja n−1
kuin onnistumismittarissa 3A (`research.primary.SigmaHistory`). Tämä palikka
käyttää kaupoista muodostettuja minuuttipäätöksiä; 3A käyttää authoritative-
minuuttipäätöksiä. Samoilla päätöksillä tulos on täsmälleen sama. Puuttuvaa
kauppalähdettä ei korvata authoritative-kynttilöillä tai toisin päin.

## Liukuva persentiili: percentile

```python
"p95": {"kind": "percentile", "source": "cvd", "seconds": "$takajakso", "p": "$persentiili"}
```

`seconds` oletus 86400 (24 h), `p` oletus 95, rajat 0–100. Käytetään viimeisiä
N näytettä, myös juuri sulkeutunutta näytettä. Järjestysluku on
max(1, ceil(p×N/100)): ei interpolointia. Minuutin tai sitä harvemmat näytteet
ovat tarkkoja. Esimerkiksi .5,1,1.005,2: p75=1.005.

Sekuntinäytteet käyttävät determinististä etumerkillistä log-histogrammia.
Positiivisen luvun lokero on `(1.01^(k−1), 1.01^k]`, negatiiviset peilataan
ja nollalla on oma lokero. **Palautus on aina valitun lokeron yläraja.**
Siksi samojen lukujen sekuntip75 on 1.01. Arvot −1.005 ja +1.005 tuottavat
ylärajoiksi −1 ja +1.01. Ruudukko lasketaan Decimalilla 40 numeron tarkkuudella;
näytejono ja lokerolaskurit poistavat vanhat näytteet täsmällisesti.
None, kunnes koko takajakso on täynnä tai puuttuvia näytteitä on yli 1 %.
Muuten lasketaan läsnä olevista: rank = max(1, ceil(p×läsnä_olevat/100)).
24 h minuutti-ikkunassa sallitaan enintään 14 puuttuvaa minuuttia; 15 estää
arvon. Ilman puuttuvia tulos säilyy bitilleen ennallaan.

## Tapahtuman jälkeinen seuranta: follow ja ctx.seuraa

```python
TARVITSEE = {"paluu": {"kind": "follow", "seconds": "$odotus"}}


def ehto(ctx):
    tapahtuma = ctx.price > ctx.luku(ctx.parameters["taso"])
    ehto = ctx.price <= ctx.luku(ctx.parameters["palautumisraja"])
    seuranta = ctx.seuraa("paluu", tapahtuma, ehto)
    return ctx.tulos(
        "Palautui" if seuranta.value is True else None,
        conditions={"Paluu": seuranta.value},
        state={"paluu": seuranta.state},
    )
```

`follow` ilmoittaa enimmäisodotuksen (1–86400 s); sitä ei lueta `palikat`-
sanastosta. `ctx.seuraa(nimi, X, Y)` saa bool/None-ehdot ja lukee edellisen
seurantatilan `ctx.state[nimi]`-avaimesta. Tallenna palautettu `.state` saman
avaimen alle. Muuten seuranta ei etene. Säilytä muutkin tarvitsemasi tila-avaimet.

`.value`: None, kun ei ole päätöstä; True ensimmäisellä X:n **jälkeisellä**
havainnolla, jolla Y on tosi ja aika ≤ X+T; False määräajan täytyttyä ilman
osumaa. X:n kanssa sama millisekunti ei kelpaa onnistumiseksi. Tasan määräajan
Y=True hyväksytään. Määräajan jälkeen nähty Y ei kelpaa. Toistuva X ei jatka
avointa määräaikaa. Ratkaisukauppa ei aloita uutta seurantaa samanaikaisesti.
`.started_ms` ja `.deadline_ms` ovat avoimen seurannan ajat tai None.
Pelkkä aika ei synnytä havaintoa: määräajan ylittyminen todetaan seuraavasta
kaupasta, ja hälytys saa sen ajan. Katko peruu avoimen seurannan tuntemattomana.

Täydellinen 50 %:n palautumisesimerkki on `tests/stromo_examples/burst_follow.py`.
Se tallettaa myös purskeen huipusta ja edeltävän ikkunan pohjasta lasketun
palautumishinnan; se ei etsi jälkikäteen tulevia osumia.

## Lämpeneminen, tila ja tarkistus

Kun jokin ketjun lopputuloksista (palikka, jota toinen palikka ei käytä
lähteenään) on None, ehto odottaa ja sen lamput ovat harmaita. Toleranssin
salliva persentiili/σ voi olla valmis, vaikka sen lähteen nykyinen näyte
puuttuisi. Jos ehto lukee myös välipalikoita, käsittele niiden None erikseen
ennen vertailua ja palauta vastaavalle lampulle None. Katso CVD-esimerkki. Lähteen ikkunan ja sen päälle rakennetun ikkunan lämmitykset
lasketaan yhteen. Moottorin ilmoittama kokonaislämmitys sisältää lisäksi
UTC-/ensimmäisen osajakson varan sekä pisimmän seurannan määräajan.
`parallel.py` käyttää tätä muiden aktiivisten aikavaatimusten rinnalla;
palikkatila kuuluu chunk-rajojen tilatodistukseen ja tilasta jatkamiseen.
Vain aktiivisten stromojen pyytämät verkot lasketaan; sama markkina ja sama
verkko jakavat laskennan. Vanhat stromot eivät varaa palikkatilaa.

Live tallentaa palikkatilan asetusten SQLiteen 60 s välein ja lopetuksessa.
Alle 10 min vanha, samoja palikka-asetuksia vastaava checkpoint ladataan;
vanha tai eri asetusten tila aloittaa kylmänä. Katkon yli ei keksitä nollia:
viimeisen käsitellyn osajakson ja paluun välit ovat puuttuvia. Avoin seuranta
perutaan, koska sen katkon aikaista Y:tä ei tunneta. Sulkeutunut historia
säilyy. Window-operaatiot odottavat edelleen aukotonta ikkunaa; persentiili
ja σ jatkavat yllä olevien 1 % / 90 % rajojen puitteissa. Hitaan tilastopalikan
viimeinen sulkeutunut arvo säilyy seuraavaan UTC-näyterajaan.

Tarkista paikallinen tiedosto ennen tutkimusta:

```bash
uv run --group research python research/check_stromo.py oma.py --day 2026-01-02
# Tarvittaessa: --data-root data/research/history --pair BTC-EUR --param ikkuna=10
```

Työkalu tarkistaa rakenteen, parametrien tyypit/rajat, riippuvuudet ja ctx-
rajauksen ennen funktion kääntämistä. Se lukee yhden kokonaisen UTC-päivän
kaupat ja vaaditun lämmityksen, ajaa live-syötteen ja replay-syötteen samaan
moottoriin, vertaa kaikki tilat ja hälytykset, näyttää SHA-256:n ja hälytykset/vrk.
Tulosteen `Puuttuvien osuus` ja JSONin `missing_fractions` kertovat kunkin
palikan viimeisen näytteen laadun (σ: puuttuvat tuotot, muut: puuttuvat
näytteet). Tilan sama `missing_fractions` sisältyy checkpointiin ja
tilatodistukseen; liven tilavastauksen kenttä on `block_missing_fractions`.
Osuus on 0–1, tekstissä prosentteina; keskeneräiset näytepaikat lasketaan
puuttuviksi. Kellot normalisoidaan tapahtuma-aikaan. Lamppujen näyttötila ei kuulu tiivisteeseen.
Puuttuva/viallinen lähde tai koskemattoman jakson leikkaus tuottaa VIRHEen;
tarkistus ei avaa holdoutia. Oletuspäivä on 2.1.2026 UTC. Työkalu ei takaa
strategian kannattavuutta; tarkista myös n, suunta ja tulosmittari tutkimuksesta.

Tutkimussivulla lisää luonnos, valitse parametrit ja alkupäivä ja paina
**Tarkista yhden päivän ajo**. Tavallinen **Käynnistä ajo** ajaa valitun välin,
verrokit ja tulosmittaukset. Luonnoksen tarkka lähde ja SHA-256 säilyvät ajossa.
Komentoriviltä sama onnistuu `research.replay --stromo oma --stromo-file oma.py`
sekä tavallisilla pari-, päivä- ja parametrivalinnoilla.
