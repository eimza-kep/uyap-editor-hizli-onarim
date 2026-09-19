@echo off
chcp 65001 >nul
title UYAP Dokuman Editoru ve UDF Onarim Araci
echo ====================================================================
echo  UYAP Dokuman Editoru ve UDF Dosya Iliskilendirmesi Onariliyor...
echo ====================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Fix-UyapEditor.ps1"

echo.
pause
