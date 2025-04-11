def get_theme(theme_name):
    """
    Возвращает словарь со стилями для указанной темы.
    
    Args:
        theme_name (str): Название темы ('light', 'dark')
        
    Returns:
        dict: Словарь со стилями для темы
    """
    themes = {
        "light": {
            "main_window": "* { font-family: Calibri; } QWidget { background-color: #EDE7F6; border-radius: 8px; }",
            "notes_list": """
                QListWidget {
                    background-color: #D1C4E9;
                    font-family: Calibri;
                    min-height: 400px;
                    border-radius: 8px;
                    padding: 5px;
                    border: 0.5px solid #efe2e7;
                    box-shadow: 0 2px 4px rgba(248, 241, 243, 0.3);
                }
                QListWidget::item {
                    padding: 10px;
                    margin: 5px;
                    background: #EDE7F6;
                    border-radius: 4px;
                    border: 0.5px solid #efe2e7;
                }
                QListWidget::item:selected {
                    background-color: #B39DDB;
                    color: white;
                    border: 0.5px solid #aa95cf;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #EDE7F6;
                    width: 7px;
                    border-radius: 4px;
                    margin: 4px 4px 4px 0;
                }
                QScrollBar::handle:vertical {
                    background: #B39DDB;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
                QScrollBar:horizontal {
                    height: 0;
                }
            """,
            
            "search_bar": "background-color: #D1C4E9; padding-left: 10px; border: 0.5px solid #efe2e7; border-radius: 4px; color: #686274;",
            
            "editor_container": "background-color: #FFFFFF; border-radius: 8px; border: 0.5px solid #efe2e7; box-shadow: 0 2px 4px rgba(248, 241, 243, 0.3);",
            
            "text_editor": """
                QTextEdit {
                    background-color: transparent;
                    border: none;
                    color: #4d4d4d;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #EDE7F6;
                    width: 7px;
                    border-radius: 4px;
                    margin: 4px 4px 4px 0;
                }
                QScrollBar::handle:vertical {
                    background: #B39DDB;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0;
                }
                QScrollBar:horizontal {
                    height: 0;
                }
            """,
            
            "title_input": "background-color: transparent; border: none; padding-left: 5px; color: #000000;",
            
            "separator": """
                background-color: #efe2e7;
                margin-left: 5px;
                margin-right: 5px;
                margin-bottom: 5px;
                min-height: 1px;
                max-height: 1px;
                border: none;
            """,
            
            "counter_label": "QLabel { color: #7f7377; font-size: 11px; margin-right: 10px; }",
            
            "button_style": "QPushButton { background-color: #D1C4E9; border: none; border-radius: 4px; color: #7f7377; } QPushButton:hover { background-color: #B39DDB; color: #7f7377; }",
            
            "sort_button": "QPushButton { background-color: #D1C4E9; border: none; border-radius: 4px; color: #7f7377; margin-left: 1px; } QPushButton:hover { background-color: #B39DDB; color: #7f7377; }",
            
            "settings_button": "QPushButton { background-color: #D1C4E9; border: none; border-radius: 4px; color: #7f7377; margin-left: 1px; text-align: center; padding: 0; } QPushButton:hover { background-color: #B39DDB; color: #7f7377; }",
            
            "vertical_divider": "background-color: #efe2e7;",
            
            "empty_state_label": "QLabel { background-color: #D1C4E9; border-radius: 8px; padding: 20px; font-size: 14px; color: #7f7377; border: 0.5px solid #efe2e7; }",
            
            "menu_style": """
                QMenu {
                    background-color: rgba(255, 255, 255, 0.95);
                    border: 0.5px solid #efe2e7;
                    border-radius: 10px;
                    padding: 5px;
                }
                QMenu::item {
                    color: #7f7377;
                    padding: 4px 20px 6px 10px;
                    margin: 2px 4px;
                    border-radius: 5px;
                    min-width: 180px;
                }
                QMenu::item:selected {
                    background-color: #ece0f2;
                    color: #7f7377;
                    border-radius: 5px;
                }
                
                QMenu::item:disabled {
                    color: #dbdbdb;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #efe2e7;
                    margin: 3px 5px;
                }
            """,
                        
            "sort_menu_style": """
                QMenu {
                    background-color: rgba(255, 255, 255, 0.95);
                    border: 0.5px solid #efe2e7;
                    border-radius: 10px;
                    padding: 5px;
                }
                QMenu::item {
                    color: #7f7377;
                    padding: 5px 20px 5px 10px;
                    margin: 2px 8px;
                    border-radius: 5px;
                    min-width: 280px;
                }
                QMenu::item:selected {
                    background-color: #ece0f2;
                    color: #7f7377;
                    border-radius: 5px;
                }

                QMenu::separator {
                    height: 1px;
                    background-color: #efe2e7;
                    margin: 3px 5px;
                }
            """,

            "tooltip_style": """
                QToolTip {
                    background-color: #f8f8f8;
                    color: #333333;
                    border: 1px solid #cccccc;
                    padding: 2px;
                    border-radius: 3px;
                    font-family: Calibri;
                    font-size: 11px;
                }
            """,
            
            "message_box": "QMessageBox { background-color: #EDE7F6; } QPushButton { width: 120px; height: 30px; border-radius: 4px; background-color: #EDE7F6; border: 0.5px solid #efe2e7; padding: 5px 15px; } QPushButton:hover { background-color: #D1C4E9; } QCheckBox { background-color: #EDE7F6; }"
        },
        




        "dark": {
            "main_window": "* { font-family: Calibri; } QWidget { background-color: #1E1E1E; border-radius: 8px; }",
            "notes_list": """
                QListWidget {
                    background-color: #2D2D2D;
                    font-family: Calibri;
                    min-height: 400px;
                    border-radius: 8px;
                    padding: 5px;
                    border: 0.2px solid #3C3C3C;
                    box-shadow: 0 2px 4px rgba(248, 241, 243, 0.3);
                }
                QListWidget::item {
                    padding: 10px;
                    margin: 5px;
                    background: #3C3C3C;
                    border-radius: 4px;
                    border: 0.2px solid #3C3C3C;
                    color: #CCCCCC;
                }
                QListWidget::item:selected {
                    background-color: #5C5C5C;
                    color: white;
                    border: 0.2px solid #3C3C3C;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #3C3C3C;
                    width: 7px;
                    border-radius: 4px;
                    margin: 4px 4px 4px 0;
                }
                QScrollBar::handle:vertical {
                    background: #5C5C5C;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
                QScrollBar:horizontal {
                    height: 0;
                }
            """,
            
            "search_bar": "background-color: #2D2D2D; padding-left: 10px; border: 0.2px solid #3C3C3C; border-radius: 4px; color: #CCCCCC;",
            
            "editor_container": "background-color: #2D2D2D; border-radius: 8px; border: 0.2px solid #3C3C3C; box-shadow: 0 2px 4px rgba(248, 241, 243, 0.3);",
            
            "text_editor": """
                QTextEdit {
                    background-color: transparent;
                    border: none;
                    color: #E0E0E0;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #3C3C3C;
                    width: 7px;
                    border-radius: 4px;
                    margin: 4px 4px 4px 0;
                }
                QScrollBar::handle:vertical {
                    background: #5C5C5C;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0;
                }
                QScrollBar:horizontal {
                    height: 0;
                }
            """,
            
            "title_input": "background-color: transparent; border: none; padding-left: 5px; color: #FFFFFF;",
            
            "separator": """
                background-color: #5C5C5C;
                margin-left: 5px;
                margin-right: 5px;
                margin-bottom: 5px;
                min-height: 1px;
                max-height: 1px;
                border: none;
            """,
            
            "counter_label": "QLabel { color: #CCCCCC; font-size: 11px; margin-right: 10px; }",
            
            "button_style": "QPushButton { background-color: #2D2D2D; border: none; border-radius: 4px; color: #CCCCCC; } QPushButton:hover { background-color: #5C5C5C; color: #CCCCCC; }",
            
            "sort_button": "QPushButton { background-color: #2D2D2D; border: none; border-radius: 4px; color: #CCCCCC; margin-left: 1px; } QPushButton:hover { background-color: #5C5C5C; color: #CCCCCC; }",
            
            "settings_button": "QPushButton { background-color: #2D2D2D; border: none; border-radius: 4px; color: #CCCCCC; margin-left: 1px; text-align: center; padding: 0; } QPushButton:hover { background-color: #5C5C5C; color: #CCCCCC; }",
            
            "vertical_divider": "background-color: #3C3C3C;",
            
            "empty_state_label": "QLabel { background-color: #2D2D2D; border-radius: 8px; padding: 20px; font-size: 14px; color: #CCCCCC; border: 0.2px solid #3C3C3C; }",
            
            "menu_style": """
                QMenu {
                    background-color: rgba(45, 45, 45, 0.95);
                    border: 0.2px solid #3C3C3C;
                    border-radius: 10px;
                    padding: 5px;
                }
                QMenu::item {
                    color: #CCCCCC;
                    padding: 5px 20px 5px 10px;
                    margin: 2px 4px;
                    border-radius: 5px;
                    min-width: 180px;
                }
                QMenu::item:selected {
                    background-color: #5C5C5C;
                    color: #CCCCCC;
                    border-radius: 5px;
                }

                QMenu::item:disabled {
                    color: #4b4b4b;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #3C3C3C;
                    margin: 3px 5px;
                }
            """,

            "sort_menu_style": """
                QMenu {
                    background-color: rgba(45, 45, 45, 0.95);
                    border: 0.2px solid #3C3C3C;
                    border-radius: 10px;
                    padding: 5px;
                }
                QMenu::item {
                    color: #CCCCCC;
                    padding: 4px 20px 6px 10px;
                    margin: 2px 8px;
                    border-radius: 5px;
                    min-width: 280px;
                }
                QMenu::item:selected {
                    background-color: #5C5C5C;
                    color: #CCCCCC;
                    border-radius: 5px;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #3C3C3C;
                    margin: 3px 5px;
                }
            """,

            "tooltip_style": """
                QToolTip {
                    background-color: #333333;
                    color: #f8f8f8;
                    border: 1px solid #555555;
                    padding: 2px;
                    border-radius: 3px;
                    font-family: Calibri;
                    font-size: 11px;
                }
            """,
            
            "message_box": "QMessageBox { background-color: #2D2D2D; color: #CCCCCC; } QPushButton { width: 120px; height: 30px; border-radius: 4px; background-color: #3C3C3C; border: 0.2px solid #3C3C3C; padding: 5px 15px; color: #CCCCCC; } QPushButton:hover { background-color: #5C5C5C; } QCheckBox { background-color: #2D2D2D; color: #CCCCCC; } QLabel { color: #CCCCCC; }"
        }
    }
    
    return themes.get(theme_name, themes["light"])