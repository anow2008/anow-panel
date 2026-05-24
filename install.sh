#!/bin/sh
#  anow panel installation script
#  Python 3 Compatible - Updated for anow-panel Repo

PLUGIN_NAME="anowpanel"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"
GITHUB_RAW="https://raw.githubusercontent.com/anow2008/anow-panel/main"

echo "================================================="
echo "   Welcome to anow panel Installer (Python 3)   "
echo "================================================="
echo "STATUS: Preparing system for installation..."

# حذف النسخة القديمة إن وجدت وتجهيز المجلد
rm -rf $PLUGIN_PATH
mkdir -p $PLUGIN_PATH

echo "STATUS: Downloading anow panel files from new repo..."

# تحميل ملفات البلجن من الريبو الجديد بالظبط
wget --no-check-certificate "$GITHUB_RAW/plugin.py" -O "$PLUGIN_PATH/plugin.py"
wget --no-check-certificate "$GITHUB_RAW/__init__.py" -O "$PLUGIN_PATH/__init__.py"

# تحميل اللوجو إذا قمت برفعه لاحقاً في الريبو
wget --no-check-certificate "$GITHUB_RAW/plugin.png" -O "$PLUGIN_PATH/plugin.png" 2>/dev/null

# إعطاء التصاريح اللازمة للتشغيل
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
