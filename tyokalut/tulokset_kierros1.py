#!/usr/bin/env python3
"""Kierroksen 1 kehitysjakson tulostaulukko OHJE.md:n läpäisykriteereillä.

Käyttö STROMO4-tutkimuskansiossa (pelikone):
    python3 ~/stromo-builder/tyokalut/tulokset_kierros1.py > ~/k1_tulokset.md

Lukee jokaisen data/research/runs/k1-*/config.json- ja events.jsonl-tiedoston.
Vain standardikirjasto. Ei muuta mitään.
"""

import json
import math
import sys
from datetime import date
from pathlib import Path

RUNS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/research/runs")
MIN_CLUSTERS = 100
EDGE_FACTOR = 130
MAX_PER_DAY = 20
CLUSTER_MS = 60 * 60_000


def clusters(timestamps):
    ordered = sorted(timestamps)
    return (1 + sum(b - a >= CLUSTER_MS for a, b in zip(ordered, ordered[1:]))) if ordered else 0


def load(path):
    config = json.loads((path / "config.json").read_text())
    if config.get("status") != "complete":
        return {"id": path.name, "status": config.get("status", "?"), "error": config.get("error")}
    signals = []
    with (path / "events.jsonl").open() as stream:
        for line in stream:
            event = json.loads(line)
            if event.get("sample") != "random":
                signals.append(event)
    primary = config["primary_summary"]
    win = primary["signal"]["win_pct"]
    base = primary["random"]["win_pct"]
    directional = [e for e in signals if e.get("direction") in ("up", "down")]
    days = (date.fromisoformat(config["end"]) - date.fromisoformat(config["start"])).days + 1
    n_clusters = clusters([e["timestamp_ms"] for e in directional])
    edge = float(win) - float(base) if win is not None and base is not None else None
    threshold = EDGE_FACTOR / math.sqrt(n_clusters) if n_clusters else None
    group = primary["signal"]["directional"]
    return {
        "id": path.name,
        "status": "complete",
        "parameters": {
            k: v
            for k, v in config["parameters"].items()
            if k not in ("exchange", "instrument", "cooldown_seconds")
        },
        "alerts": len(signals),
        "directionless": len(signals) - len(directional),
        "per_day": len(signals) / days,
        "clusters": n_clusters,
        "resolved": group.get("target", 0) + group.get("stop", 0),
        "win": float(win) if win is not None else None,
        "base": float(base) if base is not None else None,
        "edge": edge,
        "threshold": threshold,
    }


def fmt(value, digits=1):
    return "—" if value is None else f"{value:.{digits}f}".replace(".", ",")


def main():
    rows = [load(p) for p in sorted(RUNS.glob("k1-*")) if (p / "config.json").exists()]
    groups = {}
    for row in rows:
        stem = row["id"].rsplit("-", 1)[0]  # k1-tekijä-stromo
        groups.setdefault(stem, []).append(row)
    print("# Kierros 1 – kehitysjakso BTC-USDT 2025-11-01 – 2026-07-31\n")
    print(
        f"Läpäisy: rypäät ≥ {MIN_CLUSTERS}, reuna ≥ {EDGE_FACTOR}/√rypäät pp, "
        f"≤ {MAX_PER_DAY} hälytystä/vrk, naapurivariantti samaan suuntaan (reuna > 0).\n"
    )
    print(
        "| Ajo | Parametrit | Hälytykset | /vrk | Suunnattomat | Rypäät | Ratkenneet "
        "| Osuma % | Verrokki % | Reuna pp | Kynnys pp | Läpäisy |"
    )
    print("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for stem, variants in groups.items():
        complete = [v for v in variants if v["status"] == "complete"]
        for row in variants:
            if row["status"] != "complete":
                print(f"| {row['id']} | | | | | | | | | | | {row['status']}: {row.get('error') or ''} |")
                continue
            reasons = []
            if row["clusters"] < MIN_CLUSTERS:
                reasons.append("rypäät")
            if row["edge"] is None or row["threshold"] is None or row["edge"] < row["threshold"]:
                reasons.append("reuna")
            if row["per_day"] > MAX_PER_DAY:
                reasons.append("tiheys")
            neighbours = [v for v in complete if v is not row]
            if not neighbours or not all(v["edge"] is not None and v["edge"] > 0 for v in neighbours):
                reasons.append("naapuri")
            verdict = "✅ läpäisee" if not reasons else "❌ " + ", ".join(reasons)
            params = ", ".join(f"{k}={v}" for k, v in row["parameters"].items())
            print(
                f"| {row['id']} | {params} | {row['alerts']} | {fmt(row['per_day'])} "
                f"| {row['directionless']} | {row['clusters']} | {row['resolved']} "
                f"| {fmt(row['win'])} | {fmt(row['base'])} | {fmt(row['edge'], 2)} "
                f"| {fmt(row['threshold'], 2)} | {verdict} |"
            )
    missing = 17 - len(rows)
    if missing > 0:
        print(f"\nAjoja puuttuu vielä {missing}/17.")


if __name__ == "__main__":
    main()
