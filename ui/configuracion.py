import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.database import RUTA_DB
from ui.estilo_visual import aplicar_estilo_moderno


CARPETA_BACKUP = RUTA_DB.parent / "Backup"


class ConfiguracionWidget(QWidget):
    """Opciones generales de la aplicación."""

    def __init__(self):
        super().__init__()
        self._crear_interfaz()

    def _crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        titulo = QLabel("Configuración")
        titulo.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        layout.addWidget(titulo)

        panel = QFrame()
        panel.setObjectName("panelBackup")
        panel.setStyleSheet(
            "QFrame#panelBackup { background: #2f3136; border: 1px solid #3a3d44; border-radius: 10px; }"
            "QPushButton#botonBackup { text-align: center; padding: 11px 18px; }"
        )
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(22, 20, 22, 20)
        panel_layout.setSpacing(10)

        encabezado = QLabel("💾  Copias de seguridad")
        encabezado.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        descripcion = QLabel(
            "Guarde una copia de la base de datos o restaure una copia anterior. "
            "Las copias se almacenan en la carpeta Backup."
        )
        descripcion.setWordWrap(True)
        descripcion.setStyleSheet("color: #b9bbbe; font-size: 14px;")

        self.etiqueta_ruta = QLabel()
        self.etiqueta_ruta.setStyleSheet("color: #8e9297; font-size: 12px;")
        self._actualizar_ruta()

        botones = QHBoxLayout()
        boton_crear = QPushButton("Crear copia de seguridad")
        boton_restaurar = QPushButton("Restaurar copia")
        boton_abrir = QPushButton("Abrir carpeta de backups")
        for boton in (boton_crear, boton_restaurar, boton_abrir):
            boton.setObjectName("botonBackup")
            botones.addWidget(boton)
        botones.addStretch()

        boton_crear.clicked.connect(self.crear_copia)
        boton_restaurar.clicked.connect(self.restaurar_copia)
        boton_abrir.clicked.connect(self.abrir_carpeta_backups)

        panel_layout.addWidget(encabezado)
        panel_layout.addWidget(descripcion)
        panel_layout.addWidget(self.etiqueta_ruta)
        panel_layout.addSpacing(6)
        panel_layout.addLayout(botones)

        layout.addWidget(panel)
        layout.addStretch()
        aplicar_estilo_moderno(self, [titulo])

    def _asegurar_carpeta_backup(self):
        CARPETA_BACKUP.mkdir(parents=True, exist_ok=True)
        self._actualizar_ruta()

    def _actualizar_ruta(self):
        self.etiqueta_ruta.setText(f"Ubicación: {CARPETA_BACKUP}")

    def crear_copia(self):
        if not RUTA_DB.exists():
            QMessageBox.warning(self, "Crear copia de seguridad", "No se encontró la base de datos actual.")
            return

        try:
            self._asegurar_carpeta_backup()
            destino = self._nuevo_nombre_backup()
            # copy2 conserva los metadatos del archivo sin alterar la base original.
            shutil.copy2(RUTA_DB, destino)
        except OSError as error:
            QMessageBox.critical(self, "Crear copia de seguridad", f"No se pudo crear la copia.\n\n{error}")
            return

        QMessageBox.information(
            self,
            "Copia de seguridad creada",
            f"La copia se guardó correctamente en:\n{destino}",
        )

    @staticmethod
    def _nuevo_nombre_backup(prefijo="backup_taller"):
        marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M")
        destino = CARPETA_BACKUP / f"{prefijo}_{marca_tiempo}.db"
        indice = 2
        while destino.exists():
            destino = CARPETA_BACKUP / f"{prefijo}_{marca_tiempo}_{indice}.db"
            indice += 1
        return destino

    def restaurar_copia(self):
        self._asegurar_carpeta_backup()
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar copia de seguridad",
            str(CARPETA_BACKUP),
            "Bases de datos (*.db)",
        )
        if not archivo:
            return

        origen = Path(archivo)
        if origen.resolve() == RUTA_DB.resolve():
            QMessageBox.warning(self, "Restaurar copia", "Seleccione una copia distinta de la base actual.")
            return

        confirmar = QMessageBox.question(
            self,
            "Confirmar restauración",
            "La base de datos actual será reemplazada por la copia seleccionada.\n"
            "Esta acción no se puede deshacer.\n\n"
            "¿Desea continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmar != QMessageBox.StandardButton.Yes:
            return

        try:
            # Conserva el estado actual antes de restaurar y reemplaza desde un temporal.
            copia_previa = self._nuevo_nombre_backup("backup_antes_de_restaurar")
            shutil.copy2(RUTA_DB, copia_previa)
            temporal = RUTA_DB.with_suffix(".restaurando")
            shutil.copy2(origen, temporal)
            temporal.replace(RUTA_DB)
        except OSError as error:
            QMessageBox.critical(self, "Restaurar copia", f"No se pudo restaurar la copia.\n\n{error}")
            return

        QMessageBox.information(
            self,
            "Copia restaurada",
            "La copia se restauró correctamente. Se guardó una copia del estado anterior en Backup.\n\n"
            "Las pantallas se actualizarán al volver a abrirlas.",
        )

    def abrir_carpeta_backups(self):
        try:
            self._asegurar_carpeta_backup()
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(CARPETA_BACKUP))):
                raise OSError("El sistema no pudo abrir la carpeta.")
        except OSError as error:
            QMessageBox.warning(self, "Abrir carpeta de backups", str(error))
