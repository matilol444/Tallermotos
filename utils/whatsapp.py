from urllib.parse import quote

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from database.database import obtener_clientes, obtener_moto_por_id


def obtener_contacto_cliente(cliente_id, moto_id):
    """Obtiene el contacto y los datos básicos de la moto sin alterar la base."""
    cliente = next((item for item in obtener_clientes() if item[0] == cliente_id), None)
    moto = obtener_moto_por_id(moto_id) if moto_id is not None else None
    return cliente, moto


def abrir_whatsapp_web(numero, mensaje):
    """Abre una conversación de WhatsApp Web con el texto precompletado."""
    telefono = "".join(caracter for caracter in str(numero or "") if caracter.isdigit())
    if not telefono:
        return False

    url = f"https://web.whatsapp.com/send?phone={telefono}&text={quote(mensaje)}"
    return QDesktopServices.openUrl(QUrl(url))
