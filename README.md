# VLM Offshore Rüzgâr Türbini Kurulum Analizi

Bu proje, offshore rüzgâr türbini kurulum sürecinde kamera görüntülerini kullanarak
kurulum işlemlerinin hangi aşamada olduğunu, çalışanların performansını ve olası
güvenlik risklerini analiz edebilecek yapay zekâ tabanlı bir sistemdir.

## Proje Yapısı

```
VLM_Denemesi/
├── configs/
│   └── pipeline_config.yaml       # Merkezi konfigürasyon dosyası
├── data/
│   ├── videos/                    # Kaynak video dosyaları
│   │   └── offshore_sample.mp4    # (kullanıcı tarafından eklenmeli)
│   ├── frames/                    # Videodan çıkarılan frame'ler
│   ├── annotated_frames/          # CLIP tahminleri yazılmış frame'ler
│   └── top_frames/                # Her aşama için en iyi frame'ler
├── results/                       # Analiz çıktıları
│   ├── clip_stage_scores.csv      # CLIP skorları
│   ├── clip_summary.txt           # Özet rapor
│   └── annotated_clip_output.mp4  # Annotated video
├── scripts/
│   ├── 01_extract_frames.py       # Video → Frame çıkarma
│   ├── 02_clip_stage_scoring.py   # CLIP ile aşama skorlama
│   ├── 03_read_clip_results.py    # Sonuçları özetleme
│   ├── 04_select_top_frames.py    # En iyi frame'leri seçme
│   ├── 05_annotate_clip_predictions.py  # Frame annotasyonu
│   └── 06_make_annotated_video.py       # Video oluşturma
├── requirements.txt               # Python bağımlılıkları
├── run_all_clip_pipeline.sh       # Pipeline çalıştırma (macOS/Linux)
├── run_all_clip_pipeline.bat      # Pipeline çalıştırma (Windows)
├── vlm_offshore_calisma_raporu.md # Detaylı çalışma raporu
└── README.md                      # Bu dosya
```

## Hızlı Başlangıç

### 1. Sanal Ortam Oluştur
```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows
```

### 2. Bağımlılıkları Kur
```bash
pip install -r requirements.txt
```

### 3. Video Dosyasını Yerleştir
Video dosyanızı `data/videos/offshore_sample.mp4` konumuna kopyalayın.

### 4. Pipeline'ı Çalıştır

**Adım adım:**
```bash
python scripts/01_extract_frames.py --every 2
python scripts/02_clip_stage_scoring.py
python scripts/03_read_clip_results.py
python scripts/04_select_top_frames.py --top 3
python scripts/05_annotate_clip_predictions.py
python scripts/06_make_annotated_video.py
```

**Toplu çalıştırma:**
```bash
bash run_all_clip_pipeline.sh
```

## İşlem Aşamaları (Stages)

| Aşama | Açıklama |
|-------|----------|
| `lifting_preparation` | Kaldırma hazırlığı |
| `component_lifting` | Parça kaldırma |
| `vertical_alignment` | Dikey hizalama |
| `component_installation` | Parça montajı |
| `final_inspection` | Son kontrol |

## Model Yol Haritası

1. ✅ **CLIP** — Aşama sınıflandırma (mevcut)
2. 🔲 **YOLO / RT-DETR** — Nesne tespiti
3. 🔲 **SAM3** — Segmentasyon
4. 🔲 **ByteTrack** — Nesne takibi
5. 🔲 **Qwen-VL** — Sahne açıklama ve raporlama
