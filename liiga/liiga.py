#!/usr/bin/env python3
"""LIIGA – stromojen karsinta: Try out → Treenileiri → Dopingtesti → Kuntopuntari →
Kausi → Playoffit → Näytösottelu. Tilastot = kaikkien tulosten kirjanpito.

Ajetaan pelikoneella STROMO4-tutkimuskansiossa (~/stromo4-tutkimus):

    python3 ~/stromo-builder/liiga/liiga.py tila        # missä vaiheessa kukin variantti on
    python3 ~/stromo-builder/liiga/liiga.py aja         # aja seuraavat vaiheet jonossa
    python3 ~/stromo-builder/liiga/liiga.py aja --kuiva # näytä komennot ajamatta
    python3 ~/stromo-builder/liiga/liiga.py raportti    # aamuraportti
    python3 ~/stromo-builder/liiga/liiga.py vie         # tilastot + raportti haaraan tulokset/…
    python3 ~/stromo-builder/liiga/liiga.py paketti X   # ajon/variantin tiivistelmä leikepöydälle AI:lle
    python3 ~/stromo-builder/liiga/liiga.py yo          # aja + raportti + vie (ajastettuun yöajoon)

Etäohjaus (palvelimen liiga.stromo.uk SSH:n pakotetun komennon liiga/liiga-ohjaus kautta):

    liiga.py tila --json            # koneluettava tila (versio 1)
    liiga.py kaynnista | pysayta    # aja-silmukka taustalle / SIGINT sille ja käynnissä olevalle ajolle
    liiga.py jono-ensin|jono-ohita|jono-palauta <variantti>   # omistajan järjestys, data/research/liiga/jono.json

LIIGA 2 (selainohjaus, STROMO4_liiga2_maarittely.md): stromo kulkee kaikkine variantteineen,
ja omistaja siirtää sen vaihe kerrallaan. Ilman siirtoa mitään ei ajeta.

    liiga.py hae                     # builder mainista; STROMO4-tutkimuskansio + uv sync vain, kun LIIGA ei aja
    liiga.py tila2                   # koneluettava tila, versio 2 (prospektit, ajojono, odottavat, hautausmaa…)
    liiga.py siirra|palauta|ylos|alas gpt/utc_paivanvaihde
    liiga.py teho kevyt|taysi        # 4 prosessia / ytimet − 2 (koskee replay-ajoja)
    liiga.py playoffit X --vahvista X   # omistaja avaa koskemattoman jakson; ajetaan seuraavalla Aja-painalluksella
    Tapahtumat (data/research/liiga/tapahtumat.jsonl) liven Lokiin ja Telegramiin palvelimen kautta.

Vain standardikirjasto. LIIGA ei koskaan avaa koskematonta jaksoa (Playoffit):
se tulostaa omistajalle valmiin komennon. Tulokset luetaan ajojen config.json-
tiedostoista, joten valmiita ajoja (myös kierroksen 1 k1-ajot) ei ajeta uudelleen.
"""

import argparse
import ast
import fcntl
import os
import re
import signal
import hashlib
import itertools
import json
import math
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import NormalDist

BUILDER = Path(__file__).resolve().parents[1]
SAANNOT = json.loads((BUILDER / "liiga" / "saannot.json").read_text())
RUNS = Path("data/research/runs")
TILA = Path("data/research/liiga")
TILASTOT = TILA / "tilastot.jsonl"
JONO = TILA / "jono.json"  # omistajan järjestys: {"ensin": [id…], "ohitetut": [id…]}
RUNNING = TILA / "kaynnissa.json"
LOCK = TILA / "aja.lock"
PIDFILE = TILA / "aja.pid"
STAGE_OF_JOB = {"tryout": "Try out", "valitarkistus": "Treenileiri", "treenileiri": "Treenileiri",
                "dopingtesti": "Dopingtesti", "kausi": "Kausi", "playoffit": "Playoffit"}
ARVIO_S = {"tryout": 90, "valitarkistus": 180, "treenileiri": 600, "dopingtesti": 120, "kausi": 1200,
           "playoffit": 600}
CLUSTER_MS = 60 * 60_000
VAIHEET = ["Try out", "Treenileiri", "Dopingtesti", "Kuntopuntari", "Kausi", "Playoffit", "Näytösottelu"]
# Tappotestit (research.tappotestit) jaetaan kahteen vaiheeseen:
DOPING = ("taysmatyt",)  # huijaako: selittyykö reuna volatiliteetilla/kellonajalla
KUNTO = ("puoliskot", "tilat", "kulut")  # kestääkö: ajan, markkinatilojen ja kulujen yli
UV = ["uv", "run", "--group", "research", "python", "-m"]


# ---------- stromot ja variantit ----------


def enum_choices(source):
    """PARAMETRIT-literaalin enum-valinnat (ei exchange/instrument)."""
    for node in ast.parse(source).body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and getattr(node.targets[0], "id", None) == "PARAMETRIT"
        ):
            schema = ast.literal_eval(node.value)
            return {
                k: [str(c) for c in v["choices"]]
                for k, v in schema.items()
                if v.get("type") == "enum" and k not in ("exchange", "instrument")
            }
    raise ValueError("PARAMETRIT puuttuu")


def stromo_meta(source):
    """NIMI ja SELITYS stromotiedostosta (ei suoriteta)."""
    meta = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
            if name in ("NIMI", "SELITYS"):
                try:
                    meta[name.lower()] = ast.literal_eval(node.value)
                except ValueError:
                    pass
    return meta


def variants():
    result = []
    for path in sorted((BUILDER / "stromot").glob("*/*.py")):
        if path.name.startswith("_"):
            continue
        source = path.read_text(encoding="utf-8")
        sha = hashlib.sha256(source.encode()).hexdigest()
        choices = enum_choices(source)
        meta = stromo_meta(source)
        keys = sorted(choices)
        for combo in itertools.product(*(choices[k] for k in keys)) if keys else [()]:
            params = dict(zip(keys, combo))
            name = path.relative_to(BUILDER / "stromot").with_suffix("").as_posix()
            tag = "-".join(f"{k}_{v}" for k, v in params.items()).replace(".", "_") or "oletus"
            result.append(
                {
                    "stromo": name,
                    "file": path,
                    "sha256": sha,
                    "params": params,
                    "id": f"{name.replace('/', '-')}-{tag}",
                    "nimi": meta.get("nimi", name),
                    "selitys": meta.get("selitys", ""),
                }
            )
    return result


# ---------- ajojen luku ----------


def index_runs():
    runs = {}
    # Yksittäisajot: runs/<ajo>/config.json; yhteisajot: runs/<erä>/<variantti>/config.json
    for config_path in [*RUNS.glob("*/config.json"), *RUNS.glob("*/*/config.json")]:
        try:
            config = json.loads(config_path.read_text())
        except (OSError, ValueError):
            continue
        sha = config.get("stromo_source_sha256")
        if not sha:
            continue
        params = {k: str(v) for k, v in config.get("parameters", {}).items()}
        key = (sha, config.get("pair"), config.get("start"), config.get("end"))
        runs.setdefault(key, []).append((params, config_path.parent, config))
    return runs


def find_run(runs, v, start, end, *, complete=True):
    """Valmis ajo (tai complete=False: mikä tahansa, myös kesken oleva)."""
    found = (None, None)
    for params, path, config in runs.get((v["sha256"], SAANNOT["pari"], start, end), []):
        if all(params.get(k) == val for k, val in v["params"].items()):
            if config.get("status") == "complete":
                return path, config
            if not complete and found[0] is None:
                found = (path, config)
    return found


def clusters(timestamps):
    ordered = sorted(timestamps)
    return (1 + sum(b - a >= CLUSTER_MS for a, b in zip(ordered, ordered[1:]))) if ordered else 0


def metrics(path, config):
    signals = []
    with (path / "events.jsonl").open() as stream:
        for line in stream:
            event = json.loads(line)
            if event.get("sample") != "random" and event.get("direction") in ("up", "down"):
                signals.append(event["timestamp_ms"])
    p = config["primary_summary"]
    s, r = p["signal"]["directional"], p["random"]["directional"]
    days = (date.fromisoformat(config["end"]) - date.fromisoformat(config["start"])).days + 1
    return {
        "halytykset": config.get("signal_count", len(signals)),
        "per_vrk": config.get("signal_count", len(signals)) / days,
        "rypaat": clusters(signals),
        "s_osuma": s.get("target", 0),
        "s_stop": s.get("stop", 0),
        "r_osuma": r.get("target", 0),
        "r_stop": r.get("stop", 0),
    }


def edge(m):
    s = m["s_osuma"] + m["s_stop"]
    r = m["r_osuma"] + m["r_stop"]
    if not s or not r:
        return None, None, None
    win, base = 100 * m["s_osuma"] / s, 100 * m["r_osuma"] / r
    return win, base, win - base


# ---------- tilastot (append-only) ----------


def read_ledger():
    if not TILASTOT.exists():
        return []
    return [json.loads(line) for line in TILASTOT.read_text().splitlines() if line.strip()]


