#!/bin/bash
# ============================================================
# VLM Offshore — CLIP Pipeline Toplu Çalıştırma (macOS/Linux)
# ============================================================
# Kullanım: bash run_all_clip_pipeline.sh
# ============================================================

set -e

# Python komutunu belirle (venv aktifse "python", değilse "python3" dene)
if command -v python &> /dev/null && python -c "import sys; assert sys.version_info >= (3,8)" 2>/dev/null; then
    PY=python
elif command -v python3 &> /dev/null; then
    PY=python3
else
    echo "[HATA] Python 3.8+ bulunamadı. Lütfen Python yükleyin."
    exit 1
fi

echo "============================================================"
echo "  VLM Offshore — CLIP Pipeline"
echo "  Python: $($PY --version)"
echo "============================================================"
echo ""

# Adım 1: Frame çıkarma
echo "[1/6] Frame çıkarma..."
$PY scripts/01_extract_frames.py --every 2
echo ""

# Adım 2: CLIP skorlama
echo "[2/6] CLIP stage scoring..."
$PY scripts/02_clip_stage_scoring.py
echo ""

# Adım 3: Sonuçları oku
echo "[3/6] Sonuçları okuma ve özetleme..."
$PY scripts/03_read_clip_results.py
echo ""

# Adım 4: Top frame'leri seç
echo "[4/6] Top frame seçimi..."
$PY scripts/04_select_top_frames.py --top 3
echo ""

# Adım 5: Frame annotasyonu
echo "[5/6] Frame annotasyonu..."
$PY scripts/05_annotate_clip_predictions.py
echo ""

# Adım 6: Video oluştur
echo "[6/6] Annotated video oluşturma..."
$PY scripts/06_make_annotated_video.py
echo ""

echo "============================================================"
echo "  ✓ Pipeline tamamlandı!"
echo "  Sonuçlar: results/ dizininde"
echo "============================================================"
