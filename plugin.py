# -*- coding: utf-8 -*-
# anow panel for Enigma2 (Python 3 & Luxury FHD Skin)
# معالج ذكي ومخصص لقراءة ملف ajpanel_cmd الخاص بـ anow2008 بدون تعديل مع دعم الأيقونات الديناميكية لأسماء الأقسام

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Enigma2.Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont, loadPNG
import urllib.request
import os

# تحديد مسار الأيقونات داخل مجلد البلجن
PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS, "Extensions/anow_panel/")
ICON_FOLDER = os.path.join(PLUGIN_PATH, "icons")

# دالة ذكية تبحث عن أيقونة مطابقة لاسم القسم الفعلي (بما يشمل الأقواس والمسافات)
def build_menu_item(title, is_folder=True):
    if is_folder:
        # تنظيف الفراغات الخارجية فقط مع الإبقاء على الأقواس والمسافات الداخلية كما هي بالملف
        clean_title = title.strip()
        icon_path = os.path.join(ICON_FOLDER, f"{clean_title}.png")
        
        # إذا لم يجد الأيقونة المخصصة للقسم، يتم استخدام أيقونة المجلد الافتراضية
        if not os.path.exists(icon_path):
            icon_path = os.path.join(ICON_FOLDER, "folder.png")
    else:
        # أيقونة موحدة للأوامر والسكريبتات الداخلية
        icon_path = os.path.join(ICON_FOLDER, "execute.png")
        
    # احتياط نهائي في حال عدم وجود المجلد أو الصور الافتراضية لعدم حدوث كراش
    if not os.path.exists(icon_path):
        icon_path = os.path.join(PLUGIN_PATH, "plugin.png")
        
    res = [title] # القيمة الراجعة عند التحديد
    
    # رسم الأيقونة ونص الخيار وتنسيق الأبعاد بدقة لتناسب الـ Luxury FHD Skin
    res.append(MultiContentEntryPixmapAlphaTest(pos=(15, 7), size=(32, 32), png=loadPNG(icon_path)))
    res.append(MultiContentEntryText(pos=(60, 2), size=(900, 40), font=0, text=title, flags=0))
    
    return res

class AnowPanelMainScreen(Screen):
    skin = """
    <screen position="center,center" size="1100,650" title="anow panel v1.0" backgroundColor="#0f172a" flags="wfNoBorder">
        <eLabel position="0,0" size="1100,650" backgroundColor="#0f172a" zPosition="-1" />
        <eLabel position="5,5" size="1090,640" backgroundColor="#1e293b" zPosition="0" />
        
        <eLabel position="20,20" size="1060,60" backgroundColor="#0f172a" />
        <widget name="title_label" position="30,25" size="1040,50" font="Regular; 24" halign="center" valign="center" foregroundColor="#22c55e" backgroundColor="#0f172a" transparent="1" zPosition="2" />
        
        <eLabel position="20,90" size="1060,3" backgroundColor="#06b6d4" />
        
        <widget name="menu_list" position="40,110" size="1020,440" scrollbarMode="showOnDemand" backgroundColor="#1e293b" selectionColor="#06b6d4" transparent="0" zPosition="2" />
        
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
        self.active_section = ""
        
        # ضبط إعدادات القائمة والخطوط والأبعاد للأسطر
        self["menu_list"] = MenuList([])
        self["menu_list"].l.setFont(0, gFont("Regular", 22))
        self["menu_list"].l.setItemHeight(45)
        
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
                
                if not line or (line.startswith("●") and len(line) > 10):
                    continue
                
                # فحص الأسطر المخصصة للأقسام وتنظيف العلامات المحيطة بها فقط
                if "————" in line or "::|" in line or ("|" in line and ("★" in line or "●" in line)):
                    clean_section = line.replace("————", "").replace("★★★", "").replace("●●", "").replace("★", "").replace("::", "").replace("|", "").strip()
                    if clean_section:
                        current_section = clean_section
                        if current_section not in self.menu_data:
                            self.menu_data[current_section] = []
                            # حفظ الاسم النظيف وبناء السطر بأيقونته الخاصة
                            self.main_menu.append((current_section, build_menu_item(current_section, is_folder=True)))
                    continue
                
                if current_section:
                    clean_line = line.replace("★★★", "").replace("★", "").strip()
                    
                    if any(line.startswith(cmd) for cmd in ["opkg", "wget", "rm", "init", "cd", "curl", "chmod", "reboot", "sleep"]):
                        name = temp_name if temp_name else line
                        self.menu_data[current_section].append((name, line, build_menu_item(name, is_folder=False)))
                        temp_name = ""
                    else:
                        if "#" in line and any(line.split("#")[0].strip().startswith(cmd) for cmd in ["init", "reboot"]):
                            cmd_part = line.split("#")[0].strip()
                            name_part = line.strip()
                            self.menu_data[current_section].append((name_part, cmd_part, build_menu_item(name_part, is_folder=False)))
                        else:
                            temp_name = clean_line

            if self.main_menu:
                # عرض القائمة الرئيسية بالأيقونات الذكية
                self["menu_list"].setList([item[1] for item in self.main_menu])
                self["title_label"].setText("ANOW PANEL — الأقسام الرئيسية")
                self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | Cancel للخروج")
            else:
                self["title_label"].setText("⚠ لم يتم تقسيم الملف بشكل صحيح")
                self["hint_label"].setText("تأكد من مطابقة صيغة الملف")
            
        except Exception as e:
            self["title_label"].setText("❌ فشل الاتصال بالسيرفر وجلب البيانات!")
            self["hint_label"].setText(str(e))

    def ok_pressed(self):
        selected_idx = self["menu_list"].getSelectedIndex()
        if selected_idx is None:
            return

        if self.current_menu == "main":
            # الانتقال للقسم الفرعي وحفظ القسم النشط للاعتماد عليه عند الضغط التالي
            self.active_section = self.main_menu[selected_idx][0]
            if self.active_section in self.menu_data and self.menu_data[self.active_section]:
                self.current_menu = "sub"
                self["title_label"].setText("قسم: " + self.active_section)
                self["hint_label"].setText("⚡ اضغط OK لتشغيل السكريبت فوراً | Cancel للعودة للخلف")
                self["menu_list"].setList([item[2] for item in self.menu_data[self.active_section]])
        else:
            # تشغيل الأمر المختار من داخل القسم الحالي
            sub_list = self.menu_data[self.active_section]
            selection_name = sub_list[selected_idx][0]
            selection_target = sub_list[selected_idx][1]
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
            self["menu_list"].setList([item[1] for item in self.main_menu])
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
