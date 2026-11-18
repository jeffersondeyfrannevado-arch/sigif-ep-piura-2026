@echo off
chcp 65001 >nul
title SIGIF-EP Piura 2026 - Deteccion y Gestion de Incidencias TI (UCV 2026)
echo ===============================================================================
echo   SIGIF-EP PIURA 2026 - UNIVERSIDAD CESAR VALLEJO
echo   Aplicacion para la deteccion y gestion de incidencias y fallas en equipos
echo   informaticos de una entidad educativa publica Piura 2026
echo   Autores: Toro Agurto, Mario Andre y Nevado Fiestas, Jefferson Deyfrank
echo ===============================================================================
echo.
cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python main.py
    goto :eof
)

if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python3.11.exe" (
    "%LOCALAPPDATA%\Microsoft\WindowsApps\python3.11.exe" main.py
    goto :eof
)

py main.py
pause