def record(rows, row):
    key = (row["tapahtuma"], row["sha256"], json.dumps(row["params"], sort_keys=True), row.get("kausi"))
    if any(
        (r["tapahtuma"], r["sha256"], json.dumps(r["params"], sort_keys=True), r.get("kausi")) == key
        for r in rows
    ):
        return
    row["aika"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    TILA.mkdir(parents=True, exist_ok=True)
    with TILASTOT.open("a") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    rows.append(row)


def last(rows, event, v, kausi=None):
    for r in reversed(rows):
        if (
            r["tapahtuma"] == event
            and r["sha256"] == v["sha256"]
            and r["params"] == v["params"]
            and r.get("kausi") == kausi
        ):
            return r
    return None


def base_row(v, event):
    return {"tapahtuma": event, "stromo": v["stromo"], "sha256": v["sha256"], "params": v["params"]}


# ---------- vaiheet ----------


def tryout_file(v):
    return TILA / "tryout" / f"{v['id']}-{v['sha256'][:12]}.json"


def neighbor_sign(rows, n):
    """Naapurin tila: True = Treenileirillä plussalla, False = miinuksella tai pudonnut
    (Try out / välitarkistus), None = vielä kesken tai ohitettu naapurin takia."""
    nr = last(rows, "treenileiri", n)
    if nr:
        return nr["tulos"]["reuna"] is not None and nr["tulos"]["reuna"] > 0
    if any((x := last(rows, ev, n)) and not x["lapaisy"] for ev in ("valitarkistus", "tryout")):
        return False
    return None


def evaluate(vs, rows, runs):
    """Päivittää tilastot valmiiden ajojen perusteella ja palauttaa tilan per variantti."""
    t = SAANNOT["treenileiri"]
    state = {}
    # Try out
    for v in vs:
        f = tryout_file(v)
        if f.exists() and not last(rows, "tryout", v):
            result = json.loads(f.read_text())
            if missing_block(result):
                continue  # puuttuva palikka ei karsi: stromo odottaa STROMO4:n päivitystä
            cap = SAANNOT["tryout"]["max_halytykset"]
            ok = result.get("ok", False) and result.get("alerts_per_day", 0) <= cap
            record(rows, {**base_row(v, "tryout"), "lapaisy": ok, "tulos": result, "seula": seula()})
    # Välitarkistus: ensimmäinen kolmannes saa vain pudottaa (tiheys, harvinaisuus, toivottomuus)
    vt = t["valitarkistus"]
    for v in vs:
        if last(rows, "valitarkistus", v) or find_run(runs, v, t["alku"], t["loppu"])[1]:
            continue
        path, config = find_run(runs, v, t["alku"], vt["loppu"])
        if config and config.get("status") == "complete":
            m = metrics(path, config)
            _, _, e = edge(m)
            reasons = []
            if m["rypaat"] < vt["min_rypaat"]:
                reasons.append("harvinainen")
            if m["per_vrk"] > vt["max_vrk"]:
                reasons.append("tiheä")
            if m["rypaat"] and e is not None and e < vt["toivottomuus_kerroin"] / math.sqrt(m["rypaat"]):
                reasons.append("toivoton")
            if e is None:
                reasons.append("ei suuntaa")
            record(
                rows,
                {**base_row(v, "valitarkistus"), "lapaisy": not reasons, "syyt": reasons, "ajo": path.name,
                 "tulos": {**m, "reuna": e}},
            )
    # Treenileiri
    for v in vs:
        path, config = find_run(runs, v, t["alku"], t["loppu"])
        if config and config.get("status") == "complete" and not last(rows, "treenileiri", v):
            m = metrics(path, config)
            win, base, e = edge(m)
            threshold = t["kynnys_kerroin"] / math.sqrt(m["rypaat"]) if m["rypaat"] else None
            reasons = []
            if m["rypaat"] < t["min_rypaat"]:
                reasons.append("rypäät")
            if e is None or threshold is None or e < threshold:
                reasons.append("reuna")
            if m["per_vrk"] > t["max_vrk"]:
                reasons.append("tiheys")
            record(
                rows,
                {
                    **base_row(v, "treenileiri"),
                    "ajo": path.name,
                    "tulos": {**m, "osuma": win, "verrokki": base, "reuna": e, "kynnys": threshold},
                    "syyt": reasons,
                    "seula": seula(),
                },
            )
    # 3.1d: kun yksikin saman stromon variantti on jo miinuksella tai karsittu, kukaan
    # sen naapureista ei voi enää läpäistä naapurisääntöä -> keskeneräisiä ei ajeta.
    doomed = {v["stromo"] for v in vs if neighbor_sign(rows, v) is False} if seula()["karsinta"] else set()
    for v in vs:
        if (
            v["stromo"] in doomed
            and not last(rows, "treenileiri", v)
            and neighbor_sign(rows, v) is None
            and (to := last(rows, "tryout", v)) and to["lapaisy"]
        ):
            record(rows, {**base_row(v, "ohitus"), "lapaisy": False, "syy": "naapuri karsittu"})
    # LIIGA 2: ylennys lasketaan seulasta (promoted); omistaja siirtää käsin, kiintiötä ei ole.
    # Dopingtesti ja Kuntopuntari: ajokansion tappotestit.json (research.tappotestit, 3.1b)
    for v in vs:
        tr = last(rows, "treenileiri", v)
        if promoted(rows, v, vs) and not last(rows, "dopingtesti", v):
            f = RUNS / tr["ajo"] / "tappotestit.json"
            if f.exists():
                tests = json.loads(f.read_text()).get("testit", {})
                for event, names in (("dopingtesti", DOPING), ("kuntopuntari", KUNTO)):
                    record(
                        rows,
                        {
                            **base_row(v, event),
                            "lapaisy": all(tests.get(n, {}).get("lapaisy") is True for n in names),
                            "tulos": {n: tests.get(n) for n in names},
                        },
                    )
    # Kausi: kaudet + yhdistetty, Bonferroni Kaudelle päässeiden määrällä
    k = SAANNOT["kausi"]
    entered = sum(
        1
        for v in vs
        if (d := last(rows, "dopingtesti", v)) and d["lapaisy"]
        and (c := last(rows, "kuntopuntari", v)) and c["lapaisy"]
    )
    for v in vs:
        d = last(rows, "dopingtesti", v)
        c = last(rows, "kuntopuntari", v)
        if not d or not d["lapaisy"] or not c or not c["lapaisy"] or last(rows, "kausi", v):
            continue
        seasons = []
        for start, end in k["kaudet"]:
            path, config = find_run(runs, v, start, end)
            if not config or config.get("status") != "complete":
                break
            seasons.append((f"{start}–{end}", metrics(path, config)))
        if len(seasons) != len(k["kaudet"]):
            continue
        pooled = {key: sum(m[key] for _, m in seasons) for key in ("rypaat", "s_osuma", "s_stop", "r_osuma", "r_stop")}
        _, _, e = edge(pooled)
        z = NormalDist().inv_cdf(1 - k["alfa"] / max(1, entered))
        threshold = 50 * z / math.sqrt(pooled["rypaat"]) if pooled["rypaat"] else None
        plus = sum(1 for _, m in seasons if (edge(m)[2] or 0) > 0)
        ok = e is not None and threshold is not None and e >= threshold and plus >= k["min_kaudet_plussalla"]
        record(
            rows,
            {
                **base_row(v, "kausi"),
                "lapaisy": ok,
                "tulos": {
                    "kaudet": {name: edge(m)[2] for name, m in seasons},
                    "reuna": e,
                    "kynnys": threshold,
                    "z": z,
                    "kaudet_plussalla": plus,
                    "rypaat": pooled["rypaat"],
                },
                "seula": seula(),
            },
        )
    # Playoffit: vain omistajan avaamat ajot luetaan
    p = SAANNOT["playoffit"]
    for v in vs:
        ka = last(rows, "kausi", v)
        if ka and ka["lapaisy"] and not last(rows, "playoffit", v):
            path, config = find_run(runs, v, p["alku"], p["loppu"])
            if config and config.get("status") == "complete" and config.get("holdout_open"):
                m = metrics(path, config)
                _, _, e = edge(m)
                threshold = p["kynnys_kerroin"] / math.sqrt(m["rypaat"]) if m["rypaat"] else None
                record(
                    rows,
                    {
                        **base_row(v, "playoffit"),
                        "lapaisy": e is not None and threshold is not None and e >= threshold,
                        "tulos": {**m, "reuna": e, "kynnys": threshold},
                    },
                )
    for v in vs:
        state[v["id"]] = stage_of(rows, v, vs)
    return state


def stage_of(rows, v, vs=None):
    """(vaihe, tila) – tila: 'odottaa…', 'läpi', 'karsittu: syy'. Läpäisy lasketaan voimassa olevasta seulasta."""
    vs = vs if vs is not None else [v]
    sl = seula()
    to = last(rows, "tryout", v)
    if not to:
        return "Try out", "odottaa"
    if not tryout_pass(to, sl):
        return "Try out", "karsittu"
    tr = last(rows, "treenileiri", v)
    vt = last(rows, "valitarkistus", v)
    if not tr:
        if sl["karsinta"] and vt and not vt["lapaisy"]:
            return "Treenileiri", "karsittu välitarkistuksessa: " + ", ".join(vt["syyt"])
        if sl["karsinta"] and last(rows, "ohitus", v):
            return "Treenileiri", "ei voi edetä: naapuri karsittu"
        if sl["karsinta"] and not vt:
            return "Treenileiri", "odottaa välitarkistusta"
        return "Treenileiri", "odottaa"
    reasons = tl_reasons(tr, sl)
    if reasons:
        return "Treenileiri", "karsittu: " + ", ".join(reasons)
    nb = neighbor_ok(rows, v, vs, sl)
    if nb is None:
        return "Treenileiri", "odottaa naapuria"
    if not nb:
        return "Treenileiri", "karsittu: naapuri"
    d = last(rows, "dopingtesti", v)
    if not d:
        return "Dopingtesti", "odottaa" if Path("research/tappotestit.py").exists() else "odottaa työkalua (3.1b)"
    if not d["lapaisy"]:
        return "Dopingtesti", "karsittu"
    kp = last(rows, "kuntopuntari", v)
    if not kp["lapaisy"]:
        return "Kuntopuntari", "karsittu"
    ka = last(rows, "kausi", v)
    if not ka:
        return "Kausi", "odottaa"
    if not kausi_pass(ka, sl, sum(1 for r in rows if r["tapahtuma"] == "kausi")):
        return "Kausi", "karsittu"
    po = last(rows, "playoffit", v)
    if not po:
        return "Playoffit", "odottaa omistajaa"
    if not po["lapaisy"]:
        return "Playoffit", "karsittu"
    return "Näytösottelu", "valmis"


# ---------- seula (omistajan säädettävä suppilo, 4.11.2026) ----------

SEULAT = {
    "iso_kampa": {"karsinta": False, "tryout_max": 200, "tl_k": 1.0, "tl_min_rypaat": 30, "tl_max_vrk": 20,
                  "naapuri": "enemmistö", "kausi_alfa": 0.05, "kausi_min_plus": 3},
    "normaali": {"karsinta": True, "tryout_max": 200, "tl_k": 2.0, "tl_min_rypaat": 100, "tl_max_vrk": 20,
                 "naapuri": "kaikki", "kausi_alfa": 0.05, "kausi_min_plus": 3},
    "tiukka": {"karsinta": True, "tryout_max": 200, "tl_k": 3.0, "tl_min_rypaat": 100, "tl_max_vrk": 20,
               "naapuri": "kaikki", "kausi_alfa": 0.01, "kausi_min_plus": 3},
}
SEULA_OLETUS = "iso_kampa"
# Omat säätimet: (tyyppi, min, max) tai valinnat
SEULA_RAJAT = {
    "karsinta": (bool,), "tryout_max": (int, 10, 1000), "tl_k": (float, 0.0, 3.0),
    "tl_min_rypaat": (int, 10, 300), "tl_max_vrk": (int, 1, 100), "naapuri": ("kaikki", "enemmistö", "pois"),
    "kausi_alfa": (float, 0.001, 0.2), "kausi_min_plus": (int, 1, 4),
}
VERTAILTAVAT = ("tl_k", "tl_min_rypaat", "tl_max_vrk", "naapuri", "karsinta", "tryout_max")


def seula():
    """Voimassa oleva seula: {'nimi': …, arvot…}."""
    c = read_json(OHJAUS, {}).get("seula") or {}
    base = dict(SEULAT.get(c.get("nimi"), SEULAT[SEULA_OLETUS]))
    if c.get("nimi") == "oma":
        base.update({k: c[k] for k in SEULA_RAJAT if k in c})
    return {"nimi": c.get("nimi") if c.get("nimi") in (*SEULAT, "oma") else SEULA_OLETUS, **base}


def tryout_pass(row, sl):
    result = row.get("tulos", {})
    return bool(result.get("ok")) and result.get("alerts_per_day", 0) <= sl["tryout_max"]


def se_pp(n):
    return 50 / math.sqrt(n) if n else None


def tl_reasons(row, sl):
    t = row["tulos"]
    n, e = t.get("rypaat") or 0, t.get("reuna")
    reasons = []
    if n < sl["tl_min_rypaat"]:
        reasons.append("rypäät")
    if e is None or not n or e < sl["tl_k"] * se_pp(n):
        reasons.append("reuna")
    if t.get("per_vrk", 0) > sl["tl_max_vrk"]:
        reasons.append("tiheys")
    return reasons


def neighbor_ok(rows, v, vs, sl):
    """Naapurisääntö seulan mukaan: True/False/None (odottaa)."""
    if sl["naapuri"] == "pois":
        return True
    group = [n for n in vs if n["stromo"] == v["stromo"]]
    signs = []
    for n in group:
        to = last(rows, "tryout", n)
        tr = last(rows, "treenileiri", n)
        if tr:
            signs.append(tr["tulos"]["reuna"] is not None and tr["tulos"]["reuna"] > 0)
        elif (to and not tryout_pass(to, sl)) or (
                sl["karsinta"] and (x := last(rows, "valitarkistus", n)) and not x["lapaisy"]):
            signs.append(False)
        else:
            signs.append(None)
    if sl["naapuri"] == "kaikki":
        others = [sg for n, sg in zip(group, signs) if n is not v]
        return False if False in others else None if None in others else True
    if None in signs:
        return None
    return 2 * sum(signs) > len(signs)


def promoted(rows, v, vs):
    sl = seula()
    tr = last(rows, "treenileiri", v)
    return bool(tr) and not tl_reasons(tr, sl) and neighbor_ok(rows, v, vs, sl) is True


def kausi_pass(row, sl, entered):
    t = row["tulos"]
    n = t.get("rypaat")
    if n is None and t.get("kynnys") and t.get("z"):
        n = round((50 * t["z"] / t["kynnys"]) ** 2)  # vanha rivi: rypäät kynnyksestä
    e = t.get("reuna")
    if e is None or not n:
        return False
    z = NormalDist().inv_cdf(1 - sl["kausi_alfa"] / max(1, entered))
    return e >= 50 * z / math.sqrt(n) and t.get("kaudet_plussalla", 0) >= sl["kausi_min_plus"]


def jalkisaadetty(row, sl):
    """Arvioitiinko tulos eri seulalla kuin ajon aikana? Vanhat rivit = Normaali."""
    then = row.get("seula") or {"nimi": "normaali", **SEULAT["normaali"]}
    return any(then.get(k) != sl.get(k) for k in VERTAILTAVAT)


def chance_meter(vs, rows, sl):
    """Sattumamittari: odotettu sattumaläpäisy vs toteutunut Treenileirillä."""
    alpha = 1 - NormalDist().cdf(sl["tl_k"])
    measured = [(v, r) for v in vs if (r := last(rows, "treenileiri", v))]
    passed = sum(1 for _, r in measured if not tl_reasons(r, sl))
    warn = []
    if alpha * 100 >= 5:
        warn.append(f"⚠️ sattumalta läpi ~{alpha * 100:.0f} / 100 varianttia")
    if sl["tl_min_rypaat"] < 100:
        warn.append("⚠️ pieni otos: reuna heiluu")
    if sl["naapuri"] == "pois":
        warn.append("⚠️ naapurisääntö pois: yksittäinen onnenkantamoinen pääsee läpi")
    if sl["kausi_alfa"] > 0.05:
        warn.append("⚠️ Kauden α yli 5 %")
    expected = len(measured) * alpha
    return {
        "alfa": alpha, "per_100": round(alpha * 100, 1), "testattu": len(measured),
        "odotettu_sattuma": round(expected, 2), "lapaisseet": passed,
        "erottuu": passed > expected + 2 * math.sqrt(max(expected * (1 - alpha), 1e-9)),
        "varoitukset": warn,
    }


def results_table(vs, rows, sl):
    out = []
    for v in vs:
        r = last(rows, "treenileiri", v)
        if not r:
            continue
        t = r["tulos"]
        n, e = t.get("rypaat") or 0, t.get("reuna")
        se = se_pp(n)
        out.append({
            "id": v["id"], "stromo": v["stromo"], "params": v["params"], "reuna": e, "rypaat": n,
            "se": se, "z": (e / se) if (e is not None and se) else None, "per_vrk": t.get("per_vrk"),
            "lapaisy": not tl_reasons(r, sl), "syyt": tl_reasons(r, sl),
            "jalkisaadetty": jalkisaadetty(r, sl), "ajon_seula": (r.get("seula") or {}).get("nimi", "normaali"),
        })
    return out


# ---------- ajaminen ----------


def param_args(v):
    return [a for k, val in v["params"].items() for a in ("--param", f"{k}={val}")]


def replay_cmd(v, start, end, run_id):
    run_id = f"{run_id}-{datetime.now():%m%d%H%M}"
    return UV + [
        "research.replay", "--stromo", v["id"], "--stromo-file", str(v["file"]),
        "--pair", SAANNOT["pari"], "--start", start, "--end", end,
        "--output", str(RUNS / run_id),
    ] + param_args(v)


def jobs(vs, rows, runs, state):
    """Seuraavat ajettavat komennot vaiheittain, halvimmat ensin."""
    out = []
    t, k = SAANNOT["treenileiri"], SAANNOT["kausi"]
    for v in vs:
        stage, status = state[v["id"]]
        if stage == "Try out" and status == "odottaa":
            if waiting_block(v):
                continue
            out.append(("tryout", v, UV + [
                "research.check_stromo", str(v["file"]), "--json",
                "--day", SAANNOT["tryout"]["paiva"], "--pair", SAANNOT["pari"],
            ] + param_args(v)))
        elif stage == "Treenileiri" and status == "odottaa välitarkistusta" and seula()["karsinta"]:
            path, _ = find_run(runs, v, t["alku"], t["valitarkistus"]["loppu"])
            if not path:
                out.append(("valitarkistus", v, replay_cmd(v, t["alku"], t["valitarkistus"]["loppu"], f"liiga-vt-{v['id']}")))
        elif stage == "Treenileiri" and status == "odottaa":
            path, _ = find_run(runs, v, t["alku"], t["loppu"])
            if not path:
                out.append(("treenileiri", v, replay_cmd(v, t["alku"], t["loppu"], f"liiga-tl-{v['id']}")))
        elif stage == "Dopingtesti" and status == "odottaa":
            tr = last(rows, "treenileiri", v)
            if not Path("research/tappotestit.py").exists():
                continue  # työkalu (3.1b) puuttuu vielä
            out.append(("dopingtesti", v, UV + [
                "research.tappotestit", str(RUNS / tr["ajo"]), "--kulut-pct", SAANNOT["dopingtesti"]["kulut_pct"],
            ]))
        elif stage == "Kausi" and status == "odottaa":
            for i, (start, end) in enumerate(k["kaudet"], 1):
                path, _ = find_run(runs, v, start, end)
                if not path:
                    out.append(("kausi", v, replay_cmd(v, start, end, f"liiga-k{i}-{v['id']}")))
        elif (stage, status) == ("Playoffit", "odottaa omistajaa") and v["stromo"] in playoff_opened():
            p = SAANNOT["playoffit"]
            if not find_run(runs, v, p["alku"], p["loppu"])[0]:
                out.append(("playoffit", v, replay_cmd(v, p["alku"], p["loppu"], f"liiga-po-{v['id']}")
                            + ["--open-holdout", "--reason", "LIIGA Playoffit (omistaja avasi selaimesta)"]))
    order = {"tryout": 0, "valitarkistus": 1, "treenileiri": 2, "dopingtesti": 3, "kausi": 4, "playoffit": 5}
    return sorted(out, key=lambda j: order[j[0]])


# ---------- yhteisajo (omistaja 4.11. klo 23.44) ----------

ERA_KOOT = 60  # enintään näin monta varianttia yhteen kauppakierrokseen
ERALLISET = {"valitarkistus", "treenileiri", "kausi"}
TUNNISTIMET = {"hintahyppy", "volyymi_normaaliin", "cvd_kaanto", "cvd_paine", "momentum", "regiimi",
               "spreadi_normaaliin", "syvyys_normaaliin"}


def rhythm_class(v):
    """Nopean polun luokka: erään vain samaa luokkaa (sekaerä putoaa hitaalle polulle)."""
    for node in ast.parse(v["file"].read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "EHDOT":
            try:
                ehdot = ast.literal_eval(node.value)
            except ValueError:
                return "python"
            if not isinstance(ehdot, dict):
                return "python"
            kinds = {c.get("palikka") for c in ehdot.values() if isinstance(c, dict)}
            return "tunnistin" if kinds & TUNNISTIMET else "deklaratiivinen"
    return "python"


def period_of(cmd):
    return (cmd[cmd.index("--start") + 1], cmd[cmd.index("--end") + 1]) if "--start" in cmd else None


def batch_group(todo):
    """Jonon ensimmäisen kanssa samaa vaihetta, jaksoa ja rytmiluokkaa olevat ajot (jonon järjestyksessä)."""
    kind, v, cmd = todo[0]
    if kind not in ERALLISET:
        return [todo[0]]
    period, cls = period_of(cmd), rhythm_class(v)
    group = [(k, w, c) for k, w, c in todo
             if k == kind and period_of(c) == period and rhythm_class(w) == cls]
    return group[:ERA_KOOT]


def batch_cmd(kind, group, dry=False):
    stamp = datetime.now().strftime("%m%d%H%M%S")
    start, end = period_of(group[0][2])
    spec = [{"id": w["id"], "stromo-file": str(w["file"].resolve()), "params": w["params"]} for _, w, _ in group]
    path = TILA / "erat" / f"{kind}-{stamp}.json"
    if not dry:
        atomic_write(path, spec)
    return UV + ["research.replay", "--batch", str(path), "--pair", SAANNOT["pari"], "--start", start,
                 "--end", end, "--output", str(RUNS / f"liiga-era-{kind}-{stamp}")]


def run_jobs(dry):
    if dry:
        return run_queue(dry)
    TILA.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("LIIGA on jo käynnissä.", flush=True)
            return
        PIDFILE.write_text(str(os.getpid()))
        try:
            run_queue(dry)
        except KeyboardInterrupt:
            print(f"{datetime.now():%H.%M} pysäytetty.", flush=True)
        finally:
            RUNNING.unlink(missing_ok=True)
            PIDFILE.unlink(missing_ok=True)


def run_queue(dry):
    """LIIGA 2: ajetaan vain omistajan ajojonoon siirtämien stromojen sallitut vaiheet, jonon järjestyksessä."""
    ran = 0
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    while True:
        vs, rows, runs = variants(), read_ledger(), index_runs()
        state = evaluate(vs, rows, runs)
        if not dry:
            sync_events(vs, rows, runs, state)
        todo = allowed_jobs(vs, rows, runs, state)
        if not todo:
            print("Jono tyhjä.")
            if ran and not dry:
                queue_done_event(vs, rows, runs, started)
            return
        kind, v, cmd = todo[0]
        group = batch_group(todo)
        if len(group) > 1:
            cmd = batch_cmd(kind, group, dry)
        cmd = with_power(cmd)
        if dry:
            print(f"{datetime.now():%H.%M} teho {control()['teho']}")
            if len(group) > 1:
                print(f"  yhteisajo {kind}: {len(group)} varianttia → {' '.join(cmd)}")
            for kind_, v_, cmd_ in todo[len(group):] if len(group) > 1 else todo:
                print(f"  {kind_:12} {' '.join(with_power(cmd_))}")
            return
        atomic_write(RUNNING, {
            "tyyppi": kind, "id": v["id"], "stromo": v["stromo"], "ajo": output_of(cmd),
            "alkoi": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "vaihe": STAGE_OF_JOB[kind], "teho": control()["teho"],
            "era": [w["id"] for _, w, _ in group] if len(group) > 1 else None,
            "stromot": sorted({w["stromo"] for _, w, _ in group}),
        })
        print(f"{datetime.now():%H.%M} {kind}: {v['id']}"
              + (f" + {len(group) - 1} muuta yhteisajona" if len(group) > 1 else ""), flush=True)
        if kind == "tryout":
            proc = subprocess.run(cmd, capture_output=True, text=True)
            try:
                result = json.loads(proc.stdout)
            except ValueError:
                result = {"ok": False, "virhe": (proc.stderr or proc.stdout)[-2000:]}
            result.setdefault("ok", proc.returncode == 0)
            result["stromo4"] = stromo4_revision()
            f = tryout_file(v)
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps(result, ensure_ascii=False))
        else:
            log = TILA / "ajot.log"
            TILA.mkdir(parents=True, exist_ok=True)
            with log.open("a") as stream:
                stream.write(f"\n{datetime.now().isoformat()} {kind} {v['id']}\n")
                stream.flush()
                proc = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT)
            if proc.returncode != 0:
                print(f"  epäonnistui ({proc.returncode}), ks. {log}. Pysähdytään.", flush=True)
                if proc.returncode not in (-signal.SIGINT, 130):
                    add_event("virhe", v["stromo"], f"Ajo epäonnistui ({STAGE_OF_JOB[kind]}, {v['id']}); LIIGA pysähtyi.")
                return
        ran += 1


