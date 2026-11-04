# Kolmas tukitesti: kaksinkertainen volyymi ja tuen menetys ▼

**Tekijä:** gpt · **Päivä:** 2026-11-04
**Tyyppi:** tutkimusstromo (LIIGA)
**Pari:** OKX BTC-USDT

## Hypoteesi
- **Mekanismi:** Kolmannen uusintatestin aikana aktivoituvat myyjät, riskirajojen toteutukset tai stopit saattavat ylittää tukialueen ostokysynnän. Vaikka pelkkä kokonaisvolyymi ei näytä aggressorin puolta, kolmanteen kosketukseen keskittyvä vähintään kaksinkertainen volyymi ja sitä seuraava ensimmäinen sulku selvästi tuen **alapuolella** osoittavat tason menetyksen. Hypoteesi koskee toistettujen tukitestien jälkeistä alaspäin tapahtuvaa siirtymää, ei tavallista yksittäistä murtotunnistinta.
- **Suunta:** ▼: kolmannen testin jälkeen ensimmäinen 1m sulku on ≤ `L × 0,9980` ennen ylöspäistä `L × 1,0025` -rajaa; kulta merkitään vain alaspäin.
- **Miksi ei pelkkä volatiliteetti:** Vaatii kolme erillistä yritystä samaan etukäteen lukittuun tukialueeseen, volyymin tuplauksen juuri kolmannessa ja toteutuneen sulkumurron; ilman tätä järjestystä tavallinen volatiliteettipiikki ei täytä ehtoja.
- **Aikajänne:** Kolmannen testin jälkeinen 0–5 min sulkumurto, jonka kultahälytyksestä 3A mittaa −σ15 ennen +σ15 seuraavan 60 min aikana.

## Ehdot
| Nimi | Palikka | Asetukset | Tyyppi | Pääehto | Voimassa / hystereesi |
|---|---|---|---|---|---|
| Kolmas tukitesti, 2× volyymi | Uusi: `kolmas_tukitesti_vol2` | Lukittu tuki `L`; kolme erillistä uusintatestiä; `V3 ≥ 2 × V2`; 60 s suljetut low/close/volume; yhteinen määritelmä alla | tapahtuma | kyllä | `voimassa_s=300` |
| Tuki menetettiin ▼ | Uusi: `tukitestin_ensimmainen_ratkaisu` | Ensimmäinen 1m close ≤ `L × 0,9980` 5 min sisällä kolmannen testin jälkeen, ennen yhtäkään close ≥ `L × 1,0025`; suunta ▼ | tapahtuma | ei | `voimassa_s=60` |

**Tapahtumien järjestys:** Pääehto syntyy kolmannen kosketusminuutin sulkeuduttua. Vahvistus on saman testisarjan **ensimmäinen** 5 minuutin sisällä toteutuva sulkuraja. Jos vastakkainen raja tulee ensin, tämä stromo ei laukea; myöhäinen sulku ei kelpaa. Kahden ehdon stromolla on pronssi (kolmas testi) ja kulta (vahvistus), **ei hopeaa**.

### Kolmen kosketuksen ja tuplavolyymin tarkka määritelmä

**Yhteinen, ennen dataa lukittu tukitestin määritelmä:**
1. Tukiehdokas `L` määritetään **vain menneistä** suljetuista 60 s näytteistä: 1m `low`-minimi aikaväliltä `(t−180 min, t−30 min]`. Ehdokas lukitaan, kun viisi peräkkäistä suljettua 1m `close`-arvoa on vähintään `L × 1,005`. Uusintatestien laskenta alkaa vasta tämän lukitushetken jälkeen; aiempaa pohjamuodostusta **ei** lasketa kolmeksi testiksi. Yksi aktiivinen taso per pari; tasoa ei liu'uteta kesken sarjan.
2. Testi #1, #2 tai #3 alkaa ensimmäisestä suljetusta 1m kynttilästä, jolla `low ≤ L × (1 + kosketuskaista_pct/100)` ja edellisen minuutin `close` oli kyseisen kaistan yläpuolella. Sarjan eri testien välillä vaaditaan vähintään 20 minuuttia sekä viisi peräkkäistä 1m sulkua `> L × 1,0035`. Näin saman kynttilärykelmän kosketuksia ei lasketa kolmeksi.
3. Ensimmäisen ja toisen testin jälkeen yksikin suljettu 1m `close < L × 0,998` hylkää tason ennen kolmatta testiä. Muuten uusi testi sallitaan vasta palautumisen jälkeen. Koko sarja vanhenee kuusi tuntia tasolukituksesta; datakatko, uudelleenkäynnistys ilman tilaa tai vanhentuminen peruu keskeneräisen sarjan. Kolmas kosketus sulkee laskurin riippumatta siitä, tuleeko kulta.
4. Kunkin testin volyymi `Vi` on **kolmen viimeisen täysin suljetun 60 s `volume`-näytteen** BTC-summa, päättyen kyseisen kosketusminuutin sulkuun. Kolmannen testin ehto on täsmälleen `V2 > 0` ja `V3 ≥ 2 × V2`; `V1` voidaan tallentaa diagnostiikkaan mutta sitä ei käytetä rajana. Mitta on **kokonais-BTC-volyymi**, ei aggressoripuolen CVD.
5. Kolmannesta testistä (`t3`) alkaa enintään 5 min aikaikkuna **t3:n sulkuhetki mukaan lukien**. Tarkastellaan vain sen hetkisiä ja myöhempiä suljettuja 1m `close`-arvoja: ▲-raja `close ≥ L × 1,0025`, ▼-raja `close ≤ L × 0,9980`. **Ensimmäinen saavutettu raja ratkaisee**; sen jälkeen vastakkainen stromo ei saa laukaisua samasta testisarjasta. Jos kumpaakaan rajaa ei saavuteta viimeistään `t3 + 300 s`, kumpikaan ei laukea. Puuttuva data peruu ratkaisun; ei jälkikäteistä täyttöä.

