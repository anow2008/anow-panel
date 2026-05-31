# -*- coding: utf-8 -*-
# anow panel for Enigma2 (Python 3 & Luxury FHD Skin)
# تم حل مشكلة الـ TypeError وفصل الأمر عن الاسم بنجاح لصور OpenATV

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Console import Console
from Screens.MessageBox import MessageBox
import urllib.request

class AnowPanelMainScreen(Screen):
    skin = """
    <screen position="center,center" size="1100,650" title="anow panel v1.0" backgroundColor="#0f172a" flags="wfNoBorder">
        <eLabel position="0,0" size="1100,650" backgroundColor="#0f172a" zPosition="-1" />
        <eLabel position="5,5" size="1090,640" backgroundColor="#1e293b" zPosition="0" />
        
        <eLabel position="20,20" size="1060,60" backgroundColor="#0f172a" />
        <widget name="title_label" position="30,25" size="1040,50" font="Regular; 24" halign="center" valign="center" foregroundColor="#22c55e" backgroundColor="#0f172a" transparent="1" zPosition="2" />
        
        <eLabel position="20,90" size="1060,3" backgroundColor="#06b6d4" />
        
        <widget name="menu_list" position="40,110" size="1020,440" scrollbarMode="showOnDemand" font="Regular; 22" itemHeight="45" foregroundColor="#ffffff" backgroundColor="#1e293b" selectionColor="#06b6d4" selectionForegroundColor="#ffffff" transparent="0" zPosition="2" />
        
        <eLabel position="20,565" size="1060,2" backgroundColor="#334155" />
        <widget name="hint_label" position="30,580" size="1040,40" font="Regular; 18" halign="left" valign="center" foregroundColor="#94a3b8" backgroundColor="#1e293b" transparent="1" zPosition="2" />
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
        
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
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
                
                if any(x in line for x in ["★", "●", "||", "————"]):
                    clean_section = line.replace("————", "").replace("★★★", "").replace("●●", "").replace("★", "").replace("::", "").replace("|", "").strip()
                    if clean_section:
                        current_section = clean_section
                        if current_section not in self.menu_data:
                            self.menu_data[current_section] = []
                            self.main_menu.append((current_section, current_section))
                    continue
                
                if current_section:
                    if any(line.startswith(cmd) for cmd in ["opkg", "wget", "rm", "init", "cd", "curl", "chmod"]):
                        name = current_item_name if current_item_name else line
                        # حفظ البيانات كـ Tuple (الاسم المعروض، الأمر الحقيقي للينكس)
                        self.menu_data[current_section].append((name, line))
                        current_item_name = ""
                    else:
                        current_item_name = line

            if self.main_menu:
                self["menu_list"].setList(self.main_menu)
                self["title_label"].setText("ANOW PANEL — القائمة الرئيسية")
                self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | Cancel للخروج")
            else:
                self["title_label"].setText("⚠ تم جلب الملف ولكنه فارغ أو منسق بشكل خاطئ")
                self["hint_label"].setText("تأكد من وجود أقسام وأوامر داخل ملف ajpanel_cmd")
            
        except Exception as e:
            self["title_label"].setText("❌ فشل الاتصال بالسيرفر وجلب البيانات!")
            self["hint_label"].setText(str(e))

    def ok_pressed(self):
        selected = self["menu_list"].getCurrent()
        if not selected:
            return

        # هنا تم الإصلاح: selected يعيد التوبل الحالي المختار من القائمة
        selection_name = selected[0]
        selection_target = selected[1]

        if self.current_menu == "main":
            if selection_target in self.menu_data and self.menu_data[selection_target]:
                self.current_menu = "sub"
                self["title_label"].setText("قسم: " + str(selection_name))
                self["hint_label"].setText("⚡ اضغط OK لتشغيل السكريبت فوراً | Cancel للعودة للخلف")
                self["menu_list"].setList(self.menu_data[selection_target])
        else:
            # داخل القائمة الفرعية، الاختيار يحتوي على (اسم السكريبت، أمر اللينكس النصي)
            # نقوم بتمرير السلسلة النصية الصافية للأمر هنا
            self.execute_command(str(selection_name), str(selection_target))

    def execute_command(self, name, cmd):
        # صياغة آمنة للرسالة بدون تداخل كائنات بايثون
        msg_text = "جاري تشغيل السكريبت بالخلفية:\n" + name + "\n\nيرجى الانتظار ثواني..."
        self.session.openWithCallback(
            self.command_finished, 
            MessageBox, 
            msg_text, 
            MessageBox.TYPE_INFO, 
            timeout=4
        )
        # تنفيذ الأمر النصي الصافي في التلنت بالخلفية
        self.console.execute(cmd)

    def command_finished(self, answer=None):
        self.session.open(MessageBox, "✅ تم إرسال الأمر للنظام بنجاح!", MessageBox.TYPE_INFO, timeout=3)

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
        where=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
