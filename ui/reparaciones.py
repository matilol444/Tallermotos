from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QComboBox,
    QAbstractItemView,
    QStackedWidget,
    QDateEdit,
)
from PySide6.QtCore import Qt, QTimer, QDate

from database.database import (
    obtener_clientes,
    obtener_motos,
    obtener_reparaciones,
    obtener_reparacion_por_id,
    crear_reparacion,
    actualizar_reparacion,
    borrar_reparacion,
    obtener_repuestos,
    obtener_repuestos_de_reparacion,
    agregar_repuesto_a_reparacion,
    eliminar_repuesto_de_reparacion,
    actualizar_reparacion_repuestos,
)
from utils.whatsapp import abrir_whatsapp_web, obtener_contacto_cliente
from ui.estilo_visual import aplicar_estilo_moderno


class ReparacionesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.reparacion_seleccionada = None
        self._init_ui()
        QTimer.singleShot(0, self.refrescar)

    def refrescar(self):
        self.cargar_clientes()
        self.cargar_motos()
        self.cargar_reparaciones()

    def showEvent(self, event):
        self.refrescar()
        super().showEvent(event)

    def _init_ui(self):
        self.setWindowTitle("Reparaciones")

        self.paginas = QStackedWidget()

        pagina_lista = QWidget()
        lista_layout = QVBoxLayout(pagina_lista)

        titulo = QLabel("Reparaciones")
        titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        cliente_layout = QHBoxLayout()
        label_cliente = QLabel("Cliente:")
        label_cliente.setFixedWidth(90)
        self.combo_clientes = QComboBox()
        self.combo_clientes.currentIndexChanged.connect(self.cargar_motos)
        self.combo_clientes.currentIndexChanged.connect(self.cargar_reparaciones)
        cliente_layout.addWidget(label_cliente)
        cliente_layout.addWidget(self.combo_clientes)

        moto_layout = QHBoxLayout()
        label_moto = QLabel("Moto:")
        label_moto.setFixedWidth(90)
        self.combo_motos = QComboBox()
        self.combo_motos.currentIndexChanged.connect(self.cargar_reparaciones)
        moto_layout.addWidget(label_moto)
        moto_layout.addWidget(self.combo_motos)

        boton_nuevo = QPushButton("Nueva reparación")
        boton_editar = QPushButton("Editar reparación")
        boton_eliminar = QPushButton("Eliminar reparación")
        boton_whatsapp = QPushButton("Avisar moto lista")

        boton_nuevo.clicked.connect(self.nueva_reparacion)
        boton_editar.clicked.connect(self.editar_reparacion)
        boton_eliminar.clicked.connect(self.eliminar_reparacion)
        boton_whatsapp.clicked.connect(self.avisar_moto_lista_whatsapp)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(boton_nuevo)
        botones_layout.addWidget(boton_editar)
        botones_layout.addWidget(boton_eliminar)
        botones_layout.addWidget(boton_whatsapp)
        botones_layout.addStretch()

        self.tabla_reparaciones = QTableWidget(0, 12)
        self.tabla_reparaciones.setHorizontalHeaderLabels([
            "ID",
            "Cliente",
            "Moto",
            "Problema",
            "Diagnóstico",
            "Trabajo",
            "Repuestos",
            "Mano de obra",
            "Estado",
            "Fecha ingreso",
            "Fecha entrega",
            "Total",
        ])
        self.tabla_reparaciones.verticalHeader().setVisible(False)
        self.tabla_reparaciones.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_reparaciones.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_reparaciones.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(10, QHeaderView.ResizeToContents)
        self.tabla_reparaciones.horizontalHeader().setSectionResizeMode(11, QHeaderView.ResizeToContents)
        self.tabla_reparaciones.itemSelectionChanged.connect(self._seleccionar_reparacion)

        lista_layout.addWidget(titulo)
        lista_layout.addLayout(cliente_layout)
        lista_layout.addLayout(moto_layout)
        lista_layout.addLayout(botones_layout)
        lista_layout.addWidget(self.tabla_reparaciones)

        self.pagina_lista = pagina_lista

        pagina_formulario = QWidget()
        formulario_layout = QVBoxLayout(pagina_formulario)

        self.label_form_titulo = QLabel("Nueva reparación")
        self.label_form_titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        self.form_combo_clientes = QComboBox()
        self.form_combo_clientes.currentIndexChanged.connect(self.cargar_motos_form)
        self.form_combo_motos = QComboBox()
        self.input_problema = QTextEdit()
        self.input_diagnostico = QTextEdit()
        self.input_trabajo = QTextEdit()
        self.input_repuestos = QTextEdit()
        self.input_mano_obra = QLineEdit()
        self.input_total = QLineEdit()
        self.combo_repuestos = QComboBox()
        self.input_cantidad_repuesto = QLineEdit()
        self.input_precio_unitario = QLineEdit()
        self.tabla_repuestos_reparacion = QTableWidget(0, 5)
        self.tabla_repuestos_reparacion.setHorizontalHeaderLabels([
            "ID",
            "Repuesto",
            "Cantidad",
            "Precio unitario",
            "Subtotal",
        ])
        self.tabla_repuestos_reparacion.verticalHeader().setVisible(False)
        self.tabla_repuestos_reparacion.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_repuestos_reparacion.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_repuestos_reparacion.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_repuestos_reparacion.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_repuestos_reparacion.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_repuestos_reparacion.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla_repuestos_reparacion.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla_repuestos_reparacion.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.date_ingreso = QDateEdit()
        self.date_ingreso.setCalendarPopup(True)
        self.date_ingreso.setDate(QDate.currentDate())
        self.date_entrega = QDateEdit()
        self.date_entrega.setCalendarPopup(True)
        self.date_entrega.setSpecialValueText("Sin fecha")
        self.date_entrega.setDate(QDate())
        self.combo_estado = QComboBox()
        self.combo_estado.addItems([
            "Pendiente",
            "En diagnóstico",
            "Esperando repuesto",
            "En reparación",
            "Lista para entregar",
            "Entregada",
            "Cancelada",
        ])

        self.input_problema.setPlaceholderText("Problema reportado")
        self.input_diagnostico.setPlaceholderText("Diagnóstico")
        self.input_trabajo.setPlaceholderText("Trabajo realizado")
        self.input_repuestos.setPlaceholderText("Repuestos utilizados")
        self.input_problema.setFixedHeight(100)
        self.input_diagnostico.setFixedHeight(100)
        self.input_trabajo.setFixedHeight(100)
        self.input_repuestos.setFixedHeight(100)
        self.input_mano_obra.setPlaceholderText("Mano de obra")
        self.input_total.setPlaceholderText("Precio total")
        self.input_cantidad_repuesto.setPlaceholderText("Cantidad")
        self.input_precio_unitario.setPlaceholderText("Precio unitario")

        form_layout = QVBoxLayout()
        form_layout.addLayout(self._crear_campo("Cliente:", self.form_combo_clientes))
        form_layout.addLayout(self._crear_campo("Moto:", self.form_combo_motos))
        form_layout.addWidget(QLabel("Problema reportado:"))
        form_layout.addWidget(self.input_problema)
        form_layout.addWidget(QLabel("Diagnóstico:"))
        form_layout.addWidget(self.input_diagnostico)
        form_layout.addWidget(QLabel("Trabajo realizado:"))
        form_layout.addWidget(self.input_trabajo)
        form_layout.addWidget(QLabel("Repuestos utilizados:"))
        form_layout.addWidget(self.input_repuestos)
        form_layout.addLayout(self._crear_campo("Mano de obra:", self.input_mano_obra))
        form_layout.addLayout(self._crear_campo("Precio total:", self.input_total))
        form_layout.addWidget(QLabel("Repuestos utilizados:"))
        form_layout.addLayout(self._crear_campo("Repuesto:", self.combo_repuestos))
        form_layout.addLayout(self._crear_campo("Cantidad:", self.input_cantidad_repuesto))
        form_layout.addLayout(self._crear_campo("Precio unitario:", self.input_precio_unitario))
        boton_agregar_repuesto = QPushButton("Agregar repuesto")
        boton_agregar_repuesto.clicked.connect(self.agregar_repuesto_a_formulario)
        form_layout.addWidget(boton_agregar_repuesto)
        form_layout.addWidget(self.tabla_repuestos_reparacion)
        boton_eliminar_repuesto = QPushButton("Eliminar repuesto de la reparación")
        boton_eliminar_repuesto.clicked.connect(self.eliminar_repuesto_de_formulario)
        form_layout.addWidget(boton_eliminar_repuesto)
        form_layout.addLayout(self._crear_campo("Fecha ingreso:", self.date_ingreso))
        form_layout.addLayout(self._crear_campo("Fecha entrega:", self.date_entrega))
        form_layout.addLayout(self._crear_campo("Estado:", self.combo_estado))

        boton_guardar = QPushButton("Guardar reparación")
        boton_cancelar = QPushButton("Cancelar")
        boton_guardar.clicked.connect(self.guardar_reparacion)
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
        label.setFixedWidth(120)
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
            self.tabla_reparaciones.setRowCount(0)
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
        cliente_id = self._get_cliente_id_seleccionado()
        moto_actual = self._get_moto_id_seleccionado()
        self.combo_motos.blockSignals(True)
        self.combo_motos.clear()
        self.tabla_reparaciones.setRowCount(0)

        if cliente_id is None:
            self.combo_motos.addItem("Seleccione un cliente", -1)
            self.combo_motos.setCurrentIndex(0)
            self.combo_motos.blockSignals(False)
            return

        motos = obtener_motos(cliente_id)
        if not motos:
            self.combo_motos.addItem("No hay motos", -1)
            self.combo_motos.setCurrentIndex(0)
            self.combo_motos.blockSignals(False)
            self.cargar_reparaciones()
            return

        for moto in motos:
            moto_id, _, marca, modelo, ano, patente, kilometros = moto
            self.combo_motos.addItem(f"{marca} {modelo} ({patente})", moto_id)

        self._seleccionar_moto_en_lista(moto_actual)
        self.combo_motos.blockSignals(False)
        self.cargar_reparaciones()

    def cargar_reparaciones(self):
        cliente_id = self._get_cliente_id_seleccionado()
        moto_id = self._get_moto_id_seleccionado()
        self.tabla_reparaciones.setRowCount(0)

        if cliente_id is None:
            self.reparacion_seleccionada = None
            return

        reparaciones = obtener_reparaciones(cliente_id, moto_id)
        for reparacion in reparaciones:
            fila = self.tabla_reparaciones.rowCount()
            self.tabla_reparaciones.insertRow(fila)
            for columna, valor in enumerate(reparacion):
                texto = ""
                if valor is not None:
                    if isinstance(valor, float):
                        texto = f"{valor:.2f}"
                    else:
                        texto = str(valor)
                item = QTableWidgetItem(texto)
                if columna == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_reparaciones.setItem(fila, columna, item)

        self.tabla_reparaciones.clearSelection()
        self.reparacion_seleccionada = None
        print(f"[reparaciones] registros cargados: {len(reparaciones)} (cliente={cliente_id}, moto={moto_id})")

    def nueva_reparacion(self):
        cliente_id = self._get_cliente_id_seleccionado()

        self.reparacion_seleccionada = None
        self.form_mode = "create"
        self.label_form_titulo.setText("Nueva reparación")
        self._limpiar_formulario()
        if not self.cargar_clientes_form(cliente_id):
            QMessageBox.warning(self, "Nueva reparación", "No hay clientes disponibles para asignar.")
            return

        self._cargar_repuestos_disponibles()
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def editar_reparacion(self):
        reparacion_id = self._get_reparacion_seleccionada_id()
        if reparacion_id is None:
            QMessageBox.warning(self, "Editar reparación", "Seleccione una reparación para editar.")
            return

        reparacion = obtener_reparacion_por_id(reparacion_id)
        if reparacion is None:
            QMessageBox.warning(self, "Editar reparación", "No se pudo cargar la reparación seleccionada.")
            return

        cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra, estado, fecha_ingreso, fecha_entrega, total = reparacion
        if not self.cargar_clientes_form(cliente_id):
            QMessageBox.warning(self, "Editar reparación", "No hay clientes disponibles para asignar.")
            return

        self.reparacion_seleccionada = reparacion_id
        self.form_mode = "edit"
        self.label_form_titulo.setText("Editar reparación")
        self._cargar_repuestos_disponibles()
        self._cargar_formulario_desde_seleccion(reparacion)
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def guardar_reparacion(self):
        cliente_id = self._get_cliente_id_form()
        if cliente_id is None:
            QMessageBox.warning(self, "Guardar reparación", "Seleccione un cliente válido.")
            return

        moto_id = self._get_moto_id_form()
        if moto_id is None:
            QMessageBox.warning(self, "Guardar reparación", "Seleccione una moto válida.")
            return

        problema = self.input_problema.toPlainText().strip()
        diagnostico = self.input_diagnostico.toPlainText().strip()
        trabajo = self.input_trabajo.toPlainText().strip()
        repuestos = self.input_repuestos.toPlainText().strip()
        mano_obra = self.input_mano_obra.text().strip()
        estado = self.combo_estado.currentText()

        try:
            mano_obra_val = float(mano_obra) if mano_obra else None
        except ValueError:
            QMessageBox.warning(self, "Guardar reparación", "La mano de obra debe ser un número válido.")
            return

        fecha_ingreso = self.date_ingreso.date().toString("yyyy-MM-dd")
        fecha_entrega = self.date_entrega.date().toString("yyyy-MM-dd") if self.date_entrega.date().isValid() else None
        total_texto = self.input_total.text().strip()
        try:
            total_val = float(total_texto) if total_texto else None
        except ValueError:
            QMessageBox.warning(self, "Guardar reparación", "El total debe ser un número válido.")
            return

        if self.reparacion_seleccionada is None:
            reparacion_id = crear_reparacion(
                cliente_id,
                moto_id,
                problema,
                diagnostico,
                trabajo,
                repuestos,
                mano_obra_val,
                estado,
                fecha_ingreso,
                fecha_entrega,
                total_val,
            )
            self.reparacion_seleccionada = reparacion_id
            QMessageBox.information(self, "Reparación creada", "La reparación fue guardada correctamente.")
        else:
            actualizar_reparacion(
                self.reparacion_seleccionada,
                cliente_id,
                moto_id,
                problema,
                diagnostico,
                trabajo,
                repuestos,
                mano_obra_val,
                estado,
                fecha_ingreso,
                fecha_entrega,
                total_val,
            )
            QMessageBox.information(self, "Reparación actualizada", "Los datos de la reparación fueron actualizados.")

        items = []
        for fila in range(self.tabla_repuestos_reparacion.rowCount()):
            item_id = self.tabla_repuestos_reparacion.item(fila, 0)
            item_cantidad = self.tabla_repuestos_reparacion.item(fila, 2)
            item_precio = self.tabla_repuestos_reparacion.item(fila, 3)
            if item_id is None or item_cantidad is None or item_precio is None:
                continue
            try:
                repuesto_id = int(item_id.text())
                cantidad = int(item_cantidad.text())
                precio_unitario = float(item_precio.text())
            except ValueError:
                continue
            items.append((repuesto_id, cantidad, precio_unitario))

        if not actualizar_reparacion_repuestos(self.reparacion_seleccionada, items):
            QMessageBox.warning(self, "Guardar reparación", "No se pudo actualizar la relación de repuestos por falta de stock.")
            return

        if total_val is None:
            total_val = 0.0
            for fila in range(self.tabla_repuestos_reparacion.rowCount()):
                item_cantidad = self.tabla_repuestos_reparacion.item(fila, 2)
                item_precio = self.tabla_repuestos_reparacion.item(fila, 3)
                if item_cantidad is not None and item_precio is not None:
                    try:
                        total_val += int(item_cantidad.text()) * float(item_precio.text())
                    except ValueError:
                        pass
            total_val += mano_obra_val if mano_obra_val is not None else 0.0
            actualizar_reparacion(self.reparacion_seleccionada, cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra_val, estado, fecha_ingreso, fecha_entrega, total_val)

        self._seleccionar_cliente_en_lista(cliente_id)
        self.cargar_motos()
        self._seleccionar_moto_en_lista(moto_id)
        self.cargar_reparaciones()
        self.paginas.setCurrentWidget(self.pagina_lista)

    def cancelar_formulario(self):
        self.paginas.setCurrentWidget(self.pagina_lista)

    def eliminar_reparacion(self):
        reparacion_id = self._get_reparacion_seleccionada_id()
        if reparacion_id is None:
            QMessageBox.warning(self, "Eliminar reparación", "Seleccione una reparación para eliminar.")
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar reparación",
            "¿Está seguro de que desea eliminar la reparación seleccionada?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if respuesta == QMessageBox.Yes:
            borrar_reparacion(reparacion_id)
            QMessageBox.information(self, "Reparación eliminada", "La reparación fue eliminada correctamente.")
            self.cargar_reparaciones()

    def avisar_moto_lista_whatsapp(self):
        reparacion_id = self._get_reparacion_seleccionada_id()
        if reparacion_id is None:
            QMessageBox.warning(self, "WhatsApp", "Seleccione una reparación para avisar al cliente.")
            return

        reparacion = obtener_reparacion_por_id(reparacion_id)
        if reparacion is None:
            QMessageBox.warning(self, "WhatsApp", "No se pudo cargar la reparación seleccionada.")
            return

        cliente_id, moto_id, _, _, _, _, _, estado, _, _, _ = reparacion
        cliente, moto = obtener_contacto_cliente(cliente_id, moto_id)
        if cliente is None or not cliente[3]:
            QMessageBox.warning(self, "WhatsApp", "El cliente seleccionado no tiene un número de WhatsApp cargado.")
            return

        marca = moto[1] if moto else ""
        modelo = moto[2] if moto else ""
        mensaje = (
            f"Hola {cliente[1]}, le informamos el estado de su moto {marca} {modelo}: "
            f"{estado or 'Sin estado'}.\n\nTaller de Motos"
        )
        if not abrir_whatsapp_web(cliente[3], mensaje):
            QMessageBox.warning(self, "WhatsApp", "No se pudo abrir WhatsApp Web.")

    def _seleccionar_reparacion(self):
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
        self.cargar_motos_form()
        return True

    def _get_cliente_id_form(self):
        indice = self.form_combo_clientes.currentIndex()
        if indice < 0:
            return None
        cliente_id = self.form_combo_clientes.itemData(indice)
        return cliente_id if cliente_id != -1 else None

    def cargar_motos_form(self):
        cliente_id = self._get_cliente_id_form()
        self.form_combo_motos.blockSignals(True)
        self.form_combo_motos.clear()

        if cliente_id is None:
            self.form_combo_motos.addItem("Seleccione un cliente", -1)
            self.form_combo_motos.blockSignals(False)
            return

        motos = obtener_motos(cliente_id)
        if not motos:
            self.form_combo_motos.addItem("No hay motos", -1)
            self.form_combo_motos.blockSignals(False)
            return

        for moto in motos:
            moto_id, _, marca, modelo, ano, patente, kilometros = moto
            self.form_combo_motos.addItem(f"{marca} {modelo} ({patente})", moto_id)
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
        if cliente_id is None:
            if self.combo_clientes.count():
                self.combo_clientes.setCurrentIndex(0)
            return

        for i in range(self.combo_clientes.count()):
            if self.combo_clientes.itemData(i) == cliente_id:
                self.combo_clientes.setCurrentIndex(i)
                return

        if self.combo_clientes.count():
            self.combo_clientes.setCurrentIndex(0)

    def _seleccionar_moto_en_lista(self, moto_id):
        if moto_id is None:
            if self.combo_motos.count():
                self.combo_motos.setCurrentIndex(0)
            return

        for i in range(self.combo_motos.count()):
            if self.combo_motos.itemData(i) == moto_id:
                self.combo_motos.setCurrentIndex(i)
                return

        if self.combo_motos.count():
            self.combo_motos.setCurrentIndex(0)

    def _limpiar_formulario(self):
        self.form_combo_motos.clear()
        self.combo_repuestos.clear()
        self.input_cantidad_repuesto.clear()
        self.input_precio_unitario.clear()
        self.tabla_repuestos_reparacion.setRowCount(0)
        self.input_problema.clear()
        self.input_diagnostico.clear()
        self.input_trabajo.clear()
        self.input_repuestos.clear()
        self.input_mano_obra.clear()
        self.input_total.clear()
        self.date_ingreso.setDate(QDate.currentDate())
        self.date_entrega.setDate(QDate())
        self.combo_estado.setCurrentIndex(0)

    def _get_reparacion_seleccionada_id(self):
        fila = self.tabla_reparaciones.currentRow()
        if fila < 0:
            return None

        item_id = self.tabla_reparaciones.item(fila, 0)
        if item_id is None:
            return None

        return int(item_id.text())

    def _cargar_repuestos_disponibles(self):
        self.combo_repuestos.clear()
        repuestos = obtener_repuestos()
        for repuesto in repuestos:
            repuesto_id, nombre, codigo, marca, stock, precio_compra, precio_venta = repuesto
            self.combo_repuestos.addItem(f"{nombre} ({stock} disp.)", repuesto_id)

    def agregar_repuesto_a_formulario(self):
        repuesto_id = self.combo_repuestos.currentData()
        if repuesto_id is None:
            QMessageBox.warning(self, "Agregar repuesto", "Seleccione un repuesto válido.")
            return

        try:
            cantidad = int(self.input_cantidad_repuesto.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Agregar repuesto", "La cantidad debe ser un número entero.")
            return

        try:
            precio_unitario = float(self.input_precio_unitario.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Agregar repuesto", "El precio unitario debe ser un número válido.")
            return

        if cantidad <= 0:
            QMessageBox.warning(self, "Agregar repuesto", "La cantidad debe ser mayor que cero.")
            return

        fila = self.tabla_repuestos_reparacion.rowCount()
        self.tabla_repuestos_reparacion.insertRow(fila)
        self.tabla_repuestos_reparacion.setItem(fila, 0, QTableWidgetItem(str(repuesto_id)))
        self.tabla_repuestos_reparacion.setItem(fila, 1, QTableWidgetItem(self.combo_repuestos.currentText()))
        self.tabla_repuestos_reparacion.setItem(fila, 2, QTableWidgetItem(str(cantidad)))
        self.tabla_repuestos_reparacion.setItem(fila, 3, QTableWidgetItem(f"{precio_unitario:.2f}"))
        self.tabla_repuestos_reparacion.setItem(fila, 4, QTableWidgetItem(f"{cantidad * precio_unitario:.2f}"))
        self.input_cantidad_repuesto.clear()
        self.input_precio_unitario.clear()

    def eliminar_repuesto_de_formulario(self):
        fila = self.tabla_repuestos_reparacion.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Eliminar repuesto", "Seleccione un repuesto de la lista para eliminar.")
            return
        self.tabla_repuestos_reparacion.removeRow(fila)

    def _cargar_repuestos_asociados(self, reparacion_id=None):
        self.tabla_repuestos_reparacion.setRowCount(0)
        if reparacion_id is None:
            return
        repuestos = obtener_repuestos_de_reparacion(reparacion_id)
        for item in repuestos:
            relacion_id, repuesto_id, nombre, cantidad, precio_unitario = item
            fila = self.tabla_repuestos_reparacion.rowCount()
            self.tabla_repuestos_reparacion.insertRow(fila)
            self.tabla_repuestos_reparacion.setItem(fila, 0, QTableWidgetItem(str(repuesto_id)))
            self.tabla_repuestos_reparacion.setItem(fila, 1, QTableWidgetItem(str(nombre)))
            self.tabla_repuestos_reparacion.setItem(fila, 2, QTableWidgetItem(str(cantidad)))
            self.tabla_repuestos_reparacion.setItem(fila, 3, QTableWidgetItem(f"{precio_unitario:.2f}"))
            self.tabla_repuestos_reparacion.setItem(fila, 4, QTableWidgetItem(f"{cantidad * precio_unitario:.2f}"))

    def _cargar_formulario_desde_seleccion(self, reparacion):
        cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra, estado, fecha_ingreso, fecha_entrega, total = reparacion
        self.input_problema.setText(problema if problema is not None else "")
        self.input_diagnostico.setText(diagnostico if diagnostico is not None else "")
        self.input_trabajo.setText(trabajo if trabajo is not None else "")
        self.input_repuestos.setText(repuestos if repuestos is not None else "")
        self.input_mano_obra.setText(str(mano_obra) if mano_obra is not None else "")
        self.input_total.setText(str(total) if total is not None else "")
        self.combo_estado.setCurrentText(estado if estado is not None else "Pendiente")

        if fecha_ingreso is not None:
            try:
                self.date_ingreso.setDate(QDate.fromString(fecha_ingreso, "yyyy-MM-dd"))
            except Exception:
                self.date_ingreso.setDate(QDate.currentDate())
        else:
            self.date_ingreso.setDate(QDate.currentDate())

        if fecha_entrega is not None:
            try:
                self.date_entrega.setDate(QDate.fromString(fecha_entrega, "yyyy-MM-dd"))
            except Exception:
                self.date_entrega.setDate(QDate())
        else:
            self.date_entrega.setDate(QDate())

        self._cargar_repuestos_asociados(reparacion_id=self.reparacion_seleccionada)

        if moto_id is not None:
            for i in range(self.form_combo_motos.count()):
                if self.form_combo_motos.itemData(i) == moto_id:
                    self.form_combo_motos.setCurrentIndex(i)
                    break
