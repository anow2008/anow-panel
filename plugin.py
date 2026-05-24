# -*- coding: utf-8 -*-
# anow panel for Enigma2
# المصدر الأساسي: التجميعة الكاملة المرتبة يدوياً لـ anow2008

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Console import Console
from Screens.MessageBox import MessageBox

class AnowPanelMainScreen(Screen):
    # تصميم الواجهة (Skin) ليكون متوافقاً مع شاشات FHD و HD
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
        
        self["title_label"] = Label("القائمة الرئيسية للبانل")
        self["hint_label"] = Label("اضغط OK للدخول، أو Cancel للخروج")
        
        # الأقسام الرئيسية للبانل بنفس ترتيب ملف المصدر بالظبط
        self.main_menu = [
            ("⚙️ Command اوامر الانيجما2", "enigma_cmds"),
            ("📡 تحميل اعدادات للصورة", "image_settings"),
            ("🛰️ astra-sm & abertis", "astra_menu"),
            ("🌐 ملفات ترددات satellites.xml", "satellites_menu"),
            ("📂 ملف القنوات channels", "channels_menu"),
            ("🖼️ البيكونات picons", "picons_menu"),
            ("🔑 المحاكيات والشفرات Softcams & Keys", "softcams_menu"),
            ("🔌 إضافات الـ Plugins العامة", "plugins_menu"),
            ("🪐 إضافات الـ biss Plugins", "biss_menu"),
            ("📺 إضافات الـ IPTV Plugins", "iptv_menu"),
            ("🛠️ البانلات PANELS", "panels_menu"),
            ("🎨 السكينات Skins", "skins_menu"),
            ("🔄 تحديث ملف البانل وصيانة النظام", "maintenance_menu")
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
            if selection_target == "enigma_cmds":
                self.load_sub_menu("Command اوامر الانيجما2", [
                    ("opkg update", "opkg update"),
                    ("opkg update && opkg upgrade", "opkg update && opkg upgrade"),
                    ("opkg install wget", "opkg install wget"),
                    ("opkg install curl", "opkg install curl")
                ])
            elif selection_target == "image_settings":
                self.load_sub_menu("تحميل اعدادات للصورة", [
                    ("OpenATV settings", "wget https://raw.githubusercontent.com/anow2008/Downloading-settings/main/OpenATV/install.sh -O - | /bin/sh"),
                    ("openpli settings", "wget https://raw.githubusercontent.com/anow2008/Downloading-settings/main/openpli/install.sh -O - | /bin/sh")
                ])
            elif selection_target == "astra_menu":
                self.load_sub_menu("astra-sm & abertis", [
                    ("تثبيت حزمة astra-sm العامة", "opkg update && opkg install astra-sm"),
                    ("تحميل ملفات التشغيل في أمر واحد (الكل)", "wget -O /etc/astra/scripts/abertis https://raw.githubusercontent.com/anow2008/astra/main/scripts/abertis && chmod 755 /etc/astra/scripts/abertis && wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/astra.conf -O /etc/astra/astra.conf && chmod 755 /etc/astra/astra.conf && wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/etc/sysctl.conf -O /etc/sysctl.conf && chmod 644 /etc/sysctl.conf && sysctl -p"),
                    ("تحميل ملفات صورة openpli في أمر واحد", "wget -O /etc/astra/scripts/abertis https://raw.githubusercontent.com/anow2008/astra/main/scripts/abertis && chmod 755 /etc/astra/scripts/abertis && wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/astra-sm.lua -O /etc/astra/astra-sm.lua && chmod 755 /etc/astra/astra-sm.lua && wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/astra-sm.conf -O /etc/astra/astra-sm.conf && chmod 755 /etc/astra/astra-sm.conf && wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/etc/sysctl.conf -O /etc/sysctl.conf && chmod 644 /etc/sysctl.conf && sysctl -p"),
                    ("1. تحميل ملف abertis منفصل", "wget -O /etc/astra/scripts/abertis https://raw.githubusercontent.com/anow2008/astra/main/scripts/abertis && chmod 755 /etc/astra/scripts/abertis"),
                    ("2. تحميل ملف astra.conf منفصل", "wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/astra.conf -O /etc/astra/astra.conf && chmod 755 /etc/astra/astra.conf"),
                    ("3. تحميل ملف astra-sm.lua منفصل", "wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/astra-sm.lua -O /etc/astra/astra-sm.lua && chmod 755 /etc/astra/astra-sm.lua"),
                    ("4. تحميل ملف astra-sm.conf منفصل", "wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/astra-sm.conf -O /etc/astra/astra-sm.conf && chmod 755 /etc/astra/astra-sm.conf"),
                    ("5. تحميل ملف etc/sysctl.conf منفصل", "wget --no-check-certificate https://raw.githubusercontent.com/anow2008/astra/refs/heads/main/etc/sysctl.conf -O /etc/sysctl.conf && chmod 644 /etc/sysctl.conf && sysctl -p")
                ])
            elif selection_target == "satellites_menu":
                self.load_sub_menu("ملفات ترددات satellites.xml", [
                    ("satellites.xml (OE-Alliance الرسمي)", "wget --no-check-certificate https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/refs/heads/master/src/satellites.xml -O /etc/tuxbox/satellites.xml && cp /etc/tuxbox/satellites.xml /etc/enigma2/satellites.xml && echo 'Done! Satellites updated in both locations.'"),
                    ("satellites.xml anow (نسختك الخاصة)", "wget --no-check-certificate https://raw.githubusercontent.com/anow2008/satellites.xml/main/satellites.xml -O /etc/tuxbox/satellites.xml && cp /etc/tuxbox/satellites.xml /etc/enigma2/satellites.xml && echo 'Done! Your custom satellites.xml updated.'")
                ])
            elif selection_target == "channels_menu":
                self.load_sub_menu("ملف القنوات channels", [
                    ("تحميل وتحديث ملف قنوات anow الشامل", "wget --no-check-certificate -O /tmp/channels.tar.gz https://raw.githubusercontent.com/anow2008/channels/main/channels.tar.gz && tar -xzf /tmp/channels.tar.gz -C /tmp && rm -rf /etc/enigma2/userbouquet.* && cp -rf /tmp/etc/enigma2/* /etc/enigma2/ && chmod 644 /etc/enigma2/userbouquet.* /etc/enigma2/lamedb && wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 && rm -rf /tmp/channels.tar.gz /tmp/etc 2>/dev/null")
                ])
            elif selection_target == "picons_menu":
                self.load_sub_menu("البيكونات picons", [
                    ("picons eliesat", "wget -qO- 'https://gitlab.com/eliesat/picons/-/raw/main/archive.sh' | sh"),
                    ("eliesat picons-motor", "wget -qO- --no-check-certificate https://raw.githubusercontent.com/eliesatpanelgrid/oe2.0/main/picons/picons-all.sh | bash"),
                    ("picons anow (تحميل إلى hdd)", "mkdir -p /media/hdd/picon && cd /media/hdd/picon && wget -qO- https://github.com/anow2008/picon-picon/archive/refs/heads/main.tar.gz | tar xz --strip-components=2 picon-picon-main/picon"),
                    ("❌ Delete all picons (تفريغ مجلد البيكونات)", "MS=''; for path in /media/hdd /media/usb /usr/share/enigma2; do [ -d '$path' ] && MS='$path' && break; done; [ -n '$MS' ] && [ -d '$MS/picon' ] && rm -rf '$MS/picon'/* && echo 'DONE: $MS/picon is now empty' || echo 'No picon folder found'")
                ])
            elif selection_target == "softcams_menu":
                self.load_sub_menu("المحاكيات والشفرات Softcams & Keys", [
                    ("oscam 11.726-emu-r802", "wget https://raw.githubusercontent.com/anow2008/cam-emu/main/oscam/installer.sh -O - | /bin/sh"),
                    ("Ncam fairman", "wget https://raw.githubusercontent.com/biko-73/Ncam_EMU/main/installer.sh -O - | /bin/sh"),
                    ("config anow", "wget -qO- https://raw.githubusercontent.com/anow2008/conf/main/install/install.sh | sh"),
                    ("🗑️ remove-config-file", "wget -qO- https://raw.githubusercontent.com/anow2008/ajpanel_cmd/main/remove/remove-config-file.sh | sh"),
                    ("🗑️ remove-emus-and-config", "wget -qO- https://raw.githubusercontent.com/anow2008/ajpanel_cmd/main/remove/remove-emus-and-config-file.sh | sh"),
                    ("🗑️ remove-emus", "wget -qO- https://raw.githubusercontent.com/anow2008/ajpanel_cmd/main/remove/remove-emus.sh | sh"),
                    ("🔑 softcam.key التحديث التلقائي", "wget -O /etc/tuxbox/config/SoftCam.Key https://raw.githubusercontent.com/anow2008/softcam.key/main/softcam.key")
                ])
            elif selection_target == "plugins_menu":
                self.load_sub_menu("إضافات الـ Plugins العامة", [
                    ("ArabicSavior", "wget https://raw.githubusercontent.com/fairbird/ArabicSavior/main/installer.sh -O - | /bin/sh"),
                    ("AISubtitles", "wget https://github.com/milanello13/aisubtitles/releases/download/v2.0/enigma2-plugin-extensions-aisubtitles_v2.0_all.ipk -O /tmp/subs.ipk && opkg install /tmp/subs.ipk"),
                    ("Mytranslator (Eliesat GitLab)", "wget 'https://gitlab.com/eliesat/extensions/-/raw/main/mytranslator/mytranslator.sh' -qO - | /bin/sh"),
                    ("Mytranslator anow", "wget -qO- https://raw.githubusercontent.com/anow2008/my-translator/main/mytranslator.sh | sh"),
                    ("subssupport-1.5.8-r9", "wget 'https://gitlab.com/eliesat/extensions/-/raw/main/subssupport/subssupport-1.5.8-r9.sh' -O - | /bin/sh"),
                    ("Subssupport-mnasr 1.8.0.r8", "wget https://gitlab.com/eliesat/extensions/-/raw/main/subssupport/subssupport.sh -qO - | /bin/sh"),
                    ("RaedQuickSignal", "wget https://raw.githubusercontent.com/fairbird/RaedQuickSignal/main/installer.sh -O - | /bin/sh"),
                    ("FootOnsat", "wget https://raw.githubusercontent.com/fairbird/FootOnsat/main/Download/install.sh -O - | /bin/sh"),
                    ("CiefpSettings T2mi Abertis", "wget https://raw.githubusercontent.com/ciefp/CiefpSettingsT2miAbertis/main/installer.sh -O - | /bin/sh"),
                    ("CiefpSettingsT2miAbertisOpenPLi", "wget https://raw.githubusercontent.com/ciefp/CiefpSettingsT2miAbertisOpenPLi/main/installer.sh -O - | /bin/sh"),
                    ("IPAudioPro (رابط أول)", "wget https://raw.githubusercontent.com/zKhadiri/IPAudioPro-Releases-/main/installer.sh -O - | /bin/sh"),
                    ("IPAudioPro (رابط ثانٍ)", "wget -q '--no-check-certificate' https://raw.githubusercontent.com/zKhadiri/IPAudioPro-Releases-/refs/heads/main/installer.sh -O - | /bin/sh"),
                    ("myaudio Config (IPAudioPro.json)", "wget -O /etc/enigma2/IPAudioPro.json https://raw.githubusercontent.com/anow2008/sound/refs/heads/main/etc/enigma2/IPAudioPro.json"),
                    ("ip2sat", "wget 'https://gitlab.com/eliesat/extensions/-/raw/main/ip2sat/ip2sat.sh' -O - | /bin/sh"),
                    ("OAWeather (تثبيت كامل وإعادة تشغيل)", "wget -qO- https://github.com/oe-alliance/OAWeather/archive/refs/heads/main.tar.gz | tar -xzv --strip-components=2 -C /usr/lib/enigma2/python/ OAWeather-main/src/ && chmod -R 755 /usr/lib/enigma2/python/Plugins/Extensions/OAWeather /usr/lib/enigma2/python/Components/Converter /usr/lib/enigma2/python/Components/Sources /usr/lib/enigma2/python/Components/Renderer && find /usr/lib/enigma2/python/Plugins/Extensions/OAWeather -name '*.py[oc]' -delete && init 4 && sleep 2 && init 3")
                ])
            elif selection_target == "biss_menu":
                self.load_sub_menu("إضافات الـ biss Plugins", [
                    ("BissPro-Smart (بلجن ذكي)", "wget -qO - https://raw.githubusercontent.com/anow2008/BissPro-Smart/main/install.sh | sh"),
                    ("🗑️ remove BissPro-Smart", "rm -rf /usr/lib/enigma2/python/Plugins/Extensions/BissPro-Smart && killall -9 enigma2"),
                    ("KeyAdder", "wget https://raw.githubusercontent.com/fairbird/KeyAdder/main/installer.sh -O - | /bin/sh"),
                    ("E2BissKeyEditor", "wget https://raw.githubusercontent.com/ismail9875/E2BissKeyEditor/refs/heads/main/installer.sh -O - | /bin/sh"),
                    ("FuryBiss", "wget https://raw.githubusercontent.com/islam-2412/FuryBiss/main/fury/installer.sh -O - | /bin/sh")
                ])
            elif selection_target == "iptv_menu":
                self.load_sub_menu("إضافات الـ IPTV Plugins", [
                    ("E2iPlayer python3", "wget 'https://github.com/oe-mirrors/e2iplayer/archive/refs/heads/python3.zip' -O /tmp/e2iplayer-python3.zip && unzip /tmp/e2iplayer-python3.zip -d /tmp/ && cp -rf /tmp/e2iplayer-python3/IPTVPlayer /usr/lib/enigma2/python/Plugins/Extensions && rm -f /tmp/e2iplayer-python3.zip && rm -fr /tmp/e2iplayer-master"),
                    ("e2iplayer-oem", "wget 'https://gitlab.com/eliesat/extensions/-/raw/main/e2iplayer-oem/e2iplayer.sh' -O - | /bin/sh"),
                    ("X-Streamity (رابط جيت هاب)", "wget https://raw.githubusercontent.com/biko-73/xstreamity/main/installer.sh -qO - | /bin/sh"),
                    ("X-Streamity (فيد eliesat)", "wget https://raw.githubusercontent.com/eliesatpanelgrid/oe2.0/main/addons/xstreamity/xstreamity.sh -qO - | /bin/sh"),
                    ("Estalker emilnabil", "wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/EStalker/EStalker.sh -O - | /bin/sh"),
                    ("xklass (رابط أول)", "wget 'https://gitlab.com/eliesat/extensions/-/raw/main/xklass/xklass.sh' -O - | /bin/sh"),
                    ("xklass emilnabil", "wget https://dreambox4u.com/emilnabil237/plugins/xklass/installer.sh -O - | /bin/sh"),
                    ("PlutoTV (رابط أول)", "wget https://raw.githubusercontent.com/MOHAMED19OS/Download/main/PlutoTV/installer.sh -qO - | /bin/sh"),
                    ("PlutoTV (رابط ثانٍ)", "wget 'https://gitlab.com/eliesat/extensions/-/raw/main/plutotv/plutotv.sh' -O - | /bin/sh"),
                    ("HasBahCa (رابط أول)", "wget https://raw.githubusercontent.com/MOHAMED19OS/Download/main/HasBahCa/installer.sh -qO - | /bin/sh"),
                    ("HasBahCa (رابط ثانٍ)", "wget https://raw.githubusercontent.com/Belfagor2005/HasBahCa/main/installer.sh -O - | /bin/sh"),
                    ("HasBahCa (رابط ثالث)", "wget 'https://gitlab.com/eliesat/extensions/-/raw/main/hasbahca/hasbahca.sh' -O - | /bin/sh"),
                    ("Vavoo", "wget https://raw.githubusercontent.com/eliesatpanelgrid/oe2.0/main/addons/vavoo/vavoo.sh -qO - | /bin/sh")
                ])
            elif selection_target == "panels_menu":
                self.load_sub_menu("البانلات PANELS", [
                    ("AJPanel biko-73", "wget https://raw.githubusercontent.com/biko-73/AjPanel/main/installer.sh -O - | /bin/sh"),
                    ("SmartAddonspanel emilnabil", "wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/SmartAddonspanel/smart-Panel.sh -O - | /bin/sh"),
                    ("EmilPanelPro", "wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/EmilPanelPro/emilpanelpro.sh -O - | /bin/sh"),
                    ("CiefpPanel", "wget https://raw.githubusercontent.com/ciefp/CiefpsettingsPanel/main/installer.sh -O - | /bin/sh"),
                    ("EliesatPanel", "wget https://raw.githubusercontent.com/eliesat/eliesatpanel/main/installer.sh -O - | /bin/sh"),
                    ("Epanel emilnabil", "wget https://dreambox4u.com/emilnabil237/plugins/epanel/installer.sh -O - | /bin/sh")
                ])
            elif selection_target == "skins_menu":
                self.load_sub_menu("السكينات Skins", [
                    ("Fury-FHD islam-2412", "wget https://raw.githubusercontent.com/islam-2412/IPKS/refs/heads/main/fury/installer.sh -O - | /bin/sh"),
                    ("premiumfhd-blue Eliesat", "wget \"https://gitlab.com/eliesat/skins/-/raw/main/all/premium-fhd/premiumfhd-blue.sh\" -O - | /bin/sh")
                ])
            elif selection_target == "maintenance_menu":
                self.load_sub_menu("تحديث البانل وصيانة النظام", [
                    ("🔄 تحديث ملف ajpanel_cmd وجلبه تلقائياً", "rm -f /media/hdd/ajpanel_cmd /media/hdd/Ajpanel_Eliesatpanel/ajpanel_cmd && wget --no-check-certificate 'https://raw.githubusercontent.com/anow2008/ajpanel_cmd/refs/heads/main/ajpanel_cmd' -P /media/hdd/ && cp /media/hdd/ajpanel_cmd /media/hdd/Ajpanel_Eliesatpanel/"),
                    ("🗑️ remove crash logs", "wget 'https://raw.githubusercontent.com/anow2008/ajpanel_cmd/refs/heads/main/remove/remove-crash-logs.sh' -O - | /bin/sh"),
                    ("➡️ Init 0 (Deep Standby)", "init 0"),
                    ("➡️ Init 1 (Stops Enigma2 & network)", "init 1"),
                    ("➡️ Init 3 (Starts Enigma2 normally)", "init 3"),
                    ("➡️ Init 4 (Stops Enigma2)", "init 4"),
                    ("➡️ Init 6 (Reboots the box)", "init 6")
                ])
        else:
            # تنفيذ الأمر المختار مباشرة بالخلفية
            self.execute_command(selection_name, selection_target)

    def load_sub_menu(self, title, items):
        self.current_menu = "sub"
        self["title_label"].setText(title)
        self["hint_label"].setText("اضغط OK لتنفيذ الأمر، أو Cancel للعودة للقائمة السابقة")
        self["menu_list"].setList(items)

    def execute_command(self, name, cmd):
        self.session.openWithCallback(
            self.command_finished, 
            MessageBox, 
            ("جاري الآن تنفيذ: %s\nيرجى الانتظار..." % name), 
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
        description="لوحة تحكم كاملة لتحديث القنوات، السوفتكام، والبلجنات الخاصة بك", 
        whereabouts=PluginDescriptor.WHERE_PLUGINMENU, 
        icon="plugin.png", 
        fnc=main
    )
