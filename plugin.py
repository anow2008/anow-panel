# -*- coding: utf-8 -*-
# anow panel for Enigma2 (Python 3) - Universal auto-scaling skin

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from enigma import getDesktop, gFont, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_VALIGN_CENTER
from twisted.internet.threads import deferToThread
import os
import re
import ssl
import urllib.request

try:
    from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
except ImportError:  # very old images
    from Components.MultiContent import MultiContentEntryText
    from Components.MultiContent import MultiContentEntryPixmapAlphaTest as MultiContentEntryPixmapAlphaBlend

try:
    from enigma import BT_SCALE, BT_KEEP_ASPECT_RATIO
    ICON_FLAGS = BT_SCALE | BT_KEEP_ASPECT_RATIO
except ImportError:
    ICON_FLAGS = 0

DATA_URL = "https://raw.githubusercontent.com/anow2008/ajpanel_cmd/refs/heads/main/ajpanel_cmd"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
C_BG = "#0b1220"        # outer background
C_PANEL = "#111c33"     # main panel
C_HEADER = "#0b1220"    # header strip
C_ACCENT = "#06b6d4"    # cyan accent
C_TITLE = "#38bdf8"     # title text
C_TEXT = "#ffffff"      # list text
C_MUTED = "#94a3b8"     # hint text
C_LINE = "#334155"      # separators
C_SEL_BG = "#06b6d4"    # selection background
C_SEL_FG = "#0b1220"    # selection text
C_RED = "#ef4444"
C_GREEN = "#22c55e"


# ---------------------------------------------------------------------------
# Scale helpers (shared by the skin and the icon list)
# ---------------------------------------------------------------------------
try:
    _DESKTOP_W = getDesktop(0).size().width()
except Exception:
    _DESKTOP_W = 1920
SC = max(0.5, _DESKTOP_W / 1920.0)


def S(v):
    return int(round(v * SC))


ROW_H = 56
FONT_LIST = 28
ICON_SIZE = 40
ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

# Exact icon mapping: each online section and each command has its own icon.
# Keep these names in sync with the PNG files in the local icons/ directory.
SECTION_ICONS = {
    "command اوامر الانيجما2": "terminal",
    "عند تحميل صورة جديدة": "newimage",
    "تحميل اعدات للصورة": "settings",
    "astra-sm": "astra",
    "astra.conf **abertis": "network",
    "channels": "channels",
    "picons": "picons",
    "softcams": "softcam",
    "keys": "keys",
    "free cccam": "cccam",
    "epgimport": "epg",
    "plugins": "plugins",
    "subtitles plugins": "subtitles",
    "biss plugins": "biss",
    "panels": "panel",
    "skins": "skins",
    "fix": "repair",
    "remove": "remove",
    "clean": "clean",
    "ajpanel_cmd": "commandsfile",
    "init codes": "power",
}

# Command labels are matched exactly (case-insensitive); no broad substring
# matching, so e.g. a plugin name containing "cam" cannot steal another icon.
ITEM_ICONS = {
    "openatv": "openatv", "openpli": "openpli",
    "t2mi abertis": "abertis", "t2mi abertisopenpli": "abertispli",
    "تحميل ملف abertis": "download", "1 تحميل ملف abertis": "download",
    "1. أمر تحميل ملف astra.conf": "configfile",
    "2. أمر تحميل ملف astra-sm.lua": "lua",
    "3. أمر تحميل ملف astra-sm.conf": "configfile",
    "4. تحميل ملف (etc/sysctl.conf)": "systemfile",
    "channels 1": "channels1", "channels 22": "channels22",
    "openpicons": "openpicons", "picons eliesat": "eliesat",
    "picons anow": "anowpicons",
    "oscam-11.726-by-lenuxsat": "oscam", "ncam": "ncam", "config": "config",
    "softcam.key": "softcamkey", "cccam": "cccam",
    "epgimport anow": "epgimport", "epg-gold": "epggold",
    "epgimport": "epgimportplugin", "cacheflush": "cacheflush",
    "arabicsavior": "arabicsavior", "raedquicksignal": "quicksignal",
    "footonsat": "footonsat", "simplesport": "simplesport",
    "ciefpsettings t2mi abertis": "ciefp", "ciefpsettingst2miabertisopenpli": "ciefppli",
    "ipaudiopro": "ipaudio", "myaudio": "myaudio", "ipaudioplus": "ipaudioplus",
    "ip2sat": "ip2sat", "servercolor": "servercolor",
    "epgtranslator": "translator", "subssupportpro": "subsupport",
    "aisubtitles": "aisubtitles", "mytranslator 1.76": "mytranslator",
    "subssupport-1.5.8-r9": "subsupport", "subssupport-mnasr 1.8.0.r8": "subsupportm",
    "aisubtitles new with apikey": "aisubtitleskey",
    "bisspro-smart": "bisspro", "keyadder": "keyadder", "furybiss": "furybiss",
    "ajpanel": "ajpanel", "ciefppanel": "ciefppanel", "anowpanel": "anowpanel",
    "aglare-fhd v8.5": "aglare", "premiumfhd-blue": "premiumfhd",
    "aglare-fhd pli_7.2": "aglarepli", "fury-fhd": "furyfhd", "luka-fhd": "lukafhd",
    "ffmpeg": "ffmpeg", "remove all cam": "removecam",
    "remove-config-file": "removeconfig", "remove-emus-and-config": "removeemusconfig",
    "remove-emus": "removeemus", "remove bisspro-smart": "removebiss",
    "remove epg-gold": "removeepg", "remove all picons": "removepicons",
    "remove crash logs": "removelogs", "clean": "clean",
    "ajpanel_cmd": "commandsfile", "haitham.xml": "xmlfile",
    "init codes": "power",
}

