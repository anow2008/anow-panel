# -*- coding: utf-8 -*-
# anow panel for Enigma2 (Python 3) - Universal auto-scaling skin

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
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
    from enigma import BT_SCALE, BT_KEEP_ASPECT_RATIO, BT_HALIGN_CENTER, BT_VALIGN_CENTER
    ICON_FLAGS = BT_SCALE | BT_KEEP_ASPECT_RATIO | BT_HALIGN_CENTER | BT_VALIGN_CENTER
except ImportError:
    ICON_FLAGS = 0

DATA_URL = "https://raw.githubusercontent.com/anow2008/ajpanel_cmd/refs/heads/main/ajpanel_cmd"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
C_BG = "#050b17"        # fallback background (when background.png is missing)
C_PANEL = "#0a1428"     # list panel / info card
C_ROW = "#0f1d38"       # list row
C_SEL = "#125aba"       # selected row (matches background.png lines)
C_ACCENT = "#125aba"    # blue accent
C_TITLE = "#5aa9ff"     # title text
C_TEXT = "#ffffff"      # main text
C_MUTED = "#8fa3c0"     # hint / description text
C_LINE = "#244f8a"      # panel borders
C_RED = "#ef4444"
C_GREEN = "#22c55e"


# ---------------------------------------------------------------------------
# Auto scaling: everything is designed on a 1920x1080 base, scaled by the
# smaller of width/height ratios (same method as the BissPro plugin)
# ---------------------------------------------------------------------------
try:
    _d = getDesktop(0).size()
    SC = min(_d.width() / 1920.0, _d.height() / 1080.0)
except Exception:
    SC = 1.0


def S(v):
    return int(v * SC)


def F(v):
    return int(max(20, v * SC))


def _ci(c):
    return int(c[1:], 16)


