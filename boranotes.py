import sys
import os
import sqlite3
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QTextEdit, QHBoxLayout, QLineEdit, QLabel, QMessageBox, QCheckBox, QSplitter, QMenu, QGridLayout, QWidgetAction 
)
from PyQt6.QtGui import (
    QFont, QIcon, QTextCursor, QTextCharFormat, QShortcut, QKeySequence, QColor,
    QDesktopServices, QTextFrameFormat, QTextBlockFormat, QSyntaxHighlighter
)
from PyQt6.QtCore import Qt, QTimer, QMimeData, QPoint, QUrl, QSize

from themes import get_theme
from about import get_about_content, get_about_title


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


DB_FILE = "notes.db"
MONTHS = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
    7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}

class CustomTextEdit(QTextEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_font = QFont("Calibri", 11)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_custom_context_menu)

    def show_custom_context_menu(self, position):
        custom_menu = QMenu(self)
        custom_menu.setFont(QFont("Calibri", 9))
        
        main_window = self.window()
        if not main_window or not hasattr(main_window, 'current_theme'):
            return  
        
        has_selected_text = self.textCursor().hasSelection()
        has_any_text = not self.document().isEmpty()
        
        theme_name = main_window.current_theme
        theme = get_theme(theme_name)
        custom_menu.setStyleSheet(theme["menu_style"])

        format_menu = custom_menu.addMenu(" ✒️  Форматирование                ")
        format_menu.setStyleSheet(theme["menu_style"])
        
        bold_action = format_menu.addAction("Ctrl + B  | Жирный  ")
        italic_action = format_menu.addAction("Ctrl + I  | Курсив  ")
        underline_action = format_menu.addAction("Ctrl + U  | Подчеркнутый  ")
        strikethrough_action = format_menu.addAction("Ctrl + T  | Зачеркнутый  ")  
        highlight_action = format_menu.addAction("Ctrl + H  | Выделить ")
        format_menu.addSeparator()
        clear_format_action = format_menu.addAction("Очистить форматирование")

        bold_action.setEnabled(has_selected_text)
        italic_action.setEnabled(has_selected_text)
        underline_action.setEnabled(has_selected_text)
        strikethrough_action.setEnabled(has_selected_text)
        highlight_action.setEnabled(has_selected_text)
        clear_format_action.setEnabled(has_selected_text)
        
        special_symbols_menu = custom_menu.addMenu(" 🔣  Специальные символы                ")
        special_symbols_menu.setStyleSheet(theme["menu_style"])
        
        empty_circle_action = special_symbols_menu.addAction("○ Пустой кружок")
        full_circle_action = special_symbols_menu.addAction("● Тёмный кружок")
        dark_arrow_action = special_symbols_menu.addAction("➤ Тёмная стрелочка")
        check_mark_action = special_symbols_menu.addAction("✔ Галочка/готово!")
        cross_mark_action = special_symbols_menu.addAction("✘ Крестик/не готово!")
        music_note_action = special_symbols_menu.addAction("♫ Музыкальная нота")
        heart_note_action = special_symbols_menu.addAction("♥︎ Заполененное сердечко")
        
        special_emoji_menu = custom_menu.addMenu(" 😊  Специальные эмоджи                ")
        special_emoji_menu.setStyleSheet(theme["menu_style"])
        
        purple_heart_action = special_emoji_menu.addAction("💜 Фиолетовое сердечко")
        pushpin_action = special_emoji_menu.addAction("📌 Канцелярская кнопка")
        star_action = special_emoji_menu.addAction("⭐ Звездочка")
        calendar_action = special_emoji_menu.addAction("📅 Календарик")
        note_action = special_emoji_menu.addAction("📝 Заметка")
        exclamation_action = special_emoji_menu.addAction("‼️ Восклицательный знак")
        coffee_action = special_emoji_menu.addAction("☕ Кофеек")
        cake_action = special_emoji_menu.addAction("🍰 Тортик")
        pill_action = special_emoji_menu.addAction("💊 Витаминка")
        done_action = special_emoji_menu.addAction("✅ Сделано!")
        cross_action = special_emoji_menu.addAction("❌ Крестик")
        merch_action = special_emoji_menu.addAction("💸 На мерч бтс")

        custom_menu.addSeparator()
        copy_action = custom_menu.addAction(" 📋  Копировать ")
        copy_action.triggered.connect(self.copy)
        copy_action.setEnabled(has_selected_text)
        
        cut_action = custom_menu.addAction(" ✂️  Вырезать ")
        cut_action.triggered.connect(self.cut)
        cut_action.setEnabled(has_selected_text)
        
        paste_action = custom_menu.addAction(" 📌  Вставить ")
        paste_action.triggered.connect(self.paste)
        
        select_all_action = custom_menu.addAction(" ✅  Выделить всё ")
        select_all_action.triggered.connect(self.selectAll)
        select_all_action.setEnabled(has_any_text)

        custom_menu.addSeparator()

        bold_action.triggered.connect(lambda: self.apply_formatting('bold'))
        italic_action.triggered.connect(lambda: self.apply_formatting('italic'))
        underline_action.triggered.connect(lambda: self.apply_formatting('underline'))
        strikethrough_action.triggered.connect(lambda: self.apply_formatting('strikethrough'))
        highlight_action.triggered.connect(lambda: self.apply_formatting('highlight'))
        
        clear_format_action.triggered.connect(self.clear_formatting)
        
        empty_circle_action.triggered.connect(lambda: self.insert_special_character("○"))
        full_circle_action.triggered.connect(lambda: self.insert_special_character("●"))
        dark_arrow_action.triggered.connect(lambda: self.insert_special_character("➤"))
        check_mark_action.triggered.connect(lambda: self.insert_special_character("✔"))
        cross_mark_action.triggered.connect(lambda: self.insert_special_character("✘"))
        music_note_action.triggered.connect(lambda: self.insert_special_character("♫"))
        heart_note_action.triggered.connect(lambda: self.insert_special_character("♥︎"))

        purple_heart_action.triggered.connect(lambda: self.insert_special_character("💜"))
        pushpin_action.triggered.connect(lambda: self.insert_special_character("📌"))
        star_action.triggered.connect(lambda: self.insert_special_character("⭐"))
        calendar_action.triggered.connect(lambda: self.insert_special_character("📅"))
        note_action.triggered.connect(lambda: self.insert_special_character("📝"))
        exclamation_action.triggered.connect(lambda: self.insert_special_character("❗"))
        coffee_action.triggered.connect(lambda: self.insert_special_character("☕"))
        cake_action.triggered.connect(lambda: self.insert_special_character("🍰"))
        pill_action.triggered.connect(lambda: self.insert_special_character("💊"))
        done_action.triggered.connect(lambda: self.insert_special_character("✅"))
        cross_action.triggered.connect(lambda: self.insert_special_character("❌"))
        merch_action.triggered.connect(lambda: self.insert_special_character("💸"))

        custom_menu.exec(self.mapToGlobal(position))

    def apply_formatting(self, format_type):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return 
        
        format = QTextCharFormat()
        current_format = cursor.charFormat()
        
        if format_type == 'bold':
            is_bold = current_format.fontWeight() == QFont.Weight.Bold
            format.setFontWeight(QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
        elif format_type == 'italic':
            format.setFontItalic(not current_format.fontItalic())
        elif format_type == 'underline':
            format.setFontUnderline(not current_format.fontUnderline())
        elif format_type == 'strikethrough':
            format.setFontStrikeOut(not current_format.fontStrikeOut())
        elif format_type == 'highlight':
            main_window = self.window()
            theme_name = main_window.current_theme if hasattr(main_window, 'current_theme') else "light"
            highlight_color = QColor("#775c88") if theme_name == "dark" else QColor("#e4d5ff")
            
            current_color = current_format.background().color()
            if current_color.name() in [highlight_color.name(), "#e4d5ff", "#775c88"]:
                format.setBackground(QColor("transparent"))
            else:
                format.setBackground(highlight_color)
        
        cursor.mergeCharFormat(format)

    def insert_special_character(self, character):
        cursor = self.textCursor()
        cursor.insertText(character)
        self.setTextCursor(cursor)

    def clear_formatting(self, format_type=None):
        cursor = self.textCursor()
        format = QTextCharFormat()
        format.setFont(self.default_font)
        format.setBackground(QColor("transparent"))
        cursor.mergeCharFormat(format)

    def insertFromMimeData(self, source: QMimeData):
        cursor = self.textCursor()
        default_format = QTextCharFormat()
        default_format.setFont(self.default_font)
        cursor.insertText(source.text())
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(default_format)

class NotesApp(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.setWindowTitle("BORA NOTES")
        self.setGeometry(100, 100, 987, 693)
        self.setMinimumHeight(500)

        self.current_note_id = None
        self.skip_delete_confirmation = False
        self._notes_cache = {}
        self.need_save = False
        self.is_notes_list_visible = True
        self.initial_notes_list_width = 200
        self.current_theme = "light"  

        self._save_timer = QTimer()
        self._save_timer.setInterval(1000)
        self._save_timer.timeout.connect(self._perform_auto_save)

        self.create_database()
        
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'sort_method'")
                if not cursor.fetchone():
                    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                                ("sort_method", "date_desc"))
                    conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при установке сортировки по умолчанию: {e}")
        
        self.load_theme_setting()
        self.initUI()
        self.load_notes()

        if self.is_first_launch():
            self.new_note()
            self.notes_list.setCurrentRow(0)
        else:
            self.load_last_note()

        self.text_editor.setAcceptRichText(True)
        self.setup_shortcuts()
        self.splitter.splitterMoved.connect(self.check_list_visibility)
        self.title_input.textChanged.connect(self.update_note_title)

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.left_container = QWidget()
        self.left_container.setMinimumWidth(10)
        self.left_container.setMaximumWidth(self.width() - 30)
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.search_bar = QLineEdit()
        self.search_bar.setFixedHeight(24)
        self.search_bar.setPlaceholderText("Поиск по записям")
        self.search_bar.textChanged.connect(self.search_notes)
        left_layout.addWidget(self.search_bar)

        self.notes_list = QListWidget()
        self.notes_list.setWordWrap(True)  
        self.notes_list.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.notes_list.itemClicked.connect(self.load_note)
        self.notes_list.currentItemChanged.connect(self.on_item_selection_changed)
        self.notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_notes_list_context_menu)
        left_layout.addWidget(self.notes_list)

        self.right_container = QWidget()
        self.right_container.setMinimumWidth(90)
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        buttons_layout = QHBoxLayout()
        
        self.toggle_button = QPushButton("◀")
        self.toggle_button.setFixedSize(24, 24)
        self.toggle_button.clicked.connect(self.toggle_notes_list)
        self.toggle_button.setToolTip("Скрыть/показать список заметок")

        self.btn_new = QPushButton("✏️")
        self.btn_new.setFixedSize(24, 24)
        self.btn_new.clicked.connect(self.new_note)
        self.btn_new.setToolTip("Создать новую заметку")

        self.btn_delete = QPushButton("🗑️")
        self.btn_delete.setFixedSize(24, 24)
        self.btn_delete.clicked.connect(self.delete_note)
        self.btn_delete.setToolTip("Удалить текущую заметку")

        self.button_separator = QWidget()
        self.button_separator.setFixedSize(1, 24)
        self.button_separator.setStyleSheet("background-color: #ccc;")  # Цвет разделителя

        self.btn_color = QPushButton("🎨")
        self.btn_color.setFixedSize(24, 24)
        self.btn_color.clicked.connect(self.show_color_palette)
        self.btn_color.setToolTip("Изменить цвет текста")
        self.btn_color.setEnabled(False)

        self.btn_size = QPushButton("🤏")
        self.btn_size.setFixedSize(24, 24)
        self.btn_size.clicked.connect(self.show_size_menu)
        self.btn_size.setToolTip("Изменить размер текста")
        self.btn_size.setEnabled(False)

        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.btn_new)
        buttons_layout.addWidget(self.btn_delete)
        buttons_layout.addWidget(self.button_separator)
        buttons_layout.addWidget(self.btn_color)
        buttons_layout.addWidget(self.btn_size)  
        buttons_layout.addStretch()
        self.right_layout.addLayout(buttons_layout)

        self.editor_container = QWidget()
        editor_layout = QVBoxLayout(self.editor_container)
        editor_layout.setContentsMargins(10, 10, 10, 10)
        editor_layout.setSpacing(10)

        self.title_input = QLineEdit()
        self.title_input.setFont(QFont("Calibri", 14, QFont.Weight.Bold))
        self.title_input.setPlaceholderText("Без Названия")
        self.title_input.textChanged.connect(self.auto_save)
        self.title_input.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.title_input.customContextMenuRequested.connect(self.show_title_context_menu)
        self.title_input.setTextMargins(-3, 6, 0, 0)  

        self.separator = QWidget()
        self.separator.setFixedHeight(1)

        self.text_editor = CustomTextEdit()
        self.text_editor.setFont(QFont("Calibri", 11))
        self.text_editor.textChanged.connect(self.auto_save)
        self.text_editor.textChanged.connect(self.auto_format)
        self.text_editor.textChanged.connect(self.update_counter)
        self.text_editor.selectionChanged.connect(self.update_color_button_state)  
        self.text_editor.setViewportMargins(1, 0, 0, 0)

        editor_layout.addWidget(self.title_input)
        editor_layout.addWidget(self.separator)
        editor_layout.addWidget(self.text_editor)
        self.right_layout.addWidget(self.editor_container)

        self.splitter.addWidget(self.left_container)
        self.splitter.addWidget(self.right_container)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([self.initial_notes_list_width, 600])
        self.splitter.setCollapsible(1, False)
        self.splitter.setHandleWidth(3)

        layout.addWidget(self.splitter)

        bottom_panel = QWidget()
        bottom_panel.setFixedHeight(23)
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(1, 0, 0, 0)

        self.sort_button = QPushButton("🗃")
        self.sort_button.setFixedSize(25, 23)
        self.sort_button.clicked.connect(self.show_sort_menu)
        self.sort_button.setToolTip("Сортировка заметок")
        bottom_layout.addWidget(self.sort_button)

        self.category_button = QPushButton("🗂️")
        self.category_button.setFixedSize(25, 23)
        self.category_button.clicked.connect(self.show_category_menu)
        self.category_button.setToolTip("Категории заметок")
        bottom_layout.addWidget(self.category_button)

        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(25, 23)
        self.settings_button.clicked.connect(self.show_settings)
        self.settings_button.setStyleSheet("margin-left: -5px;")
        self.settings_button.setToolTip("Настройки")
        bottom_layout.addWidget(self.settings_button)

        self.spotify_button = QPushButton("💜")
        self.spotify_button.setFixedSize(25, 23)
        self.spotify_button.clicked.connect(self.open_spotify)
        self.spotify_button.setStyleSheet("margin-left: -5px;")
        self.spotify_button.setToolTip("Открыть Spotify")
        bottom_layout.addWidget(self.spotify_button)

        bottom_layout.addStretch()

        self.counter_label = QLabel()
        bottom_layout.addWidget(self.counter_label)

        layout.addWidget(bottom_panel)
        self.setLayout(layout)
        
        self.apply_theme(self.current_theme)

    def show_title_context_menu(self, position):
        context_menu = QMenu(self)
        context_menu.setFont(QFont("Calibri", 9))
        
        theme = get_theme(self.current_theme)
        context_menu.setStyleSheet(theme["menu_style"])
        
        has_selected_text = self.title_input.hasSelectedText()
        has_any_text = bool(self.title_input.text())
        
        copy_action = context_menu.addAction(" 📋  Копировать ")
        copy_action.triggered.connect(self.title_input.copy)
        copy_action.setEnabled(has_selected_text)

        cut_action = context_menu.addAction(" ✂️  Вырезать ")
        cut_action.triggered.connect(self.title_input.cut)
        cut_action.setEnabled(has_selected_text)
        
        paste_action = context_menu.addAction(" 📌  Вставить ")
        paste_action.triggered.connect(self.title_input.paste)
        
        context_menu.exec(self.title_input.mapToGlobal(position))

    def open_spotify(self):
        show_spotify_confirmation = True
        
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'show_spotify_confirmation'")
                result = cursor.fetchone()
                if result and result[0] == "False":
                    show_spotify_confirmation = False
        except sqlite3.Error as e:
            print(f"Ошибка при проверке кнопки Spotify: {e}")
        
        if show_spotify_confirmation:
            msg = QMessageBox()
            msg.setWindowTitle("Открыть Spotify")
            msg.setText("Вы хотите открыть сайт Spotify? Откроется страница с Вашими любимыми треками в браузере.")
            checkbox = QCheckBox("Больше не напоминать")
            msg.setCheckBox(checkbox)
            
            theme = get_theme(self.current_theme)
            msg.setStyleSheet(theme["message_box"])
            
            yes_button = QPushButton("Да")
            no_button = QPushButton("Нет")
            msg.addButton(yes_button, QMessageBox.ButtonRole.YesRole)
            msg.addButton(no_button, QMessageBox.ButtonRole.NoRole)
            msg.exec()
            
            if checkbox.isChecked():
                try:
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                                    ("show_spotify_confirmation", "False"))
                        conn.commit()
                except sqlite3.Error as e:
                    print(f"Ошибка при сохранении настройки Spotify: {e}")
            
            if msg.clickedButton() != yes_button:
                return
        
        QDesktopServices.openUrl(QUrl("https://open.spotify.com/collection/tracks"))

    def update_note_title(self):
        if not self.current_note_id:
            return
            
        title = self.title_input.text().strip()
        is_pinned = self._notes_cache[self.current_note_id].get('pinned', False)
        
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == self.current_note_id:
                current_text = item.text()
                date_line = current_text.split('\n')[1] if '\n' in current_text else ""
                new_title = title if title else "Без Названия"
                display_title = f"⭐ {new_title}" if is_pinned else new_title
                item.setText(f"{display_title}\n{date_line}")
                break
        
        if self.current_note_id in self._notes_cache:
            self._notes_cache[self.current_note_id]['title'] = title

    def show_notes_list_context_menu(self, position):
        theme = get_theme(self.current_theme)
        context_menu = QMenu(self)
        context_menu.setStyleSheet(theme["menu_style"])
        
        item = self.notes_list.itemAt(position)
        
        if item:
            note_id = item.data(Qt.ItemDataRole.UserRole)
            is_pinned = self._notes_cache[note_id].get('pinned', False)
            
            pinned_count = sum(1 for note in self._notes_cache.values() if note.get('pinned', False))
            
            pin_action = context_menu.addAction("⭐ Открепить" if is_pinned else "⭐ Закрепить")
            pin_action.triggered.connect(lambda: self.toggle_pin_status(note_id))
            
            if not is_pinned and pinned_count >= 3:
                pin_action.setEnabled(False)
                pin_action.setText("⭐ Закрепить (достигнут лимит)")
            
            delete_action = context_menu.addAction(" ❌ Удалить запись ")
            delete_action.triggered.connect(self.delete_note)
            
            context_menu.addSeparator()
            
            current_categories = self._notes_cache[note_id].get('categories', [])
            
            category_menu = context_menu.addMenu("🗂️ Добавить в категорию")
            category_menu.setStyleSheet(theme["menu_style"])
            
            categories = [
                {"icon": "📓", "name": "Личное", "id": "personal"},
                {"icon": "📚", "name": "Учеба", "id": "study"},
                {"icon": "👔", "name": "Работа", "id": "work"},
                {"icon": "🏡", "name": "Ежедневное", "id": "daily"},
                {"icon": "☁️", "name": "Вдохновение", "id": "inspiration"}
            ]
            
            if len(current_categories) >= 2:
                category_menu.setEnabled(False)
                category_menu.setTitle("🗂️ Добавить в категорию (достигнут лимит)")
            else:
                for category in categories:
                    if category["id"] not in current_categories:
                        action = category_menu.addAction(f"{category['icon']} {category['name']}")
                        action.triggered.connect(lambda checked, cat=category["id"]: self.add_note_to_category(note_id, cat))
            
            if current_categories:
                remove_category_menu = context_menu.addMenu("🗑️ Убрать из категории")
                remove_category_menu.setStyleSheet(theme["menu_style"])
                
                for cat_id in current_categories:
                    category_info = next((c for c in categories if c["id"] == cat_id), None)
                    if category_info:
                        action = remove_category_menu.addAction(f"{category_info['icon']} {category_info['name']}")
                        action.triggered.connect(lambda checked, cat=cat_id: self.remove_note_from_category(note_id, cat))
        else:
            new_action = context_menu.addAction(" ✏️ Создать запись ")
            new_action.triggered.connect(self.new_note)
        
        context_menu.exec(self.notes_list.mapToGlobal(position))


    def add_note_to_category(self, note_id, category):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM categories WHERE note_id = ?", (note_id,))
                category_count = cursor.fetchone()[0]
                
                if category_count >= 2:
                    QMessageBox.information(self, "Ограничение", "Заметка может быть добавлена максимум в 2 категории")
                    return
                
                cursor.execute("INSERT OR IGNORE INTO categories (note_id, category) VALUES (?, ?)", 
                            (note_id, category))
                conn.commit()
                
                if note_id in self._notes_cache:
                    categories = self._notes_cache[note_id].get('categories', [])
                    if category not in categories:
                        categories.append(category)
                        self._notes_cache[note_id]['categories'] = categories
                
                current_row = self.notes_list.currentRow()
                self.load_notes()

                for i in range(self.notes_list.count()):
                    item = self.notes_list.item(i)
                    if item and item.data(Qt.ItemDataRole.UserRole) == note_id:
                        self.notes_list.setCurrentRow(i)
                        break
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить заметку в категорию: {str(e)}")

    def remove_note_from_category(self, note_id, category):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM categories WHERE note_id = ? AND category = ?", 
                            (note_id, category))
                conn.commit()
                
                if note_id in self._notes_cache:
                    categories = self._notes_cache[note_id].get('categories', [])
                    if category in categories:
                        categories.remove(category)
                        self._notes_cache[note_id]['categories'] = categories
                
                current_row = self.notes_list.currentRow()
                self.load_notes()
                
                for i in range(self.notes_list.count()):
                    item = self.notes_list.item(i)
                    if item and item.data(Qt.ItemDataRole.UserRole) == note_id:
                        self.notes_list.setCurrentRow(i)
                        break
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось удалить заметку из категории: {str(e)}")

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = get_theme(theme_name)
        
        self.setStyleSheet(theme["main_window"])
        self.notes_list.setStyleSheet(theme["notes_list"] + """
            QListWidget::item {
                padding: 5px;
                min-height: 40px;
            }
        """)
        self.search_bar.setStyleSheet(theme["search_bar"])
        self.editor_container.setStyleSheet(theme["editor_container"])
        self.text_editor.setStyleSheet(theme["text_editor"])
        self.title_input.setStyleSheet(theme["title_input"])
        self.separator.setStyleSheet(theme["separator"])
        self.counter_label.setStyleSheet(theme["counter_label"])
        if hasattr(self, 'empty_state_label') and self.empty_state_label:
            self.empty_state_label.setStyleSheet(theme["empty_state_label"])
        
        self.toggle_button.setStyleSheet(theme["button_style"])
        self.btn_new.setStyleSheet(theme["button_style"])
        self.btn_delete.setStyleSheet(theme["button_style"])
        self.sort_button.setStyleSheet(theme["sort_button"])
        self.category_button.setStyleSheet(theme["sort_button"])  
        self.settings_button.setStyleSheet(theme["settings_button"])
        self.spotify_button.setStyleSheet(theme["settings_button"])
        
        separator_color = "#555555" if theme_name == "dark" else "#ccc"
        self.button_separator.setStyleSheet(f"background-color: {separator_color};")
        
        if hasattr(self, 'btn_color'):
            self.update_color_button_state()

        QApplication.instance().setStyleSheet(theme["tooltip_style"])
        
        current_item = self.notes_list.currentItem()
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) in self._notes_cache:
                note_id = item.data(Qt.ItemDataRole.UserRole)
                if self._notes_cache[note_id].get('pinned', False):
                    is_selected = (item == current_item)
                    
                    if theme_name == "light":
                        if is_selected:
                            item.setBackground(QColor("#eecbe3"))  
                        else:
                            item.setBackground(QColor("#f1dbea"))  
                    else:
                        if is_selected:
                            item.setBackground(QColor("#858585")) 
                        else:
                            item.setBackground(QColor("#484444")) 
        
        self.update_highlight_color()
        self.save_theme_setting(theme_name)


    def update_highlight_color(self):
        highlight_color = QColor("#775c88") if self.current_theme == "dark" else QColor("#e4d5ff")
        old_highlight_color = QColor("#e4d5ff") if self.current_theme == "dark" else QColor("#775c88")
        
        cursor = self.text_editor.textCursor()
        current_position = cursor.position()
        
        doc_cursor = QTextCursor(self.text_editor.document())
        doc_cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        while not doc_cursor.atEnd():
            doc_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
            
            char_format = doc_cursor.charFormat()
            bg_color = char_format.background().color()
            
            if bg_color.name() in [old_highlight_color.name(), "#e4d5ff", "#775c88"]:
                new_format = QTextCharFormat()
                new_format.setBackground(highlight_color)
                doc_cursor.mergeCharFormat(new_format)
            
            doc_cursor.clearSelection()
        
        cursor.setPosition(current_position)
        self.text_editor.setTextCursor(cursor)

    def load_theme_setting(self):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
                if cursor.fetchone() is None:
                    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
                    conn.commit()
                    return
                    
                cursor.execute("SELECT value FROM settings WHERE key = 'theme'")
                result = cursor.fetchone()
                if result:
                    self.current_theme = result[0]
                    print(f"Загружена тема: {self.current_theme}")
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке темы: {e}")
            self.current_theme = "light"

    def save_theme_setting(self, theme_name):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
                if cursor.fetchone() is None:

                    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
                
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                            ("theme", theme_name))
                conn.commit()
                print(f"Сохранена тема: {theme_name}")
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении темы: {e}")

    def show_settings(self):
        settings_menu = QMenu(self)
        settings_menu.setFont(QFont("Calibri", 9))
        
        theme = get_theme(self.current_theme)
        settings_menu.setStyleSheet(theme["menu_style"])
        
        theme_menu = settings_menu.addMenu("Тема оформления")
        theme_menu.setStyleSheet(theme["menu_style"])
        
        light_theme = theme_menu.addAction("🌞 Светлая тема")
        dark_theme = theme_menu.addAction("🌛 Темная тема")
        
        light_theme.triggered.connect(lambda: self.apply_theme("light"))
        dark_theme.triggered.connect(lambda: self.apply_theme("dark"))

        settings_menu.addSeparator()
        
        about_action = settings_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about_info)
    
        settings_menu.exec(self.settings_button.mapToGlobal(QPoint(0, -settings_menu.sizeHint().height())))

    def show_about_info(self):
        about_title = get_about_title()
        about_content = get_about_content()
        
        html_content = f"""
        <div style="font-family: Calibri; font-size: 12pt;">
        {about_content.replace("\n", "<br>")}
        </div>
        """
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM notes WHERE title = ?", (about_title,))
            result = cursor.fetchone()
            
            if result:
                note_id = result[0]
                for i in range(self.notes_list.count()):
                    item = self.notes_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == note_id:
                        self.notes_list.setCurrentItem(item)
                        self.load_note()
                        break
                return

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (title, content, created_at, last_accessed) VALUES (?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))",
                (about_title, html_content)
            )
            conn.commit()
            note_id = cursor.lastrowid

        self.load_notes()
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                self.load_note()
                break

    def resizeEvent(self, event):
        self.left_container.setMaximumWidth(self.width() - 90)
        super().resizeEvent(event)

    def check_list_visibility(self, pos, index):
        if pos <= 10:
            self.is_notes_list_visible = False
            self.toggle_button.setText("▶")
        else:
            self.is_notes_list_visible = True
            self.toggle_button.setText("◀")

    def toggle_notes_list(self):
        if self.is_notes_list_visible:
            self.left_container.hide()
            self.toggle_button.setText("▶")
        else:
            self.left_container.show()
            self.toggle_button.setText("◀")
            self.splitter.setSizes([self.initial_notes_list_width, self.splitter.sizes()[1]])
        self.is_notes_list_visible = not self.is_notes_list_visible

    def _perform_auto_save(self):
        if self.need_save and self.current_note_id:
            title = self.title_input.text().strip()
            content = self.text_editor.toHtml()

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET title = ?, content = ?, last_accessed = datetime('now', 'localtime') WHERE id = ?", 
                            (title, content, self.current_note_id))
                conn.commit()

            self._notes_cache[self.current_note_id] = {'title': title, 'content': content}
            
            current_sort = None
            try:
                cursor.execute("SELECT value FROM settings WHERE key = 'sort_method'")
                result = cursor.fetchone()
                if result:
                    current_sort = result[0]
            except sqlite3.Error:
                pass
            
            if current_sort in ["modified_desc", "modified_asc"]:
                self.notes_list.blockSignals(True)
                current_row = self.notes_list.currentRow()
                self.load_notes()  
                
                for i in range(self.notes_list.count()):
                    if self.notes_list.item(i).data(Qt.ItemDataRole.UserRole) == self.current_note_id:
                        self.notes_list.setCurrentRow(i)
                        break
                
                self.notes_list.blockSignals(False)
            else:
                self.notes_list.blockSignals(True)
                current_row = self.notes_list.currentRow()
                self.load_notes()
                self.notes_list.setCurrentRow(current_row)
                self.notes_list.blockSignals(False)
            
            self.need_save = False
        self._save_timer.stop()


    def create_database(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, created_at TEXT, last_accessed TEXT)")
            
            try:
                cursor.execute("SELECT pinned FROM notes LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE notes ADD COLUMN pinned INTEGER DEFAULT 0")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    note_id INTEGER,
                    category TEXT,
                    PRIMARY KEY (note_id, category),
                    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON notes(last_accessed)")
            cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            
            cursor.execute("SELECT value FROM settings WHERE key = 'current_category'")
            if not cursor.fetchone():
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                            ("current_category", "all"))
            
            conn.commit()

    def show_category_menu(self):
        category_menu = QMenu(self)
        category_menu.setFont(QFont("Calibri", 9))
        
        theme = get_theme(self.current_theme)
        category_menu.setStyleSheet(theme["menu_style"])
        
        current_category = "all"
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'current_category'")
                result = cursor.fetchone()
                if result:
                    current_category = result[0]
        except sqlite3.Error:
            pass
        
        categories = [
            {"icon": "📓", "name": "Личное", "id": "personal"},
            {"icon": "📚", "name": "Учеба", "id": "study"},
            {"icon": "👔", "name": "Работа", "id": "work"},
            {"icon": "🏡", "name": "Ежедневное", "id": "daily"},
            {"icon": "☁️", "name": "Вдохновение", "id": "inspiration"}
        ]
        
        for category in categories:
            action_text = f"{category['icon']} {category['name']}"
            if current_category == category['id']:
                action_text += "   ✓"
            
            action = category_menu.addAction(action_text)
            action.triggered.connect(lambda checked, cat=category['id']: self.filter_by_category(cat))

        no_category_action = category_menu.addAction("🚫 Без категории")
        if current_category == "no_category":
            no_category_action.setText("🚫 Без категории   ✓")
        no_category_action.triggered.connect(lambda: self.filter_by_category("no_category"))
        
        category_menu.addSeparator()
        
        all_action = category_menu.addAction("Убрать фильтр по категориям")
        if current_category == "all":
            all_action.setText("Убрать фильтр по категориям   ✓")
        all_action.triggered.connect(lambda: self.filter_by_category("all"))
        
        menu_height = category_menu.sizeHint().height()
        category_menu.exec(self.category_button.mapToGlobal(QPoint(0, -menu_height)))

    def filter_by_category(self, category):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                            ("current_category", category))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении выбранной категории: {e}")
        
        current_id = None
        if self.notes_list.currentItem():
            current_id = self.notes_list.currentItem().data(Qt.ItemDataRole.UserRole)
        
        self.load_notes()
        
        if current_id:
            for i in range(self.notes_list.count()):
                item = self.notes_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) == current_id:
                    self.notes_list.setCurrentRow(i)
                    break

    def load_notes(self):
        self.notes_list.clear()
        
        self.notes_list.setWordWrap(True)
        self.notes_list.setUniformItemSizes(False)
        
        current_sort = "date_desc"  
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'sort_method'")
                result = cursor.fetchone()
                if result:
                    current_sort = result[0]
        except sqlite3.Error:
            pass
        
        current_category = "all"  
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'current_category'")
                result = cursor.fetchone()
                if result:
                    current_category = result[0]
        except sqlite3.Error:
            pass
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            if current_category == "all":
                cursor.execute("SELECT id, title, created_at FROM notes WHERE pinned = 1 ORDER BY created_at DESC")
            elif current_category == "no_category":
                cursor.execute("""
                    SELECT n.id, n.title, n.created_at 
                    FROM notes n 
                    WHERE n.pinned = 1 
                    AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.note_id = n.id)
                    ORDER BY n.created_at DESC
                """)
            else:
                cursor.execute("""
                    SELECT n.id, n.title, n.created_at 
                    FROM notes n 
                    JOIN categories c ON n.id = c.note_id 
                    WHERE n.pinned = 1 AND c.category = ? 
                    ORDER BY n.created_at DESC
                """, (current_category,))
            
            pinned_notes = cursor.fetchall()
            
            sort_clause = ""
            if current_sort == "date_desc":
                sort_clause = "ORDER BY n.created_at DESC"
            elif current_sort == "date_asc":
                sort_clause = "ORDER BY n.created_at ASC"
            elif current_sort == "name_asc":
                sort_clause = "ORDER BY CASE WHEN n.title = '' THEN 'Без названия' ELSE n.title END COLLATE NOCASE ASC"
            elif current_sort == "name_desc":
                sort_clause = "ORDER BY CASE WHEN n.title = '' THEN 'Без названия' ELSE n.title END COLLATE NOCASE DESC"
            elif current_sort == "modified_desc":
                sort_clause = "ORDER BY n.last_accessed DESC"
            else:  
                sort_clause = "ORDER BY n.last_accessed ASC"
            
            if current_category == "all":
                cursor.execute(f"SELECT id, title, created_at FROM notes WHERE pinned = 0 {sort_clause.replace('n.', '')}")
            elif current_category == "no_category":
                cursor.execute(f"""
                    SELECT n.id, n.title, n.created_at 
                    FROM notes n 
                    WHERE n.pinned = 0 
                    AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.note_id = n.id)
                    {sort_clause}
                """)
            else:
                cursor.execute(f"""
                    SELECT n.id, n.title, n.created_at 
                    FROM notes n 
                    JOIN categories c ON n.id = c.note_id 
                    WHERE n.pinned = 0 AND c.category = ? 
                    {sort_clause}
                """, (current_category,))
            
            regular_notes = cursor.fetchall()
            
            for note in pinned_notes:
                cursor.execute("SELECT category FROM categories WHERE note_id = ?", (note[0],))
                categories = [row[0] for row in cursor.fetchall()]
                self._add_note_item(note, is_pinned=True, categories=categories)
            
            if pinned_notes and regular_notes:
                separator = QListWidgetItem()
                separator.setFlags(Qt.ItemFlag.NoItemFlags)
                separator.setSizeHint(QSize(self.notes_list.width() - 10, 1))
                separator.setBackground(QColor("#e0e0e0" if self.current_theme == "light" else "#444"))
                self.notes_list.addItem(separator)
            
            for note in regular_notes:
                cursor.execute("SELECT category FROM categories WHERE note_id = ?", (note[0],))
                categories = [row[0] for row in cursor.fetchall()]
                self._add_note_item(note, is_pinned=False, categories=categories)
            
            self.check_empty_state()


    def load_note(self):
        if hasattr(self, '_is_loading') and self._is_loading:
            return
            
        self._is_loading = True
        
        current_item = self.notes_list.currentItem()
        if current_item:
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            if note_id != self.current_note_id:
                self.current_note_id = note_id
                
                if note_id in self._notes_cache:
                    cached_note = self._notes_cache[note_id]
                    self.title_input.setText(cached_note['title'])
                    
                    if cached_note['content'] is None:
                        with sqlite3.connect(DB_FILE) as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE notes SET last_accessed = datetime('now', 'localtime') WHERE id = ?", (note_id,))
                            cursor.execute("SELECT content FROM notes WHERE id = ?", (note_id,))
                            content = cursor.fetchone()[0]
                            self.text_editor.setHtml(content)
                            self._notes_cache[note_id]['content'] = content
                            conn.commit()
                    else:
                        self.text_editor.setHtml(cached_note['content'])
                else:
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE notes SET last_accessed = datetime('now', 'localtime') WHERE id = ?", (note_id,))
                        cursor.execute("SELECT title, content FROM notes WHERE id = ?", (note_id,))
                        note = cursor.fetchone()
                        if note:
                            self.title_input.setText(note[0])
                            self.text_editor.setHtml(note[1])
                            self._notes_cache[note_id] = {'title': note[0], 'content': note[1]}
                        conn.commit()
    
        self._is_loading = False

    def search_notes(self):
        search_text = self.search_bar.text().strip().lower()
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            item.setHidden(not any(search_text in text.lower() for text in item.text().split('\n')))

    def load_last_note(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content FROM notes ORDER BY last_accessed DESC LIMIT 1")
            result = cursor.fetchone()

            if result:
                self.current_note_id = result[0]
                self.title_input.setText(result[1])
                self.text_editor.setHtml(result[2])

                for i in range(self.notes_list.count()):
                    item = self.notes_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == self.current_note_id:
                        self.notes_list.setCurrentItem(item)
                        break

    def auto_save(self):
        self.need_save = True
        if not self._save_timer.isActive():
            self._save_timer.start()

    def show_empty_state(self):
        self.editor_container.hide()
        if not hasattr(self, 'empty_state_label') or not self.empty_state_label:
            self.empty_state_label = QLabel("Записей пока нет!\n\nСоздайте новую запись, нажав на кнопку ✏️\nИли проверьте папку категорий 🗂️", self)
            self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.right_layout.addWidget(self.empty_state_label)
        
        theme = get_theme(self.current_theme)
        self.empty_state_label.setStyleSheet(theme["empty_state_label"])
        self.empty_state_label.show()

    def check_empty_state(self):
        if self.notes_list.count() == 0:
            self.show_empty_state()
        else:
            if hasattr(self, 'empty_state_label'):
                self.empty_state_label.hide()
            self.editor_container.show()

    def new_note(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (title, content, created_at, last_accessed) VALUES (?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))", ("", ""))
            conn.commit()
            note_id = cursor.lastrowid

        self.load_notes()
        self.current_note_id = note_id
        self.title_input.clear()
        self.text_editor.clear()
        
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                break
                
        self.check_empty_state()

    def delete_note(self):
        if self.current_note_id:
            if not self.skip_delete_confirmation:
                msg = QMessageBox()
                msg.setWindowTitle("Удаление")
                msg.setText("Уверены, что хотите удалить эту заметку?")
                checkbox = QCheckBox("Больше никогда не спрашивать")
                msg.setCheckBox(checkbox)
                
                theme = get_theme(self.current_theme)
                msg.setStyleSheet(theme["message_box"])
                
                delete_button = QPushButton("Да")
                cancel_button = QPushButton("Нет")
                msg.addButton(delete_button, QMessageBox.ButtonRole.YesRole)
                msg.addButton(cancel_button, QMessageBox.ButtonRole.NoRole)
                msg.exec()

                if checkbox.isChecked():
                    self.skip_delete_confirmation = True

                if msg.clickedButton() != delete_button:
                    return

            try:
                current_row = self.notes_list.currentRow()
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM notes WHERE id = ?", (self.current_note_id,))
                    conn.commit()

                if self.current_note_id in self._notes_cache:
                    del self._notes_cache[self.current_note_id]

                self.current_note_id = None
                self.title_input.clear()
                self.text_editor.clear()
                self.load_notes()

                new_row = min(current_row, self.notes_list.count() - 1)
                if new_row >= 0:
                    self.notes_list.setCurrentRow(new_row)
                    item = self.notes_list.item(new_row)
                    if item:
                        self.load_note()

                self.check_empty_state()

            except sqlite3.Error as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить заметку: {str(e)}")

    def setup_shortcuts(self):
        bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_shortcut.activated.connect(self.toggle_bold)

        italic_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        italic_shortcut.activated.connect(self.toggle_italic)

        underline_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_shortcut.activated.connect(self.toggle_underline)

        highlight_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        highlight_shortcut.activated.connect(self.toggle_highlight)

        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo)

        strikethrough_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)  
        strikethrough_shortcut.activated.connect(self.toggle_strikethrough)

    def toggle_bold(self):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        format = QTextCharFormat()
        
        current_format = cursor.charFormat()
        is_bold = current_format.fontWeight() == QFont.Weight.Bold
        
        if is_bold:
            format.setFontWeight(QFont.Weight.Normal)
        else:
            format.setFontWeight(QFont.Weight.Bold)
        
        cursor.mergeCharFormat(format)

    def toggle_italic(self):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        format = QTextCharFormat()
        
        current_format = cursor.charFormat()
        is_italic = current_format.fontItalic()
        
        format.setFontItalic(not is_italic)
        
        cursor.mergeCharFormat(format)

    def toggle_underline(self):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        format = QTextCharFormat()
        
        current_format = cursor.charFormat()
        is_underline = current_format.fontUnderline()
        
        format.setFontUnderline(not is_underline)
        
        cursor.mergeCharFormat(format)

    def toggle_strikethrough(self):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        format = QTextCharFormat()
        
        current_format = cursor.charFormat()
        is_strikeout = current_format.fontStrikeOut()
        
        format.setFontStrikeOut(not is_strikeout)
        
        cursor.mergeCharFormat(format)

    def toggle_highlight(self):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        format = QTextCharFormat()
        
        highlight_color = QColor("#775c88") if self.current_theme == "dark" else QColor("#e4d5ff")
        
        current_format = cursor.charFormat()
        current_color = current_format.background().color()

        if current_color.name() in [highlight_color.name(), "#e4d5ff", "#775c88"]:
            format.setBackground(QColor("transparent"))
        else:
            format.setBackground(highlight_color)
        
        cursor.mergeCharFormat(format)

    def undo(self):
        self.text_editor.undo()

    def auto_format(self):
        cursor = self.text_editor.textCursor()
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        text = cursor.selectedText()
        if "--" in text:
            cursor.insertText(text.replace("--", "—"))

    def update_counter(self):
        text = self.text_editor.toPlainText()
        char_count = len(text)
        word_count = len(text.split())
        self.counter_label.setText(f"Количество слов: {word_count} | Количество символов: {char_count}")

    def is_first_launch(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM notes")
            count = cursor.fetchone()[0]
            return count == 0

    def show_sort_menu(self):
        sort_menu = QMenu(self)
        sort_menu.setFont(QFont("Calibri", 9))
        
        theme = get_theme(self.current_theme)
        sort_menu.setStyleSheet(theme["sort_menu_style"])

        current_sort = "date_desc"  
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'sort_method'")
                result = cursor.fetchone()
                if result:
                    current_sort = result[0]
        except sqlite3.Error:
            pass

        new_to_old = sort_menu.addAction("От новых к старым записям" + ("   ✓" if current_sort == "date_desc" else ""))
        old_to_new = sort_menu.addAction("От старых к новым записям" + ("   ✓" if current_sort == "date_asc" else ""))
        
        sort_menu.addSeparator()
        
        name_az = sort_menu.addAction("По имени файла (от А до Я)" + ("   ✓" if current_sort == "name_asc" else ""))
        name_za = sort_menu.addAction("По имени файла (от Я до А)" + ("   ✓" if current_sort == "name_desc" else ""))
        
        sort_menu.addSeparator()
        
        modified_new = sort_menu.addAction("По времени последнего изменения (от новых к старым)" + ("   ✓" if current_sort == "modified_desc" else ""))
        modified_old = sort_menu.addAction("По времени последнего изменения (от старых к новым)" + ("   ✓" if current_sort == "modified_asc" else ""))

        new_to_old.triggered.connect(lambda: self.sort_notes("date_desc"))
        old_to_new.triggered.connect(lambda: self.sort_notes("date_asc"))
        name_az.triggered.connect(lambda: self.sort_notes("name_asc"))
        name_za.triggered.connect(lambda: self.sort_notes("name_desc"))
        modified_new.triggered.connect(lambda: self.sort_notes("modified_desc"))
        modified_old.triggered.connect(lambda: self.sort_notes("modified_asc"))

        menu_height = sort_menu.sizeHint().height()
        sort_menu.exec(self.sort_button.mapToGlobal(QPoint(0, -menu_height)))

    def sort_notes(self, sort_type):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
                if not cursor.fetchone():
                    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
                
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                            ("sort_method", sort_type))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении способа сортировки: {e}")
        
        current_id = None
        if self.notes_list.currentItem():
            current_id = self.notes_list.currentItem().data(Qt.ItemDataRole.UserRole)

        self.load_notes()
        
        if current_id:
            for i in range(self.notes_list.count()):
                item = self.notes_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) == current_id:
                    self.notes_list.setCurrentRow(i)
                    break


    def show_color_palette(self):
        if not self.text_editor.textCursor().hasSelection():
            return
            
        color_menu = QMenu(self)
        color_menu.setFont(QFont("Calibri", 9))
        
        color_grid = QWidget()
        
        if self.current_theme == "dark":
            color_grid.setStyleSheet("background-color: #3a3a3a; border-radius: 3px;")
        else:
            color_grid.setStyleSheet("""
                background-color: #fefefe; 
                border-radius: 3px;
                border: 1px solid #f2f2f2;
            """)
        
        grid_layout = QGridLayout(color_grid)
        grid_layout.setSpacing(4)  
        grid_layout.setHorizontalSpacing(6)  
        
        colors = [
            # Первый столбец
            ["#aa95cf", "#c7b4e9", "#e2d3fd", "#eadcff"],
            # Второй столбец
            ["#cf95b8", "#e9b4e2", "#fdd3ef", "#ffdcff"],
            # Третий столбец
            ["#818ec4", "#b4b5e9", "#d3e3fd", "#dcfffe"],
            # Четвертый столбец
            ["#97cf95", "#b4e9b7", "#d3fddd", "#e8ffe7"],
            # Пятый столбец
            ["#fda553", "#fdb877", "#ffd0a5", "#ffe9d5"],
            # Шестой столбец
            ["#182ef3", "#ff0f0f", "#17ca1a", "#8f17ca"]
        ]
        
        for col, column_colors in enumerate(colors):
            for row, color in enumerate(column_colors):
                color_button = QPushButton()
                color_button.setFixedSize(18, 18)  
                
                if self.current_theme == "dark":
                    color_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color}; 
                            border: 1px solid #555555; 
                            border-radius: 3px;
                        }}
                        QPushButton:hover {{
                            border: 1px solid #4a4545;
                        }}
                        QPushButton:pressed {{
                            border: 1px solid #4a4545;
                        }}
                    """)
                else:
                    color_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color}; 
                            border: 1px solid #efe2e7; 
                            border-radius: 3px;
                        }}
                        QPushButton:hover {{
                            border: 1px solid #e5d3da;
                        }}
                        QPushButton:pressed {{
                            border: 1px solid #e5d3da;
                        }}
                    """)
                
                color_button.clicked.connect(lambda checked, c=color: self.apply_text_color_and_clear(c))
                
                grid_layout.addWidget(color_button, row, col)
        
        default_button = QPushButton("По умолчанию темы")
        default_button.setFixedHeight(20)  
        default_button.setFont(QFont("Calibri", 8))
        
        if self.current_theme == "dark":
            default_button.setStyleSheet("""
                QPushButton {
                    background-color: #555;
                    color: #fff;
                    border: none;
                    border-radius: 3px;
                    padding: 2px;
                    font-weight: normal;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #666;
                }
            """)
        else:
            default_button.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    color: #333;
                    border: none;
                    border-radius: 3px;
                    padding: 2px;
                    font-weight: normal;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
        
        default_button.clicked.connect(lambda: self.apply_text_color_and_clear("default"))
        grid_layout.addWidget(default_button, 4, 0, 1, 6) 
        
        grid_layout.setContentsMargins(5, 5, 5, 5)
        
        action = QWidgetAction(color_menu)
        action.setDefaultWidget(color_grid)
        color_menu.addAction(action)

        color_menu.setStyleSheet("""
            QMenu {
                background-color: transparent;
                border: none;
            }
        """)
        
        color_menu.exec(self.btn_color.mapToGlobal(QPoint(0, self.btn_color.height())))

    def apply_text_color_and_clear(self, color):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        end_position = cursor.selectionEnd()
        
        format = QTextCharFormat()
        
        if color == "default":
            default_color = QColor("#2f2f2f") if self.current_theme == "light" else QColor("#ffffff")
            format.setForeground(default_color)
        else:
            format.setForeground(QColor(color))
        
        cursor.mergeCharFormat(format)
        
        cursor.setPosition(end_position)
        self.text_editor.setTextCursor(cursor)
        
        QApplication.activePopupWidget().close() if QApplication.activePopupWidget() else None

        self.text_editor.setFocus()
        
        self.auto_save()

    def update_default_text_colors(self):
        default_color = QColor("#2f2f2f") if self.current_theme == "light" else QColor("#ffffff")
        
        cursor = QTextCursor(self.text_editor.document())
        
        while not cursor.atEnd():
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
            
            char_format = cursor.charFormat()
            current_color = char_format.foreground().color()
            
            opposite_default = QColor("#ffffff") if self.current_theme == "light" else QColor("#2f2f2f")
            if current_color.name() == opposite_default.name():
                new_format = QTextCharFormat()
                new_format.setForeground(default_color)
                cursor.mergeCharFormat(new_format)
            
            cursor.clearSelection()

    def update_color_button_state(self):
        has_selection = self.text_editor.textCursor().hasSelection()
        self.btn_color.setEnabled(has_selection)
        
        theme = get_theme(self.current_theme)
        if has_selection:
            self.btn_color.setStyleSheet(theme["button_style"])
        else:
            if self.current_theme == "dark":
                inactive_style = """
                    QPushButton {
                        background-color: #2f2f2f;
                        color: #555;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #2f2f2f;
                    }
                """
            else:
                inactive_style = """
                    QPushButton {
                        background-color: #e0e0e0;
                        color: #555;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """
            self.btn_color.setStyleSheet(inactive_style)

    def show_size_menu(self):
        if not self.text_editor.textCursor().hasSelection():
            return
            
        size_menu = QMenu(self)
        size_menu.setFont(QFont("Calibri", 9))
        
        size_grid = QWidget()
        
        if self.current_theme == "dark":
            size_grid.setStyleSheet("background-color: #3a3a3a; border-radius: 3px;")
        else:
            size_grid.setStyleSheet("""
                background-color: #fefefe; 
                border-radius: 3px;
                border: 1px solid #f2f2f2;
            """)
        
        grid_layout = QGridLayout(size_grid)
        grid_layout.setSpacing(4)
        
        size_buttons = [
            {"text": "H1", "size": 18, "tooltip": "Заголовок 1 уровня"},
            {"text": "H2", "size": 14, "tooltip": "Заголовок 2 уровня"},
            {"text": "н", "size": 11, "tooltip": "Размер по умолчанию"},
            {"text": ".", "size": 9, "tooltip": "Ваще мелебнкий шрифт жестб"}
        ]
        
        for col, button_info in enumerate(size_buttons):
            size_button = QPushButton(button_info["text"])
            size_button.setFixedSize(20, 20)
            size_button.setToolTip(button_info["tooltip"])
            
            font = size_button.font()
            font.setPointSize(8)  
            size_button.setFont(font)
            
            if self.current_theme == "dark":
                size_button.setStyleSheet("""
                    QPushButton {
                        background-color: #555;
                        color: #fff;
                        border: 1px solid #555555; 
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        border: 1px solid #4a4545;
                        background-color: #666;
                    }
                    QPushButton:pressed {
                        border: 1px solid #4a4545;
                    }
                """)
            else:
                size_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        color: #333;
                        border: 1px solid #efe2e7; 
                        border-radius: 3px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        border: 1px solid #e5d3da;
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        border: 1px solid #e5d3da;
                    }
                """)
            
            font_size = button_info["size"]
            size_button.clicked.connect(lambda checked=False, size=font_size: self.apply_font_size_and_clear(size))
            
            grid_layout.addWidget(size_button, 0, col)
        
        grid_layout.setContentsMargins(7, 4, 7, 4)
        
        action = QWidgetAction(size_menu)
        action.setDefaultWidget(size_grid)
        size_menu.addAction(action)
        
        size_menu.setStyleSheet("""
            QMenu {
                background-color: transparent;
                border: none;
            }
        """)

        size_menu.exec(self.btn_size.mapToGlobal(QPoint(0, self.btn_size.height())))


    def apply_font_size_and_clear(self, size):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        end_position = cursor.selectionEnd()

        format = QTextCharFormat()
        format.setFontPointSize(size)
        cursor.mergeCharFormat(format)
        
        cursor.setPosition(end_position)
        self.text_editor.setTextCursor(cursor)
        
        QApplication.activePopupWidget().close() if QApplication.activePopupWidget() else None
        
        self.text_editor.setFocus()
        
        self.auto_save()

    def toggle_pin_status(self, note_id):
        pinned_count = sum(1 for note in self._notes_cache.values() if note.get('pinned', False))
        
        is_currently_pinned = self._notes_cache[note_id].get('pinned', False)
        
        if not is_currently_pinned and pinned_count >= 3:
            QMessageBox.information(self, "Ошибка", "Можно закрепить не более 3 заметок")
            return

        new_pinned_status = 0 if is_currently_pinned else 1
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET pinned = ? WHERE id = ?",
                            (new_pinned_status, note_id))
                conn.commit()
                
                self._notes_cache[note_id]['pinned'] = not is_currently_pinned
                
                self.load_notes()
                
                for i in range(self.notes_list.count()):
                    item = self.notes_list.item(i)
                    if item and item.data(Qt.ItemDataRole.UserRole) == note_id:
                        self.notes_list.setCurrentItem(item)
                        break
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обновить статус закрепления: {str(e)}")

    def _add_note_item(self, note, is_pinned, categories=None):
        note_id = note[0]
        title = note[1] if note[1] else "Без Названия"
        date_obj = datetime.strptime(note[2].split('.')[0], '%Y-%m-%d %H:%M:%S')
        date = f"{date_obj.day} {MONTHS[date_obj.month]} {date_obj.year} {date_obj.hour:02d}:{date_obj.minute:02d}"
        
        category_icons = {
            "personal": "📓",
            "study": "📚",
            "work": "👔",
            "daily": "🏡",
            "inspiration": "☁️"
        }
        
        category_display = ""
        if categories:
            category_display = " ".join([category_icons.get(cat, "") for cat in categories[:2]])
        
        if is_pinned:
            display_title = f"⭐ {category_display} {title}" if category_display else f"⭐ {title}"
        else:
            display_title = f"{category_display} {title}" if category_display else title
        
        item = QListWidgetItem()
        item.setText(f"{display_title}\n{date}")
        item.setData(Qt.ItemDataRole.UserRole, note_id)
        
        item.setFlags(item.flags() | Qt.ItemFlag.ItemNeverHasChildren)
        
        if is_pinned:
            if self.current_theme == "light":
                item.setBackground(QColor("#f1dbea"))  
            else:
                item.setBackground(QColor("#484444"))  
        
        self.notes_list.addItem(item)
        
        if note_id not in self._notes_cache:
            self._notes_cache[note_id] = {'title': note[1], 'content': None, 'pinned': is_pinned, 'categories': categories or []}
        else:
            self._notes_cache[note_id]['pinned'] = is_pinned
            self._notes_cache[note_id]['categories'] = categories or []

    def on_item_selection_changed(self, current, previous):
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if not item or not item.data(Qt.ItemDataRole.UserRole) in self._notes_cache:
                continue
                
            note_id = item.data(Qt.ItemDataRole.UserRole)
            is_pinned = self._notes_cache[note_id].get('pinned', False)
            
            if is_pinned:
                is_selected = (item == current)
                
                if self.current_theme == "light":
                    if is_selected:
                        item.setBackground(QColor("#eecbe3"))  
                    else:
                        item.setBackground(QColor("#f1dbea"))  
                else:
                    if is_selected:
                        item.setBackground(QColor("#858585")) 
                    else:
                        item.setBackground(QColor("#484444"))  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('icon.ico')))
    app.setStyle('Fusion')
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())
