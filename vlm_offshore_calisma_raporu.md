# VLM Tabanlı Offshore Rüzgâr Türbini Kurulum Analizi Projesi — Çalışma Raporu

## 1. Projenin Genel Amacı

Bu çalışma kapsamında amaç, offshore rüzgâr türbini / rüzgâr gülü kurulum sürecinde kamera görüntülerini kullanarak kurulum işlemlerinin hangi aşamada olduğunu, çalışanların işi ne kadar doğru yaptığını, parça konumlarını, işlem ilerleme yüzdesini ve olası iş güvenliği risklerini analiz edebilecek yapay zekâ tabanlı bir sistem geliştirmektir.

Sistemden beklenen temel çıktılar şunlardır:

- Görüntü veya video üzerinden mevcut işlem aşamasını belirlemek.
- Büyük parçaların konumunu ve hareket durumunu analiz etmek.
- İşlem adımının yaklaşık yüzde kaç tamamlandığını tahmin etmek.
- Çalışanları, ekipmanları ve kritik bölgeleri tespit etmek.
- Çalışanların prosedüre uygun davranıp davranmadığını değerlendirmek.
- Olası kazalarda olay zincirini ve hata/ihmal ihtimalini analiz etmek.
- Sonuçları insan tarafından anlaşılabilir rapor formatında sunmak.

Bu nedenle proje yalnızca klasik görüntü işleme problemi olarak değil; object detection, segmentation, tracking, action/procedure understanding, rule-based reasoning ve Vision-Language Model bileşenlerini birleştiren multimodal bir sistem olarak ele alınmıştır.

---

## 2. İlk Aşamada Belirlenen Ana Teknolojik Alan: Vision-Language Model

Çalışmanın başlangıcında genel konu olarak Visual Language Model ifadesi ele alınmış, ancak literatürde daha doğru kullanımın Vision-Language Model (VLM) olduğu belirtilmiştir.

VLM, görüntü ve metni birlikte işleyebilen multimodal yapay zekâ modelidir. Bu modeller görüntüden bilgi çıkarabilir, görüntü hakkında soru cevaplayabilir, sahne açıklaması yapabilir ve görsel veriler üzerinden mantıksal çıkarım üretebilir.

Projede VLM’in tek başına bütün sistemi çözmeyeceği, daha çok şu amaçlarla kullanılacağı netleştirilmiştir:

- Görsel sahneyi açıklamak.
- İşlem aşamasını yorumlamak.
- Güvenlik risklerini doğal dille ifade etmek.
- Detection, segmentation ve tracking çıktılarından elde edilen kanıtları raporlamak.
- Olay sonrası analiz ve açıklama üretmek.

---

## 3. Projeye Özel Problem Tanımı

Daha sonra proje bağlamı netleştirilmiştir. Hocanın verdiği ana problem şu şekilde tanımlanmıştır:

Offshore rüzgâr türbini kurulum sürecinde belirli kamera açılarından alınan görüntüler kullanılarak çalışanların işlemleri ne kadar doğru yaptığı, hangi işlem adımında olunduğu, hangi parçanın nerede bulunduğu ve işlem adımının yaklaşık yüzde kaç tamamlandığı tespit edilmelidir.

Ayrıca olası bir kazada kimin hatalı olabileceğini analiz etmek için olay zinciri çıkarılmalıdır.

Bu problem doğrultusunda sistemin cevaplaması gereken sorular şunlar olarak belirlenmiştir:

- Hangi kurulum aşamasındayız?
- Ana parça nerede ve hangi yönde hareket ediyor?
- Parça kaldırılıyor mu, hizalanıyor mu, kuruluyor mu, yoksa son kontrolde mi?
- Çalışanlar doğru yerde mi?
- Çalışanlar güvenlik ekipmanlarını kullanıyor mu?
- Tehlikeli bölgeye giriş var mı?
- İşlem prosedüre uygun ilerliyor mu?
- Olası ihlal veya risk hangi zaman aralığında oluştu?

---

## 4. Video Örneği ve Mimari Güncellemesi

Kullanıcı tarafından örnek olarak bir Vimeo videosu verilmiştir:

