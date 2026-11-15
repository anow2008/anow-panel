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
import glob
import json
from shlex import quote
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
GITHUB_API_URL = "https://api.github.com/repos/anow2008/ajpanel_cmd/contents/file"

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
SECTION_ICONS = {
    "command اوامر الانيجما2": "terminal",
    "عند تحميل صورة جديدة": "newimage",
    "تحميل اعدات للصورة": "settings",
    "astra-sm": "abertis",
    "astra.conf **abertis": "abertis",
    "channels": "channels",
    "picons": "picons",
    "softcams": "softcam",
    "keys": "keys",
    "free cccam": "free",
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
    "install files": "opkginstall",
    "online files install": "opkginstall",
}

ITEM_ICONS = {
    "openatv": "openatv", 
    "openpli": "openpli",
    "opkg update && opkg upgrade && opkg install wget curl && wget -qO- https://raw.githubusercontent.com/anow2008/new-image/main/new-image.sh | sh": "new",
    "opkg update && opkg upgrade": "software",
    "opkg update": "software", 
    "opkg install wget": "software",
    "opkg install curl": "software",
    "opkg install unzip": "software",
    "init 0": "power",
    "init 1": "power",
    "init 3": "power",
    "init 4": "power",
    "init 6": "power",
    "install files": "opkginstall",
    "online files install": "opkginstall",
}

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

# ---------------------------------------------------------------------------
# "Install Files": install .ipk / .tar.gz files found on HDD / USB / /tmp
# ---------------------------------------------------------------------------
INSTALL_SECTION = "Install Files"
INSTALL_TARGET = "__install_files__"
ONLINE_INSTALL_SECTION = "Online Files Install"
ONLINE_INSTALL_TARGET = "__online_files_install__"

INSTALL_EXTS = (".ipk", ".tar.gz", ".tgz")
SCAN_SKIP_DIRS = ("movie", "picon", "epg", "timeshift", "lost+found")
SCAN_MAX_DEPTH = 2          
SCAN_MAX_FILES = 300


def _scan_roots():
    roots = ["/media/hdd", "/media/usb", "/media/mmc", "/hdd", "/tmp"]
    for p in sorted(glob.glob("/media/*")) + sorted(glob.glob("/autofs/*")):
        if p not in roots:
            roots.append(p)
    return [r for r in roots if os.path.isdir(r)]


def find_install_files(roots=None, max_depth=SCAN_MAX_DEPTH):
    found, seen = [], set()
    for root in (roots if roots is not None else _scan_roots()):
        real = os.path.realpath(root)
        if real in seen:
            continue
        seen.add(real)
        base = real.rstrip(os.sep).count(os.sep)
        for cur, dirs, files in os.walk(real):
            depth = cur.rstrip(os.sep).count(os.sep) - base
            if depth >= max_depth:
                dirs[:] = []
            else:
                dirs[:] = [d for d in dirs if not d.startswith(".") and d.lower() not in SCAN_SKIP_DIRS]
            for f in files:
                if not f.startswith(".") and f.lower().endswith(INSTALL_EXTS):
                    found.append((f, os.path.join(cur, f)))
            if len(found) >= SCAN_MAX_FILES:
                break
        if len(found) >= SCAN_MAX_FILES:
            break
    found.sort(key=lambda item: item[0].lower())
    return found[:SCAN_MAX_FILES]


def fetch_github_install_files():
    """Fetch files list from GitHub API directory and filter .ipk, .tar.gz, .tgz files"""
    try:
        req = urllib.request.Request(GITHUB_API_URL, headers={"User-Agent": "Enigma2 AnowPanel"})
        try:
            response = urllib.request.urlopen(req, timeout=10).read()
        except ssl.SSLError:
            ctx = ssl._create_unverified_context()
            response = urllib.request.urlopen(req, timeout=10, context=ctx).read()
        
        files_data = json.loads(response.decode("utf-8", errors="ignore"))
        supported_list = []
        for item in files_data:
            if item.get("type") == "file":
                name = item.get("name", "")
                download_url = item.get("download_url")
                if name and download_url and name.lower().endswith(INSTALL_EXTS):
                    supported_list.append((name, download_url))
        supported_list.sort(key=lambda item: item[0].lower())
        return supported_list
    except Exception as e:
        print("AnowPanel GitHub API Error:", str(e))
        return []


def human_size(n):
    n = float(n)
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return ("%d %s" if unit == "B" else "%.1f %s") % (n, unit)
        n /= 1024.0
    return "%.1f GB" % n