# ---------- tulosteet ----------


def fmt(x, d=1):
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def table(vs, rows, state):
    lines = ["| Variantti | Vaihe | Tila | Treenileiri reuna / kynnys pp | Rypäät |", "|---|---|---|---:|---:|"]
    for v in vs:
        stage, status = state[v["id"]]
        tr = last(rows, "treenileiri", v)
        t = tr["tulos"] if tr else {}
        lines.append(
            f"| {v['id']} | {stage} | {status} | {fmt(t.get('reuna'), 2)} / {fmt(t.get('kynnys'), 2)} | {t.get('rypaat', '—')} |"
        )
    return "\n".join(lines)


def report(vs, rows, state):
    t = SAANNOT["treenileiri"]
    tested = [r for r in rows if r["tapahtuma"] == "treenileiri"]
    alpha = 1 - NormalDist().cdf(2)  # 100/√rypäät ≈ 2 keskivirhettä
    passed = {s: 0 for s in VAIHEET}
    reached = {s: 0 for s in VAIHEET}
    for v in vs:
        stage, status = state[v["id"]]
        i = VAIHEET.index(stage)
        for s in VAIHEET[: i + 1]:
            reached[s] += 1
        for s in VAIHEET[:i]:
            passed[s] += 1
    out = [
        f"# LIIGA – raportti {datetime.now():%-d.%-m.%Y %H.%M}",
        "",
        f"Variantteja {len(vs)}, välitarkistuksessa pudonneita "
        f"{sum(1 for r in rows if r['tapahtuma'] == 'valitarkistus' and not r['lapaisy'])}, "
        f"Treenileirillä mitattu {len(tested)}. "
        f"Sattumalta Treenileirin läpäiseviä odotetaan noin {fmt(len(tested) * alpha)} "
        f"(kynnys {t['kynnys_kerroin']}/√rypäät ≈ {fmt(alpha * 100)} % per variantti).",
        "",
        "| Vaihe | Saapui | Läpi |",
        "|---|---:|---:|",
    ]
    out += [f"| {s} | {reached[s]} | {passed[s]} |" for s in VAIHEET[:-1]]
    out += ["", "## 🏆 Hall of Fame", "", hall_of_fame(vs, rows, state), "", "## Kaikki variantit", "", table(vs, rows, state)]
    ready = [v["id"] for v in vs if state[v["id"]] == ("Playoffit", "odottaa omistajaa")]
    if ready:
        out += ["", "**Valmiina Playoffeihin (omistaja ajaa, kerran):**", ""]
        p = SAANNOT["playoffit"]
        for v in vs:
            if v["id"] in ready:
                cmd = replay_cmd(v, p["alku"], p["loppu"], f"liiga-po-{v['id']}")
                out.append("    " + " ".join(cmd) + ' --open-holdout --reason "LIIGA Playoffit"')
    return "\n".join(out) + "\n"


