import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget
)
from PySide6.QtCore import Qt

from database.database import crear_tablas
from ui.clientes import ClientesWidget
from ui.motos import MotosWidget
from ui.turnos import TurnosWidget
from ui.reparaciones import ReparacionesWidget
from ui.presupuestos import PresupuestosWidget
from ui.repuestos import RepuestosWidget
from ui.historial import HistorialWidget
from ui.dashboard import DashboardWidget
from ui.configuracion import ConfiguracionWidget
from ui.login import LoginDialog
from ui.caja import CajaWidget


class VentanaPrincipal(QMainWindow):
    PERMISOS_POR_ROL = {
        "Administrador": set(range(10)),
        "Dueño": set(range(10)),
        "Recepción": {1, 2, 3, 5},
        "Mecánico": {2, 4, 7},
    }

    def __init__(self, usuario_activo):
        super().__init__()
        self.usuario_activo = usuario_activo

        self.setWindowTitle("Taller de Motos")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        # Menú lateral
        menu = QVBoxLayout()

        titulo = QLabel("🏍 Taller")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:22px;font-weight:bold;color:white;")

        menu.addWidget(titulo)

        usuario = QLabel(f"Conectado: {self.usuario_activo['usuario']}\n{self.usuario_activo['rol']}")
        usuario.setAlignment(Qt.AlignCenter)
        usuario.setStyleSheet("color:#b9bbbe; font-size:13px; padding:8px 0 14px;")
        menu.addWidget(usuario)

        botones = [
            ("🏠 Inicio", 0),
            ("👤 Clientes", 1),
            ("🏍 Motos", 2),
            ("📅 Turnos", 3),
            ("🔧 Reparaciones", 4),
            ("💰 Presupuestos", 5),
            ("🧰 Repuestos", 6),
            ("📜 Historial", 7),
            ("⚙ Configuración", 8),
            ("💳 Caja", 9),
        ]

        permitidos = self.PERMISOS_POR_ROL.get(self.usuario_activo["rol"], set())

        for texto, indice in botones:
            boton = QPushButton(texto)
            boton.setMinimumHeight(45)
            if indice in permitidos:
                menu.addWidget(boton)
                boton.clicked.connect(lambda checked=False, idx=indice: self.paneles.setCurrentIndex(idx))

        menu.addStretch()

        menu_widget = QWidget()
        menu_widget.setLayout(menu)
        menu_widget.setFixedWidth(250)

        # Panel principal con cambio de pantallas
        self.paneles = QStackedWidget()

        self.paneles.addWidget(DashboardWidget())
        self.paneles.addWidget(ClientesWidget())
        self.motos_widget = MotosWidget()
        self.paneles.addWidget(self.motos_widget)
        self.paneles.addWidget(TurnosWidget())
        self.paneles.addWidget(ReparacionesWidget())
        self.paneles.addWidget(PresupuestosWidget())
        self.paneles.addWidget(RepuestosWidget())
        self.paneles.addWidget(HistorialWidget())
        self.paneles.addWidget(ConfiguracionWidget())
        self.paneles.addWidget(CajaWidget())

        if self.usuario_activo["rol"] == "Mecánico":
            self._configurar_motos_solo_consulta()

        self.paneles.currentChanged.connect(self._refrescar_widget_actual)
        indice_inicial = min(permitidos) if permitidos else 0
        self.paneles.setCurrentIndex(indice_inicial)
        self._refrescar_widget_actual(indice_inicial)

        layout.addWidget(menu_widget)
        layout.addWidget(self.paneles)

        self.setStyleSheet("""
            QMainWindow{
                background:#202225;
            }

            QWidget{
                background:#202225;
                color:white;
            }

            QPushButton{
                background:#2f3136;
                border:none;
                border-radius:8px;
                padding:10px;
                text-align:left;
                font-size:16px;
            }

            QPushButton:hover{
                background:#5865F2;
            }
        """)

    def _refrescar_widget_actual(self, index=None):
        widget = self.paneles.currentWidget()
        if widget is None:
            return

        refrescar = getattr(widget, "refrescar", None)
        if callable(refrescar):
            refrescar()

    def _configurar_motos_solo_consulta(self):
        """Restringe la pantalla existente de Motos a lectura para Mecánico."""
        acciones_de_edicion = {"Nueva moto", "Editar moto", "Eliminar moto"}
        for boton in self.motos_widget.findChildren(QPushButton):
            if boton.text() in acciones_de_edicion:
                boton.hide()


if __name__ == "__main__":
    crear_tablas()
    app = QApplication(sys.argv)

    login = LoginDialog()
    if login.exec() == LoginDialog.DialogCode.Accepted:
        ventana = VentanaPrincipal(login.usuario_activo)
        ventana.show()
    else:
        sys.exit(0)

    sys.exit(app.exec())
