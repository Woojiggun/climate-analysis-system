@echo off
cd /d "D:\AI project\climate-analysis-system\backend"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000