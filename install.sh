#!/bin/sh
#  anow panel installation script - Archive Full Download
#  Python 3 Compatible

PLUGIN_NAME="anowpanel"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"
ARCHIVE_URL="https://github.com/anow2008/anow-panel/archive/refs/heads/main.tar.gz"
TEMP_TAR="/tmp/anow-panel.tar.gz"
TEMP_DIR="/tmp/anow-panel-main"

echo "================================================="
echo "   Welcome to anow panel Installer (Python 3)   "
echo "================================================="
echo "STATUS: Preparing system for installation..."

# تجهيز المسار وحذف أي نسخ قديمة أو ملفات مؤقتة
rm -rf $PLUGIN_PATH
rm -rf $TEMP_TAR
rm -rf /tmp/anow-panel-*
mkdir -p $PLUGIN_PATH

echo "STATUS: Downloading repository archive..."

# تحميل الملف المضغوط للمستودع بالكامل
wget --no-check-certificate "$ARCHIVE_URL" -O "$TEMP_TAR"

if [ -f "$TEMP_TAR" ]; then
    echo "STATUS: Extracting archive files..."
    tar -xzf "$TEMP_TAR" -C /tmp/
    
    # نقل محتويات المستودع المستخرجة إلى مسار البلجن النهائي مباشرة
    if [ -d "$TEMP_DIR" ]; then
        cp -r $TEMP_DIR/* $PLUGIN_PATH/
    else
        cp -r /tmp/anow-panel-*/* $PLUGIN_PATH/
    fi
    
    # تنظيف الملفات المؤقتة
    rm -rf $TEMP_TAR
    rm -rf /tmp/anow-panel-*
else
    echo "ERROR: Failed to download archive package!"
    exit 1
fi

# إعطاء التصاريح اللازمة لجميع الملفات والمجلدات (بما فيها icons)
chmod -R 755 $PLUGIN_PATH

echo "================================================="
echo "       anow panel installed successfully!        "
echo "================================================="
echo "STATUS: Restarting Enigma2 to apply changes..."
echo "================================================="

sleep 2
if [ -f /etc/init.d/enigma2 ]; then
    /etc/init.d/enigma2 restart
elif [ -f /usr/bin/cammanager ]; then
    init 4 && init 3
else
    killall -9 enigma2
fi

exit 0
