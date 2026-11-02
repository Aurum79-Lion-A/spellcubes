# SpellCubes (C) Copyright 2024-2026 Lion-A Softwares
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import json
import base64
import io
from PIL import Image  # Resim Base64 dönüşümü için

from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                               QToolBar, QFileDialog, QComboBox,
                               QFontComboBox, QInputDialog, QMessageBox,
                               QColorDialog, QLabel, QDialog, QGridLayout,
                               QLineEdit, QPushButton, QCheckBox,
                               QVBoxLayout, QPlainTextEdit)
from PySide6.QtGui import (QFont, QAction, QBrush, QActionGroup, QTextListFormat,
                           QTextTableFormat, QTextCharFormat, QColor,
                           QTextDocument, QTextCursor, QKeySequence)
from PySide6.QtCore import Qt, QFileInfo, QLocale
from PySide6.QtPrintSupport import QPrinter, QPrintDialog


# ----------------------------------------------------------------------
#  Uygulama bilgileri (ÇEVİRİLMEZ)
# ----------------------------------------------------------------------
APP_NAME = "SpellCubes"
COPYRIGHT_LINE = "SpellCubes (C) Copyright 2024-2026 Lion-A Softwares"
LICENSE_NAME = "GNU General Public License v3 (GPLv3)"
LICENSE_URL = "https://www.gnu.org/licenses/gpl-3.0.html"
# Lisans metni yasal nedenlerle her zaman İngilizce kalır, çevrilmez.
LICENSE_NOTICE = (
    "This program is free software: you can redistribute it and/or modify "
    "it under the terms of the GNU General Public License version 3 as "
    "published by the Free Software Foundation.\n\n"
    "This program is distributed in the hope that it will be useful, "
    "but WITHOUT ANY WARRANTY; without even the implied warranty of "
    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
    "GNU General Public License for more details.\n\n"
    "You should have received a copy of the GNU General Public License "
    "along with this program. If not, see <https://www.gnu.org/licenses/>."
)

# ----------------------------------------------------------------------
#  Dil sistemi (i18n)
# ----------------------------------------------------------------------
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
I18N_DIR = os.path.join(APP_DIR, "i18n")

# Yerleşik İngilizce metinler: i18n klasörü yoksa, bozuksa ya da bir anahtar
# eksikse program her zaman buradan İngilizce'ye döner.
DEFAULT_EN = {
    "menu_file": "File",
    "menu_edit": "Edit",
    "menu_insert": "Insert",
    "menu_help": "Help",
    "menu_language": "Language",
    "toolbar_title": "Formatting",

    "act_new": "New",
    "act_open": "Open...",
    "act_save": "Save",
    "act_save_as": "Save As...",
    "act_pdf": "Export as PDF...",
    "act_print": "Print...",
    "act_exit": "Exit",
    "act_undo": "Undo",
    "act_redo": "Redo",
    "act_cut": "Cut",
    "act_copy": "Copy",
    "act_paste": "Paste",
    "act_select_all": "Select All",
    "act_find": "Find and Replace...",
    "act_find_next": "Find Next",
    "act_bold": "Bold",
    "act_italic": "Italic",
    "act_underline": "Underline",
    "act_color": "Text Color",
    "act_size_up": "Increase Size",
    "act_size_down": "Decrease Size",
    "act_left": "Left",
    "act_center": "Center",
    "act_right": "Right",
    "act_justify": "Justify",
    "act_bullets": "Bullets",
    "act_numbered": "Numbered",
    "act_image": "Insert Image",
    "act_table": "Insert Table...",
    "act_about": "About / License (GPLv3)...",

    "fr_title": "Find and Replace",
    "fr_find": "Find:",
    "fr_replace": "Replace:",
    "fr_case": "Case sensitive",
    "fr_find_next": "Find Next",
    "fr_replace_btn": "Replace",
    "fr_replace_all": "Replace All",
    "fr_close": "Close",
    "fr_wrapped": "Wrapped around to the beginning.",
    "fr_not_found": "Not found.",
    "fr_replaced": "{count} replacement(s) made.",

    "untitled": "Untitled",
    "status_fmt": "Line {line}, Col {col}   |   {words} words, {chars} characters",

    "sp_text": "The document has unsaved changes.",
    "sp_info": "Do you want to save before closing?",
    "sp_save": "Save",
    "sp_discard": "Don't Save",
    "sp_cancel": "Cancel",

    "error": "Error",
    "open_title": "Open SpellCubes File",
    "save_as_title": "Save SpellCubes File As",
    "spellcubes_files": "SpellCubes Files",
    "all_files": "All Files",
    "file_opened": "File opened.",
    "saved_fmt": "Saved: {name}",
    "err_open": "An error occurred while opening the file: {error}",
    "err_save": "An error occurred while saving the file: {error}",

    "pdf_title": "Export as PDF",
    "pdf_files": "PDF Files",
    "pdf_created": "PDF created: {name}",
    "err_pdf": "An error occurred while creating the PDF: {error}",

    "image_title": "Insert Image",
    "image_files": "Image Files",
    "err_image": "An unexpected error occurred while inserting the image: {error}",

    "table_title": "Insert Table",
    "table_rows": "Number of rows:",
    "table_cols": "Number of columns:",
    "color_title": "Text Color",

    "about_title": "About SpellCubes",
    "about_description": "A simple rich text editor.",
    "about_close": "Close",
}


