#!/usr/bin/env python3
import argparse
import json
import os
import glob
from typing import Any, Dict, List, Tuple


def safe_get(d: Dict[str, Any], *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def parse_observation_file(path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    rows: List[Dict[str, Any]] = []
    inst_rows: List[Dict[str, Any]] = []
    anomalies: List[Dict[str, Any]] = []
    try:
        with open(path, "r") as f:
            payload = json.load(f)
    except Exception as e:
        anomalies.append({"type": "file_read_error", "file": path, "error": str(e)})
        return rows, inst_rows, anomalies

    observations = payload.get("observations", [])
    for obs in observations:
        ts = obs.get("timestamp") or safe_get(obs, "data", "timestamp")
        cycle = obs.get("cycle")
        data = obs.get("data", {})
        row = {
            "file": os.path.basename(path),
            "cycle": cycle,
            "timestamp": ts if isinstance(ts, str) else str(ts),
            "total_agents": data.get("total_agents"),
            "total_steps": data.get("total_steps"),
            "avg_happiness": data.get("avg_happiness"),
            "avg_energy": data.get("avg_energy"),
            "total_wealth": data.get("total_wealth"),
            "successful_instances": data.get("successful_instances"),
        }
        rows.append(row)

        if row["total_agents"] is not None and row["total_agents"] <= 0:
            anomalies.append({"type": "non_positive_agents", "file": row["file"], "cycle": cycle, "timestamp": row["timestamp"], "value": row["total_agents"]})
        if row["total_wealth"] is not None and row["total_wealth"] < 0:
            anomalies.append({"type": "negative_wealth", "file": row["file"], "cycle": cycle, "timestamp": row["timestamp"], "value": row["total_wealth"]})

        for inst in data.get("instance_results", []) or []:
            step_results = inst.get("step_results", [])
            start = step_results[0] if step_results else {}
            end = step_results[-1] if step_results else {}
            def dval(k):
                s = start.get(k); e = end.get(k)
                return (s, e, (e - s) if (s is not None and e is not None) else None)
            sh, eh, dh = dval("avg_happiness")
            se, ee, de = dval("avg_energy")
            sw, ew, dw = dval("total_wealth")
            inst_rows.append({
                "file": row["file"],
                "timestamp": row["timestamp"],
                "cycle": cycle,
                "instance_id": inst.get("instance_id"),
                "steps": len(step_results),
                "start_happiness": sh, "end_happiness": eh, "delta_happiness": dh,
                "start_energy": se, "end_energy": ee, "delta_energy": de,
                "start_wealth": sw, "end_wealth": ew, "delta_wealth": dw,
            })
            if dh is not None and abs(dh) > 0.2:
                anomalies.append({"type": "happiness_jump", "file": row["file"], "instance_id": inst.get("instance_id"), "delta": dh, "timestamp": row["timestamp"]})
            if de is not None and abs(de) > 0.2:
                anomalies.append({"type": "energy_jump", "file": row["file"], "instance_id": inst.get("instance_id"), "delta": de, "timestamp": row["timestamp"]})
            if dw is not None and dw < 0:
                anomalies.append({"type": "wealth_drop", "file": row["file"], "instance_id": inst.get("instance_id"), "delta": dw, "timestamp": row["timestamp"]})

    return rows, inst_rows, anomalies


def write_csv(path: str, rows: List[Dict[str, Any]], header: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            line = []
            for h in header:
                v = r.get(h)
                if isinstance(v, str):
                    v = v.replace("\n", " ").replace("\r", " ").replace(",", ";")
                line.append("" if v is None else str(v))
            f.write(",".join(line) + "\n")


def generate_html_report(path: str, rollup_rows: List[Dict[str, Any]], anomalies: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Build arrays
    rows_sorted = sorted(rollup_rows, key=lambda r: (r.get("timestamp") or "", r.get("file") or ""))
    labels = [r.get("timestamp") for r in rows_sorted]
    happiness = [r.get("avg_happiness") for r in rows_sorted]
    energy = [r.get("avg_energy") for r in rows_sorted]
    wealth = [r.get("total_wealth") for r in rows_sorted]

    # Anomalies HTML
    parts_list = []
    for a in anomalies[:200]:
        details = {k: v for k, v in a.items() if k not in ("type", "file", "timestamp")}
        parts_list.append('<div class="anomaly"><b>{}</b> — file: {}, ts: {}, details: {}</div>'.format(
            a.get("type"), a.get("file"), a.get("timestamp", "-"), json.dumps(details)))
    anomalies_html = "".join(parts_list)
    if len(anomalies) > 200:
        anomalies_html += '<p class="small">(Showing first 200 anomalies)</p>'

    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Live Observations Report</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }
    h1 { margin-bottom: 4px; }
    .small { color: #666; margin-top: 0; }
    .grid { display: grid; grid-template-columns: 1fr; gap: 24px; }
    .panel { padding: 16px; border: 1px solid #ddd; border-radius: 8px; }
    .anomaly { background: #fff8e1; padding: 8px; border-radius: 6px; margin: 6px 0; border: 1px solid #ffe082; }
  </style>
  </head>
  <body>
    <h1>Society Live Observations</h1>
    <p class="small">Auto-generated roll-up of happiness, energy, and wealth over time.</p>
    <div class="grid">
      <div class="panel">
        <h3>Average Happiness</h3>
        <canvas id="chartH"></canvas>
      </div>
      <div class="panel">
        <h3>Average Energy</h3>
        <canvas id="chartE"></canvas>
      </div>
      <div class="panel">
        <h3>Total Wealth</h3>
        <canvas id="chartW"></canvas>
      </div>
      <div class="panel">
        <h3>Anomalies (__COUNT__):</h3>
        __ANOMALIES__
      </div>
    </div>
    <script>
      const labels = __LABELS__;
      const dataH = __H__;
      const dataE = __E__;
      const dataW = __W__;
      const commonOpts = {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { maxRotation: 45, minRotation: 45 } } }
      };
      new Chart(document.getElementById('chartH').getContext('2d'), {
        type: 'line', data: { labels, datasets: [{ label: 'Happiness', data: dataH, borderColor: '#42a5f5', fill: false }] }, options: commonOpts });
      new Chart(document.getElementById('chartE').getContext('2d'), {
        type: 'line', data: { labels, datasets: [{ label: 'Energy', data: dataE, borderColor: '#66bb6a', fill: false }] }, options: commonOpts });
      new Chart(document.getElementById('chartW').getContext('2d'), {
        type: 'line', data: { labels, datasets: [{ label: 'Wealth', data: dataW, borderColor: '#ffa726', fill: false }] }, options: commonOpts });
    </script>
  </body>
</html>
"""

    html = (html
            .replace("__COUNT__", str(len(anomalies)))
            .replace("__ANOMALIES__", anomalies_html)
            .replace("__LABELS__", json.dumps(labels))
            .replace("__H__", json.dumps(happiness))
            .replace("__E__", json.dumps(energy))
            .replace("__W__", json.dumps(wealth))
            )

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(description="Aggregate live observations and generate report")
    ap.add_argument("--glob", default="gcp_deployment/live_observations_*.json")
    ap.add_argument("--outdir", default="results/rollups")
    ap.add_argument("--report", default="results/observations_report.html")
    args = ap.parse_args()

    files = sorted(glob.glob(args.glob))
    rollup_rows: List[Dict[str, Any]] = []
    inst_rows: List[Dict[str, Any]] = []
    anomalies: List[Dict[str, Any]] = []

    for p in files:
        r, i, a = parse_observation_file(p)
        rollup_rows.extend(r)
        inst_rows.extend(i)
        anomalies.extend(a)

    # Consecutive-point anomaly checks for spikes/drops
    by_time = sorted(rollup_rows, key=lambda r: (r.get("timestamp") or "", r.get("file") or ""))
    prev = None
    for r in by_time:
        if prev and prev.get("timestamp") != r.get("timestamp"):
            for fld, name, up, down in (("total_wealth", "wealth", 0.5, -0.1), ("avg_happiness", "happiness", 0.25, -0.25), ("avg_energy", "energy", 0.25, -0.25)):
                a = prev.get(fld); b = r.get(fld)
                if a is not None and b is not None and a != 0:
                    pct = (b - a) / abs(a)
                    if pct > up:
                        anomalies.append({"type": f"{name}_spike", "from": a, "to": b, "pct": round(pct,3), "timestamp": r.get("timestamp"), "file": r.get("file")})
                    if pct < down:
                        anomalies.append({"type": f"{name}_drop", "from": a, "to": b, "pct": round(pct,3), "timestamp": r.get("timestamp"), "file": r.get("file")})
        prev = r

    os.makedirs(args.outdir, exist_ok=True)
    write_csv(os.path.join(args.outdir, "timeseries_rollup.csv"), rollup_rows, [
        "file","cycle","timestamp","total_agents","total_steps","avg_happiness","avg_energy","total_wealth","successful_instances"
    ])
    write_csv(os.path.join(args.outdir, "per_instance_deltas.csv"), inst_rows, [
        "file","timestamp","cycle","instance_id","steps","start_happiness","end_happiness","delta_happiness","start_energy","end_energy","delta_energy","start_wealth","end_wealth","delta_wealth"
    ])
    with open(os.path.join(args.outdir, "anomalies.json"), "w", encoding="utf-8") as f:
        json.dump(anomalies, f, indent=2)

    generate_html_report(args.report, rollup_rows, anomalies)
    print("Wrote:")
    print(f" - {args.outdir}/timeseries_rollup.csv")
    print(f" - {args.outdir}/per_instance_deltas.csv")
    print(f" - {args.outdir}/anomalies.json")
    print(f" - {args.report}")


if __name__ == "__main__":
    main()
