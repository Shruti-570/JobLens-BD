@echo off
cd /d "%~dp0"
start "JobLens BD" http://localhost:8501
python -m streamlit run app.py
