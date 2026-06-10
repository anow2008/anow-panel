# -*- coding: utf-8 -*-
# ==============================================================================
# Plugin: anow panel v1.0
# Developed by: anow2008
# Compatible with: Python 3 & OpenATV 7.6 (Luxury FHD Skin)
# Description: Fixed <not-a-string> issue for OpenATV 7.6 / Python 3
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
    بناء سطر القائمة الاحترافي المتوافق مع بايثون 3 وصور OpenATV الحديثة.
    يعيد Tuple يحتوي على العنوان أولاً، ثم قائمة بمكونات الرسم (الأيقونة والنص).
    """
    if is_folder:
        clean_title = title.strip()
        icon_path = os.path.join(ICON_FOLDER, f"{clean_title}.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(ICON_FOLDER, "folder.png")
    else:
        icon_path = os.path.join(ICON_FOLDER, "script.png")
        
    png = loadPNG(icon_path)
    
    # قائمة مكونات الرسم فقط داخل السطر
    components = [
        MultiContentEntryPixmapAlphaTest(pos=(15, 7), size=(32, 32), png=png),
        MultiContentEntryText(pos=(60, 2), size=(900, 40), font=0, text=title, flags=0)
    ]
    
    # إرجاع التنسيق القياسي (العنوان، قائمة المكونات)
    return (title, components)


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
        
        self["title_label"] = Label("anow panel — Fetching sections and data...")
        self["hint_label"] = Label("Please wait a moment...")
        
        self.menu_data = {}
        self.main_menu = []
        self.current_menu = "main"
        self.active_section = ""
        
        self["menu_list"] = MenuList([])
        
        # ضبط محرك القائمة ليدعم الـ MultiContent بشكل صحيح
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
            
            clean_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    clean_lines.append(line)
            
            i = 0
            while i < len(clean_lines):
                line = clean_lines[i]
                
                if "————" in line or "★★★" in line or "●●" in line or "||" in line:
                    clean_section = line.replace("————", "").replace("★★★", "").replace("●●", "").replace("★", "").replace("::", "").replace("|", "").strip()
                    if clean_section:
                        current_section = clean_section
                        if current_section not in self.menu_data:
                            self.menu_data[current_section] = []
                            display_item = build_menu_item(current_section, is_folder=True)
                            # هنا نحتفظ بـ display_item كامل لتمريره للـ MenuList مباشرة
                            self.main_menu.append((current_section, display_item))
                    i += 1
                    continue
                
                if current_section:
                    is_cmd = any(line.lower().startswith(c) for c in ["opkg", "wget", "rm", "init", "cd", "curl", "chmod"])
                    
                    if not is_cmd:
                        script_name = line
                        if (i + 1) < len(clean_lines):
                            next_line = clean_lines[i+1]
                            is_next_cmd = any(next_line.lower().startswith(c) for c in ["opkg", "wget", "rm", "init", "cd", "curl", "chmod"])
                            
                            if is_next_cmd:
                                display_item = build_menu_item(script_name, is_folder=False)
                                self.menu_data[current_section].append((script_name, next_line, display_item))
                                i += 2
                                continue
                    else:
                        display_item = build_menu_item(line[:50] + "...", is_folder=False)
                        self.menu_data[current_section].append((line[:50] + "...", line, display_item))
                
                i += 1

            if self.main_menu:
                # نمرر الـ display_item مباشرة (والذي أصبح عبارة عن Tuple جاهز ومطابق للمواصفات)
                self["menu_list"].setList([item[1] for item in self.main_menu])
                self["title_label"].setText("ANOW PANEL — Main Sections")
                self["hint_label"].setText("📡 Select section and press OK | Cancel to exit")
            else:
                self["title_label"].setText("⚠ File ajpanel_cmd is empty or format mismatch")
            
        except Exception as e:
            self["title_label"].setText("❌ Failed to fetch data!")
            self["hint_label"].setText(str(e))

    def ok_pressed(self):
        selected_idx = self["menu_list"].getSelectedIndex()
        if selected_idx is None:
            return

        if self.current_menu == "main":
            self.active_section = self.main_menu[selected_idx][0]
            if self.active_section in self.menu_data and self.menu_data[self.active_section]:
                self.current_menu = "sub"
                self["title_label"].setText("Section: " + self.active_section)
                self["hint_label"].setText("⚡ Press OK to execute script | Cancel to go back")
                self["menu_list"].setList([item[2] for item in self.menu_data[self.active_section]])
            else:
                self.session.open(MessageBox, "This section does not contain valid commands!", MessageBox.TYPE_INFO)
        else:
            sub_list = self.menu_data[self.active_section]
            selection_name = sub_list[selected_idx][0]
            selection_target = sub_list[selected_idx][1]
            self.execute_command(selection_name, selection_target)

    def execute_command(self, name, cmd):
        try:
            from Screens.Console import Console
            clean_cmd = str(cmd).strip()
            self.session.open(Console, title=str(name), cmdlist=[clean_cmd])
        except Exception as e:
            self.session.open(MessageBox, "Execution Error: " + str(e), MessageBox.TYPE_ERROR)

    def cancel_pressed(self):
        if self.current_menu == "sub":
            self.current_menu = "main"
            self["title_label"].setText("ANOW PANEL — Main Sections")
            self["hint_label"].setText("📡 Select section and press OK | Cancel to exit")
            self["menu_list"].setList([item[1] for item in self.main_menu])
        else:
            self.close()

def main(session, **kwargs):
    session.open(AnowPanelMainScreen)

def Plugins(**kwargs):
    return PluginDescriptor(
        name="anow panel", 
        description="Smart control panel for anow2008 with icons", 
        where=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
