@echo off
rem Doble clic para abrir Product Tester en el navegador (Windows).
cd /d "%~dp0"

where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo No encontre Python. Instalalo desde https://www.python.org/downloads/
  echo y marca la casilla "Add Python to PATH". Despues volve a abrir este archivo.
  pause
  exit /b 1
)

if not exist .venv (
  echo Primera vez: instalando lo necesario, tarda un minuto...
  %PY% -m venv .venv
  if errorlevel 1 ( echo Error creando el entorno. & pause & exit /b 1 )
  .venv\Scripts\python -m pip install -q --upgrade pip
)
.venv\Scripts\python -m pip install -q -r requirements.txt
if errorlevel 1 ( echo Error instalando dependencias. & pause & exit /b 1 )

if not exist .env (
  copy .env.example .env >nul
  echo Cree el archivo .env: completalo con tus claves de Meta y Shopify cuando las tengas.
)

echo Abriendo Product Tester... deja esta ventana abierta; cerrala para apagarlo.
.venv\Scripts\python -m product_tester web %*
pause
