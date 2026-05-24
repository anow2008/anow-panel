# -*- coding: utf-8 -*-
# anow panel for Enigma2 (Python 3 & Luxury FHD Skin)
# المصدر: القراءة الديناميكية من GitHub بتصميم احترافي متطور

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Console import Console
from Screens.MessageBox import MessageBox
import urllib.request

class AnowPanelMainScreen(Screen):
    # تصميم احترافي مودرن (فول اتش دي FHD 1920x1080) متناسق ومريح للعين
    skin = """
    <screen position="center,center" size="1100,650" title="anow panel v1.0" backgroundColor="#0f172a" flags="wfNoBorder">
        <eLabel position="0,0" size="1100,650" backgroundColor="#0f172a" zPosition="-1" />
        <eLabel position="5,5" size="1090,640" backgroundColor="#1e293b" zPosition="0" />
        
        # 
        <eLabel position="20,20" size="1060,60" backgroundColor="#0f172a" />
        <widget name="title_label" position="30,25" size="1040,50" font="Regular; 26" halign="center" valign="center" foregroundColor="#22c55e" backgroundColor="#0f172a" transparent="1" />
        
        <eLabel position="20,90" size="1060,3" backgroundColor="#06b6d4" />
        
        <widget name="menu_list" position="30,110" size="1040,440" scrollbarMode="showOnDemand" font="Regular; 23" itemHeight="45" foregroundColor="#ffffff" backgroundColor="#1e293b" selectionColor="#06b6d4" selectionForegroundColor="#ffffff" transparent="1" />
        
        <eLabel position="20,565" size="1060,2" backgroundColor="#334155" />
        <widget name="hint_label" position="30,580" size="1040,40" font="Regular; 18" halign="left" valign="center" foregroundColor="#94a3b8" backgroundColor="#1e293b" transparent="1" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.console = Console()
        
        self["title_label"] = Label("anow panel — جاري سحب البيانات من السيرفر...")
        self["hint_label"] = Label("يرجى الانتظار ثواني...")
        
        self.menu_data = {}
        self.main_menu = []
        self.current_menu = "main"
        self["menu_list"] = MenuList([])
        
        self["actions"] = ActionMap(["OkCancelActions"], {
            "ok": self.ok_pressed,
            "cancel": self.cancel_pressed
        }, -1)
        
        self.onLayoutFinish.append(self.fetch_github_data)

    def fetch_github_data(self):
        url = "https://raw.githubusercontent.com/anow2008/ajpanel_cmd/refs/heads/main/ajpanel_cmd"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
            
            lines = content.split('\n')
            current_section = None
            current_item_name = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "★★★" in line and "||" in line:
                    clean_section = line.replace("————★★★|", "").replace("|★★★————", "").strip()
                    current_section = clean_section
                    self.menu_data[current_section] = []
                    self.main_menu.append((current_section, current_section))
                elif "————●●★::|" in line:
                    clean_section = line.replace("————●●★::|", "").replace("|::★●●————", "").replace("|::★●●", "").strip()
                    current_section = clean_section
                    self.menu_data[current_section] = []
                    self.main_menu.append((current_section, current_section))
                
                elif current_section:
                    if line.startswith("★★★") and line.endswith("★★★"):
                        current_item_name = line.replace("★★★", "").strip()
                    elif line.startswith("opkg") or line.startswith("wget") or line.startswith("rm") or line.startswith("init") or line.startswith("cd"):
                        name = current_item_name if current_item_name else line
                        self.menu_data[current_section].append((name, line))
                        current_item_name = ""
                    elif line.startswith("OpenATV") or line.startswith("openpli"):
                        current_item_name = line
            
            self["menu_list"].setList(self.main_menu)
            self["title_label"].setText("ANOW PANEL — القائمة الرئيسية")
            self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | Cancel للخروج")
            
        except Exception as e:
            self["title_label"].setText("❌ فشل الاتصال بالسيرفر وجلب البيانات!")
            self["hint_label"].setText("تأكد من وجود إنترنت نشط في الرسيفر ثم أعد فتح البانل.")

    def ok_pressed(self):
        selected = self["menu_list"].getCurrent()
        if not selected:
            return

        selection_name = selected[0]
        selection_target = selected[1]

        if self.current_menu == "main":
            if selection_target in self.menu_data and self.menu_data[selection_target]:
                self.current_menu = "sub"
                self["title_label"].setText("قسم: %s" % selection_name)
                self["hint_label"].setText("⚡ اضغط OK لتشغيل السكريبت فوراً | Cancel للعودة للخلف")
                self["menu_list"].setList(self.menu_data[selection_target])
        else:
            self.execute_command(selection_name, selection_target)

    def execute_command(self, name, cmd):
        self.session.openWithCallback(
            self.command_finished, 
            MessageBox, 
            ("جاري تشغيل السكريبت بالخلفية:\n%s\n\nيرجى الانتظار قليلاً..." % name), 
            MessageBox.TYPE_INFO, 
            timeout=5
        )
        self.console.execute(cmd)

    def command_finished(self, answer=None):
        self.session.open(MessageBox, "✅ تم تنفيذ السكريبت والأمر بنجاح!", MessageBox.TYPE_INFO, timeout=3)

    def cancel_pressed(self):
        if self.current_menu == "sub":
            self.current_menu = "main"
            self["title_label"].setText("ANOW PANEL — القائمة الرئيسية")
            self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | Cancel للخروج")
            self["menu_list"].setList(self.main_menu)
        else:
            self.close()

def main(session, **kwargs):
    session.open(AnowPanelMainScreen)

def Plugins(**kwargs):
    return PluginDescriptor(
        name="anow panel", 
        description="لوحة التحكم الذكية والإصدار الاحترافي المطور لـ anow2008", 
        whereabouts=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
