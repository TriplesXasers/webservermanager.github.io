#!/bin/bash

clear
echo ""
echo "====================================================="
echo "     WEB SERVER MANAGER - KURULUM BAŞLATIYOR"
echo "====================================================="
echo ""

# Renkler
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}[UYARI] Python3 bulunamadı!${NC}"
    read -p "Python3 kurulsun mu? (Yoksa program çalışmaz) [E/H]: " choice
    if [[ $choice =~ ^[Ee]$ ]]; then
        echo "Python3 kuruluyor..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if ! command -v brew &> /dev/null; then
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python@3.12
        elif [[ -f /etc/debian_version ]]; then
            sudo apt update && sudo apt install -y python3 python3-pip python3-venv
        elif [[ -f /etc/redhat-release ]]; then
            sudo yum install -y python3 python3-pip || sudo dnf install -y python3 python3-pip
        else
            echo -e "${RED}[HATA] Desteklenmeyen dağıtım!${NC}"
            read -n 1 -s -r -p "Çıkmak için bir tuşa basın..."
            exit 1
        fi
    else
        echo "Kurulum iptal edildi."
        read -n 1 -s -r -p "Çıkmak için bir tuşa basın..."
        exit 1
    fi
else
    echo -e "${GREEN}Python3 bulundu.${NC}"
fi

# Python sürüm kontrolü
PYVER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || echo "0")
echo "Python sürümü: $PYVER"
if [[ $(echo "$PYVER < 3.0.0" | bc -l 2>/dev/null || echo 1) -eq 1 ]]; then
    echo -e "${RED}[HATA] Python 3.0.0 veya üstü gerekli!${NC}"
    read -n 1 -s -r -p "Çıkmak için bir tuşa basın..."
    exit 1
fi

# Gerekli paketler
packages=("requests" "pyperclip" "psutil")
for pkg in "${packages[@]}"; do
    python3 -c "import $pkg" 2>/dev/null
    if [ $? -ne 0 ]; then
        while true; do
            echo -e "${YELLOW}[EKLENTİ] $pkg eksik!${NC}"
            read -p "$pkg kurulsun mu? (Yoksa program çalışmaz) [E/H]: " choice
            if [[ $choice =~ ^[Ee]$ ]]; then
                echo "$pkg kuruluyor..."
                python3 -m pip install $pkg --quiet --user
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}$pkg başarıyla kuruldu.${NC}"
                    break
                else
                    echo -e "${RED}[HATA] $pkg kurulamadı! Yeniden deneniyor...${NC}"
                fi
            else
                echo "Kurulum iptal edildi."
                read -n 1 -s -r -p "Çıkmak için bir tuşa basın..."
                exit 1
            fi
        done
    fi
done

# Node.js kontrolü
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}[UYARI] Node.js bulunamadı!${NC}"
    read -p "Node.js kurulsun mu? (Yoksa localtunnel çalışmaz) [E/H]: " choice
    if [[ $choice =~ ^[Ee]$ ]]; then
        echo "Node.js kuruluyor..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install node
        elif [[ -f /etc/debian_version ]]; then
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt install -y nodejs
        elif [[ -f /etc/redhat-release ]]; then
            curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
            sudo yum install -y nodejs || sudo dnf install -y nodejs
        fi
    else
        echo "Node.js olmadan devam ediliyor."
    fi
else
    echo -e "${GREEN}Node.js bulundu.${NC}"
fi

# npm ve localtunnel
if command -v npm &> /dev/null; then
    if ! npm list -g localtunnel &> /dev/null; then
        echo -e "${YELLOW}[UYARI] localtunnel eksik!${NC}"
        read -p "localtunnel kurulsun mu? [E/H]: " choice
        if [[ $choice =~ ^[Ee]$ ]]; then
            while true; do
                echo "localtunnel kuruluyor..."
                npm install -g localtunnel --silent
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}localtunnel başarıyla kuruldu.${NC}"
                    break
                else
                    echo -e "${RED}[HATA] localtunnel kurulamadı! Yeniden deneniyor...${NC}"
                fi
            done
        else
            echo "localtunnel olmadan devam ediliyor."
        fi
    else
        echo -e "${GREEN}localtunnel bulundu.${NC}"
    fi
else
    echo -e "${RED}[HATA] npm bulunamadı!${NC}"
    read -n 1 -s -r -p "Çıkmak için bir tuşa basın..."
    exit 1
fi

# sites klasörü
mkdir -p sites

echo ""
echo "====================================================="
echo "        KURULUM TAMAMLANDI! BAŞLATIYOR..."
echo "====================================================="
echo ""
python3 "$(dirname "$0")/main.py"
