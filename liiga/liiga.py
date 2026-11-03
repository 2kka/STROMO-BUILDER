#!/usr/bin/env python3
"""LIIGA – stromojen karsinta: Try out → Treenileiri → Dopingtesti → Kuntopuntari →
Kausi → Playoffit → Näytösottelu. Tilastot = kaikkien tulosten kirjanpito.

Ajetaan pelikoneella STROMO4-tutkimuskansiossa (~/stromo4-tutkimus):

    python3 ~/stromo-builder/liiga/liiga.py tila        # missä vaiheessa kukin variantti on
    python3 ~/stromo-builder/liiga/liiga.py aja         # aja seuraavat vaiheet jonossa
    python3 ~/stromo-builder/liiga/liiga.py aja --kuiva # näytä komennot ajamatta
    python3 ~/stromo-builder/liiga/liiga.py raportti    # aamuraportti
    python3 ~/stromo-builder/liiga/liiga.py vie         # tilastot + raportti haaraan tulokset/…

Vain standardikirjasto. LIIGA ei koskaan avaa koskematonta jaksoa (Playoffit):
se tulostaa omistajalle valmiin komennon. Tulokset luetaan ajojen config.json-
tiedostoista, joten valmiita ajoja (myös kierroksen 1 k1-ajot) ei ajeta uudelleen.
"""

import argparse
import ast
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


def variants():
    result = []
    for path in sorted((BUILDER / "stromot").glob("*/*.py")):
        if path.name.startswith("_"):
            continue
        source = path.read_text(encoding="utf-8")
        sha = hashlib.sha256(source.encode()).hexdigest()
        choices = enum_choices(source)
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
                }
            )
    return result


# ---------- ajojen luku ----------


def index_runs():
    runs = {}
    for config_path in RUNS.glob("*/config.json"):
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


def find_run(runs, v, start, end):
    for params, path, config in runs.get((v["sha256"], SAANNOT["pari"], start, end), []):
        if all(params.get(k) == val for k, val in v["params"].items()):
            return path, config
    return None, None


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


def evaluate(vs, rows, runs):
    """Päivittää tilastot valmiiden ajojen perusteella ja palauttaa tilan per variantti."""
    t = SAANNOT["treenileiri"]
    state = {}
    # Try out
    for v in vs:
        f = tryout_file(v)
        if f.exists() and not last(rows, "tryout", v):
            result = json.loads(f.read_text())
            record(rows, {**base_row(v, "tryout"), "lapaisy": result.get("ok", False), "tulos": result})
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
                },
            )
    # Naapurisääntö ja ylennys (enintään max_jatkoon per arviointi, suurin reuna/kynnys)
    candidates = []
    for v in vs:
        row = last(rows, "treenileiri", v)
        if not row or row["syyt"] or last(rows, "ylennys", v):
            continue
        neighbours = [
            last(rows, "treenileiri", n) for n in vs if n["stromo"] == v["stromo"] and n is not v
        ]
        if neighbours and all(
            n and n["tulos"]["reuna"] is not None and n["tulos"]["reuna"] > 0 for n in neighbours
        ):
            candidates.append((row["tulos"]["reuna"] / row["tulos"]["kynnys"], v))
        elif neighbours and all(n for n in neighbours):
            record(rows, {**base_row(v, "ylennys"), "lapaisy": False, "syy": "naapuri"})
    candidates.sort(key=lambda c: -c[0])
    for rank, (_, v) in enumerate(candidates):
        ok = rank < t["max_jatkoon"]
        record(rows, {**base_row(v, "ylennys"), "lapaisy": ok, "syy": None if ok else "kiintiö"})
    # Dopingtesti ja Kuntopuntari: ajokansion tappotestit.json (research.tappotestit, 3.1b)
    for v in vs:
        up = last(rows, "ylennys", v)
        tr = last(rows, "treenileiri", v)
        if up and up["lapaisy"] and not last(rows, "dopingtesti", v):
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
                },
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
        state[v["id"]] = stage_of(rows, v)
    return state


