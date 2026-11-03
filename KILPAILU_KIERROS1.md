# Kilpailu, kierros 1 (3.11.2026)

Claude ja GPT kirjoittavat kumpikin stromoja samoilla säännöillä ja samalla
tiedolla. Tuomarina ja ajajana toimii omistaja.

## Osallistujat ja tieto

- **Claude** (omistajan STROMO4-istunto) ja **GPT** (ChatGPT).
- Molemmilla on käytössä vain tämä repo: [OHJE.md](OHJE.md), [PALIKAT.md](PALIKAT.md),
  esimerkit ja `stromot/omistaja/`. Kumpikaan ei näe toisen stromoja ennen lukitusta.

## Palautus

- Enintään **kolme stromoa**, kullekin enintään **kaksi lukittua varianttia**
  (oletus + naapuri, enum-valintoina). Yhteensä enintään kuusi testiä per tekijä.
- Tiedostot kansioon `stromot/claude/` tai `stromot/gpt/`, omaan haaraan
  (`kierros1/claude`, `kierros1/gpt`) ja PR:ksi. Jokaisessa tiedostossa
  docstring: mekanismi, odotettu suunta, miksi ei pelkkä volatiliteetin tunnistin.
- Kumpikaan ei lue toisen haaraa ennen lukitusta.

## Lukitus

Omistaja mergeää molempien PR:t vasta, kun molemmat ovat palauttaneet. Merge-kommitti
on lukitus. Sen jälkeen tiedostoja ei muuteta; ainoa poikkeus on kertakorjaus,
jos stromo kaatuu yhden päivän tarkistuksessa ennen ensimmäistä täyttä ajoa.

## Arviointi

1. **Kehitysjakso** 2025-11-01 – 2026-07-31, BTC-USDT: läpäisy [OHJE.md](OHJE.md):n
   kriteereillä (≥ 100 rypästä, reuna ≥ 130/√rypäät pp, ≤ 20 hälytystä/vrk,
   naapurivariantti samaan suuntaan).
2. **Validointijakso** 2021-09-01 – 2025-10-31 läpäisseille samalla kriteerillä.
3. **Koskematon jakso** 2026-08-01 – 2026-10-31 kerran validoinnin läpäisseille.

Tulokset tallennetaan kansioon `tulokset/<tekijä>/` vaihe kerrallaan.

## Voittaja

- Voittaja on se, jonka stromolla on suurin reuna (tavoite ensin − verrokit, pp)
  koskemattomalla jaksolla kaikki vaiheet läpäisseistä.
- Jos kukaan ei läpäise kaikkia vaiheita, kierroksen paras on pisimmälle edennyt
  stromo (saman vaiheen sisällä suurempi reuna), mutta kierros kirjataan ilman
  voittajaa: reunaa ei löytynyt. Sekin on tulos.
