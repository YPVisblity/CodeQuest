@echo off
REM CodeQuest launcher: Django + Caddy + ngrok
REM Keep this file in mysite/ (same folder as manage.py and Caddyfile)

cd /d "%~dp0"

REM ---- settings ----
set "PYTHON=C:\Users\Admin\anaconda3\envs\pythonclean\python.exe"
REM Must match Caddyfile: ":8000" and "reverse_proxy 127.0.0.1:8001"
set "CADDY_PORT=8000"
set "DJANGO_PORT=8001"
REM Fixed ngrok domain, e.g. https://xxx.ngrok-free.dev  (empty = random URL)
set "NGROK_URL=https://makeshift-mothball-tactful.ngrok-free.dev"

echo [1/4] collectstatic
"%PYTHON%" manage.py collectstatic --noinput
if errorlevel 1 (
    echo collectstatic failed.
    pause
    exit /b 1
)

echo [2/4] Django  127.0.0.1:%DJANGO_PORT%
start "Django" cmd /k ""%PYTHON%" manage.py runserver 127.0.0.1:%DJANGO_PORT%"

echo [3/4] Caddy   :%CADDY_PORT%
start "Caddy" cmd /k "caddy run --config Caddyfile"

echo [4/4] ngrok   -^> %CADDY_PORT%
if "%NGROK_URL%"=="" (
    start "ngrok" cmd /k "ngrok http %CADDY_PORT%"
) else (
    start "ngrok" cmd /k "ngrok http %CADDY_PORT% --url %NGROK_URL%"
)

echo.
echo Local: http://127.0.0.1:%CADDY_PORT%
echo Close the Django / Caddy / ngrok windows to stop.
