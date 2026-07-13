from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from database.database import autenticar_usuario
from ui.estilo_visual import aplicar_estilo_moderno


class LoginDialog(QDialog):
    """Pantalla de acceso previa a la ventana principal."""

    def __init__(self):
        super().__init__()
        self.usuario_activo = None
        self._crear_interfaz()

    def _crear_interfaz(self):
        self.setWindowTitle("Ingresar al Taller de Motos")
        self.setModal(True)
        self.setFixedSize(390, 285)
        self.setStyleSheet("""
            QDialog { background: #202225; color: white; }
            QLineEdit {
                background: #2f3136; border: 1px solid #3a3d44; border-radius: 7px;
                padding: 10px; color: white; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #5865f2; }
            QPushButton {
                background: #5865f2; border: none; border-radius: 7px; color: white;
                padding: 11px; font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { background: #4752c4; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(38, 30, 38, 30)
        layout.setSpacing(11)

        titulo = QLabel("🏍 Taller de Motos")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 23px; font-weight: bold;")
        subtitulo = QLabel("Inicie sesión para continuar")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("color: #b9bbbe; font-size: 14px; margin-bottom: 12px;")

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_usuario.setClearButtonEnabled(True)
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.returnPressed.connect(self.ingresar)

        boton_ingresar = QPushButton("Ingresar")
        boton_ingresar.clicked.connect(self.ingresar)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addWidget(self.input_usuario)
        layout.addWidget(self.input_password)
        layout.addSpacing(6)
        layout.addWidget(boton_ingresar)

        self.input_usuario.setFocus()
        aplicar_estilo_moderno(self, [titulo])

    def ingresar(self):
        usuario = self.input_usuario.text().strip()
        password = self.input_password.text()
        if not usuario or not password:
            QMessageBox.warning(self, "Iniciar sesión", "Ingrese usuario y contraseña.")
            return

        datos = autenticar_usuario(usuario, password)
        if datos is None:
            self.input_password.clear()
            self.input_password.setFocus()
            QMessageBox.warning(self, "Iniciar sesión", "Usuario o contraseña incorrectos.")
            return

        usuario_id, nombre, rol = datos
        self.usuario_activo = {"id": usuario_id, "usuario": nombre, "rol": rol or ""}
        self.accept()
