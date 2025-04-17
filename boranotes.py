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
    QDesktopServices, QTextFrameFormat, QTextBlockFormat
)
from PyQt6.QtCore import Qt, QTimer, QMimeData, QPoint, QUrl, QSize

from themes import get_theme
from about import get_about_content, get_about_title


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Константы приложения
DB_FILE = "notes.db"
MONTHS = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
    7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}


class CustomTextEdit(QTextEdit):
    """Расширенный текстовый редактор с дополнительными функциями форматирования"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_font = QFont("Calibri", 11) # ВОТ ТУТ
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_custom_context_menu)

    def show_custom_context_menu(self, position):
        """Показывает контекстное меню с дополнительными опциями форматирования"""
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

        # Меню форматирования
        format_menu = custom_menu.addMenu(" ✒️  Форматирование                ")
        format_menu.setStyleSheet(theme["menu_style"])
        
        bold_action = format_menu.addAction("Ctrl + B  | Жирный  ")
        italic_action = format_menu.addAction("Ctrl + I  | Курсив  ")
        underline_action = format_menu.addAction("Ctrl + U  | Подчеркнутый  ")
        strikethrough_action = format_menu.addAction("Ctrl + T  | Зачеркнутый  ")  
        highlight_action = format_menu.addAction("Ctrl + H  | Выделить ")
        format_menu.addSeparator()
        clear_format_action = format_menu.addAction("Очистить форматирование")

        # Активация/деактивация пунктов меню в зависимости от наличия выделенного текста
        bold_action.setEnabled(has_selected_text)
        italic_action.setEnabled(has_selected_text)
        underline_action.setEnabled(has_selected_text)
        strikethrough_action.setEnabled(has_selected_text)
        highlight_action.setEnabled(has_selected_text)
        clear_format_action.setEnabled(has_selected_text)
        
        # Меню специальных символов
        special_symbols_menu = custom_menu.addMenu(" 🔣  Специальные символы                ")
        special_symbols_menu.setStyleSheet(theme["menu_style"])
        
        empty_circle_action = special_symbols_menu.addAction("○ Пустой кружок")
        full_circle_action = special_symbols_menu.addAction("● Тёмный кружок")
        dark_arrow_action = special_symbols_menu.addAction("➤ Тёмная стрелочка")
        check_mark_action = special_symbols_menu.addAction("✔ Галочка/готово!")
        cross_mark_action = special_symbols_menu.addAction("✘ Крестик/не готово!")
        music_note_action = special_symbols_menu.addAction("♫ Музыкальная нота")
        heart_note_action = special_symbols_menu.addAction("♥︎ Заполененное сердечко")
        
        # Меню эмодзи
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
        # Стандартные действия редактирования
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

        # Подключение действий форматирования
        bold_action.triggered.connect(lambda: self.apply_formatting('bold'))
        italic_action.triggered.connect(lambda: self.apply_formatting('italic'))
        underline_action.triggered.connect(lambda: self.apply_formatting('underline'))
        strikethrough_action.triggered.connect(lambda: self.apply_formatting('strikethrough'))
        highlight_action.triggered.connect(lambda: self.apply_formatting('highlight'))
        
        clear_format_action.triggered.connect(self.clear_formatting)
        
        # Подключение действий для специальных символов
        empty_circle_action.triggered.connect(lambda: self.insert_special_character("○"))
        full_circle_action.triggered.connect(lambda: self.insert_special_character("●"))
        dark_arrow_action.triggered.connect(lambda: self.insert_special_character("➤"))
        check_mark_action.triggered.connect(lambda: self.insert_special_character("✔"))
        cross_mark_action.triggered.connect(lambda: self.insert_special_character("✘"))
        music_note_action.triggered.connect(lambda: self.insert_special_character("♫"))
        heart_note_action.triggered.connect(lambda: self.insert_special_character("♥︎"))

        # Подключение действий для эмодзи
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
        """Применяет выбранное форматирование к выделенному тексту"""
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
        """Вставляет специальный символ в текущую позицию курсора"""
        cursor = self.textCursor()
        cursor.insertText(character)
        self.setTextCursor(cursor)

    def clear_formatting(self):
        """Очищает форматирование выделенного текста"""
        cursor = self.textCursor()
        format = QTextCharFormat()
        format.setFont(self.default_font)
        format.setBackground(QColor("transparent"))
        cursor.mergeCharFormat(format)

    def insertFromMimeData(self, source: QMimeData):
        """Переопределяет вставку из буфера обмена для сохранения стандартного форматирования"""
        cursor = self.textCursor()
        default_format = QTextCharFormat()
        default_format.setFont(self.default_font)
        cursor.insertText(source.text())
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(default_format)

class NotesApp(QWidget):
    """Основной класс приложения для заметок"""
    
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.setWindowTitle("BORA NOTES")
        self.setGeometry(100, 100, 987, 693)
        self.setMinimumHeight(500)

        # Инициализация переменных состояния
        self.current_note_id = None
        self.skip_delete_confirmation = False
        self._notes_cache = {}
        self.need_save = False
        self.is_notes_list_visible = True
        self.initial_notes_list_width = 200
        self.current_theme = "light"  

        # Настройка таймера автосохранения
        self._save_timer = QTimer()
        self._save_timer.setInterval(1000)
        self._save_timer.timeout.connect(self._perform_auto_save)

        # Инициализация базы данных и интерфейса
        self.create_database()
        
        # Устанавливаем сортировку по умолчанию, если она еще не задана
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

        # Загрузка начальной заметки
        if self.is_first_launch():
            self.new_note()
            self.notes_list.setCurrentRow(0)
        else:
            self.load_last_note()

        # Дополнительные настройки
        self.text_editor.setAcceptRichText(True)
        self.setup_shortcuts()
        self.splitter.splitterMoved.connect(self.check_list_visibility)
        self.title_input.textChanged.connect(self.update_note_title)


    def initUI(self):
        """Инициализирует пользовательский интерфейс"""
        layout = QVBoxLayout()
        layout.setSpacing(5)

        # Создание разделителя для основных панелей
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель (список заметок)
        self.left_container = QWidget()
        self.left_container.setMinimumWidth(10)
        self.left_container.setMaximumWidth(self.width() - 30)
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Поле поиска
        self.search_bar = QLineEdit()
        self.search_bar.setFixedHeight(24)
        self.search_bar.setPlaceholderText("Поиск по записям")
        self.search_bar.textChanged.connect(self.search_notes)
        left_layout.addWidget(self.search_bar)

        # Список заметок
        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.load_note)
        self.notes_list.currentItemChanged.connect(self.on_item_selection_changed) 
        self.notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_notes_list_context_menu)
        left_layout.addWidget(self.notes_list)

        # Правая панель (редактор заметок)
        self.right_container = QWidget()
        self.right_container.setMinimumWidth(90)
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопки управления
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

        # Добавляем вертикальный разделитель
        self.button_separator = QWidget()
        self.button_separator.setFixedSize(1, 24)
        self.button_separator.setStyleSheet("background-color: #ccc;")  # Цвет разделителя

        # Добавляем кнопку изменения цвета текста
        self.btn_color = QPushButton("🎨")
        self.btn_color.setFixedSize(24, 24)
        self.btn_color.clicked.connect(self.show_color_palette)
        self.btn_color.setToolTip("Изменить цвет текста")
        self.btn_color.setEnabled(False)

        # Добавляем кнопку изменения размера текста
        self.btn_size = QPushButton("🤏")
        self.btn_size.setFixedSize(24, 24)
        self.btn_size.clicked.connect(self.show_size_menu)
        self.btn_size.setToolTip("Изменить размер текста")
        self.btn_size.setEnabled(False)

        # Добавляем элементы в layout
        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.btn_new)
        buttons_layout.addWidget(self.btn_delete)
        buttons_layout.addWidget(self.button_separator)
        buttons_layout.addWidget(self.btn_color)
        buttons_layout.addWidget(self.btn_size)  # Добавляем новую кнопку
        buttons_layout.addStretch()
        self.right_layout.addLayout(buttons_layout)

        # Контейнер редактора
        self.editor_container = QWidget()
        editor_layout = QVBoxLayout(self.editor_container)
        editor_layout.setContentsMargins(10, 10, 10, 10)
        editor_layout.setSpacing(10)

        # Поле заголовка
        self.title_input = QLineEdit()
        self.title_input.setFont(QFont("Calibri", 14, QFont.Weight.Bold))
        self.title_input.setPlaceholderText("Без Названия")
        self.title_input.textChanged.connect(self.auto_save)
        self.title_input.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.title_input.customContextMenuRequested.connect(self.show_title_context_menu)
        self.title_input.setTextMargins(-3, 6, 0, 0)  

        # Разделитель
        self.separator = QWidget()
        self.separator.setFixedHeight(1)

        # Текстовый редактор
        self.text_editor = CustomTextEdit()
        self.text_editor.setFont(QFont("Calibri", 11))
        self.text_editor.textChanged.connect(self.auto_save)
        self.text_editor.textChanged.connect(self.auto_format)
        self.text_editor.textChanged.connect(self.update_counter)
        self.text_editor.selectionChanged.connect(self.update_color_button_state)  # Добавьте эту строку
        self.text_editor.setViewportMargins(1, 0, 0, 0)

        editor_layout.addWidget(self.title_input)
        editor_layout.addWidget(self.separator)
        editor_layout.addWidget(self.text_editor)
        self.right_layout.addWidget(self.editor_container)

        # Настройка разделителя
        self.splitter.addWidget(self.left_container)
        self.splitter.addWidget(self.right_container)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([self.initial_notes_list_width, 600])
        self.splitter.setCollapsible(1, False)
        self.splitter.setHandleWidth(3)

        layout.addWidget(self.splitter)

        # Нижняя панель
        bottom_panel = QWidget()
        bottom_panel.setFixedHeight(23)
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(1, 0, 0, 0)

        # Кнопки нижней панели
        self.sort_button = QPushButton("🗃")
        self.sort_button.setFixedSize(25, 23)
        self.sort_button.clicked.connect(self.show_sort_menu)
        self.sort_button.setToolTip("Сортировка заметок")
        bottom_layout.addWidget(self.sort_button)

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

        # Счетчик слов и символов
        self.counter_label = QLabel()
        bottom_layout.addWidget(self.counter_label)

        layout.addWidget(bottom_panel)
        self.setLayout(layout)
        
        # Применяем тему
        self.apply_theme(self.current_theme)

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
        """Открывает Spotify в браузере с подтверждением"""
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
        """Обновляет заголовок текущей заметки в списке и сохраняет его немедленно"""
        if not self.current_note_id:
            return
            
        title = self.title_input.text().strip()
        is_pinned = self._notes_cache[self.current_note_id].get('pinned', False)
        
        # Обновляем заголовок в списке
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == self.current_note_id:
                current_text = item.text()
                date_line = current_text.split('\n')[1] if '\n' in current_text else ""
                new_title = title if title else "Без Названия"
                display_title = f"⭐ {new_title}" if is_pinned else new_title
                item.setText(f"{display_title}\n{date_line}")
                break
        
        # Обновляем кэш
        if self.current_note_id in self._notes_cache:
            self._notes_cache[self.current_note_id]['title'] = title
        
        # Немедленно сохраняем заголовок в базу данных
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET title = ? WHERE id = ?", 
                            (title, self.current_note_id))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении заголовка: {e}")



    def show_notes_list_context_menu(self, position):
        """Показывает контекстное меню для списка заметок"""
        theme = get_theme(self.current_theme)
        context_menu = QMenu(self)
        context_menu.setStyleSheet(theme["menu_style"])
        
        # Получаем элемент под курсором
        item = self.notes_list.itemAt(position)
        
        if item:
            # Если курсор над элементом списка
            note_id = item.data(Qt.ItemDataRole.UserRole)
            is_pinned = self._notes_cache[note_id].get('pinned', False)
            
            # Проверяем количество закрепленных заметок
            pinned_count = sum(1 for note in self._notes_cache.values() if note.get('pinned', False))
            
            # Добавляем действие для закрепления/открепления
            pin_action = context_menu.addAction("⭐ Открепить" if is_pinned else "⭐ Закрепить")
            pin_action.triggered.connect(lambda: self.toggle_pin_status(note_id))
            
            # Делаем кнопку неактивной, если достигнут лимит закрепленных заметок
            if not is_pinned and pinned_count >= 3:
                pin_action.setEnabled(False)
                pin_action.setText("⭐ Закрепить (достигнут лимит)")
            
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
        
        # Устанавливаем цвет разделителя в зависимости от темы
        separator_color = "#555555" if theme_name == "dark" else "#ccc"
        self.button_separator.setStyleSheet(f"background-color: {separator_color};")
        
        if hasattr(self, 'btn_color'):
            self.update_color_button_state()

        QApplication.instance().setStyleSheet(theme["tooltip_style"])
        
        # Обновляем стиль закрепленных заметок
        current_item = self.notes_list.currentItem()
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) in self._notes_cache:
                note_id = item.data(Qt.ItemDataRole.UserRole)
                if self._notes_cache[note_id].get('pinned', False):
                    is_selected = (item == current_item)
                    
                    if theme_name == "light":
                        if is_selected:
                            item.setBackground(QColor("#eecbe3"))  # Светлая тема, выбрана
                        else:
                            item.setBackground(QColor("#f1dbea"))  # Светлая тема, не выбрана
                    else:
                        if is_selected:
                            item.setBackground(QColor("#858585"))  # Темная тема, выбрана
                        else:
                            item.setBackground(QColor("#484444"))  # Темная тема, не выбрана
        
        self.update_highlight_color()
        self.save_theme_setting(theme_name)



    def update_highlight_color(self):
        """Обновляет цвет выделения текста при смене темы"""
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
        """Обрабатывает изменение размера окна"""
        self.left_container.setMaximumWidth(self.width() - 90)
        super().resizeEvent(event)

    def check_list_visibility(self, pos, index):
        """Проверяет видимость списка заметок при перемещении разделителя"""
        if pos <= 10:
            self.is_notes_list_visible = False
            self.toggle_button.setText("▶")
        else:
            self.is_notes_list_visible = True
            self.toggle_button.setText("◀")

    def toggle_notes_list(self):
        """Переключает видимость списка заметок"""
        if self.is_notes_list_visible:
            self.left_container.hide()
            self.toggle_button.setText("▶")
        else:
            self.left_container.show()
            self.toggle_button.setText("◀")
            self.splitter.setSizes([self.initial_notes_list_width, self.splitter.sizes()[1]])
        self.is_notes_list_visible = not self.is_notes_list_visible

    def _perform_auto_save(self):
        """Выполняет автосохранение заметки"""
        if self.need_save and self.current_note_id:
            title = self.title_input.text().strip()
            content = self.text_editor.toHtml()

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET title = ?, content = ?, last_accessed = datetime('now', 'localtime') WHERE id = ?", 
                            (title, content, self.current_note_id))
                conn.commit()

            self._notes_cache[self.current_note_id] = {'title': title, 'content': content}
            
            # Проверяем текущий способ сортировки
            current_sort = None
            try:
                cursor.execute("SELECT value FROM settings WHERE key = 'sort_method'")
                result = cursor.fetchone()
                if result:
                    current_sort = result[0]
            except sqlite3.Error:
                pass
            
            # Если сортировка по времени последнего изменения, обновляем список
            if current_sort in ["modified_desc", "modified_asc"]:
                self.notes_list.blockSignals(True)
                current_row = self.notes_list.currentRow()
                self.load_notes()  # Перезагружаем список заметок с учетом новой сортировки
                
                # Находим и выбираем текущую заметку в обновленном списке
                for i in range(self.notes_list.count()):
                    if self.notes_list.item(i).data(Qt.ItemDataRole.UserRole) == self.current_note_id:
                        self.notes_list.setCurrentRow(i)
                        break
                
                self.notes_list.blockSignals(False)
            else:
                # Для других типов сортировки просто обновляем заголовок
                self.notes_list.blockSignals(True)
                current_row = self.notes_list.currentRow()
                self.load_notes()
                self.notes_list.setCurrentRow(current_row)
                self.notes_list.blockSignals(False)
            
            self.need_save = False
        self._save_timer.stop()


    def create_database(self):
        """Создает базу данных, если она не существует"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, created_at TEXT, last_accessed TEXT)")
            
            # Проверяем, существует ли уже колонка pinned
            try:
                cursor.execute("SELECT pinned FROM notes LIMIT 1")
            except sqlite3.OperationalError:
                # Если колонки нет, добавляем ее
                cursor.execute("ALTER TABLE notes ADD COLUMN pinned INTEGER DEFAULT 0")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON notes(last_accessed)")
            cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            conn.commit()

    def load_notes(self):
        """Загружает список заметок из базы данных"""
        self.notes_list.clear()
        
        # Устанавливаем режим переноса текста и запрещаем обрезание
        self.notes_list.setWordWrap(True)
        self.notes_list.setUniformItemSizes(False)
        
        # Получаем текущий способ сортировки
        current_sort = "date_desc"  # По умолчанию
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'sort_method'")
                result = cursor.fetchone()
                if result:
                    current_sort = result[0]
        except sqlite3.Error:
            pass
        
        # Загружаем заметки из БД с учетом сортировки
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # Сначала загружаем закрепленные заметки (всегда сверху)
            cursor.execute("SELECT id, title, created_at FROM notes WHERE pinned = 1 ORDER BY created_at DESC")
            pinned_notes = cursor.fetchall()
            
            # Затем загружаем обычные заметки с учетом сортировки
            if current_sort == "date_desc":
                cursor.execute("SELECT id, title, created_at FROM notes WHERE pinned = 0 ORDER BY created_at DESC")
            elif current_sort == "date_asc":
                cursor.execute("SELECT id, title, created_at FROM notes WHERE pinned = 0 ORDER BY created_at ASC")
            elif current_sort == "name_asc":
                cursor.execute("SELECT id, title, created_at FROM notes WHERE pinned = 0 ORDER BY CASE WHEN title = '' THEN 'Без названия' ELSE title END COLLATE NOCASE ASC")
            elif current_sort == "name_desc":
                cursor.execute("SELECT id, title, created_at FROM notes WHERE pinned = 0 ORDER BY CASE WHEN title = '' THEN 'Без названия' ELSE title END COLLATE NOCASE DESC")
            elif current_sort == "modified_desc":
                cursor.execute("SELECT id, title, created_at FROM notes WHERE pinned = 0 ORDER BY last_accessed DESC")
            else:  # modified_asc
                cursor.execute("SELECT id, title, created_at FROM notes WHERE pinned = 0 ORDER BY last_accessed ASC")
            
            regular_notes = cursor.fetchall()
            
            # Добавляем закрепленные заметки в список
            for note in pinned_notes:
                self._add_note_item(note, is_pinned=True)
            
            # Добавляем разделитель, если есть и закрепленные и обычные заметки
            if pinned_notes and regular_notes:
                separator = QListWidgetItem()
                separator.setFlags(Qt.ItemFlag.NoItemFlags)
                separator.setSizeHint(QSize(self.notes_list.width() - 10, 1))
                separator.setBackground(QColor("#e0e0e0" if self.current_theme == "light" else "#444"))
                self.notes_list.addItem(separator)
            
            # Добавляем обычные заметки
            for note in regular_notes:
                self._add_note_item(note, is_pinned=False)
            
            self.check_empty_state()


    def load_note(self):
        """Загружает выбранную заметку для редактирования"""
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
        """Выполняет поиск по заметкам"""
        search_text = self.search_bar.text().strip().lower()
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            item.setHidden(not any(search_text in text.lower() for text in item.text().split('\n')))

    def load_last_note(self):
        """Загружает последнюю открытую заметку"""
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
        """Запускает таймер автосохранения"""
        self.need_save = True
        if not self._save_timer.isActive():
            self._save_timer.start()

    def show_empty_state(self):
        """Показывает сообщение, когда нет заметок"""
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
        """Проверяет, есть ли заметки, и показывает соответствующее состояние"""
        if self.notes_list.count() == 0:
            self.show_empty_state()
        else:
            if hasattr(self, 'empty_state_label'):
                self.empty_state_label.hide()
            self.editor_container.show()

    def new_note(self):
        """Создает новую заметку"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (title, content, created_at, last_accessed) VALUES (?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))", ("", ""))
            conn.commit()
            note_id = cursor.lastrowid

        self.load_notes()
        self.current_note_id = note_id
        self.title_input.clear()
        self.text_editor.clear()
        
        # Находим и выбираем новую заметку в списке
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.notes_list.setCurrentItem(item)
                break
                
        self.check_empty_state()

    def delete_note(self):
        """Удаляет текущую заметку"""
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
        """Настраивает горячие клавиши для форматирования текста"""
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
        """Переключает жирное начертание выделенного текста"""
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
        """Переключает курсивное начертание выделенного текста"""
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
        """Переключает подчеркивание выделенного текста"""
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
        """Переключает зачеркивание выделенного текста"""
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
        """Переключает выделение фоном для выделенного текста"""
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
        """Отменяет последнее действие в редакторе"""
        self.text_editor.undo()

    def auto_format(self):
        """Автоматически форматирует текст при вводе"""
        cursor = self.text_editor.textCursor()
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        text = cursor.selectedText()
        if "--" in text:
            cursor.insertText(text.replace("--", "—"))

    def update_counter(self):
        """Обновляет счетчик слов и символов"""
        text = self.text_editor.toPlainText()
        char_count = len(text)
        word_count = len(text.split())
        self.counter_label.setText(f"Количество слов: {word_count} | Количество символов: {char_count}")

    def is_first_launch(self):
        """Проверяет, является ли это первым запуском приложения"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM notes")
            count = cursor.fetchone()[0]
            return count == 0

    def show_sort_menu(self):
        """Показывает меню сортировки заметок"""
        sort_menu = QMenu(self)
        sort_menu.setFont(QFont("Calibri", 9))
        
        theme = get_theme(self.current_theme)
        sort_menu.setStyleSheet(theme["sort_menu_style"])

        # Получаем текущий способ сортировки из базы данных
        current_sort = "date_desc"  # По умолчанию - от новых к старым
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = 'sort_method'")
                result = cursor.fetchone()
                if result:
                    current_sort = result[0]
        except sqlite3.Error:
            # Если произошла ошибка, используем значение по умолчанию
            pass

        # Добавляем пункты меню с галочкой для активного способа сортировки
        new_to_old = sort_menu.addAction("От новых к старым записям" + ("   ✓" if current_sort == "date_desc" else ""))
        old_to_new = sort_menu.addAction("От старых к новым записям" + ("   ✓" if current_sort == "date_asc" else ""))
        
        sort_menu.addSeparator()
        
        name_az = sort_menu.addAction("По имени файла (от А до Я)" + ("   ✓" if current_sort == "name_asc" else ""))
        name_za = sort_menu.addAction("По имени файла (от Я до А)" + ("   ✓" if current_sort == "name_desc" else ""))
        
        sort_menu.addSeparator()
        
        modified_new = sort_menu.addAction("По времени последнего изменения (от новых к старым)" + ("   ✓" if current_sort == "modified_desc" else ""))
        modified_old = sort_menu.addAction("По времени последнего изменения (от старых к новым)" + ("   ✓" if current_sort == "modified_asc" else ""))

        # Привязываем действия
        new_to_old.triggered.connect(lambda: self.sort_notes("date_desc"))
        old_to_new.triggered.connect(lambda: self.sort_notes("date_asc"))
        name_az.triggered.connect(lambda: self.sort_notes("name_asc"))
        name_za.triggered.connect(lambda: self.sort_notes("name_desc"))
        modified_new.triggered.connect(lambda: self.sort_notes("modified_desc"))
        modified_old.triggered.connect(lambda: self.sort_notes("modified_asc"))

        # Показываем меню возле кнопки, но направленное вверх
        menu_height = sort_menu.sizeHint().height()
        sort_menu.exec(self.sort_button.mapToGlobal(QPoint(0, -menu_height)))

    def sort_notes(self, sort_type):
        """Сортирует список заметок по выбранному критерию"""
        # Сохраняем выбранный способ сортировки
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                # Проверяем существование таблицы settings
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
                if not cursor.fetchone():
                    # Если таблицы нет, создаем ее
                    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
                
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                            ("sort_method", sort_type))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении способа сортировки: {e}")
        
        # Сохраняем текущий выбранный элемент
        current_id = None
        if self.notes_list.currentItem():
            current_id = self.notes_list.currentItem().data(Qt.ItemDataRole.UserRole)
        
        # Перезагружаем список заметок с учетом новой сортировки
        self.load_notes()
        
        # Восстанавливаем выбор, если возможно
        if current_id:
            for i in range(self.notes_list.count()):
                item = self.notes_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) == current_id:
                    self.notes_list.setCurrentRow(i)
                    break


    def show_color_palette(self):
        """Показывает палитру предустановленных цветов для текста"""
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
        """Применяет выбранный цвет к выделенному тексту и сбрасывает выделение"""
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
        """Обновляет цвета текста по умолчанию при смене темы"""
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
        """Обновляет состояние кнопки изменения цвета в зависимости от выделения текста"""
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

    def update_default_text_colors(self):
        """Обновляет цвета текста по умолчанию при смене темы"""
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

    def show_size_menu(self):
        """Показывает меню для изменения размера текста"""
        if not self.text_editor.textCursor().hasSelection():
            return
            
        size_menu = QMenu(self)
        size_menu.setFont(QFont("Calibri", 9))
        
        # Создаем сетку размеров
        size_grid = QWidget()
        
        # Устанавливаем фон и границу в зависимости от темы
        if self.current_theme == "dark":
            # Для темной темы - цвет 3a3a3a
            size_grid.setStyleSheet("background-color: #3a3a3a; border-radius: 3px;")
        else:
            # Для светлой темы - цвет fefefe с обводкой f2f2f2
            size_grid.setStyleSheet("""
                background-color: #fefefe; 
                border-radius: 3px;
                border: 1px solid #f2f2f2;
            """)
        
        grid_layout = QGridLayout(size_grid)
        grid_layout.setSpacing(4)
        
        # Создаем кнопки размеров
        size_buttons = [
            {"text": "H1", "size": 18, "tooltip": "Заголовок 1 уровня"},
            {"text": "H2", "size": 14, "tooltip": "Заголовок 2 уровня"},
            {"text": "н", "size": 11, "tooltip": "Размер по умолчанию"},
            {"text": ".", "size": 9, "tooltip": "Ваще мелебнкий шрифт жестб"}
        ]
        
        # Размещаем кнопки в сетке горизонтально
        for col, button_info in enumerate(size_buttons):
            size_button = QPushButton(button_info["text"])
            # Устанавливаем размер 20x20
            size_button.setFixedSize(20, 20)
            size_button.setToolTip(button_info["tooltip"])
            
            # Настраиваем шрифт для кнопок
            font = size_button.font()
            font.setPointSize(8)  # Немного уменьшаем размер шрифта
            size_button.setFont(font)
            
            # Добавляем обводку и эффект при наведении в зависимости от темы
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
            
            # Подключаем обработчик нажатия
            font_size = button_info["size"]
            size_button.clicked.connect(lambda checked=False, size=font_size: self.apply_font_size_and_clear(size))
            
            grid_layout.addWidget(size_button, 0, col)
        
        # Настраиваем отступы для сетки
        grid_layout.setContentsMargins(7, 4, 7, 4)
        
        # Создаем действие для вставки виджета сетки в меню
        action = QWidgetAction(size_menu)
        action.setDefaultWidget(size_grid)
        size_menu.addAction(action)
        
        # Убираем стандартные границы и фон меню
        size_menu.setStyleSheet("""
            QMenu {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Показываем меню под кнопкой
        size_menu.exec(self.btn_size.mapToGlobal(QPoint(0, self.btn_size.height())))



    def apply_font_size_and_clear(self, size):
        """Применяет выбранный размер шрифта к выделенному тексту и сбрасывает выделение"""
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            return
            
        # Сохраняем позицию конца выделения
        end_position = cursor.selectionEnd()
        
        # Применяем размер шрифта
        format = QTextCharFormat()
        format.setFontPointSize(size)
        cursor.mergeCharFormat(format)
        
        # Сбрасываем выделение, устанавливая курсор в конец бывшего выделения
        cursor.setPosition(end_position)
        self.text_editor.setTextCursor(cursor)
        
        # Закрываем меню
        QApplication.activePopupWidget().close() if QApplication.activePopupWidget() else None
        
        # Явно устанавливаем фокус обратно на текстовый редактор
        self.text_editor.setFocus()
        
        # Сохраняем изменения
        self.auto_save()

    def update_color_button_state(self):
        """Обновляет состояние кнопок форматирования в зависимости от выделения текста"""
        has_selection = self.text_editor.textCursor().hasSelection()
        self.btn_color.setEnabled(has_selection)
        self.btn_size.setEnabled(has_selection)  # Добавляем обновление состояния кнопки размера
        
        theme = get_theme(self.current_theme)
        if has_selection:
            # Используем тот же стиль, что и для других кнопок
            self.btn_color.setStyleSheet(theme["button_style"])
            self.btn_size.setStyleSheet(theme["button_style"])
        else:
            if self.current_theme == "dark":
                inactive_style = """
                    QPushButton {
                        background-color: #232323;
                        color: #555;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #232323;
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
            self.btn_size.setStyleSheet(inactive_style)

    def toggle_pin_status(self, note_id):
        """Переключает статус закрепления заметки"""
        # Получаем текущее количество закрепленных заметок
        pinned_count = sum(1 for note in self._notes_cache.values() if note.get('pinned', False))
        
        # Проверяем статус текущей заметки
        is_currently_pinned = self._notes_cache[note_id].get('pinned', False)
        
        if not is_currently_pinned and pinned_count >= 3:
            QMessageBox.information(self, "Ошибка", "Можно закрепить не более 3 заметок")
            return
        
        # Обновляем статус в базе данных
        new_pinned_status = 0 if is_currently_pinned else 1
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notes SET pinned = ? WHERE id = ?",
                            (new_pinned_status, note_id))
                conn.commit()
                
                # Обновляем кэш
                self._notes_cache[note_id]['pinned'] = not is_currently_pinned
                
                # Перезагружаем список заметок
                self.load_notes()
                
                # Выбираем текущую заметку в обновленном списке
                for i in range(self.notes_list.count()):
                    item = self.notes_list.item(i)
                    if item and item.data(Qt.ItemDataRole.UserRole) == note_id:
                        self.notes_list.setCurrentItem(item)
                        break
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось обновить статус закрепления: {str(e)}")

    def _add_note_item(self, note, is_pinned):
        """Добавляет элемент заметки в список"""
        note_id = note[0]
        title = note[1] if note[1] else "Без Названия"
        date_obj = datetime.strptime(note[2].split('.')[0], '%Y-%m-%d %H:%M:%S')
        date = f"{date_obj.day} {MONTHS[date_obj.month]} {date_obj.year} {date_obj.hour:02d}:{date_obj.minute:02d}"
        
        # Добавляем звездочку для закрепленных заметок
        display_title = f"⭐ {title}" if is_pinned else title
        
        item = QListWidgetItem()
        item.setText(f"{display_title}\n{date}")
        item.setData(Qt.ItemDataRole.UserRole, note_id)
        
        # Устанавливаем флаг, чтобы текст не обрезался
        item.setFlags(item.flags() | Qt.ItemFlag.ItemNeverHasChildren)
        
        # Устанавливаем специальный фон для закрепленных заметок в зависимости от темы
        if is_pinned:
            if self.current_theme == "light":
                item.setBackground(QColor("#f1dbea"))  # Светлая тема, не выбрана
            else:
                item.setBackground(QColor("#484444"))  # Темная тема, не выбрана
        
        self.notes_list.addItem(item)
        
        # Обновляем кэш
        if note_id not in self._notes_cache:
            self._notes_cache[note_id] = {'title': note[1], 'content': None, 'pinned': is_pinned}
        else:
            self._notes_cache[note_id]['pinned'] = is_pinned
        
        # Обновляем кэш
        if note_id not in self._notes_cache:
            self._notes_cache[note_id] = {'title': note[1], 'content': None, 'pinned': is_pinned}
        else:
            self._notes_cache[note_id]['pinned'] = is_pinned

    def on_item_selection_changed(self, current, previous):
        """Обрабатывает изменение выбора элемента в списке заметок"""
        # Обновляем цвета закрепленных заметок при изменении выбора
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
                        item.setBackground(QColor("#eecbe3"))  # Светлая тема, выбрана
                    else:
                        item.setBackground(QColor("#f1dbea"))  # Светлая тема, не выбрана
                else:
                    if is_selected:
                        item.setBackground(QColor("#858585"))  # Темная тема, выбрана
                    else:
                        item.setBackground(QColor("#484444"))  # Темная тема, не выбрана


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('icon.ico')))
    app.setStyle('Fusion')
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())
