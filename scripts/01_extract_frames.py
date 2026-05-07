#!/usr/bin/env python3
"""
01_extract_frames.py
====================
Video dosyasından belirli aralıklarla frame çıkarır.

Kullanım:
    python scripts/01_extract_frames.py --every 2
    python scripts/01_extract_frames.py --video data/videos/offshore_sample.mp4 --output data/frames --every 3
"""

import argparse
import os
import sys
import cv2
import yaml
from pathlib import Path


def load_config(config_path="configs/pipeline_config.yaml"):
    """YAML konfigürasyon dosyasını yükler."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def extract_frames(video_path, output_dir, every_n_seconds=2, output_format="jpg", jpeg_quality=95):
    """
    Video dosyasından belirli saniye aralıklarıyla frame çıkarır.
    
    Args:
        video_path: Video dosyasının yolu
        output_dir: Çıkarılan frame'lerin kaydedileceği dizin
        every_n_seconds: Kaç saniyede bir frame alınacak
        output_format: Çıktı formatı (jpg, png)
        jpeg_quality: JPEG kalitesi (0-100)
    
    Returns:
        Çıkarılan frame sayısı
    """
    # Video dosyasını kontrol et
    if not os.path.exists(video_path):
        print(f"[HATA] Video dosyası bulunamadı: {video_path}")
        print(f"       Lütfen video dosyasını '{video_path}' konumuna yerleştirin.")
        sys.exit(1)
    
    # Çıktı dizinini oluştur
    os.makedirs(output_dir, exist_ok=True)
    
    # Videoyu aç
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[HATA] Video açılamadı: {video_path}")
        sys.exit(1)
    
    # Video bilgilerini al
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print("=" * 60)
    print("  FRAME ÇIKARMA İŞLEMİ")
    print("=" * 60)
    print(f"  Video: {video_path}")
    print(f"  FPS: {fps:.1f}")
    print(f"  Toplam frame: {total_frames}")
    print(f"  Süre: {duration:.1f} saniye ({duration/60:.1f} dakika)")
    print(f"  Frame aralığı: Her {every_n_seconds} saniyede bir")
    print(f"  Tahmini çıktı frame sayısı: {int(duration / every_n_seconds)}")
    print(f"  Çıktı dizini: {output_dir}")
    print("=" * 60)
    
    # Frame aralığını hesapla
    frame_interval = int(fps * every_n_seconds)
    if frame_interval < 1:
        frame_interval = 1
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            timestamp = frame_count / fps
            filename = f"frame_{saved_count:05d}_t{timestamp:.1f}s.{output_format}"
            filepath = os.path.join(output_dir, filename)
            
            if output_format == "jpg":
                cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
            else:
                cv2.imwrite(filepath, frame)
            
            saved_count += 1
            
            if saved_count % 10 == 0:
                print(f"  [{saved_count} frame kaydedildi] t={timestamp:.1f}s")
        
        frame_count += 1
    
    cap.release()
    
    print(f"\n  ✓ Tamamlandı! Toplam {saved_count} frame çıkarıldı.")
    print(f"  ✓ Frame'ler '{output_dir}' dizinine kaydedildi.")
    
    return saved_count


def main():
    parser = argparse.ArgumentParser(
        description="Video dosyasından belirli aralıklarla frame çıkarır."
    )
    parser.add_argument(
        "--video", type=str, default=None,
        help="Video dosyasının yolu (varsayılan: config dosyasından okunur)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Frame çıktı dizini (varsayılan: config dosyasından okunur)"
    )
    parser.add_argument(
        "--every", type=float, default=None,
        help="Kaç saniyede bir frame alınacak (varsayılan: 2)"
    )
    parser.add_argument(
        "--format", type=str, default=None, choices=["jpg", "png"],
        help="Çıktı formatı (varsayılan: jpg)"
    )
    parser.add_argument(
        "--config", type=str, default="configs/pipeline_config.yaml",
        help="Konfigürasyon dosyası yolu"
    )
    
    args = parser.parse_args()
    
    # Konfigürasyon yükle
    config = load_config(args.config)
    
    # Parametreleri belirle (CLI > config > varsayılan)
    if config:
        video_cfg = config.get("video", {})
        video_path = args.video or video_cfg.get("input_path", "data/videos/offshore_sample.mp4")
        output_dir = args.output or video_cfg.get("frame_output_dir", "data/frames")
        every_n = args.every or video_cfg.get("frame_interval_seconds", 2)
        fmt = args.format or video_cfg.get("output_format", "jpg")
        quality = video_cfg.get("jpeg_quality", 95)
    else:
        video_path = args.video or "data/videos/offshore_sample.mp4"
        output_dir = args.output or "data/frames"
        every_n = args.every or 2
        fmt = args.format or "jpg"
        quality = 95
    
    extract_frames(video_path, output_dir, every_n, fmt, quality)


if __name__ == "__main__":
    main()