https://vimeo.com/273681277

Bu video offshore rüzgâr türbini kurulum sürecine benzer bir sahne içerdiği için sistem tasarımına şu yeni gereksinimler eklenmiştir:

- Sadece çalışan güvenliği değil, işlem aşaması takibi de yapılmalıdır.
- Parça konumu, vinç hareketi ve ana bileşenlerin kurulum sürecindeki durumu analiz edilmelidir.
- Sistemin “hangi işlem adımındayız?” sorusuna cevap vermesi gerekir.
- Sistemin “bu işlem adımının yüzde kaçındayız?” sorusuna yaklaşık cevap üretmesi gerekir.
- Çalışan doğruluk değerlendirmesi, işlem adımına göre yapılmalıdır.

Bu noktadan sonra mimari yalnızca “iş güvenliği ihlali tespiti” değil, “kurulum süreci takibi + çalışan uyumu + olay analizi” şeklinde genişletilmiştir.

---

## 5. Önerilen Genel Sistem Mimarisi

Çalışma sırasında aşağıdaki çok katmanlı mimari önerilmiştir:

1. Video Input Layer  
   Kamera veya video dosyasından görüntü alınır.

2. Frame Sampling Layer  
   Videodaki her frame analiz edilmez. Örneğin 2–5 FPS veya belirli saniye aralıklarıyla frame alınır.

3. Fast Detection Layer  
   YOLO veya RT-DETR gibi modellerle çalışan, vinç, kanca, türbin parçası, PPE ekipmanları gibi nesneler hızlıca tespit edilir.

4. Segmentation Layer  
   SAM3 ile çalışan, büyük parça, vinç kancası, kurulum bölgesi ve risk bölgeleri piksel seviyesinde ayrılır.

5. Tracking Layer  
   ByteTrack, BoT-SORT veya benzeri yöntemlerle çalışanlar ve büyük parçalar video boyunca takip edilir.

6. Process State Estimator  
   Sistem mevcut işlem aşamasını tahmin eder. Örneğin lifting preparation, component lifting, vertical alignment, component installation veya final inspection.

7. Progress Estimator  
   Parçanın konumu, açısı, hareket yönü ve hedef bölgeye uzaklığı kullanılarak işlem ilerleme yüzdesi hesaplanır.

8. Worker Compliance Engine  
   Çalışanın o işlem adımında yapması gerekenlerle görüntüdeki davranışı karşılaştırılır.

9. Safety Rule Engine  
   PPE eksikliği, tehlikeli bölgeye giriş, yük altında durma, platform kenarı riski gibi kurallar kontrol edilir.

10. VLM Reasoning and Report Layer  
    Qwen-VL, LLaVA veya benzeri VLM modelleriyle sahne açıklanır, olay raporu ve belirsizlik bilgileri üretilir.

---

## 6. Öğrenilen ve İncelenen Model Aileleri

### 6.1. CLIP

CLIP, görüntü ve metni aynı embedding uzayına taşıyan bir model olarak incelenmiştir.

Projede CLIP’in görevi şu şekilde belirlenmiştir:

- Bir frame’in hangi işlem aşamasına daha çok benzediğini skorlamak.
- Örneğin component_lifting, vertical_alignment veya final_inspection gibi aday aşamalar arasında benzerlik skoru üretmek.
- Hızlı ve hafif bir ön tahmin katmanı olarak kullanmak.

Örnek stage prompt seti oluşturulmuştur:

- lifting_preparation
- component_lifting
- vertical_alignment
- component_installation
- final_inspection

Özellikle vertical_alignment ve final_inspection etiketlerinin proje bağlamında teknik olarak uygun olduğu belirtilmiştir.

### 6.2. LLaVA

LLaVA, görüntü hakkında soru-cevap ve açıklama üretebilen bir VLM olarak incelenmiştir.

CLIP yalnızca skor verirken, LLaVA’nın sahneyi açıklayabileceği belirtilmiştir.

Projede LLaVA’nın olası görevleri:

- Görsel sahne açıklaması yapmak.
- İşlem aşamasını gerekçesiyle açıklamak.
- Görüntüdeki riskleri yorumlamak.
- Belirsizlikleri raporlamak.

