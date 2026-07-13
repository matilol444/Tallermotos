from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDateEdit,
    QTimeEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QComboBox,
    QAbstractItemView,
    QStackedWidget
)
from PySide6.QtCore import Qt, QDate, QTime, QTimer

from database.database import (
    obtener_clientes,
    obtener_motos,
    obtener_turnos,
    obtener_turno_por_id,
    crear_turno,
    actualizar_turno,
    borrar_turno,
)
from utils.whatsapp import abrir_whatsapp_web, obtener_contacto_cliente
from ui.estilo_visual import aplicar_estilo_moderno


class TurnosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.turno_seleccionado = None
        self._init_ui()
        QTimer.singleShot(0, self.refrescar)

    def refrescar(self):
        self.cargar_clientes()
        self.cargar_motos()
        self.cargar_turnos()

    def showEvent(self, event):
        self.refrescar()
        super().showEvent(event)

    def _init_ui(self):
        self.setWindowTitle("Turnos")

        self.paginas = QStackedWidget()

        pagina_lista = QWidget()
        lista_layout = QVBoxLayout(pagina_lista)

        titulo = QLabel("Turnos")
        titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        cliente_layout = QHBoxLayout()
        label_cliente = QLabel("Cliente:")
        label_cliente.setFixedWidth(90)
        self.combo_clientes = QComboBox()
        self.combo_clientes.currentIndexChanged.connect(lambda _: self.cargar_motos())
        self.combo_clientes.currentIndexChanged.connect(self.cargar_turnos)
        cliente_layout.addWidget(label_cliente)
        cliente_layout.addWidget(self.combo_clientes)

        moto_layout = QHBoxLayout()
        label_moto = QLabel("Moto:")
        label_moto.setFixedWidth(90)
        self.combo_motos = QComboBox()
        self.combo_motos.currentIndexChanged.connect(self.cargar_turnos)
        moto_layout.addWidget(label_moto)
        moto_layout.addWidget(self.combo_motos)

        boton_nuevo = QPushButton("Nuevo turno")
        boton_editar = QPushButton("Editar turno")
        boton_eliminar = QPushButton("Eliminar turno")
        boton_whatsapp = QPushButton("Enviar recordatorio por WhatsApp")

        boton_nuevo.clicked.connect(self.nuevo_turno)
        boton_editar.clicked.connect(self.editar_turno)
        boton_eliminar.clicked.connect(self.eliminar_turno)
        boton_whatsapp.clicked.connect(self.enviar_recordatorio_whatsapp)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(boton_nuevo)
        botones_layout.addWidget(boton_editar)
        botones_layout.addWidget(boton_eliminar)
        botones_layout.addWidget(boton_whatsapp)
        botones_layout.addStretch()

        self.tabla_turnos = QTableWidget(0, 7)
        self.tabla_turnos.setHorizontalHeaderLabels([
            "ID",
            "Cliente",
            "Moto",
            "Fecha",
            "Hora",
            "Motivo",
            "Estado"
        ])
        self.tabla_turnos.verticalHeader().setVisible(False)
        self.tabla_turnos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_turnos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_turnos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_turnos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_turnos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_turnos.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_turnos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla_turnos.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabla_turnos.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.tabla_turnos.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tabla_turnos.itemSelectionChanged.connect(self._seleccionar_turno)

        lista_layout.addWidget(titulo)
        lista_layout.addLayout(cliente_layout)
        lista_layout.addLayout(moto_layout)
        lista_layout.addLayout(botones_layout)
        lista_layout.addWidget(self.tabla_turnos)

        self.pagina_lista = pagina_lista

        pagina_formulario = QWidget()
        formulario_layout = QVBoxLayout(pagina_formulario)

        self.label_form_titulo = QLabel("Nuevo turno")
        self.label_form_titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        self.form_combo_clientes = QComboBox()
        self.form_combo_clientes.currentIndexChanged.connect(
            lambda: self.cargar_motos_form(self._get_cliente_id_form())
        )
        self.form_combo_motos = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.input_motivo = QTextEdit()
        self.input_motivo.setFixedHeight(120)
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Pendiente", "Confirmado", "Finalizado", "Cancelado"])

        self.input_motivo.setPlaceholderText("Motivo del turno")

        form_layout = QVBoxLayout()
        form_layout.addLayout(self._crear_campo("Cliente:", self.form_combo_clientes))
        form_layout.addLayout(self._crear_campo("Moto:", self.form_combo_motos))
        form_layout.addLayout(self._crear_campo("Fecha:", self.date_edit))
        form_layout.addLayout(self._crear_campo("Hora:", self.time_edit))
        form_layout.addWidget(QLabel("Motivo:"))
        form_layout.addWidget(self.input_motivo)
        form_layout.addLayout(self._crear_campo("Estado:", self.combo_estado))

        boton_guardar = QPushButton("Guardar turno")
        boton_cancelar = QPushButton("Cancelar")
        boton_guardar.clicked.connect(self.guardar_turno)
        boton_cancelar.clicked.connect(self.cancelar_formulario)

        botones_form_layout = QHBoxLayout()
        botones_form_layout.addWidget(boton_guardar)
        botones_form_layout.addWidget(boton_cancelar)
        botones_form_layout.addStretch()

        formulario_layout.addWidget(self.label_form_titulo)
        formulario_layout.addLayout(form_layout)
        formulario_layout.addLayout(botones_form_layout)

        self.pagina_formulario = pagina_formulario

        self.paginas.addWidget(self.pagina_lista)
        self.paginas.addWidget(self.pagina_formulario)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.paginas)
        aplicar_estilo_moderno(self, [titulo, self.label_form_titulo])

    def _crear_campo(self, etiqueta, campo):
        layout = QHBoxLayout()
        label = QLabel(etiqueta)
        label.setFixedWidth(90)
        layout.addWidget(label)
        layout.addWidget(campo)
        return layout

    def cargar_clientes(self):
        cliente_actual = self._get_cliente_id_seleccionado()
        self.combo_clientes.blockSignals(True)
        self.combo_clientes.clear()
        clientes = obtener_clientes()

        if not clientes:
            self.combo_clientes.addItem("No hay clientes", -1)
            self.combo_clientes.setCurrentIndex(0)
            self.combo_clientes.blockSignals(False)
            self.tabla_turnos.setRowCount(0)
            return

        for cliente in clientes:
            cliente_id, nombre, telefono, whatsapp, direccion = cliente
            self.combo_clientes.addItem(f"{nombre} ({cliente_id})", cliente_id)

        if cliente_actual is not None:
            self._seleccionar_cliente_en_lista(cliente_actual)
        else:
            self.combo_clientes.setCurrentIndex(0)
        self.combo_clientes.blockSignals(False)
        self.cargar_motos()

    def cargar_motos(self):
        cliente_id = self.combo_clientes.currentData()
        self.combo_motos.blockSignals(True)
        self.combo_motos.clear()
        self.tabla_turnos.setRowCount(0)

        if cliente_id is not None and cliente_id != -1:
            for moto_id, _, marca, modelo, _, _, _ in obtener_motos(cliente_id):
                self.combo_motos.addItem(f"{marca} {modelo}", moto_id)

        self.combo_motos.blockSignals(False)
        self.cargar_turnos()

    def cargar_turnos(self):
        cliente_id = self._get_cliente_id_seleccionado()
        moto_id = self._get_moto_id_seleccionado()
        self.tabla_turnos.setRowCount(0)

        if cliente_id is None:
            self.turno_seleccionado = None
            return

        turnos = obtener_turnos(cliente_id, moto_id)
        for turno in turnos:
            fila = self.tabla_turnos.rowCount()
            self.tabla_turnos.insertRow(fila)
            for columna, valor in enumerate(turno):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                if columna == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_turnos.setItem(fila, columna, item)

        self.tabla_turnos.clearSelection()
        self.turno_seleccionado = None
        print(f"[turnos] registros cargados: {len(turnos)} (cliente={cliente_id}, moto={moto_id})")

    def nuevo_turno(self):
        cliente_id = self._get_cliente_id_seleccionado()

        self.turno_seleccionado = None
        self.form_mode = "create"
        self.label_form_titulo.setText("Nuevo turno")

        self._limpiar_formulario()
        if not self.cargar_clientes_form(cliente_id):
            QMessageBox.warning(self, "Nuevo turno", "No hay clientes disponibles para asignar.")
            return

        self.paginas.setCurrentWidget(self.pagina_formulario)

    def editar_turno(self):
        turno_id = self._get_turno_seleccionado_id()
        if turno_id is None:
            QMessageBox.warning(self, "Editar turno", "Seleccione un turno para editar.")
            return

        turno = obtener_turno_por_id(turno_id)
        if turno is None:
            QMessageBox.warning(self, "Editar turno", "No se pudo cargar el turno seleccionado.")
            return

        cliente_id, moto_id, fecha, hora, motivo, estado = turno
        if not self.cargar_clientes_form(cliente_id):
            QMessageBox.warning(self, "Editar turno", "No hay clientes disponibles para asignar.")
            return

        self.turno_seleccionado = turno_id
        self.form_mode = "edit"
        self.label_form_titulo.setText("Editar turno")
        self._cargar_formulario_desde_seleccion(turno)
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def guardar_turno(self):
        cliente_id = self._get_cliente_id_form()
        if cliente_id is None:
            QMessageBox.warning(self, "Guardar turno", "Seleccione un cliente válido.")
            return

        moto_id = self._get_moto_id_form()
        if moto_id is None:
            QMessageBox.warning(self, "Guardar turno", "Seleccione una moto válida.")
            return

        fecha = self.date_edit.date().toString("yyyy-MM-dd")
        hora = self.time_edit.time().toString("HH:mm")
        motivo = self.input_motivo.toPlainText().strip()
        estado = self.combo_estado.currentText()

        if not fecha or not hora:
            QMessageBox.warning(self, "Guardar turno", "La fecha y la hora son obligatorias.")
            return

        print("[DEBUG] 1. Datos obtenidos del formulario en guardar_turno():")
        print(f"  - cliente_id: {cliente_id}")
        print(f"  - moto_id (del combo): {moto_id}")
        print(f"  - moto_texto (del combo): {self.form_combo_motos.currentText()}")
        print(f"  - datos completos: fecha={fecha}, hora={hora}, motivo='{motivo}', estado='{estado}'")

        if self.turno_seleccionado is None:
            print("[DEBUG] 2. Llamando a crear_turno() con los siguientes datos:")
            print(f"  - cliente_id={cliente_id}, moto_id={moto_id}, fecha={fecha}, hora={hora}, motivo='{motivo}', estado='{estado}'")
            crear_turno(cliente_id, moto_id, fecha, hora, motivo, estado)
            QMessageBox.information(self, "Turno creado", "El turno fue guardado correctamente.")
        else:
            print(f"[DEBUG] 2. Llamando a actualizar_turno() para el turno_id={self.turno_seleccionado}:")
            print(f"  - cliente_id={cliente_id}, moto_id={moto_id}, fecha={fecha}, hora={hora}, motivo='{motivo}', estado='{estado}'")
            actualizar_turno(self.turno_seleccionado, cliente_id, moto_id, fecha, hora, motivo, estado)
            QMessageBox.information(self, "Turno actualizado", "Los datos del turno fueron actualizados.")

        self._seleccionar_cliente_en_lista(cliente_id)
        self.cargar_motos()
        self._seleccionar_moto_en_lista(moto_id)
        self.cargar_turnos()
        self.paginas.setCurrentWidget(self.pagina_lista)

    def cancelar_formulario(self):
        self.paginas.setCurrentWidget(self.pagina_lista)

    def eliminar_turno(self):
        turno_id = self._get_turno_seleccionado_id()
        if turno_id is None:
            QMessageBox.warning(self, "Eliminar turno", "Seleccione un turno para eliminar.")
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar turno",
            "¿Está seguro de que desea eliminar el turno seleccionado?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            borrar_turno(turno_id)
            QMessageBox.information(self, "Turno eliminado", "El turno fue eliminado correctamente.")
            self.cargar_turnos()

    def enviar_recordatorio_whatsapp(self):
        turno_id = self._get_turno_seleccionado_id()
        if turno_id is None:
            QMessageBox.warning(self, "WhatsApp", "Seleccione un turno para enviar el recordatorio.")
            return

        turno = obtener_turno_por_id(turno_id)
        if turno is None:
            QMessageBox.warning(self, "WhatsApp", "No se pudo cargar el turno seleccionado.")
            return

        cliente_id, moto_id, fecha, hora, motivo, estado = turno
        cliente, moto = obtener_contacto_cliente(cliente_id, moto_id)
        if cliente is None or not cliente[3]:
            QMessageBox.warning(self, "WhatsApp", "El cliente seleccionado no tiene un número de WhatsApp cargado.")
            return

        marca = moto[1] if moto else ""
        modelo = moto[2] if moto else ""
        mensaje = (
            f"Hola {cliente[1]}, le recordamos su turno para su moto {marca} {modelo} "
            f"el día {fecha} a las {hora}.\n\nTaller de Motos"
        )
        if not abrir_whatsapp_web(cliente[3], mensaje):
            QMessageBox.warning(self, "WhatsApp", "No se pudo abrir WhatsApp Web.")

    def _seleccionar_turno(self):
        pass

    def _get_cliente_id_seleccionado(self):
        indice = self.combo_clientes.currentIndex()
        if indice < 0:
            return None
        cliente_id = self.combo_clientes.itemData(indice)
        return cliente_id if cliente_id != -1 else None

    def cargar_clientes_form(self, selected_cliente_id=None):
        self.form_combo_clientes.blockSignals(True)
        self.form_combo_clientes.clear()
        clientes = obtener_clientes()

        if not clientes:
            self.form_combo_clientes.addItem("No hay clientes", -1)
            self.form_combo_clientes.blockSignals(False)
            return False

        selected_index = 0
        for i, cliente in enumerate(clientes):
            cliente_id, nombre, telefono, whatsapp, direccion = cliente
            self.form_combo_clientes.addItem(f"{nombre} ({cliente_id})", cliente_id)
            if cliente_id == selected_cliente_id:
                selected_index = i

        self.form_combo_clientes.setCurrentIndex(selected_index)
        self.form_combo_clientes.blockSignals(False)
        self.cargar_motos_form(self.form_combo_clientes.itemData(selected_index))
        return True

    def _get_cliente_id_form(self):
        indice = self.form_combo_clientes.currentIndex()
        if indice < 0:
            return None
        cliente_id = self.form_combo_clientes.itemData(indice)
        return cliente_id if cliente_id != -1 else None

    def cargar_motos_form(self, cliente_id):
        print(f"[DEBUG] Iniciando carga de motos para cliente_id: {cliente_id}")
        self.form_combo_motos.blockSignals(True)
        self.form_combo_motos.clear()

        if cliente_id is not None and cliente_id != -1:
            motos = obtener_motos(cliente_id)
            print(f"[DEBUG] Resultado de obtener_motos({cliente_id}): {motos}")
            print(f"[DEBUG] Cantidad de motos devueltas: {len(motos)}")
            for moto_id, _, marca, modelo, _, _, _ in motos:
                print(f"  [DEBUG] Agregando moto al combo: id={moto_id}, texto='{marca} {modelo}'")
                self.form_combo_motos.addItem(f"{marca} {modelo}", moto_id)
        else:
            print("[DEBUG] cliente_id es None o inválido, no se cargan motos.")

        self.form_combo_motos.blockSignals(False)

    def _get_moto_id_seleccionado(self):
        indice = self.combo_motos.currentIndex()
        if indice < 0:
            return None
        moto_id = self.combo_motos.itemData(indice)
        return moto_id if moto_id != -1 else None

    def _get_moto_id_form(self):
        indice = self.form_combo_motos.currentIndex()
        if indice < 0:
            return None
        moto_id = self.form_combo_motos.itemData(indice)
        return moto_id if moto_id != -1 else None

    def _seleccionar_cliente_en_lista(self, cliente_id):
        for i in range(self.combo_clientes.count()):
            if self.combo_clientes.itemData(i) == cliente_id:
                self.combo_clientes.setCurrentIndex(i)
                return

    def _seleccionar_moto_en_lista(self, moto_id):
        for i in range(self.combo_motos.count()):
            if self.combo_motos.itemData(i) == moto_id:
                self.combo_motos.setCurrentIndex(i)
                return

    def _actualizar_label_cliente_form(self):
        cliente_id = self._get_cliente_id_seleccionado()
        cliente_nombre = ""
        if cliente_id is not None:
            clientes = obtener_clientes()
            for cliente in clientes:
                if cliente[0] == cliente_id:
                    cliente_nombre = cliente[1]
                    break
        self.label_cliente_seleccionado.setText(cliente_nombre)

    def _limpiar_formulario(self):
        self.form_combo_motos.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.input_motivo.clear()
        self.combo_estado.setCurrentIndex(0)

    def _get_turno_seleccionado_id(self):
        fila = self.tabla_turnos.currentRow()
        if fila < 0:
            return None

        item_id = self.tabla_turnos.item(fila, 0)
        if item_id is None:
            return None

        return int(item_id.text())

    def _cargar_formulario_desde_seleccion(self, turno):
        cliente_id, moto_id, fecha, hora, motivo, estado = turno
        self.input_motivo.setText(motivo if motivo is not None else "")
        self.date_edit.setDate(QDate.fromString(fecha, "yyyy-MM-dd"))
        self.time_edit.setTime(QTime.fromString(hora, "HH:mm"))
        self.combo_estado.setCurrentText(estado if estado is not None else "Pendiente")

        if moto_id is not None:
            for i in range(self.form_combo_motos.count()):
                if self.form_combo_motos.itemData(i) == moto_id:
                    self.form_combo_motos.setCurrentIndex(i)
                    break
