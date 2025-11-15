#!/usr/bin/env python3
"""Generate a PDF report with summary and simple line charts."""

import argparse
import csv
import json
import math
import os
from statistics import mean
from typing import List, Dict, Tuple


def read_rollup(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def read_anomalies(path: str) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def parse_float(val: str) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return math.nan


def escape_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_text(x: float, y: float, text: str, size: float = 12) -> str:
    return f"BT /F1 {size} Tf {x:.2f} {y:.2f} Td ({escape_text(text)}) Tj ET"


def chart_commands(values: List[float], rect: Tuple[float, float, float, float], color: Tuple[float, float, float], label: str) -> List[str]:
    x0, y0, width, height = rect
    cmds = [pdf_text(x0, y0 + height + 15, label, 12)]
    # axes
    cmds.append(f"0 0 0 RG {x0:.2f} {y0:.2f} m {x0:.2f} {y0 + height:.2f} l {x0 + width:.2f} {y0:.2f} l S")

    clean = [v for v in values if not math.isnan(v)]
    if not clean:
        cmds.append(pdf_text(x0 + width / 2, y0 + height / 2, "(no data)", 10))
        return cmds

    vmin = min(clean)
    vmax = max(clean)
    if math.isclose(vmin, vmax):
        vmin -= 0.5
        vmax += 0.5

    cmds.append(f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f} RG 1 w")
    count = len(values)
    for idx, val in enumerate(values):
        if math.isnan(val):
            continue
        x = x0 + (width if count == 1 else width * idx / (count - 1))
        norm = (val - vmin) / (vmax - vmin)
        y = y0 + norm * height
        if idx == 0 or all(math.isnan(values[k]) for k in range(idx)):
            cmds.append(f"{x:.2f} {y:.2f} m")
        else:
            cmds.append(f"{x:.2f} {y:.2f} l")
    cmds.append("S 1 0 0 0 RG")
    return cmds


def build_pdf(objects: List[bytes]) -> bytes:
    out = bytearray()
    out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{idx} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(b"trailer\n<< /Size ")
    out.extend(str(len(objects)+1).encode("ascii"))
    out.extend(b" /Root 1 0 R >>\nstartxref\n")
    out.extend(str(xref).encode("ascii"))
    out.extend(b"\n%%EOF")
    return bytes(out)


def make_content_page(summary_lines: List[str], metrics: Dict[str, List[float]]) -> bytes:
    elements: List[str] = []
    y_cursor = 750
    elements.append(pdf_text(72, y_cursor, "Society Live Observations", 18))
    y_cursor -= 30
    for line in summary_lines:
        elements.append(pdf_text(72, y_cursor, line, 11))
        y_cursor -= 14

    chart_height = 120
    chart_width = 468
    start_y = 360
    colors = {
        "avg_happiness": (0.259, 0.647, 0.961),
        "avg_energy": (0.4, 0.733, 0.416),
        "total_wealth": (1.0, 0.655, 0.149),
    }
    labels = {
        "avg_happiness": "Average Happiness",
        "avg_energy": "Average Energy",
        "total_wealth": "Total Wealth",
    }
    for idx, key in enumerate(["avg_happiness", "avg_energy", "total_wealth"]):
        rect = (72, start_y - idx * (chart_height + 30), chart_width, chart_height)
        elements.extend(chart_commands(metrics.get(key, []), rect, colors[key], labels[key]))

    content = "\n".join(elements).encode("ascii")
    return stream_object(content)


def make_anomaly_page(anomalies: List[Dict[str, str]]) -> bytes:
    elements = [pdf_text(72, 750, "Anomalies", 16)]
    y = 720
    to_show = anomalies[:30]
    if not to_show:
        elements.append(pdf_text(72, y, "(No anomalies detected)", 12))
    else:
        for entry in to_show:
            text = (
                f"[{entry.get('type','?')}] ts={entry.get('timestamp','-')}"
                f" file={entry.get('file','-')} details="
            )
            details = {k: v for k, v in entry.items() if k not in ("type", "timestamp", "file")}
            lines = [text + json.dumps(details, ensure_ascii=False)]
            for line in lines:
                elements.append(pdf_text(72, y, line, 10))
                y -= 14
                if y < 72:
                    break
            if y < 72:
                elements.append(pdf_text(72, y, "(truncated)", 10))
                break

    return stream_object("\n".join(elements).encode("ascii"))


def stream_object(data: bytes) -> bytes:
    return b"<< /Length " + str(len(data)).encode("ascii") + b" >>\nstream\n" + data + b"\nendstream"


def make_pdf(rollup: List[Dict[str, str]], anomalies: List[Dict[str, str]], output: str) -> None:
    timestamps = [row.get("timestamp") for row in rollup if row.get("timestamp")]
    metrics = {k: [parse_float(row.get(k)) for row in rollup] for k in ("avg_happiness", "avg_energy", "total_wealth")}

    summary_lines: List[str] = []
    summary_lines.append(f"Observations: {len(rollup)}")
    if timestamps:
        summary_lines.append(f"First timestamp: {timestamps[0]}")
        summary_lines.append(f"Last timestamp: {timestamps[-1]}")
    for key, label in (("avg_happiness", "Avg happiness"), ("avg_energy", "Avg energy"), ("total_wealth", "Total wealth")):
        vals = [v for v in metrics[key] if not math.isnan(v)]
        if vals:
            summary_lines.append(f"{label}: mean {mean(vals):.3f}, min {min(vals):.3f}, max {max(vals):.3f}")
    summary_lines.append(f"Anomalies detected: {len(anomalies)}")

    # PDF objects formation
    # 1: catalog, 2: pages, 3: page1, 4: font, 5: content1, 6: page2,7 content2
    page1_content = make_content_page(summary_lines, metrics)
    page2_content = make_anomaly_page(anomalies)

    obj_catalog = b"<< /Type /Catalog /Pages 2 0 R >>"
    obj_pages = b"<< /Type /Pages /Kids [3 0 R 6 0 R] /Count 2 >>"
    obj_page1 = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
    obj_font = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    obj_page2 = b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 7 0 R >>"

    pdf_bytes = build_pdf([
        obj_catalog,
        obj_pages,
        obj_page1,
        obj_font,
        page1_content,
        obj_page2,
        page2_content,
    ])

    with open(output, "wb") as f:
        f.write(pdf_bytes)
    print(f"Wrote PDF: {output}")


def main():
    parser = argparse.ArgumentParser(description="Create PDF report from rollup CSV and anomalies JSON")
    parser.add_argument("--rollup", default="results/rollups/timeseries_rollup.csv")
    parser.add_argument("--anomalies", default="results/rollups/anomalies.json")
    parser.add_argument("--pdf", default="results/rollups/observations_report.pdf")
    args = parser.parse_args()

    rollup = read_rollup(args.rollup)
    anomalies = read_anomalies(args.anomalies)
    os.makedirs(os.path.dirname(args.pdf) or ".", exist_ok=True)
    make_pdf(rollup, anomalies, args.pdf)


if __name__ == "__main__":
    main()
