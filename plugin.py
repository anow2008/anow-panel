# -*- coding: utf-8 -*-
# anow panel for Enigma2 (Python 3 & Luxury FHD Skin)

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from twisted.web.client import getPage

class AnowPanelMainScreen(Screen):
    skin = """
    <screen position="center,center" size="1100,650" title="anow panel v2.0" backgroundColor="#0f172a" flags="wfNoBorder">
        <eLabel position="0,0" size="1100,650" backgroundColor="#0f172a" zPosition="-1" />
        <eLabel position="5,5" size="1090,640" backgroundColor="#1e293b" zPosition="0" />
        
        <!-- Header -->
        <eLabel position="20,15" size="1060,60" backgroundColor="#0f172a" />
        <widget name="title_label" position="30,20" size="1040,50" font="Regular; 24" halign="center" valign="center" foregroundColor="#38bdf8" backgroundColor="#0f172a" transparent="1" zPosition="2" />
        
        <eLabel position="20,80" size="1060,3" backgroundColor="#06b6d4" />
        
        <!-- List -->
        <widget name="menu_list" position="40,95" size="1020,460" scrollbarMode="showOnDemand" font="Regular; 22" itemHeight="45" foregroundColor="#ffffff" backgroundColor="#1e293b" selectionColor="#06b6d4" selectionForegroundColor="#ffffff" transparent="0" zPosition="2" />
        
        <eLabel position="20,565" size="1060,2" backgroundColor="#334155" />
        
        <!-- Status -->
        <widget name="hint_label" position="30,575" size="1040,30" font="Regular; 18" halign="left" valign="center" foregroundColor="#94a3b8" backgroundColor="#1e293b" transparent="1" zPosition="2" />
        
        <!-- Buttons -->
        <eLabel position="30,612" size="20,20" backgroundColor="#ef4444" zPosition="2" />
        <widget name="key_red" position="60,608" size="200,25" font="Regular; 16" halign="left" valign="center" foregroundColor="#ffffff" backgroundColor="#1e293b" transparent="1" zPosition="2" />
        
        <eLabel position="270,612" size="20,20" backgroundColor="#22c55e" zPosition="2" />
        <widget name="key_green" position="300,608" size="200,25" font="Regular; 16" halign="left" valign="center" foregroundColor="#ffffff" backgroundColor="#1e293b" transparent="1" zPosition="2" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        self["title_label"] = Label("ANOW PANEL v2.0 — جاري الاتصال بالسيرفر...")
        self["hint_label"] = Label("⏳ يرجى الانتظار جاري جلب الأوامر والأقسام...")
        self["key_red"] = Label("خروج (Exit)")
        self["key_green"] = Label("تحديث (Refresh)")
        
        self.menu_data = {}
        self.main_menu = []
        self.current_menu = "main"
        self["menu_list"] = MenuList([])
        
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "ok": self.ok_pressed,
            "cancel": self.cancel_pressed,
            "red": self.close,
            "green": self.fetch_github_data
        }, -1)
        
        self.onLayoutFinish.append(self.fetch_github_data)

    def fetch_github_data(self):
        self["title_label"].setText("ANOW PANEL v2.0 — جاري جلب البيانات...")
        self["hint_label"].setText("⏳ جاري التحميل من GitHub...")
        self["menu_list"].setList([])
        
        url = b"https://raw.githubusercontent.com/anow2008/ajpanel_cmd/refs/heads/main/ajpanel_cmd"
        getPage(url, timeout=10, headers={b'User-Agent': b'Enigma2 AnowPanel'}).addCallback(self.parse_data).addErrback(self.fetch_failed)

    def parse_data(self, data):
        try:
            content = data.decode('utf-8', errors='ignore')
            lines = content.split('\n')
            
            self.menu_data = {}
            self.main_menu = []
            current_section = None
            temp_name = ""
            
            for line in lines:
                line = line.strip()
                
                if not line or (line.startswith("●") and len(line) > 10):
                    continue
                
                if "————" in line or "::|" in line or ("|" in line and ("★" in line or "●" in line)):
                    clean_section = line.replace("————", "").replace("★★★", "").replace("●●", "").replace("★", "").replace("::", "").replace("|", "").strip()
                    if clean_section:
                        current_section = clean_section
                        if current_section not in self.menu_data:
                            self.menu_data[current_section] = []
                            self.main_menu.append((current_section, current_section))
                    continue
                
                if current_section:
                    if line.startswith("★") and line.endswith("★"):
                        temp_name = line.replace("★★★", "").replace("★", "").strip()
                        continue
                    
                    if "#" in line and any(line.split("#")[0].strip().startswith(cmd) for cmd in ["init", "reboot"]):
                        cmd_part = line.split("#")[0].strip()
                        name_part = line.strip()
                        self.menu_data[current_section].append((name_part, cmd_part))
                        temp_name = ""
                        continue

                    name = temp_name if temp_name else line
                    self.menu_data[current_section].append((name, line))
                    temp_name = ""

            if self.main_menu:
                self.current_menu = "main"
                self["menu_list"].setList(self.main_menu)
                self["menu_list"].moveToIndex(0)  # الوقوف تلقائياً على أول قسم
                self["title_label"].setText("ANOW PANEL — الأقسام الرئيسية")
                self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | الأخضر للتحديث | Red/Exit للخروج")
            else:
                self["title_label"].setText("⚠ تنبيه")
                self["hint_label"].setText("لم يتم العثور على أية أقسام في الملف النصي!")

        except Exception as e:
            self["title_label"].setText("❌ خطأ أثناء قراءة البيانات")
            self["hint_label"].setText(str(e))

    def fetch_failed(self, error):
        self["title_label"].setText("❌ فشل الاتصال بالسيرفر!")
        self["hint_label"].setText("تأكد من إعدادات الشبكة أو الرابط (اضغط الأخضر لإعادة المحاولة)")

    def ok_pressed(self):
        selected = self["menu_list"].getCurrent()
        if not selected:
            return

        selection_name = str(selected[0])
        selection_target = str(selected[1])

        if self.current_menu == "main":
            if selection_target in self.menu_data and self.menu_data[selection_target]:
                self.current_menu = "sub"
                self["title_label"].setText("قسم: " + selection_name)
                self["hint_label"].setText("⚡ اضغط OK لتشغيل السكريبت فوراً | Cancel للعودة للأقسام")
                self["menu_list"].setList(self.menu_data[selection_target])
                self["menu_list"].moveToIndex(0)  # الوقوف تلقائياً على أول عنصر داخل القسم الفرعي
        else:
            self.execute_command(selection_name, selection_target)

    def execute_command(self, name, cmd):
        try:
            from Screens.Console import Console
            self.session.open(Console, title=str(name), cmdlist=[str(cmd).strip()])
        except Exception as e:
            self.session.open(MessageBox, "خطأ أثناء التنفيذ: " + str(e), MessageBox.TYPE_ERROR)

    def cancel_pressed(self):
        if self.current_menu == "sub":
            self.current_menu = "main"
            self["title_label"].setText("ANOW PANEL — الأقسام الرئيسية")
            self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | Red/Exit للخروج")
            self["menu_list"].setList(self.main_menu)
            self["menu_list"].moveToIndex(0)  # الوقوف على أول قسم عند العودة
        else:
            self.close()

def main(session, **kwargs):
    session.open(AnowPanelMainScreen)

def Plugins(**kwargs):
    return PluginDescriptor(
        name="anow panel", 
        description="لوحة التحكم الذكية v2.0 - الإصدار المتطور لـ anow2008", 
        where=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
