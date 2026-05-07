#!/usr/bin/env python3
"""
04_select_top_frames.py
=======================
Her işlem aşaması için en yüksek CLIP skorlu frame'leri seçer ve kopyalar.

Kullanım:
    python scripts/04_select_top_frames.py
    python scripts/04_select_top_frames.py --top 3
"""

import argparse
import os
import sys
import csv
import shutil
import yaml
from collections import defaultdict


def load_config(config_path="configs/pipeline_config.yaml"):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def select_top_frames(csv_path, frames_dir, output_dir, top_n=3):
    if not os.path.exists(csv_path):
        print(f"[HATA] CSV bulunamadı: {csv_path}")
        sys.exit(1)

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["confidence"] = float(row["confidence"])
            rows.append(row)

    # Her aşama için grupla
    stage_groups = defaultdict(list)
    for r in rows:
        stage_groups[r["predicted_stage"]].append(r)

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("  TOP FRAME SEÇİMİ")
    print("=" * 60)

    total_copied = 0
    for stage, items in sorted(stage_groups.items()):
        items_sorted = sorted(items, key=lambda x: x["confidence"], reverse=True)
        top_items = items_sorted[:top_n]

        stage_dir = os.path.join(output_dir, stage)
        os.makedirs(stage_dir, exist_ok=True)

        print(f"\n  [{stage}] — {len(items)} frame, en iyi {len(top_items)} seçildi:")
        for item in top_items:
            src = os.path.join(frames_dir, item["frame_file"])
            dst = os.path.join(stage_dir, item["frame_file"])
            if os.path.exists(src):
                shutil.copy2(src, dst)
                total_copied += 1
                print(f"    ✓ {item['frame_file']} (güven: {item['confidence']:.3f})")
            else:
                print(f"    ✗ {item['frame_file']} — kaynak bulunamadı")

    print(f"\n  ✓ Toplam {total_copied} frame '{output_dir}' dizinine kopyalandı.")


def main():
    parser = argparse.ArgumentParser(description="Her aşama için en iyi frame'leri seçer.")
    parser.add_argument("--csv", type=str, default=None)
    parser.add_argument("--frames", type=str, default=None)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--top", type=int, default=3, help="Her aşamadan kaç frame seçilecek")
    parser.add_argument("--config", type=str, default="configs/pipeline_config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    if config:
        r_cfg = config.get("results", {})
        v_cfg = config.get("video", {})
        csv_path = args.csv or r_cfg.get("csv_output", "results/clip_stage_scores.csv")
        frames_dir = args.frames or v_cfg.get("frame_output_dir", "data/frames")
        output_dir = args.output or r_cfg.get("top_frames_dir", "data/top_frames")
    else:
        csv_path = args.csv or "results/clip_stage_scores.csv"
        frames_dir = args.frames or "data/frames"
        output_dir = args.output or "data/top_frames"

    select_top_frames(csv_path, frames_dir, output_dir, args.top)


if __name__ == "__main__":
    main()
