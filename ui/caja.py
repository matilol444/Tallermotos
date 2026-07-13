from datetime import date, timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QAbstractItemView,
)

from database.database import crear_movimiento_caja, obtener_movimientos_caja


CATEGORIAS = {
    "Ingreso": ["Reparaciones cobradas", "Presupuestos aceptados", "Otros ingresos"],
    "Egreso": ["Compra de repuestos", "Otros gastos"],
}


class DialogoMovimiento(QDialog):
    def __init__(self, tipo, parent=None):
        super().__init__(parent)
        self.tipo = tipo
        self.setWindowTitle(f"Registrar {tipo.lower()}")
        self.setMinimumWidth(390)
        self.setStyleSheet("""
            QDialog { background: #202225; color: white; }
            QLineEdit, QComboBox, QDateEdit {
                background: #2f3136; border: 1px solid #3a3d44; border-radius: 6px;
                padding: 8px; color: white;
            }
            QPushButton { background: #5865f2; border: none; border-radius: 6px; padding: 8px 14px; color: white; }
            QPushButton:hover { background: #4752c4; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        titulo = QLabel(f"Nuevo {tipo.lower()}")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(CATEGORIAS[tipo])
        self.input_descripcion = QLineEdit()
        self.input_descripcion.setPlaceholderText("Detalle opcional")
        self.input_monto = QLineEdit()
        self.input_monto.setPlaceholderText("Importe")
        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(QDate.currentDate())

        for etiqueta, campo in (
            ("Categoría", self.combo_categoria),
            ("Descripción", self.input_descripcion),
            ("Importe", self.input_monto),
            ("Fecha", self.fecha),
        ):
            layout.addWidget(QLabel(f"{etiqueta}:"))
            layout.addWidget(campo)

        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(self._validar_y_aceptar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _validar_y_aceptar(self):
        try:
            monto = float(self.input_monto.text().strip().replace(",", "."))
        except ValueError:
            monto = 0
        if monto <= 0:
            QMessageBox.warning(self, "Caja", "Ingrese un importe mayor a cero.")
            return
        self.accept()

    def datos(self):
        return (
            self.tipo,
            self.combo_categoria.currentText(),
            self.input_descripcion.text().strip(),
            float(self.input_monto.text().strip().replace(",", ".")),
            self.fecha.date().toString("yyyy-MM-dd"),
        )


class TarjetaTotal(QFrame):
    def __init__(self, titulo, color):
        super().__init__()
        self.setStyleSheet(
            "background:#2f3136; border:1px solid #3a3d44; border-left:4px solid " + color + "; border-radius:9px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        etiqueta = QLabel(titulo)
        etiqueta.setStyleSheet("color:#b9bbbe; font-size:14px;")
        self.valor = QLabel("$ 0,00")
        self.valor.setStyleSheet("font-size:25px; font-weight:bold; color:white;")
        layout.addWidget(etiqueta)
        layout.addWidget(self.valor)

    def actualizar(self, monto):
        self.valor.setText(f"$ {monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))


class CajaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._crear_interfaz()
        self.refrescar()

    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(15)

        cabecera = QHBoxLayout()
        titulo = QLabel("Caja / Finanzas")
        titulo.setStyleSheet("font-size:26px; font-weight:bold;")
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Hoy", "Esta semana", "Este mes"])
        self.combo_filtro.setCurrentText("Este mes")
        self.combo_filtro.currentTextChanged.connect(self.refrescar)
        cabecera.addWidget(titulo)
        cabecera.addStretch()
        cabecera.addWidget(QLabel("Período:"))
        cabecera.addWidget(self.combo_filtro)
        layout.addLayout(cabecera)

        grilla = QGridLayout()
        self.tarjeta_ingresos = TarjetaTotal("Total ingresos", "#57f287")
        self.tarjeta_egresos = TarjetaTotal("Total egresos", "#ed4245")
        self.tarjeta_ganancia = TarjetaTotal("Ganancia", "#5865f2")
        grilla.addWidget(self.tarjeta_ingresos, 0, 0)
        grilla.addWidget(self.tarjeta_egresos, 0, 1)
        grilla.addWidget(self.tarjeta_ganancia, 0, 2)
        for columna in range(3):
            grilla.setColumnStretch(columna, 1)
        layout.addLayout(grilla)

        acciones = QHBoxLayout()
        boton_ingreso = QPushButton("+ Registrar ingreso")
        boton_egreso = QPushButton("− Registrar egreso")
        boton_ingreso.clicked.connect(lambda: self.registrar_movimiento("Ingreso"))
        boton_egreso.clicked.connect(lambda: self.registrar_movimiento("Egreso"))
        acciones.addWidget(boton_ingreso)
        acciones.addWidget(boton_egreso)
        acciones.addStretch()
        layout.addLayout(acciones)

        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Tipo", "Categoría", "Descripción", "Importe"])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tabla, 1)

    def _rango_fechas(self):
        hoy = date.today()
        filtro = self.combo_filtro.currentText()
        if filtro == "Hoy":
            inicio = hoy
        elif filtro == "Esta semana":
            inicio = hoy - timedelta(days=hoy.weekday())
        else:
            inicio = hoy.replace(day=1)
        return inicio.isoformat(), hoy.isoformat()

    def refrescar(self):
        desde, hasta = self._rango_fechas()
        movimientos = obtener_movimientos_caja(desde, hasta)
        ingresos = sum(monto for _, tipo, _, _, monto, _ in movimientos if tipo == "Ingreso")
        egresos = sum(monto for _, tipo, _, _, monto, _ in movimientos if tipo == "Egreso")
        self.tarjeta_ingresos.actualizar(ingresos)
        self.tarjeta_egresos.actualizar(egresos)
        self.tarjeta_ganancia.actualizar(ingresos - egresos)

        self.tabla.setRowCount(0)
        for _, tipo, categoria, descripcion, monto, fecha in movimientos:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            valores = [
                fecha,
                tipo,
                categoria,
                descripcion or "-",
                f"$ {monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            ]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                if tipo == "Egreso" and columna in (1, 4):
                    item.setForeground(Qt.GlobalColor.red)
                self.tabla.setItem(fila, columna, item)

    def registrar_movimiento(self, tipo):
        dialogo = DialogoMovimiento(tipo, self)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        crear_movimiento_caja(*dialogo.datos())
        self.refrescar()
