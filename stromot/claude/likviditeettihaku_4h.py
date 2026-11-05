"""Likviditeettihaku 4 h (lukittu jakso): edellisen 4 h ääripään ohi pyyhkäisy, joka ei pidä.

Uusi kortti 5.11.2026 (omistaja): kierroksen Treenileirissä variantti jakso 14400 oli
ainoa erottuva tulos (z 2,70 klusteri-SE:llä, reuna +4,5 pp, 1 880 rypästä), mutta se kuoli
naapurisääntöön (24 h -naapuri toivoton välitarkistuksessa). 4 h ja 24 h ovat eri hypoteeseja,
joten 4 h testataan omana stromonaan. Hypoteesi syntyi kehitysdatasta → Treenileiri ja
Dopingtesti ovat tälle EI-riippumattomia; varsinainen testi on Kausi 2021-09–2025-10 ja
lasketaan testibudjettiin yhdeksi testiksi. Logiikka on sama kuin likviditeettihaku.py:ssä.

Mekanismi: stop- ja breakout-toimeksiannot kasautuvat juuri edellisen ääripään
(4 h tai 24 h korkein/matalin) taakse. Isompi toimija voi työntää hinnan rajan
yli laukaistakseen ne ja täyttää oman vastakkaisen positionsa niitä vastaan.
Kun laukaistut toimeksiannot on syöty eikä uusia ostajia/myyjiä tule, hinta
palaa rajan sisään. Paluu rajan sisäpuolelle muutaman minuutin sisällä paljastaa,
että ylitys oli likviditeetin haku eikä aito murto.

Odotettu suunta: pyyhkäisyä vastaan (yläpään pyyhkäisyn jälkeen alas, alapään ylös).

Ei pelkkä volatiliteetin tunnistin: hälytys vaatii epäonnistuneen ylityksen
nimenomaisen tason yli, ja suunta tulee siitä, kummalle puolelle hinta palasi.
Ylitys, joka pitää, ei tuota hälytystä. Erottuu murrosta: murto hälyttää 60 min
ääripään ylityksestä ylityksen suuntaan; tämä odottaa 4 h tai 24 h ääripään
ylityksen epäonnistumista ja hälyttää vastaan.
"""

NIMI = "Likviditeettihaku 4 h"
SELITYS = (
    "Minuutin korkein/matalin ylittää edellisen 4 h ääripään vähintään 0,1·σ15; "
    "5 min sisällä minuutti sulkeutuu takaisin ääripään sisäpuolelle → pyyhkäisyä vastaan."
)
EHDOT = ("Pyyhkäisy", "Paluu")
PARAMETRIT = {
    "exchange": {"type": "enum", "default": "okx", "choices": ["okx"]},
    "instrument": {
        "type": "enum",
        "default": "BTC-USDT",
        "choices": ["BTC-USDT", "BTC-EUR", "BTC-USDC"],
    },
    "cooldown_seconds": {"type": "integer", "default": 3600, "min": 0, "max": 86400},
    "jakso": {
        "type": "enum",
        "default": "14400",
        "choices": ["14400"],
        "label": "Ääripään takajakso s (lukittu 4 h)",
    },
}
TARVITSEE = {
    "hinta": {"kind": "series", "field": "close", "step": 60},
    "korkein": {"kind": "series", "field": "high", "step": 60},
    "matalin": {"kind": "series", "field": "low", "step": 60},
    "huippu": {"kind": "window", "source": "korkein", "op": "max", "seconds": "$jakso"},
    "pohja": {"kind": "window", "source": "matalin", "op": "min", "seconds": "$jakso"},
    "sigma15": {"kind": "sigma", "source": "hinta", "period": 900, "count": 96},
    "paluu": {"kind": "follow", "seconds": 300},
}


def ehto(ctx):
    if "huippu" not in ctx.uudet:
        return None
    hinta = ctx.palikat["hinta"]
    # Edellisen minuutin ikkuna-arvot: eivät sisällä juuri sulkeutunutta minuuttia.
    vanha_huippu = ctx.state.get("huippu")
    vanha_pohja = ctx.state.get("pohja")
    marginaali = ctx.luku("0.1") * ctx.palikat["sigma15"]
    yli = vanha_huippu is not None and ctx.palikat["korkein"] > vanha_huippu * (1 + marginaali)
    ali = vanha_pohja is not None and ctx.palikat["matalin"] < vanha_pohja * (1 - marginaali)
    tapahtuma = yli != ali

    suunta = ctx.state.get("suunta")
    taso = ctx.state.get("taso")
    palasi = False
    if suunta == "up" and taso is not None:
        palasi = hinta < taso
    if suunta == "down" and taso is not None:
        palasi = hinta > taso

    seuranta = ctx.seuraa("paluu", tapahtuma, palasi)
    viesti = None
    hsuunta = None
    if seuranta.value is True:
        hsuunta = "down" if suunta == "up" else "up"
        viesti = "Likviditeettihaku: ääripään ylitys ei pitänyt, hinta palasi sisään"
    if seuranta.started_ms == ctx.timestamp_ms:
        suunta = "up" if yli else "down"
        taso = vanha_huippu if yli else vanha_pohja

    return ctx.tulos(
        viesti,
        conditions={"Pyyhkäisy": tapahtuma, "Paluu": seuranta.value},
        state={
            "paluu": seuranta.state,
            "suunta": suunta,
            "taso": taso,
            "huippu": ctx.palikat["huippu"],
            "pohja": ctx.palikat["pohja"],
        },
        direction=hsuunta,
    )
