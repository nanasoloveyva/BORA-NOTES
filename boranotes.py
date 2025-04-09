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
from PyQt6.QtCore import Qt, QTimer, QMimeData, QPoint
from PyQt6.QtWidgets import QVBoxLayout
from themes import get_theme

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
        
        # Получаем стиль меню из текущей темы приложения
        theme_name = self.window().current_theme
        theme = get_theme(theme_name)
        custom_menu.setStyleSheet(theme["menu_style"])

        undo_action = custom_menu.addAction(" ↩️  Отменить ")
        undo_action.triggered.connect(self.undo)
        
        redo_action = custom_menu.addAction(" ↪️  Повторить ")
        redo_action.triggered.connect(self.redo)
        
        custom_menu.addSeparator()

        format_menu = custom_menu.addMenu(" ✒️  Форматирование                  ▶")
        format_menu.setStyleSheet(theme["menu_style"])
        
        bold_action = format_menu.addAction("Жирный")
        italic_action = format_menu.addAction("Курсив")
        underline_action = format_menu.addAction("Подчеркнутый")
        highlight_action = format_menu.addAction("Выделить")
        format_menu.addSeparator()
        clear_format_action = format_menu.addAction("Очистить форматирование")

        copy_action = custom_menu.addAction(" 📋  Копировать ")
        copy_action.triggered.connect(self.copy)
        
        cut_action = custom_menu.addAction(" ✂️  Вырезать ")
        cut_action.triggered.connect(self.cut)
        
        paste_action = custom_menu.addAction(" 📌  Вставить ")
        paste_action.triggered.connect(self.paste)
        
        select_all_action = custom_menu.addAction(" ✅  Выделить всё ")
        select_all_action.triggered.connect(self.selectAll)

        custom_menu.addSeparator()
        
        delete_action = custom_menu.addAction(" ❌  Удалить ")
        delete_action.triggered.connect(self.textCursor().removeSelectedText)

        bold_action.triggered.connect(lambda: self.parent().toggle_bold())
        italic_action.triggered.connect(lambda: self.parent().toggle_italic())
        underline_action.triggered.connect(lambda: self.parent().toggle_underline())
        highlight_action.triggered.connect(lambda: self.parent().toggle_highlight())
        clear_format_action.triggered.connect(self.clear_formatting)

        custom_menu.exec(self.mapToGlobal(position))

    def clear_formatting(self):
        cursor = self.textCursor()
        format = QTextCharFormat()
        format.setFont(self.default_font)
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

        # Сначала создаем базу данных
        self.create_database()
        
        # Затем загружаем сохраненную тему
        self.load_theme_setting()
        
        # Инициализируем UI
        self.initUI()
        
        # Загружаем заметки
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

        bottom_layout.addStretch()

        self.counter_label = QLabel()
        bottom_layout.addWidget(self.counter_label)

        layout.addWidget(bottom_panel)
        self.setLayout(layout)
        self.text_editor.textChanged.connect(self.update_counter)
        
        # Применяем тему
        self.apply_theme(self.current_theme)

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
    

        self.save_theme_setting(theme_name)

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
        
        # Добавляем пункты меню для выбора темы
        theme_menu = settings_menu.addMenu("Тема оформления")
        theme_menu.setStyleSheet(theme["menu_style"])
        
        light_theme = theme_menu.addAction("🌞 Светлая тема")
        dark_theme = theme_menu.addAction("🌛 Темная тема")
        
        # Отмечаем текущую тему
        if self.current_theme == "light":
            light_theme.setIcon(QIcon(resource_path('check.png')))
        else:
            dark_theme.setIcon(QIcon(resource_path('check.png')))
        
        # Привязываем действия
        light_theme.triggered.connect(lambda: self.apply_theme("light"))
        dark_theme.triggered.connect(lambda: self.apply_theme("dark"))
        
        # Показываем меню возле кнопки настроек
        settings_menu.exec(self.settings_button.mapToGlobal(QPoint(0, -settings_menu.sizeHint().height())))

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

    def toggle_bold(self):
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        new_weight = QFont.Weight.Normal if format.fontWeight() == QFont.Weight.Bold else QFont.Weight.Bold
        format.setFontWeight(new_weight)
        cursor.mergeCharFormat(format)

    def toggle_italic(self):
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        format.setFontItalic(not format.fontItalic())
        cursor.mergeCharFormat(format)

    def toggle_underline(self):
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        format.setFontUnderline(not format.fontUnderline())
        cursor.mergeCharFormat(format)

    def toggle_highlight(self):
        cursor = self.text_editor.textCursor()
        format = cursor.charFormat()
        current_color = format.background().color()
        new_color = QColor("transparent") if current_color == QColor("#e4d5ff") else QColor("#e4d5ff")
        format.setBackground(new_color)
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