#!/usr/bin/env python3
"""
06_make_annotated_video.py
==========================
Annotated frame'lerden bir video oluşturur.

Kullanım:
    python scripts/06_make_annotated_video.py
    python scripts/06_make_annotated_video.py --fps 3
"""

import argparse
import os
import sys
import glob
import cv2
import yaml


def load_config(config_path="configs/pipeline_config.yaml"):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def make_video(frames_dir, output_path, fps=2, codec="mp4v"):
    frame_files = sorted(
        glob.glob(os.path.join(frames_dir, "*.jpg")) +
        glob.glob(os.path.join(frames_dir, "*.png"))
    )

    if not frame_files:
        print(f"[HATA] '{frames_dir}' dizininde frame bulunamadı.")
        sys.exit(1)

    # İlk frame'den boyut al
    sample = cv2.imread(frame_files[0])
    if sample is None:
        print("[HATA] İlk frame okunamadı.")
        sys.exit(1)

    h, w = sample.shape[:2]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*codec)
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    print("=" * 60)
    print("  VIDEO OLUŞTURMA")
    print("=" * 60)
    print(f"  Frame sayısı: {len(frame_files)}")
    print(f"  Çözünürlük: {w}x{h}")
    print(f"  FPS: {fps}")
    print(f"  Tahmini süre: {len(frame_files) / fps:.1f} saniye")
    print(f"  Çıktı: {output_path}")

    for fpath in frame_files:
        frame = cv2.imread(fpath)
        if frame is not None:
            if frame.shape[:2] != (h, w):
                frame = cv2.resize(frame, (w, h))
            writer.write(frame)

    writer.release()
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n  ✓ Video oluşturuldu: {output_path} ({file_size:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Annotated frame'lerden video oluşturur.")
    parser.add_argument("--frames", type=str, default=None)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--config", type=str, default="configs/pipeline_config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    if config:
        r_cfg = config.get("results", {})
        v_cfg = config.get("output_video", {})
        frames_dir = args.frames or r_cfg.get("annotated_frames_dir", "data/annotated_frames")
        output_path = args.output or r_cfg.get("annotated_video_output", "results/annotated_clip_output.mp4")
        fps = args.fps or v_cfg.get("fps", 2)
    else:
        frames_dir = args.frames or "data/annotated_frames"
        output_path = args.output or "results/annotated_clip_output.mp4"
        fps = args.fps or 2

    make_video(frames_dir, output_path, fps)


if __name__ == "__main__":
    main()