def install_command(path):
    if path.lower().endswith(".ipk"):
        return "opkg install %s" % quote(path)
    return "tar -xzf %s -C /" % quote(path)


def icon_for(name, kind="command", section=None, target=None):
    key = _icon_key(name)
    if kind == "section":
        return SECTION_ICONS.get(key, "folder")
    if _icon_key(section) == _icon_key(INSTALL_SECTION) or _icon_key(section) == _icon_key(ONLINE_INSTALL_SECTION):
        return "opkginstall" if str(target).lower().endswith(".ipk") else "archive"
    exact = ITEM_ICONS.get(key)
    if exact:
        return exact
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


def build_skin():
    W, H = 1500, 900            
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
        _rect(38, 103, 884, 624, C_LINE, 1),
        _rect(40, 105, 880, 620, C_PANEL, 2),
        _rect(938, 103, 514, 624, C_LINE, 1),
        _rect(940, 105, 510, 620, C_PANEL, 2),
        '<widget name="menu_list" position="%d,%d" size="%d,%d" itemHeight="%d" scrollbarMode="showNever" '
        'backgroundColor="%s" backgroundColorSelected="%s" foregroundColor="%s" foregroundColorSelected="%s" '
        'zPosition="3" />' % (S(list_x), S(list_y), S(LIST_W), S(list_h), S(ROW_H),
                              C_PANEL, C_SEL, C_TEXT, C_TEXT),
        '<widget name="preview_icon" position="%d,%d" size="%d,%d" alphatest="blend" scale="1" zPosition="3" />' % (
            S(logo_x), S(150), S(LOGO_SIZE), S(LOGO_SIZE)),
        _widget("preview_name", card_x + 20, 450, card_w - 40, 110, 40, C_TEXT, "center", 4, "top"),
        _widget("preview_info", card_x + 20, 570, card_w - 40, 60, 28, C_MUTED, "center", 4, "top"),
        _widget("hint_label", 50, 745, 1400, 60, 30, C_MUTED, "left", 4),
        _rect(50, 847, 26, 26, C_RED, 4, 6),
        _widget("key_red", 88, 835, 280, 50, 24, C_TEXT, "left", 4),
        _rect(380, 847, 26, 26, C_GREEN, 4, 6),
        _widget("key_green", 418, 835, 320, 50, 24, C_TEXT, "left", 4),
        '</screen>',
    ]
    return "\n".join(parts)


def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Enigma2 AnowPanel"})
    try:
        return urllib.request.urlopen(req, timeout=10).read()
    except ssl.SSLError:
        ctx = ssl._create_unverified_context()
        return urllib.request.urlopen(req, timeout=10, context=ctx).read()


def parse_content(content):
    menu_data, main_menu = {}, []
    section, temp_name = None, ""

    for line in content.split("\n"):
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

        if not (line.split(None, 1)[0] in ("wget", "curl", "opkg", "init", "rm", "cd", "mkdir", "tar", "killall", "sh", "bash", "echo", "chmod", "cp", "mv", "sysctl", "ls", "cat", "sed", "ln", "touch", "reboot", "service", "sleep", "unzip") or "&&" in line or "://" in line):
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
    except TypeError:
        return MultiContentEntryText(**kw)


