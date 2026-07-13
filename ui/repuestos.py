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
    QAbstractItemView,
    QStackedWidget,
)
from PySide6.QtCore import Qt, QTimer

from database.database import (
    obtener_repuestos,
    obtener_repuesto_por_id,
    crear_repuesto,
    actualizar_repuesto,
    borrar_repuesto,
)
from ui.estilo_visual import aplicar_estilo_moderno


class RepuestosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.repuesto_seleccionado = None
        self._init_ui()
        QTimer.singleShot(0, self.refrescar)

    def refrescar(self):
        self.cargar_repuestos()

    def showEvent(self, event):
        self.refrescar()
        super().showEvent(event)

    def _init_ui(self):
        self.setWindowTitle("Repuestos")

        self.paginas = QStackedWidget()

        pagina_lista = QWidget()
        lista_layout = QVBoxLayout(pagina_lista)

        titulo = QLabel("Repuestos")
        titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        boton_nuevo = QPushButton("Nuevo repuesto")
        boton_editar = QPushButton("Editar repuesto")
        boton_eliminar = QPushButton("Eliminar repuesto")

        boton_nuevo.clicked.connect(self.nuevo_repuesto)
        boton_editar.clicked.connect(self.editar_repuesto)
        boton_eliminar.clicked.connect(self.eliminar_repuesto)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(boton_nuevo)
        botones_layout.addWidget(boton_editar)
        botones_layout.addWidget(boton_eliminar)
        botones_layout.addStretch()

        self.tabla_repuestos = QTableWidget(0, 7)
        self.tabla_repuestos.setHorizontalHeaderLabels([
            "ID",
            "Nombre",
            "Código",
            "Marca",
            "Stock",
            "Precio compra",
            "Precio venta",
        ])
        self.tabla_repuestos.verticalHeader().setVisible(False)
        self.tabla_repuestos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_repuestos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_repuestos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_repuestos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_repuestos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_repuestos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla_repuestos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_repuestos.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabla_repuestos.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tabla_repuestos.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tabla_repuestos.itemSelectionChanged.connect(self._seleccionar_repuesto)

        lista_layout.addWidget(titulo)
        lista_layout.addLayout(botones_layout)
        lista_layout.addWidget(self.tabla_repuestos)

        self.pagina_lista = pagina_lista

        pagina_formulario = QWidget()
        formulario_layout = QVBoxLayout(pagina_formulario)

        self.label_form_titulo = QLabel("Nuevo repuesto")
        self.label_form_titulo.setStyleSheet("font-size:24px;font-weight:bold; margin-bottom:16px;")

        self.input_nombre = QLineEdit()
        self.input_codigo = QLineEdit()
        self.input_marca = QLineEdit()
        self.input_stock = QLineEdit()
        self.input_precio_compra = QLineEdit()
        self.input_precio_venta = QLineEdit()

        self.input_nombre.setPlaceholderText("Nombre")
        self.input_codigo.setPlaceholderText("Código")
        self.input_marca.setPlaceholderText("Marca")
        self.input_stock.setPlaceholderText("Stock")
        self.input_precio_compra.setPlaceholderText("Precio compra")
        self.input_precio_venta.setPlaceholderText("Precio venta")

        form_layout = QVBoxLayout()
        form_layout.addLayout(self._crear_campo("Nombre:", self.input_nombre))
        form_layout.addLayout(self._crear_campo("Código:", self.input_codigo))
        form_layout.addLayout(self._crear_campo("Marca:", self.input_marca))
        form_layout.addLayout(self._crear_campo("Stock:", self.input_stock))
        form_layout.addLayout(self._crear_campo("Precio compra:", self.input_precio_compra))
        form_layout.addLayout(self._crear_campo("Precio venta:", self.input_precio_venta))

        boton_guardar = QPushButton("Guardar repuesto")
        boton_cancelar = QPushButton("Cancelar")
        boton_guardar.clicked.connect(self.guardar_repuesto)
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

    def cargar_repuestos(self):
        self.tabla_repuestos.setRowCount(0)
        repuestos = obtener_repuestos()

        for repuesto in repuestos:
            fila = self.tabla_repuestos.rowCount()
            self.tabla_repuestos.insertRow(fila)
            for columna, valor in enumerate(repuesto):
                texto = ""
                if valor is not None:
                    if isinstance(valor, float):
                        texto = f"{valor:.2f}"
                    else:
                        texto = str(valor)
                item = QTableWidgetItem(texto)
                if columna == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_repuestos.setItem(fila, columna, item)

        self.tabla_repuestos.clearSelection()
        self.repuesto_seleccionado = None

    def nuevo_repuesto(self):
        self.repuesto_seleccionado = None
        self.label_form_titulo.setText("Nuevo repuesto")
        self._limpiar_formulario()
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def editar_repuesto(self):
        repuesto_id = self._get_repuesto_seleccionado_id()
        if repuesto_id is None:
            QMessageBox.warning(self, "Editar repuesto", "Seleccione un repuesto para editar.")
            return

        repuesto = obtener_repuesto_por_id(repuesto_id)
        if repuesto is None:
            QMessageBox.warning(self, "Editar repuesto", "No se pudo cargar el repuesto seleccionado.")
            return

        self.repuesto_seleccionado = repuesto_id
        self.label_form_titulo.setText("Editar repuesto")
        self._cargar_formulario_desde_seleccion(repuesto)
        self.paginas.setCurrentWidget(self.pagina_formulario)

    def guardar_repuesto(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Guardar repuesto", "El nombre es obligatorio.")
            return

        codigo = self.input_codigo.text().strip()
        marca = self.input_marca.text().strip()
        stock_texto = self.input_stock.text().strip()
        precio_compra_texto = self.input_precio_compra.text().strip()
        precio_venta_texto = self.input_precio_venta.text().strip()

        try:
            stock = int(stock_texto) if stock_texto else 0
        except ValueError:
            QMessageBox.warning(self, "Guardar repuesto", "El stock debe ser un número entero.")
            return

        try:
            precio_compra = float(precio_compra_texto) if precio_compra_texto else None
        except ValueError:
            QMessageBox.warning(self, "Guardar repuesto", "El precio de compra debe ser un número válido.")
            return

        try:
            precio_venta = float(precio_venta_texto) if precio_venta_texto else None
        except ValueError:
            QMessageBox.warning(self, "Guardar repuesto", "El precio de venta debe ser un número válido.")
            return

        if self.repuesto_seleccionado is None:
            crear_repuesto(nombre, codigo, marca, stock, precio_compra, precio_venta)
            QMessageBox.information(self, "Repuesto creado", "El repuesto fue guardado correctamente.")
        else:
            actualizar_repuesto(self.repuesto_seleccionado, nombre, codigo, marca, stock, precio_compra, precio_venta)
            QMessageBox.information(self, "Repuesto actualizado", "El repuesto fue actualizado correctamente.")

        self.cargar_repuestos()
        self.paginas.setCurrentWidget(self.pagina_lista)

    def cancelar_formulario(self):
        self.paginas.setCurrentWidget(self.pagina_lista)

    def eliminar_repuesto(self):
        repuesto_id = self._get_repuesto_seleccionado_id()
        if repuesto_id is None:
            QMessageBox.warning(self, "Eliminar repuesto", "Seleccione un repuesto para eliminar.")
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar repuesto",
            "¿Está seguro de que desea eliminar el repuesto seleccionado?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if respuesta == QMessageBox.Yes:
            borrar_repuesto(repuesto_id)
            QMessageBox.information(self, "Repuesto eliminado", "El repuesto fue eliminado correctamente.")
            self.cargar_repuestos()

    def _seleccionar_repuesto(self):
        pass

    def _limpiar_formulario(self):
        self.input_nombre.clear()
        self.input_codigo.clear()
        self.input_marca.clear()
        self.input_stock.clear()
        self.input_precio_compra.clear()
        self.input_precio_venta.clear()

    def _cargar_formulario_desde_seleccion(self, repuesto):
        _, nombre, codigo, marca, stock, precio_compra, precio_venta = repuesto
        self.input_nombre.setText(nombre if nombre is not None else "")
        self.input_codigo.setText(codigo if codigo is not None else "")
        self.input_marca.setText(marca if marca is not None else "")
        self.input_stock.setText(str(stock) if stock is not None else "")
        self.input_precio_compra.setText(str(precio_compra) if precio_compra is not None else "")
        self.input_precio_venta.setText(str(precio_venta) if precio_venta is not None else "")

    def _get_repuesto_seleccionado_id(self):
        fila = self.tabla_repuestos.currentRow()
        if fila < 0:
            return None

        item_id = self.tabla_repuestos.item(fila, 0)
        if item_id is None:
            return None

        return int(item_id.text())