def hof_entries(vs, rows):
    """Treenileirillä mitatut, reuna/kynnys-suhteen mukaan paras ensin."""
    best = []
    for v in vs:
        row = last(rows, "treenileiri", v)
        if row and row["tulos"].get("reuna") is not None and row["tulos"].get("kynnys"):
            t = row["tulos"]
            best.append((t["reuna"] / t["kynnys"], v, t))
    best.sort(key=lambda b: -b[0])
    return best


def hall_of_fame(vs, rows, state, top=5):
    """Pistepörssi: Treenileirin reuna suhteessa kynnykseen, paras ensin."""
    best = hof_entries(vs, rows)
    medals = ["🥇", "🥈", "🥉"]
    lines = [
        "| # | Tekijä | Stromo | Variantti | Reuna pp | Kynnys pp | Rypäät | Vaihe |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for i, (ratio, v, t) in enumerate(best[:top]):
        author, name = v["stromo"].split("/", 1)
        params = ", ".join(f"{k} {val}" for k, val in v["params"].items()) or "oletus"
        stage, status = state[v["id"]]
        mark = medals[i] if i < 3 else str(i + 1)
        lines.append(
            f"| {mark} | {author} | {name} | {params} | {fmt(t['reuna'], 2)} | {fmt(t['kynnys'], 2)} "
            f"| {t['rypaat']} | {stage}: {status} |"
        )
    if not best:
        lines.append("| – | – | – | – | – | – | – | Treenileiri kesken |")
    lines += [
        "",
        f"Mitattu {len(best)} varianttia. Läpäisy vaatii reunan ≥ kynnyksen (suhde ≥ 1) "
        "ja naapurivariantin plussalla. Päivittyy LIIGAn yöajosta.",
    ]
    return "\n".join(lines)


def update_readme(text_block):
    readme = BUILDER / "README.md"
    content = readme.read_text()
    start, end = "<!-- HOF:START -->", "<!-- HOF:END -->"
    if start in content and end in content:
        head, rest = content.split(start, 1)
        _, tail = rest.split(end, 1)
        readme.write_text(f"{head}{start}\n{text_block}\n{end}{tail}")


def export(text, hof=None):
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    branch = f"tulokset/{stamp}"
    git = ["git", "-C", str(BUILDER)]
    subprocess.run(git + ["fetch", "-q", "origin", "main"], check=True)
    subprocess.run(git + ["checkout", "-q", "-B", branch, "origin/main"], check=True)
    target = BUILDER / "tilastot"
    target.mkdir(exist_ok=True)
    if TILASTOT.exists():
        (target / "tilastot.jsonl").write_text(TILASTOT.read_text())
    (target / "raportti.md").write_text(text)
    if hof:
        update_readme(hof)
    subprocess.run(git + ["add", "tilastot", "README.md"], check=True)
    subprocess.run(git + ["-c", "user.name=LIIGA pelikone", "-c", "user.email=liiga@localhost",
                          "commit", "-q", "-m", f"LIIGA-tulokset {stamp}"], check=True)
    subprocess.run(git + ["push", "-q", "origin", branch], check=True)
    subprocess.run(git + ["checkout", "-q", "main"], check=False)
    print(f"Viety haaraan {branch}. Avaa PR GitHubissa tai pyydä Claudea.")


def package(target, vs, rows):
    """Yksi markdown-paketti AI-tarkastukseen: stromo, tilastorivit ja ajojen summary.md:t."""
    matches = [v for v in vs if target in (v["id"], v["stromo"], v["stromo"].split("/")[-1])]
    run_dirs = [RUNS / target] if (RUNS / target / "config.json").exists() else []
    if run_dirs and not matches:
        sha = json.loads((run_dirs[0] / "config.json").read_text()).get("stromo_source_sha256")
        matches = [v for v in vs if v["sha256"] == sha]
    if not matches:
        sys.exit(f"Ei löydy ajoa tai varianttia: {target}")
    runs = index_runs()
    out = [f"# LIIGA-paketti: {target}", ""]
    seen_files = set()
    for v in matches:
        if v["file"] not in seen_files:
            seen_files.add(v["file"])
            out += [f"## Stromo {v['stromo']} (SHA-256 {v['sha256'][:12]})", "", "```python",
                    v["file"].read_text(encoding="utf-8").rstrip(), "```", ""]
        out += [f"## Variantti {v['id']}", "", "Tilastot:", "", "```json"]
        out += [json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows
                if r["sha256"] == v["sha256"] and r["params"] == v["params"]] or ["(ei rivejä)"]
        out += ["```", ""]
        for key, items in runs.items():
            if key[0] != v["sha256"]:
                continue
            for params, path, config in items:
                if all(params.get(k) == val for k, val in v["params"].items()) and (path / "summary.md").exists():
                    out += [f"### Ajo {path.name} ({key[2]} – {key[3]})", "", (path / "summary.md").read_text().strip(), ""]
    text = "\n".join(out) + "\n"
    try:
        subprocess.run(["clip.exe"], input=text.encode("utf-16-le"), check=True)
        print(f"Paketti ({len(text):,} merkkiä) kopioitu leikepöydälle: liitä se Claudelle tai GPT:lle.")
    except (OSError, subprocess.CalledProcessError):
        print(text)


# ---------- ohjaus (liiga-ohjaus / liiga.stromo.uk) ----------


def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False))
    os.replace(tmp, path)


