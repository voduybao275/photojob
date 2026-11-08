<<<<<<< HEAD
"""
Photoshop CC Interface Clone in Python using PyQt6
File: main.py
Description: A pixel-accurate, fully styled Photo Job interface built with PyQt6.
Features:
- Ctrl+Z / Ctrl+Alt+Z: Undo previous step (quay lại bước trước)
- Ctrl+Shift+Z / Ctrl+Y: Redo next step (làm lại bước kế tiếp)
- History Panel: Visual history state stack with one-click time travel
- Ctrl+S shortcut to save image as .dbp / .png / .jpg / .webp / .ico / .bmp
- Interactive Canvas with real layer composition and drawing support
- File -> Open (Ctrl+O) to load images or .dbp project files
- File -> Save (Ctrl+S) and Save As (Ctrl+Shift+S)
"""

import sys
import os
import io
import json
import zipfile
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QCheckBox, QToolButton,
    QScrollArea, QFrame, QTabBar, QTabWidget,
    QLineEdit, QListWidget, QListWidgetItem,
    QMenu, QColorDialog, QButtonGroup, QFileDialog, QMessageBox
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap, QIcon, QFont,
    QLinearGradient, QPolygonF, QPainterPath,
    QKeySequence, QImage, QAction
)
from PyQt6.QtCore import Qt, QSize, QPoint, QPointF, QRect, QRectF, pyqtSignal, QBuffer, QIODevice, QTimer


# ==============================================================================
# 1. COLOR THEME AND STYLESHEET (Photo Job DARK THEME)
# ==============================================================================

DARK_PALETTE = {
    "bg_darkest": "#1e1e1e",     # Canvas workspace background
    "bg_dark": "#282828",        # Sub-bars, tab bar background
    "bg_panel": "#333333",       # Main panels, options bar, menus
    "bg_hover": "#444444",       # Hover button background
    "bg_active": "#505050",      # Active/selected button background
    "bg_selected": "#264f78",    # Selected item in list (blue)
    "bg_input": "#222222",       # Input fields & combos
    "border_dark": "#181818",    # Dark division lines
    "border_light": "#3f3f3f",   # Subtle borders
    "text_primary": "#dcdcdc",   # Main text color
    "text_muted": "#888888",     # Muted labels
    "accent_blue": "#0d66d0",    # PS highlight blue
    "accent_cyan": "#36a3f7",    # Active tab marker / focus
    "icon_normal": "#b5b5b5",    # Tool icon color
    "icon_active": "#ffffff",    # Active tool icon color
}

PHOTOSHOP_QSS = f"""
QMainWindow {{
    background-color: {DARK_PALETTE["bg_panel"]};
}}

QWidget {{
    color: {DARK_PALETTE["text_primary"]};
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 11px;
}}

/* Toolbars & Options Bar */
QFrame#OptionsBar {{
    background-color: {DARK_PALETTE["bg_panel"]};
    border-bottom: 1px solid {DARK_PALETTE["border_dark"]};
}}

QFrame#ToolBarFrame {{
    background-color: {DARK_PALETTE["bg_panel"]};
    border-right: 1px solid {DARK_PALETTE["border_dark"]};
}}

QFrame#DockPanel {{
    background-color: {DARK_PALETTE["bg_panel"]};
    border-left: 1px solid {DARK_PALETTE["border_dark"]};
}}

/* Menu Bar */
QMenuBar {{
    background-color: {DARK_PALETTE["bg_panel"]};
    color: {DARK_PALETTE["text_primary"]};
    border-bottom: 1px solid {DARK_PALETTE["border_dark"]};
    padding: 1px 4px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 4px 7px;
    margin: 0px 1px;
    border-radius: 2px;
}}
QMenuBar::item:selected {{
    background-color: {DARK_PALETTE["bg_hover"]};
    color: #ffffff;
}}
QMenuBar::item:pressed {{
    background-color: {DARK_PALETTE["bg_active"]};
}}

/* Menus */
QMenu {{
    background-color: {DARK_PALETTE["bg_panel"]};
    color: {DARK_PALETTE["text_primary"]};
    border: 1px solid {DARK_PALETTE["border_dark"]};
    padding: 3px 0px;
}}
QMenu::item {{
    padding: 5px 24px 5px 20px;
}}
QMenu::item:selected {{
    background-color: {DARK_PALETTE["accent_blue"]};
    color: #ffffff;
}}
QMenu::separator {{
    height: 1px;
    background-color: {DARK_PALETTE["border_dark"]};
    margin: 3px 0px;
}}

/* Tool Buttons */
QToolButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 2px;
    padding: 1px;
    color: {DARK_PALETTE["icon_normal"]};
}}
QToolButton:hover {{
    background-color: {DARK_PALETTE["bg_hover"]};
    border: 1px solid {DARK_PALETTE["border_light"]};
}}
QToolButton:pressed, QToolButton:checked {{
    background-color: {DARK_PALETTE["bg_active"]};
    border: 1px solid {DARK_PALETTE["border_dark"]};
}}

/* Comboboxes */
QComboBox {{
    background-color: {DARK_PALETTE["bg_input"]};
    border: 1px solid {DARK_PALETTE["border_light"]};
    border-radius: 2px;
    color: {DARK_PALETTE["text_primary"]};
    padding: 1px 5px;
    font-size: 11px;
    min-height: 18px;
}}
QComboBox:hover {{
    border: 1px solid #5a5a5a;
}}
QComboBox::drop-down {{
    border: none;
    width: 14px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid {DARK_PALETTE["icon_normal"]};
    width: 0;
    height: 0;
    margin-right: 4px;
}}
QComboBox QAbstractItemView {{
    background-color: {DARK_PALETTE["bg_panel"]};
    border: 1px solid {DARK_PALETTE["border_dark"]};
    selection-background-color: {DARK_PALETTE["accent_blue"]};
    color: {DARK_PALETTE["text_primary"]};
    outline: none;
}}

/* Checkboxes */
QCheckBox {{
    color: {DARK_PALETTE["text_primary"]};
    spacing: 5px;
}}
QCheckBox::indicator {{
    width: 12px;
    height: 12px;
    border: 1px solid {DARK_PALETTE["border_light"]};
    border-radius: 2px;
    background-color: {DARK_PALETTE["bg_input"]};
}}
QCheckBox::indicator:hover {{
    border: 1px solid #555555;
}}
QCheckBox::indicator:checked {{
    background-color: {DARK_PALETTE["accent_blue"]};
    border: 1px solid {DARK_PALETTE["accent_blue"]};
}}

/* Line Edit */
QLineEdit {{
    background-color: {DARK_PALETTE["bg_input"]};
    border: 1px solid {DARK_PALETTE["border_light"]};
    border-radius: 2px;
    color: {DARK_PALETTE["text_primary"]};
    padding: 1px 4px;
    selection-background-color: {DARK_PALETTE["accent_blue"]};
}}
QLineEdit:focus {{
    border: 1px solid {DARK_PALETTE["accent_cyan"]};
}}

/* ScrollBars */
QScrollBar:vertical {{
    background: {DARK_PALETTE["bg_darkest"]};
    width: 13px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #424242;
    min-height: 24px;
    border-radius: 2px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: #505050;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {DARK_PALETTE["bg_darkest"]};
    height: 13px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: #424242;
    min-width: 24px;
    border-radius: 2px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #505050;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Tab Widget & Tab Bar */
QTabWidget::pane {{
    border: none;
    background-color: {DARK_PALETTE["bg_panel"]};
}}
QTabBar::tab {{
    background-color: {DARK_PALETTE["bg_panel"]};
    color: {DARK_PALETTE["text_muted"]};
    padding: 5px 10px;
    margin-right: 1px;
    border-top: 2px solid transparent;
    font-size: 11px;
}}
QTabBar::tab:selected {{
    color: #ffffff;
    background-color: {DARK_PALETTE["bg_panel"]};
    border-top: 2px solid {DARK_PALETTE["accent_cyan"]};
}}
QTabBar::tab:hover:!selected {{
    color: {DARK_PALETTE["text_primary"]};
    background-color: {DARK_PALETTE["bg_hover"]};
}}

/* Document Tab Bar */
QTabBar#DocumentTabBar::tab {{
    background-color: {DARK_PALETTE["bg_dark"]};
    color: {DARK_PALETTE["text_muted"]};
    padding: 5px 14px;
    border-right: 1px solid {DARK_PALETTE["border_dark"]};
    border-top: 2px solid transparent;
    font-size: 11px;
}}
QTabBar#DocumentTabBar::tab:selected {{
    background-color: {DARK_PALETTE["bg_panel"]};
    color: #ffffff;
    border-top: 2px solid {DARK_PALETTE["accent_blue"]};
}}

/* List / Tree Widgets for Layers */
QListWidget {{
    background-color: {DARK_PALETTE["bg_dark"]};
    border: 1px solid {DARK_PALETTE["border_dark"]};
    color: {DARK_PALETTE["text_primary"]};
    outline: none;
}}
QListWidget::item {{
    padding: 2px;
    border-bottom: 1px solid #282828;
}}
QListWidget::item:selected {{
    background-color: {DARK_PALETTE["bg_selected"]};
    color: #ffffff;
}}
QListWidget::item:hover:!selected {{
    background-color: #2c2c2c;
}}
"""


# ==============================================================================
# 2. VECTOR ICON FACTORY (CRISP PROCEDURAL VECTOR ICONS)
# ==============================================================================

