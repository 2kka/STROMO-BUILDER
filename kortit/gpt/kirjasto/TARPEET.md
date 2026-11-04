# Käyttöstromokirjaston tarvekartoitus

**Tekijä:** gpt · **Päivä:** 2026-11-04

## Mikä on käyttäjän tarve?

STROMO4 on **ihmisen huomionohjaus**, ei kauppa-automaatti. BTC:tä seurataan OKX:n BTC-USDT-, BTC-EUR- tai BTC-USDC-parilla. Käyttäjä on noin puolet ajasta shortissa, joten jokaisessa suunnallisessa pohjassa **long ja short ovat yhtä tärkeitä**. Markkinan spot-kauppavirta ja kirja ovat havainnon lähde; short-position tulos, SL, TP ja R vaativat erillisen luotettavan positio-/käyttäjätiedon. Shortin instrumenttia tai vipua ei päätellä spot-feedistä.

| Päivän vaihe | Tarve / tavallinen virhe | Nykyinen näkymä jo näyttää | Miksi hälytys on hyödyllinen |
|---|---|---|---|
| Valmistelu | Tasojen unohtuminen, ruudun jatkuva vahtiminen | Kynttilät, heatmap, valittavat tasot | #01 muistuttaa oman ennalta asetetun tason lähestymisestä |
| Entry-ajoitus | Reagointi läpäisyyn ennen kynttilän sulkeutumista; shortin unohtaminen | Kynttilät, CVD, volyymi, spread | #02 varmistaa sulun, suunnan ja virran longille tai shortille |
| Trendin seuranta | Liikkeen takaa-ajaminen ilman osallistumisen arviota | Momentum, suhteellinen volyymi, CVD | #03 yhdistää suunnan ja poikkeavan osallistumisen |
| Tuen/vastuksen tarkistus | Tason kosketus luullaan automaattiseksi käänteeksi | Oma taso ja kynttiläkaavio | #04 tuo yhden ajallisesti sidotun tarkasteluhetken |
| Nopea markkina | Hätiköity market-toimeksianto leveään spreadiin | Spread, hintahyppy, kirja | #05 varoittaa kahden poikkeaman yhdistelmästä |
| Huono markkina | Uusi idea ohueen kirjaan | Markkinan tila, syvyys, spread | #06 nostaa toteutusriskin hiljaiselta ruudulta huomioon |
| Position hoito | Tavoite lähestyy huomaamatta | TP/SL-tasot, CVD, positio | #07 muistuttaa position TP:stä ja virran luonteesta |
| Riskiraja | SL lähestyy ja toteutus heikkenee | SL, kirjan syvyys | #08 varoittaa lisäriskistä; ei korvaa stopia |
| Voitollinen positio | Suurin avoin voitto nähdään ikään kuin realisoituna | Positio ja nykyinen P&L | #09 näyttää voiton palautumisen R-kontekstissa |
| Perusteen muuttuminen | Pidetään longia tai shortia vanhan signaalin varassa | Stromojen tasot ja virta | #10 huomauttaa seurattavan stromon *suunnan* muutoksesta |

## Rajaus ja arvot

- Kaikissa kymmenessä pohjassa yksi **pääehto**. Pronssi = pääehdon huomio, hopea vain kolmella ehdolla, kulta = kaikki ehdot. Kaksiehtoisissa ei ole hopeaa.
- Kun parametrissa on **suunta**, valinta on näkyvästi **long / short**. Positiosidonnaisissa suunta saadaan valitusta positiosta, ei oletusarvoisesti longista.
- Hälytystiheydet ovat ennakkoarvioita yksittäiselle pohjalle; kaikkien kymmenen samanaikainen käyttö kasvattaisi äänikuormaa. Ota käyttöön vain kulloinkin tarpeelliset.
- Hintaan sidotut ja position rajat vaativat käyttäjän valinnan; mitään tasoa tai SL:ää ei keksitä.
- Hintahypyn, spreadin ja syvyyden hälytykset eivät ole suuntasignaaleja. Volyymipiikki on suunnaton, vaikka se yhdistettäisiin Momentum ▲/▼ -tilaan.
- Kohde-ehdon ja position tietojen puuttuessa hälytys on **tuntematon / ei aktiivinen**, ei epätosi markkinatulos eikä lupa ottaa riskiä.

## Rakentamisjärjestys

Suoraan nykyisillä palikoilla ja kohde-ehdoilla: #01–#03, #05–#09; #04 tarvitsee olemassa olevan 5m-sulun **jatkuvan ehdon** ja käynnin jälkeisen ajoitusvarmistuksen, #10 eksplisiittisen suunnallisen seurattavan stromon. Näiden deklaratiivisten pohjien moottorituki on vielä toteutus- ja hyväksymiskysymys, ei testattu fakta. Ehdot eivät tee toimeksiantoja.