Ancak LLaVA’nın tek başına kesin karar verici olmaması gerektiği, daha çok açıklama katmanı olarak kullanılmasının doğru olduğu vurgulanmıştır.

### 6.3. Qwen-VL / Qwen2.5-VL / Qwen3-VL

Qwen-VL ailesi daha güçlü multimodal reasoning ve video understanding kabiliyeti nedeniyle proje açısından önemli görülmüştür.

Hocanın verdiği model olan Qwen3-VL-235B-A22B-Thinking ifadesi parçalarına ayrılarak açıklanmıştır:

- Qwen3: model ailesinin üçüncü nesli.
- VL: Vision-Language özelliği.
- 235B: toplam parametre ölçeği.
- A22B: aktif uzman/parametre yapısı.
- Thinking: daha derin muhakeme gerektiren işler için kullanılan varyant.

Bu modelin gerçek zamanlı canlı analiz için çok ağır olduğu, daha çok kaza sonrası detaylı olay analizi, prosedür karşılaştırması ve raporlama için uygun olduğu belirtilmiştir.

Canlı veya yakın gerçek zamanlı sistem için daha küçük Qwen-VL modellerinin kullanılmasının daha mantıklı olduğu ifade edilmiştir.

### 6.4. SAM3

SAM3, Segment Anything Model 3 olarak incelenmiştir.

SAM3’ün temel görevi:

- Görüntü veya videodaki nesneleri segmentlemek.
- Text prompt, visual prompt veya exemplar prompt ile nesne maskeleri çıkarmak.
- Video içinde nesneleri takip etmek.
- Pixel-level evidence üretmek.

Projede SAM3’ün rolü şu şekilde konumlandırılmıştır:

SAM3 karar vermez; görsel kanıt üretir.

Örneğin:

- Büyük türbin parçasının maskesi çıkarılır.
- Parça merkezi, parça açısı ve parça alanı hesaplanır.
- Çalışan maskesi çıkarılır.
- Çalışanın tehlikeli bölgeyle çakışıp çakışmadığı hesaplanır.
- Vinç kancası ve parça ilişkisi analiz edilir.

SAM3’ün CLIP, YOLO, tracking ve VLM çıktılarıyla birlikte kullanılacağı belirtilmiştir.

---

## 7. Kod Uygulamasına Geçiş Planı

Kullanıcı, teorik model anlatımlarından sonra artık her model için kod çalışması yapıp çıktıları yorumlamayı öğrenmek istediğini belirtmiştir.

Bu nedenle ilk uygulama paketi olarak CLIP tabanlı bir pipeline planlanmıştır. İlk uygulamanın hafif, hızlı ve çalıştırılabilir olması amacıyla önce CLIP ile başlanması uygun görülmüştür.

İlk kod paketi şu adımları içerecek şekilde hazırlanmıştır:

1. Video dosyasından belirli aralıklarla frame çıkarma.
2. Çıkarılan frame’leri CLIP ile işlem aşaması açısından skorlama.
3. CLIP sonuçlarını CSV dosyasına kaydetme.
4. Sonuçları terminalde özetleme.
5. Her işlem aşaması için en yüksek skorlu frame’leri seçme.
6. Frame üzerine tahminleri yazma.
7. Annotated frame’lerden kısa bir video üretme.

---

## 8. Proje Dosya Yapısı ve Oluşturulan Dosyalar

CLIP pipeline için gerekli tüm dosyalar proje dizinine yerleştirilmiştir. Proje yapısı şu şekildedir:

