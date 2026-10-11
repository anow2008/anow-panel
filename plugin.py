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

# الملف المحلي (موجود جنب plugin.py). لو مش موجود يرجع للنت.
LOCAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ajpanel_cmd")
USE_LOCAL_ONLY = False   # True = ما يدخلش نت خالص لجلب القايمة

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

# first matching keyword wins (lower-case, matched inside the section name)
ICON_KEYWORDS = [
    ("softcam", ("softcam", "cam", "emu", "oscam", "ncam", "سوفت", "كام")),
    ("update", ("update", "upgrade", "تحديث")),
    ("picons", ("picon", "بيكون")),
    ("skins", ("skin", "theme", "سكين", "سكن")),
    ("channels", ("channel", "bouquet", "list", "settings", "قنوات", "قوائم")),
    ("plugins", ("plugin", "addon", "extension", "بلجن", "اضافات", "إضافات")),
    ("network", ("network", "ftp", "wifi", "ssh", "telnet", "dns", "شبكة")),
    ("backup", ("backup", "restore", "clean", "نسخ", "تنظيف")),
    ("power", ("restart", "reboot", "power", "ريستارت", "اعادة", "إعادة")),
    ("tools", ("tool", "system", "utility", "ادوات", "أدوات", "نظام")),
]

_pix_cache = {}


def get_icon(name):
    if name not in _pix_cache:
        _pix_cache[name] = LoadPixmap(os.path.join(ICON_DIR, name + ".png"))
    return _pix_cache[name]


def icon_for(section_name):
    low = section_name.lower()
    for icon, words in ICON_KEYWORDS:
        for w in words:
            if w in low:
                return icon
    return "default"


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
    """يقرأ من الملف المحلي لو موجود، وإلا ينزّله من النت (مع fallback لـ SSL)."""
    if os.path.isfile(LOCAL_FILE):
        with open(LOCAL_FILE, "rb") as f:
            return f.read()
    if USE_LOCAL_ONLY:
        raise IOError("الملف المحلي غير موجود: " + LOCAL_FILE)

    req = urllib.request.Request(url, headers={"User-Agent": "Enigma2 AnowPanel"})
    try:
        return urllib.request.urlopen(req, timeout=10).read()
    except ssl.SSLError:
        ctx = ssl._create_unverified_context()
        return urllib.request.urlopen(req, timeout=10, context=ctx).read()


class IconList(MenuList):
    """List with a small icon in front of every row."""

    def __init__(self):
        MenuList.__init__(self, [], False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", S(FONT_LIST)))
        self.l.setItemHeight(S(ROW_H))

    def build(self, items, kind):
        """items: [(name, target)], kind: 'section' or 'command'"""
        row_h, ico = S(ROW_H), S(ICON_SIZE)
        x_ico = S(14)
        x_txt = x_ico + ico + S(16)
        width = S(1140)  # inner list width in base units
        out = []
        for name, target in items:
            icon = icon_for(name) if kind == "section" else "run"
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
        self["hint_label"].setText("⏳ جاري تحميل القائمة...")
        self["menu_list"].setList([])
        d = deferToThread(download, DATA_URL)
        d.addCallback(self.parse_data)
        d.addErrback(self.fetch_failed)

    def parse_data(self, data):
        try:
            content = data.decode("utf-8", errors="ignore")
            lines = content.split("\n")

            self.menu_data = {}
            self.main_menu = []
            current_section = None
            temp_name = ""

            for line in lines:
                line = line.strip()

                if not line or (line.startswith("●") and len(line) > 10):
                    continue

                if "————" in line or "::|" in line or ("|" in line and ("★" in line or "●" in line)):
                    clean_section = (line.replace("————", "").replace("★★★", "")
                                     .replace("●●", "").replace("★", "")
                                     .replace("::", "").replace("|", "").strip())
                    if clean_section:
                        current_section = clean_section
                        if current_section not in self.menu_data:
                            self.menu_data[current_section] = []
                            self.main_menu.append((current_section, current_section))
                    continue

                if current_section:
                    if line.startswith("★") and line.endswith("★"):
                        temp_name = line.replace("★★★", "").replace("★", "").strip()
                        continue

                    if "#" in line and any(line.split("#")[0].strip().startswith(cmd) for cmd in ["init", "reboot"]):
                        cmd_part = line.split("#")[0].strip()
                        name_part = line.strip()
                        self.menu_data[current_section].append((name_part, cmd_part))
                        temp_name = ""
                        continue

                    name = temp_name if temp_name else line
                    self.menu_data[current_section].append((name, line))
                    temp_name = ""

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
                self["menu_list"].build(self.menu_data[selection_target], "command")
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