def read_json(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def queue_control():
    c = read_json(JONO, {})
    return {"ensin": list(c.get("ensin", [])), "ohitetut": list(c.get("ohitetut", []))}


def apply_queue(todo):
    """(laji, v, komento, ohitettu): omistajan 'ensin' kärkeen, ohitetut merkitään."""
    c = queue_control()
    first = {i: n for n, i in enumerate(c["ensin"])}
    out = [(k, v, cmd, v["id"] in c["ohitetut"]) for k, v, cmd in todo]
    return sorted(out, key=lambda j: (j[3], first.get(j[1]["id"], len(first))))


def output_of(cmd):
    return Path(cmd[cmd.index("--output") + 1]).name if "--output" in cmd else None


def liiga_running():
    """Onko aja-silmukka käynnissä (lukko varattu)?"""
    if not LOCK.exists():
        return False
    with LOCK.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(lock, fcntl.LOCK_UN)
        return False


def estimates(runs):
    """Mediaanikesto valmiista ajoista samalla jaksolla, muuten vakioarvio."""
    t, k = SAANNOT["treenileiri"], SAANNOT["kausi"]
    spans = {"valitarkistus": [(t["alku"], t["valitarkistus"]["loppu"])], "treenileiri": [(t["alku"], t["loppu"])],
             "kausi": [tuple(x) for x in k["kaudet"]]}
    out = dict(ARVIO_S)
    for kind, wanted in spans.items():
        times = sorted(
            c["elapsed_seconds"]
            for (_, _, start, end), items in runs.items() if (start, end) in wanted
            for _, _, c in items if c.get("status") == "complete" and c.get("elapsed_seconds")
        )
        if times:
            out[kind] = round(times[len(times) // 2])
    return out


def state_json(vs, rows, runs, state):
    by_stage = {s: [0, 0] for s in VAIHEET}
    for v in vs:
        stage, status = state[v["id"]]
        i = VAIHEET.index(stage)
        for s in VAIHEET[: i + 1]:
            by_stage[s][0] += 1
        for s in VAIHEET[:i]:
            by_stage[s][1] += 1
    variants_out = []
    for v in vs:
        stage, status = state[v["id"]]
        tr = last(rows, "treenileiri", v)
        t = tr["tulos"] if tr else None
        variants_out.append({
            "id": v["id"], "stromo": v["stromo"], "tekija": v["stromo"].split("/", 1)[0],
            "params": v["params"], "vaihe": stage, "tila": status,
            "treenileiri": {key: t.get(key) for key in ("reuna", "kynnys", "rypaat", "osuma", "verrokki", "per_vrk")}
            if t else None,
        })
    hof = [{"id": v["id"], "stromo": v["stromo"], "tekija": v["stromo"].split("/", 1)[0], "params": v["params"],
            "suhde": ratio, "reuna": t["reuna"], "kynnys": t["kynnys"], "rypaat": t["rypaat"],
            "vaihe": state[v["id"]][0], "tila": state[v["id"]][1]}
           for ratio, v, t in hof_entries(vs, rows)[:5]]
    est = estimates(runs)
    queue = [{"tyyppi": kind, "id": v["id"], "tekija": v["stromo"].split("/", 1)[0],
              "arvio_s": est.get(kind), "ohitettu": skipped, "syy": None}
             for kind, v, _, skipped in apply_queue(jobs(vs, rows, runs, state))]
    queue += [{"tyyppi": "treenileiri", "id": v["id"], "tekija": v["stromo"].split("/", 1)[0],
               "arvio_s": None, "ohitettu": False, "syy": "naapuri karsittu"}
              for v in vs if state[v["id"]][1] == "ei voi edetä: naapuri karsittu"]
    running = liiga_running()
    current = read_json(RUNNING, None) if running else None
    if current:
        config = read_json(RUNS / current["ajo"] / "config.json", {}) if current.get("ajo") else {}
        pct, eta = config.get("progress_percent"), config.get("eta_seconds")
        current["edistyminen"] = None if pct is None else max(0.0, min(1.0, pct / 100))
        current["arvio_valmis"] = (
            datetime.fromtimestamp(datetime.now(timezone.utc).timestamp() + eta, timezone.utc).isoformat(timespec="seconds")
            if isinstance(eta, (int, float)) else None
        )
    return {
        "versio": 1,
        "aika": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "vaiheet": [{"nimi": s, "saapui": a, "lapi": b} for s, (a, b) in by_stage.items()],
        "variantit": variants_out,
        "hall_of_fame": hof,
        "kaynnissa": current,
        "jono": queue,
        "pelikone": {"liiga_kaynnissa": running},
    }


def start_background():
    if liiga_running():
        return {"ok": True, "viesti": "LIIGA on jo käynnissä"}
    vs, rows, runs = variants(), read_ledger(), index_runs()
    if not allowed_jobs(vs, rows, runs, evaluate(vs, rows, runs)):
        return {"ok": False, "viesti": "Ajojono on tyhjä: siirrä ensin stromo ajojonoon"}
    TILA.mkdir(parents=True, exist_ok=True)
    with (TILA / "aja.log").open("a") as log:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "aja"], stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    return {"ok": True, "pid": child.pid}


def stop_background():
    """SIGINT vain omalle aja-silmukalle ja sen prosessiryhmälle (myös käynnissä oleva ajo)."""
    if not liiga_running():
        return {"ok": True, "viesti": "LIIGA ei ole käynnissä"}
    pid = int(PIDFILE.read_text())
    cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
    if not any(part.endswith(b"liiga.py") for part in cmdline) or b"aja" not in cmdline:
        raise ValueError("PID ei ole LIIGAn aja-prosessi")
    os.killpg(os.getpgid(pid), signal.SIGINT)
    current = read_json(RUNNING, {})
    add_event("keskeytetty", current.get("stromo"),
              "LIIGA pysäytettiin; keskeytetty ajo alkaa seuraavalla kerralla alusta.")
    return {"ok": True, "pysaytetty": pid}


def queue_command(command, identifier, vs):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,511}", identifier or ""):
        raise ValueError("Virheellinen varianttitunniste")
    if identifier not in {v["id"] for v in vs}:
        raise ValueError("Tuntematon variantti")
    c = queue_control()
    c["ensin"] = [i for i in c["ensin"] if i != identifier]
    if command == "jono-ensin":
        c["ohitetut"] = [i for i in c["ohitetut"] if i != identifier]
        c["ensin"].insert(0, identifier)
    elif command == "jono-ohita":
        if identifier not in c["ohitetut"]:
            c["ohitetut"].append(identifier)
    else:  # jono-palauta
        c["ohitetut"] = [i for i in c["ohitetut"] if i != identifier]
    atomic_write(JONO, c)
    return {"ok": True, **c}


# ---------- LIIGA 2: selainohjaus (omistaja lukitsi 4.11.2026, STROMO4_liiga2_maarittely.md) ----------

OHJAUS = TILA / "ohjaus.json"  # {"siirrot": {stromo: vaihe}, "jono": [stromo], "teho": "taysi", "haettu": iso}
TAPAHTUMAT = TILA / "tapahtumat.jsonl"
STROMOTILA = TILA / "stromotila.json"
TAPAHTUMALUKKO = TILA / "tapahtumat.lock"
# Omistajan siirrot: Dopingtesti kattaa Kuntopuntarin (sama tappotestiajo).
SIIRROT = ["Try out", "Treenileiri", "Dopingtesti", "Kausi", "Playoffit"]
SLOT = {"Try out": 0, "Treenileiri": 1, "Dopingtesti": 2, "Kuntopuntari": 2, "Kausi": 3, "Playoffit": 4,
        "Näytösottelu": 5}
KIERROS2_ALKOI = "2026-11-04"
TEHO = {"kevyt": 4, "taysi": max(1, (os.cpu_count() or 1) - 2)}
STROMO_RE = r"[a-z]+/[A-Za-z0-9_]{1,120}"


def control():
    c = read_json(OHJAUS, {})
    return {"siirrot": dict(c.get("siirrot", {})), "jono": list(c.get("jono", [])),
            "teho": c.get("teho") if c.get("teho") in TEHO else "taysi", "haettu": c.get("haettu"),
            "migroitu": bool(c.get("migroitu"))}


def save_control(c):
    saved = read_json(OHJAUS, {})
    saved.update({k: c[k] for k in ("siirrot", "jono", "teho", "haettu", "migroitu")})
    atomic_write(OHJAUS, saved)


def git_out(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


_REVISION = []


def stromo4_revision(refresh=False):
    if refresh or not _REVISION:
        try:
            _REVISION[:] = [git_out("rev-parse", "--short=12", "HEAD")]
        except (OSError, subprocess.CalledProcessError):
            _REVISION[:] = [None]
    return _REVISION[0]


def missing_block(result):
    """Try outin virhe 'tuntematon palikka X' → X (muuten None)."""
    m = re.search(r"tuntematon palikka '?([A-Za-z0-9_]+)'?", json.dumps(result, ensure_ascii=False))
    return m.group(1) if m and not result.get("ok") else None


def waiting_block(v):
    """Puuttuva palikka samalla STROMO4-versiolla → ei ajeta Try outia uudelleen ennen päivitystä."""
    result = read_json(tryout_file(v), None)
    if not result or not missing_block(result):
        return None
    return missing_block(result) if result.get("stromo4") == stromo4_revision() else None


def playoff_opened():
    return {s for s, stage in control()["siirrot"].items() if stage == "Playoffit"}


def with_power(cmd):
    if "research.replay" not in cmd or "--processes" in cmd:
        return cmd
    return cmd + ["--processes", str(TEHO[control()["teho"]])]


def dead_status(status):
    return status.startswith("karsittu") or status.startswith("ei voi edetä")


def stromo_views(vs, rows, runs, state, ctl=None):
    """Stromotason näkymä: kategoria prospekti / jonossa / ajossa / odottaa / hautausmaa / historia / valmis."""
    ctl = ctl or control()
    running = read_json(RUNNING, None) if liiga_running() else None
    pending = jobs(vs, rows, runs, state)
    est = estimates(runs)
    scale = TEHO["taysi"] / TEHO["kevyt"] if ctl["teho"] == "kevyt" else 1
    groups = {}
    for v in vs:
        groups.setdefault(v["stromo"], []).append(v)
    out = {}
    for s, group in groups.items():
        sha = group[0]["sha256"]
        own = [r for r in rows if r["stromo"] == s and r["sha256"] == sha]
        first = min((r["aika"] for r in own), default=None)
        allowed = SIIRROT.index(ctl["siirrot"][s]) if s in ctl["siirrot"] else -1
        sl = seula()
        up = any(promoted(rows, v, vs) for v in group)
        early = sl["karsinta"] and sl["naapuri"] == "kaikki"
        killer = next((v for v in group if neighbor_sign(rows, v) is False), None) if early else None
        alive = [v for v in group if not dead_status(state[v["id"]][1])]
        dead = (bool(killer) and not up) or not alive
        killer = killer or next((v for v in group if dead_status(state[v["id"]][1])), None)
        need = min((SLOT[state[v["id"]][0]] for v in alive), default=None)
        block = next((b for v in group if (b := waiting_block(v))), None)
        mine = [(k, v) for k, v, _ in pending if v["stromo"] == s and SLOT[STAGE_OF_JOB[k]] <= allowed]
        view = {
            "stromo": s, "tekija": s.split("/", 1)[0], "nimi": group[0]["nimi"], "selitys": group[0]["selitys"],
            "siirretty": ctl["siirrot"].get(s),
            "variantit": [{"id": v["id"], "params": v["params"], "vaihe": state[v["id"]][0],
                           "tila": state[v["id"]][1]} for v in group],
        }
        if dead:
            who = killer or group[-1]
            row = next((last(rows, e, who) for e in ("treenileiri", "valitarkistus", "tryout") if last(rows, e, who)),
                       None)
            t = (row or {}).get("tulos", {})
            view |= {"kategoria": "hautausmaa", "vaihe": state[who["id"]][0], "syy": state[who["id"]][1],
                     "aika": (row or {}).get("aika"), "kierros": 1 if first and first < KIERROS2_ALKOI else 2,
                     "luvut": {k: t.get(k) for k in ("reuna", "kynnys", "rypaat", "per_vrk")}}
        elif first and first < KIERROS2_ALKOI:
            view |= {"kategoria": "historia", "kierros": 1, "syy": "kierros 1 – jäi historiaan (omistaja 4.11.)"}
        elif need == SLOT["Näytösottelu"]:
            view |= {"kategoria": "valmis"}
        elif block or (allowed < 0 and not own):
            view |= {"kategoria": "prospekti", "palikka": block}
        elif running and s in (running.get("stromot") or [running.get("stromo")]):
            view |= {"kategoria": "ajossa", "vaihe": running.get("vaihe")}
        elif need is not None and need > allowed:
            view |= {"kategoria": "odottaa", "lapi": SIIRROT[need - 1] if need else None,
                     "seuraava": SIIRROT[need] if need < len(SIIRROT) else None}
        else:
            notes = sorted({state[v["id"]][1] for v in alive})
            view |= {"kategoria": "jonossa", "vaihe": SIIRROT[allowed] if allowed >= 0 else None,
                     "huom": None if mine else ", ".join(notes)}
        if view["kategoria"] in ("jonossa", "ajossa"):
            view["ajoja"] = len(mine)
            view["arvio_s"] = round(sum(est.get(k, ARVIO_S.get(k, 600)) * (1 if k == "tryout" else scale)
                                        for k, _ in mine))
        out[s] = view
    if not ctl["migroitu"]:  # ensimmäinen LIIGA 2 -kutsu: kesken olevat jatkavat nykyisen vaiheensa loppuun
        for s, view in out.items():
            group = groups[s]
            alive = [v for v in group if not dead_status(state[v["id"]][1])]
            if view["kategoria"] == "odottaa" and alive:
                ctl["siirrot"][s] = SIIRROT[min(SLOT[state[v["id"]][0]] for v in alive)]
                ctl["jono"].append(s)
        ctl["migroitu"] = True
        save_control(ctl)
        return stromo_views(vs, rows, runs, state, ctl)
    return out


def queue_order(views, ctl):
    members = [s for s, w in views.items() if w["kategoria"] in ("jonossa", "ajossa")]
    order = [s for s in ctl["jono"] if s in members]
    return order + sorted(s for s in members if s not in order)


def allowed_jobs(vs, rows, runs, state):
    ctl = control()
    views = stromo_views(vs, rows, runs, state, ctl)
    order = queue_order(views, ctl)
    todo = [
        (k, v, cmd) for k, v, cmd in jobs(vs, rows, runs, state)
        if v["stromo"] in order and SLOT[STAGE_OF_JOB[k]] <= SIIRROT.index(ctl["siirrot"][v["stromo"]])
    ]
    return sorted(todo, key=lambda j: order.index(j[1]["stromo"]))


# ---------- tapahtumat (liven Loki ja Telegram palvelimen kautta) ----------


def _events_locked(stream_lock):
    fcntl.flock(stream_lock, fcntl.LOCK_EX)


def read_events():
    if not TAPAHTUMAT.exists():
        return []
    return [json.loads(line) for line in TAPAHTUMAT.read_text().splitlines() if line.strip()]


def _append_event(laji, stromo, teksti):
    n = len(read_events()) + 1
    row = {"id": n, "aika": datetime.now(timezone.utc).isoformat(timespec="seconds"), "laji": laji,
           "stromo": stromo, "teksti": teksti}
    with TAPAHTUMAT.open("a") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def add_event(laji, stromo, teksti):
    TILA.mkdir(parents=True, exist_ok=True)
    with TAPAHTUMALUKKO.open("a") as lock:
        _events_locked(lock)
        return _append_event(laji, stromo, teksti)


def view_key(w):
    k = w["kategoria"]
    if k == "odottaa":
        return f"odottaa:{w['seuraava']}"
    if k == "prospekti" and w.get("palikka"):
        return "prospekti:palikka"
    return k


def sync_events(vs, rows, runs, state):
    """Vertaa stromojen tilaa edelliseen ja kirjaa muutokset tapahtumiksi (yksi kirjoittaja kerrallaan)."""
    ctl = control()
    views = stromo_views(vs, rows, runs, state, ctl)
    changed = False
    for s, w in views.items():  # puuttuva palikka palauttaa prospekteihin
        if w["kategoria"] == "prospekti" and w.get("palikka") and s in ctl["siirrot"]:
            del ctl["siirrot"][s]
            changed = True
    if changed:
        save_control(ctl)
    TILA.mkdir(parents=True, exist_ok=True)
    with TAPAHTUMALUKKO.open("a") as lock:
        _events_locked(lock)
        saved = read_json(STROMOTILA, None)
        previous = None if saved is None else saved.get("tila", saved)
        notified = set(() if saved is None else saved.get("ilmoitetut", []))
        current = {s: view_key(w) for s, w in views.items()}
        sl = seula()
        then = (saved or {}).get("seula") or {"nimi": "normaali", **SEULAT["normaali"]}
        if previous is None:
            notified = {f"{s}|{k}" for s, k in current.items()}
        elif any(then.get(k) != sl.get(k) for k in (*VERTAILTAVAT, "kausi_alfa", "kausi_min_plus")):
            # Seulan muutos: yksi yhteenveto, ei stromokohtaista piippausta.
            moved = [s for s, k in current.items() if previous.get(s) not in (None, k)]
            up = sum(1 for s in moved if current[s].startswith("odottaa:"))
            down = sum(1 for s in moved if current[s] == "hautausmaa")
            notified |= {f"{s}|{k}" for s, k in current.items()}
            _append_event("seula", None, f"Seula {sl['nimi']} arvioi tulokset uudelleen: {up} stromoa odottaa "
                                         f"siirtoa, {down} hautausmaalle, {len(moved) - up - down} muuta muutosta.")
        else:
            fresh = [s for s, k in current.items() if s not in previous and k.startswith("prospekti")]
            if fresh:
                _append_event("prospektit", None, f"{len(fresh)} uutta prospektia: " + ", ".join(fresh))
            for s, k in current.items():
                old, w = previous.get(s), views[s]
                if old is None or old == k or f"{s}|{k}" in notified:
                    continue
                notified.add(f"{s}|{k}")
                if k.startswith("odottaa:"):
                    _append_event("lapaisi", s, f"{s} läpäisi vaiheen {w['lapi']} → odottaa siirtoa: {w['seuraava']}")
                elif k == "hautausmaa":
                    _append_event("hautausmaa", s, f"{s} hautausmaalle ({w['vaihe']}): {w['syy']}")
                elif k == "valmis":
                    _append_event("valmis", s, f"{s} läpäisi Playoffit → Näytösottelu")
                elif k == "prospekti:palikka":
                    _append_event("palikka", s, f"{s} odottaa palikkaa {w['palikka']} (STROMO4); palasi prospekteihin")
        atomic_write(STROMOTILA, {"tila": current, "ilmoitetut": sorted(notified),
                                  "seula": {k: sl[k] for k in (*VERTAILTAVAT, "kausi_alfa", "kausi_min_plus", "nimi")}})
    return views


def queue_done_event(vs, rows, runs, started):
    state = evaluate(vs, rows, runs)
    sync_events(vs, rows, runs, state)
    since = [e for e in read_events() if e["aika"] >= started]
    passed = sum(e["laji"] == "lapaisi" for e in since)
    dead = sum(e["laji"] == "hautausmaa" for e in since)
    add_event("jono_valmis", None, f"Ajojono valmis: {passed} odottaa siirtoa, {dead} hautausmaalle.")


# ---------- komennot ----------


def fetch_updates():
    """Hae prospektit: builder mainista aina; STROMO4-tutkimuskansio vain, kun LIIGA ei aja."""
    out = {"ok": True}
    b = str(BUILDER)
    try:
        if git_out("rev-parse", "--abbrev-ref", "HEAD", cwd=b) != "main" or git_out(
                "status", "--porcelain", "--untracked-files=no", cwd=b):
            out["builder_virhe"] = "Builder ei ole puhtaassa main-haarassa; haku ohitettiin."
        else:
            git_out("fetch", "-q", "origin", "main", cwd=b)
            git_out("merge", "--ff-only", "-q", "origin/main", cwd=b)
    except (OSError, subprocess.CalledProcessError) as error:
        out["builder_virhe"] = f"Builderin haku epäonnistui: {getattr(error, 'stderr', '') or error}"[:500]
    TILA.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            out["stromo4"] = "päivitetään ajon jälkeen"
        else:
            try:
                if git_out("status", "--porcelain", "--untracked-files=no"):
                    out["stromo4_virhe"] = "Tutkimuskansiossa on muutoksia; STROMO4:ää ei päivitetty."
                else:
                    git_out("fetch", "-q", "origin", "main")
                    before = git_out("rev-parse", "HEAD")
                    target = git_out("rev-parse", "origin/main")
                    if before != target:
                        git_out("checkout", "-q", "--detach", target)
                    if before != target or not Path(".venv").exists():
                        env = {**os.environ}
                        env.setdefault("UV_PYTHON_INSTALL_DIR", str(Path.home() / ".local/share/uv/python"))
                        subprocess.run(["uv", "sync", "--group", "research", "-q"], env=env, check=True,
                                       capture_output=True, text=True)
                    out["stromo4"] = "päivitetty" if before != target else "ajan tasalla"
            except (OSError, subprocess.CalledProcessError) as error:
                out["stromo4_virhe"] = f"STROMO4-päivitys epäonnistui: {getattr(error, 'stderr', '') or error}"[:500]
    stromo4_revision(refresh=True)
    ctl = control()
    ctl["haettu"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_control(ctl)
    out["ok"] = not any(k.endswith("_virhe") for k in out)
    out["versiot"] = {"stromo4": stromo4_revision(), "haettu": ctl["haettu"]}
    return out


def stromo_command(command, target, confirm=None):
    if not re.fullmatch(STROMO_RE, target or ""):
        raise ValueError("Virheellinen stromon nimi")
    vs, rows, runs = variants(), read_ledger(), index_runs()
    state = evaluate(vs, rows, runs)
    ctl = control()
    views = stromo_views(vs, rows, runs, state, ctl)
    ctl = control()
    if target not in views:
        raise ValueError("Tuntematon stromo")
    w = views[target]
    if command == "siirra":
        if w["kategoria"] == "prospekti" and not w.get("palikka"):
            ctl["siirrot"][target] = "Try out"
        elif w["kategoria"] == "odottaa" and w["seuraava"] and w["seuraava"] != "Playoffit":
            ctl["siirrot"][target] = w["seuraava"]
        elif w["kategoria"] == "odottaa" and w["seuraava"] == "Playoffit":
            raise ValueError("Playoffit avataan omalla vahvistuksella")
        else:
            raise ValueError(f"Stromoa ei voi siirtää (tila: {w['kategoria']})")
        ctl["jono"] = [s for s in ctl["jono"] if s != target] + [target]
    elif command == "palauta":
        if w["kategoria"] != "jonossa":
            raise ValueError("Vain jonossa odottavan (ei ajossa olevan) stromon voi palauttaa")
        stage = SIIRROT.index(ctl["siirrot"][target])
        if stage == 0 and not any(r["stromo"] == target for r in rows):
            del ctl["siirrot"][target]
        elif stage > 0:
            ctl["siirrot"][target] = SIIRROT[stage - 1]
        else:
            raise ValueError("Try outin aloittanutta stromoa ei voi palauttaa prospekteihin")
        ctl["jono"] = [s for s in ctl["jono"] if s != target]
    elif command in ("ylos", "alas"):
        order = queue_order(views, ctl)
        if target not in order:
            raise ValueError("Stromo ei ole ajojonossa")
        i = order.index(target)
        j = i - 1 if command == "ylos" else i + 1
        if 0 <= j < len(order):
            order[i], order[j] = order[j], order[i]
        ctl["jono"] = order
    elif command == "playoffit":
        if confirm != target:
            raise ValueError("Vahvistus ei vastaa stromon nimeä")
        if w["kategoria"] != "odottaa" or w["seuraava"] != "Playoffit":
            raise ValueError("Stromo ei odota Playoffeja")
        ctl["siirrot"][target] = "Playoffit"
        ctl["jono"] = [s for s in ctl["jono"] if s != target] + [target]
        add_event("playoffit", target, f"Omistaja avasi koskemattoman jakson stromolle {target} (Playoffit).")
    save_control(ctl)
    return {"ok": True, "siirrot": ctl["siirrot"], "jono": ctl["jono"]}


def seula_command(target, key=None, value=None):
    """seula <iso_kampa|normaali|tiukka|oma> tai seula-arvo <avain> <arvo> (asettaa Oman)."""
    c = read_json(OHJAUS, {})
    current = seula()
    if key is None:
        if target not in (*SEULAT, "oma"):
            raise ValueError("Seula on iso_kampa, normaali, tiukka tai oma")
        new = {"nimi": target, **({k: current[k] for k in SEULA_RAJAT} if target == "oma" else {})}
    else:
        if key not in SEULA_RAJAT:
            raise ValueError("Tuntematon seulan säädin")
        rule = SEULA_RAJAT[key]
        if rule[0] is bool:
            if value not in ("paalla", "pois"):
                raise ValueError(f"{key}: paalla tai pois")
            parsed = value == "paalla"
        elif rule[0] in (int, float):
            try:
                parsed = rule[0](value)
            except (TypeError, ValueError):
                raise ValueError(f"{key}: luku {rule[1]}–{rule[2]}") from None
            if not (rule[1] <= parsed <= rule[2]) or (isinstance(parsed, float) and not math.isfinite(parsed)):
                raise ValueError(f"{key}: luku {rule[1]}–{rule[2]}")
        else:
            value = {"enemmisto": "enemmistö"}.get(value, value)
            if value not in rule:
                raise ValueError(f"{key}: {' / '.join(rule)}")
            parsed = value
        new = {"nimi": "oma", **{k: current[k] for k in SEULA_RAJAT}, key: parsed}
    c["seula"] = new
    history = list(c.get("seulahistoria", []))[-49:]
    history.append({"aika": datetime.now(timezone.utc).isoformat(timespec="seconds"), **new})
    c["seulahistoria"] = history
    atomic_write(OHJAUS, c)
    sl = seula()
    add_event("seula", None, f"Seula: {sl['nimi']} (raja {sl['tl_k']:g} keskivirhettä, min {sl['tl_min_rypaat']} "
                             f"rypästä, naapuri {sl['naapuri']}, aikainen karsinta "
                             f"{'päällä' if sl['karsinta'] else 'pois'})")
    return {"ok": True, "seula": sl}


def state_json2(vs, rows, runs, state):
    views = sync_events(vs, rows, runs, state)
    ctl = control()
    order = queue_order(views, ctl)
    running = liiga_running()
    current = read_json(RUNNING, None) if running else None
    if current:
        config = read_json(RUNS / current["ajo"] / "config.json", {}) if current.get("ajo") else {}
        pct, eta = config.get("progress_percent"), config.get("eta_seconds")
        current["edistyminen"] = None if pct is None else max(0.0, min(1.0, pct / 100))
        current["arvio_valmis"] = (
            datetime.fromtimestamp(datetime.now(timezone.utc).timestamp() + eta, timezone.utc).isoformat(timespec="seconds")
            if isinstance(eta, (int, float)) else None
        )
    try:
        builder = git_out("rev-parse", "--short=12", "HEAD", cwd=str(BUILDER))
    except (OSError, subprocess.CalledProcessError):
        builder = None
    by_cat = lambda c: [w for w in views.values() if w["kategoria"] == c]  # noqa: E731
    sl = seula()
    table_rows = results_table(vs, rows, sl)
    shame = sorted((r for r in table_rows if r["z"] is not None), key=lambda r: r["z"])[:5]
    queue = [views[s] for s in order]
    total = sum(w.get("arvio_s") or 0 for w in queue)
    hof = [{"id": v["id"], "stromo": v["stromo"], "tekija": v["stromo"].split("/", 1)[0], "params": v["params"],
            "suhde": ratio, "reuna": t["reuna"], "kynnys": t["kynnys"], "rypaat": t["rypaat"],
            "vaihe": state[v["id"]][0], "tila": state[v["id"]][1]}
           for ratio, v, t in hof_entries(vs, rows)[:5]]
    return {
        "versio": 2,
        "aika": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versiot": {"builder": builder, "stromo4": stromo4_revision(), "haettu": ctl["haettu"]},
        "pelikone": {"liiga_kaynnissa": running, "teho": ctl["teho"], "prosessit": TEHO},
        "kaynnissa": current,
        "prospektit": sorted(by_cat("prospekti"), key=lambda w: w["stromo"]),
        "ajojono": queue,
        "jono_arvio_s": total,
        "odottavat": sorted(by_cat("odottaa"), key=lambda w: (-SLOT[w["seuraava"]] if w["seuraava"] else 0, w["stromo"])),
        "valmiit": by_cat("valmis"),
        "hautausmaa": sorted(by_cat("hautausmaa"), key=lambda w: w.get("aika") or "", reverse=True),
        "historia": sorted(by_cat("historia"), key=lambda w: w["stromo"]),
        "hall_of_fame": hof,
        "hall_of_shame": shame,
        "seula": {**sl, "esiasetukset": SEULAT, "rajat": {k: list(v[1:]) if v[0] in (int, float) else
                  (["paalla", "pois"] if v[0] is bool else list(v)) for k, v in SEULA_RAJAT.items()},
                  "sattuma": chance_meter(vs, rows, sl)},
        "tulokset": table_rows,
        "tapahtumat": read_events()[-50:],
    }


def main():
    parser = argparse.ArgumentParser(description="LIIGA")
    parser.add_argument("komento", choices=["tila", "aja", "raportti", "vie", "paketti", "yo", "kaynnista",
                                            "pysayta", "jono-ensin", "jono-ohita", "jono-palauta",
                                            "tila2", "hae", "siirra", "palauta", "ylos", "alas", "teho",
                                            "playoffit", "seula", "seula-arvo"])
    parser.add_argument("kohde", nargs="?",
                        help="paketti: ajokansio/variantti/stromo; jono-*: variantti; siirra|palauta|ylos|alas|"
                             "playoffit: stromo (esim. gpt/utc_paivanvaihde); teho: kevyt|taysi")
    parser.add_argument("--vahvista", help="playoffit: stromon nimi uudelleen")
    parser.add_argument("arvo", nargs="?", help="seula-arvo: uusi arvo")
    parser.add_argument("--kuiva", action="store_true")
    parser.add_argument("--json", action="store_true", help="tila: koneluettava (liiga.stromo.uk)")
    args = parser.parse_args()
    if not Path("research/replay.py").exists():
        sys.exit("Aja STROMO4-tutkimuskansiossa (~/stromo4-tutkimus).")
    machine = (args.json or args.komento in ("kaynnista", "pysayta", "tila2", "hae", "siirra", "palauta", "ylos",
                                             "alas", "teho", "playoffit", "seula", "seula-arvo")
               or args.komento.startswith("jono-"))
    if machine:
        try:
            if args.komento == "kaynnista":
                out = start_background()
            elif args.komento == "pysayta":
                out = stop_background()
            elif args.komento.startswith("jono-"):
                out = queue_command(args.komento, args.kohde, variants())
            elif args.komento == "hae":
                out = fetch_updates()
            elif args.komento in ("siirra", "palauta", "ylos", "alas", "playoffit"):
                out = stromo_command(args.komento, args.kohde, args.vahvista)
            elif args.komento == "seula":
                out = seula_command(args.kohde)
            elif args.komento == "seula-arvo":
                out = seula_command("oma", args.kohde, args.arvo)
            elif args.komento == "teho":
                if args.kohde not in TEHO:
                    raise ValueError("Teho on kevyt tai taysi")
                ctl = control()
                ctl["teho"] = args.kohde
                save_control(ctl)
                out = {"ok": True, "teho": args.kohde, "prosessit": TEHO[args.kohde]}
            elif args.komento == "tila2":
                vs, rows, runs = variants(), read_ledger(), index_runs()
                out = state_json2(vs, rows, runs, evaluate(vs, rows, runs))
            else:
                vs, rows, runs = variants(), read_ledger(), index_runs()
                out = state_json(vs, rows, runs, evaluate(vs, rows, runs))
            print(json.dumps(out, ensure_ascii=False, allow_nan=False))
        except Exception as error:  # noqa: BLE001 – koneluettava virhe palvelimelle
            print(json.dumps({"virhe": f"{type(error).__name__}: {error}"}, ensure_ascii=False))
            sys.exit(1)
        return
    if args.komento in ("aja", "yo"):
        run_jobs(args.kuiva)
        if args.komento == "aja" or args.kuiva:
            return
    vs, rows, runs = variants(), read_ledger(), index_runs()
    state = evaluate(vs, rows, runs)
    if args.komento == "tila":
        print(table(vs, rows, state))
    elif args.komento == "raportti":
        print(report(vs, rows, state))
    elif args.komento == "paketti":
        if not args.kohde:
            sys.exit("Anna ajokansio, variantti tai stromon nimi, esim. paketti uupumus")
        package(args.kohde, vs, rows)
    else:  # vie, yo
        export(report(vs, rows, state), hall_of_fame(vs, rows, state))


if __name__ == "__main__":
    main()