class IconFactory:
    """Creates crisp vector QIcons matching Photoshop CC icons."""

    @staticmethod
    def create_icon(name: str, size: int = 24, color: str = DARK_PALETTE["icon_normal"], has_sub: bool = False) -> QIcon:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(color), 1.3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        w, h = float(size), float(size)
        cx, cy = w / 2.0, h / 2.0

        if name == "move":
            painter.drawLine(QPointF(cx, 4), QPointF(cx, h - 4))
            painter.drawLine(QPointF(4, cy), QPointF(w - 4, cy))
            painter.drawLine(QPointF(cx - 2.5, 6.5), QPointF(cx, 4))
            painter.drawLine(QPointF(cx + 2.5, 6.5), QPointF(cx, 4))
            painter.drawLine(QPointF(cx - 2.5, h - 6.5), QPointF(cx, h - 4))
            painter.drawLine(QPointF(cx + 2.5, h - 6.5), QPointF(cx, h - 4))
            painter.drawLine(QPointF(6.5, cy - 2.5), QPointF(4, cy))
            painter.drawLine(QPointF(6.5, cy + 2.5), QPointF(4, cy))
            painter.drawLine(QPointF(w - 6.5, cy - 2.5), QPointF(w - 4, cy))
            painter.drawLine(QPointF(w - 6.5, cy + 2.5), QPointF(w - 4, cy))

        elif name == "marquee":
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern([3, 2])
            painter.setPen(pen)
            painter.drawRect(QRectF(4.5, 4.5, w - 9, h - 9))

        elif name == "lasso":
            path = QPainterPath()
            path.moveTo(6, 17)
            path.cubicTo(4, 8, 12, 4, 18, 7)
            path.cubicTo(21, 10, 18, 18, 13, 17)
            path.cubicTo(9, 16, 8, 20, 6, 20)
            painter.drawPath(path)

        elif name == "quick_select":
            painter.drawLine(QPointF(5, h - 5), QPointF(14, 10))
            painter.setPen(QPen(QColor(color), 2.2))
            painter.drawPoint(QPointF(14, 10))
            pen.setWidthF(1.0)
            painter.setPen(pen)
            painter.drawLine(QPointF(18, 3), QPointF(18, 7))
            painter.drawLine(QPointF(16, 5), QPointF(20, 5))
            painter.drawLine(QPointF(9, 3), QPointF(9, 5))
            painter.drawLine(QPointF(8, 4), QPointF(10, 4))

        elif name == "crop":
            painter.drawPolyline([QPointF(7, 4), QPointF(7, 17), QPointF(20, 17)])
            painter.drawPolyline([QPointF(4, 7), QPointF(17, 7), QPointF(17, 20)])

        elif name == "frame":
            painter.drawRect(QRectF(4.5, 4.5, w - 9, h - 9))
            painter.drawLine(QPointF(5, 5), QPointF(w - 5, h - 5))
            painter.drawLine(QPointF(w - 5, 5), QPointF(5, h - 5))

        elif name == "eyedropper":
            path = QPainterPath()
            path.moveTo(17, 5)
            path.lineTo(19, 7)
            path.lineTo(12, 14)
            path.lineTo(8, 16)
            path.lineTo(10, 12)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(QPointF(8, 16), QPointF(5, 19))

        elif name == "healing_brush":
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(-45)
            painter.drawRoundedRect(QRectF(-8, -4, 16, 8), 4, 4)
            painter.drawPoint(QPointF(-2, 0))
            painter.drawPoint(QPointF(2, 0))
            painter.restore()

        elif name == "brush":
            path = QPainterPath()
            path.moveTo(18, 4)
            path.lineTo(14, 8)
            path.lineTo(11, 13)
            path.cubicTo(8, 15, 6, 18, 5, 20)
            path.cubicTo(7, 19, 10, 17, 12, 14)
            path.lineTo(16, 11)
            path.lineTo(20, 6)
            path.closeSubpath()
            painter.drawPath(path)

        elif name == "stamp":
            painter.drawRoundedRect(QRectF(9, 4, 6, 7), 2, 2)
            painter.drawLine(QPointF(6, 13), QPointF(18, 13))
            painter.drawRect(QRectF(4.5, 15.5, 15, 4))

        elif name == "history_brush":
            painter.drawLine(QPointF(13, 8), QPointF(8, 19))
            painter.drawArc(QRectF(4, 4, 12, 12), 45 * 16, 220 * 16)
            painter.drawLine(QPointF(4, 7), QPointF(4, 10))
            painter.drawLine(QPointF(4, 7), QPointF(7, 7))

        elif name == "eraser":
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(-30)
            painter.drawRect(QRectF(-8, -5, 16, 10))
            painter.drawLine(QPointF(-1, -5), QPointF(-1, 5))
            painter.restore()

        elif name == "bucket":
            path = QPainterPath()
            path.moveTo(10, 5)
            path.lineTo(18, 11)
            path.lineTo(14, 17)
            path.lineTo(6, 11)
            path.closeSubpath()
            painter.drawPath(path)
            painter.setBrush(QBrush(QColor(color)))
            drop = QPainterPath()
            drop.moveTo(18, 16)
            drop.cubicTo(16, 18, 16, 20, 18, 20)
            drop.cubicTo(20, 20, 20, 18, 18, 16)
            painter.drawPath(drop)
            painter.setBrush(Qt.BrushStyle.NoBrush)

        elif name == "blur":
            path = QPainterPath()
            path.moveTo(cx, 4)
            path.cubicTo(cx - 6, 12, cx - 6, 18, cx, 19)
            path.cubicTo(cx + 6, 18, cx + 6, 12, cx, 4)
            painter.drawPath(path)

        elif name == "dodge":
            painter.drawEllipse(QRectF(6, 4, 12, 12))
            painter.drawLine(QPointF(cx, 16), QPointF(cx, 21))

        elif name == "pen":
            path = QPainterPath()
            path.moveTo(cx, 4)
            path.lineTo(18, 13)
            path.lineTo(15, 19)
            path.lineTo(9, 19)
            path.lineTo(6, 13)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(QPointF(cx, 4), QPointF(cx, 12))
            painter.drawPoint(QPointF(cx, 12))

        elif name == "type":
            painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "T")

        elif name == "path_select":
            path = QPainterPath()
            path.moveTo(6, 5)
            path.lineTo(17, 12)
            path.lineTo(12, 13)
            path.lineTo(15, 19)
            path.lineTo(13, 20)
            path.lineTo(10, 14)
            path.lineTo(6, 17)
            path.closeSubpath()
            painter.setBrush(QBrush(QColor(color)))
            painter.drawPath(path)
            painter.setBrush(Qt.BrushStyle.NoBrush)

        elif name == "shape":
            painter.drawRect(QRectF(5.5, 6.5, w - 11, h - 13))

        elif name == "hand":
            path = QPainterPath()
            path.moveTo(8, 19)
            path.lineTo(8, 12)
            path.lineTo(10, 7)
            path.lineTo(12, 10)
            path.lineTo(13, 6)
            path.lineTo(15, 9)
            path.lineTo(16, 8)
            path.lineTo(18, 11)
            path.lineTo(18, 16)
            path.cubicTo(18, 20, 10, 20, 8, 19)
            painter.drawPath(path)

        elif name == "zoom":
            painter.drawEllipse(QRectF(5, 5, 10, 10))
            painter.drawLine(QPointF(13, 13), QPointF(19, 19))
            painter.drawLine(QPointF(7.5, 10), QPointF(12.5, 10))
            painter.drawLine(QPointF(10, 7.5), QPointF(10, 12.5))

        elif name == "dots":
            painter.setBrush(QBrush(QColor(color)))
            painter.drawEllipse(QRectF(6, 11, 2.5, 2.5))
            painter.drawEllipse(QRectF(11, 11, 2.5, 2.5))
            painter.drawEllipse(QRectF(16, 11, 2.5, 2.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)

        elif name == "quick_mask":
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(QRectF(4.5, 4.5, 15, 15))
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawEllipse(QRectF(7.5, 7.5, 9, 9))
            painter.setBrush(Qt.BrushStyle.NoBrush)

        elif name == "screen_mode":
            painter.drawRect(QRectF(4.5, 5.5, 15, 13))
            painter.drawRect(QRectF(7.5, 8.5, 9, 7))

        elif name == "home":
            path = QPainterPath()
            path.moveTo(cx, 4)
            path.lineTo(18, 11)
            path.lineTo(16, 11)
            path.lineTo(16, 19)
            path.lineTo(8, 19)
            path.lineTo(8, 11)
            path.lineTo(6, 11)
            path.closeSubpath()
            painter.drawPath(path)

        elif name.startswith("align_"):
            sub = name.replace("align_", "")
            if sub == "top":
                painter.drawLine(QPointF(4, 4), QPointF(20, 4))
                painter.drawRect(QRectF(6, 6, 4, 10))
                painter.drawRect(QRectF(14, 6, 4, 14))
            elif sub == "v_center":
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.drawLine(QPointF(4, cy), QPointF(20, cy))
                pen.setStyle(Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.drawRect(QRectF(6, 6, 4, 12))
                painter.drawRect(QRectF(14, 8, 4, 8))
            elif sub == "bottom":
                painter.drawLine(QPointF(4, 20), QPointF(20, 20))
                painter.drawRect(QRectF(6, 8, 4, 10))
                painter.drawRect(QRectF(14, 4, 4, 14))
            elif sub == "left":
                painter.drawLine(QPointF(4, 4), QPointF(4, 20))
                painter.drawRect(QRectF(6, 6, 10, 4))
                painter.drawRect(QRectF(6, 14, 14, 4))
            elif sub == "h_center":
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.drawLine(QPointF(cx, 4), QPointF(cx, 20))
                pen.setStyle(Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.drawRect(QRectF(6, 6, 12, 4))
                painter.drawRect(QRectF(8, 14, 8, 4))
            elif sub == "right":
                painter.drawLine(QPointF(20, 4), QPointF(20, 20))
                painter.drawRect(QRectF(8, 6, 10, 4))
                painter.drawRect(QRectF(4, 14, 14, 4))

        elif name.startswith("dist_"):
            sub = name.replace("dist_", "")
            if sub == "h":
                painter.drawRect(QRectF(4, 6, 3, 12))
                painter.drawRect(QRectF(10.5, 6, 3, 12))
                painter.drawRect(QRectF(17, 6, 3, 12))
            else:
                painter.drawRect(QRectF(6, 4, 12, 3))
                painter.drawRect(QRectF(6, 10.5, 12, 3))
                painter.drawRect(QRectF(6, 17, 12, 3))

        elif name.startswith("3d_"):
            painter.drawRect(QRectF(6, 6, 12, 12))
            painter.drawLine(QPointF(6, 6), QPointF(10, 3))
            painter.drawLine(QPointF(18, 6), QPointF(22, 3))
            painter.drawLine(QPointF(10, 3), QPointF(22, 3))
            painter.drawLine(QPointF(22, 3), QPointF(22, 15))
            painter.drawLine(QPointF(18, 18), QPointF(22, 15))

        elif name == "link":
            painter.drawRoundedRect(QRectF(5, 7, 7, 10), 3, 3)
            painter.drawRoundedRect(QRectF(12, 7, 7, 10), 3, 3)

        elif name == "fx":
            painter.setFont(QFont("Georgia", 11, QFont.Weight.Bold))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "fx")

        elif name == "layer_mask":
            painter.drawRect(QRectF(4.5, 5.5, 15, 13))
            painter.setBrush(QBrush(QColor(color)))
            painter.drawEllipse(QRectF(9, 9, 6, 6))
            painter.setBrush(Qt.BrushStyle.NoBrush)

        elif name == "adj_layer":
            painter.drawEllipse(QRectF(5.5, 5.5, 13, 13))
            painter.setBrush(QBrush(QColor(color)))
            painter.drawPie(QRectF(5.5, 5.5, 13, 13), -90 * 16, 180 * 16)
            painter.setBrush(Qt.BrushStyle.NoBrush)

        elif name == "folder":
            path = QPainterPath()
            path.moveTo(4, 7)
            path.lineTo(9, 7)
            path.lineTo(11, 9)
            path.lineTo(20, 9)
            path.lineTo(20, 19)
            path.lineTo(4, 19)
            path.closeSubpath()
            painter.drawPath(path)

        elif name == "new_layer":
            path = QPainterPath()
            path.moveTo(6, 4)
            path.lineTo(14, 4)
            path.lineTo(18, 8)
            path.lineTo(18, 20)
            path.lineTo(6, 20)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(QPointF(12, 13), QPointF(12, 17))
            painter.drawLine(QPointF(10, 15), QPointF(14, 15))

        elif name == "trash":
            painter.drawLine(QPointF(5, 7), QPointF(19, 7))
            painter.drawLine(QPointF(9, 5), QPointF(15, 5))
            painter.drawRect(QRectF(7, 7, 10, 13))
            painter.drawLine(QPointF(10, 9), QPointF(10, 17))
            painter.drawLine(QPointF(14, 9), QPointF(14, 17))

        elif name == "eye":
            path = QPainterPath()
            path.moveTo(4, cy)
            path.cubicTo(8, 7, 16, 7, 20, cy)
            path.cubicTo(16, 17, 8, 17, 4, cy)
            painter.drawPath(path)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawEllipse(QRectF(10, cy - 2, 4, 4))
            painter.setBrush(Qt.BrushStyle.NoBrush)

        elif name == "lock":
            painter.drawRoundedRect(QRectF(6.5, 10, 11, 9), 1.5, 1.5)
            painter.drawArc(QRectF(8, 5, 8, 8), 0, 180 * 16)

        elif name == "menu_hamburger":
            painter.drawLine(QPointF(4, 7), QPointF(16, 7))
            painter.drawLine(QPointF(4, 11), QPointF(16, 11))
            painter.drawLine(QPointF(4, 15), QPointF(16, 15))

        elif name == "search":
            painter.drawEllipse(QRectF(5, 5, 9, 9))
            painter.drawLine(QPointF(12, 12), QPointF(17, 17))

        elif name == "workspace":
            painter.drawRect(QRectF(4, 4, 14, 14))
            painter.drawLine(QPointF(13, 4), QPointF(13, 18))

        elif name == "share":
            painter.drawRect(QRectF(4, 6, 12, 12))
            painter.drawLine(QPointF(10, 10), QPointF(18, 2))
            painter.drawLine(QPointF(13, 2), QPointF(18, 2))
            painter.drawLine(QPointF(18, 2), QPointF(18, 7))

        # Tiny corner arrow if tool has submenu flyout (Photoshop standard)
        if has_sub:
            sub_poly = QPolygonF([
                QPointF(w - 2, h - 2),
                QPointF(w - 6, h - 2),
                QPointF(w - 2, h - 6)
            ])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawPolygon(sub_poly)

        painter.end()
        return QIcon(pixmap)


# ==============================================================================
# 3. INTERACTIVE COLOR PICKER & SWATCH WIDGETS
# ==============================================================================

class ColorGradientWidget(QWidget):
    """2D Saturation/Value gradient box matching Photoshop's Color Panel."""
    color_changed = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(145, 115)
        self.hue = 0.0          # Hue in [0, 360]
        self.sat = 0.8          # Saturation in [0, 1]
        self.val = 0.9          # Value in [0, 1]
        self.setCursor(Qt.CursorShape.CrossCursor)

    def set_hue(self, hue: float):
        self.hue = max(0.0, min(360.0, hue))
        self.update()
        self._emit_current_color()

    def _emit_current_color(self):
        c = QColor.fromHsvF(self.hue / 360.0, self.sat, self.val)
        self.color_changed.emit(c)

    def mousePressEvent(self, event):
        self._handle_mouse(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._handle_mouse(event.pos())

    def _handle_mouse(self, pos: QPoint):
        w = max(1, self.width())
        h = max(1, self.height())
        self.sat = max(0.0, min(1.0, pos.x() / w))
        self.val = max(0.0, min(1.0, 1.0 - (pos.y() / h)))
        self.update()
        self._emit_current_color()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()

        # Horizontal gradient: White -> Pure Hue Color
        base_color = QColor.fromHsvF(self.hue / 360.0, 1.0, 1.0)
        h_grad = QLinearGradient(0, 0, w, 0)
        h_grad.setColorAt(0.0, QColor(255, 255, 255))
        h_grad.setColorAt(1.0, base_color)
        painter.fillRect(0, 0, w, h, h_grad)

        # Vertical gradient: Transparent -> Black
        v_grad = QLinearGradient(0, 0, 0, h)
        v_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        v_grad.setColorAt(1.0, QColor(0, 0, 0, 255))
        painter.fillRect(0, 0, w, h, v_grad)

        # Draw circle selector
        sel_x = int(self.sat * w)
        sel_y = int((1.0 - self.val) * h)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(255, 255, 255), 1.5))
        painter.drawEllipse(QPoint(sel_x, sel_y), 5, 5)
        painter.setPen(QPen(QColor(0, 0, 0), 1.0))
        painter.drawEllipse(QPoint(sel_x, sel_y), 4, 4)


class HueBarWidget(QWidget):
    """Vertical rainbow Hue slider matching Photoshop CC with pointer arrows."""
    hue_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 115)
        self.hue = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        self._handle_mouse(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._handle_mouse(event.pos())

    def _handle_mouse(self, pos: QPoint):
        h = max(1, self.height())
        frac = max(0.0, min(1.0, pos.y() / h))
        self.hue = frac * 360.0
        self.update()
        self.hue_changed.emit(self.hue)

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()

        bar_x = 3
        bar_w = 12

        # Rainbow spectrum
        grad = QLinearGradient(0, 0, 0, h)
        stops = [0.0, 0.16, 0.33, 0.5, 0.67, 0.83, 1.0]
        hues = [0, 60, 120, 180, 240, 300, 360]
        for s, hu in zip(stops, hues):
            grad.setColorAt(s, QColor.fromHsv(hu % 360, 255, 255))

        painter.fillRect(bar_x, 0, bar_w, h, grad)
        painter.setPen(QPen(QColor(20, 20, 20), 1))
        painter.drawRect(bar_x, 0, bar_w - 1, h - 1)

        # Dual triangular pointers pointing into the hue bar
        y_pos = int((self.hue / 360.0) * h)
        y_pos = max(2, min(h - 3, y_pos))

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(0, 0, 0), 1))

        # Left arrow
        left_tri = QPolygonF([
            QPointF(0, y_pos - 3),
            QPointF(bar_x, y_pos),
            QPointF(0, y_pos + 3)
        ])
        painter.drawPolygon(left_tri)

        # Right arrow
        right_tri = QPolygonF([
            QPointF(w - 1, y_pos - 3),
            QPointF(bar_x + bar_w, y_pos),
            QPointF(w - 1, y_pos + 3)
        ])
        painter.drawPolygon(right_tri)


