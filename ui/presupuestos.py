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
)
from PySide6.QtCore import Qt, QTimer

from database.database import (
    obtener_clientes,
    obtener_motos,
    obtener_reparaciones,
    obtener_presupuestos,
    obtener_presupuesto_por_id,
    crear_presupuesto,
    actualizar_presupuesto,
    borrar_presupuesto,
)
from utils.pdf import generar_pdf_presupuesto
from utils.whatsapp import abrir_whatsapp_web, obtener_contacto_cliente
from ui.estilo_visual import aplicar_estilo_moderno


class PresupuestosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.presupuesto_seleccionado = None
        self._init_ui()
        QTimer.singleShot(0, self.refrescar)

    def refrescar(self):
        self.cargar_clientes()
        self.cargar_motos()
        self.cargar_presupuestos()

    def showEvent(self, event):
        self.refrescar()
        super().showEvent(event)

    def _init_ui(self):
        self.setWindowTitle("Presupuestos")

        self.paginas = QStackedWidget()

        pagina_lista = QWidget()
        lista_layout = QVBoxLayout(pagina_lista)

        titulo = QLabel("Presupuestos")
        titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        cliente_layout = QHBoxLayout()
        label_cliente = QLabel("Cliente:")
        label_cliente.setFixedWidth(90)
        self.combo_clientes = QComboBox()
        self.combo_clientes.currentIndexChanged.connect(self.cargar_motos)
        self.combo_clientes.currentIndexChanged.connect(self.cargar_presupuestos)
        cliente_layout.addWidget(label_cliente)
        cliente_layout.addWidget(self.combo_clientes)

        moto_layout = QHBoxLayout()
        label_moto = QLabel("Moto:")
        label_moto.setFixedWidth(90)
        self.combo_motos = QComboBox()
        self.combo_motos.currentIndexChanged.connect(self.cargar_presupuestos)
        moto_layout.addWidget(label_moto)
        moto_layout.addWidget(self.combo_motos)

        boton_nuevo = QPushButton("Nuevo presupuesto")
        boton_editar = QPushButton("Editar presupuesto")
        boton_eliminar = QPushButton("Eliminar presupuesto")
        boton_whatsapp = QPushButton("Enviar presupuesto")

        boton_nuevo.clicked.connect(self.nuevo_presupuesto)
        boton_editar.clicked.connect(self.editar_presupuesto)
        boton_eliminar.clicked.connect(self.eliminar_presupuesto)
        boton_whatsapp.clicked.connect(self.enviar_presupuesto_whatsapp)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(boton_nuevo)
        botones_layout.addWidget(boton_editar)
        botones_layout.addWidget(boton_eliminar)
        botones_layout.addWidget(boton_whatsapp)
        botones_layout.addStretch()

        self.tabla_presupuestos = QTableWidget(0, 9)
        self.tabla_presupuestos.setHorizontalHeaderLabels([
            "ID",
            "Cliente",
            "Moto",
            "Reparación",
            "Descripción",
            "Repuestos",
            "Mano de obra",
            "Total",
            "Estado",
        ])
        self.tabla_presupuestos.verticalHeader().setVisible(False)
        self.tabla_presupuestos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_presupuestos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_presupuestos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.tabla_presupuestos.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.tabla_presupuestos.itemSelectionChanged.connect(self._seleccionar_presupuesto)

        lista_layout.addWidget(titulo)
        lista_layout.addLayout(cliente_layout)
        lista_layout.addLayout(moto_layout)
        lista_layout.addLayout(botones_layout)
        lista_layout.addWidget(self.tabla_presupuestos)

        self.pagina_lista = pagina_lista

        pagina_formulario = QWidget()
        formulario_layout = QVBoxLayout(pagina_formulario)

        self.label_form_titulo = QLabel("Nuevo presupuesto")
        self.label_form_titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        self.form_combo_clientes = QComboBox()
        self.form_combo_clientes.currentIndexChanged.connect(self.cargar_motos_form)
        self.form_combo_clientes.currentIndexChanged.connect(self.cargar_reparaciones_form)
        self.form_combo_motos = QComboBox()
        self.form_combo_motos.currentIndexChanged.connect(self.cargar_reparaciones_form)
        self.combo_reparaciones = QComboBox()
        self.input_descripcion = QTextEdit()
        self.input_repuestos = QLineEdit()
        self.input_mano_obra = QLineEdit()
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Pendiente", "Aceptado", "Rechazado"])
        self.label_total = QLabel("Total: $0.00")
        self.label_total.setStyleSheet("font-size:16px;font-weight:bold;")

        self.input_descripcion.setPlaceholderText("Descripción del trabajo")
        self.input_repuestos.setPlaceholderText("0.00")
        self.input_mano_obra.setPlaceholderText("0.00")
        self.input_descripcion.setFixedHeight(100)

        self.input_repuestos.textChanged.connect(self._actualizar_total)
        self.input_mano_obra.textChanged.connect(self._actualizar_total)

        form_layout = QVBoxLayout()
        form_layout.addLayout(self._crear_campo("Cliente:", self.form_combo_clientes))
        form_layout.addLayout(self._crear_campo("Moto:", self.form_combo_motos))
        form_layout.addLayout(self._crear_campo("Reparación:", self.combo_reparaciones))
        form_layout.addWidget(QLabel("Descripción del trabajo:"))
        form_layout.addWidget(self.input_descripcion)
        form_layout.addLayout(self._crear_campo("Repuestos:", self.input_repuestos))
        form_layout.addLayout(self._crear_campo("Mano de obra:", self.input_mano_obra))
        form_layout.addWidget(self.label_total)
        form_layout.addLayout(self._crear_campo("Estado:", self.combo_estado))

        boton_guardar = QPushButton("Guardar presupuesto")
        boton_cancelar = QPushButton("Cancelar")
        boton_pdf = QPushButton("Generar PDF")
        boton_guardar.clicked.connect(self.guardar_presupuesto)
        boton_cancelar.clicked.connect(self.cancelar_formulario)
        boton_pdf.clicked.connect(self.generar_pdf_actual)

        botones_form_layout = QHBoxLayout()
        botones_form_layout.addWidget(boton_guardar)
        botones_form_layout.addWidget(boton_cancelar)
        botones_form_layout.addWidget(boton_pdf)
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
        label.setFixedWidth(100)
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
            self.tabla_presupuestos.setRowCount(0)
            return

        for cliente in clientes:
            cliente_id, nombre, telefono, whatsapp, direccion = cliente
            self.combo_clientes.addItem(f"{nombre} ({cliente_id})", cliente_id)

        self._seleccionar_cliente_en_lista(cliente_actual)
        if self.combo_clientes.currentIndex() < 0:
            self.combo_clientes.setCurrentIndex(0)
        self.combo_clientes.blockSignals(False)
        self.cargar_motos()

    def cargar_motos(self):
        cliente_id = self._get_cliente_id_seleccionado()
        moto_actual = self._get_moto_id_seleccionado()
        self.combo_motos.blockSignals(True)
        self.combo_motos.clear()
        self.tabla_presupuestos.setRowCount(0)

        if cliente_id is None:
            self.combo_motos.addItem("Seleccione un cliente", -1)
            self.combo_motos.blockSignals(False)
            return

        motos = obtener_motos(cliente_id)
        if not motos:
            self.combo_motos.addItem("No hay motos", -1)
            self.combo_motos.blockSignals(False)
            self.cargar_presupuestos()
            return

        for moto in motos:
            moto_id, _, marca, modelo, ano, patente, kilometros = moto
            self.combo_motos.addItem(f"{marca} {modelo} ({patente})", moto_id)

        self._seleccionar_moto_en_lista(moto_actual)
        self.combo_motos.blockSignals(False)
        self.cargar_presupuestos()

    def cargar_presupuestos(self):
        cliente_id = self._get_cliente_id_seleccionado()
        moto_id = self._get_moto_id_seleccionado()
        self.tabla_presupuestos.setRowCount(0)

        if cliente_id is None:
            return

        presupuestos = obtener_presupuestos(cliente_id, moto_id)
        for presupuesto in presupuestos:
            fila = self.tabla_presupuestos.rowCount()
            self.tabla_presupuestos.insertRow(fila)
            for columna, valor in enumerate(presupuesto):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                if columna == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_presupuestos.setItem(fila, columna, item)

        self.tabla_presupuestos.clearSelection()
        self.presupuesto_seleccionado = None

    def nuevo_presupuesto(self):
        cliente_id = self._get_cliente_id_seleccionado()

        self.presupuesto_seleccionado = None
        self.label_form_titulo.setText("Nuevo presupuesto")
        self._limpiar_formulario()
        if not self.cargar_clientes_form(cliente_id):
            QMessageBox.warning(self, "Nuevo presupuesto", "No hay clientes disponibles para asignar.")
            return
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def editar_presupuesto(self):
        presupuesto_id = self._get_presupuesto_seleccionado_id()
        if presupuesto_id is None:
            QMessageBox.warning(self, "Editar presupuesto", "Seleccione un presupuesto para editar.")
            return

        presupuesto = obtener_presupuesto_por_id(presupuesto_id)
        if presupuesto is None:
            QMessageBox.warning(self, "Editar presupuesto", "No se pudo cargar el presupuesto seleccionado.")
            return

        cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado = presupuesto
        if not self.cargar_clientes_form(cliente_id):
            QMessageBox.warning(self, "Editar presupuesto", "No hay clientes disponibles para asignar.")
            return

        self.presupuesto_seleccionado = presupuesto_id
        self.label_form_titulo.setText("Editar presupuesto")
        self._cargar_formulario_desde_seleccion(presupuesto)
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def guardar_presupuesto(self):
        cliente_id = self._get_cliente_id_form()
        if cliente_id is None:
            QMessageBox.warning(self, "Guardar presupuesto", "Seleccione un cliente válido.")
            return

        moto_id = self._get_moto_id_form()
        if moto_id is None:
            QMessageBox.warning(self, "Guardar presupuesto", "Seleccione una moto válida.")
            return

        descripcion = self.input_descripcion.toPlainText().strip()
        if not descripcion:
            QMessageBox.warning(self, "Guardar presupuesto", "La descripción del trabajo es obligatoria.")
            return

        repuestos_val = self._parse_numero(self.input_repuestos.text())
        mano_obra_val = self._parse_numero(self.input_mano_obra.text())
        estado = self.combo_estado.currentText()
        total_val = repuestos_val + mano_obra_val
        reparacion_id = self._get_reparacion_id_form()

        if self.presupuesto_seleccionado is None:
            crear_presupuesto(cliente_id, moto_id, reparacion_id, descripcion, repuestos_val, mano_obra_val, total_val, estado)
            QMessageBox.information(self, "Presupuesto creado", "El presupuesto fue guardado correctamente.")
        else:
            actualizar_presupuesto(
                self.presupuesto_seleccionado,
                cliente_id,
                moto_id,
                reparacion_id,
                descripcion,
                repuestos_val,
                mano_obra_val,
                total_val,
                estado,
            )
            QMessageBox.information(self, "Presupuesto actualizado", "Los datos del presupuesto fueron actualizados.")

        self._seleccionar_cliente_en_lista(cliente_id)
        self.cargar_motos()
        self._seleccionar_moto_en_lista(moto_id)
        self.cargar_presupuestos()
        self.paginas.setCurrentWidget(self.pagina_lista)

    def cancelar_formulario(self):
        self.paginas.setCurrentWidget(self.pagina_lista)

    def generar_pdf_actual(self):
        presupuesto_id = self._get_presupuesto_seleccionado_id()
        if presupuesto_id is None:
            QMessageBox.warning(self, "Generar PDF", "Seleccione un presupuesto para exportar.")
            return

        presupuesto = obtener_presupuesto_por_id(presupuesto_id)
        if presupuesto is None:
            QMessageBox.warning(self, "Generar PDF", "No se pudo cargar el presupuesto seleccionado.")
            return

        cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado = presupuesto
        cliente = None
        for item in obtener_clientes():
            if item[0] == cliente_id:
                cliente = item
                break

        moto = None
        for item in obtener_motos(cliente_id):
            if item[0] == moto_id:
                moto = item
                break

        presupuesto_data = {
            'id': presupuesto_id,
            'fecha': None,
            'cliente_nombre': cliente[1] if cliente else '-',
            'cliente_telefono': cliente[2] if cliente else '-',
            'cliente_direccion': cliente[4] if cliente else '-',
            'moto_marca': moto[2] if moto else '-',
            'moto_modelo': moto[3] if moto else '-',
            'moto_patente': moto[5] if moto else '-',
            'moto_kilometros': moto[6] if moto else '-',
            'descripcion': descripcion or '-',
            'repuestos': f"${repuestos:.2f}" if repuestos is not None else '$0.00',
            'mano_obra': f"${mano_obra:.2f}" if mano_obra is not None else '$0.00',
            'total': total if total is not None else 0.0,
            'estado': estado or 'Pendiente',
        }

        ruta_pdf = generar_pdf_presupuesto(presupuesto_data)
        QMessageBox.information(self, "PDF generado", f"El presupuesto fue exportado correctamente en:\n{ruta_pdf}")

    def eliminar_presupuesto(self):
        presupuesto_id = self._get_presupuesto_seleccionado_id()
        if presupuesto_id is None:
            QMessageBox.warning(self, "Eliminar presupuesto", "Seleccione un presupuesto para eliminar.")
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar presupuesto",
            "¿Está seguro de que desea eliminar el presupuesto seleccionado?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if respuesta == QMessageBox.Yes:
            borrar_presupuesto(presupuesto_id)
            QMessageBox.information(self, "Presupuesto eliminado", "El presupuesto fue eliminado correctamente.")
            self.cargar_presupuestos()

    def enviar_presupuesto_whatsapp(self):
        presupuesto_id = self._get_presupuesto_seleccionado_id()
        if presupuesto_id is None:
            QMessageBox.warning(self, "WhatsApp", "Seleccione un presupuesto para enviarlo.")
            return

        presupuesto = obtener_presupuesto_por_id(presupuesto_id)
        if presupuesto is None:
            QMessageBox.warning(self, "WhatsApp", "No se pudo cargar el presupuesto seleccionado.")
            return

        cliente_id, moto_id, _, _, _, _, total, estado = presupuesto
        cliente, moto = obtener_contacto_cliente(cliente_id, moto_id)
        if cliente is None or not cliente[3]:
            QMessageBox.warning(self, "WhatsApp", "El cliente seleccionado no tiene un número de WhatsApp cargado.")
            return

        marca = moto[1] if moto else ""
        modelo = moto[2] if moto else ""
        total_formateado = f"{float(total or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        mensaje = (
            f"Hola {cliente[1]}, le enviamos el presupuesto para su moto {marca} {modelo}.\n"
            f"Total: $ {total_formateado}\n"
            f"Estado: {estado or 'Pendiente'}\n\nTaller de Motos"
        )
        if not abrir_whatsapp_web(cliente[3], mensaje):
            QMessageBox.warning(self, "WhatsApp", "No se pudo abrir WhatsApp Web.")

    def _seleccionar_presupuesto(self):
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
        self.cargar_reparaciones_form()
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
        self.cargar_reparaciones_form()

    def cargar_reparaciones_form(self):
        cliente_id = self._get_cliente_id_form()
        moto_id = self._get_moto_id_form()
        self.combo_reparaciones.clear()
        self.combo_reparaciones.addItem("Sin reparación relacionada", -1)

        if cliente_id is None or moto_id is None:
            return

        reparaciones = obtener_reparaciones(cliente_id, moto_id)
        for reparacion in reparaciones:
            reparacion_id = reparacion[0]
            descripcion = reparacion[3] if len(reparacion) > 3 else ""
            self.combo_reparaciones.addItem(f"{descripcion[:40]} ({reparacion_id})", reparacion_id)

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

    def _get_reparacion_id_form(self):
        indice = self.combo_reparaciones.currentIndex()
        if indice < 0:
            return None
        reparacion_id = self.combo_reparaciones.itemData(indice)
        return reparacion_id if reparacion_id != -1 else None

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

    def _limpiar_formulario(self):
        self.form_combo_motos.clear()
        self.combo_reparaciones.clear()
        self.input_descripcion.clear()
        self.input_repuestos.clear()
        self.input_mano_obra.clear()
        self.combo_estado.setCurrentIndex(0)
        self._actualizar_total()

    def _actualizar_total(self):
        repuestos_val = self._parse_numero(self.input_repuestos.text())
        mano_obra_val = self._parse_numero(self.input_mano_obra.text())
        total_val = repuestos_val + mano_obra_val
        self.label_total.setText(f"Total: ${total_val:.2f}")

    def _parse_numero(self, texto):
        texto = texto.strip().replace("$", "")
        try:
            return float(texto) if texto else 0.0
        except ValueError:
            return 0.0

    def _get_presupuesto_seleccionado_id(self):
        fila = self.tabla_presupuestos.currentRow()
        if fila < 0:
            return None

        item_id = self.tabla_presupuestos.item(fila, 0)
        if item_id is None:
            return None

        return int(item_id.text())

    def _cargar_formulario_desde_seleccion(self, presupuesto):
        cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado = presupuesto
        self.input_descripcion.setText(descripcion if descripcion is not None else "")
        self.input_repuestos.setText(f"{repuestos:.2f}" if repuestos is not None else "0.00")
        self.input_mano_obra.setText(f"{mano_obra:.2f}" if mano_obra is not None else "0.00")
        self.combo_estado.setCurrentText(estado if estado is not None else "Pendiente")

        self._seleccionar_form_combo(self.form_combo_clientes, cliente_id)
        self.cargar_motos_form()
        self._seleccionar_form_combo(self.form_combo_motos, moto_id)
        self.cargar_reparaciones_form()
        self._seleccionar_form_combo(self.combo_reparaciones, reparacion_id)
        self._actualizar_total()

    def _seleccionar_form_combo(self, combo, valor):
        for i in range(combo.count()):
            if combo.itemData(i) == valor:
                combo.setCurrentIndex(i)
                return
