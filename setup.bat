@echo off
chcp 65001 >nul
title Web Server Manager - Kurulum & Başlatma

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

:: Python sürüm kontrolü
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set pyver=%%i
echo Python sürümü: %pyver%
echo %pyver% | findstr /r "^3\.[0-9][0-9]*" >nul
if %errorlevel% neq 0 (
    echo [HATA] Python 3.0.0 veya üstü gerekli!
    pause
    exit
)

:: venv oluştur
if not exist "venv" (
    echo Sanal ortam (venv) oluşturuluyor...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [HATA] venv oluşturulamadı!
        pause
        exit
    )
)

:: venv aktif et
call venv\Scripts\activate.bat

:: Gerekli paketler
set packages=requests pyperclip psutil
for %%p in (%packages%) do (
    python -c "import %%p" >nul 2>&1
    if %errorlevel% neq 0 (
        :install_%%p
        echo [EKLENTİ] %%p eksik!
        set /p choice="%%p kurulsun mu? [E/H]: "
        if /i "%choice%"=="E" (
            echo %%p kuruluyor...
            pip install %%p --quiet
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

:: Node.js ve localtunnel
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] Node.js bulunamadı!
    set /p choice="Node.js kurulsun mu? [E/H]: "
    if /i "%choice%"=="E" (
        powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.17.0/node-v20.17.0-x64.msi' -OutFile 'node.msi'" >nul
        msiexec /i node.msi /quiet /norestart
        del node.msi
        echo Node.js kuruldu. Yeniden başlatın.
    )
)

npm list -g localtunnel >nul 2>&1
if %errorlevel% neq 0 (
    set /p choice="localtunnel kurulsun mu? [E/H]: "
    if /i "%choice%"=="E" (
        npm install -g localtunnel --silent
    )
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
