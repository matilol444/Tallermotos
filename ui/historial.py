from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, QTimer

from database.database import (
    obtener_clientes,
    obtener_motos,
    obtener_reparaciones,
    obtener_turnos,
    obtener_presupuestos,
)
from ui.estilo_visual import aplicar_estilo_moderno


class HistorialWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        QTimer.singleShot(0, self.refrescar)

    def refrescar(self):
        self.cargar_clientes()
        self.cargar_historial()

    def showEvent(self, event):
        self.refrescar()
        super().showEvent(event)

    def _init_ui(self):
        self.setWindowTitle("Historial del cliente")

        layout_principal = QVBoxLayout(self)

        titulo = QLabel("Historial del cliente")
        titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")
        layout_principal.addWidget(titulo)

        selector_layout = QHBoxLayout()
        label_cliente = QLabel("Cliente:")
        label_cliente.setFixedWidth(90)
        self.combo_clientes = QComboBox()
        self.combo_clientes.currentIndexChanged.connect(self.cargar_historial)
        selector_layout.addWidget(label_cliente)
        selector_layout.addWidget(self.combo_clientes)
        layout_principal.addLayout(selector_layout)

        info_box = QWidget()
        info_box.setObjectName("panelInformacion")
        info_layout = QVBoxLayout(info_box)
        self.label_nombre = QLabel()
        self.label_telefono = QLabel()
        self.label_whatsapp = QLabel()
        self.label_direccion = QLabel()
        info_layout.addLayout(self._crear_campo("Nombre:", QLabel(""), self.label_nombre))
        info_layout.addLayout(self._crear_campo("Teléfono:", QLabel(""), self.label_telefono))
        info_layout.addLayout(self._crear_campo("WhatsApp:", QLabel(""), self.label_whatsapp))
        info_layout.addLayout(self._crear_campo("Dirección:", QLabel(""), self.label_direccion))
        seccion_info = QLabel("Información del cliente")
        layout_principal.addWidget(seccion_info)
        layout_principal.addWidget(info_box)

        self.tabla_motos = self._crear_tabla(
            ["Marca", "Modelo", "Año", "Patente", "Kilómetros"],
            5,
        )
        seccion_motos = QLabel("Motos del cliente")
        layout_principal.addWidget(seccion_motos)
        layout_principal.addWidget(self.tabla_motos)

        self.tabla_reparaciones = self._crear_tabla(
            ["Fecha ingreso", "Moto", "Problema", "Estado", "Total"],
            5,
        )
        seccion_reparaciones = QLabel("Historial de reparaciones")
        layout_principal.addWidget(seccion_reparaciones)
        layout_principal.addWidget(self.tabla_reparaciones)

        self.tabla_turnos = self._crear_tabla(
            ["Fecha", "Hora", "Motivo", "Estado"],
            4,
        )
        seccion_turnos = QLabel("Historial de turnos")
        layout_principal.addWidget(seccion_turnos)
        layout_principal.addWidget(self.tabla_turnos)

        self.tabla_presupuestos = self._crear_tabla(
            ["Fecha", "Descripción", "Total", "Estado"],
            4,
        )
        seccion_presupuestos = QLabel("Historial de presupuestos")
        layout_principal.addWidget(seccion_presupuestos)
        layout_principal.addWidget(self.tabla_presupuestos)

        layout_principal.addStretch()
        aplicar_estilo_moderno(
            self,
            [titulo],
            [seccion_info, seccion_motos, seccion_reparaciones, seccion_turnos, seccion_presupuestos],
        )

    def _crear_campo(self, etiqueta, label_etiqueta, valor_label):
        layout = QHBoxLayout()
        label_etiqueta.setText(etiqueta)
        label_etiqueta.setFixedWidth(120)
        layout.addWidget(label_etiqueta)
        layout.addWidget(valor_label)
        return layout

    def _crear_tabla(self, headers, columnas):
        tabla = QTableWidget(0, columnas)
        tabla.setHorizontalHeaderLabels(headers)
        tabla.verticalHeader().setVisible(False)
        tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabla.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        if columnas >= 3:
            tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        if columnas >= 4:
            tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        if columnas >= 5:
            tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        return tabla

    def cargar_clientes(self):
        cliente_actual = self._get_cliente_id_seleccionado()
        self.combo_clientes.blockSignals(True)
        self.combo_clientes.clear()

        clientes = obtener_clientes()
        for cliente in clientes:
            cliente_id, nombre, telefono, whatsapp, direccion = cliente
            self.combo_clientes.addItem(f"{nombre} ({cliente_id})", cliente_id)

        if cliente_actual is not None:
            for indice in range(self.combo_clientes.count()):
                if self.combo_clientes.itemData(indice) == cliente_actual:
                    self.combo_clientes.setCurrentIndex(indice)
                    break
            else:
                self.combo_clientes.setCurrentIndex(0)
        elif self.combo_clientes.count() > 0:
            self.combo_clientes.setCurrentIndex(0)

        self.combo_clientes.blockSignals(False)

    def cargar_historial(self):
        cliente_id = self._get_cliente_id_seleccionado()
        if cliente_id is None:
            self._limpiar_info()
            self.tabla_motos.setRowCount(0)
            self.tabla_reparaciones.setRowCount(0)
            self.tabla_turnos.setRowCount(0)
            self.tabla_presupuestos.setRowCount(0)
            return

        cliente = None
        for registro in obtener_clientes():
            if registro[0] == cliente_id:
                cliente = registro
                break

        if cliente is None:
            self._limpiar_info()
            return

        self.label_nombre.setText(str(cliente[1] or ""))
        self.label_telefono.setText(str(cliente[2] or ""))
        self.label_whatsapp.setText(str(cliente[3] or ""))
        self.label_direccion.setText(str(cliente[4] or ""))

        self._llenar_motos(cliente_id)
        self._llenar_reparaciones(cliente_id)
        self._llenar_turnos(cliente_id)
        self._llenar_presupuestos(cliente_id)

    def _llenar_motos(self, cliente_id):
        self.tabla_motos.setRowCount(0)
        motos = obtener_motos(cliente_id)
        for moto in motos:
            fila = self.tabla_motos.rowCount()
            self.tabla_motos.insertRow(fila)
            datos = [moto[2], moto[3], moto[4], moto[5], moto[6]]
            for columna, valor in enumerate(datos):
                self.tabla_motos.setItem(fila, columna, QTableWidgetItem(str(valor) if valor is not None else ""))

    def _llenar_reparaciones(self, cliente_id):
        self.tabla_reparaciones.setRowCount(0)
        reparaciones = obtener_reparaciones(cliente_id)
        for reparacion in reparaciones:
            fila = self.tabla_reparaciones.rowCount()
            self.tabla_reparaciones.insertRow(fila)
            datos = [
                reparacion[9] or "",
                reparacion[2] or "",
                reparacion[3] or "",
                reparacion[8] or "",
                f"{reparacion[11]:.2f}" if reparacion[11] is not None else "",
            ]
            for columna, valor in enumerate(datos):
                self.tabla_reparaciones.setItem(fila, columna, QTableWidgetItem(str(valor)))

    def _llenar_turnos(self, cliente_id):
        self.tabla_turnos.setRowCount(0)
        turnos = obtener_turnos(cliente_id)
        for turno in turnos:
            fila = self.tabla_turnos.rowCount()
            self.tabla_turnos.insertRow(fila)
            datos = [turno[3], turno[4], turno[5], turno[6]]
            for columna, valor in enumerate(datos):
                self.tabla_turnos.setItem(fila, columna, QTableWidgetItem(str(valor) if valor is not None else ""))

    def _llenar_presupuestos(self, cliente_id):
        self.tabla_presupuestos.setRowCount(0)
        presupuestos = obtener_presupuestos(cliente_id)
        for presupuesto in presupuestos:
            fila = self.tabla_presupuestos.rowCount()
            self.tabla_presupuestos.insertRow(fila)
            datos = [
                "-",
                presupuesto[4] or "",
                f"{presupuesto[7]:.2f}" if presupuesto[7] is not None else "",
                presupuesto[8] or "",
            ]
            for columna, valor in enumerate(datos):
                self.tabla_presupuestos.setItem(fila, columna, QTableWidgetItem(str(valor)))

    def _limpiar_info(self):
        self.label_nombre.setText("")
        self.label_telefono.setText("")
        self.label_whatsapp.setText("")
        self.label_direccion.setText("")
        self.tabla_motos.setRowCount(0)
        self.tabla_reparaciones.setRowCount(0)
        self.tabla_turnos.setRowCount(0)
        self.tabla_presupuestos.setRowCount(0)

    def _get_cliente_id_seleccionado(self):
        indice = self.combo_clientes.currentIndex()
        if indice < 0:
            return None
        cliente_id = self.combo_clientes.itemData(indice)
        return int(cliente_id) if cliente_id is not None else None
