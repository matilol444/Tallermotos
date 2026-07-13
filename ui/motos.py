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
    QStackedWidget
)
from PySide6.QtCore import Qt, QTimer

from database.database import (
    conectar,
    obtener_clientes,
    obtener_motos,
    obtener_moto_por_id,
    crear_moto,
    actualizar_moto,
    borrar_moto,
)
from ui.estilo_visual import aplicar_estilo_moderno


class MotosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.moto_id_seleccionada = None
        self._init_ui()
        QTimer.singleShot(0, self.refrescar)

    def refrescar(self):
        self.cargar_clientes()
        self.cargar_motos()

    def showEvent(self, event):
        self.refrescar()
        super().showEvent(event)

    def _init_ui(self):
        self.setWindowTitle("Motos")

        self.paginas = QStackedWidget()

        # Página de lista de motos
        pagina_lista = QWidget()
        lista_layout = QVBoxLayout(pagina_lista)

        titulo = QLabel("Motos")
        titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        cliente_layout = QHBoxLayout()
        label_cliente = QLabel("Cliente:")
        label_cliente.setFixedWidth(90)
        self.combo_clientes = QComboBox()
        self.combo_clientes.currentIndexChanged.connect(self.cargar_motos)
        cliente_layout.addWidget(label_cliente)
        cliente_layout.addWidget(self.combo_clientes)

        boton_nuevo = QPushButton("Nueva moto")
        boton_editar = QPushButton("Editar moto")
        boton_eliminar = QPushButton("Eliminar moto")

        boton_nuevo.clicked.connect(self.nueva_moto)
        boton_editar.clicked.connect(self.editar_moto)
        boton_eliminar.clicked.connect(self.eliminar_moto)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(boton_nuevo)
        botones_layout.addWidget(boton_editar)
        botones_layout.addWidget(boton_eliminar)
        botones_layout.addStretch()

        self.tabla_motos = QTableWidget(0, 6)
        self.tabla_motos.setHorizontalHeaderLabels([
            "ID",
            "Marca",
            "Modelo",
            "Año",
            "Patente",
            "Kilómetros"
        ])
        self.tabla_motos.verticalHeader().setVisible(False)
        self.tabla_motos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_motos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_motos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_motos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_motos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_motos.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_motos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla_motos.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabla_motos.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabla_motos.itemSelectionChanged.connect(self._seleccionar_moto)

        lista_layout.addWidget(titulo)
        lista_layout.addLayout(cliente_layout)
        lista_layout.addLayout(botones_layout)
        lista_layout.addWidget(self.tabla_motos)

        self.pagina_lista = pagina_lista

        # Página de formulario de moto
        pagina_formulario = QWidget()
        formulario_layout = QVBoxLayout(pagina_formulario)

        self.label_form_titulo = QLabel("Nueva moto")
        self.label_form_titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        self.combo_cliente_form = QComboBox()
        self.combo_cliente_form.setMinimumWidth(200)

        self.input_marca = QLineEdit()
        self.input_modelo = QLineEdit()
        self.input_ano = QLineEdit()
        self.input_patente = QLineEdit()
        self.input_kilometros = QLineEdit()
        self.input_notas = QTextEdit()

        self.input_marca.setPlaceholderText("Marca")
        self.input_modelo.setPlaceholderText("Modelo")
        self.input_ano.setPlaceholderText("Año")
        self.input_patente.setPlaceholderText("Patente")
        self.input_kilometros.setPlaceholderText("Kilómetros")
        self.input_notas.setPlaceholderText("Notas")
        self.input_notas.setFixedHeight(120)

        form_layout = QVBoxLayout()
        form_layout.addLayout(self._crear_campo("Cliente:", self.combo_cliente_form))
        form_layout.addLayout(self._crear_campo("Marca:", self.input_marca))
        form_layout.addLayout(self._crear_campo("Modelo:", self.input_modelo))
        form_layout.addLayout(self._crear_campo("Año:", self.input_ano))
        form_layout.addLayout(self._crear_campo("Patente:", self.input_patente))
        form_layout.addLayout(self._crear_campo("Kilómetros:", self.input_kilometros))
        form_layout.addWidget(QLabel("Notas:"))
        form_layout.addWidget(self.input_notas)

        boton_guardar = QPushButton("Guardar moto")
        boton_cancelar = QPushButton("Cancelar")
        boton_guardar.clicked.connect(self.guardar_moto)
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
            self.tabla_motos.setRowCount(0)
            self.combo_clientes.blockSignals(False)
            self.cargar_motos()
            return

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
        else:
            self.combo_clientes.setCurrentIndex(0)

        self.combo_clientes.blockSignals(False)
        self.cargar_motos()

    def cargar_motos(self):
        cliente_id = self._get_cliente_id_seleccionado()
        self.tabla_motos.setRowCount(0)

        if cliente_id is None:
            return

        motos = obtener_motos(cliente_id)
        for moto in motos:
            fila = self.tabla_motos.rowCount()
            self.tabla_motos.insertRow(fila)
            moto_datos = [moto[0], moto[2], moto[3], moto[4], moto[5], moto[6]]
            for columna, valor in enumerate(moto_datos):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                if columna == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_motos.setItem(fila, columna, item)

        self.tabla_motos.clearSelection()
        self.moto_id_seleccionada = None

    def nueva_moto(self):
        cliente_id = self._get_cliente_id_seleccionado()
        if not self.cargar_clientes_form(cliente_id):
            QMessageBox.warning(self, "Nueva moto", "No hay clientes disponibles para asignar.")
            return

        self.moto_id_seleccionada = None
        self.form_mode = "create"
        self.label_form_titulo.setText("Nueva moto")
        self._limpiar_formulario()
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def editar_moto(self):
        moto_id = self._get_moto_seleccionada_id()
        if moto_id is None:
            QMessageBox.warning(self, "Editar moto", "Seleccione una moto para editar.")
            return

        moto = obtener_moto_por_id(moto_id)
        if moto is None:
            QMessageBox.warning(self, "Editar moto", "No se pudo cargar la moto seleccionada.")
            return

        cliente_id = moto[0]
        if not self.cargar_clientes_form(cliente_id):
            QMessageBox.warning(self, "Editar moto", "No hay clientes disponibles para asignar.")
            return

        self.moto_id_seleccionada = moto_id
        self.form_mode = "edit"
        self.label_form_titulo.setText("Editar moto")
        self._cargar_formulario_desde_seleccion()
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def guardar_moto(self):
        cliente_id = self._get_cliente_id_form()
        if cliente_id is None:
            QMessageBox.warning(self, "Guardar moto", "Seleccione un cliente válido.")
            return

        marca = self.input_marca.text().strip()
        modelo = self.input_modelo.text().strip()
        ano = self.input_ano.text().strip()
        patente = self.input_patente.text().strip()
        kilometros = self.input_kilometros.text().strip()
        notas = self.input_notas.toPlainText().strip()

        if not marca or not modelo:
            QMessageBox.warning(self, "Guardar moto", "La marca y el modelo son obligatorios.")
            return

        try:
            ano_val = int(ano) if ano else None
        except ValueError:
            QMessageBox.warning(self, "Guardar moto", "El año debe ser un número válido.")
            return

        try:
            kilometros_val = int(kilometros) if kilometros else None
        except ValueError:
            QMessageBox.warning(self, "Guardar moto", "Los kilómetros deben ser un número válido.")
            return

        if self.moto_id_seleccionada is None:
            crear_moto(cliente_id, marca, modelo, ano_val, patente, kilometros_val)
            QMessageBox.information(self, "Moto creada", "La moto fue guardada correctamente.")
        else:
            actualizar_moto(self.moto_id_seleccionada, cliente_id, marca, modelo, ano_val, patente, kilometros_val)
            QMessageBox.information(self, "Moto actualizada", "Los datos de la moto fueron actualizados.")

        self.cargar_motos()
        self.paginas.setCurrentWidget(self.pagina_lista)

    def cancelar_formulario(self):
        self.paginas.setCurrentWidget(self.pagina_lista)

    def eliminar_moto(self):
        moto_id = self._get_moto_seleccionada_id()
        if moto_id is None:
            QMessageBox.warning(self, "Eliminar moto", "Seleccione una moto para eliminar.")
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar moto",
            "¿Está seguro de que desea eliminar la moto seleccionada?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            borrar_moto(moto_id)
            QMessageBox.information(self, "Moto eliminada", "La moto fue eliminada correctamente.")
            self.cargar_motos()

    def _seleccionar_moto(self):
        pass

    def _get_cliente_id_seleccionado(self):
        indice = self.combo_clientes.currentIndex()
        if indice < 0:
            return None
        cliente_id = self.combo_clientes.itemData(indice)
        return cliente_id if cliente_id != -1 else None

    def cargar_clientes_form(self, selected_cliente_id=None):
        self.combo_cliente_form.clear()
        clientes = obtener_clientes()

        if not clientes:
            self.combo_cliente_form.addItem("No hay clientes", -1)
            return False

        selected_index = 0
        for i, cliente in enumerate(clientes):
            cliente_id, nombre, telefono, whatsapp, direccion = cliente
            self.combo_cliente_form.addItem(f"{nombre} ({cliente_id})", cliente_id)
            if cliente_id == selected_cliente_id:
                selected_index = i

        self.combo_cliente_form.setCurrentIndex(selected_index)
        return True

    def _get_cliente_id_form(self):
        indice = self.combo_cliente_form.currentIndex()
        if indice < 0:
            return None
        cliente_id = self.combo_cliente_form.itemData(indice)
        return cliente_id if cliente_id != -1 else None

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
        self.input_marca.clear()
        self.input_modelo.clear()
        self.input_ano.clear()
        self.input_patente.clear()
        self.input_kilometros.clear()
        self.input_notas.clear()

    def _get_moto_seleccionada_id(self):
        fila = self.tabla_motos.currentRow()
        if fila < 0:
            return None

        item_id = self.tabla_motos.item(fila, 0)
        if item_id is None:
            return None

        return int(item_id.text())

    def _cargar_formulario_desde_seleccion(self):
        fila = self.tabla_motos.currentRow()
        if fila < 0:
            return

        self.moto_id_seleccionada = self._get_moto_seleccionada_id()
        self.input_marca.setText(self.tabla_motos.item(fila, 1).text())
        self.input_modelo.setText(self.tabla_motos.item(fila, 2).text())
        self.input_ano.setText(self.tabla_motos.item(fila, 3).text())
        self.input_patente.setText(self.tabla_motos.item(fila, 4).text())
        self.input_kilometros.setText(self.tabla_motos.item(fila, 5).text())