class ForegroundBackgroundWidget(QWidget):
    """Photoshop's iconic overlapping Foreground/Background color swatches."""
    color_selected = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.fg_color = QColor(0, 0, 0)
        self.bg_color = QColor(255, 255, 255)

    def set_foreground(self, color: QColor):
        self.fg_color = color
        self.update()
        self.color_selected.emit(self.fg_color)

    def swap_colors(self):
        self.fg_color, self.bg_color = self.bg_color, self.fg_color
        self.update()
        self.color_selected.emit(self.fg_color)

    def reset_colors(self):
        self.fg_color = QColor(0, 0, 0)
        self.bg_color = QColor(255, 255, 255)
        self.update()
        self.color_selected.emit(self.fg_color)

    def mousePressEvent(self, event):
        pos = event.pos()
        if pos.x() > 22 and pos.y() < 14:
            self.swap_colors()
            return
        if pos.x() < 14 and pos.y() > 22:
            self.reset_colors()
            return
        cd = QColorDialog(self.fg_color, self)
        if cd.exec():
            self.set_foreground(cd.selectedColor())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background square (lower right: 12, 12, 18, 18)
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.setBrush(QBrush(self.bg_color))
        painter.drawRect(12, 12, 18, 18)

        # Foreground square (upper left: 4, 4, 18, 18)
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.setBrush(QBrush(self.fg_color))
        painter.drawRect(4, 4, 18, 18)

        # Swap arrow (curved icon at top right)
        painter.setPen(QPen(QColor(160, 160, 160), 1))
        painter.drawLine(25, 4, 30, 4)
        painter.drawLine(30, 4, 30, 9)
        painter.drawLine(30, 4, 28, 2)
        painter.drawLine(30, 4, 32, 2)

        # Reset small D icon at bottom left
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawRect(2, 24, 6, 6)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(5, 27, 6, 6)


# ==============================================================================
# 4. PHOTOSHOP TOOLBAR (LEFT VERTICAL STRIP)
# ==============================================================================

