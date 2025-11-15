#!/usr/bin/env python3
"""Generate per-component and cross-system summaries for the NOUS project."""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
from collections import defaultdict
from datetime import datetime
from statistics import mean
from typing import Any, Dict, Iterable, List, Tuple


def read_csv_rows(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def parse_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def summarize_ai_society() -> Dict[str, Any]:
    rollup_path = "results/rollups/timeseries_rollup.csv"
    anomalies_path = "results/rollups/anomalies.json"
    rows = read_csv_rows(rollup_path)
    timestamps = [parse_timestamp(r.get("timestamp")) for r in rows]

    happiness_values = [parse_float(r.get("avg_happiness")) for r in rows]
    energy_values = [parse_float(r.get("avg_energy")) for r in rows]
    wealth_values = [parse_float(r.get("total_wealth")) for r in rows]
    total_agents = [parse_float(r.get("total_agents")) for r in rows]

    def stats(values: List[float]) -> Dict[str, float]:
        clean = [v for v in values if not math.isnan(v)]
        if not clean:
            return {"mean": math.nan, "min": math.nan, "max": math.nan, "latest": math.nan}
        return {
            "mean": mean(clean),
            "min": min(clean),
            "max": max(clean),
            "latest": clean[-1],
        }

    anomalies = []
    if os.path.exists(anomalies_path):
        anomalies = read_json(anomalies_path)

    documents = [
        "LLM_SOCIETY_README.md",
        "comprehensive_2500_agent_analysis.md",
        "COMPREHENSIVE_LLM_INTEGRATION_SUMMARY.md",
        "GOD_PORTAL_DESIGN.md",
    ]
    documents = [p for p in documents if os.path.exists(p)]

    ts_clean = [t for t in timestamps if t is not None]
    span = None
    if ts_clean:
        span = {
            "start": min(ts_clean).isoformat(),
            "end": max(ts_clean).isoformat(),
            "duration_hours": (max(ts_clean) - min(ts_clean)).total_seconds() / 3600,
        }

    facts = []
    h_stats = stats(happiness_values)
    e_stats = stats(energy_values)
    w_stats = stats(wealth_values)
    if not math.isnan(h_stats["mean"]):
        facts.append(
            f"Average happiness {h_stats['mean']:.3f} (range {h_stats['min']:.3f}–{h_stats['max']:.3f}); latest {h_stats['latest']:.3f}."
        )
    if not math.isnan(e_stats["mean"]):
        facts.append(
            f"Average energy {e_stats['mean']:.3f}; latest {e_stats['latest']:.3f}."
        )
    if not math.isnan(w_stats["mean"]):
        facts.append(
            f"Total wealth grew to {w_stats['latest']:.0f} (avg {w_stats['mean']:.0f})."
        )
    if anomalies:
        anomaly_types = defaultdict(int)
        for a in anomalies:
            anomaly_types[a.get("type", "unknown")] += 1
        top_types = sorted(anomaly_types.items(), key=lambda kv: kv[1], reverse=True)[:3]
        facts.append(
            "Anomalies flagged: "
            + ", ".join(f"{k} ({v})" for k, v in top_types)
            + ("; others omitted" if len(anomaly_types) > 3 else "")
        )

    metrics = {
        "observations": len(rows),
        "anomalies": len(anomalies),
        "timespan": span,
        "happiness": h_stats,
        "energy": e_stats,
        "wealth": w_stats,
        "avg_agents": stats(total_agents)["mean"],
    }

    return {
        "id": "ai_society",
        "label": "AI Society",
        "metrics": metrics,
        "documents": documents,
        "facts": facts,
    }


def summarize_spatial_lab() -> Dict[str, Any]:
    files = glob.glob("results/sprint_1_multi_scale/*.json")
    records: List[Dict[str, Any]] = []
    for path in files:
        try:
            data = read_json(path)
            if isinstance(data, list):
                records.extend(data)
        except json.JSONDecodeError:
            continue

    total = len(records)
    correct = sum(1 for r in records if r.get("is_correct"))
    categories = defaultdict(lambda: {"total": 0, "correct": 0})
    providers = defaultdict(int)
    latencies = []
    costs = []
    difficulties = defaultdict(lambda: {"total": 0, "correct": 0})

    for r in records:
        categories[r.get("category", "unknown")]["total"] += 1
        if r.get("is_correct"):
            categories[r.get("category", "unknown")]["correct"] += 1
        providers[r.get("provider", "unknown")] += 1
        latencies.append(parse_float(r.get("latency_ms")))
        costs.append(parse_float(r.get("cost_estimate")))
        difficulties[r.get("difficulty", "unknown")]["total"] += 1
        if r.get("is_correct"):
            difficulties[r.get("difficulty", "unknown")]["correct"] += 1

    accuracy = (correct / total) if total else math.nan

    category_breakdown = {
        cat: {
            "total": dat["total"],
            "accuracy": (dat["correct"] / dat["total"]) if dat["total"] else math.nan,
        }
        for cat, dat in categories.items()
    }

    difficulty_breakdown = {
        str(diff): {
            "total": dat["total"],
            "accuracy": (dat["correct"] / dat["total"]) if dat["total"] else math.nan,
        }
        for diff, dat in difficulties.items()
    }

    valid_latency = [v for v in latencies if not math.isnan(v)]
    valid_costs = [v for v in costs if not math.isnan(v)]

    metrics = {
        "tasks": total,
        "accuracy": accuracy,
        "avg_latency_ms": mean(valid_latency) if valid_latency else math.nan,
        "avg_cost_estimate": mean(valid_costs) if valid_costs else math.nan,
        "providers": dict(providers),
        "category_breakdown": category_breakdown,
        "difficulty_breakdown": difficulty_breakdown,
    }

    facts = [
        f"Total tasks evaluated: {total} across {len(category_breakdown)} categories.",
        f"Overall accuracy: {accuracy*100:.1f}%" if not math.isnan(accuracy) else "Accuracy unavailable.",
        f"Average latency: {metrics['avg_latency_ms']:.1f} ms" if valid_latency else "Latency unavailable.",
    ]

    documents = [
        "SPATIAL_LAB_README.md",
        "results/sprint_1_multi_scale/DETAILED_ANALYSIS_REPORT.md",
        "SPATIAL_AI_LAB_IMPLEMENTATION_SUMMARY.md",
    ]
    documents = [p for p in documents if os.path.exists(p)]

    return {
        "id": "spatial_lab",
        "label": "Spatial AI Lab",
        "metrics": metrics,
        "documents": documents,
        "facts": facts,
    }


def summarize_warehouse() -> Dict[str, Any]:
    files = glob.glob("results/warehouse_coordination_results_*.json")
    entries: List[Dict[str, Any]] = []
    for path in files:
        data = read_json(path)
        if isinstance(data, list):
            entries.extend(data)

    total = len(entries)
    if total == 0:
        return {
            "id": "warehouse_coordination",
            "label": "Warehouse Coordination",
            "metrics": {},
            "documents": [],
            "facts": ["No warehouse coordination results found."],
        }

    strategy_stats = defaultdict(list)
    collision_stats = defaultdict(list)
    efficiency = []
    success_rates = []
    for e in entries:
        strategy = e.get("strategy", "unknown")
        eff = parse_float(e.get("avg_efficiency"))
        col = parse_float(e.get("avg_collision_count"))
        sr = parse_float(e.get("success_rate"))
        if not math.isnan(eff):
            strategy_stats[strategy].append(eff)
            efficiency.append(eff)
        if not math.isnan(col):
            collision_stats[strategy].append(col)
        if not math.isnan(sr):
            success_rates.append(sr)

    strategy_summary = {
        strat: {
            "avg_efficiency": mean(vals) if vals else math.nan,
            "avg_collisions": mean(collision_stats.get(strat, [])) if collision_stats.get(strat) else math.nan,
            "count": len(vals),
        }
        for strat, vals in strategy_stats.items()
    }

    distributed = strategy_summary.get("distributed", {})
    centralized = strategy_summary.get("centralized", {})

    diff_eff = None
    if distributed and centralized and not math.isnan(distributed.get("avg_efficiency", math.nan)) and not math.isnan(
        centralized.get("avg_efficiency", math.nan)
    ):
        diff_eff = distributed["avg_efficiency"] - centralized["avg_efficiency"]

    facts = [
        f"Scenarios evaluated: {total} across {len(strategy_summary)} strategies.",
        f"Average success rate: {mean(success_rates)*100:.1f}%" if success_rates else "Success rate unavailable.",
    ]
    if diff_eff is not None:
        facts.append(
            f"Distributed coordination improves efficiency over centralized by {diff_eff*100:.1f} percentage points."
        )

    documents = [
        "warehouse_coordination_results_20250629_160305.json",
        "results/warehouse_coordination_results_20250629_202324.json",
        "research_validator.py",
    ]
    documents = [p for p in documents if os.path.exists(p)]

    metrics = {
        "scenarios": total,
        "strategy_summary": strategy_summary,
        "overall_efficiency": mean(efficiency) if efficiency else math.nan,
        "overall_success_rate": mean(success_rates) if success_rates else math.nan,
    }

    return {
        "id": "warehouse_coordination",
        "label": "Warehouse / Factory Coordination",
        "metrics": metrics,
        "documents": documents,
        "facts": facts,
    }


def summarize_cloudvr() -> Dict[str, Any]:
    files = glob.glob("research_outputs/*.json")
    reports: List[Dict[str, Any]] = []
    for path in files:
        data = read_json(path)
        if isinstance(data, dict):
            reports.append(data)

    total = len(reports)
    if total == 0:
        return {
            "id": "cloudvr_perfguard",
            "label": "CloudVR PerfGuard",
            "metrics": {},
            "documents": [],
            "facts": ["No CloudVR research outputs found."],
        }

    successes = sum(1 for r in reports if r.get("success"))
    total_data = sum(r.get("data_count", 0) or 0 for r in reports)
    total_cost = sum(r.get("total_cost", 0) or 0 for r in reports)
    research_quality = [parse_float(r.get("research_quality")) for r in reports if r.get("research_quality") is not None]
    paper_counts = [len(r.get("papers", [])) for r in reports]

    apps = defaultdict(int)
    for r in reports:
        for app in r.get("apps_analyzed", []) or []:
            apps[app] += 1

    quality_mean = mean(research_quality) if research_quality else math.nan

    facts = [
        f"Research reports generated: {total} (success rate {successes/total*100:.1f}%).",
        f"Total VR test runs analyzed: {total_data} across {len(apps)} applications.",
        f"Average research quality score: {quality_mean:.1f}" if not math.isnan(quality_mean) else "Research quality unavailable.",
        f"Total AI cost tracked: ${total_cost:.2f}.",
    ]

    documents = glob.glob("cloudvr_perfguard/ai_integration/*_report.md") + glob.glob("research_outputs/*.md")
    documents += [
        "FINAL_SYSTEM_SUMMARY.md",
        "REAL_RESEARCH_ACHIEVEMENT_SUMMARY.md",
        "CloudVR-PerfGuard AI Research System - Final Summary"
    ]
    documents = [p for p in documents if os.path.exists(p)]

    metrics = {
        "reports": total,
        "success_rate": successes / total,
        "total_data_points": total_data,
        "total_cost": total_cost,
        "avg_research_quality": quality_mean,
        "avg_papers_per_report": mean(paper_counts) if paper_counts else math.nan,
        "apps_coverage": dict(apps),
    }

    return {
        "id": "cloudvr_perfguard",
        "label": "CloudVR PerfGuard Research",
        "metrics": metrics,
        "documents": documents,
        "facts": facts,
    }


def summarize_evolution() -> Dict[str, Any]:
    analysis_path = "mega_scale_analysis_20250526_013218.json"
    segmented_path = "segmented_evolution_results.json"
    analysis = read_json(analysis_path) if os.path.exists(analysis_path) else {}
    segmented = read_json(segmented_path) if os.path.exists(segmented_path) else []

    segments = []
    if isinstance(segmented, list):
        for seg in segmented:
            if isinstance(seg, dict):
                segments.append(seg)

    total_segments = len(segments)
    avg_pareto = None
    if segments:
        hues: List[float] = []
        glows: List[float] = []
        densities: List[float] = []
        for seg in segments:
            cues = seg.get("best_cues_pareto_front", []) or []
            for cue in cues:
                hues.append(parse_float(cue.get("color_hue")))
                glows.append(parse_float(cue.get("glow")))
                densities.append(parse_float(cue.get("particle_density")))
        avg_pareto = {
            "avg_glow": mean([v for v in glows if not math.isnan(v)]) if glows else math.nan,
            "avg_color_hue": mean([v for v in hues if not math.isnan(v)]) if hues else math.nan,
            "avg_particle_density": mean([v for v in densities if not math.isnan(v)]) if densities else math.nan,
        }

    facts = []
    if analysis:
        total_exp = analysis.get("total_experiments")
        success = analysis.get("successful_experiments")
        if total_exp:
            facts.append(f"Evolution experiments executed: {total_exp} (successes: {success}).")
    if total_segments:
        if avg_pareto and not math.isnan(avg_pareto.get("avg_glow", math.nan)):
            facts.append(
                f"Segments analyzed: {total_segments}, mean glow {avg_pareto['avg_glow']:.3f}."
            )
        else:
            facts.append(f"Segments analyzed: {total_segments} (cue averages unavailable).")

    documents = [
        "mega_scale_report_20250526_013218.md",
        "segmented_evolution_results.json",
        "comprehensive_research_paper.py",
    ]
    documents = [p for p in documents if os.path.exists(p)]

    metrics = {
        "experiments": analysis,
        "segments": total_segments,
        "avg_pareto": avg_pareto,
    }

    return {
        "id": "evolution",
        "label": "Evolutionary Discovery",
        "metrics": metrics,
        "documents": documents,
        "facts": facts,
    }


def collect_component_summaries() -> List[Dict[str, Any]]:
    components = [
        summarize_ai_society(),
        summarize_spatial_lab(),
        summarize_warehouse(),
        summarize_cloudvr(),
        summarize_evolution(),
    ]
    return components


def write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(data), f, indent=2)