class Translator:
    """i18n/<kod>.json dosyalarından metin yükler. Her hatada İngilizce'ye döner.
    Son seçilen dil i18n/user.preferences dosyasında tutulur (registry kullanılmaz)."""

    PREF_FILE = "user.preferences"

    def __init__(self, folder):
        self.folder = folder
        self.code = "en"
        self.strings = dict(DEFAULT_EN)

    @staticmethod
    def _read(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else None
        except (OSError, ValueError):
            return None

    # --- Tercih dosyası ---
    def _pref_path(self):
        return os.path.join(self.folder, self.PREF_FILE)

    def load_preference(self):
        """user.preferences dosyasından son seçilen dil kodunu okur. Yoksa '' döner."""
        data = self._read(self._pref_path())
        if data:
            code = data.get("language", "")
            if isinstance(code, str):
                return code
        return ""

    def save_preference(self):
        """Son seçilen dili i18n/user.preferences dosyasına yazar."""
        try:
            os.makedirs(self.folder, exist_ok=True)
            with open(self._pref_path(), "w", encoding="utf-8") as f:
                json.dump({"language": self.code}, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # Yazılamazsa (salt okunur klasör vb.) program çalışmaya devam eder

    def available(self):
        """{kod: görünen ad} döner. İngilizce her zaman vardır."""
        langs = {"en": "English"}
        try:
            for filename in sorted(os.listdir(self.folder)):
                if not filename.lower().endswith(".json"):
                    continue
                code = filename[:-5]
                data = self._read(os.path.join(self.folder, filename))
                if data is not None:
                    langs[code] = str(data.get("_name", code))
        except OSError:
            pass
        return langs

    def load(self, code):
        """Dili yükler. Dosya yoksa/bozuksa İngilizce kalır. Yüklenen kodu döner."""
        strings = dict(DEFAULT_EN)
        loaded = "en"
        try:
            code = os.path.basename(str(code or "en")).lower()
            data = self._read(os.path.join(self.folder, code + ".json"))
            if data:
                for key, value in data.items():
                    if isinstance(value, str) and not key.startswith("_"):
                        strings[key] = value
                loaded = code
        except Exception:
            strings = dict(DEFAULT_EN)
            loaded = "en"
        self.strings = strings
        self.code = loaded
        return loaded

    def t(self, key, **kwargs):
        text = self.strings.get(key) or DEFAULT_EN.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                try:
                    return DEFAULT_EN.get(key, key).format(**kwargs)
                except Exception:
                    return text
        return text


# ----------------------------------------------------------------------
#  Hakkında / Lisans penceresi
# ----------------------------------------------------------------------
class AboutDialog(QDialog):
    def __init__(self, parent, t):
        super().__init__(parent)
        self.setWindowTitle(t("about_title"))
        self.resize(520, 420)

        title = QLabel(f"<h2>{APP_NAME}</h2>")
        description = QLabel(t("about_description"))
        copyright_label = QLabel(COPYRIGHT_LINE)
        license_label = QLabel(
            f'License: <a href="{LICENSE_URL}">{LICENSE_NAME}</a>')
        license_label.setOpenExternalLinks(True)

        notice = QPlainTextEdit()
        notice.setReadOnly(True)
        notice.setPlainText(LICENSE_NOTICE)

        close_btn = QPushButton(t("about_close"))
        close_btn.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(copyright_label)
        layout.addWidget(license_label)
        layout.addWidget(notice)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)


# ----------------------------------------------------------------------
#  Bul ve Değiştir penceresi
# ----------------------------------------------------------------------
class FindReplaceDialog(QDialog):
    def __init__(self, parent, editor, t):
        super().__init__(parent)
        self.editor = editor
        self.t = t

        self.find_edit = QLineEdit()
        self.replace_edit = QLineEdit()
        self.case_check = QCheckBox()
        self.info_label = QLabel("")

        self.find_label = QLabel()
        self.replace_label = QLabel()
        self.find_btn = QPushButton()
        self.replace_btn = QPushButton()
        self.replace_all_btn = QPushButton()
        self.close_btn = QPushButton()

        layout = QGridLayout(self)
        layout.addWidget(self.find_label, 0, 0)
        layout.addWidget(self.find_edit, 0, 1, 1, 2)
        layout.addWidget(self.replace_label, 1, 0)
        layout.addWidget(self.replace_edit, 1, 1, 1, 2)
        layout.addWidget(self.case_check, 2, 1, 1, 2)
        layout.addWidget(self.find_btn, 3, 0)
        layout.addWidget(self.replace_btn, 3, 1)
        layout.addWidget(self.replace_all_btn, 3, 2)
        layout.addWidget(self.info_label, 4, 0, 1, 2)
        layout.addWidget(self.close_btn, 4, 2)

        self.find_btn.clicked.connect(self.find_next)
        self.replace_btn.clicked.connect(self.replace_one)
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.close_btn.clicked.connect(self.close)
        self.find_edit.returnPressed.connect(self.find_next)

        self.retranslate()

    def retranslate(self):
        t = self.t
        self.setWindowTitle(t("fr_title"))
        self.find_label.setText(t("fr_find"))
        self.replace_label.setText(t("fr_replace"))
        self.case_check.setText(t("fr_case"))
        self.find_btn.setText(t("fr_find_next"))
        self.replace_btn.setText(t("fr_replace_btn"))
        self.replace_all_btn.setText(t("fr_replace_all"))
        self.close_btn.setText(t("fr_close"))
        self.info_label.setText("")

    def _flags(self):
        if self.case_check.isChecked():
            return QTextDocument.FindFlag.FindCaseSensitively
        return QTextDocument.FindFlag(0)

    def open_dialog(self):
        selected = self.editor.textCursor().selectedText()
        if selected and "\u2029" not in selected:  # tek satırlık seçimse alana yaz
            self.find_edit.setText(selected)
        self.info_label.setText("")
        self.show()
        self.raise_()
        self.activateWindow()
        self.find_edit.setFocus()
        self.find_edit.selectAll()

    def find_next(self):
        text = self.find_edit.text()
        if not text:
            return False
        flags = self._flags()
        if self.editor.find(text, flags):
            self.info_label.setText("")
            return True
        # Sona gelindi, baştan devam et
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        if self.editor.find(text, flags):
            self.info_label.setText(self.t("fr_wrapped"))
            return True
        self.info_label.setText(self.t("fr_not_found"))
        return False

    def replace_one(self):
        text = self.find_edit.text()
        if not text:
            return
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        if self.case_check.isChecked():
            match = selected == text
        else:
            match = selected.lower() == text.lower()
        if cursor.hasSelection() and match:
            cursor.insertText(self.replace_edit.text())
        self.find_next()

    def replace_all(self):
        text = self.find_edit.text()
        if not text:
            return
        replacement = self.replace_edit.text()
        flags = self._flags()
        doc = self.editor.document()

        cursor = QTextCursor(doc)
        cursor.beginEditBlock()  # tek seferde geri alınabilsin
        count = 0
        while True:
            cursor = doc.find(text, cursor, flags)
            if cursor.isNull():
                break
            cursor.insertText(replacement)
            count += 1
        cursor.endEditBlock()
        self.info_label.setText(self.t("fr_replaced", count=count))


# ----------------------------------------------------------------------
#  Ana pencere
# ----------------------------------------------------------------------
class SpellCubesUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1000, 700)

        self.current_file = None

        # Dil sistemi: user.preferences -> sistem dili -> İngilizce
        self.i18n = Translator(I18N_DIR)
        self.t = self.i18n.t
        try:
            code = self.i18n.load_preference()
            if not code:
                code = QLocale.system().name().split("_")[0]
            self.i18n.load(code)
        except Exception:
            self.i18n.load("en")

        self.tr_actions = []   # (QAction, anahtar)
        self.tr_menus = []     # (QMenu, anahtar)

        self.editor = QTextEdit()
        self.editor.setFontPointSize(12)
        self.editor.setFontFamily("Arial")
        self.setCentralWidget(self.editor)

        self.find_dialog = FindReplaceDialog(self, self.editor, self.t)

        self.create_actions()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()

        # Sinyaller
        self.editor.currentCharFormatChanged.connect(self.update_toolbar_format)
        self.editor.cursorPositionChanged.connect(self.update_alignment_actions)
        self.editor.cursorPositionChanged.connect(self.update_list_actions)
        self.editor.cursorPositionChanged.connect(self.update_status)
        self.editor.textChanged.connect(self.update_status)
        self.editor.document().modificationChanged.connect(self.update_title)

        self.editor.document().setModified(False)
        self.update_title()
        self.update_status()

    # --- Yardımcı: aksiyon üretici (metin anahtarla çevrilir) ---
    def make_action(self, key, slot=None, shortcut=None, checkable=False):
        action = QAction(self.t(key), self)
        if shortcut:
            action.setShortcut(shortcut)
        action.setCheckable(checkable)
        if slot:
            action.triggered.connect(slot)
        self.tr_actions.append((action, key))
        return action

    def add_menu(self, key, parent_menu=None):
        if parent_menu is None:
            menu = self.menuBar().addMenu(self.t(key))
        else:
            menu = parent_menu.addMenu(self.t(key))
        self.tr_menus.append((menu, key))
        return menu

    # --- Aksiyonlar ---
    def create_actions(self):
        # Dosya
        self.new_action = self.make_action("act_new", self.new_file, QKeySequence.New)
        self.open_action = self.make_action("act_open", self.open_file, QKeySequence.Open)
        self.save_action = self.make_action("act_save", self.save_file, QKeySequence.Save)
        self.save_as_action = self.make_action("act_save_as", self.save_file_as,
                                               QKeySequence.SaveAs)
        self.pdf_action = self.make_action("act_pdf", self.export_pdf)
        self.print_action = self.make_action("act_print", self.print_document,
                                             QKeySequence.Print)
        self.exit_action = self.make_action("act_exit", self.close, "Ctrl+Q")

        # Düzen
        self.undo_action = self.make_action("act_undo", self.editor.undo, QKeySequence.Undo)
        # Yinele: Alt+Z
        self.redo_action = self.make_action("act_redo", self.editor.redo, "Alt+Z")
        self.cut_action = self.make_action("act_cut", self.editor.cut, QKeySequence.Cut)
        self.copy_action = self.make_action("act_copy", self.editor.copy, QKeySequence.Copy)
        self.paste_action = self.make_action("act_paste", self.editor.paste, QKeySequence.Paste)
        self.select_all_action = self.make_action("act_select_all", self.editor.selectAll,
                                                  QKeySequence.SelectAll)
        self.find_action = self.make_action("act_find", self.find_dialog.open_dialog,
                                            QKeySequence.Find)
        self.find_next_action = self.make_action("act_find_next", self.find_dialog.find_next,
                                                 "F3")

        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)
        self.cut_action.setEnabled(False)
        self.copy_action.setEnabled(False)
        self.editor.undoAvailable.connect(self.undo_action.setEnabled)
        self.editor.redoAvailable.connect(self.redo_action.setEnabled)
        self.editor.copyAvailable.connect(self.cut_action.setEnabled)
        self.editor.copyAvailable.connect(self.copy_action.setEnabled)

        # Temel biçimlendirme
        self.bold_action = self.make_action("act_bold", self.set_bold, "Ctrl+B", True)
        self.italic_action = self.make_action("act_italic", self.set_italic, "Ctrl+I", True)
        self.underline_action = self.make_action("act_underline", self.set_underline,
                                                 "Ctrl+U", True)

        # Renk ve boyut
        self.color_action = self.make_action("act_color", self.select_color)
        self.increase_size_action = self.make_action(
            "act_size_up", lambda: self.change_font_size(1), "Ctrl+.")
        self.decrease_size_action = self.make_action(
            "act_size_down", lambda: self.change_font_size(-1), "Ctrl+,")

        # Hizalama
        self.align_left_action = self.make_action(
            "act_left", lambda: self.editor.setAlignment(Qt.AlignLeft), checkable=True)
        self.align_center_action = self.make_action(
            "act_center", lambda: self.editor.setAlignment(Qt.AlignHCenter), checkable=True)
        self.align_right_action = self.make_action(
            "act_right", lambda: self.editor.setAlignment(Qt.AlignRight), checkable=True)
        self.align_justify_action = self.make_action(
            "act_justify", lambda: self.editor.setAlignment(Qt.AlignJustify), checkable=True)
        for action in (self.align_left_action, self.align_center_action,
                       self.align_right_action, self.align_justify_action):
            action.triggered.connect(self.update_alignment_actions)

        # Listeler (aç/kapa)
        self.bullet_list_action = self.make_action(
            "act_bullets", lambda: self.toggle_list(QTextListFormat.ListDisc), checkable=True)
        self.numbered_list_action = self.make_action(
            "act_numbered", lambda: self.toggle_list(QTextListFormat.ListDecimal), checkable=True)

        # Ekle
        self.image_action = self.make_action("act_image", self.insert_image)
        self.table_action = self.make_action("act_table", self.insert_table)

        # Yardım
        self.about_action = self.make_action("act_about", self.show_about)

    def create_menu_bar(self):
        file_menu = self.add_menu("menu_file")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.pdf_action)
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = self.add_menu("menu_edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addAction(self.select_all_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)
        edit_menu.addAction(self.find_next_action)

        insert_menu = self.add_menu("menu_insert")
        insert_menu.addAction(self.image_action)
        insert_menu.addAction(self.table_action)

        help_menu = self.add_menu("menu_help")
        self.language_menu = self.add_menu("menu_language", help_menu)
        self.language_menu.aboutToShow.connect(self.build_language_menu)
        self.build_language_menu()
        help_menu.addSeparator()
        help_menu.addAction(self.about_action)

    def create_toolbar(self):
        self.toolbar = QToolBar(self.t("toolbar_title"))
        toolbar = self.toolbar
        self.addToolBar(toolbar)

        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()

        # Font ve boyut
        self.font_combo = QFontComboBox(self)
        self.font_combo.setCurrentFont(QFont("Arial"))
        self.font_combo.currentFontChanged.connect(self.set_font)
        toolbar.addWidget(self.font_combo)

        self.size_combo = QComboBox(self)
        self.size_combo.setEditable(True)
        self.size_combo.setInsertPolicy(QComboBox.NoInsert)
        self.size_combo.addItems([str(s) for s in
                                  [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]])
        self.size_combo.setCurrentText("12")
        # Hem listeden seçimi hem elle yazıp Enter'a basmayı yakala
        self.size_combo.activated.connect(
            lambda i: self.apply_size(self.size_combo.itemText(i)))
        self.size_combo.lineEdit().returnPressed.connect(
            lambda: self.apply_size(self.size_combo.currentText()))
        toolbar.addWidget(self.size_combo)

        toolbar.addSeparator()
        toolbar.addAction(self.bold_action)
        toolbar.addAction(self.italic_action)
        toolbar.addAction(self.underline_action)

        toolbar.addSeparator()
        toolbar.addAction(self.color_action)
        toolbar.addSeparator()
        toolbar.addAction(self.increase_size_action)
        toolbar.addAction(self.decrease_size_action)

        toolbar.addSeparator()
        toolbar.addAction(self.align_left_action)
        toolbar.addAction(self.align_center_action)
        toolbar.addAction(self.align_right_action)
        toolbar.addAction(self.align_justify_action)

        toolbar.addSeparator()
        toolbar.addAction(self.bullet_list_action)
        toolbar.addAction(self.numbered_list_action)

        toolbar.addSeparator()
        toolbar.addAction(self.image_action)
        toolbar.addAction(self.table_action)

    def create_status_bar(self):
        self.status_label = QLabel("")
        self.statusBar().addPermanentWidget(self.status_label)

    # --- Dil menüsü ve dil değiştirme ---
    def build_language_menu(self):
        """i18n klasörünü tarar; yeni eklenen .json dosyaları yeniden başlatmadan görünür."""
        self.language_menu.clear()
        self.lang_group = QActionGroup(self)
        self.lang_group.setExclusive(True)
        for code, name in self.i18n.available().items():
            action = QAction(name, self, checkable=True)
            action.setData(code)
            action.setChecked(code == self.i18n.code)
            action.triggered.connect(lambda checked=False, c=code: self.set_language(c))
            self.lang_group.addAction(action)
            self.language_menu.addAction(action)

    def set_language(self, code):
        self.i18n.load(code)
        self.i18n.save_preference()  # i18n/user.preferences dosyasına yazar
        self.retranslate()

    def retranslate(self):
        for action, key in self.tr_actions:
            action.setText(self.t(key))
        for menu, key in self.tr_menus:
            menu.setTitle(self.t(key))
        self.toolbar.setWindowTitle(self.t("toolbar_title"))
        self.find_dialog.retranslate()
        self.update_title()
        self.update_status()

    def show_about(self):
        AboutDialog(self, self.t).exec()

    # --- Başlık ve durum çubuğu ---
    def update_title(self, *args):
        name = (QFileInfo(self.current_file).fileName()
                if self.current_file else self.t("untitled"))
        star = "*" if self.editor.document().isModified() else ""
        self.setWindowTitle(f"{star}{name} - {APP_NAME}")

    def update_status(self):
        text = self.editor.toPlainText()
        words = len(text.split())
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        self.status_label.setText(
            self.t("status_fmt", line=line, col=col, words=words, chars=len(text)))

    # --- Biçimlendirme yardımcıları ---
    def merge_format(self, fmt):
        """Seçili metne (ya da seçim yoksa sonradan yazılacak metne) biçimi uygular."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)  # seçili metne doğrudan uygula
        self.editor.mergeCurrentCharFormat(fmt)  # sonradan yazılacak metin için
        self.editor.setFocus()

    def set_font(self, font):
        fmt = QTextCharFormat()
        fmt.setFontFamilies([font.family()])
        self.merge_format(fmt)

    def apply_size(self, text):
        try:
            size = float(text.replace(",", "."))
        except ValueError:
            return
        if 1 <= size <= 200:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)
            self.merge_format(fmt)

    def set_bold(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if checked else QFont.Weight.Normal)
        self.merge_format(fmt)

    def set_italic(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontItalic(checked)
        self.merge_format(fmt)

    def set_underline(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(checked)
        self.merge_format(fmt)

    def update_toolbar_format(self, fmt):
        """İmleç hareket ettiğinde toolbar'daki seçimleri günceller."""
        # Sinyalleri engelle: yoksa toolbar güncellenirken metne biçim uygulanır
        self.font_combo.blockSignals(True)
        self.font_combo.setCurrentFont(fmt.font())
        self.font_combo.blockSignals(False)

        point_size = fmt.fontPointSize()
        if point_size <= 0:
            point_size = self.editor.font().pointSizeF() or 12
        size_text = str(int(point_size)) if float(point_size).is_integer() else str(point_size)
        self.size_combo.blockSignals(True)
        self.size_combo.setCurrentText(size_text)
        self.size_combo.blockSignals(False)

        self.bold_action.setChecked(fmt.font().bold())
        self.italic_action.setChecked(fmt.fontItalic())
        self.underline_action.setChecked(fmt.fontUnderline())

        self.update_alignment_actions()
        self.update_list_actions()

    def update_alignment_actions(self):
        """Hizalama butonlarını o anki hizalamaya göre günceller."""
        alignment = self.editor.textCursor().blockFormat().alignment()

        self.align_left_action.setChecked(bool(alignment & Qt.AlignLeft))
        self.align_center_action.setChecked(bool(alignment & Qt.AlignHCenter))
        self.align_right_action.setChecked(bool(alignment & Qt.AlignRight))
        self.align_justify_action.setChecked(bool(alignment & Qt.AlignJustify))

    def update_list_actions(self):
        """Liste butonlarını, imleç liste öğesindeyse aktif hale getirir."""
        current_list = self.editor.textCursor().currentList()
        style = current_list.format().style() if current_list else None

        self.bullet_list_action.setChecked(style == QTextListFormat.ListDisc)
        self.numbered_list_action.setChecked(style == QTextListFormat.ListDecimal)

    def toggle_list(self, style):
        """Aynı butona tekrar basılınca listeden çıkar."""
        cursor = self.editor.textCursor()
        current_list = cursor.currentList()
        cursor.beginEditBlock()
        if current_list and current_list.format().style() == style:
            current_list.remove(cursor.block())
            block_fmt = cursor.blockFormat()
            block_fmt.setIndent(0)
            cursor.setBlockFormat(block_fmt)
        else:
            cursor.createList(style)
        cursor.endEditBlock()
        self.update_list_actions()

    # --- Renk ve boyut ---
    def select_color(self):
        cursor = self.editor.textCursor()  # dialog açılmadan önce seçimi sakla
        brush = self.editor.currentCharFormat().foreground()
        initial = brush.color() if brush.style() != Qt.NoBrush else QColor(0, 0, 0)
        color = QColorDialog.getColor(initial, self, self.t("color_title"))
        if not color.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setForeground(QBrush(color, Qt.SolidPattern))
        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
            self.editor.setTextCursor(cursor)
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def change_font_size(self, delta):
        current_size = self.editor.fontPointSize() or 12
        new_size = current_size + delta
        if 6 <= new_size <= 72:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(new_size)
            self.merge_format(fmt)
            self.size_combo.setCurrentText(str(int(new_size)))

    # --- Dosya yönetimi ---
    def file_filter(self):
        return (f"{self.t('spellcubes_files')} (*.cube);;"
                f"{self.t('all_files')} (*)")

    def maybe_save(self):
        """Kaydedilmemiş değişiklik varsa kullanıcıya sorar. False dönerse işlem iptal."""
        if not self.editor.document().isModified():
            return True

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle(APP_NAME)
        box.setText(self.t("sp_text"))
        box.setInformativeText(self.t("sp_info"))
        save_btn = box.addButton(self.t("sp_save"), QMessageBox.AcceptRole)
        box.addButton(self.t("sp_discard"), QMessageBox.DestructiveRole)
        cancel_btn = box.addButton(self.t("sp_cancel"), QMessageBox.RejectRole)
        box.setDefaultButton(save_btn)
        box.exec()

        clicked = box.clickedButton()
        if clicked is save_btn:
            return self.save_file()
        if clicked is cancel_btn:
            return False
        return True  # Kaydetme

    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    def new_file(self):
        if not self.maybe_save():
            return
        self.editor.clear()
        self.current_file = None
        self.editor.document().setModified(False)
        self.update_title()

    def open_file(self):
        if not self.maybe_save():
            return
        filename, _ = QFileDialog.getOpenFileName(
            self, self.t("open_title"), "", self.file_filter())
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        """Verilen yoldaki dosyayı doğrudan açar (çift tıklama ile açılış için de kullanılır)."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.editor.setHtml(html_content)
            self.current_file = filename
            self.editor.document().setModified(False)
            self.editor.document().clearUndoRedoStacks()
            self.update_title()
            self.statusBar().showMessage(self.t("file_opened"), 3000)
        except Exception as e:
            QMessageBox.critical(self, self.t("error"), self.t("err_open", error=e))

    def save_file(self):
        if self.current_file:
            return self._save_to_path(self.current_file)
        return self.save_file_as()

    def save_file_as(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, self.t("save_as_title"), "", self.file_filter())
        if not filename:
            return False
        if not filename.endswith('.cube'):
            filename += '.cube'
        return self._save_to_path(filename)

    def _save_to_path(self, path):
        html_content = self.editor.toHtml()  # Resimler Base64 olarak HTML içinde kalır
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            QMessageBox.critical(self, self.t("error"), self.t("err_save", error=e))
            return False
        self.current_file = path
        self.editor.document().setModified(False)
        self.update_title()
        self.statusBar().showMessage(
            self.t("saved_fmt", name=QFileInfo(path).fileName()), 3000)
        return True

    # --- PDF ve yazdırma ---
    def export_pdf(self):
        suggested = ""
        if self.current_file:
            suggested = QFileInfo(self.current_file).completeBaseName() + ".pdf"
        filename, _ = QFileDialog.getSaveFileName(
            self, self.t("pdf_title"), suggested, f"{self.t('pdf_files')} (*.pdf)")
        if not filename:
            return
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            self.editor.document().print_(printer)
            self.statusBar().showMessage(
                self.t("pdf_created", name=QFileInfo(filename).fileName()), 4000)
        except Exception as e:
            QMessageBox.critical(self, self.t("error"), self.t("err_pdf", error=e))

    def print_document(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.Accepted:
            self.editor.document().print_(printer)

    # --- Resim ekleme (Pillow ile Base64) ---
    def insert_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, self.t("image_title"), "",
            f"{self.t('image_files')} (*.png *.jpg *.jpeg *.gif);;"
            f"{self.t('all_files')} (*)")
        if not filename:
            return
        try:
            cursor = self.editor.textCursor()
            img = Image.open(filename)

            image_format_str = QFileInfo(filename).suffix().upper()
            if not image_format_str or image_format_str == "JPG":
                image_format_str = "JPEG"
            elif image_format_str == "GIF":
                image_format_str = "PNG"

            save_format = image_format_str
            # JPEG şeffaflık (alpha kanalı) desteklemez
            if save_format == "JPEG" and img.mode in ('RGBA', 'LA', 'P'):
                save_format = "PNG"
                image_format_str = "PNG"

            buffer = io.BytesIO()
            img.save(buffer, format=save_format)
            base64_data = base64.b64encode(buffer.getvalue()).decode()
            mime_type = f"image/{image_format_str.lower()}"

            cursor.insertHtml(f'<img src="data:{mime_type};base64,{base64_data}">')
        except Exception as e:
            QMessageBox.critical(self, self.t("error"), self.t("err_image", error=e))

    # --- Tablo ekleme ---
    def insert_table(self):
        rows, ok_rows = QInputDialog.getInt(
            self, self.t("table_title"), self.t("table_rows"), 3, 1, 50)
        if not ok_rows:
            return
        cols, ok_cols = QInputDialog.getInt(
            self, self.t("table_title"), self.t("table_cols"), 3, 1, 50)
        if not ok_cols:
            return

        table_format = QTextTableFormat()
        table_format.setBorder(1)
        table_format.setCellPadding(4)
        self.editor.textCursor().insertTable(rows, cols, table_format)


# Uygulamayı çalıştırma bloğu
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = SpellCubesUygulamasi()
        window.show()

        # Dışarıdan (çift tıklama ile) gelen dosyayı aç
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            window.load_file(sys.argv[1])

        sys.exit(app.exec())
    except Exception as e:
        import traceback
        print("-" * 50)
        print(f"Critical error while starting the application:\n{e}\n\nTraceback:\n{traceback.format_exc()}")
        print("-" * 50)
        sys.exit(1)