class PhotoshopToolBar(QFrame):
    """The vertical left-hand tool palette with all Photoshop CC tools."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ToolBarFrame")
        self.setFixedWidth(36)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 4, 2, 4)
        layout.setSpacing(1)

        # Collapse / Expand header button (>>)
        self.btn_expand = QToolButton(self)
        self.btn_expand.setText("»")
        self.btn_expand.setFixedSize(30, 18)
        self.btn_expand.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {DARK_PALETTE['text_muted']}; border: none;"
        )
        layout.addWidget(self.btn_expand, 0, Qt.AlignmentFlag.AlignCenter)

        # Tool definitions matching the screenshot
        tools = [
            ("move", "Move Tool (V)", True),
            ("marquee", "Rectangular Marquee Tool (M)", True),
            ("lasso", "Lasso Tool (L)", True),
            ("quick_select", "Object Selection Tool (W)", True),
            ("crop", "Crop Tool (C)", True),
            ("frame", "Frame Tool (K)", False),
            ("eyedropper", "Eyedropper Tool (I)", True),
            ("healing_brush", "Spot Healing Brush Tool (J)", True),
            ("brush", "Brush Tool (B)", True),
            ("stamp", "Clone Stamp Tool (S)", True),
            ("history_brush", "History Brush Tool (Y)", True),
            ("eraser", "Eraser Tool (E)", True),
            ("bucket", "Gradient Tool (G)", True),
            ("blur", "Blur Tool", True),
            ("dodge", "Dodge Tool (O)", True),
            ("pen", "Pen Tool (P)", True),
            ("type", "Horizontal Type Tool (T)", True),
            ("path_select", "Path Selection Tool (A)", True),
            ("shape", "Rectangle Tool (U)", True),
            ("hand", "Hand Tool (H)", True),
            ("zoom", "Zoom Tool (Z)", True),
            ("dots", "Edit Toolbar (...)", False),
        ]

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        for name, tip, has_sub in tools:
            btn = QToolButton(self)
            btn.setCheckable(True)
            btn.setFixedSize(30, 24)
            btn.setIcon(IconFactory.create_icon(name, 20, DARK_PALETTE["icon_normal"], has_sub))
            btn.setIconSize(QSize(18, 18))
            btn.setToolTip(tip)

            if name == "move":
                btn.setChecked(True)

            self.btn_group.addButton(btn)
            layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(4)

        # Color picker swatches
        self.color_swatch = ForegroundBackgroundWidget(self)
        layout.addWidget(self.color_swatch, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(3)

        # Quick mask & screen mode buttons
        btn_mask = QToolButton(self)
        btn_mask.setFixedSize(30, 20)
        btn_mask.setIcon(IconFactory.create_icon("quick_mask", 16, DARK_PALETTE["icon_normal"]))
        btn_mask.setToolTip("Edit in Quick Mask Mode (Q)")
        layout.addWidget(btn_mask, 0, Qt.AlignmentFlag.AlignCenter)

        btn_screen = QToolButton(self)
        btn_screen.setFixedSize(30, 20)
        btn_screen.setIcon(IconFactory.create_icon("screen_mode", 16, DARK_PALETTE["icon_normal"]))
        btn_screen.setToolTip("Change Screen Mode (F)")
        layout.addWidget(btn_screen, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()


# ==============================================================================
# 5. OPTIONS BAR (HORIZONTAL BAR UNDER MENU)
# ==============================================================================

class PhotoshopOptionsBar(QFrame):
    """The horizontal options bar adjusting contextually to the active tool."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OptionsBar")
        self.setFixedHeight(30)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 1, 6, 1)
        layout.setSpacing(6)

        # Photoshop home button
        btn_home = QToolButton(self)
        btn_home.setIcon(IconFactory.create_icon("home", 18, DARK_PALETTE["icon_normal"]))
        btn_home.setFixedSize(22, 22)
        btn_home.setToolTip("Home")
        layout.addWidget(btn_home)

        # Active Tool Icon (Move Tool)
        tool_icon = QLabel(self)
        tool_icon.setPixmap(IconFactory.create_icon("move", 16, DARK_PALETTE["text_primary"]).pixmap(16, 16))
        layout.addWidget(tool_icon)

        # Auto-Select Checkbox & ComboBox
        self.cb_auto = QCheckBox("Auto-Select:", self)
        self.cb_auto.setChecked(True)
        layout.addWidget(self.cb_auto)

        self.combo_target = QComboBox(self)
        self.combo_target.addItems(["Layer", "Group"])
        self.combo_target.setFixedWidth(66)
        layout.addWidget(self.combo_target)

        layout.addSpacing(4)

        # Show Transform Controls Checkbox
        self.cb_transform = QCheckBox("Show Transform Controls", self)
        layout.addWidget(self.cb_transform)

        layout.addWidget(self._make_separator())

        # Alignment Buttons
        align_tools = [
            ("align_top", "Align Top Edges"),
            ("align_v_center", "Align Vertical Centers"),
            ("align_bottom", "Align Bottom Edges"),
            ("align_left", "Align Left Edges"),
            ("align_h_center", "Align Horizontal Centers"),
            ("align_right", "Align Right Edges"),
        ]
        for name, tip in align_tools:
            btn = QToolButton(self)
            btn.setIcon(IconFactory.create_icon(name, 16, DARK_PALETTE["icon_normal"]))
            btn.setFixedSize(20, 20)
            btn.setToolTip(tip)
            layout.addWidget(btn)

        # Distribute Buttons
        dist_tools = [
            ("dist_h", "Distribute Horizontally"),
            ("dist_v", "Distribute Vertically"),
        ]
        for name, tip in dist_tools:
            btn = QToolButton(self)
            btn.setIcon(IconFactory.create_icon(name, 16, DARK_PALETTE["icon_normal"]))
            btn.setFixedSize(20, 20)
            btn.setToolTip(tip)
            layout.addWidget(btn)

        layout.addWidget(self._make_separator())

        # More options button (...)
        btn_more = QToolButton(self)
        btn_more.setText("...")
        btn_more.setFixedSize(22, 20)
        btn_more.setStyleSheet("font-weight: bold;")
        layout.addWidget(btn_more)

        # 3D Mode Section
        lbl_3d = QLabel("3D Mode:", self)
        lbl_3d.setStyleSheet(f"color: {DARK_PALETTE['text_muted']}; font-size: 10px; margin-left: 4px;")
        layout.addWidget(lbl_3d)

        for i in range(5):
            btn_3d = QToolButton(self)
            btn_3d.setIcon(IconFactory.create_icon("3d_mode", 15, DARK_PALETTE["text_muted"]))
            btn_3d.setFixedSize(18, 18)
            layout.addWidget(btn_3d)

        layout.addStretch()

    def _make_separator(self):
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"color: {DARK_PALETTE['border_light']};")
        line.setFixedHeight(16)
        return line


# ==============================================================================
# 6. CENTRAL CANVAS WORKSPACE & DOCUMENT MODEL
# ==============================================================================

class PhotoshopCanvas(QWidget):
    """The document canvas simulating Photoshop's 2100 x 1500 px document with live layers & drawing."""
    canvas_updated = pyqtSignal()
    history_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc_width = 2100
        self.doc_height = 1500
        self.dpi = 300
        self.zoom = 0.70  # 70% zoom matching the screenshot

        # Real layers storage
        self.layers = []
        bg_image = QImage(self.doc_width, self.doc_height, QImage.Format.Format_ARGB32_Premultiplied)
        bg_image.fill(QColor(255, 255, 255))
        self.layers.append({
            "id": "layer_bg",
            "name": "Background",
            "visible": True,
            "opacity": 1.0,
            "locked": True,
            "blend_mode": "Normal",
            "image": bg_image
        })

        self.active_layer_idx = 0
        self.brush_color = QColor(0, 0, 0)
        self.brush_size = 10
        self.is_drawing = False
        self.last_doc_point = None

        # History / Undo-Redo system (Ctrl+Z)
        self.undo_stack = []
        self.redo_stack = []
        self.current_action_name = "New Document"
        self.max_undo_steps = 30
        self._batch_history_update = False

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(800, 500)
        self.setStyleSheet(f"background-color: {DARK_PALETTE['bg_darkest']};")

    def _create_snapshot(self, action_name: str) -> dict:
        layers_copy = []
        for lyr in self.layers:
            layers_copy.append({
                "id": lyr.get("id", ""),
                "name": lyr.get("name", "Layer"),
                "visible": lyr.get("visible", True),
                "opacity": lyr.get("opacity", 1.0),
                "locked": lyr.get("locked", False),
                "blend_mode": lyr.get("blend_mode", "Normal"),
                "image": lyr["image"].copy()
            })
        return {
            "name": action_name,
            "doc_width": self.doc_width,
            "doc_height": self.doc_height,
            "dpi": self.dpi,
            "active_layer_idx": self.active_layer_idx,
            "layers": layers_copy
        }

    def _restore_snapshot(self, snap: dict):
        self.doc_width = snap["doc_width"]
        self.doc_height = snap["doc_height"]
        self.dpi = snap["dpi"]
        self.active_layer_idx = snap["active_layer_idx"]
        restored = []
        for lyr in snap["layers"]:
            restored.append({
                "id": lyr["id"],
                "name": lyr["name"],
                "visible": lyr["visible"],
                "opacity": lyr["opacity"],
                "locked": lyr["locked"],
                "blend_mode": lyr["blend_mode"],
                "image": lyr["image"].copy()
            })
        self.layers = restored
        self.update()
        self.canvas_updated.emit()

    def save_undo_state(self, action_name: str):
        """Saves current state to undo stack before making a change."""
        snap = self._create_snapshot(self.current_action_name)
        self.undo_stack.append(snap)
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.current_action_name = action_name
        if not self._batch_history_update:
            self.history_changed.emit()

    def undo(self, emit_signal: bool = True) -> tuple[bool, str]:
        """Undo step (Ctrl+Z): reverts to previous document state."""
        if not self.undo_stack:
            return False, ""
        self.is_drawing = False
        self.last_doc_point = None
        curr = self._create_snapshot(self.current_action_name)
        self.redo_stack.append(curr)
        prev = self.undo_stack.pop()
        undone_action = self.current_action_name
        self._restore_snapshot(prev)
        self.current_action_name = prev.get("name", "Step")
        if emit_signal and not self._batch_history_update:
            self.history_changed.emit()
        return True, undone_action

    def redo(self, emit_signal: bool = True) -> tuple[bool, str]:
        """Redo step (Ctrl+Shift+Z / Ctrl+Y): re-applies undone document state."""
        if not self.redo_stack:
            return False, ""
        self.is_drawing = False
        self.last_doc_point = None
        curr = self._create_snapshot(self.current_action_name)
        self.undo_stack.append(curr)
        nxt = self.redo_stack.pop()
        redone_action = nxt.get("name", "Step")
        self._restore_snapshot(nxt)
        self.current_action_name = redone_action
        if emit_signal and not self._batch_history_update:
            self.history_changed.emit()
        return True, redone_action

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def get_undo_name(self) -> str:
        return self.current_action_name if self.can_undo() else ""

    def get_redo_name(self) -> str:
        if self.can_redo():
            return self.redo_stack[-1].get("name", "Step")
        return ""

    def reset_history(self, initial_name: str = "New Document"):
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_action_name = initial_name
        self.history_changed.emit()

    def get_history_list(self) -> list[tuple[str, str]]:
        def get_icon(name: str) -> str:
            n = name.lower()
            if "brush" in n:
                return "brush"
            elif "layer" in n:
                if "delete" in n:
                    return "trash"
                elif "visib" in n:
                    return "eye"
                return "new_layer"
            elif "open" in n or "document" in n or "new" in n:
                return "home"
            return "history_brush"

        items = []
        for s in self.undo_stack:
            name = s.get("name", "Step")
            items.append((name, get_icon(name)))
        items.append((self.current_action_name, get_icon(self.current_action_name)))
        for s in reversed(self.redo_stack):
            name = s.get("name", "Step")
            items.append((name, get_icon(name)))
        return items

    def get_current_history_index(self) -> int:
        return len(self.undo_stack)

    def jump_to_history_index(self, target_idx: int):
        curr_idx = len(self.undo_stack)
        if target_idx == curr_idx:
            return
        self._batch_history_update = True
        try:
            if target_idx < curr_idx:
                for _ in range(curr_idx - target_idx):
                    self.undo(emit_signal=False)
            elif target_idx > curr_idx:
                for _ in range(target_idx - curr_idx):
                    self.redo(emit_signal=False)
        finally:
            self._batch_history_update = False
            self.history_changed.emit()
            self.canvas_updated.emit()

    def set_brush_color(self, color: QColor):
        self.brush_color = color

    def get_composite_image(self) -> QImage:
        """Composites all visible layers into a single high-res QImage."""
        comp = QImage(self.doc_width, self.doc_height, QImage.Format.Format_ARGB32_Premultiplied)
        comp.fill(QColor(0, 0, 0, 0))

        painter = QPainter(comp)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Render from bottom to top
        for layer in reversed(self.layers):
            if layer.get("visible", True):
                opacity = float(layer.get("opacity", 1.0))
                painter.setOpacity(opacity)
                painter.drawImage(0, 0, layer["image"])

        painter.end()
        return comp

    def get_pil_image(self) -> Image.Image:
        """Converts the composited document into a PIL RGBA Image."""
        comp = self.get_composite_image()
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.ReadWrite)
        comp.save(buf, "PNG")
        data = bytes(buf.data())
        buf.close()
        return Image.open(io.BytesIO(data)).convert("RGBA")

    def load_from_pil(self, pil_img: Image.Image):
        """Loads a PIL image into the canvas, adjusting document size."""
        self.doc_width, self.doc_height = pil_img.size
        # Convert PIL Image to QImage
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        qimg = QImage.fromData(buf.getvalue(), "PNG").convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)

        self.layers = [{
            "id": "layer_0",
            "name": "Background",
            "visible": True,
            "opacity": 1.0,
            "locked": True,
            "blend_mode": "Normal",
            "image": qimg
        }]
        self.active_layer_idx = 0
        self.reset_history("Open Image")
        self.update()
        self.canvas_updated.emit()

    def _get_canvas_viewport_rect(self) -> QRect:
        vw, vh = self.width(), self.height()
        margin = 18
        max_cw = max(10, vw - (margin * 2))
        max_ch = max(10, vh - (margin * 2))
        ratio = max(0.01, self.doc_width / max(1, self.doc_height))

        cw = max_cw
        ch = int(cw / ratio)
        if ch > max_ch:
            ch = max_ch
            cw = int(ch * ratio)

        cx = (vw - cw) // 2
        cy = (vh - ch) // 2
        return QRect(cx, cy, cw, ch)

    def _view_to_doc(self, pt: QPoint):
        r = self._get_canvas_viewport_rect()
        if r.contains(pt):
            doc_x = int((pt.x() - r.x()) * self.doc_width / r.width())
            doc_y = int((pt.y() - r.y()) * self.doc_height / r.height())
            return QPoint(doc_x, doc_y)
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            doc_pt = self._view_to_doc(event.position().toPoint())
            if doc_pt:
                self.save_undo_state("Brush Tool")
                self.is_drawing = True
                self.last_doc_point = doc_pt
                self._draw_stroke(doc_pt, doc_pt)

    def mouseMoveEvent(self, event):
        if self.is_drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            doc_pt = self._view_to_doc(event.position().toPoint())
            if doc_pt and self.last_doc_point:
                self._draw_stroke(self.last_doc_point, doc_pt)
                self.last_doc_point = doc_pt

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = False
            self.last_doc_point = None
            self.canvas_updated.emit()

    def _draw_stroke(self, p1: QPoint, p2: QPoint):
        if 0 <= self.active_layer_idx < len(self.layers):
            layer = self.layers[self.active_layer_idx]
            p = QPainter(layer["image"])
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.drawLine(p1, p2)
            p.end()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        canvas_rect = self._get_canvas_viewport_rect()

        # Draw dark canvas drop shadow
        shadow_rect = QRect(canvas_rect.x() + 1, canvas_rect.y() + 1, canvas_rect.width() + 2, canvas_rect.height() + 2)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 180))

        # Composite and render document
        composite = self.get_composite_image()
        painter.drawImage(canvas_rect, composite)

        # 1px border around sheet
        painter.setPen(QPen(QColor(10, 10, 10), 1))
        painter.drawRect(canvas_rect)


