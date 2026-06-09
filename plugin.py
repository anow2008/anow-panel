# -*- coding: utf-8 -*-
# ==============================================================================
# Plugin: anow panel v1.0
# Developed by: anow2008
# Compatible with: Python 3 & OpenATV 7.6 (Luxury FHD Skin)
# Description: الإصدار الذهبي النهائي - فصل ذكي وصارم بين أسماء السكريبتات وأوامر التنفيذ
# ==============================================================================

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

# مكتبات العرض المتوافقة مع بايثون 3 لصور OpenATV الحديثة
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont, loadPNG
import urllib.request
import os

# ------------------------------------------------------------------------------
# إعدادات المسارات والأيقونات
# ------------------------------------------------------------------------------
PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS, "Extensions/anow_panel/")
ICON_FOLDER = os.path.join(PLUGIN_PATH, "icons")

def build_menu_item(title, is_folder=True):
    """
    بناء سطر القائمة الاحترافي (الأيقونة + النص) متوافق مع بايثون 3
    """
    if is_folder:
        clean_title = title.strip()
        icon_path = os.path.join(ICON_FOLDER, f"{clean_title}.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(ICON_FOLDER, "folder.png")
    else:
        icon_path = os.path.join(ICON_FOLDER, "script.png")
        
    png = loadPNG(icon_path)
    res = [title]
    res.append(MultiContentEntryPixmapAlphaTest(pos=(15, 7), size=(32, 32), png=png))
    res.append(MultiContentEntryText(pos=(60, 2), size=(900, 40), font=0, text=title, flags=0))
    return res


# ------------------------------------------------------------------------------
# الشاشة الرئيسية للبلجن
# ------------------------------------------------------------------------------
class AnowPanelMainScreen(Screen):
    skin = """
    <screen position="center,center" size="1100,650" title="anow panel v1.0" backgroundColor="#0f172a" flags="wfNoBorder">
        <eLabel position="0,0" size="1100,650" backgroundColor="#0f172a" zPosition="-1" />
        <eLabel position="5,5" size="1090,640" backgroundColor="#1e293b" zPosition="0" />
        
        <eLabel position="20,20" size="1060,60" backgroundColor="#0f172a" />
        <widget name="title_label" position="30,25" size="1040,50" font="Regular; 24" halign="center" valign="center" foregroundColor="#22c55e" backgroundColor="#0f172a" transparent="1" zPosition="2" />
        
        <eLabel position="20,90" size="1060,3" backgroundColor="#06b6d4" />
        
        <widget name="menu_list" position="40,110" size="1020,440" scrollbarMode="showOnDemand" foregroundColor="#ffffff" backgroundColor="#1e293b" selectionColor="#06b6d4" selectionForegroundColor="#ffffff" transparent="0" zPosition="2" />
        
        <eLabel position="20,565" size="1060,2" backgroundColor="#334155" />
        <widget name="hint_label" position="30,580" size="1040,40" font="Regular; 18" halign="left" valign="center" foregroundColor="#94a3b8" backgroundColor="#1e293b" transparent="1" zPosition="2" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        self["title_label"] = Label("anow panel — جاري جلب الأقسام والبيانات...")
        self["hint_label"] = Label("يرجى الانتظار ثواني...")
        
        self.menu_data = {}
        self.main_menu = []
        self.current_menu = "main"
        self.active_section = ""
        
        self["menu_list"] = MenuList([])
        
        # حماية وضبط خطوط القائمة لصور OpenATV الحديثة
        try:
            self["menu_list"].list.setFont(0, gFont("Regular", 23))
            self["menu_list"].list.setItemHeight(45)
        except:
            try:
                self["menu_list"].l.setFont(0, gFont("Regular", 23))
                self["menu_list"].l.setItemHeight(45)
            except:
                pass
        
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
            
            # تنظيف وتجهيز السطور الفعلية فقط من الفراغات
            clean_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    clean_lines.append(line)
            
            # معالجة ذكية جداً لفصل الاسم عن الأمر
            i = 0
            while i < len(clean_lines):
                line = clean_lines[i]
                
                # 1. رصد الأقسام الرئيسية (التي تحتوي على أسطر الزخرفة الطويلة مثل ———— أو ★★★)
                if "————" in line or "★★★" in line or "●●" in line or "||" in line:
                    clean_section = line.replace("————", "").replace("★★★", "").replace("●●", "").replace("★", "").replace("::", "").replace("|", "").strip()
                    if clean_section:
                        current_section = clean_section
                        if current_section not in self.menu_data:
                            self.menu_data[current_section] = []
                            display_item = build_menu_item(current_section, is_folder=True)
                            self.main_menu.append((current_section, display_item))
                    i += 1
                    continue
                
                # 2. رصد السكريبتات والأوامر داخل القسم الحالي
                if current_section:
                    # فحص إذا كان السطر الحالي يمثل أمراً (يبدأ بكلمات النظام الشهيرة)
                    is_cmd = any(line.lower().startswith(c) for c in ["opkg", "wget", "rm", "init", "cd", "curl", "chmod"])
                    
                    if not is_cmd:
                        # هذا سطر "اسم السكريبت" (مثل: ★[ تثبيت ايمو سيسكام ]★)
                        script_name = line
                        
                        # نتحقق من السطر التالي مباشرة لمعرفة هل هو الأمر الخاص به؟
                        if (i + 1) < len(clean_lines):
                            next_line = clean_lines[i+1]
                            is_next_cmd = any(next_line.lower().startswith(c) for c in ["opkg", "wget", "rm", "init", "cd", "curl", "chmod"])
                            
                            if is_next_cmd:
                                # ممتاز! وجدنا الاسم وتحته أمره الصافي مباشرة
                                display_item = build_menu_item(script_name, is_folder=False)
                                self.menu_data[current_section].append((script_name, next_line, display_item))
                                i += 2 # نتخطى السطرين لأننا سحبنا الاسم والأمر معاً
                                continue
                    else:
                        # لو السطر طلع أمر مباشر بدون اسم فوقه، نخليه هو الاسم والأمر معاً للامان
                        display_item = build_menu_item(line[:50] + "...", is_folder=False)
                        self.menu_data[current_section].append((line[:50] + "...", line, display_item))
                
                i += 1

            # عرض الأقسام الرئيسية
            if self.main_menu:
                self["menu_list"].setList([item[1] for item in self.main_menu])
                self["title_label"].setText("ANOW PANEL — الأقسام الرئيسية")
                self["hint_label"].setText("📡 اختر القسم واضغط OK للدخول | Cancel للخروج")
            else:
                self["title_label"].setText("⚠ ملف ajpanel_cmd فارغ أو تنسيقه غير متوافق")
            
        except Exception as e:
            self["title_label"].setText("❌ فشل جلب البيانات!")
            self["hint_label"].setText(str(e))

    def ok_pressed(self):
        selected_idx = self["menu_list"].getSelectedIndex()
        if selected_idx is None:
            return

        if self.current_menu == "main":
            self.active_section = self.main_menu[selected_idx][0]
            if self.active_section in self.menu_data and self.menu_data[self.active_section]:
                self.current_menu = "sub"
                self["title_label"].setText("قسم: " + self.active_section)
                self["hint_label"].setText("⚡ اضغط OK لتشغيل السكريبت فوراً | Cancel للعودة للخلف")
                self["menu_list"].setList([item[2] for item in self.menu_data[self.active_section]])
            else:
                self.session.open(MessageBox, "هذا القسم لا يحتوي على أوامر لينكس صالحة للتنفيذ!", MessageBox.TYPE_INFO)
        else:
            sub_list = self.menu_data[self.active_section]
            selection_name = sub_list[selected_idx][0]
            selection_target = sub_list[selected_idx][1]
            self.execute_command(selection_name, selection_target)

    def execute_command(self, name, cmd):
        try:
            from Screens.Console import Console
            clean_cmd = str(cmd).strip()
            # الآن نرسل أمر اللينكس الحقيقي الصافي 100% للكونسول
            self.session.open(Console, title=str(name), cmdlist=[clean_cmd])
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
        description="لوحة التحكم الذكية والإصدار الاحترافي المطور لـ anow2008 بالأيقونات", 
        where=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
