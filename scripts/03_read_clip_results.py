#!/usr/bin/env python3
"""
03_read_clip_results.py
=======================
CLIP skorlama sonuçlarını okur ve terminalde özetler.

Kullanım:
    python scripts/03_read_clip_results.py
    python scripts/03_read_clip_results.py --csv results/clip_stage_scores.csv
"""

import argparse
import os
import sys
import csv
import yaml
from collections import Counter


def load_config(config_path="configs/pipeline_config.yaml"):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def read_and_summarize(csv_path, summary_output=None):
    if not os.path.exists(csv_path):
        print(f"[HATA] CSV bulunamadı: {csv_path}")
        sys.exit(1)

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["confidence"] = float(row["confidence"])
            rows.append(row)

    if not rows:
        print("[UYARI] CSV dosyası boş.")
        return

    stage_counter = Counter(r["predicted_stage"] for r in rows)
    total = len(rows)

    stage_confs = {}
    for r in rows:
        s = r["predicted_stage"]
        stage_confs.setdefault(s, []).append(r["confidence"])

    sorted_rows = sorted(rows, key=lambda x: x["confidence"], reverse=True)

    lines = []
    lines.append("=" * 70)
    lines.append("  CLIP STAGE SCORING — SONUÇ ÖZETİ")
    lines.append("=" * 70)
    lines.append(f"  Toplam frame: {total}")
    lines.append("")

    for stage, count in stage_counter.most_common():
        pct = (count / total) * 100
        avg = sum(stage_confs[stage]) / len(stage_confs[stage])
        lines.append(f"  {stage:<30s}  {count:>4} frame ({pct:5.1f}%)  avg_conf={avg:.3f}")

    lines.append("")
    lines.append("  Top 5 en yüksek güven:")
    for r in sorted_rows[:5]:
        lines.append(f"    {r['frame_file']:<30s} → {r['predicted_stage']:<25s} ({r['confidence']:.3f})")

    lines.append("")
    lines.append("  Bottom 5 en düşük güven:")
    for r in sorted_rows[-5:]:
        lines.append(f"    {r['frame_file']:<30s} → {r['predicted_stage']:<25s} ({r['confidence']:.3f})")

    lines.append("=" * 70)

    report = "\n".join(lines)
    print(report)

    if summary_output:
        os.makedirs(os.path.dirname(summary_output), exist_ok=True)
        with open(summary_output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n  ✓ Özet kaydedildi: {summary_output}")


def main():
    parser = argparse.ArgumentParser(description="CLIP sonuçlarını özetler.")
    parser.add_argument("--csv", type=str, default=None)
    parser.add_argument("--summary", type=str, default=None)
    parser.add_argument("--config", type=str, default="configs/pipeline_config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    if config:
        r_cfg = config.get("results", {})
        csv_path = args.csv or r_cfg.get("csv_output", "results/clip_stage_scores.csv")
        summary_out = args.summary or r_cfg.get("summary_output", "results/clip_summary.txt")
    else:
        csv_path = args.csv or "results/clip_stage_scores.csv"
        summary_out = args.summary or "results/clip_summary.txt"

    read_and_summarize(csv_path, summary_out)


if __name__ == "__main__":
    main()
