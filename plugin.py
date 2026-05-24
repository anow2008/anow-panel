# -*- coding: utf-8 -*-
# anow panel for Enigma2
# المصدر: القراءة الديناميكية المباشرة من رابط GitHub الخاص بك

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Console import Console
from Screens.MessageBox import MessageBox
import urllib2 # أو استخدام requests/twisted لجلب الرابط بالخلفية

class AnowPanelMainScreen(Screen):
    skin = """
    <screen position="center,center" size="780,560" title="anow panel v1.0">
        <widget name="title_label" position="15,15" size="750,40" font="Regular; 22" halign="center" valign="center" foregroundColor="#00FF00" />
        <widget name="menu_list" position="15,70" size="750,420" scrollbarMode="showOnDemand" font="Regular; 20" itemHeight="35" />
        <eLabel position="15,505" size="750,2" backgroundColor="#555555" />
        <widget name="hint_label" position="15,515" size="750,30" font="Regular; 16" halign="left" valign="center" foregroundColor="#aaaaaa" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.console = Console()
        
        self["title_label"] = Label("anow panel - جاري جلب البيانات...")
        self["hint_label"] = Label("يرجى الانتظار حتى يتم تحميل الأوامر من السيرفر...")
        
        self.menu_data = {}
        self.main_menu = []
        self.current_menu = "main"
        self["menu_list"] = MenuList([])
        
        self["actions"] = ActionMap(["OkCancelActions"], {
            "ok": self.ok_pressed,
            "cancel": self.cancel_pressed
        }, -1)
        
        # استدعاء دالة قراءة الرابط عند فتح البانل
        self.onLayoutFinish.append(self.fetch_github_data)

    def fetch_github_data(self):
        url = "https://raw.githubusercontent.com/anow2008/ajpanel_cmd/refs/heads/main/ajpanel_cmd"
        try:
            # فتح وقراءة الرابط المباشر الخاص بك
            req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib2.urlopen(req, timeout=8)
            content = response.read()
            
            # معالجة الملف وتقسيمه لأقسام وأوامر بنفس ترتيبك
            lines = content.split('\n')
            current_section = None
            current_item_name = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # التعرف على الأقسام الرئيسية في ملفك
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
                
                # التعرف على الأوامر والأسماء تحت كل قسم
                elif current_section:
                    if line.startswith("★★★") and line.endswith("★★★"):
                        current_item_name = line.replace("★★★", "").strip()
                    elif line.startswith("opkg") or line.startswith("wget") or line.startswith("rm") or line.startswith("init") or line.startswith("cd"):
                        name = current_item_name if current_item_name else line
                        self.menu_data[current_section].append((name, line))
                        current_item_name = "" # تفريغ الاسم للأمر التالي
                    elif line.startswith("OpenATV") or line.startswith("openpli"):
                        current_item_name = line
            
            # تحديث الواجهة بعد نجاح الجلب
            self["menu_list"].setList(self.main_menu)
            self["title_label"].setText("القائمة الرئيسية للبانل")
            self["hint_label"].setText("اضغط OK للدخول، أو Cancel للخروج")
            
        except Exception as e:
            self["title_label"].setText("فشل الاتصال بالسيرفر!")
            self["hint_label"].setText("تأكد من اتصال الإنترنت بالرسيفر.")

    def ok_pressed(self):
        selected = self["menu_list"].getCurrent()
        if not selected:
            return

        selection_name = selected[0]
        selection_target = selected[1]

        if self.current_menu == "main":
            # فتح القسم الفرعي وجلب أوامره من البيانات المقروءة من الرابط
            if selection_target in self.menu_data and self.menu_data[selection_target]:
                self.current_menu = "sub"
                self["title_label"].setText(selection_name)
                self["hint_label"].setText("اضغط OK لتنفيذ الأمر، أو Cancel للعودة")
                self["menu_list"].setList(self.menu_data[selection_target])
        else:
            # تنفيذ الأمر المختار في الخلفية
            self.execute_command(selection_name, selection_target)

    def execute_command(self, name, cmd):
        self.session.openWithCallback(
            self.command_finished, 
            MessageBox, 
            ("جاري تنفيذ: %s\nيرجى الانتظار..." % name), 
            MessageBox.TYPE_INFO, 
            timeout=4
        )
        self.console.execute(cmd)

    def command_finished(self, answer=None):
        self.session.open(MessageBox, "تم تنفيذ السكربت بنجاح!", MessageBox.TYPE_INFO, timeout=3)

    def cancel_pressed(self):
        if self.current_menu == "sub":
            self.current_menu = "main"
            self["title_label"].setText("القائمة الرئيسية للبانل")
            self["hint_label"].setText("اضغط OK للدخول، أو Cancel للخروج")
            self["menu_list"].setList(self.main_menu)
        else:
            self.close()

def main(session, **kwargs):
    session.open(AnowPanelMainScreen)

def Plugins(**kwargs):
    return PluginDescriptor(
        name="anow panel", 
        description="لوحة تحكم ديناميكية متصلة مباشرة بملف أوامرك على GitHub", 
        whereabouts=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