def sanitize_for_json(value: Any) -> Any:
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(v) for v in value]
    return value


def build_html(components: List[Dict[str, Any]], combined: Dict[str, Any]) -> str:
    rows = []
    for comp in components:
        metric_lines = []
        for key, value in comp.get("metrics", {}).items():
            metric_lines.append(f"<li><code>{key}</code>: {escape_html(value)}</li>")
        doc_links = "".join(f"<li>{escape_html(doc)}</li>" for doc in comp.get("documents", []))
        fact_lines = "".join(f"<li>{escape_html(fact)}</li>" for fact in comp.get("facts", []))
        rows.append(
            f"""
            <section>
              <h2>{escape_html(comp['label'])}</h2>
              <h3>Key Facts</h3>
              <ul>{fact_lines}</ul>
              <h3>Metrics</h3>
              <ul>{''.join(metric_lines)}</ul>
              <h3>Documents</h3>
              <ul>{doc_links}</ul>
            </section>
            """
        )

    combined_rows = "".join(
        f"<li>{escape_html(item)}</li>" for item in combined.get("highlights", [])
    )

    html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>NOUS Component Summary</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #f9fafb; color: #111; }}
    header {{ margin-bottom: 24px; }}
    section {{ background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 1px 2px rgba(15,23,42,0.08); }}
    h1 {{ margin-bottom: 0; }}
    h2 {{ color: #1f2937; }}
    code {{ background: #eef2ff; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>NOUS Component Summary</h1>
    <p>Generated fact-based overview of key subsystems and datasets.</p>
    <h2>Cross-System Highlights</h2>
    <ul>{combined_rows}</ul>
  </header>
  {''.join(rows)}
</body>
</html>
"""
    return html


def escape_html(value: Any) -> str:
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return "nan"
        return f"{value}"
    text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def stream_object(data: bytes) -> bytes:
    return b"<< /Length " + str(len(data)).encode("ascii") + b" >>\nstream\n" + data + b"\nendstream"


def build_pdf_bytes(components: List[Dict[str, Any]], combined: Dict[str, Any]) -> bytes:
    def text_block(lines: Iterable[str], x: float, y: float, size: float = 12) -> List[str]:
        cmds = []
        cursor = y
        for line in lines:
            cmds.append(pdf_text(x, cursor, line, size))
            cursor -= size + 2
        return cmds

    highlights = combined.get("highlights", [])
    page_one_cmds: List[str] = [pdf_text(72, 750, "NOUS Component Overview", 18)]
    page_one_cmds += text_block(highlights, 72, 720)

    sections_cmds: List[str] = []
    cursor_y = 680
    for comp in components:
        sections_cmds.append(pdf_text(72, cursor_y, comp["label"], 14))
        cursor_y -= 18
        for fact in comp.get("facts", []):
            sections_cmds.append(pdf_text(84, cursor_y, fact, 10))
            cursor_y -= 14
        cursor_y -= 6
        if cursor_y < 150:
            break

    page_one_cmds += sections_cmds

    remaining_components = components
    page_two_cmds: List[str] = []
    cursor_y = 750
    for comp in remaining_components:
        page_two_cmds.append(pdf_text(72, cursor_y, f"{comp['label']} Metrics", 14))
        cursor_y -= 18
        for k, v in comp.get("metrics", {}).items():
            page_two_cmds.append(pdf_text(84, cursor_y, f"{k}: {v}", 9))
            cursor_y -= 12
        cursor_y -= 12
        if cursor_y < 100:
            break

    page1_stream = stream_object("\n".join(page_one_cmds).encode("ascii", errors="ignore"))
    page2_stream = stream_object("\n".join(page_two_cmds).encode("ascii", errors="ignore"))

    catalog = b"<< /Type /Catalog /Pages 2 0 R >>"
    pages = b"<< /Type /Pages /Kids [3 0 R 6 0 R] /Count 2 >>"
    page1 = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
    font = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    page2 = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 7 0 R >>"

    return build_pdf([catalog, pages, page1, font, page1_stream, page2, page2_stream])


def pdf_text(x: float, y: float, text: str, size: float = 12) -> str:
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"BT /F1 {size} Tf {x:.2f} {y:.2f} Td ({text}) Tj ET"


def build_pdf(objects: List[bytes]) -> bytes:
    output = bytearray()
    output.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{idx} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for off in offsets:
        output.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    output.extend(b"trailer\n<< /Size ")
    output.extend(str(len(objects)+1).encode("ascii"))
    output.extend(b" /Root 1 0 R >>\nstartxref\n")
    output.extend(str(xref_offset).encode("ascii"))
    output.extend(b"\n%%EOF")
    return bytes(output)


def compute_combined_summary(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    highlights: List[str] = []

    ai = next((c for c in components if c["id"] == "ai_society"), None)
    spatial = next((c for c in components if c["id"] == "spatial_lab"), None)
    warehouse = next((c for c in components if c["id"] == "warehouse_coordination"), None)
    cloudvr = next((c for c in components if c["id"] == "cloudvr_perfguard"), None)

    if ai:
        happiness = ai["metrics"].get("happiness", {}).get("mean")
        wealth = ai["metrics"].get("wealth", {}).get("latest")
        if happiness is not None and not math.isnan(happiness):
            highlights.append(f"AI Society maintains mean happiness {happiness:.3f} with wealth reaching {wealth:.0f}.")

    if spatial:
        accuracy = spatial["metrics"].get("accuracy")
        if accuracy is not None and not math.isnan(accuracy):
            highlights.append(f"Spatial Lab achieved {accuracy*100:.1f}% accuracy across {spatial['metrics']['tasks']} tasks.")

    if warehouse:
        diff = warehouse["metrics"].get("strategy_summary", {}).get("distributed", {}).get("avg_efficiency")
        central = warehouse["metrics"].get("strategy_summary", {}).get("centralized", {}).get("avg_efficiency")
        if diff is not None and central is not None and not math.isnan(diff) and not math.isnan(central):
            highlights.append(
                f"Distributed warehouse strategy beats centralized by {(diff-central)*100:+.1f} efficiency points."
            )

    if cloudvr:
        success_rate = cloudvr["metrics"].get("success_rate")
        total_data = cloudvr["metrics"].get("total_data_points")
        if success_rate is not None:
            highlights.append(
                f"CloudVR produced {cloudvr['metrics']['reports']} reports with success {success_rate*100:.1f}% analyzing {total_data} tests."
            )

    return {"highlights": highlights}


def main():
    parser = argparse.ArgumentParser(description="Summarize NOUS components")
    parser.add_argument("--outdir", default="results/component_reports")
    parser.add_argument("--html", default="results/component_reports/index.html")
    parser.add_argument("--pdf", default="results/component_reports/overview.pdf")
    args = parser.parse_args()

    components = collect_component_summaries()
    combined = compute_combined_summary(components)

    os.makedirs(args.outdir, exist_ok=True)
    for comp in components:
        write_json(os.path.join(args.outdir, f"{comp['id']}_summary.json"), comp)
    write_json(os.path.join(args.outdir, "combined_summary.json"), combined)

    html = build_html(components, combined)
    with open(args.html, "w", encoding="utf-8") as f:
        f.write(html)

    pdf_bytes = build_pdf_bytes(components, combined)
    with open(args.pdf, "wb") as f:
        f.write(pdf_bytes)

    print("Generated component summaries:")
    for comp in components:
        print(f" - {comp['label']} ({comp['id']})")
    print(f"HTML report: {args.html}")
    print(f"PDF report: {args.pdf}")


if __name__ == "__main__":
    main()
