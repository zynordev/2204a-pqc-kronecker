"""VoiceBox Design System — PyQt6 Stil ve Tema Tanımları.

Referans: /home/halil/Downloads/voicebox-DESIGN.md
- Yüksek kontrastlı editoryal dergi estetiği.
- Temel: Saf Siyah (#0A0A0A) ve Saf Beyaz (#FAFAFA).
- Vurgu: Tek ve agresif Kırmızı (#EF4444).
- Kenar Yumuşatma: İstisnasız HER YERDE 0px (Tamamen keskin, düz, gölgesiz).
- Tipografi: Archivo Black / Arial Black (Başlıklar), Work Sans / Segoe UI (Gövde), Space Mono / Courier New (Kod/Hex).
"""

# Renk Paleti Tokenları
COLOR_PRIMARY = "#0A0A0A"        # Siyah
COLOR_SECONDARY = "#EF4444"      # Kırmızı Vurgu
COLOR_TERTIARY = "#FAFAFA"       # Beyaz

COLOR_BG = "#FAFAFA"             # Saf Beyaz Sayfa Arka Planı
COLOR_SURFACE = "#F5F5F5"        # Kart Arka Planı
COLOR_SURFACE_RAISED = "#E5E5E5" # Vurgulu / Hover Yüzey

COLOR_TEXT_PRIMARY = "#0A0A0A"   # Ana Metin
COLOR_TEXT_SECONDARY = "#525252" # İkincil Metin
COLOR_TEXT_TERTIARY = "#A3A3A3"  # Pasif / Placeholder

COLOR_BORDER_SUBTLE = "#E5E5E5"  # 1px/2px İnce Kenarlık
COLOR_BORDER_MEDIUM = "#D4D4D4"  # Giriş Kutuları Kenarlığı
COLOR_BORDER_STRONG = "#0A0A0A"  # 2px Güçlü Siyah Kenarlık

COLOR_SUCCESS = "#16A34A"        # Başarılı Yeşil
COLOR_WARNING = "#CA8A04"        # Uyarı Sarı
COLOR_ERROR = "#EF4444"          # Hata Kırmızı

# Yazı Tipleri
FONT_DISPLAY = "'Archivo Black', Impact, 'Arial Black', sans-serif"
FONT_UI = "'Work Sans', -apple-system, 'Segoe UI', Helvetica, sans-serif"
FONT_MONO = "'Space Mono', 'Courier New', Consolas, monospace"