# A distinct icon for any unlisted command, based on its parent section.
SECTION_FALLBACK_ICONS = {
    "plugins": "pluginitem", "subtitles plugins": "subtitleitem",
    "softcams": "softcamitem", "skins": "skinitem", "remove": "removeitem",
    "channels": "channelitem", "picons": "piconitem", "panels": "panelitem",
}

def _icon_key(value):
    return " ".join(str(value or "").strip().lower().split())

COMMAND_PREFIX_ICONS = (
    ("opkg update", "opkgupdate"), ("opkg install", "opkginstall"),
    ("opkg upgrade", "opkgupgrade"), ("wget", "wget"), ("curl", "curl"),
    ("unzip", "unzip"), ("tar", "archive"), ("init ", "power"),
    ("reboot", "power"),
)

def icon_for(name, kind="command", section=None, target=None):
    key = _icon_key(name)
    if kind == "section":
        return SECTION_ICONS.get(key, "folder")
    exact = ITEM_ICONS.get(key)
    if exact:
        return exact
    # The first online category contains raw shell commands without display
    # titles, so assign icons from the command itself rather than one shared icon.
    if _icon_key(section).startswith("command"):
        command = str(target or name).strip().lower()
        for prefix, icon_name in COMMAND_PREFIX_ICONS:
            if command.startswith(prefix):
                return icon_name
    return SECTION_FALLBACK_ICONS.get(_icon_key(section), "item")

_pix_cache = {}


def get_icon(name):
    if name not in _pix_cache:
        path = os.path.join(ICON_DIR, name + ".png")
        if not os.path.isfile(path):
            path = os.path.join(ICON_DIR, "item.png")
        _pix_cache[name] = LoadPixmap(path)
    return _pix_cache[name]


