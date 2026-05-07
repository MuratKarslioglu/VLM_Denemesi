#!/usr/bin/env python3
"""
05_annotate_clip_predictions.py
===============================
Frame'lerin üzerine CLIP tahminlerini (aşama + güven skoru) yazarak
annotated frame'ler oluşturur.

Kullanım:
    python scripts/05_annotate_clip_predictions.py
"""

import argparse
import os
import sys
import csv
import cv2
import yaml


def load_config(config_path="configs/pipeline_config.yaml"):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def annotate_frames(csv_path, frames_dir, output_dir, ann_cfg=None):
    if not os.path.exists(csv_path):
        print(f"[HATA] CSV bulunamadı: {csv_path}")
        sys.exit(1)

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["confidence"] = float(row["confidence"])
            rows.append(row)

    os.makedirs(output_dir, exist_ok=True)

    # Annotasyon ayarları
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = ann_cfg.get("font_scale", 0.7) if ann_cfg else 0.7
    thickness = ann_cfg.get("font_thickness", 2) if ann_cfg else 2
    bar_height = ann_cfg.get("bar_height", 60) if ann_cfg else 60

    print("=" * 60)
    print("  FRAME ANNOTASYONU")
    print("=" * 60)

    count = 0
    for r in rows:
        src = os.path.join(frames_dir, r["frame_file"])
        if not os.path.exists(src):
            continue

        frame = cv2.imread(src)
        if frame is None:
            continue

        h, w = frame.shape[:2]
        conf = r["confidence"]
        stage = r["predicted_stage"]

        # Renk seç (güvene göre)
        if conf >= 0.6:
            color = (0, 200, 0)  # Yeşil
        elif conf >= 0.4:
            color = (0, 200, 200)  # Sarı
        else:
            color = (0, 0, 200)  # Kırmızı

        # Üst bar çiz
        cv2.rectangle(frame, (0, 0), (w, bar_height), (0, 0, 0), -1)

        # Metin yaz
        text = f"Stage: {stage} | Confidence: {conf:.1%}"
        cv2.putText(frame, text, (10, 25), font, font_scale, (255, 255, 255), thickness)

        # Güven barı çiz
        bar_w = int((w - 20) * conf)
        cv2.rectangle(frame, (10, 35), (10 + bar_w, 50), color, -1)
        cv2.rectangle(frame, (10, 35), (w - 10, 50), (100, 100, 100), 1)

        # Kaydet
        dst = os.path.join(output_dir, r["frame_file"])
        cv2.imwrite(dst, frame)
        count += 1

    print(f"  ✓ {count} annotated frame oluşturuldu → {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Frame'lere CLIP tahminlerini yazar.")
    parser.add_argument("--csv", type=str, default=None)
    parser.add_argument("--frames", type=str, default=None)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--config", type=str, default="configs/pipeline_config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    if config:
        r_cfg = config.get("results", {})
        v_cfg = config.get("video", {})
        csv_path = args.csv or r_cfg.get("csv_output", "results/clip_stage_scores.csv")
        frames_dir = args.frames or v_cfg.get("frame_output_dir", "data/frames")
        output_dir = args.output or r_cfg.get("annotated_frames_dir", "data/annotated_frames")
        ann_cfg = config.get("annotation", {})
    else:
        csv_path = args.csv or "results/clip_stage_scores.csv"
        frames_dir = args.frames or "data/frames"
        output_dir = args.output or "data/annotated_frames"
        ann_cfg = {}

    annotate_frames(csv_path, frames_dir, output_dir, ann_cfg)


if __name__ == "__main__":
    main()
