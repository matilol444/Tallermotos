from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
    obtener_clientes,
    crear_cliente,
    actualizar_cliente,
    eliminar_cliente as eliminar_cliente_db
)
from ui.estilo_visual import aplicar_estilo_moderno


class ClientesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cliente_id_seleccionado = None
        self._init_ui()
        QTimer.singleShot(0, self.refrescar)

    def refrescar(self):
        self.cargar_clientes()

    def showEvent(self, event):
        self.refrescar()
        super().showEvent(event)

    def _init_ui(self):
        self.setWindowTitle("Clientes")

        self.paginas = QStackedWidget()

        # Página de lista
        pagina_lista = QWidget()
        lista_layout = QVBoxLayout(pagina_lista)

        titulo = QLabel("Clientes")
        titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        boton_nuevo = QPushButton("Nuevo cliente")
        boton_editar = QPushButton("Editar cliente")
        boton_eliminar = QPushButton("Eliminar cliente")

        boton_nuevo.clicked.connect(self.nuevo_cliente)
        boton_editar.clicked.connect(self.editar_cliente)
        boton_eliminar.clicked.connect(self.eliminar_cliente)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(boton_nuevo)
        botones_layout.addWidget(boton_editar)
        botones_layout.addWidget(boton_eliminar)
        botones_layout.addStretch()

        self.tabla_clientes = QTableWidget(0, 5)
        self.tabla_clientes.setHorizontalHeaderLabels([
            "ID",
            "Nombre",
            "Teléfono",
            "WhatsApp",
            "Dirección"
        ])
        self.tabla_clientes.verticalHeader().setVisible(False)
        self.tabla_clientes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_clientes.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_clientes.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tabla_clientes.itemSelectionChanged.connect(self._seleccionar_cliente)

        lista_layout.addWidget(titulo)
        lista_layout.addLayout(botones_layout)
        lista_layout.addWidget(self.tabla_clientes)

        self.pagina_lista = pagina_lista

        # Página de formulario
        pagina_formulario = QWidget()
        formulario_layout = QVBoxLayout(pagina_formulario)

        self.label_form_titulo = QLabel("Nuevo cliente")
        self.label_form_titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        self.input_nombre = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_whatsapp = QLineEdit()
        self.input_direccion = QLineEdit()

        self.input_nombre.setPlaceholderText("Nombre completo")
        self.input_telefono.setPlaceholderText("Teléfono")
        self.input_whatsapp.setPlaceholderText("WhatsApp")
        self.input_direccion.setPlaceholderText("Dirección")

        form_layout = QVBoxLayout()
        form_layout.addLayout(self._crear_campo("Nombre:", self.input_nombre))
        form_layout.addLayout(self._crear_campo("Teléfono:", self.input_telefono))
        form_layout.addLayout(self._crear_campo("WhatsApp:", self.input_whatsapp))
        form_layout.addLayout(self._crear_campo("Dirección:", self.input_direccion))

        boton_guardar = QPushButton("Guardar cliente")
        boton_cancelar = QPushButton("Cancelar")
        boton_guardar.clicked.connect(self.guardar_cliente)
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
        clientes = obtener_clientes()
        self.tabla_clientes.setRowCount(0)

        for cliente in clientes:
            fila = self.tabla_clientes.rowCount()
            self.tabla_clientes.insertRow(fila)
            for columna, valor in enumerate(cliente):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                if columna == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_clientes.setItem(fila, columna, item)

        self.tabla_clientes.clearSelection()
        self.cliente_id_seleccionado = None

    def nuevo_cliente(self):
        self.cliente_id_seleccionado = None
        self._limpiar_formulario()
        self._mostrar_formulario("create")

    def editar_cliente(self):
        cliente_id = self._get_cliente_seleccionado_id()
        if cliente_id is None:
            QMessageBox.warning(self, "Editar cliente", "Seleccione un cliente para editar.")
            return

        self.cliente_id_seleccionado = cliente_id
        self._cargar_formulario_desde_seleccion()
        self._mostrar_formulario("edit")

    def guardar_cliente(self):
        nombre = self.input_nombre.text().strip()
        telefono = self.input_telefono.text().strip()
        whatsapp = self.input_whatsapp.text().strip()
        direccion = self.input_direccion.text().strip()

        if not nombre:
            QMessageBox.warning(self, "Guardar cliente", "El nombre es obligatorio.")
            return

        if getattr(self, "form_mode", "create") == "create":
            crear_cliente(nombre, telefono, whatsapp, direccion)
            QMessageBox.information(self, "Cliente creado", "El cliente fue guardado correctamente.")
        else:
            actualizar_cliente(
                self.cliente_id_seleccionado,
                nombre,
                telefono,
                whatsapp,
                direccion
            )
            QMessageBox.information(self, "Cliente actualizado", "Los datos del cliente fueron actualizados.")

        self.cargar_clientes()
        self._mostrar_lista()

    def cancelar_formulario(self):
        self._mostrar_lista()

    def eliminar_cliente(self):
        cliente_id = self._get_cliente_seleccionado_id()
        if cliente_id is None:
            QMessageBox.warning(self, "Eliminar cliente", "Seleccione un cliente para eliminar.")
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar cliente",
            "¿Está seguro de que desea eliminar el cliente seleccionado?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            eliminar_cliente_db(cliente_id)
            QMessageBox.information(self, "Cliente eliminado", "El cliente fue eliminado correctamente.")
            self.cargar_clientes()

    def _seleccionar_cliente(self):
        pass

    def _mostrar_formulario(self, mode):
        self.form_mode = mode
        if mode == "create":
            self.label_form_titulo.setText("Nuevo cliente")
            self._limpiar_formulario()
        else:
            self.label_form_titulo.setText("Editar cliente")
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def _mostrar_lista(self):
        self.paginas.setCurrentWidget(self.pagina_lista)

    def _limpiar_formulario(self):
        self.input_nombre.clear()
        self.input_telefono.clear()
        self.input_whatsapp.clear()
        self.input_direccion.clear()

    def _get_cliente_seleccionado_id(self):
        fila = self.tabla_clientes.currentRow()
        if fila < 0:
            return None

        item_id = self.tabla_clientes.item(fila, 0)
        if item_id is None:
            return None

        return int(item_id.text())

    def _cargar_formulario_desde_seleccion(self):
        fila = self.tabla_clientes.currentRow()
        if fila < 0:
            return

        self.cliente_id_seleccionado = self._get_cliente_seleccionado_id()
        self.input_nombre.setText(self.tabla_clientes.item(fila, 1).text())
        self.input_telefono.setText(self.tabla_clientes.item(fila, 2).text())
        self.input_whatsapp.setText(self.tabla_clientes.item(fila, 3).text())
        self.input_direccion.setText(self.tabla_clientes.item(fila, 4).text())
