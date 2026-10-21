#!/usr/bin/env bash
# ==============================================================================
# UYAP Doküman Editörü macOS & Linux Hızlı Onarım ve Başlatıcı Scripti v1.3
# ==============================================================================
# macOS Sequoia (15.x), Sonoma, Ventura (Apple Silicon M1-M4 & Intel) ve Linux
# için Java algılama, bozuk önbellek temizleme, bellek artırma ve başlatıcı.
# ==============================================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}   UYAP DOKÜMAN EDİTÖRÜ HIZLI ONARIM VE BAŞLATICI (macOS/Linux)   ${NC}"
echo -e "${CYAN}==================================================================${NC}"

OS="$(uname -s)"
ARCH="$(uname -m)"

echo -e "\n${BLUE}[1/4] Sistem Bilgileri:${NC}"
echo "  İşletim Sistemi : $OS"
echo "  İşlemci Mimarisi: $ARCH"

# 1. Java Tespiti (Özellikle Apple Silicon Homebrew ve JVM dizinleri)
JAVA_BIN=""

CANDIDATE_JAVAS=(
    "java"
    "/opt/homebrew/opt/openjdk@8/bin/java"
    "/opt/homebrew/opt/openjdk@11/bin/java"
    "/opt/homebrew/opt/openjdk@17/bin/java"
    "/opt/homebrew/opt/openjdk/bin/java"
    "/usr/local/opt/openjdk@8/bin/java"
    "/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home/bin/java"
    "/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home/bin/java"
    "/usr/lib/jvm/java-8-openjdk-amd64/bin/java"
    "/usr/lib/jvm/default-java/bin/java"
)

for j in "${CANDIDATE_JAVAS[@]}"; do
    if command -v "$j" >/dev/null 2>&1; then
        JAVA_BIN="$j"
        break
    elif [ -x "$j" ]; then
        JAVA_BIN="$j"
        break
    fi
done

if [ -n "$JAVA_BIN" ]; then
    JAVA_VER=$("$JAVA_BIN" -version 2>&1 | head -n 1)
    echo -e "  ${GREEN}✓ Java Bulundu:${NC} $JAVA_VER"
    echo "    Yol: $JAVA_BIN"
else
    echo -e "  ${RED}✗ Java bulunamadı!${NC}"
    if [ "$OS" = "Darwin" ]; then
        echo -e "    ${YELLOW}Öneri (Apple Silicon/Intel):${NC}"
        echo "    brew install openjdk@8"
        echo "    sudo ln -sfn /opt/homebrew/opt/openjdk@8/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-8.jdk"
    fi
fi

# 2. UYAP Editör Uygulaması Tespiti
echo -e "\n${BLUE}[2/4] UYAP Editör Kurulumu Tespiti:${NC}"

UYAP_APP=""
CANDIDATE_APPS=(
    "/Applications/UYAP Editor.app"
    "/Applications/UyapEditor.app"
    "/Applications/UYAP Doküman Editörü.app"
    "$HOME/Applications/UYAP Editor.app"
    "/opt/uyap/editor.jar"
    "$HOME/uyap/editor.jar"
    "$HOME/.uyap/editor.jar"
)

for app in "${CANDIDATE_APPS[@]}"; do
    if [ -d "$app" ] || [ -f "$app" ]; then
        UYAP_APP="$app"
        echo -e "  ${GREEN}✓ UYAP Editör Bulundu:${NC} $app"
        break
    fi
done

if [ -z "$UYAP_APP" ]; then
    echo -e "  ${YELLOW}⚠ Standart UYAP Editör uygulaması bulunamadı.${NC}"
    echo "    Resmi İndirme: https://uyap.gov.tr/Uyap-Editor"
fi

# 3. Bozuk Önbellek Klasörlerini Temizleme
echo -e "\n${BLUE}[3/4] Bozuk Önbellek Temizliği:${NC}"

CACHE_DIRS=(
    "$HOME/.uyap"
    "$HOME/.uyap_cache"
    "$HOME/Library/Caches/Oracle/Java/Deployment/cache"
    "$HOME/Library/Application Support/UYAP/cache"
    "$HOME/.java/deployment/cache"
)

CLEANED=0
for d in "${CACHE_DIRS[@]}"; do
    if [ -d "$d" ]; then
        rm -rf "$d" 2>/dev/null || true
        echo -e "  ${GREEN}✓ Temizlendi:${NC} $d"
        CLEANED=$((CLEANED + 1))
    fi
done

if [ "$CLEANED" -eq 0 ]; then
    echo "  ℹ️  Önbellek klasörleri temiz durumda."
fi

# 4. Yüksek Bellekli Başlatma Komutu
echo -e "\n${BLUE}[4/4] Optimize Başlatıcı:${NC}"

VM_ARGS="-Xms512m -Xmx2048m -Dsun.java2d.uiScale=1.0 -Dfile.encoding=UTF-8"

if [ -n "$UYAP_APP" ] && [ -d "$UYAP_APP" ]; then
    echo -e "  ${GREEN}✓ macOS Uygulaması Başlatılabilir:${NC}"
    echo "    open -a \"$UYAP_APP\""
elif [ -n "$UYAP_APP" ] && [ -f "$UYAP_APP" ] && [ -n "$JAVA_BIN" ]; then
    echo -e "  ${GREEN}✓ JAR Başlatma Komutu:${NC}"
    echo "    $JAVA_BIN $VM_ARGS -jar \"$UYAP_APP\""
else
    echo "  Bellek Taşması (OutOfMemory) Önleyici Standart Çalıştırma:"
    echo "  java $VM_ARGS -jar <editor.jar>"
fi

echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${GREEN}✓ Onarım ve ortam hazırlığı tamamlandı!${NC}"
echo -e "${CYAN}==================================================================${NC}\n"