class IconList(MenuList):
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
            entry = [(name, target, icon), _row_bg(w, h)]
            pix = get_icon(icon)
            if pix:
                entry.append(MultiContentEntryPixmapAlphaBlend(
                    pos=(x_ico, S(10)), size=(ico, ico), png=pix, flags=ICON_FLAGS))
            entry.append(MultiContentEntryText(
                pos=(x_txt, 0), size=(tw, h), font=0, flags=flags, text=name,
                color=_ci(C_TEXT), color_sel=_ci(C_TEXT)))
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
        self._scanning = False
        self["menu_list"] = IconList()
        self["menu_list"].onSelectionChanged.append(self.update_preview)

        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "ok": self.ok_pressed,
            "cancel": self.cancel_pressed,
            "red": self.close,
            "green": self.fetch_github_data,
        }, -1)

        self.onLayoutFinish.append(self.fetch_github_data)

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
            if self.main_menu:
                self.main_menu = list(self.main_menu) + [
                    ("Online Files Install", ONLINE_INSTALL_TARGET),
                    (INSTALL_SECTION, INSTALL_TARGET)
                ]
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

    def clear_preview(self):
        self["preview_name"].setText("")
        self["preview_info"].setText("")
        self["preview_icon"].hide()

    def update_preview(self):
        selected = self["menu_list"].getCurrent()
        if not selected:
            self.clear_preview()
            return
        name, target, icon = selected[0][0], selected[0][1], selected[0][2]
        if self.current_menu == "main":
            if target == INSTALL_TARGET:
                info = "Local IPK / TAR.GZ"
            elif target == ONLINE_INSTALL_TARGET:
                info = "GitHub Online Folder (IPK & Tar.gz)"
            else:
                info = "%d أمر" % len(self.menu_data.get(target, []))
        elif self.current_section == INSTALL_SECTION:
            try:
                info = human_size(os.path.getsize(target)) + "\n" + os.path.dirname(target)
            except Exception:
                info = os.path.dirname(target)
        elif self.current_section == ONLINE_INSTALL_SECTION:
            info = "GitHub Direct Link (" + ("IPK" if target.endswith(".ipk") else "TAR.GZ") + ")"
        else:
            info = self.current_section
        name = str(name)
        if len(name) > 42:
            name = name[:39] + "..."
        self["preview_name"].setText(str(name))
        self["preview_info"].setText(str(info))
        pix = get_icon(icon)
        if pix and self["preview_icon"].instance:
            self["preview_icon"].instance.setPixmap(pix)
            self["preview_icon"].show()
        else:
            self["preview_icon"].hide()

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
            if selection_target == INSTALL_TARGET:
                self.open_install_files()
            elif selection_target == ONLINE_INSTALL_TARGET:
                self.open_online_install_files()
            elif selection_target in self.menu_data and self.menu_data[selection_target]:
                self.current_menu = "sub"
                self.current_section = selection_name
                self["title_label"].setText("قسم: " + selection_name)
                self["hint_label"].setText("⚡ OK لتشغيل السكريبت  |  Cancel للعودة")
                self["menu_list"].build(self.menu_data[selection_target], "command", selection_target)
                self["menu_list"].moveToIndex(0)
                self.update_preview()
        elif self.current_section == INSTALL_SECTION:
            self.install_file(selection_name, selection_target)
        elif self.current_section == ONLINE_INSTALL_SECTION:
            self.install_online_file(selection_name, selection_target)
        else:
            self.execute_command(selection_name, selection_target)

    def execute_command(self, name, cmd):
        self.session.openWithCallback(
            lambda answer: self.run_command(answer, name, cmd),
            MessageBox,
            "هل تريد تنفيذ هذا الأمر؟\n\n" + str(name),
            MessageBox.TYPE_YESNO,
            default=False,
        )

    def run_command(self, answer, name, cmd):
        if not answer:
            return
        try:
            from Screens.Console import Console
            self.session.open(Console, title=str(name), cmdlist=[str(cmd).strip()])
        except Exception as e:
            self.session.open(MessageBox, "خطأ أثناء التنفيذ: " + str(e), MessageBox.TYPE_ERROR)

    def open_install_files(self):
        self._scanning = True
        self["hint_label"].setText("⏳ جاري البحث عن ملفات ipk و tar.gz ...")
        d = deferToThread(find_install_files)
        d.addCallback(self.install_files_found)
        d.addErrback(self.install_scan_failed)

    def install_files_found(self, files):
        if not self._scanning:
            return
        self._scanning = False
        if not files:
            self["hint_label"].setText("📡 OK للدخول  |  الأخضر للتحديث  |  الأحمر للخروج")
            self.session.open(
                MessageBox,
                "لم يتم العثور على ملفات ipk أو tar.gz في:\n/media/hdd  /media/usb  /tmp",
                MessageBox.TYPE_INFO,
            )
            return
        self.menu_data[INSTALL_TARGET] = files
        self.current_menu = "sub"
        self.current_section = INSTALL_SECTION
        self["title_label"].setText("قسم: " + INSTALL_SECTION)
        self["hint_label"].setText("📦 OK للتثبيت  |  Cancel للعودة")
        self["menu_list"].build(files, "command", INSTALL_SECTION)
        self["menu_list"].moveToIndex(0)
        self.update_preview()

    def install_scan_failed(self, error):
        self._scanning = False
        self["hint_label"].setText("📡 OK للدخول  |  الأخضر للتحديث  |  الأحمر للخروج")
        self.session.open(MessageBox, "خطأ أثناء البحث عن الملفات: " + str(error), MessageBox.TYPE_ERROR)

    # --- Online Files (IPK & Tar.gz) Functions ---
    def open_online_install_files(self):
        self["hint_label"].setText("⏳ جاري جلب الملفات من GitHub...")
        d = deferToThread(fetch_github_install_files)
        d.addCallback(self.online_files_found)
        d.addErrback(self.online_scan_failed)

    def online_files_found(self, files):
        if not files:
            self["hint_label"].setText("📡 OK للدخول  |  الأخضر للتحديث  |  الأحمر للخروج")
            self.session.open(MessageBox, "لم يتم العثور على أي ملفات IPK أو Tar.gz في المجلد المحدد على GitHub.", MessageBox.TYPE_INFO)
            return
        self.menu_data[ONLINE_INSTALL_TARGET] = files
        self.current_menu = "sub"
        self.current_section = ONLINE_INSTALL_SECTION
        self["title_label"].setText("قسم: " + ONLINE_INSTALL_SECTION)
        self["hint_label"].setText("📦 OK للتحميل والتثبيت  |  Cancel للعودة")
        self["menu_list"].build(files, "command", ONLINE_INSTALL_SECTION)
        self["menu_list"].moveToIndex(0)
        self.update_preview()

    def online_scan_failed(self, error):
        self["hint_label"].setText("📡 OK للدخول  |  الأخضر للتحديث  |  الأحمر للخروج")
        self.session.open(MessageBox, "خطأ أثناء الاتصال بـ GitHub: " + str(error), MessageBox.TYPE_ERROR)

    def install_online_file(self, name, url):
        is_ipk = name.lower().endswith(".ipk")
        msg = "هل تريد تحميل وتثبيت هذا الملف عبر الإنترنت؟\n\n" + str(name)
        if not is_ipk:
            msg += "\n\n(ملاحظة: هذا الملف سيتم فك ضغطه على جذر النظام /)"
        self.session.openWithCallback(
            lambda answer: self.run_online_install(answer, name, url, is_ipk),
            MessageBox,
            msg,
            MessageBox.TYPE_YESNO,
            default=False,
        )

    def run_online_install(self, answer, name, url, is_ipk):
        if not answer:
            return
        try:
            from Screens.Console import Console
            tmp_file = "/tmp/" + name
            if is_ipk:
                cmd = f"wget -O {quote(tmp_file)} {quote(url)} && opkg install {quote(tmp_file)}"
            else:
                cmd = f"wget -O {quote(tmp_file)} {quote(url)} && tar -xzf {quote(tmp_file)} -C /"
            
            self.session.openWithCallback(
                self.ask_restart, Console, title="تثبيت: " + str(name), cmdlist=[cmd])
        except Exception as e:
            self.session.open(MessageBox, "خطأ أثناء التثبيت: " + str(e), MessageBox.TYPE_ERROR)

    def install_file(self, name, path):
        if not os.path.isfile(path):
            self.session.open(MessageBox, "الملف غير موجود:\n" + path, MessageBox.TYPE_ERROR)
            return
        text = "هل تريد تثبيت هذا الملف؟\n\n" + str(name)
        if not path.lower().endswith(".ipk"):
            text += "\n\nسيتم فك الضغط على النظام (/)"
        self.session.openWithCallback(
            lambda answer: self.run_install(answer, name, path),
            MessageBox, text, MessageBox.TYPE_YESNO, default=False,
        )

    def run_install(self, answer, name, path):
        if not answer:
            return
        try:
            from Screens.Console::Console if False else ... # fallback handling
            from Screens.Console import Console
            self.session.openWithCallback(
                self.ask_restart, Console, title=str(name), cmdlist=[install_command(path)])
        except Exception as e:
            self.session.open(MessageBox, "خطأ أثناء التثبيت: " + str(e), MessageBox.TYPE_ERROR)

    def ask_restart(self, *args):
        self.session.openWithCallback(
            self.do_restart, MessageBox,
            "هل تريد إعادة تشغيل الواجهة (GUI) الآن؟", MessageBox.TYPE_YESNO, default=False)

    def do_restart(self, answer):
        if answer:
            from Screens.Standby import TryQuitMainloop
            self.session.open(TryQuitMainloop, 3)

    def cancel_pressed(self):
        self._scanning = False
        if self.current_menu == "sub":
            self.show_main()
        else:
            self.close()


def main(session, **kwargs):
    session.open(AnowPanelMainScreen)


def Plugins(**kwargs):
    return PluginDescriptor(
        name="anow panel",
        description="لوحة التحكم الذكية v1.0 - anow2008",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="plugin.png",
        fnc=main
    )