def stage_of(rows, v):
    """(vaihe, tila) – tila: 'odottaa', 'läpi', 'karsittu: syy'."""
    to = last(rows, "tryout", v)
    if not to:
        return "Try out", "odottaa"
    if not to["lapaisy"]:
        return "Try out", "karsittu"
    tr = last(rows, "treenileiri", v)
    if not tr:
        return "Treenileiri", "odottaa"
    if tr["syyt"]:
        return "Treenileiri", "karsittu: " + ", ".join(tr["syyt"])
    up = last(rows, "ylennys", v)
    if not up:
        return "Treenileiri", "odottaa naapuria"
    if not up["lapaisy"]:
        return "Treenileiri", "karsittu: " + up["syy"]
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
    if not ka["lapaisy"]:
        return "Kausi", "karsittu"
    po = last(rows, "playoffit", v)
    if not po:
        return "Playoffit", "odottaa omistajaa"
    if not po["lapaisy"]:
        return "Playoffit", "karsittu"
    return "Näytösottelu", "valmis"


# ---------- ajaminen ----------


def param_args(v):
    return [a for k, val in v["params"].items() for a in ("--param", f"{k}={val}")]


def replay_cmd(v, start, end, run_id):
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
            out.append(("tryout", v, UV + [
                "research.check_stromo", str(v["file"]), "--json",
                "--day", SAANNOT["tryout"]["paiva"], "--pair", SAANNOT["pari"],
            ] + param_args(v)))
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
    order = {"tryout": 0, "treenileiri": 1, "dopingtesti": 2, "kausi": 3}
    return sorted(out, key=lambda j: order[j[0]])


def run_jobs(dry):
    while True:
        vs, rows, runs = variants(), read_ledger(), index_runs()
        state = evaluate(vs, rows, runs)
        todo = jobs(vs, rows, runs, state)
        if not todo:
            print("Jono tyhjä.")
            return
        kind, v, cmd = todo[0]
        print(f"{datetime.now():%H.%M} {kind}: {v['id']}", flush=True)
        if dry:
            for kind, v, cmd in todo:
                print(f"  {kind:12} {' '.join(cmd)}")
            return
        if kind == "tryout":
            proc = subprocess.run(cmd, capture_output=True, text=True)
            try:
                result = json.loads(proc.stdout)
            except ValueError:
                result = {"ok": False, "virhe": (proc.stderr or proc.stdout)[-2000:]}
            result.setdefault("ok", proc.returncode == 0)
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
                return


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
        f"Variantteja {len(vs)}, Treenileirillä mitattu {len(tested)}. "
        f"Sattumalta Treenileirin läpäiseviä odotetaan noin {fmt(len(tested) * alpha)} "
        f"(kynnys {t['kynnys_kerroin']}/√rypäät ≈ {fmt(alpha * 100)} % per variantti).",
        "",
        "| Vaihe | Saapui | Läpi |",
        "|---|---:|---:|",
    ]
    out += [f"| {s} | {reached[s]} | {passed[s]} |" for s in VAIHEET[:-1]]
    out += ["", table(vs, rows, state)]
    ready = [v["id"] for v in vs if state[v["id"]] == ("Playoffit", "odottaa omistajaa")]
    if ready:
        out += ["", "**Valmiina Playoffeihin (omistaja ajaa, kerran):**", ""]
        p = SAANNOT["playoffit"]
        for v in vs:
            if v["id"] in ready:
                cmd = replay_cmd(v, p["alku"], p["loppu"], f"liiga-po-{v['id']}")
                out.append("    " + " ".join(cmd) + ' --open-holdout --reason "LIIGA Playoffit"')
    return "\n".join(out) + "\n"


def export(text):
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
    subprocess.run(git + ["add", "tilastot"], check=True)
    subprocess.run(git + ["-c", "user.name=LIIGA pelikone", "-c", "user.email=liiga@localhost",
                          "commit", "-q", "-m", f"LIIGA-tulokset {stamp}"], check=True)
    subprocess.run(git + ["push", "-q", "origin", branch], check=True)
    subprocess.run(git + ["checkout", "-q", "main"], check=False)
    print(f"Viety haaraan {branch}. Avaa PR GitHubissa tai pyydä Claudea.")


def main():
    parser = argparse.ArgumentParser(description="LIIGA")
    parser.add_argument("komento", choices=["tila", "aja", "raportti", "vie"])
    parser.add_argument("--kuiva", action="store_true")
    args = parser.parse_args()
    if not Path("research/replay.py").exists():
        sys.exit("Aja STROMO4-tutkimuskansiossa (~/stromo4-tutkimus).")
    if args.komento == "aja":
        run_jobs(args.kuiva)
        return
    vs, rows, runs = variants(), read_ledger(), index_runs()
    state = evaluate(vs, rows, runs)
    if args.komento == "tila":
        print(table(vs, rows, state))
    elif args.komento == "raportti":
        print(report(vs, rows, state))
    else:
        export(report(vs, rows, state))


if __name__ == "__main__":
    main()
