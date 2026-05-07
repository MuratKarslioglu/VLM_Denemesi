#!/usr/bin/env python3
"""
02_clip_stage_scoring.py
========================
Çıkarılan frame'leri CLIP modeli ile işlem aşaması (stage) açısından skorlar.

Her frame için tanımlanan stage prompt'larına karşı benzerlik skoru hesaplanır
ve sonuçlar CSV dosyasına kaydedilir.

Kullanım:
    python scripts/02_clip_stage_scoring.py
    python scripts/02_clip_stage_scoring.py --frames data/frames --model ViT-B/32
"""

import argparse
import os
import sys
import csv
import glob
import yaml
import numpy as np
from pathlib import Path
from tqdm import tqdm

import torch
import clip
from PIL import Image


def load_config(config_path="configs/pipeline_config.yaml"):
    """YAML konfigürasyon dosyasını yükler."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def get_stage_labels_and_prompts(config):
    """Config dosyasından stage etiketleri ve prompt'ları döndürür."""
    if config and "stages" in config:
        stages = config["stages"]
        labels = [s["label"] for s in stages]
        prompts = [s["prompt"] for s in stages]
        return labels, prompts
    
    # Varsayılan etiketler ve promptlar
    default_stages = {
        "lifting_preparation": "A crane preparing to lift a large wind turbine component, workers attaching rigging and slings",
        "component_lifting": "A large wind turbine component being lifted by a crane, suspended in the air",
        "vertical_alignment": "A wind turbine component being aligned vertically at height, workers guiding the alignment",
        "component_installation": "A wind turbine component being installed and secured in its final position on the tower",
        "final_inspection": "Workers performing final inspection after wind turbine component installation is complete",
    }
    return list(default_stages.keys()), list(default_stages.values())


def score_frames_with_clip(frames_dir, model_name="ViT-B/32", device="auto",
                            stage_labels=None, stage_prompts=None, batch_size=16):
    """
    Tüm frame'leri CLIP ile skorlar.
    
    Args:
        frames_dir: Frame dosyalarının bulunduğu dizin
        model_name: CLIP model adı
        device: Hesaplama cihazı (auto, cuda, cpu)
        stage_labels: Aşama etiketleri listesi
        stage_prompts: Aşama prompt'ları listesi
        batch_size: Her seferde işlenecek frame sayısı
    
    Returns:
        Skorlama sonuçları listesi (dict'ler)
    """
    # Cihaz belirle
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print("=" * 60)
    print("  CLIP STAGE SCORING")
    print("=" * 60)
    print(f"  Model: {model_name}")
    print(f"  Cihaz: {device}")
    print(f"  Frame dizini: {frames_dir}")
    
    # Frame dosyalarını bul
    frame_files = sorted(
        glob.glob(os.path.join(frames_dir, "*.jpg")) +
        glob.glob(os.path.join(frames_dir, "*.png"))
    )
    
    if not frame_files:
        print(f"[HATA] '{frames_dir}' dizininde frame bulunamadı.")
        print("       Önce 01_extract_frames.py scriptini çalıştırın.")
        sys.exit(1)
    
    print(f"  Toplam frame: {len(frame_files)}")
    print(f"  Aşama sayısı: {len(stage_labels)}")
    print(f"  Aşamalar: {', '.join(stage_labels)}")
    print("=" * 60)
    
    # CLIP modelini yükle
    print("\n  CLIP modeli yükleniyor...")
    model, preprocess = clip.load(model_name, device=device)
    model.eval()
    print(f"  ✓ Model yüklendi: {model_name}")
    
    # Text prompt'larını tokenize et
    text_tokens = clip.tokenize(stage_prompts).to(device)
    
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    print(f"  ✓ {len(stage_prompts)} adet text prompt encode edildi.")
    
    # Frame'leri batch olarak işle
    results = []
    
    print(f"\n  Frame'ler skorlanıyor (batch_size={batch_size})...")
    
    for i in tqdm(range(0, len(frame_files), batch_size), desc="  Scoring"):
        batch_files = frame_files[i:i + batch_size]
        batch_images = []
        
        for fpath in batch_files:
            try:
                img = preprocess(Image.open(fpath).convert("RGB")).unsqueeze(0)
                batch_images.append(img)
            except Exception as e:
                print(f"  [UYARI] Frame okunamadı: {fpath} — {e}")
                continue
        
        if not batch_images:
            continue
        
        batch_tensor = torch.cat(batch_images, dim=0).to(device)
        
        with torch.no_grad():
            image_features = model.encode_image(batch_tensor)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Benzerlik skorları (cosine similarity)
            similarities = (image_features @ text_features.T).cpu().numpy()
        
        for j, fpath in enumerate(batch_files[:len(batch_images)]):
            scores = similarities[j]
            # Softmax uygula
            exp_scores = np.exp(scores - np.max(scores))
            probs = exp_scores / exp_scores.sum()
            
            best_idx = np.argmax(probs)
            
            result = {
                "frame_file": os.path.basename(fpath),
                "frame_path": fpath,
                "predicted_stage": stage_labels[best_idx],
                "confidence": float(probs[best_idx]),
            }
            
            # Her aşama için skoru ekle
            for k, label in enumerate(stage_labels):
                result[f"score_{label}"] = float(probs[k])
            
            results.append(result)
    
    print(f"\n  ✓ Toplam {len(results)} frame skorlandı.")
    return results


def save_results_to_csv(results, csv_path, stage_labels):
    """Sonuçları CSV dosyasına kaydeder."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    fieldnames = ["frame_file", "predicted_stage", "confidence"]
    fieldnames += [f"score_{label}" for label in stage_labels]
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            row = {k: r[k] for k in fieldnames if k in r}
            writer.writerow(row)
    
    print(f"  ✓ Sonuçlar kaydedildi: {csv_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Frame'leri CLIP ile işlem aşaması açısından skorlar."
    )
    parser.add_argument("--frames", type=str, default=None, help="Frame dizini")
    parser.add_argument("--model", type=str, default=None, help="CLIP model adı")
    parser.add_argument("--device", type=str, default=None, help="Cihaz (auto/cuda/cpu)")
    parser.add_argument("--output", type=str, default=None, help="CSV çıktı yolu")
    parser.add_argument("--batch-size", type=int, default=None, help="Batch boyutu")
    parser.add_argument("--config", type=str, default="configs/pipeline_config.yaml")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    # Parametreleri belirle
    if config:
        clip_cfg = config.get("clip", {})
        video_cfg = config.get("video", {})
        results_cfg = config.get("results", {})
        
        frames_dir = args.frames or video_cfg.get("frame_output_dir", "data/frames")
        model_name = args.model or clip_cfg.get("model_name", "ViT-B/32")
        device = args.device or clip_cfg.get("device", "auto")
        csv_output = args.output or results_cfg.get("csv_output", "results/clip_stage_scores.csv")
        batch_size = args.batch_size or clip_cfg.get("batch_size", 16)
    else:
        frames_dir = args.frames or "data/frames"
        model_name = args.model or "ViT-B/32"
        device = args.device or "auto"
        csv_output = args.output or "results/clip_stage_scores.csv"
        batch_size = args.batch_size or 16
    
    stage_labels, stage_prompts = get_stage_labels_and_prompts(config)
    
    results = score_frames_with_clip(
        frames_dir=frames_dir,
        model_name=model_name,
        device=device,
        stage_labels=stage_labels,
        stage_prompts=stage_prompts,
        batch_size=batch_size,
    )
    
    save_results_to_csv(results, csv_output, stage_labels)


if __name__ == "__main__":
    main()
