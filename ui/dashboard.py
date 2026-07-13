from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.database import conectar


UMBRAL_STOCK_BAJO = 5


class TarjetaIndicador(QFrame):
    def __init__(self, titulo, icono, color):
        super().__init__()
        self.setObjectName("tarjetaIndicador")
        self.setStyleSheet(
            "QFrame#tarjetaIndicador {"
            "background-color: #2f3136; border: 1px solid #3a3d44; "
            "border-left: 4px solid " + color + "; border-radius: 10px;"
            "}"
        )
        self.setMinimumHeight(104)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(3)

        encabezado = QHBoxLayout()
        etiqueta_titulo = QLabel(f"{icono}  {titulo}")
        etiqueta_titulo.setStyleSheet("color: #b9bbbe; font-size: 13px;")
        encabezado.addWidget(etiqueta_titulo)
        encabezado.addStretch()

        self.valor = QLabel("0")
        self.valor.setStyleSheet("font-size: 30px; font-weight: bold; color: white;")

        layout.addLayout(encabezado)
        layout.addWidget(self.valor)

    def actualizar(self, valor):
        self.valor.setText(str(valor))


class DashboardWidget(QWidget):
    """Resumen de la operación del taller, leído directamente desde SQLite."""

    def __init__(self):
        super().__init__()
        self._crear_interfaz()
        self.refrescar()

    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        cabecera = QHBoxLayout()
        textos = QVBoxLayout()
        titulo = QLabel("Dashboard")
        titulo.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        subtitulo = QLabel("Resumen de la actividad del taller")
        subtitulo.setStyleSheet("font-size: 14px; color: #b9bbbe;")
        textos.addWidget(titulo)
        textos.addWidget(subtitulo)
        cabecera.addLayout(textos)
        cabecera.addStretch()
        self.etiqueta_fecha = QLabel()
        self.etiqueta_fecha.setStyleSheet("color: #b9bbbe; font-size: 13px;")
        cabecera.addWidget(self.etiqueta_fecha, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addLayout(cabecera)

        grilla = QGridLayout()
        grilla.setHorizontalSpacing(14)
        grilla.setVerticalSpacing(14)
        definiciones = [
            ("Clientes registrados", "👤", "#5865f2"),
            ("Motos registradas", "🏍", "#57f287"),
            ("Turnos para hoy", "📅", "#faa61a"),
            ("Reparaciones pendientes", "⏳", "#ed4245"),
            ("Reparaciones en proceso", "🔧", "#3498db"),
            ("Presupuestos pendientes", "💰", "#9b59b6"),
            ("Repuestos con poco stock", "📦", "#e67e22"),
        ]
        self.tarjetas = {}
        for indice, (nombre, icono, color) in enumerate(definiciones):
            tarjeta = TarjetaIndicador(nombre, icono, color)
            self.tarjetas[nombre] = tarjeta
            grilla.addWidget(tarjeta, indice // 3, indice % 3)

        # Equilibra la última fila, que contiene una tarjeta adicional.
        grilla.setColumnStretch(0, 1)
        grilla.setColumnStretch(1, 1)
        grilla.setColumnStretch(2, 1)
        layout.addLayout(grilla)

        actividad = QLabel("Actividad reciente")
        actividad.setStyleSheet("font-size: 19px; font-weight: bold; color: white; margin-top: 4px;")
        layout.addWidget(actividad)

        tablas = QHBoxLayout()
        tablas.setSpacing(14)
        self.tabla_reparaciones = self._crear_tabla(
            "Últimas reparaciones creadas", ["Cliente", "Moto", "Problema", "Estado", "Ingreso"]
        )
        self.tabla_clientes = self._crear_tabla(
            "Últimos clientes agregados", ["Cliente", "Teléfono", "WhatsApp"]
        )
        tablas.addWidget(self.tabla_reparaciones, 3)
        tablas.addWidget(self.tabla_clientes, 2)
        layout.addLayout(tablas, 1)

    def _crear_tabla(self, titulo, columnas):
        contenedor = QFrame()
        contenedor.setObjectName("panelActividad")
        contenedor.setStyleSheet(
            "QFrame#panelActividad { background-color: #2f3136; border: 1px solid #3a3d44; border-radius: 10px; }"
            "QTableWidget { background-color: #2f3136; border: none; gridline-color: #3a3d44; }"
            "QTableWidget::item { padding: 5px; }"
            "QHeaderView::section { background-color: #292b2f; border: none; border-bottom: 1px solid #3a3d44; padding: 7px; color: #b9bbbe; font-weight: bold; }"
        )
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(12, 10, 12, 12)
        etiqueta = QLabel(titulo)
        etiqueta.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        tabla = QTableWidget(0, len(columnas))
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabla.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        tabla.setFocusPolicy(Qt.NoFocus)
        tabla.verticalHeader().setVisible(False)
        tabla.horizontalHeader().setStretchLastSection(True)
        for columna in range(len(columnas) - 1):
            tabla.horizontalHeader().setSectionResizeMode(columna, QHeaderView.ResizeMode.Stretch)
        tabla.setMinimumHeight(175)
        layout.addWidget(etiqueta)
        layout.addWidget(tabla)
        contenedor.tabla = tabla
        return contenedor

    def refrescar(self):
        """Actualiza las métricas al abrir la aplicación o volver a Inicio."""
        hoy = date.today().isoformat()
        self.etiqueta_fecha.setText(f"Hoy: {date.today().strftime('%d/%m/%Y')}")

        conexion = conectar()
        try:
            cursor = conexion.cursor()
            metricas = {
                "Clientes registrados": self._contar(cursor, "SELECT COUNT(*) FROM clientes"),
                "Motos registradas": self._contar(cursor, "SELECT COUNT(*) FROM motos"),
                "Turnos para hoy": self._contar(cursor, "SELECT COUNT(*) FROM turnos WHERE fecha = ?", (hoy,)),
                "Reparaciones pendientes": self._contar(cursor, "SELECT COUNT(*) FROM reparaciones WHERE estado = 'Pendiente'"),
                "Reparaciones en proceso": self._contar(cursor, "SELECT COUNT(*) FROM reparaciones WHERE estado = 'En reparación'"),
                "Presupuestos pendientes": self._contar(cursor, "SELECT COUNT(*) FROM presupuestos WHERE estado = 'Pendiente'"),
                "Repuestos con poco stock": self._contar(cursor, "SELECT COUNT(*) FROM repuestos WHERE COALESCE(stock, 0) <= ?", (UMBRAL_STOCK_BAJO,)),
            }
            for nombre, cantidad in metricas.items():
                self.tarjetas[nombre].actualizar(cantidad)

            cursor.execute(
                "SELECT COALESCE(c.nombre, 'Sin cliente'), "
                "COALESCE(TRIM(m.marca || ' ' || m.modelo), 'Sin moto'), "
                "COALESCE(r.problema, '-'), COALESCE(r.estado, '-'), COALESCE(r.fecha_ingreso, '-') "
                "FROM reparaciones r "
                "LEFT JOIN clientes c ON c.id = r.cliente_id "
                "LEFT JOIN motos m ON m.id = r.moto_id "
                "ORDER BY r.id DESC LIMIT 5"
            )
            self._cargar_filas(self.tabla_reparaciones.tabla, cursor.fetchall())

            # La tabla no guarda fecha de alta; el ID autoincremental indica el orden de creación.
            cursor.execute(
                "SELECT nombre, COALESCE(telefono, '-'), COALESCE(whatsapp, '-') "
                "FROM clientes ORDER BY id DESC LIMIT 5"
            )
            self._cargar_filas(self.tabla_clientes.tabla, cursor.fetchall())
        finally:
            conexion.close()

    @staticmethod
    def _contar(cursor, consulta, parametros=()):
        cursor.execute(consulta, parametros)
        return cursor.fetchone()[0]

    @staticmethod
    def _cargar_filas(tabla, filas):
        tabla.setRowCount(0)
        for fila_datos in filas:
            fila = tabla.rowCount()
            tabla.insertRow(fila)
            for columna, valor in enumerate(fila_datos):
                item = QTableWidgetItem(str(valor) if valor is not None else "-")
                item.setToolTip(item.text())
                tabla.setItem(fila, columna, item)
