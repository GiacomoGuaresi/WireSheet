"""Foglio di stile dell'applicazione."""

ACCENT = "#2f6fdf"
DANGER = "#c62828"
OK = "#1a7f37"

STYLE = f"""
QWidget#stack, QScrollArea#cardScroll {{ background: #eef0f3; }}

QFrame#CableCard {{
    background: white;
    border: 1px solid #d5d9e0;
    border-radius: 8px;
}}
QFrame#CableCard[active="true"] {{ border: 2px solid {ACCENT}; }}

QFrame#TitleBlockCard {{
    background: #fdf6e3;
    border: 1px solid #e3d3a4;
    border-radius: 8px;
}}
QFrame#TitleBlockCard QLineEdit, QFrame#TitleBlockCard QSpinBox {{ background: white; }}
QLabel#cardTitle {{ font-weight: bold; font-size: 11pt; color: #3b4250; }}

QLineEdit#cardName {{
    font-weight: bold;
    font-size: 11pt;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 2px 4px;
    background: transparent;
}}
QLineEdit#cardName:hover {{ border-color: #d5d9e0; }}
QLineEdit#cardName:focus {{ border-color: {ACCENT}; background: white; }}

QLabel#summary {{ color: #5a6270; }}
QLabel#statusOk {{ color: #1a7f37; font-weight: bold; }}
QLabel#statusError {{ color: #b00000; font-weight: bold; }}
QLabel#errors {{ color: #b00000; }}
QLabel#endTitle {{ font-weight: bold; color: #3b4250; }}

QToolButton#cardAction {{
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 2px 6px;
}}
QToolButton#cardAction:hover {{ border-color: #c4cad4; background: #f3f5f8; }}

QPushButton#primary {{
    background: {ACCENT};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 5px 14px;
    font-weight: bold;
}}
QPushButton#primary:hover {{ background: #2560c8; }}

QPushButton#addCable {{
    border: 2px dashed #b5bcc8;
    border-radius: 8px;
    padding: 12px;
    color: #4a5568;
    background: transparent;
}}
QPushButton#addCable:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}

QWidget#previewPanel {{ background: #f7f8fa; }}
"""
