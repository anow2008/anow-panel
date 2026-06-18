# -*- coding: utf-8 -*-
# anow panel for Enigma2 (Python 3 & Luxury FHD Skin)
# معالج ذكي ومخصص لقراءة ملف ajpanel_cmd الخاص بـ anow2008 بدون تعديل

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
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
        
        self["title_label"] = Label("anow panel — جاري سحب البيانات وتقسيم الأقسام...")
        self["hint_label"] = Label("يرجى الانتظار ثواني...")
        
        self.menu_data = {}
        self.main_menu = []
        self.current_menu = "main"
        self["menu_list"] = MenuList([])
        
        self["actions"] = ActionMap(["SetupActions"], {
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
            temp_name = ""
            
            for line in lines:
                line = line.strip()
                
                # 1. تخطي الأسطر الفارغة أو الأسطر المليئة بالنقاط فقط (الفواصل)
                if not line or (line.startswith("●") and len(line) > 10):
                    continue
                
                # 2. التعرف على الأقسام الرئيسية المفرغة المحتوية على الفواصل والأشرطة والمحصورة بـ |
                if "————" in line or "::|" in line or ("|" in line and ("★" in line or "●" in line)):
                    clean_section = line.replace("————", "").replace("★★★", "").replace("●●", "").replace("★", "").replace("::", "").replace("|", "").strip()
                    if clean_section:
                        current_section = clean_section
                        if current_section not in self.menu_data:
                            self.menu_data[current_section] = []
                            self.main_menu.append((current_section, current_section))
                    continue
                
                # 3. معالجة الأوامر والنصوص داخل الأقسام
                if current_section:
                    # تنظيف النجوم من أسطر الأسماء مثل ★★★ ArabicSavior ★★★
                    if line.startswith("★") and line.endswith("★"):
                        temp_name = line.replace("★★★", "").replace("★", "").strip()
                        continue
                    
                    # إذا كان السطر يحتوي على جزء تعليق (مثال: init 0 # Deep Standby) نأخذه كأمر مباشر
                    if "#" in line and any(line.split("#")[0].strip().startswith(cmd) for cmd in ["init", "reboot"]):
                        cmd_part = line.split("#")[0].strip()
                        name_part = line.strip()
                        self.menu_data[current_section].append((name_part, cmd_part))
                        temp_name = ""
                        continue

                    # معالجة ذكية: أي سطر ليس قسماً وليس عنواناً صريحاً بالنجوم، هو أمر تنفيذي فوراً
                    # هذا يضمن قراءة الأوامر التي تبدأ بمتغيرات مثل MS="" أو غيرها بدون تقييد بكلمات محددة
                    name = temp_name if temp_name else line
                    self.menu_data[current_section].append((name, line))
                    temp_name = ""  # تصفير الاسم المؤقت بعد التعيين للأمر

            # إذا تم العثور على أقسام، اعرض القائمة الرئيسية
            if self.main_menu:
                self["menu_list"].setList(self.main_menu)
                self["title_label"].setText("ANOW PANEL — الأقسام الرئيسية")
                self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | Cancel للخروج")
            else:
                self["title_label"].setText("⚠ لم يتم تقسيم الملف بشكل صحيح")
                self["hint_label"].setText("تأكد من مطابقة صيغة الملف")
            
        except Exception as e:
            self["title_label"].setText("❌ فشل الاتصال بالسيرفر وجلب البيانات!")
            self["hint_label"].setText(str(e))

    def ok_pressed(self):
        selected = self["menu_list"].getCurrent()
        if not selected:
            return

        selection_name = str(selected[0])
        selection_target = str(selected[1])

        if self.current_menu == "main":
            # فتح القسم الفرعي
            if selection_target in self.menu_data and self.menu_data[selection_target]:
                self.current_menu = "sub"
                self["title_label"].setText("قسم: " + selection_name)
                self["hint_label"].setText("⚡ اضغط OK لتشغيل السكريبت فوراً | Cancel للعودة للخلف")
                self["menu_list"].setList(self.menu_data[selection_target])
        else:
            # تشغيل الأمر الفعلي المتواجد بالملف عبر الكونسول
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
            self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | Cancel للخروج")
            self["menu_list"].setList(self.main_menu)
        else:
            self.close()

def main(session, **kwargs):
    session.open(AnowPanelMainScreen)

def Plugins(**kwargs):
    return PluginDescriptor(
        name="anow panel", 
        description="لوحة التحكم الذكية والإصدار المتطور لـ anow2008", 
        where=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
