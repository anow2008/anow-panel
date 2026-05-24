#!/bin/sh
#  anow panel installation script
#  Python 3 Compatible

# 1. تحديد المسارات واسم البلجن
PLUGIN_NAME="anowpanel"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"
GITHUB_RAW="https://raw.githubusercontent.com/anow2008/ajpanel_cmd/main"

echo "================================================="
echo "   Welcome to anow panel Installer (Python 3)   "
echo "================================================="
echo "STATION: Preparing system for installation..."

# 2. حذف أي نسخة قديمة وتجهيز المجلد الجديد
rm -rf $PLUGIN_PATH
mkdir -p $PLUGIN_PATH

echo "STATUS: Downloading anow panel files from GitHub..."

# 3. تحميل ملفات البلجن الأساسية من الجيت هاب بتاعك
# ملحوظة: تأكد من رفع ملفات plugin.py و __init__.py في الريبو الأساسي
wget --no-check-certificate "$GITHUB_RAW/plugin.py" -O "$PLUGIN_PATH/plugin.py"
wget --no-check-certificate "$GITHUB_RAW/__init__.py" -O "$PLUGIN_PATH/__init__.py"

# تحميل اللوجو (إذا كان متوفراً في الريبو)
wget --no-check-certificate "$GITHUB_RAW/plugin.png" -O "$PLUGIN_PATH/plugin.png" 2>/dev/null

# 4. إعطاء التصاريح الصحيحة للملفات لتعمل بدون مشاكل
chmod -R 755 $PLUGIN_PATH

echo "================================================="
echo "       anow panel installed successfully!        "
echo "================================================="
echo "STATION: Restarting Enigma2 to apply changes..."
echo "================================================="

# 5. عمل ريستارت للأنيجما بناءً على نوع الصورة ليتعرف الجهاز على البانل
sleep 2
if [ -f /etc/init.d/enigma2 ]; then
    /etc/init.d/enigma2 restart
elif [ -f /usr/bin/cammanager ]; then
    init 4 && init 3
else
    killall -9 enigma2
fi

exit 0