# ---------------------------------------------------------------------------
# Skin builder: designed on a 1920 px wide base, scaled to the real desktop
# ---------------------------------------------------------------------------
def build_skin():
    W, H = 1200, 720
    pad = 30
    row_h = ROW_H
    rows = 8
    list_y = 115
    list_h = row_h * rows
    sep_y = list_y + list_h + 14
    hint_y = sep_y + 10
    btn_y = hint_y + 62

    return """
    <screen name="AnowPanelMainScreen" position="center,center" size="{W},{H}" title="anow panel" backgroundColor="{bg}" flags="wfNoBorder">
        <eLabel position="0,0" size="{W},{H}" backgroundColor="{accent}" zPosition="0" />
        <eLabel position="{b},{b}" size="{iw},{ih}" backgroundColor="{panel}" zPosition="1" />

        <eLabel position="{b},{b}" size="{iw},{hh}" backgroundColor="{header}" zPosition="2" />
        <widget name="title_label" position="{pad},{ty}" size="{tw},{th}" font="Regular;{f_title}" halign="center" valign="center" foregroundColor="{title}" backgroundColor="{header}" transparent="1" zPosition="3" />
        <eLabel position="{b},{hl}" size="{iw},{S4}" backgroundColor="{accent}" zPosition="3" />

        <widget name="menu_list" position="{pad},{ly}" size="{tw},{lh}" font="Regular;{f_list}" itemHeight="{rh}" scrollbarMode="showOnDemand" foregroundColor="{text}" backgroundColor="{panel}" foregroundColorSelected="{selfg}" backgroundColorSelected="{selbg}" transparent="0" zPosition="3" />

        <eLabel position="{pad},{sy}" size="{tw},{S2}" backgroundColor="{line}" zPosition="3" />
        <widget name="hint_label" position="{pad},{hy}" size="{tw},{hh2}" font="Regular;{f_hint}" halign="left" valign="center" foregroundColor="{muted}" backgroundColor="{panel}" transparent="1" zPosition="3" />

        <eLabel position="{pad},{by}" size="{sq},{sq}" backgroundColor="{red}" zPosition="3" />
        <widget name="key_red" position="{k1x},{by_t}" size="{kw},{kh}" font="Regular;{f_key}" halign="left" valign="center" foregroundColor="{text}" backgroundColor="{panel}" transparent="1" zPosition="3" />
        <eLabel position="{g_sq},{by}" size="{sq},{sq}" backgroundColor="{green}" zPosition="3" />
        <widget name="key_green" position="{k2x},{by_t}" size="{kw},{kh}" font="Regular;{f_key}" halign="left" valign="center" foregroundColor="{text}" backgroundColor="{panel}" transparent="1" zPosition="3" />
    </screen>
    """.format(
        W=S(W), H=S(H),
        b=S(3), iw=S(W - 6), ih=S(H - 6),
        hh=S(90), hl=S(90), S4=S(4), S2=S(2),
        pad=S(pad), ty=S(18), tw=S(W - 2 * pad), th=S(58), f_title=S(34),
        ly=S(list_y), lh=S(list_h), rh=S(row_h), f_list=S(FONT_LIST),
        sy=S(sep_y), hy=S(hint_y), hh2=S(40), f_hint=S(24),
        by=S(btn_y), by_t=S(btn_y - 6), sq=S(26),
        k1x=S(pad + 40), kw=S(300), kh=S(38), f_key=S(24),
        g_sq=S(pad + 380), k2x=S(pad + 420),
        bg=C_BG, panel=C_PANEL, header=C_HEADER, accent=C_ACCENT,
        title=C_TITLE, text=C_TEXT, muted=C_MUTED, line=C_LINE,
        selbg=C_SEL_BG, selfg=C_SEL_FG, red=C_RED, green=C_GREEN,
    )


def download(url):
    """Blocking download (runs in a thread). Falls back to an unverified
    SSL context for old images that lack up-to-date CA certificates."""
    req = urllib.request.Request(url, headers={"User-Agent": "Enigma2 AnowPanel"})
    try:
        return urllib.request.urlopen(req, timeout=10).read()
    except ssl.SSLError:
        ctx = ssl._create_unverified_context()
        return urllib.request.urlopen(req, timeout=10, context=ctx).read()


# ---------------------------------------------------------------------------
# Parser for the ajpanel_cmd text file
# ---------------------------------------------------------------------------
CMD_WORDS = (
    "wget", "curl", "opkg", "init", "rm", "cd", "mkdir", "tar", "killall", "sh", "bash",
    "echo", "chmod", "cp", "mv", "sysctl", "ls", "cat", "sed", "ln", "touch", "reboot",
    "service", "sleep", "unzip", "/bin/sh", "/etc/init.d/",
)
_VAR_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def looks_like_command(line):
    """True for shell commands, False for plain descriptions such as
    '1. أمر تحميل ملف astra.conf' that must never be executed."""
    first = line.split(None, 1)[0]
    if first in CMD_WORDS or _VAR_ASSIGN.match(first):
        return True
    return "&&" in line or "://" in line


def clean_text(content):
    content = re.sub(r"●{5,}", "\n", content)
    content = re.sub(r"(\S)(★★★)", r"\1\n\2", content)
    return content


def parse_content(content):
    """Returns (main_menu, menu_data); main_menu = [(name, key)],
    menu_data = {key: [(name, command)]}"""
    menu_data, main_menu = {}, []
    section, temp_name = None, ""

    for line in clean_text(content).split("\n"):
        line = line.strip()
        if not line:
            continue

        if "————" in line or "::|" in line or ("|" in line and ("★" in line or "●" in line)):
            name = (line.replace("————", "").replace("★★★", "").replace("●●", "")
                    .replace("★", "").replace("::", "").replace("|", "")
                    .strip().strip("()").strip())
            if name:
                section = name
                if section not in menu_data:
                    menu_data[section] = []
                    main_menu.append((section, section))
            temp_name = ""
            continue

        if section is None:
            continue

        if line.startswith("★") and line.endswith("★"):
            temp_name = line.replace("★★★", "").replace("★", "").strip()
            continue

        if "#" in line and line.split("#")[0].strip().startswith(("init", "reboot")):
            menu_data[section].append((line, line.split("#")[0].strip()))
            temp_name = ""
            continue

        if not looks_like_command(line):
            temp_name = line
            continue

        menu_data[section].append((temp_name or line, line))
        temp_name = ""

    return main_menu, menu_data