# Dimensions (base units) - same as the reference plugin
ROW_H = 100            # list row height
ICON_SIZE = 80         # icon inside a row
FONT_NAME = 34         # row title font
FONT_DESC = 24         # row description font
LIST_W = 860           # row width
LOGO_SIZE = 280        # big preview icon
CORNER_BOX = 28
CORNER_ROW = 26
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(PLUGIN_DIR, "icons")
BG_PATH = os.path.join(PLUGIN_DIR, "background.png")

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
def _rect(x, y, w, h, color, z=1, r=CORNER_BOX):
    pw, ph = S(w), S(h)
    rad = min(S(r), ph // 2, pw // 2)
    corner = ' cornerRadius="%d"' % rad if rad > 0 else ""
    return '<eLabel position="%d,%d" size="%d,%d" backgroundColor="%s" zPosition="%d"%s />' % (
        S(x), S(y), pw, ph, color, z, corner)


def _widget(name, x, y, w, h, size, fg, align="left", z=4, valign="center"):
    return ('<widget name="%s" position="%d,%d" size="%d,%d" font="Regular;%d" foregroundColor="%s" '
            'transparent="1" halign="%s" valign="%s" zPosition="%d" />') % (
        name, S(x), S(y), S(w), S(h), F(size), fg, align, valign, z)


def build_skin():
    W, H = 1500, 900            # the same size as background.png
    list_x, list_y, list_h = 50, 115, ROW_H * 6
    card_x, card_w = 940, 510
    logo_x = card_x + (card_w - LOGO_SIZE) // 2

    if os.path.isfile(BG_PATH):
        bg = '<ePixmap pixmap="%s" position="0,0" size="%d,%d" zPosition="0" alphatest="blend" scale="1" />' % (
            BG_PATH, S(W), S(H))
    else:
        bg = _rect(0, 0, W, H, C_BG, 0, 40)

    parts = [
        '<screen name="AnowPanelMainScreen" position="center,center" size="%d,%d" title="anow panel" '
        'backgroundColor="#00000000" flags="wfNoBorder">' % (S(W), S(H)),
        bg,
        _widget("title_label", 50, 12, 1400, 68, 44, C_TITLE, "center"),
        # borders + panels (list on the left, info card on the right)
        _rect(38, 103, 884, 624, C_LINE, 1),
        _rect(40, 105, 880, 620, C_PANEL, 2),
        _rect(938, 103, 514, 624, C_LINE, 1),
        _rect(940, 105, 510, 620, C_PANEL, 2),
        '<widget name="menu_list" position="%d,%d" size="%d,%d" itemHeight="%d" scrollbarMode="showNever" '
        'backgroundColor="%s" backgroundColorSelected="%s" foregroundColor="%s" foregroundColorSelected="%s" '
        'zPosition="3" />' % (S(list_x), S(list_y), S(LIST_W), S(list_h), S(ROW_H),
                              C_PANEL, C_SEL, C_TEXT, C_TEXT),
        # big icon of the highlighted row
        '<widget name="preview_icon" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="3" />' % (
            S(logo_x), S(150), S(LOGO_SIZE), S(LOGO_SIZE)),
        _widget("preview_name", card_x + 20, 450, card_w - 40, 110, 40, C_TEXT, "center", 4, "top"),
        _widget("preview_info", card_x + 20, 570, card_w - 40, 60, 28, C_MUTED, "center", 4, "top"),
        _widget("hint_label", 50, 745, 1400, 60, 30, C_MUTED, "left", 4),
        # colour keys under the bottom line of the background
        _rect(50, 847, 26, 26, C_RED, 4, 6),
        _widget("key_red", 88, 835, 280, 50, 24, C_TEXT, "left", 4),
        _rect(380, 847, 26, 26, C_GREEN, 4, 6),
        _widget("key_green", 418, 835, 320, 50, 24, C_TEXT, "left", 4),
        '</screen>',
    ]
    return "\n".join(parts)


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


def _row_bg(w, h):
    kw = dict(pos=(0, S(3)), size=(w, h - S(6)), font=0, text="",
              backcolor=_ci(C_ROW), backcolor_sel=_ci(C_SEL))
    try:
        return MultiContentEntryText(cornerRadius=S(CORNER_ROW), **kw)
    except TypeError:  # old images ignore rounded corners
        return MultiContentEntryText(**kw)


class IconList(MenuList):
    """Rows like the BissPro plugin: rounded row, 80px icon, title + description."""

    def __init__(self):
        MenuList.__init__(self, [], False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", F(FONT_NAME)))
        self.l.setFont(1, gFont("Regular", F(FONT_DESC)))
        self.l.setItemHeight(S(ROW_H))

    def build(self, items, kind, section=None):
        w, h = S(LIST_W), S(ROW_H)
        ico = S(ICON_SIZE)
        x_ico = S(10)
        x_txt = S(105)
        tw = w - x_txt - S(10)
        flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER
        out = []
        for name, target in items:
            icon = icon_for(name, kind, section, target)
            if kind == "section":
                desc = "%d أمر" % len(self.owner_data.get(target, [])) if hasattr(self, "owner_data") else ""
            elif str(name).strip() == str(target).strip():
                desc = section or ""
            else:
                desc = str(target).strip().replace("\n", " ")
                if len(desc) > 70:
                    desc = desc[:67] + "..."

            entry = [(name, target, icon, desc), _row_bg(w, h)]
            pix = get_icon(icon)
            if pix:
                entry.append(MultiContentEntryPixmapAlphaBlend(
                    pos=(x_ico, S(10)), size=(ico, ico), png=pix, flags=ICON_FLAGS))
            entry.append(MultiContentEntryText(
                pos=(x_txt, S(10)), size=(tw, S(45)), font=0, flags=flags, text=name,
                color=_ci(C_TEXT), color_sel=_ci(C_TEXT)))
            entry.append(MultiContentEntryText(
                pos=(x_txt, S(55)), size=(tw, S(35)), font=1, flags=flags, text=desc,
                color=_ci(C_MUTED), color_sel=_ci("#dbe8ff")))
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
        self["preview_icon"] = Pixmap()
        self["preview_name"] = Label("")
        self["preview_info"] = Label("")

        self.menu_data = {}
        self.main_menu = []
        self.current_menu = "main"
        self.current_section = ""
        self["menu_list"] = IconList()
        self["menu_list"].owner_data = self.menu_data
        self["menu_list"].onSelectionChanged.append(self.update_preview)

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
        self.clear_preview()
        d = deferToThread(download, DATA_URL)
        d.addCallback(self.parse_data)
        d.addErrback(self.fetch_failed)

    def parse_data(self, data):
        try:
            content = data.decode("utf-8", errors="ignore")
            self.main_menu, self.menu_data = parse_content(content)
            self["menu_list"].owner_data = self.menu_data
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

    # --------------------------------------------------------------- preview
    def clear_preview(self):
        self["preview_name"].setText("")
        self["preview_info"].setText("")
        self["preview_icon"].hide()

    def update_preview(self):
        """Show the big icon + name of the highlighted row in the right card."""
        selected = self["menu_list"].getCurrent()
        if not selected:
            self.clear_preview()
            return
        name, target, icon = selected[0][0], selected[0][1], selected[0][2]
        if self.current_menu == "main":
            count = len(self.menu_data.get(target, []))
            info = "%d أمر" % count
        else:
            info = self.current_section
        self["preview_name"].setText(str(name))
        self["preview_info"].setText(str(info))
        pix = get_icon(icon)
        if pix and self["preview_icon"].instance:
            self["preview_icon"].instance.setPixmap(pix)
            self["preview_icon"].show()
        else:
            self["preview_icon"].hide()

    # ------------------------------------------------------------ navigation
    def show_main(self):
        self.current_menu = "main"
        self["menu_list"].build(self.main_menu, "section")
        self["menu_list"].moveToIndex(0)
        self.update_preview()
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
                self.current_section = selection_name
                self["title_label"].setText("قسم: " + selection_name)
                self["hint_label"].setText("⚡ OK لتشغيل السكريبت  |  Cancel للعودة")
                self["menu_list"].build(self.menu_data[selection_target], "command", selection_target)
                self["menu_list"].moveToIndex(0)
                self.update_preview()
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
