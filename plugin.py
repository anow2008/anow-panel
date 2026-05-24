# -*- coding: utf-8 -*-
# anow panel for Enigma2
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Console import Console
from Screens.MessageBox import MessageBox

class AnowPanelMainScreen(Screen):
    # تصميم واجهة البلجن (Skin) متوافق مع شاشات FHD و HD
    skin = """
    <screen position="center,center" size="750,550" title="anow panel v1.0">
        <widget name="title_label" position="15,15" size="720,40" font="Regular; 22" halign="center" valign="center" foregroundColor="#00FF00" />
        <widget name="menu_list" position="15,70" size="720,410" scrollbarMode="showOnDemand" font="Regular; 20" itemHeight="35" />
        <eLabel position="15,495" size="720,2" backgroundColor="#555555" />
        <widget name="hint_label" position="15,505" size="720,30" font="Regular; 16" halign="left" valign="center" foregroundColor="#aaaaaa" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.console = Console()
        
        self["title_label"] = Label("القائمة الرئيسية للبانل")
        self["hint_label"] = Label("اضغط OK للدخول، أو Cancel للخروج")
        
        # الأقسام الرئيسية للبانل مستوحاة بالكامل من ملفك
        self.main_menu = [
            ("⚙️ أوامر الانيجما2 والتحديثات العامة", "system_menu"),
            ("📡 إعدادات الصور والقنوات (Settings)", "channels_menu"),
            ("🔑 تشفير نيوكامد و أسترا (Astra-SM)", "astra_menu"),
            ("🔌 إضافات وبلاجينز عامة ومحاكيات", "plugins_menu"),
            ("🎨 سكينات وبانلات أخرى (Skins & Panels)", "skins_menu")
        ]
        
        self.current_menu = "main"
        self["menu_list"] = MenuList(self.main_menu)
        
        self["actions"] = ActionMap(["OkCancelActions"], {
            "ok": self.ok_pressed,
            "cancel": self.cancel_pressed
        }, -1)

    def ok_pressed(self):
        selected = self["menu_list"].getCurrent()
        if not selected:
            return

        selection_name = selected[0]
        selection_target = selected[1]

        if self.current_menu == "main":
            if selection_target == "system_menu":
                self.load_sub_menu("أوامر الانيجما2 العامة", [
                    ("تحديث الفيد (opkg update)", "opkg update"),
                    ("تحديث وترقية الصورة (update & upgrade)", "opkg update && opkg upgrade"),
                    ("تثبيت أداة wget", "opkg install wget"),
                    ("تثبيت أداة curl", "opkg install curl")
                ])
            elif selection_target == "channels_menu":
                self.load_sub_menu("إعدادات الصور والقنوات", [
                    ("تحميل إعدادات صورة OpenATV", "wget https://raw.githubusercontent.com/anow2008/Downloading-settings/main/OpenATV/install.sh -O - | /bin/sh"),
                    ("تحميل إعدادات صورة openpli", "wget https://raw.githubusercontent.com/anow2008/Downloading-settings/main/openpli/install.sh -O - | /bin/sh")
                ])
            elif selection_target == "astra_menu":
                self.load_sub_menu("أوامر astra-sm وتحديث الملفات", [
                    ("تثبيت حزمة astra-sm", "opkg update && opkg install astra-sm"),
                    ("تحميل ملف التشفير والتحديث في أمر واحد", "wget -O /etc/astra/scripts/abertis https://raw.githubusercontent.com/anow2008/astra/main/scripts/abertis && chmod 755 /etc/astra/scripts/abertis && wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/main/scripts/astra.conf -O /etc/astra/astra.conf")
                ])
            elif selection_target == "plugins_menu":
                self.load_sub_menu("المحاكيات والإضافات العامة", [
                    ("تثبيت بلجن BissPro-Smart الخاص بك", "wget -qO - https://raw.githubusercontent.com/anow2008/BissPro-Smart/main/install.sh | sh"),
                    ("تثبيت بلجن حماية اللغة العربية ArabicSavior", "wget https://raw.githubusercontent.com/fairbird/ArabicSavior/main/installer.sh -O - | /bin/sh")
                ])
            elif selection_target == "skins_menu":
                self.load_sub_menu("السكينات والبانلات المتاحة", [
                    ("تثبيت سكين Fury-FHD", "wget https://raw.githubusercontent.com/islam-2412/IPKS/refs/heads/main/fury/installer.sh -O - | /bin/sh"),
                    ("تثبيت سكين premiumfhd-blue", "wget \"https://gitlab.com/eliesat/skins/-/raw/main/all/premium-fhd/premiumfhd-blue.sh\" -O - | /bin/sh"),
                    ("تثبيت CiefpsettingsPanel", "wget https://raw.githubusercontent.com/ciefp/CiefpsettingsPanel/main/installer.sh -O - | /bin/sh"),
                    ("تثبيت EliesatPanel", "wget https://raw.githubusercontent.com/eliesat/eliesatpanel/main/installer.sh -O - | /bin/sh"),
                    ("تثبيت Epanel للمطور emilnabil", "wget https://dreambox4u.com/emilnabil237/plugins/epanel/installer.sh -O - | /bin/sh")
                ])
        else:
            # تنفيذ الأمر المختار في الخلفية
            self.execute_command(selection_name, selection_target)

    def load_sub_menu(self, title, items):
        self.current_menu = "sub"
        self["title_label"].setText(title)
        self["hint_label"].setText("اضغط OK لتنفيذ الأمر، أو Cancel للعودة")
        self["menu_list"].setList(items)

    def execute_command(self, name, cmd):
        self.session.openWithCallback(
            self.command_finished, 
            MessageBox, 
            ("جاري الآن تنفيذ: %s\nيرجى الانتظار..." % name), 
            MessageBox.TYPE_INFO, 
            timeout=3
        )
        self.console.execute(cmd)

    def command_finished(self, answer=None):
        self.session.open(MessageBox, "تم تنفيذ الأمر بنجاح!", MessageBox.TYPE_INFO, timeout=3)

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
        description="لوحة تحكم كاملة لتحديث القنوات، السوفتكام، والبلجنات الخاصة بك", 
        whereabouts=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