# VoiceBox QSS Ana Stil Sayfası
VOICEBOX_QSS = f"""
/* === GENEL SAYFA VE TABAN === */
QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_UI};
    font-size: 13px;
    selection-background-color: {COLOR_PRIMARY};
    selection-color: {COLOR_TERTIARY};
}}

QMainWindow, QDialog {{
    background-color: {COLOR_BG};
}}

/* === DÜĞMELER (BUTTONS) === */
/* Birincil Düğme (Primary Button) */
QPushButton {{
    background-color: {COLOR_PRIMARY};
    color: {COLOR_TERTIARY};
    border: 2px solid {COLOR_PRIMARY};
    border-radius: 0px;
    padding: 10px 20px;
    font-family: {FONT_UI};
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
}}
QPushButton:hover {{
    background-color: {COLOR_SECONDARY};
    border-color: {COLOR_SECONDARY};
    color: {COLOR_TERTIARY};
}}
QPushButton:pressed {{
    background-color: #DC2626;
    border-color: #DC2626;
}}
QPushButton:disabled {{
    background-color: {COLOR_SURFACE_RAISED};
    color: {COLOR_TEXT_TERTIARY};
    border-color: {COLOR_BORDER_SUBTLE};
}}

/* İkincil Düğme (Secondary Button) */
QPushButton[voiceboxRole="secondary"] {{
    background-color: transparent;
    color: {COLOR_TEXT_PRIMARY};
    border: 2px solid {COLOR_PRIMARY};
}}
QPushButton[voiceboxRole="secondary"]:hover {{
    background-color: {COLOR_PRIMARY};
    color: {COLOR_TERTIARY};
}}
QPushButton[voiceboxRole="secondary"]:pressed {{
    background-color: #262626;
}}

/* Tehlikeli / İptal Düğmesi (Destructive) */
QPushButton[voiceboxRole="destructive"] {{
    background-color: {COLOR_SECONDARY};
    color: {COLOR_TERTIARY};
    border: 2px solid {COLOR_SECONDARY};
}}
QPushButton[voiceboxRole="destructive"]:hover {{
    background-color: #DC2626;
    border-color: #DC2626;
}}

/* Küçük Boy Düğme */
QPushButton[voiceboxSize="sm"] {{
    padding: 5px 12px;
    font-size: 11px;
}}

/* === GİRİŞ KUTULARI (INPUTS) === */
QLineEdit, QSpinBox, QComboBox {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT_PRIMARY};
    border: 2px solid {COLOR_BORDER_MEDIUM};
    border-radius: 0px;
    padding: 8px 12px;
    font-family: {FONT_UI};
    font-size: 13px;
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 2px solid {COLOR_PRIMARY};
    background-color: #FFFFFF;
}}
QLineEdit:disabled {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_TEXT_TERTIARY};
}}

/* === KARTLAR VE ÇERÇEVELER (CARDS) === */
QFrame[voiceboxCard="default"] {{
    background-color: {COLOR_BG};
    border: 2px solid {COLOR_BORDER_SUBTLE};
    border-radius: 0px;
    padding: 16px;
}}
QFrame[voiceboxCard="default"]:hover {{
    border: 2px solid {COLOR_BORDER_STRONG};
}}

/* Üstten Kırmızı Şeritli Öne Çıkan Kart */
QFrame[voiceboxCard="elevated"] {{
    background-color: {COLOR_BG};
    border: 2px solid {COLOR_BORDER_SUBTLE};
    border-top: 4px solid {COLOR_SECONDARY};
    border-radius: 0px;
    padding: 16px;
}}

/* Alıntı Kutusu (Pull Quote) */
QFrame[voiceboxCard="quote"] {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER_SUBTLE};
    border-left: 4px solid {COLOR_SECONDARY};
    border-radius: 0px;
    padding: 12px 16px;
}}

/* === SEKME ÇUBUĞU (TAB WIDGET) === */
QTabWidget::pane {{
    border: 2px solid {COLOR_BORDER_STRONG};
    border-top: none;
    background-color: {COLOR_BG};
    border-radius: 0px;
}}
QTabBar::tab {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_TEXT_SECONDARY};
    border: 2px solid {COLOR_BORDER_MEDIUM};
    border-bottom: 2px solid {COLOR_BORDER_STRONG};
    border-radius: 0px;
    padding: 10px 24px;
    font-family: {FONT_UI};
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-right: 4px;
}}
QTabBar::tab:hover {{
    background-color: {COLOR_SURFACE_RAISED};
    color: {COLOR_TEXT_PRIMARY};
}}
QTabBar::tab:selected {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT_PRIMARY};
    border: 2px solid {COLOR_BORDER_STRONG};
    border-top: 4px solid {COLOR_SECONDARY};
    border-bottom: none;
}}

/* === LİSTELER VE TABLOLAR (TABLES & LISTS) === */
QTableWidget, QTreeWidget, QListWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT_PRIMARY};
    border: 2px solid {COLOR_BORDER_STRONG};
    border-radius: 0px;
    gridline-color: {COLOR_BORDER_SUBTLE};
    font-family: {FONT_UI};
    font-size: 12px;
}}
QHeaderView::section {{
    background-color: {COLOR_PRIMARY};
    color: {COLOR_TERTIARY};
    border: none;
    border-right: 1px solid #262626;
    padding: 8px 10px;
    font-family: {FONT_UI};
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    border-radius: 0px;
}}
QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {COLOR_BORDER_SUBTLE};
}}
QTableWidget::item:selected {{
    background-color: {COLOR_SURFACE_RAISED};
    color: {COLOR_TEXT_PRIMARY};
}}

/* === HEX GÖRÜNTÜLEYİCİ METİN ALANI (MONOSPACE CODE) === */
QTextEdit[voiceboxCode="true"] {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_MONO};
    font-size: 11px;
    line-height: 1.5;
    border: 2px solid {COLOR_BORDER_STRONG};
    border-radius: 0px;
    padding: 10px;
}}

/* === İLERLEME ÇUBUĞU (PROGRESS BAR) === */
QProgressBar {{
    background-color: {COLOR_SURFACE};
    border: 2px solid {COLOR_BORDER_STRONG};
    border-radius: 0px;
    text-align: center;
    color: {COLOR_PRIMARY};
    font-weight: 700;
    font-size: 11px;
    height: 22px;
}}
QProgressBar::chunk {{
    background-color: {COLOR_PRIMARY};
}}

/* === KAYDIRMA ÇUBUKLARI (SCROLLBARS) === */
QScrollBar:vertical {{
    background: {COLOR_SURFACE};
    width: 10px;
    margin: 0px;
    border-left: 1px solid {COLOR_BORDER_SUBTLE};
}}
QScrollBar::handle:vertical {{
    background: {COLOR_PRIMARY};
    min-height: 20px;
    border-radius: 0px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {COLOR_SURFACE};
    height: 10px;
    margin: 0px;
    border-top: 1px solid {COLOR_BORDER_SUBTLE};
}}
QScrollBar::handle:horizontal {{
    background: {COLOR_PRIMARY};
    min-width: 20px;
    border-radius: 0px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""