class IconList(MenuList):
    """List with a small icon in front of every row."""

    def __init__(self):
        MenuList.__init__(self, [], False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", S(FONT_LIST)))
        self.l.setItemHeight(S(ROW_H))

    def build(self, items, kind, section=None):
        """Build rows with exact per-section/per-command icon assignment."""
        row_h, ico = S(ROW_H), S(ICON_SIZE)
        x_ico = S(14)
        x_txt = x_ico + ico + S(16)
        width = S(1140)  # inner list width in base units
        out = []
        for name, target in items:
            icon = icon_for(name, kind, section, target)

            entry = [(name, target)]
            pix = get_icon(icon)
            if pix:
                entry.append(MultiContentEntryPixmapAlphaBlend(
                    pos=(x_ico, (row_h - ico) // 2), size=(ico, ico), png=pix, flags=ICON_FLAGS))
            entry.append(MultiContentEntryText(
                pos=(x_txt, 0), size=(width - x_txt, row_h), font=0,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=name))
            out.append(entry)
        self.setList(out)


class AnowPanelMainScreen(Screen):
    skin = build_skin()

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        self["title_label"] = Label("ANOW PANEL")
        self["hint_label"] = Label("")
        self["key_red"] = Label("خروج (Exit)")
        self["key_green"] = Label("تحديث (Refresh)")

        self.menu_data = {}
        self.main_menu = []
        self.current_menu = "main"
        self["menu_list"] = IconList()

        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "ok": self.ok_pressed,
            "cancel": self.cancel_pressed,
            "red": self.close,
            "green": self.fetch_github_data,
        }, -1)

        self.onLayoutFinish.append(self.fetch_github_data)

    # ------------------------------------------------------------------ data
    def fetch_github_data(self):
        self["title_label"].setText("ANOW PANEL — جاري جلب البيانات...")
        self["hint_label"].setText("⏳ جاري التحميل من GitHub...")
        self["menu_list"].setList([])
        d = deferToThread(download, DATA_URL)
        d.addCallback(self.parse_data)
        d.addErrback(self.fetch_failed)

    def parse_data(self, data):
        try:
            content = data.decode("utf-8", errors="ignore")
            self.main_menu, self.menu_data = parse_content(content)
            if self.main_menu:
                self.show_main()
            else:
                self["title_label"].setText("⚠ تنبيه")
                self["hint_label"].setText("لم يتم العثور على أية أقسام في الملف النصي!")
        except Exception as e:
            self["title_label"].setText("❌ خطأ أثناء قراءة البيانات")
            self["hint_label"].setText(str(e))

    def fetch_failed(self, error):
        self["title_label"].setText("❌ فشل الاتصال بالسيرفر!")
        self["hint_label"].setText("تأكد من الشبكة أو الرابط (اضغط الأخضر لإعادة المحاولة)")

    # ------------------------------------------------------------ navigation
    def show_main(self):
        self.current_menu = "main"
        self["menu_list"].build(self.main_menu, "section")
        self["menu_list"].moveToIndex(0)
        self["title_label"].setText("ANOW PANEL — الأقسام الرئيسية")
        self["hint_label"].setText("📡 OK للدخول  |  الأخضر للتحديث  |  الأحمر للخروج")

    def ok_pressed(self):
        selected = self["menu_list"].getCurrent()
        if not selected:
            return

        selection_name = str(selected[0][0])
        selection_target = str(selected[0][1])

        if self.current_menu == "main":
            if selection_target in self.menu_data and self.menu_data[selection_target]:
                self.current_menu = "sub"
                self["title_label"].setText("قسم: " + selection_name)
                self["hint_label"].setText("⚡ OK لتشغيل السكريبت  |  Cancel للعودة")
                self["menu_list"].build(self.menu_data[selection_target], "command", selection_target)
                self["menu_list"].moveToIndex(0)
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
            self.show_main()
        else:
            self.close()


def main(session, **kwargs):
    session.open(AnowPanelMainScreen)


def Plugins(**kwargs):
    return PluginDescriptor(
        name="anow panel",
        description="لوحة التحكم الذكية v2.0 - anow2008",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="plugin.png",
        fnc=main
    )
