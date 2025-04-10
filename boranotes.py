import sys
import os
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QTextEdit, QHBoxLayout, QLineEdit, QLabel, QMessageBox, QCheckBox, QSplitter, QMenu
)
from PyQt6.QtGui import (
    QFont, QIcon, QTextCursor, QTextCharFormat, QShortcut, QKeySequence, QColor
)
from PyQt6.QtCore import Qt, QTimer, QMimeData, QPoint, QUrl
from PyQt6.QtWidgets import QVBoxLayout
from themes import get_theme
from PyQt6.QtGui import QDesktopServices
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
        self.default_font = QFont("Calibri", 12)
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
        strikethrough_action = format_menu.addAction("Ctrl + T  | Зачеркнутый  ")  # Добавляем новый пункт
        highlight_action = format_menu.addAction("Ctrl + H  | Выделить ")
        format_menu.addSeparator()
        clear_format_action = format_menu.addAction("Очистить форматирование")

        bold_action.setEnabled(has_selected_text)
        italic_action.setEnabled(has_selected_text)
        underline_action.setEnabled(has_selected_text)
        strikethrough_action.setEnabled(has_selected_text)
        highlight_action.setEnabled(has_selected_text)
        clear_format_action.setEnabled(has_selected_text)
        
        # Добавляем меню специальных символов
        special_symbols_menu = custom_menu.addMenu(" 🔣  Специальные символы                ")
        special_symbols_menu.setStyleSheet(theme["menu_style"])
        
        empty_circle_action = special_symbols_menu.addAction("○ Пустой кружок")
        full_circle_action = special_symbols_menu.addAction("● Тёмный кружок")
        dark_arrow_action = special_symbols_menu.addAction("➤ Тёмная стрелочка")
        check_mark_action = special_symbols_menu.addAction("✔ Галочка/готово!")
        cross_mark_action = special_symbols_menu.addAction("✘ Крестик/не готово!")
        music_note_action = special_symbols_menu.addAction("♫ Музыкальная нота")
        heart_note_action = special_symbols_menu.addAction("♥︎ Заполененное сердечко")
        
        # Добавляем меню специальных эмоджи
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

        # Безопасно подключаем действия форматирования
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
            return  # Если текст не выделен, ничего не делаем
        
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

    def clear_formatting(self):
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
        self.current_theme = "light"  # По умолчанию светлая тема

        self._save_timer = QTimer()
        self._save_timer.setInterval(1000)
        self._save_timer.timeout.connect(self._perform_auto_save)

        self.create_database()
        
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
        left_layout.addWidget(self.search_bar)

        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.load_note)
        self.notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_notes_list_context_menu)
        left_layout.addWidget(self.notes_list)

        self.right_container = QWidget()
        self.right_container.setMinimumWidth(90)
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.toggle_button = QPushButton("◀")
        self.toggle_button.setFixedSize(24, 24)
        self.toggle_button.clicked.connect(self.toggle_notes_list)

        buttons_layout = QHBoxLayout()

        self.btn_new = QPushButton("✏️")
        self.btn_new.setFixedSize(24, 24)
        self.btn_new.clicked.connect(self.new_note)

        self.btn_delete = QPushButton("🗑️")
        self.btn_delete.setFixedSize(24, 24)
        self.btn_delete.clicked.connect(self.delete_note)

        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.btn_new)
        buttons_layout.addWidget(self.btn_delete)
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

        self.separator = QWidget()
        self.separator.setFixedHeight(1)

        self.text_editor = CustomTextEdit()
        self.text_editor.setFont(QFont("Calibri", 12))
        self.text_editor.textChanged.connect(self.auto_save)
        self.text_editor.textChanged.connect(self.auto_format)

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
        bottom_layout.addWidget(self.sort_button)

        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(25, 23)
        self.settings_button.clicked.connect(self.show_settings)
        self.settings_button.setStyleSheet("margin-left: -5px;")  # Сдвигаем влево на 2px
        bottom_layout.addWidget(self.settings_button)

        self.spotify_button = QPushButton("💜")
        self.spotify_button.setFixedSize(25, 23)
        self.spotify_button.clicked.connect(self.open_spotify)
        self.spotify_button.setStyleSheet("margin-left: -5px;")  # Такой же отступ как у кнопки настроек
        bottom_layout.addWidget(self.spotify_button)

        bottom_layout.addStretch()

        self.counter_label = QLabel()
        bottom_layout.addWidget(self.counter_label)

        layout.addWidget(bottom_panel)
        self.setLayout(layout)
        self.text_editor.textChanged.connect(self.update_counter)
        
        # Применяем тему
        self.apply_theme(self.current_theme)

        self.toggle_button.setToolTip("Скрыть/показать список заметок")
        self.btn_new.setToolTip("Создать новую заметку")
        self.btn_delete.setToolTip("Удалить текущую заметку")
        self.sort_button.setToolTip("Сортировка заметок")
        self.settings_button.setToolTip("Настройки")
        self.spotify_button.setToolTip("Открыть Spotify")

    def show_title_context_menu(self, position):
        """Показывает пользовательское контекстное меню для поля заголовка"""
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
        
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://open.spotify.com/collection/tracks"))

    

    def update_note_title(self):
        if not self.current_note_id:
            return
            
        title = self.title_input.text().strip()
        
        # Обновляем заголовок в списке
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self.current_note_id:
                # Получаем текущий текст элемента и обновляем только заголовок
                current_text = item.text()
                date_line = current_text.split('\n')[1] if '\n' in current_text else ""
                new_title = title if title else "Без Названия"
                item.setText(f"{new_title}\n{date_line}")
                break
        
        if self.current_note_id in self._notes_cache:
            self._notes_cache[self.current_note_id]['title'] = title
    

    def show_notes_list_context_menu(self, position):
        theme = get_theme(self.current_theme)
        context_menu = QMenu(self)
        context_menu.setStyleSheet(theme["menu_style"])
        
        # Получаем элемент под курсором
        item = self.notes_list.itemAt(position)
        
        if item:
            # Если курсор над элементом списка
            delete_action = context_menu.addAction(" ❌ Удалить запись ")
            delete_action.triggered.connect(self.delete_note)
        else:
            # Если курсор над пустой областью
            new_action = context_menu.addAction(" ✏️ Создать запись ")
            new_action.triggered.connect(self.new_note)
        
        context_menu.exec(self.notes_list.mapToGlobal(position))

    def apply_theme(self, theme_name):
        """Применяет выбранную тему к интерфейсу"""
        self.current_theme = theme_name
        theme = get_theme(theme_name)
        
        # Применяем стили из темы
        self.setStyleSheet(theme["main_window"])
        self.notes_list.setStyleSheet(theme["notes_list"])
        self.search_bar.setStyleSheet(theme["search_bar"])
        self.editor_container.setStyleSheet(theme["editor_container"])
        self.text_editor.setStyleSheet(theme["text_editor"])
        self.title_input.setStyleSheet(theme["title_input"])
        self.separator.setStyleSheet(theme["separator"])
        self.counter_label.setStyleSheet(theme["counter_label"])
        
        # Обновляем стиль для пустого состояния, если оно существует
        if hasattr(self, 'empty_state_label') and self.empty_state_label:
            self.empty_state_label.setStyleSheet(theme["empty_state_label"])
        
        # Кнопки
        self.toggle_button.setStyleSheet(theme["button_style"])
        self.btn_new.setStyleSheet(theme["button_style"])
        self.btn_delete.setStyleSheet(theme["button_style"])
        self.sort_button.setStyleSheet(theme["sort_button"])
        self.settings_button.setStyleSheet(theme["settings_button"])
        self.spotify_button.setStyleSheet(theme["settings_button"])

        QApplication.instance().setStyleSheet(theme["tooltip_style"])
    
        
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
        """Загружает сохраненную тему из базы данных"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                # Проверяем, существует ли таблица settings
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
                if cursor.fetchone() is None:
                    # Если таблицы нет, создаем ее
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
            # Если произошла ошибка, используем тему по умолчанию
            self.current_theme = "light"

    def save_theme_setting(self, theme_name):
        """Сохраняет выбранную тему в базу данных"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                # Проверяем, существует ли таблица settings
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
                if cursor.fetchone() is None:
                    # Если таблицы нет, создаем ее
                    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
                
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                            ("theme", theme_name))
                conn.commit()
                print(f"Сохранена тема: {theme_name}")
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении темы: {e}")

    def show_settings(self):
        """Показывает меню настроек"""
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
        """Создает или переходит к заметке 'О программе'"""
        about_title = get_about_title()
        about_content = get_about_content()
        
        # Преобразуем текст в HTML с явным указанием шрифта Calibri
        html_content = f"""
        <div style="font-family: Calibri; font-size: 12pt;">
        {about_content.replace("\n", "<br>")}
        </div>
        """
        
        # Проверяем, существует ли уже заметка "О программе"
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM notes WHERE title = ?", (about_title,))
            result = cursor.fetchone()
            
            if result:
                # Если заметка уже существует, просто переходим к ней
                note_id = result[0]
                for i in range(self.notes_list.count()):
                    item = self.notes_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == note_id:
                        self.notes_list.setCurrentItem(item)
                        self.load_note()
                        break
                return

        # Если заметки нет, создаем новую
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (title, content, created_at, last_accessed) VALUES (?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))",
                (about_title, html_content)
            )
            conn.commit()
            note_id = cursor.lastrowid

        # Обновляем список заметок и переходим к новой заметке
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
                cursor.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, self.current_note_id))
                conn.commit()

            self._notes_cache[self.current_note_id] = {'title': title, 'content': content}
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON notes(last_accessed)")
            cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            conn.commit()

    def load_notes(self):
        self.notes_list.clear()
        
        # Получаем актуальные ID заметок из БД
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, created_at FROM notes ORDER BY id DESC")
            current_ids = set()
            
            for note in cursor.fetchall():
                note_id = note[0]
                current_ids.add(note_id)
                
                # Форматирование данных
                title = note[1] if note[1] else "Без Названия"
                date_obj = datetime.strptime(note[2].split('.')[0], '%Y-%m-%d %H:%M:%S')
                date = f"{date_obj.day} {MONTHS[date_obj.month]} {date_obj.year} {date_obj.hour:02d}:{date_obj.minute:02d}"

                # Создание элемента списка
                item = QListWidgetItem()
                item.setText(f"{title}\n{date}")
                item.setData(Qt.ItemDataRole.UserRole, note_id)
                self.notes_list.addItem(item)
                
                # Обновляем кэш только для новых заметок
                if note_id not in self._notes_cache:
                    self._notes_cache[note_id] = {'title': note[1], 'content': None}

        # Очищаем кэш от удаленных заметок
        for cached_id in list(self._notes_cache.keys()):
            if cached_id not in current_ids:
                del self._notes_cache[cached_id]
        
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
                
                # Проверяем, загружено ли содержимое в кэш
                if note_id in self._notes_cache:
                    cached_note = self._notes_cache[note_id]
                    self.title_input.setText(cached_note['title'])
                    
                    # Если содержимое еще не загружено, загружаем его
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
                    # Если заметки нет в кэше, загружаем полностью
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
            item.setHidden(not any(search_text in text for text in item.text().lower().split()))

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
            self.empty_state_label = QLabel("Записей пока нет!\nСоздайте новую запись, нажав на кнопку ✏️", self)
            self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.right_layout.addWidget(self.empty_state_label)
        
        # Применяем текущую тему к метке
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
        self.notes_list.setCurrentRow(0)
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
        
        # Проверяем текущее состояние жирности
        current_format = cursor.charFormat()
        is_bold = current_format.fontWeight() == QFont.Weight.Bold
        
        # Устанавливаем только свойство жирности, не трогая остальные
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
        
        # Проверяем текущее состояние курсива
        current_format = cursor.charFormat()
        is_italic = current_format.fontItalic()
        
        # Устанавливаем только свойство курсива, не трогая остальные
        format.setFontItalic(not is_italic)
        
        cursor.mergeCharFormat(format)

    def toggle_underline(self):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        format = QTextCharFormat()
        
        # Проверяем текущее состояние подчеркивания
        current_format = cursor.charFormat()
        is_underline = current_format.fontUnderline()
        
        # Устанавливаем только свойство подчеркивания, не трогая остальные
        format.setFontUnderline(not is_underline)
        
        cursor.mergeCharFormat(format)

    def toggle_strikethrough(self):
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        format = QTextCharFormat()
        
        # Проверяем текущее состояние зачеркивания
        current_format = cursor.charFormat()
        is_strikeout = current_format.fontStrikeOut()
        
        # Устанавливаем только свойство зачеркивания, не трогая остальные
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

        # Добавляем пункты меню
        new_to_old = sort_menu.addAction("От новых к старым записям")
        old_to_new = sort_menu.addAction("От старых к новым записям")
        
        sort_menu.addSeparator()
        
        name_az = sort_menu.addAction("По имени файла (от А до Я)")
        name_za = sort_menu.addAction("По имени файла (от Я до А)")
        
        sort_menu.addSeparator()
        
        modified_new = sort_menu.addAction("По времени последнего изменения (от новых к старым)")
        modified_old = sort_menu.addAction("По времени последнего изменения (от старых к новым)")

        # Привязываем действия
        new_to_old.triggered.connect(lambda: self.sort_notes("date_desc"))
        old_to_new.triggered.connect(lambda: self.sort_notes("date_asc"))
        name_az.triggered.connect(lambda: self.sort_notes("name_asc"))
        name_za.triggered.connect(lambda: self.sort_notes("name_desc"))
        modified_new.triggered.connect(lambda: self.sort_notes("modified_desc"))
        modified_old.triggered.connect(lambda: self.sort_notes("modified_asc"))

        # Показываем меню возле кнопки
        sort_menu.exec(self.sort_button.mapToGlobal(QPoint(0, -sort_menu.sizeHint().height())))

    def sort_notes(self, sort_type):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            if sort_type == "date_desc":
                cursor.execute("SELECT id, title, created_at FROM notes ORDER BY created_at DESC")
            elif sort_type == "date_asc":
                cursor.execute("SELECT id, title, created_at FROM notes ORDER BY created_at ASC")
            elif sort_type == "name_asc":
                cursor.execute("SELECT id, title, created_at FROM notes ORDER BY CASE WHEN title = '' THEN 'Без названия' ELSE title END COLLATE NOCASE ASC")
            elif sort_type == "name_desc":
                cursor.execute("SELECT id, title, created_at FROM notes ORDER BY CASE WHEN title = '' THEN 'Без названия' ELSE title END COLLATE NOCASE DESC")
            elif sort_type == "modified_desc":
                cursor.execute("SELECT id, title, created_at FROM notes ORDER BY last_accessed DESC")
            else:  # modified_asc
                cursor.execute("SELECT id, title, created_at FROM notes ORDER BY last_accessed ASC")
            
            self.notes_list.clear()
            for note in cursor.fetchall():
                title = note[1] if note[1] else "Без названия"
                date_obj = datetime.strptime(note[2].split('.')[0], '%Y-%m-%d %H:%M:%S')
                date = f"{date_obj.day} {MONTHS[date_obj.month]} {date_obj.year} {date_obj.hour:02d}:{date_obj.minute:02d}"

                item = QListWidgetItem()
                item.setText(f"{title}\n{date}")
                item.setData(Qt.ItemDataRole.UserRole, note[0])
                self.notes_list.addItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('icon.ico')))
    app.setStyle('Fusion')
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())