class DocumentWorkspace(QWidget):
    """Combines document tabs, scrollable canvas, and bottom status bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Document tab bar at top
        tab_bar_frame = QFrame(self)
        tab_bar_frame.setFixedHeight(26)
        tab_bar_frame.setStyleSheet(
            f"background-color: {DARK_PALETTE['bg_dark']}; border-bottom: 1px solid {DARK_PALETTE['border_dark']};"
        )
        tb_layout = QHBoxLayout(tab_bar_frame)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(0)

        self.tab_bar = QTabBar(tab_bar_frame)
        self.tab_bar.setObjectName("DocumentTabBar")
        self.tab_bar.addTab("Untitled-1 @ 70% (RGB/8)  ✕")
        self.tab_bar.setCurrentIndex(0)
        tb_layout.addWidget(self.tab_bar)
        tb_layout.addStretch()

        layout.addWidget(tab_bar_frame)

        # Center scroll area containing the canvas
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.canvas = PhotoshopCanvas(self)
        self.scroll_area.setWidget(self.canvas)
        layout.addWidget(self.scroll_area, 1)

        # Bottom status bar matching Photoshop CC
        status_frame = QFrame(self)
        status_frame.setFixedHeight(22)
        status_frame.setStyleSheet(
            f"background-color: {DARK_PALETTE['bg_panel']}; border-top: 1px solid {DARK_PALETTE['border_dark']};"
        )
        st_layout = QHBoxLayout(status_frame)
        st_layout.setContentsMargins(6, 0, 6, 0)
        st_layout.setSpacing(8)

        # Zoom level edit: "70%"
        self.zoom_edit = QLineEdit("70%", status_frame)
        self.zoom_edit.setFixedWidth(44)
        self.zoom_edit.setFixedHeight(18)
        self.zoom_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_edit.setStyleSheet(
            f"background-color: {DARK_PALETTE['bg_input']}; border: 1px solid {DARK_PALETTE['border_light']}; font-size: 10px;"
        )
        st_layout.addWidget(self.zoom_edit)

        # Document dimensions & resolution label
        self.lbl_info = QLabel("2100 px x 1500 px (300 ppi)  ▾", status_frame)
        self.lbl_info.setStyleSheet(f"color: {DARK_PALETTE['text_primary']}; font-size: 10px;")
        st_layout.addWidget(self.lbl_info)

        # Status text for save / status confirmations
        self.lbl_status = QLabel("Press Ctrl+S to save (.dbp, .png, .jpg, .webp, .ico)", status_frame)
        self.lbl_status.setStyleSheet("color: #79c0ff; font-size: 10px; margin-left: 12px;")
        st_layout.addWidget(self.lbl_status)

        st_layout.addStretch()
        layout.addWidget(status_frame)

    def set_document_name(self, name: str):
        self.tab_bar.setTabText(0, f"{name} @ 70% (RGB/8)  ✕")
        self.lbl_info.setText(f"{self.canvas.doc_width} px x {self.canvas.doc_height} px ({self.canvas.dpi} ppi)  ▾")

    def show_status_message(self, text: str, timeout_ms: int = 4000):
        self.lbl_status.setText(text)
        if timeout_ms > 0:
            QTimer.singleShot(timeout_ms, lambda: self.lbl_status.setText("Press Ctrl+S to save (.dbp, .png, .jpg, .webp, .ico)"))


# ==============================================================================
# 7. RIGHT SIDEBAR DOCK PANELS (COLOR, SWATCHES, LAYERS, CHANNELS)
# ==============================================================================

class ColorPanel(QWidget):
    """Upper panel: Color / Swatches / Gradients / Patterns."""
    color_selected = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        picker_row = QHBoxLayout()
        picker_row.setSpacing(6)

        # Swatch preview
        swatch_col = QVBoxLayout()
        self.color_chip = QFrame(self)
        self.color_chip.setFixedSize(20, 20)
        self.color_chip.setStyleSheet("background-color: #000000; border: 1px solid #555555;")
        swatch_col.addWidget(self.color_chip)
        swatch_col.addStretch()
        picker_row.addLayout(swatch_col)

        # 2D gradient box
        self.grad_box = ColorGradientWidget(self)
        picker_row.addWidget(self.grad_box)

        # Vertical rainbow hue bar
        self.hue_bar = HueBarWidget(self)
        picker_row.addWidget(self.hue_bar)

        self.hue_bar.hue_changed.connect(self.grad_box.set_hue)
        self.grad_box.color_changed.connect(self._on_color_picked)

        layout.addLayout(picker_row)
        layout.addStretch()

    def _on_color_picked(self, color: QColor):
        self.color_chip.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #555555;")
        self.color_selected.emit(color)


class LayersPanel(QWidget):
    """Lower panel: Layers / Channels / Paths matching Photoshop exactly."""
    layer_action_triggered = pyqtSignal()

    def __init__(self, parent=None, canvas: PhotoshopCanvas = None):
        super().__init__(parent)
        self.canvas = canvas
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        # Filter bar: Kind combo + 5 layer type filter buttons
        filter_row = QHBoxLayout()
        filter_row.setSpacing(3)

        combo_filter = QComboBox(self)
        combo_filter.addItems(["Kind", "Name", "Effect", "Mode", "Attribute", "Color"])
        combo_filter.setFixedWidth(64)
        filter_row.addWidget(combo_filter)

        filter_icons = ["brush", "adj_layer", "type", "shape", "frame"]
        for ic in filter_icons:
            btn = QToolButton(self)
            btn.setIcon(IconFactory.create_icon(ic, 16, DARK_PALETTE["text_muted"]))
            btn.setFixedSize(19, 19)
            filter_row.addWidget(btn)

        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Blending mode and Opacity row
        blend_row = QHBoxLayout()
        blend_row.setSpacing(4)

        self.combo_blend = QComboBox(self)
        self.combo_blend.addItems([
            "Normal", "Dissolve", "Darken", "Multiply", "Color Burn", "Linear Burn",
            "Lighten", "Screen", "Color Dodge", "Overlay", "Soft Light", "Hard Light",
            "Difference", "Exclusion", "Hue", "Saturation", "Color", "Luminosity"
        ])
        self.combo_blend.setFixedWidth(95)
        blend_row.addWidget(self.combo_blend)

        blend_row.addStretch()

        lbl_opacity = QLabel("Opacity:", self)
        lbl_opacity.setStyleSheet(f"color: {DARK_PALETTE['text_muted']}; font-size: 10px;")
        blend_row.addWidget(lbl_opacity)

        self.combo_opacity = QComboBox(self)
        self.combo_opacity.addItems(["100%", "75%", "50%", "25%", "0%"])
        self.combo_opacity.setFixedWidth(54)
        blend_row.addWidget(self.combo_opacity)

        layout.addLayout(blend_row)

        # Lock and Fill row
        lock_row = QHBoxLayout()
        lock_row.setSpacing(2)

        lbl_lock = QLabel("Lock:", self)
        lbl_lock.setStyleSheet(f"color: {DARK_PALETTE['text_muted']}; font-size: 10px; margin-right: 2px;")
        lock_row.addWidget(lbl_lock)

        lock_icons = ["marquee", "brush", "move", "frame", "lock"]
        for ic in lock_icons:
            btn = QToolButton(self)
            btn.setIcon(IconFactory.create_icon(ic, 14, DARK_PALETTE["text_muted"]))
            btn.setFixedSize(17, 17)
            lock_row.addWidget(btn)

        lock_row.addStretch()

        lbl_fill = QLabel("Fill:", self)
        lbl_fill.setStyleSheet(f"color: {DARK_PALETTE['text_muted']}; font-size: 10px;")
        lock_row.addWidget(lbl_fill)

        self.combo_fill = QComboBox(self)
        self.combo_fill.addItems(["100%", "75%", "50%", "25%", "0%"])
        self.combo_fill.setFixedWidth(54)
        lock_row.addWidget(self.combo_fill)

        layout.addLayout(lock_row)

        # Layers List View
        self.layer_list = QListWidget(self)
        self.layer_list.setStyleSheet(
            f"background-color: {DARK_PALETTE['bg_dark']}; border: 1px solid {DARK_PALETTE['border_dark']};"
        )
        self.layer_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.layer_list.currentRowChanged.connect(self._on_layer_row_changed)
        layout.addWidget(self.layer_list, 1)

        # Bottom layer actions bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(1)

        actions = [
            ("link", "Link Layers"),
            ("fx", "Add a Layer Style"),
            ("layer_mask", "Add Layer Mask"),
            ("adj_layer", "Create New Fill or Adjustment Layer"),
            ("folder", "Create a New Group"),
            ("new_layer", "Create New Layer"),
            ("trash", "Delete Layer"),
        ]

        for ic_name, tip in actions:
            btn = QToolButton(self)
            btn.setIcon(IconFactory.create_icon(ic_name, 17, DARK_PALETTE["icon_normal"]))
            btn.setFixedSize(22, 20)
            btn.setToolTip(tip)
            if ic_name == "new_layer":
                btn.clicked.connect(self._create_new_layer)
            elif ic_name == "trash":
                btn.clicked.connect(self._delete_selected_layer)
            bottom_bar.addWidget(btn)

        layout.addLayout(bottom_bar)

        self.rebuild_layer_list()

    def rebuild_layer_list(self):
        self.layer_list.clear()
        if not self.canvas:
            return

        for i, lyr in enumerate(self.canvas.layers):
            item = QListWidgetItem(self.layer_list)
            item.setSizeHint(QSize(220, 34))

            widget = QWidget()
            row = QHBoxLayout(widget)
            row.setContentsMargins(3, 2, 6, 2)
            row.setSpacing(6)

            # Eye icon (toggle visibility)
            btn_eye = QToolButton()
            btn_eye.setIcon(IconFactory.create_icon("eye", 15, DARK_PALETTE["text_primary"] if lyr.get("visible", True) else DARK_PALETTE["text_muted"]))
            btn_eye.setFixedSize(18, 18)
            btn_eye.clicked.connect(lambda checked, idx=i, b=btn_eye: self._toggle_visibility(idx, b))
            row.addWidget(btn_eye)

            # Thumbnail preview
            thumb = QLabel()
            thumb.setFixedSize(32, 22)
            thumb.setStyleSheet(f"background-color: {'#ffffff' if lyr.get('name') == 'Background' else '#383838'}; border: 1px solid #1a1a1a;")
            row.addWidget(thumb)

            # Name label
            name_lbl = QLabel(lyr.get("name", "Layer"))
            if lyr.get("name") == "Background":
                name_lbl.setStyleSheet("font-style: italic; color: #ffffff;")
            else:
                name_lbl.setStyleSheet("color: #ffffff;")
            row.addWidget(name_lbl)

            row.addStretch()

            # Lock icon badge
            if lyr.get("locked", False):
                lock_lbl = QLabel()
                lock_lbl.setPixmap(IconFactory.create_icon("lock", 13, DARK_PALETTE["text_muted"]).pixmap(13, 13))
                row.addWidget(lock_lbl)

            self.layer_list.setItemWidget(item, widget)

        if 0 <= self.canvas.active_layer_idx < len(self.canvas.layers):
            self.layer_list.setCurrentRow(self.canvas.active_layer_idx)
        else:
            self.layer_list.setCurrentRow(0)

    def _toggle_visibility(self, layer_idx: int, btn_eye: QToolButton):
        if self.canvas and 0 <= layer_idx < len(self.canvas.layers):
            self.canvas.save_undo_state("Layer Visibility")
            curr = self.canvas.layers[layer_idx].get("visible", True)
            self.canvas.layers[layer_idx]["visible"] = not curr
            btn_eye.setIcon(IconFactory.create_icon("eye", 15, DARK_PALETTE["text_primary"] if not curr else DARK_PALETTE["text_muted"]))
            self.canvas.update()
            self.canvas.canvas_updated.emit()

    def _on_layer_row_changed(self, row: int):
        if self.canvas and 0 <= row < len(self.canvas.layers):
            self.canvas.active_layer_idx = row

    def _create_new_layer(self):
        if not self.canvas:
            return
        self.canvas.save_undo_state("New Layer")
        idx = len(self.canvas.layers)
        new_img = QImage(self.canvas.doc_width, self.canvas.doc_height, QImage.Format.Format_ARGB32_Premultiplied)
        new_img.fill(QColor(0, 0, 0, 0))

        self.canvas.layers.insert(0, {
            "id": f"layer_{idx}",
            "name": f"Layer {idx}",
            "visible": True,
            "opacity": 1.0,
            "locked": False,
            "blend_mode": "Normal",
            "image": new_img
        })
        self.canvas.active_layer_idx = 0
        self.rebuild_layer_list()
        self.canvas.update()
        self.canvas.canvas_updated.emit()

    def _delete_selected_layer(self):
        if not self.canvas or len(self.canvas.layers) <= 1:
            return
        row = self.layer_list.currentRow()
        if 0 <= row < len(self.canvas.layers):
            self.canvas.save_undo_state("Delete Layer")
            del self.canvas.layers[row]
            self.canvas.active_layer_idx = min(row, len(self.canvas.layers) - 1)
            self.rebuild_layer_list()
            self.canvas.update()
            self.canvas.canvas_updated.emit()


class HistoryPanel(QWidget):
    """Lower panel: History state list matching Photoshop CC with interactive undo/redo navigation."""
    def __init__(self, parent=None, canvas: PhotoshopCanvas = None):
        super().__init__(parent)
        self.canvas = canvas
        self._updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        self.history_list = QListWidget(self)
        self.history_list.setStyleSheet(
            f"background-color: {DARK_PALETTE['bg_dark']}; border: 1px solid {DARK_PALETTE['border_dark']};"
        )
        self.history_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.history_list.currentRowChanged.connect(self._on_row_clicked)
        layout.addWidget(self.history_list, 1)

        # Bottom hint & action bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(4)

        lbl_hint = QLabel("Ctrl+Z: Undo | Ctrl+Shift+Z: Redo", self)
        lbl_hint.setStyleSheet(f"color: {DARK_PALETTE['text_muted']}; font-size: 10px;")
        bottom_bar.addWidget(lbl_hint)
        bottom_bar.addStretch()

        btn_undo = QToolButton(self)
        btn_undo.setIcon(IconFactory.create_icon("history_brush", 15, DARK_PALETTE["icon_normal"]))
        btn_undo.setFixedSize(22, 20)
        btn_undo.setToolTip("Step Backward (Ctrl+Z)")
        btn_undo.clicked.connect(lambda: self.canvas.undo() if self.canvas else None)
        bottom_bar.addWidget(btn_undo)

        btn_trash = QToolButton(self)
        btn_trash.setIcon(IconFactory.create_icon("trash", 15, DARK_PALETTE["icon_normal"]))
        btn_trash.setFixedSize(22, 20)
        btn_trash.setToolTip("Delete State (Undo)")
        btn_trash.clicked.connect(lambda: self.canvas.undo() if self.canvas else None)
        bottom_bar.addWidget(btn_trash)

        layout.addLayout(bottom_bar)
        self.rebuild_history_list()

    def rebuild_history_list(self):
        if not self.canvas:
            return
        self._updating = True
        self.history_list.clear()

        states = self.canvas.get_history_list()
        current_idx = self.canvas.get_current_history_index()

        for idx, (name, icon_name) in enumerate(states):
            item = QListWidgetItem(self.history_list)
            item.setSizeHint(QSize(200, 26))

            is_current = (idx == current_idx)
            is_undone = (idx > current_idx)

            color = DARK_PALETTE["accent_cyan"] if is_current else (
                DARK_PALETTE["text_muted"] if is_undone else DARK_PALETTE["icon_normal"]
            )
            item.setIcon(IconFactory.create_icon(icon_name, 15, color))
            item.setText(f"  {name}")

            if is_current:
                item.setForeground(QBrush(QColor(DARK_PALETTE["accent_cyan"])))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            elif is_undone:
                item.setForeground(QBrush(QColor(DARK_PALETTE["text_muted"])))
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
            else:
                item.setForeground(QBrush(QColor(DARK_PALETTE["text_primary"])))

        if 0 <= current_idx < self.history_list.count():
            self.history_list.setCurrentRow(current_idx)
        self._updating = False

    def _on_row_clicked(self, row: int):
        if self._updating or not self.canvas or row < 0:
            return
        self.canvas.jump_to_history_index(row)


class PhotoshopDockPanels(QFrame):
    """The entire right sidebar dock with Collapsed strip, Color, and Layers panels."""

    def __init__(self, parent=None, canvas: PhotoshopCanvas = None):
        super().__init__(parent)
        self.canvas = canvas
        self.setObjectName("DockPanel")
        self.setFixedWidth(280)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Leftmost narrow icon strip for collapsed panels (History, etc.)
        strip = QFrame(self)
        strip.setFixedWidth(24)
        strip.setStyleSheet(
            f"background-color: {DARK_PALETTE['bg_panel']}; border-right: 1px solid {DARK_PALETTE['border_dark']};"
        )
        strip_layout = QVBoxLayout(strip)
        strip_layout.setContentsMargins(1, 3, 1, 3)
        strip_layout.setSpacing(3)

        btn_collapse = QToolButton(strip)
        btn_collapse.setText("«")
        btn_collapse.setFixedSize(20, 16)
        btn_collapse.setStyleSheet("font-size: 12px; font-weight: bold; border: none;")
        strip_layout.addWidget(btn_collapse, 0, Qt.AlignmentFlag.AlignCenter)

        btn_hist = QToolButton(strip)
        btn_hist.setIcon(IconFactory.create_icon("history_brush", 15, DARK_PALETTE["icon_normal"]))
        btn_hist.setFixedSize(20, 20)
        btn_hist.setToolTip("History")
        strip_layout.addWidget(btn_hist, 0, Qt.AlignmentFlag.AlignCenter)

        btn_prop = QToolButton(strip)
        btn_prop.setIcon(IconFactory.create_icon("frame", 15, DARK_PALETTE["icon_normal"]))
        btn_prop.setFixedSize(20, 20)
        btn_prop.setToolTip("Properties")
        strip_layout.addWidget(btn_prop, 0, Qt.AlignmentFlag.AlignCenter)

        strip_layout.addStretch()
        main_layout.addWidget(strip)

        # Vertical panels container
        panels_container = QWidget(self)
        pc_layout = QVBoxLayout(panels_container)
        pc_layout.setContentsMargins(0, 0, 0, 0)
        pc_layout.setSpacing(0)

        # Upper tab widget: Color, Swatches, Gradients, Patterns
        self.top_tabs = QTabWidget(panels_container)
        self.color_panel = ColorPanel(self)
        self.top_tabs.addTab(self.color_panel, "Color")
        self.top_tabs.addTab(QWidget(), "Swatches")
        self.top_tabs.addTab(QWidget(), "Gradients")
        self.top_tabs.addTab(QWidget(), "Patterns")
        self.top_tabs.setFixedHeight(175)

        top_menu_btn = QToolButton(self.top_tabs)
        top_menu_btn.setIcon(IconFactory.create_icon("menu_hamburger", 16, DARK_PALETTE["icon_normal"]))
        top_menu_btn.setFixedSize(20, 20)
        self.top_tabs.setCornerWidget(top_menu_btn, Qt.Corner.TopRightCorner)

        pc_layout.addWidget(self.top_tabs)

        # Divider line
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {DARK_PALETTE['border_dark']};")
        div.setFixedHeight(2)
        pc_layout.addWidget(div)

        # Lower tab widget: Layers, History, Channels, Paths
        self.bottom_tabs = QTabWidget(panels_container)
        self.layers_panel = LayersPanel(self, canvas)
        self.history_panel = HistoryPanel(self, canvas)
        self.bottom_tabs.addTab(self.layers_panel, "Layers")
        self.bottom_tabs.addTab(self.history_panel, "History")
        self.bottom_tabs.addTab(QWidget(), "Channels")
        self.bottom_tabs.addTab(QWidget(), "Paths")

        bot_menu_btn = QToolButton(self.bottom_tabs)
        bot_menu_btn.setIcon(IconFactory.create_icon("menu_hamburger", 16, DARK_PALETTE["icon_normal"]))
        bot_menu_btn.setFixedSize(20, 20)
        self.bottom_tabs.setCornerWidget(bot_menu_btn, Qt.Corner.TopRightCorner)

        pc_layout.addWidget(self.bottom_tabs, 1)

        main_layout.addWidget(panels_container, 1)

        # Connect strip buttons & canvas signals
        btn_hist.clicked.connect(lambda: self.bottom_tabs.setCurrentWidget(self.history_panel))
        if canvas:
            canvas.history_changed.connect(self.history_panel.rebuild_history_list)
            canvas.history_changed.connect(self.layers_panel.rebuild_layer_list)


# ==============================================================================
# 8. MAIN WINDOW & FILE SAVE ENGINE (.dbp / .png / .jpg / .webp / .ico / .bmp)
# ==============================================================================

class PhotoshopMainWindow(QMainWindow):
    """The complete Photo Job main window application with Ctrl+S export functionality."""

    def __init__(self):
        super().__init__()
        self.doc_name = "Untitled-1"
        self.current_file_path = None

        self.setWindowTitle("Photo Job")
        self.resize(1280, 720)

        # Set window icon (Ps logo)
        self.setWindowIcon(self._create_ps_app_icon())

        # Apply dark theme styling
        self.setStyleSheet(PHOTOSHOP_QSS)

        # Central widget layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_vbox = QVBoxLayout(central_widget)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        # Tool Options Bar (Horizontal)
        self.options_bar = PhotoshopOptionsBar(self)
        main_vbox.addWidget(self.options_bar)

        # Body layout: Toolbar (left) + Workspace (center) + Dock Panels (right)
        body_hbox = QHBoxLayout()
        body_hbox.setContentsMargins(0, 0, 0, 0)
        body_hbox.setSpacing(0)

        # Left Toolbar
        self.toolbar = PhotoshopToolBar(self)
        body_hbox.addWidget(self.toolbar)

        # Center Workspace (Canvas + Document Tabs + Status)
        self.workspace = DocumentWorkspace(self)
        body_hbox.addWidget(self.workspace, 1)

        # Right Dock Panels (Color, Swatches, Layers)
        self.dock_panels = PhotoshopDockPanels(self, self.workspace.canvas)
        body_hbox.addWidget(self.dock_panels)

        main_vbox.addLayout(body_hbox, 1)

        # Create Top Menu Bar & Shortcuts (Ctrl+S, Ctrl+O, etc.)
        self._create_menu_bar()

        # Connect toolbar swatches & color panel
        self.toolbar.color_swatch.color_selected.connect(self._on_color_changed)
        self.dock_panels.color_panel.color_selected.connect(self._on_color_changed)
        self.workspace.canvas.history_changed.connect(self._update_undo_redo_actions)
        self._update_undo_redo_actions()

    def _create_ps_app_icon(self) -> QIcon:
        pm = QPixmap(32, 32)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(0, 30, 54)))
        p.setPen(QPen(QColor(49, 168, 255), 1.5))
        p.drawRoundedRect(QRectF(1, 1, 30, 30), 4, 4)
        p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        p.setPen(QPen(QColor(49, 168, 255)))
        p.drawText(QRectF(1, 1, 30, 30), Qt.AlignmentFlag.AlignCenter, "Ps")
        p.end()
        return QIcon(pm)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        menu_items = [
            "File", "Edit", "Image", "Layer", "Type",
            "Select", "Filter", "3D", "View", "Window", "Help"
        ]

        menus = {}
        for title in menu_items:
            menu = menu_bar.addMenu(title)
            menus[title] = menu

        # Populate File menu with shortcuts
        f_menu = menus["File"]

        act_new = f_menu.addAction("New...")
        act_new.setShortcut(QKeySequence.StandardKey.New)
        act_new.triggered.connect(self.action_new)
        self.addAction(act_new)

        act_open = f_menu.addAction("Open...")
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self.action_open)
        self.addAction(act_open)

        f_menu.addAction("Open Recent")
        f_menu.addSeparator()

        f_menu.addAction("Close").setShortcut(QKeySequence.StandardKey.Close)
        f_menu.addAction("Close All")
        f_menu.addSeparator()

        # SAVE (Ctrl+S)
        self.act_save = f_menu.addAction("Save")
        self.act_save.setShortcut(QKeySequence("Ctrl+S"))
        self.act_save.triggered.connect(self.action_save)
        self.addAction(self.act_save)

        # SAVE AS (Ctrl+Shift+S)
        self.act_save_as = f_menu.addAction("Save As...")
        self.act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.act_save_as.triggered.connect(self.action_save_as)
        self.addAction(self.act_save_as)

        act_export = f_menu.addAction("Export As...")
        act_export.triggered.connect(self.action_save_as)

        f_menu.addSeparator()
        f_menu.addAction("Exit", self.close).setShortcut(QKeySequence.StandardKey.Quit)

        # Populate Edit menu with Ctrl+Z Undo / Redo
        e_menu = menus["Edit"]
        self.act_undo = e_menu.addAction("Undo")
        self.act_undo.setShortcuts([QKeySequence("Ctrl+Z"), QKeySequence("Ctrl+Alt+Z")])
        self.act_undo.triggered.connect(self.action_undo)
        self.addAction(self.act_undo)

        self.act_redo = e_menu.addAction("Redo")
        self.act_redo.setShortcuts([QKeySequence("Ctrl+Shift+Z"), QKeySequence("Ctrl+Y")])
        self.act_redo.triggered.connect(self.action_redo)
        self.addAction(self.act_redo)
        e_menu.addSeparator()
        e_menu.addAction("Cut").setShortcut(QKeySequence.StandardKey.Cut)
        e_menu.addAction("Copy").setShortcut(QKeySequence.StandardKey.Copy)
        e_menu.addAction("Paste").setShortcut(QKeySequence.StandardKey.Paste)
        e_menu.addSeparator()
        e_menu.addAction("Free Transform").setShortcut(QKeySequence("Ctrl+T"))
        e_menu.addAction("Preferences")

        for key in ["Image", "Layer", "Type", "Select", "Filter", "3D", "View", "Window", "Help"]:
            menus[key].addAction(f"{key} Options...")

        # Right side corner widget on Menu Bar
        corner_widget = QWidget(menu_bar)
        cw_layout = QHBoxLayout(corner_widget)
        cw_layout.setContentsMargins(0, 0, 8, 0)
        cw_layout.setSpacing(6)

        btn_search = QToolButton(corner_widget)
        btn_search.setIcon(IconFactory.create_icon("search", 16, DARK_PALETTE["icon_normal"]))
        btn_search.setFixedSize(22, 22)
        btn_search.setToolTip("Search")
        cw_layout.addWidget(btn_search)

        btn_workspace = QToolButton(corner_widget)
        btn_workspace.setIcon(IconFactory.create_icon("workspace", 16, DARK_PALETTE["icon_normal"]))
        btn_workspace.setFixedSize(22, 22)
        btn_workspace.setToolTip("Workspace Layout")
        cw_layout.addWidget(btn_workspace)

        btn_share = QToolButton(corner_widget)
        btn_share.setIcon(IconFactory.create_icon("share", 16, DARK_PALETTE["icon_normal"]))
        btn_share.setFixedSize(22, 22)
        btn_share.setToolTip("Share an image")
        cw_layout.addWidget(btn_share)

        menu_bar.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)

    def _on_color_changed(self, color: QColor):
        self.toolbar.color_swatch.set_foreground(color)
        self.dock_panels.color_panel.color_chip.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #555555;")
        self.workspace.canvas.set_brush_color(color)

    # --------------------------------------------------------------------------
    # UNDO / REDO & EDIT LOGIC (Ctrl+Z / Ctrl+Shift+Z)
    # --------------------------------------------------------------------------

    def action_undo(self):
        """Undo last step (Ctrl+Z / Ctrl+Alt+Z)."""
        success, action_name = self.workspace.canvas.undo()
        if success:
            self.workspace.show_status_message(f"↩ Undo: {action_name} (Ctrl+Z)")
        else:
            self.workspace.show_status_message("Nothing to undo")

    def action_redo(self):
        """Redo next step (Ctrl+Shift+Z / Ctrl+Y)."""
        success, action_name = self.workspace.canvas.redo()
        if success:
            self.workspace.show_status_message(f"↪ Redo: {action_name} (Ctrl+Shift+Z)")
        else:
            self.workspace.show_status_message("Nothing to redo")

    def _update_undo_redo_actions(self):
        """Updates Edit menu texts and enabled state based on history."""
        canvas = self.workspace.canvas
        if canvas.can_undo():
            self.act_undo.setEnabled(True)
            self.act_undo.setText(f"Undo {canvas.get_undo_name()}\tCtrl+Z")
        else:
            self.act_undo.setEnabled(False)
            self.act_undo.setText("Undo\tCtrl+Z")

        if canvas.can_redo():
            self.act_redo.setEnabled(True)
            self.act_redo.setText(f"Redo {canvas.get_redo_name()}\tCtrl+Shift+Z")
        else:
            self.act_redo.setEnabled(False)
            self.act_redo.setText("Redo\tCtrl+Shift+Z")

    def keyPressEvent(self, event):
        """Window-level fallback shortcut handler for Ctrl+Z, Ctrl+Shift+Z, Ctrl+Y."""
        modifiers = event.modifiers()
        key = event.key()

        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_Z:
                self.action_undo()
                event.accept()
                return
            elif key == Qt.Key.Key_Y:
                self.action_redo()
                event.accept()
                return
        elif modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            if key == Qt.Key.Key_Z:
                self.action_redo()
                event.accept()
                return

        super().keyPressEvent(event)

    # --------------------------------------------------------------------------
    # SAVE & EXPORT LOGIC (.dbp / .png / .jpg / .webp / .ico / .bmp)
    # --------------------------------------------------------------------------

    def action_new(self):
        """Creates a fresh document."""
        self.doc_name = "Untitled-1"
        self.current_file_path = None
        self.workspace.canvas.doc_width = 2100
        self.workspace.canvas.doc_height = 1500
        bg_image = QImage(2100, 1500, QImage.Format.Format_ARGB32_Premultiplied)
        bg_image.fill(QColor(255, 255, 255))
        self.workspace.canvas.layers = [{
            "id": "layer_bg",
            "name": "Background",
            "visible": True,
            "opacity": 1.0,
            "locked": True,
            "blend_mode": "Normal",
            "image": bg_image
        }]
        self.workspace.canvas.active_layer_idx = 0
        self.workspace.canvas.reset_history("New Document")
        self.dock_panels.layers_panel.rebuild_layer_list()
        self.workspace.set_document_name("Untitled-1")
        self.setWindowTitle("Photo Job")
        self.workspace.canvas.update()
        self.workspace.show_status_message("Created new document: 2100 x 1500 px")

    def action_open(self):
        """Opens an image (.png, .jpg, .webp, .ico, .bmp) or .dbp project."""
        file_filter = (
            "All Supported Files (*.dbp *.png *.jpg *.jpeg *.webp *.ico *.bmp);;"
            "DBP Project (*.dbp);;"
            "PNG Image (*.png);;"
            "JPEG Image (*.jpg *.jpeg);;"
            "WebP Image (*.webp);;"
            "ICO Icon (*.ico);;"
            "BMP Image (*.bmp);;"
            "All Files (*.*)"
        )
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Document", "", file_filter)
        if not file_path:
            return

        try:
            filename = os.path.basename(file_path)
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".dbp":
                self._load_dbp_project(file_path)
            else:
                pil_img = Image.open(file_path).convert("RGBA")
                self.workspace.canvas.load_from_pil(pil_img)

            self.current_file_path = file_path
            self.doc_name = os.path.splitext(filename)[0]
            self.workspace.canvas.reset_history(f"Open: {filename}")
            self.workspace.set_document_name(filename)
            self.setWindowTitle(f"{filename} - Photo Job")
            self.dock_panels.layers_panel.rebuild_layer_list()
            self.workspace.show_status_message(f"✓ Opened: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Open Error", f"Could not open file:\n{str(e)}")

    def action_save(self):
        """Ctrl+S handler: Saves directly if file exists, otherwise prompts Save As."""
        if self.current_file_path:
            self.save_to_path(self.current_file_path)
        else:
            self.action_save_as()

    def action_save_as(self):
        """Prompts the user to save as .dbp / .png / .jpg / .webp / .ico."""
        file_filter = (
            "DBP Project (*.dbp);;"
            "PNG Image (*.png);;"
            "JPEG Image (*.jpg *.jpeg);;"
            "WebP Image (*.webp);;"
            "ICO Icon (*.ico);;"
            "BMP Image (*.bmp);;"
            "All Supported Files (*.dbp *.png *.jpg *.jpeg *.webp *.ico *.bmp);;"
            "All Files (*.*)"
        )

        default_name = f"{self.doc_name}.png"
        chosen_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Document (Ctrl+S)",
            default_name,
            file_filter
        )

        if not chosen_path:
            return

        final_path = self._normalize_save_path(chosen_path, selected_filter)
        self.save_to_path(final_path)

    def _normalize_save_path(self, path: str, selected_filter: str) -> str:
        """Appends appropriate extension if user omitted it in the save dialog."""
        root, ext = os.path.splitext(path)
        if not ext:
            if "*.dbp" in selected_filter:
                return root + ".dbp"
            elif "*.png" in selected_filter:
                return root + ".png"
            elif "*.jpg" in selected_filter or "*.jpeg" in selected_filter:
                return root + ".jpg"
            elif "*.webp" in selected_filter:
                return root + ".webp"
            elif "*.ico" in selected_filter:
                return root + ".ico"
            elif "*.bmp" in selected_filter:
                return root + ".bmp"
            else:
                return root + ".png"
        return path

    def save_to_path(self, file_path: str) -> bool:
        """Saves current document into .dbp, .png, .jpg, .webp, .ico, or .bmp."""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            composite_pil = self.workspace.canvas.get_pil_image()

            if ext == ".dbp":
                self._save_dbp_project(file_path, composite_pil)

            elif ext == ".png":
                composite_pil.save(file_path, format="PNG")

            elif ext in (".jpg", ".jpeg"):
                # Flatten alpha onto solid white background for clean JPEG output
                if composite_pil.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", composite_pil.size, (255, 255, 255))
                    bg.paste(composite_pil, mask=composite_pil.split()[-1])
                    bg.save(file_path, format="JPEG", quality=95)
                else:
                    composite_pil.convert("RGB").save(file_path, format="JPEG", quality=95)

            elif ext == ".webp":
                composite_pil.save(file_path, format="WEBP", quality=95)

            elif ext == ".ico":
                # Windows Icon export
                if composite_pil.width == composite_pil.height:
                    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
                    composite_pil.save(file_path, format="ICO", sizes=sizes)
                else:
                    composite_pil.save(file_path, format="ICO")

            elif ext == ".bmp":
                if composite_pil.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", composite_pil.size, (255, 255, 255))
                    bg.paste(composite_pil, mask=composite_pil.split()[-1])
                    bg.save(file_path, format="BMP")
                else:
                    composite_pil.convert("RGB").save(file_path, format="BMP")

            else:
                composite_pil.save(file_path)

            self.current_file_path = file_path
            filename = os.path.basename(file_path)
            self.doc_name = os.path.splitext(filename)[0]

            self.workspace.set_document_name(filename)
            self.setWindowTitle(f"{filename} - Photo Job")
            self.workspace.show_status_message(f"✓ Saved successfully: {filename}")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{str(e)}")
            return False

    def _save_dbp_project(self, file_path: str, composite_pil: Image.Image):
        """Packages the document, layers, and metadata into a .dbp ZIP project file."""
        with zipfile.ZipFile(file_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # 1. Composite flat image
            comp_buf = io.BytesIO()
            composite_pil.save(comp_buf, format="PNG")
            zf.writestr("composite.png", comp_buf.getvalue())

            # 2. Preview thumbnail
            thumb = composite_pil.copy()
            thumb.thumbnail((256, 256))
            thumb_buf = io.BytesIO()
            thumb.save(thumb_buf, format="PNG")
            zf.writestr("preview.png", thumb_buf.getvalue())

            # 3. Layer images and manifest
            layers_info = []
            for i, lyr in enumerate(self.workspace.canvas.layers):
                l_img = lyr["image"]
                buf = QBuffer()
                buf.open(QIODevice.OpenModeFlag.ReadWrite)
                l_img.save(buf, "PNG")
                layer_filename = f"layers/layer_{i}.png"
                zf.writestr(layer_filename, bytes(buf.data()))
                buf.close()

                layers_info.append({
                    "id": lyr.get("id", f"layer_{i}"),
                    "name": lyr.get("name", f"Layer {i}"),
                    "visible": lyr.get("visible", True),
                    "opacity": lyr.get("opacity", 1.0),
                    "locked": lyr.get("locked", False),
                    "blend_mode": lyr.get("blend_mode", "Normal"),
                    "file": layer_filename
                })

            manifest = {
                "format": "PhotoJob_DBP",
                "version": "1.0",
                "width": self.workspace.canvas.doc_width,
                "height": self.workspace.canvas.doc_height,
                "dpi": self.workspace.canvas.dpi,
                "layers": layers_info
            }
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    def _load_dbp_project(self, file_path: str):
        """Unpackages and loads a .dbp project file."""
        with zipfile.ZipFile(file_path, "r") as zf:
            manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            self.workspace.canvas.doc_width = manifest.get("width", 2100)
            self.workspace.canvas.doc_height = manifest.get("height", 1500)
            self.workspace.canvas.dpi = manifest.get("dpi", 300)

            new_layers = []
            for l_info in manifest.get("layers", []):
                img_data = zf.read(l_info["file"])
                qimg = QImage.fromData(img_data, "PNG").convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
                new_layers.append({
                    "id": l_info.get("id"),
                    "name": l_info.get("name", "Layer"),
                    "visible": l_info.get("visible", True),
                    "opacity": l_info.get("opacity", 1.0),
                    "locked": l_info.get("locked", False),
                    "blend_mode": l_info.get("blend_mode", "Normal"),
                    "image": qimg
                })

            self.workspace.canvas.layers = new_layers
            self.workspace.canvas.active_layer_idx = 0
            self.workspace.canvas.reset_history(f"Open: {os.path.basename(file_path)}")
            self.workspace.canvas.update()


# ==============================================================================
# 9. ENTRY POINT
# ==============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = PhotoshopMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
=======
import tkinter as tk
BG = "#0f172a"
MIN_SIZE = (760, 460)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Giao diện toàn màn hình")
        self.configure(bg=BG)
        self.minsize(*MIN_SIZE)
        self.is_fullscreen = True
        #self.withdraw()
if __name__ == "__main__":
    App().mainloop()
>>>>>>> a5457e2461014a3db9f4081faacf1d29f2b88137
