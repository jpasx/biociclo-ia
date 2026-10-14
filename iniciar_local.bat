@echo off
title BioCiclo IA - Servidor Local
cd /d "%~dp0"
echo ========================================================
echo       Iniciando BioCiclo IA (Servidor Local)
echo ========================================================
echo.
echo Abrindo aplicacao no navegador: http://localhost:8501 ...
start http://localhost:8501
.\venv\Scripts\python.exe -m streamlit run app/main.py
pause