Vain historiallisessakin kauppavirrassa olevat 60 s `low`, `close`, `volume` ja UTC-näyteajat kelpaavat. Sulkeutuvaa minuuttia ei saa käyttää ennen sen sulkeutumista. 3A alkaa **kultahälytyksen havaintohetkestä**, ei kolmannen testin alusta. Molempien korttien tukitason ja tapahtumien rajat ovat identtiset; ne eivät saa jakaa epämääräistä tai eri tavalla laskettua testilaskuria.

## Parametrit ja naapurit
| Parametri | Oletus | Naapurit | Miksi tämä alue |
|---|---|---|---|
| `kosketuskaista_pct` | 0,15 % | 0,10 %, 0,20 % | Rajaa saman lukitun tukitason uusintakosketukset kohtuullisen kapeaan hintakaistaan. |

**Kiinteitä, ei säädettäviä:** historiataso 180–30 min, lukitusehto +0,50 % / 5 sulkua, testien ero ≥20 min, palautuminen +0,35 % / 5 sulkua, aiempi mitätöinti −0,20 %, kolmannen testin 3m volyymi ≥2× toisen testin, 5 min ratkaisuaika, ▲-raja +0,25 % ja ▼-raja −0,20 %. `cooldown_seconds = 14400` (4 h), yhteensä enintään 6 hälytystä/vrk per kortti. Testataan oletus ja **kaksi etukäteen lukittua naapurivarianttia**, ei lisää jälkeenpäin.

## Tarvittavat uudet palikat
- **`kolmas_tukitesti_vol2`** (yhteinen molemmille korteille): tilallinen sarjalaskuri tukitason lukitukseen, kolmeen erilliseen testiin, palautumis-/mitätöintiehtoihin ja kosketuskohtaisiin 3m volyymeihin. Palauttaa kolmannen testin tapahtuman sekä lukitut `L`, `t3` ja sarjan tunnisteen. Laskenta vain suljettujen 60 s kauppasarjojen `low`, `close`, `volume` ja UTC-aikaleimojen perusteella; toimii historiassa ja livessä.
- **`tukitestin_ensimmainen_ratkaisu`** (sama yleispalikka molemmille): vertaa kolmannen testin jälkeen 1m sulkua ensimmäisenä saavutettuun ▲-/▼-rajaan ja tuottaa vain yhden suunnatun tapahtuman per lukittu testisarja. Ei voi nähdä tulevaa, käyttää lukittua `L`:ää ja peruu sarjan katkoon. Tässä kortissa kuunnellaan vain ratkaisun ▼-haaraa.

## Odotettu tiheys
- Ennakkoarvio 0–2 kultaa/vrk BTC-USDT:llä; kolmas erillinen tukitesti, tuplavolyymi ja tason ensimmäinen alaspäin ratkaisu rajaavat osumia. Edellyttää kolmea erillistä kosketusta sekä 2× volyymiehtoa ja vahvistusta; vähintään 100 rypästä 9 kuukaudessa voi jäädä saavuttamatta. Yhden päivän Try out ≤200/vrk, Treenileiri ≤20/vrk on cooldownin puolesta varmistettu; arvio ei perustu mitattuun dataan.

## Kumoava koe
- Jos 3A:n ▼-osumien reuna on ≤0 satunnaisiin tai σ15:n ja UTC-kellonajan mukaan täsmättyihin verrokkeihin nähden, mekanismi ei saa tukea. Myös naapurikaistojen 0,10/0,20 % epäpositiivinen reuna tai alle 100 rypästä kehitysjaksolla karsii kortin; vastakkaisen suunnan tulosta ei käytetä rajaoptimointiin.

## Avoimet kysymykset
- Onko sulkeminen −0,20 % lukitun tukitason alapuolelle liian nopea tai liian myöhäinen murtoehdon määritelmä? Se on lukittu ennen dataa, eikä 5 min ratkaisuikkunaa tai tukikaistaa muuteta tuloksia katsomalla.

