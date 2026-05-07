#!/usr/bin/env python3
"""
01_extract_frames.py
====================
Video dosyasından belirli aralıklarla frame çıkarır.
Video dosya adı önemli değildir — data/videos/ dizinindeki ilk video otomatik bulunur.

Kullanım:
    python scripts/01_extract_frames.py --every 2
    python scripts/01_extract_frames.py --video data/videos/herhangi_video.mp4 --every 3
"""

import argparse
import os
import sys
import glob
import cv2
import yaml
from pathlib import Path

# Desteklenen video formatları
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv")


def load_config(config_path="configs/pipeline_config.yaml"):
    """YAML konfigürasyon dosyasını yükler."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def find_video_in_dir(video_dir):
    """
    Verilen dizindeki ilk video dosyasını otomatik bulur.
    Dosya adı ne olursa olsun çalışır.
    
    Args:
        video_dir: Video dizini yolu
    
    Returns:
        Bulunan video dosyasının tam yolu veya None
    """
    if not os.path.isdir(video_dir):
        return None
    
    video_files = []
    for f in os.listdir(video_dir):
        if f.lower().endswith(VIDEO_EXTENSIONS) and not f.startswith("."):
            video_files.append(os.path.join(video_dir, f))
    
    video_files.sort()
    
    if not video_files:
        return None
    
    if len(video_files) > 1:
        print(f"  [BİLGİ] {len(video_files)} video dosyası bulundu. İlki kullanılacak:")
        for i, vf in enumerate(video_files):
            marker = "  → " if i == 0 else "    "
            print(f"    {marker}{os.path.basename(vf)}")
    
    return video_files[0]


def resolve_video_path(cli_video, config):
    """
    Video yolunu çözümler. Öncelik sırası:
    1. CLI ile verilen --video argümanı (tam dosya yolu)
    2. Config'deki input_dir dizinindeki ilk video
    3. Varsayılan data/videos/ dizinindeki ilk video
    """
    # 1. CLI'dan geldiyse direkt kullan
    if cli_video:
        if os.path.isfile(cli_video):
            return cli_video
        elif os.path.isdir(cli_video):
            found = find_video_in_dir(cli_video)
            if found:
                return found
        print(f"[HATA] Belirtilen video bulunamadı: {cli_video}")
        sys.exit(1)
    
    # 2. Config'den oku
    if config:
        video_cfg = config.get("video", {})
        # Yeni format: input_dir (dizin)
        video_dir = video_cfg.get("input_dir", None)
        if video_dir:
            found = find_video_in_dir(video_dir)
            if found:
                return found
        # Eski format: input_path (tam yol) — geriye uyumluluk
        video_path = video_cfg.get("input_path", None)
        if video_path and os.path.isfile(video_path):
            return video_path
    
    # 3. Varsayılan dizin
    found = find_video_in_dir("data/videos")
    if found:
        return found
    
    print("[HATA] Video dosyası bulunamadı!")
    print("       Lütfen video dosyasını 'data/videos/' dizinine koyun.")
    print(f"       Desteklenen formatlar: {', '.join(VIDEO_EXTENSIONS)}")
    sys.exit(1)


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
    print(f"  Video: {os.path.basename(video_path)}")
    print(f"  Yol:   {video_path}")
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
        description="Video dosyasından belirli aralıklarla frame çıkarır. "
                    "Video adı önemli değildir, data/videos/ dizinindeki ilk video otomatik bulunur."
    )
    parser.add_argument(
        "--video", type=str, default=None,
        help="Video dosya yolu veya dizini (varsayılan: data/videos/ içindeki ilk video)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Frame çıktı dizini (varsayılan: data/frames)"
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
    
    # Video yolunu çözümle (otomatik algılama)
    video_path = resolve_video_path(args.video, config)
    
    # Diğer parametreleri belirle
    if config:
        video_cfg = config.get("video", {})
        output_dir = args.output or video_cfg.get("frame_output_dir", "data/frames")
        every_n = args.every or video_cfg.get("frame_interval_seconds", 2)
        fmt = args.format or video_cfg.get("output_format", "jpg")
        quality = video_cfg.get("jpeg_quality", 95)
    else:
        output_dir = args.output or "data/frames"
        every_n = args.every or 2
        fmt = args.format or "jpg"
        quality = 95
    
    extract_frames(video_path, output_dir, every_n, fmt, quality)


if __name__ == "__main__":
    main()