```
VLM_Denemesi/
├── configs/
│   └── pipeline_config.yaml          # Merkezi YAML konfigürasyon dosyası
├── data/
│   ├── videos/                        # Kaynak video dosyaları (repo ile birlikte gelir)
│   │   └── *.mp4                      # Otomatik algılanır — dosya adı önemli değil
│   ├── frames/                        # Videodan çıkarılan frame'ler
│   ├── annotated_frames/              # CLIP tahminleri yazılmış frame'ler
│   └── top_frames/                    # Her aşama için en iyi frame'ler
├── results/                           # Analiz çıktıları (CSV, rapor, video)
├── scripts/
│   ├── __init__.py
│   ├── 01_extract_frames.py           # Video → Frame çıkarma
│   ├── 02_clip_stage_scoring.py       # CLIP ile aşama skorlama
│   ├── 03_read_clip_results.py        # Sonuçları okuma ve özetleme
│   ├── 04_select_top_frames.py        # En iyi frame'leri seçme
│   ├── 05_annotate_clip_predictions.py # Frame annotasyonu
│   └── 06_make_annotated_video.py     # Annotated video oluşturma
├── requirements.txt                   # Python bağımlılıkları
├── run_all_clip_pipeline.sh           # Toplu çalıştırma (macOS/Linux)
├── run_all_clip_pipeline.bat          # Toplu çalıştırma (Windows)
├── README.md                          # Proje rehberi
└── vlm_offshore_calisma_raporu.md     # Bu çalışma raporu
```

Tüm scriptler `configs/pipeline_config.yaml` dosyasından merkezi olarak konfigüre edilebilir. Ayrıca her script CLI argümanları ile de parametrelenebilir. Video dosyası otomatik algılanır — `data/videos/` dizinine herhangi bir isimle video koymak yeterlidir.

---

## 9. İlerleme Durumu ve 2 Günlük Plan Özeti

### 9.1. Tamamlanan İşler (Gün 1 — Teori ve Altyapı)

Aşağıdaki maddeler tamamlanmıştır:

- [x] Projenin genel amacı ve kapsamı belirlendi.
- [x] VLM (Vision-Language Model) kavramı öğrenildi ve projedeki rolü tanımlandı.
- [x] Offshore rüzgâr türbini kurulum sürecine özel problem tanımı yapıldı.
- [x] 10 katmanlı sistem mimarisi tasarlandı (Video Input → VLM Report).
- [x] CLIP, LLaVA, Qwen-VL ve SAM3 modelleri teorik olarak incelendi.
- [x] Her modelin projedeki yeri ve görevi tanımlandı.
- [x] 5 adet işlem aşaması etiketi belirlendi (lifting_preparation → final_inspection).
- [x] CLIP tabanlı ilk pipeline tasarlandı (6 adımlı).
- [x] 6 Python script + 2 çalıştırma scripti yazıldı ve proje klasörüne yerleştirildi.
- [x] Merkezi konfigürasyon dosyası (pipeline_config.yaml) oluşturuldu.
- [x] requirements.txt, README.md, .gitignore hazırlandı.
- [x] Proje dizin yapısı (data, scripts, configs, results) oluşturuldu.
- [x] GitHub'a yükleme için proje hazır hale getirildi.
- [x] Video dosyası projeye eklendi ve GitHub'a yüklendi.
- [x] Video dosya adından bağımsız otomatik algılama sistemi eklendi.

### 9.2. CLIP Pipeline Çalıştırıldığında Ne Olacak

CLIP pipeline başarıyla çalıştırıldığında şu çıktılar elde edilecektir:

1. **data/frames/** → Videodan her 2 saniyede bir çıkarılmış frame'ler (JPG dosyaları).
2. **results/clip_stage_scores.csv** → Her frame için 5 aşamanın (lifting_preparation, component_lifting, vertical_alignment, component_installation, final_inspection) benzerlik skorları ve tahmin edilen aşama.
3. **results/clip_summary.txt** → Hangi aşamadan kaç frame var, ortalama güven skorları, en iyi/en kötü tahminlerin özet raporu.
4. **data/top_frames/** → Her aşama için en yüksek güvenli 3 frame (aşama adına göre alt klasörlerde).
5. **data/annotated_frames/** → Üzerlerine tahmin bilgisi yazılmış frame'ler (stage + confidence bar).
6. **results/annotated_clip_output.mp4** → Tüm annotated frame'lerden oluşturulan özet video.

**Bu çıktılarla yapılacak yorumlar:**
- CLIP modeli offshore kurulum sahnelerinde hangi aşamaları daha doğru tahmin ediyor?
- Hangi aşamalar birbiriyle karıştırılıyor?
- Güven skorları ne kadar yüksek? (%60+ iyi, %40-60 kabul edilebilir, %40 altı zayıf)
- CLIP tek başına yeterli mi, yoksa ek modellere (VLM, detection) ihtiyaç var mı?

### 9.3. CLIP Pipeline Sonrası Durum

CLIP pipeline tamamlandığında Gün 1'in pratik kısmı bitmiş olacak. Bu noktada proje şu aşamada olacak:

- Teori ve mimari: %100 tamamlandı.
- CLIP tabanlı aşama sınıflandırma: %100 tamamlandı.
- Sonuçlar üretildi ve yorumlandı.
- Sistemin geri kalan bileşenlerine (VLM, detection, segmentation) geçiş için hazır.

---

## 10. Şu Andan Sonra Yapılması Gerekenler — Tam Yol Haritası

### AŞAMA A: Ortam Kurulumu ve CLIP Pipeline (ŞİMDİ YAPILACAK)

Bu aşamadaki adımlar GitHub'a yükleme ve Ubuntu'da ilk çalıştırma içindir.

#### A.1. GitHub'a yükleme (macOS'ta yapılacak)
```bash
cd ~/Desktop/VLM_Denemesi
git init
git add .
git commit -m "Initial commit: CLIP pipeline + proje altyapısı"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADI/VLM_Denemesi.git
git push -u origin main
```

#### A.2. Video dosyası (TAMAMLANDI)
- Video dosyası repo ile birlikte geliyor (GitHub'a yüklendi).
- `data/videos/` dizinindeki herhangi bir video dosyası otomatik algılanır.
- Dosya adı önemli değildir — desteklenen formatlar: .mp4, .avi, .mov, .mkv, .webm
- Farklı bir video ile denemek için eski videoyu silip yenisini `data/videos/` dizinine koymak yeterlidir.

#### A.3. Ubuntu'da kurulum
```bash
# Repo'yu klonla
git clone https://github.com/KULLANICI_ADI/VLM_Denemesi.git
cd VLM_Denemesi

# Sistem bağımlılıkları (OpenCV + ffmpeg için)
sudo apt update
sudo apt install -y python3-pip python3-venv libgl1-mesa-glx libglib2.0-0 ffmpeg

# Sanal ortam
python3 -m venv venv
source venv/bin/activate

# GPU varsa önce PyTorch CUDA kurulumu
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Bağımlılıklar
pip install --upgrade pip
pip install -r requirements.txt
```

#### A.4. Video dosyası kontrolü
```bash
# Video dosyasının geldiğini doğrula
ls -la data/videos/
# Herhangi bir .mp4/.avi/.mov dosyası görünmeli
```

#### A.5. CLIP pipeline'ı çalıştır
```bash
source venv/bin/activate
bash run_all_clip_pipeline.sh
```

#### A.6. Sonuçları incele
```bash
# CSV sonuçlarına bak
cat results/clip_stage_scores.csv | head -20

# Özet raporu oku
cat results/clip_summary.txt

# Annotated video boyutunu kontrol et
ls -la results/annotated_clip_output.mp4
```

---

### AŞAMA B: CLIP Sonuçlarını Değerlendirme ve Prompt Optimizasyonu

CLIP pipeline çalıştıktan sonra yapılacaklar:

#### B.1. Sonuçları analiz et
- Her aşamadaki frame dağılımına bak: Dengeli mi, yoksa çoğu frame tek bir aşamaya mı düşüyor?
- Güven skorlarını incele: Düşük güvenli tahminler neden düşük?
- top_frames klasörlerindeki frame'leri gözle incele: Doğru aşamaya atanmış mı?

#### B.2. Prompt mühendisliği
- configs/pipeline_config.yaml dosyasındaki stage prompt'larını videodan elde edilen gözlemlere göre iyileştir.
- Örneğin "A crane preparing to lift..." yerine daha spesifik "Workers on an offshore platform connecting rigging cables to a nacelle..." gibi prompt'lar dene.
- Pipeline'ı yeniden çalıştırıp sonuçları karşılaştır.

#### B.3. Farklı CLIP modeli dene
- ViT-B/32 (mevcut — hızlı, düşük doğruluk)
- ViT-B/16 (orta — dengeli)
- ViT-L/14 (yavaş — yüksek doğruluk)
```bash
python3 scripts/02_clip_stage_scoring.py --model ViT-L/14
```

---

### AŞAMA C: Qwen-VL ile Sahne Açıklama (Gün 2 — İlk Yarı)

CLIP yalnızca skor verir. Qwen-VL ise sahneyi doğal dille açıklayabilir.

#### C.1. Qwen-VL scripti yazılacak (scripts/07_qwen_vl_scene_description.py)
- CLIP tarafından seçilen top frame'ler Qwen-VL'ye gönderilecek.
- Her frame için şu sorular sorulacak:
  - "Bu görüntüde hangi offshore kurulum aşaması gerçekleştiriliyor?"
  - "Çalışanlar ne yapıyor ve güvenlik ekipmanları var mı?"
  - "Bu işlem adımında herhangi bir risk veya ihlal görüyor musun?"
- Yanıtlar JSON/TXT olarak results/qwen_vl_descriptions.json dosyasına kaydedilecek.

#### C.2. CLIP + Qwen-VL karşılaştırması
- CLIP'in tahmin ettiği aşama ile Qwen-VL'nin açıklaması tutarlı mı?
- Qwen-VL'nin eklediği yeni bilgiler (risk, detay) neler?

---

### AŞAMA D: YOLO ile Nesne Tespiti (Gün 2 — Orta Kısım)

#### D.1. YOLO scripti yazılacak (scripts/08_yolo_object_detection.py)
- YOLOv8 veya RT-DETR ile frame'lerdeki nesneler tespit edilecek.
- Hedef nesneler: çalışan (person), vinç (crane), kanca (hook), türbin parçası, baret/yelek (PPE).
- Sonuçlar: bounding box koordinatları, sınıf, güven skoru.

#### D.2. Özel model eğitimi planı
- Eğer standart YOLO modeli offshore nesnelerini iyi tespit edemiyorsa, custom dataset ile fine-tuning planı yapılacak.
- Roboflow veya CVAT ile etiketleme.

---

### AŞAMA E: SAM3 ile Segmentasyon (Gün 2 — İkinci Yarı)

#### E.1. SAM3 scripti yazılacak (scripts/09_sam3_segmentation.py)
- YOLO'nun tespit ettiği nesnelerin piksel-seviye maskeleri çıkarılacak.
- Text prompt ile segmentasyon denenecek ("wind turbine blade", "worker", "crane hook").
- Parça alan hesaplaması ve konum analizi yapılacak.

#### E.2. SAM3 + YOLO entegrasyonu
- YOLO bounding box → SAM3 segmentation pipeline kurulacak.

---

### AŞAMA F: Tracking ve İlerleme Tahmini (İleriki Çalışma)

#### F.1. ByteTrack veya BoT-SORT ile video boyunca nesne takibi.
#### F.2. Parça pozisyonu değişimi üzerinden ilerleme yüzdesi hesaplama.
#### F.3. Çalışan hareket analizi ve tehlikeli bölge kontrolü.

---

### AŞAMA G: Entegre Sistem ve Raporlama (İleriki Çalışma)

#### G.1. Tüm bileşenleri birleştiren ana pipeline:
- Frame çıkarma → YOLO detection → SAM3 segmentation → Tracking → CLIP stage → Qwen-VL rapor.

#### G.2. Olay zinciri analizi ve kaza sonrası değerlendirme modülü.
#### G.3. Kullanıcı arayüzü veya dashboard (isteğe bağlı).

---

## 11. Ubuntu'da Çalışacak AI İçin Bağlam Özeti

> Bu bölüm, Ubuntu üzerinde çalışırken kullanılacak AI asistanının projeyi hızla anlaması için hazırlanmıştır. Yeni bir AI oturumunda bu bölümü paylaşarak devam edebilirsiniz.

### Proje Nedir?
Offshore rüzgâr türbini kurulum sürecini kamera görüntüleriyle analiz eden çok katmanlı bir AI sistemi geliştiriyoruz. Sistem şunları yapacak:
1. Kurulum aşamasını otomatik tespit etmek (CLIP ile).
2. Sahneyi doğal dille açıklamak (Qwen-VL ile).
3. Çalışanları ve ekipmanları tespit etmek (YOLO ile).
4. Nesneleri piksel seviyesinde ayırmak (SAM3 ile).
5. Video boyunca takip etmek (ByteTrack ile).
6. Güvenlik kurallarını kontrol etmek (Rule Engine).
7. Sonuçları raporlamak (VLM Reasoning Layer).

### Şu An Neredeyiz?
- Teori ve mimari tasarım tamamlandı.
- CLIP tabanlı aşama sınıflandırma pipeline'ı kodlandı ve proje klasörüne yerleştirildi.
- 6 Python script + konfigürasyon + çalıştırma scriptleri hazır.
- Video dosyası repo ile birlikte geliyor, ayrıca indirmeye gerek yok.
- Pipeline henüz çalıştırılmadı veya çalıştırıldıysa sonuçlar bu bölümün altına eklenecek.
- Script'ler video adından bağımsız çalışır (data/videos/ dizinindeki ilk videoyu otomatik bulur).

### Proje Yapısı
```
VLM_Denemesi/
├── configs/pipeline_config.yaml   # Merkezi konfigürasyon
├── data/videos/                    # Video dosyası (kullanıcı ekledi)
├── data/frames/                    # Çıkarılan frame'ler (pipeline çıktısı)
├── data/annotated_frames/          # Annotated frame'ler (pipeline çıktısı)
├── data/top_frames/                # En iyi frame'ler (pipeline çıktısı)
├── results/                        # CSV, özet rapor, video (pipeline çıktısı)
├── scripts/01-06*.py              # CLIP pipeline scriptleri
├── requirements.txt               # Bağımlılıklar
└── run_all_clip_pipeline.sh       # Toplu çalıştırma
```

### Kullanılan Teknolojiler
- **CLIP (ViT-B/32)**: Zero-shot aşama sınıflandırma.
- **OpenCV**: Frame çıkarma, annotasyon, video oluşturma.
- **PyTorch**: Model inference backend.
- **YAML**: Merkezi konfigürasyon.

### İşlem Aşamaları (Stage Labels)
1. `lifting_preparation` — Kaldırma hazırlığı
2. `component_lifting` — Parça kaldırma
3. `vertical_alignment` — Dikey hizalama
4. `component_installation` — Parça montajı
5. `final_inspection` — Son kontrol

### Bir Sonraki Adım
Pipeline çalıştırıldıysa → Sonuçları analiz et, prompt optimizasyonu yap, Qwen-VL scriptine geç.
Pipeline çalıştırılmadıysa → `bash run_all_clip_pipeline.sh` ile çalıştır.

---

## 12. Genel Değerlendirme

Bu aşamaya kadar çalışma, teori ve mimari tasarım açısından sağlam bir temel oluşturmuştur. Özellikle VLM'in tek başına karar verici olmayacağı; CLIP, SAM3, YOLO, tracking, rule engine ve Qwen-VL gibi bileşenlerin birlikte kullanılacağı netleştirilmiştir.

İlk pratik aşama olarak CLIP pipeline seçilmiştir çünkü kurulumu hafif, çalıştırması hızlı ve işlem aşaması tahmini için doğrudan kullanılabilir bir başlangıç sağlar. Bu pipeline çalıştırıldıktan sonra model çıktıları incelenecek, hangi frame'lerde vertical_alignment, component_lifting ve final_inspection gibi aşamaların daha yüksek skor aldığı yorumlanacak ve sonraki aşamada VLM tabanlı açıklama modellerine geçilecektir.

2 günlük planın Gün 1 teorik kısmı ve CLIP pipeline altyapısı tamamlanmıştır. CLIP pipeline'ın Ubuntu'da çalıştırılması ile Gün 1 pratiği de tamamlanacak, ardından Gün 2'de Qwen-VL, YOLO ve SAM3 ile genişletme çalışmalarına geçilecektir.
