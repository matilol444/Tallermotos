"""Estilo compartido para las pantallas operativas del taller.

No modifica datos ni comportamientos: centraliza únicamente la presentación.
"""

from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QTableWidget, QVBoxLayout


ESTILO_MODULO = """
QWidget#moduloTaller {
    background: #202225;
    color: white;
}
QWidget#moduloTaller QPushButton {
    background: #36393f;
    border: 1px solid #454a53;
    border-radius: 8px;
    padding: 10px 16px;
    color: white;
    font-size: 14px;
    font-weight: 600;
}
QWidget#moduloTaller QPushButton:hover { background: #5865f2; border-color: #5865f2; }
QWidget#moduloTaller QPushButton[accionVisual="principal"] { background: #5865f2; border-color: #5865f2; }
QWidget#moduloTaller QPushButton[accionVisual="principal"]:hover { background: #4752c4; }
QWidget#moduloTaller QPushButton[accionVisual="peligro"] { background: #472c31; border-color: #733840; }
QWidget#moduloTaller QPushButton[accionVisual="peligro"]:hover { background: #ed4245; border-color: #ed4245; }
QWidget#moduloTaller QPushButton[accionVisual="secundaria"] { background: #2b2d31; color: #b9bbbe; }
QWidget#moduloTaller QLineEdit,
QWidget#moduloTaller QTextEdit,
QWidget#moduloTaller QComboBox,
QWidget#moduloTaller QDateEdit,
QWidget#moduloTaller QTimeEdit {
    background: #2f3136;
    border: 1px solid #3f434b;
    border-radius: 7px;
    padding: 8px 10px;
    color: white;
    min-height: 20px;
}
QWidget#moduloTaller QLineEdit:focus,
QWidget#moduloTaller QTextEdit:focus,
QWidget#moduloTaller QComboBox:focus,
QWidget#moduloTaller QDateEdit:focus,
QWidget#moduloTaller QTimeEdit:focus { border-color: #5865f2; }
QWidget#moduloTaller QTableWidget {
    background: #2b2d31;
    alternate-background-color: #303238;
    border: 1px solid #3a3d44;
    border-radius: 9px;
    gridline-color: #3a3d44;
    selection-background-color: #5865f2;
    selection-color: white;
}
QWidget#moduloTaller QFrame#panelTabla {
    background: #2f3136;
    border: 1px solid #3a3d44;
    border-radius: 10px;
    padding: 5px;
}
QWidget#moduloTaller QTableWidget::item { padding: 7px; border: none; }
QWidget#moduloTaller QHeaderView::section {
    background: #292b2f;
    color: #b9bbbe;
    border: none;
    border-bottom: 1px solid #454a53;
    padding: 9px 7px;
    font-weight: bold;
}
QWidget#moduloTaller QScrollBar:vertical { background: #202225; width: 10px; }
QWidget#moduloTaller QScrollBar::handle:vertical { background: #4b4e57; border-radius: 5px; min-height: 25px; }
QWidget#moduloTaller QFrame#panelInformacion,
QWidget#moduloTaller QWidget#panelInformacion {
    background: #2f3136;
    border: 1px solid #3a3d44;
    border-radius: 9px;
    padding: 8px;
}
"""


def aplicar_estilo_moderno(widget, titulos=(), secciones=()):
    """Aplica espaciado, controles y tablas uniformes a una pantalla existente."""
    widget.setObjectName("moduloTaller")
    widget.setStyleSheet(ESTILO_MODULO)

    if widget.layout() is not None:
        widget.layout().setContentsMargins(24, 22, 24, 22)
        widget.layout().setSpacing(16)

    for tabla in widget.findChildren(QTableWidget):
        tabla.setAlternatingRowColors(True)
        tabla.setShowGrid(False)
        tabla.verticalHeader().setDefaultSectionSize(36)
        _envolver_tabla_en_panel(tabla)

    for boton in widget.findChildren(QPushButton):
        texto = boton.text().lower()
        boton.setMinimumHeight(max(boton.minimumHeight(), 42))
        if any(palabra in texto for palabra in ("eliminar", "borrar")):
            boton.setProperty("accionVisual", "peligro")
        elif "cancelar" in texto or "volver" in texto:
            boton.setProperty("accionVisual", "secundaria")
        elif any(palabra in texto for palabra in ("nuevo", "guardar", "agregar", "generar", "enviar", "avisar", "registrar", "ingresar")):
            boton.setProperty("accionVisual", "principal")

    for etiqueta in titulos:
        etiqueta.setStyleSheet("font-size: 26px; font-weight: bold; color: white; margin-bottom: 4px;")
    for etiqueta in secciones:
        etiqueta.setStyleSheet("font-size: 16px; font-weight: bold; color: #f2f3f5; margin-top: 8px;")


def _envolver_tabla_en_panel(tabla):
    """Añade un contenedor visual sin cambiar la referencia ni el contenido de la tabla."""
    if tabla.property("panelVisual"):
        return

    padre = tabla.parentWidget()
    layout_padre = padre.layout() if padre is not None else None
    if layout_padre is None or not hasattr(layout_padre, "insertWidget"):
        return

    indice = layout_padre.indexOf(tabla)
    if indice < 0:
        return

    panel = QFrame(padre)
    panel.setObjectName("panelTabla")
    panel_layout = QVBoxLayout(panel)
    panel_layout.setContentsMargins(7, 7, 7, 7)
    panel_layout.addWidget(tabla)
    layout_padre.insertWidget(indice, panel)
    tabla.setProperty("panelVisual", True)
