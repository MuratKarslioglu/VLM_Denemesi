@echo off
REM ============================================================
REM VLM Offshore — CLIP Pipeline Toplu Çalıştırma (Windows)
REM ============================================================
REM Kullanım: run_all_clip_pipeline.bat
REM ============================================================

echo ============================================================
echo   VLM Offshore — CLIP Pipeline
echo ============================================================
echo.

echo [1/6] Frame çıkarma...
python scripts\01_extract_frames.py --every 2
if errorlevel 1 goto :error
echo.

echo [2/6] CLIP stage scoring...
python scripts\02_clip_stage_scoring.py
if errorlevel 1 goto :error
echo.

echo [3/6] Sonuçları okuma ve özetleme...
python scripts\03_read_clip_results.py
if errorlevel 1 goto :error
echo.

echo [4/6] Top frame seçimi...
python scripts\04_select_top_frames.py --top 3
if errorlevel 1 goto :error
echo.

echo [5/6] Frame annotasyonu...
python scripts\05_annotate_clip_predictions.py
if errorlevel 1 goto :error
echo.

echo [6/6] Annotated video oluşturma...
python scripts\06_make_annotated_video.py
if errorlevel 1 goto :error
echo.

echo ============================================================
echo   Pipeline tamamlandı!
echo   Sonuçlar: results\ dizininde
echo ============================================================
goto :end

:error
echo.
echo [HATA] Pipeline sırasında bir hata oluştu!
pause
exit /b 1

:end
pause
