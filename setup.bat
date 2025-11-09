@echo off
chcp 65001 >nul
title Web Server Manager - Kurulum

echo.
echo =====================================================
echo       WEB SERVER MANAGER - KURULUM BAŞLATIYOR
echo =====================================================
echo.

:: Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] Python bulunamadı!
    set /p choice="Python kurulsun mu? (Yoksa program çalışmaz) [E/H]: "
    if /i "%choice%"=="E" (
        echo Python indiriliyor...
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe' -OutFile 'python-installer.exe'" >nul
        echo Python kuruluyor...
        start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
        del python-installer.exe
        echo Python kuruldu. Lütfen terminali yeniden açın.
        pause
        exit
    ) else (
        echo Kurulum iptal edildi.
        pause
        exit
    )
)

:: Python sürüm kontrolü (3.0.0+)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set pyver=%%i
echo Python sürümü: %pyver%
echo %pyver% | findstr /r "^3\.[0-9][0-9]*" >nul
if %errorlevel% neq 0 (
    echo [HATA] Python 3.0.0 veya üstü gerekli!
    pause
    exit
)

:: Gerekli Python paketleri
set packages=requests pyperclip psutil
for %%p in (%packages%) do (
    python -c "import %%p" >nul 2>&1
    if %errorlevel% neq 0 (
        :install_%%p
        echo [EKLENTİ] %%p eksik!
        set /p choice="%%p kurulsun mu? (Yoksa program çalışmaz) [E/H]: "
        if /i "%choice%"=="E" (
            echo %%p kuruluyor...
            python -m pip install %%p --quiet
            if %errorlevel% neq 0 (
                echo [HATA] %%p kurulamadı! Yeniden deneniyor...
                goto install_%%p
            )
            echo %%p başarıyla kuruldu.
        ) else (
            echo Kurulum iptal edildi.
            pause
            exit
        )
    )
)

:: Node.js kontrolü
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] Node.js bulunamadı!
    set /p choice="Node.js kurulsun mu? (Yoksa localtunnel çalışmaz) [E/H]: "
    if /i "%choice%"=="E" (
        echo Node.js indiriliyor...
        powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.17.0/node-v20.17.0-x64.msi' -OutFile 'node-installer.msi'" >nul
        echo Node.js kuruluyor...
        msiexec /i node-installer.msi /quiet /norestart
        del node-installer.msi
        echo Node.js kuruldu. Lütfen terminali yeniden açın.
        pause
        exit
    ) else (
        echo Node.js olmadan devam ediliyor (localtunnel çalışmayacak).
    )
) else (
    echo Node.js bulundu.
)

:: npm ve localtunnel
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] npm bulunamadı! Node.js yeniden kurulmalı.
    pause
    exit
)

npm list -g localtunnel >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] localtunnel eksik!
    set /p choice="localtunnel kurulsun mu? [E/H]: "
    if /i "%choice%"=="E" (
        :install_lt
        echo localtunnel kuruluyor...
        npm install -g localtunnel --silent
        if %errorlevel% neq 0 (
            echo [HATA] localtunnel kurulamadı! Yeniden deneniyor...
            goto install_lt
        )
        echo localtunnel başarıyla kuruldu.
    ) else (
        echo localtunnel olmadan devam ediliyor.
    )
) else (
    echo localtunnel bulundu.
)

:: sites klasörü
if not exist "sites" mkdir sites

:: main.py çalıştır
echo.
echo =====================================================
echo           KURULUM TAMAMLANDI! BAŞLATIYOR...
echo =====================================================
echo.
python main.py
pause
