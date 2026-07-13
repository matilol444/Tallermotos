import sqlite3
from pathlib import Path
import sys
import os


def obtener_ruta_recursos():
    """Obtiene la ruta base para los recursos, compatible con PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Si la aplicación está "congelada" (empaquetada), la ruta es la carpeta temporal.
        return Path(sys._MEIPASS)
    else:
        # En modo de desarrollo, la ruta es la carpeta principal del proyecto.
        return Path(__file__).resolve().parent.parent


def obtener_ruta_datos_app():
    """Obtiene una carpeta persistente para guardar datos de la aplicación."""
    if sys.platform == "win32":
        return Path(os.getenv('APPDATA')) / "TallerMotos"
    else:
        return Path.home() / ".local" / "share" / "TallerMotos"

RUTA_DATOS = obtener_ruta_datos_app()
RUTA_DB = RUTA_DATOS / "taller_motos.db"


def conectar():
    RUTA_DATOS.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(RUTA_DB)


def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla de clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        whatsapp TEXT,
        direccion TEXT
    )
    """)

    # Tabla de motos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS motos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        marca TEXT,
        modelo TEXT,
        año INTEGER,
        patente TEXT,
        kilometros INTEGER,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )
    """)

    # Tabla de turnos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS turnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        moto_id INTEGER,
        fecha TEXT,
        hora TEXT,
        motivo TEXT,
        estado TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(moto_id) REFERENCES motos(id)
    )
    """)
    _agregar_columna_si_no_existe(cursor, "turnos", "moto_id", "INTEGER")

    # Tabla de presupuestos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS presupuestos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        moto_id INTEGER,
        reparacion_id INTEGER,
        descripcion TEXT,
        mano_obra REAL,
        repuestos REAL,
        total REAL,
        estado TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(moto_id) REFERENCES motos(id),
        FOREIGN KEY(reparacion_id) REFERENCES reparaciones(id)
    )
    """)
    _agregar_columna_si_no_existe(cursor, "presupuestos", "moto_id", "INTEGER")
    _agregar_columna_si_no_existe(cursor, "presupuestos", "reparacion_id", "INTEGER")
    _agregar_columna_si_no_existe(cursor, "presupuestos", "estado", "TEXT")

    # Tabla de reparaciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reparaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        moto_id INTEGER,
        problema TEXT,
        diagnostico TEXT,
        trabajo TEXT,
        repuestos TEXT,
        mano_obra REAL,
        estado TEXT,
        fecha_ingreso TEXT,
        fecha_entrega TEXT,
        total REAL,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(moto_id) REFERENCES motos(id)
    )
    """)
    _agregar_columna_si_no_existe(cursor, "reparaciones", "fecha_ingreso", "TEXT")
    _agregar_columna_si_no_existe(cursor, "reparaciones", "fecha_entrega", "TEXT")
    _agregar_columna_si_no_existe(cursor, "reparaciones", "total", "REAL")

    # Tabla de repuestos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repuestos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT,
        marca TEXT,
        stock INTEGER DEFAULT 0,
        precio_compra REAL,
        precio_venta REAL
    )
    """)

    # Tabla de relación entre reparaciones y repuestos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reparacion_repuestos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reparacion_id INTEGER,
        repuesto_id INTEGER,
        cantidad INTEGER,
        precio_unitario REAL,
        FOREIGN KEY(reparacion_id) REFERENCES reparaciones(id),
        FOREIGN KEY(repuesto_id) REFERENCES repuestos(id)
    )
    """)

    # Usuarios del sistema y su nivel de acceso.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)
    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)",
        ("matias", "31445238", "Dueño"),
    )

    # Movimientos registrados desde el módulo Caja / Finanzas.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos_caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        categoria TEXT NOT NULL,
        descripcion TEXT,
        monto REAL NOT NULL,
        fecha TEXT NOT NULL
    )
    """)

    conexion.commit()
    conexion.close()


def _agregar_columna_si_no_existe(cursor, tabla, columna, tipo):
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [row[1] for row in cursor.fetchall()]
    if columna not in columnas:
        cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")


def autenticar_usuario(usuario, password):
    """Devuelve los datos del usuario cuando las credenciales son válidas."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, usuario, rol FROM usuarios WHERE usuario = ? AND password = ?",
        (usuario, password),
    )
    resultado = cursor.fetchone()
    conexion.close()
    return resultado


def crear_movimiento_caja(tipo, categoria, descripcion, monto, fecha):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO movimientos_caja (tipo, categoria, descripcion, monto, fecha) VALUES (?, ?, ?, ?, ?)",
        (tipo, categoria, descripcion, monto, fecha),
    )
    conexion.commit()
    conexion.close()


def obtener_movimientos_caja(fecha_desde, fecha_hasta):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, tipo, categoria, descripcion, monto, fecha FROM movimientos_caja "
        "WHERE fecha BETWEEN ? AND ? ORDER BY fecha DESC, id DESC",
        (fecha_desde, fecha_hasta),
    )
    movimientos = cursor.fetchall()
    conexion.close()
    return movimientos


def obtener_clientes():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, telefono, whatsapp, direccion FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()
    conexion.close()
    return clientes


def crear_cliente(nombre, telefono, whatsapp, direccion):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO clientes (nombre, telefono, whatsapp, direccion) VALUES (?, ?, ?, ?)", (nombre, telefono, whatsapp, direccion))
    conexion.commit()
    cliente_id = cursor.lastrowid
    conexion.close()
    return cliente_id


def actualizar_cliente(cliente_id, nombre, telefono, whatsapp, direccion):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE clientes SET nombre = ?, telefono = ?, whatsapp = ?, direccion = ? WHERE id = ?", (nombre, telefono, whatsapp, direccion, cliente_id))
    conexion.commit()
    conexion.close()


def eliminar_cliente(cliente_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conexion.commit()
    conexion.close()


def obtener_motos(cliente_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    if cliente_id is None:
        cursor.execute(
            "SELECT id, cliente_id, marca, modelo, año, patente, kilometros FROM motos ORDER BY id"
        )
    else:
        cursor.execute(
            "SELECT id, cliente_id, marca, modelo, año, patente, kilometros FROM motos WHERE cliente_id = ? ORDER BY id",
            (cliente_id,)
        )
    motos = cursor.fetchall()
    conexion.close()
    return motos


def obtener_moto_por_id(moto_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT cliente_id, marca, modelo, año, patente, kilometros FROM motos WHERE id = ?",
        (moto_id,)
    )
    moto = cursor.fetchone()
    conexion.close()
    return moto


def crear_moto(cliente_id, marca, modelo, ano, patente, kilometros):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO motos (cliente_id, marca, modelo, año, patente, kilometros) VALUES (?, ?, ?, ?, ?, ?)",
        (cliente_id, marca, modelo, ano, patente, kilometros)
    )
    conexion.commit()
    conexion.close()


def actualizar_moto(moto_id, cliente_id, marca, modelo, ano, patente, kilometros):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE motos SET cliente_id = ?, marca = ?, modelo = ?, año = ?, patente = ?, kilometros = ? WHERE id = ?",
        (cliente_id, marca, modelo, ano, patente, kilometros, moto_id)
    )
    conexion.commit()
    conexion.close()


def borrar_moto(moto_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM motos WHERE id = ?", (moto_id,))
    conexion.commit()
    conexion.close()


def obtener_turnos(cliente_id, moto_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    if moto_id is None or moto_id == -1:
        cursor.execute(
            "SELECT t.id, c.nombre, m.marca || ' ' || m.modelo, t.fecha, t.hora, t.motivo, t.estado "
            "FROM turnos t "
            "LEFT JOIN clientes c ON t.cliente_id = c.id "
            "LEFT JOIN motos m ON t.moto_id = m.id "
            "WHERE t.cliente_id = ? "
            "ORDER BY t.fecha, t.hora",
            (cliente_id,)
        )
    else:
        cursor.execute(
            "SELECT t.id, c.nombre, m.marca || ' ' || m.modelo, t.fecha, t.hora, t.motivo, t.estado "
            "FROM turnos t "
            "LEFT JOIN clientes c ON t.cliente_id = c.id "
            "LEFT JOIN motos m ON t.moto_id = m.id "
            "WHERE t.cliente_id = ? AND t.moto_id = ? "
            "ORDER BY t.fecha, t.hora",
            (cliente_id, moto_id)
        )
    turnos = cursor.fetchall()
    conexion.close()
    return turnos


def obtener_turno_por_id(turno_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT t.cliente_id, t.moto_id, t.fecha, t.hora, t.motivo, t.estado "
        "FROM turnos t WHERE t.id = ?",
        (turno_id,)
    )
    turno = cursor.fetchone()
    conexion.close()
    return turno


def crear_turno(cliente_id, moto_id, fecha, hora, motivo, estado):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO turnos (cliente_id, moto_id, fecha, hora, motivo, estado) VALUES (?, ?, ?, ?, ?, ?)",
        (cliente_id, moto_id, fecha, hora, motivo, estado)
    )
    conexion.commit()
    conexion.close()


def actualizar_turno(turno_id, cliente_id, moto_id, fecha, hora, motivo, estado):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE turnos SET cliente_id = ?, moto_id = ?, fecha = ?, hora = ?, motivo = ?, estado = ? WHERE id = ?",
        (cliente_id, moto_id, fecha, hora, motivo, estado, turno_id)
    )
    conexion.commit()
    conexion.close()


def borrar_turno(turno_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM turnos WHERE id = ?", (turno_id,))
    conexion.commit()
    conexion.close()


def obtener_presupuestos(cliente_id, moto_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    if moto_id is None or moto_id == -1:
        cursor.execute(
            "SELECT p.id, c.nombre, m.marca || ' ' || m.modelo, p.reparacion_id, p.descripcion, p.repuestos, p.mano_obra, p.total, p.estado "
            "FROM presupuestos p "
            "LEFT JOIN clientes c ON p.cliente_id = c.id "
            "LEFT JOIN motos m ON p.moto_id = m.id "
            "WHERE p.cliente_id = ? "
            "ORDER BY p.id",
            (cliente_id,)
        )
    else:
        cursor.execute(
            "SELECT p.id, c.nombre, m.marca || ' ' || m.modelo, p.reparacion_id, p.descripcion, p.repuestos, p.mano_obra, p.total, p.estado "
            "FROM presupuestos p "
            "LEFT JOIN clientes c ON p.cliente_id = c.id "
            "LEFT JOIN motos m ON p.moto_id = m.id "
            "WHERE p.cliente_id = ? AND p.moto_id = ? "
            "ORDER BY p.id",
            (cliente_id, moto_id)
        )
    presupuestos = cursor.fetchall()
    conexion.close()
    return presupuestos


def obtener_presupuesto_por_id(presupuesto_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado FROM presupuestos WHERE id = ?",
        (presupuesto_id,)
    )
    presupuesto = cursor.fetchone()
    conexion.close()
    return presupuesto


def crear_presupuesto(cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO presupuestos (cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado)
    )
    conexion.commit()
    conexion.close()


def actualizar_presupuesto(presupuesto_id, cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE presupuestos SET cliente_id = ?, moto_id = ?, reparacion_id = ?, descripcion = ?, repuestos = ?, mano_obra = ?, total = ?, estado = ? WHERE id = ?",
        (cliente_id, moto_id, reparacion_id, descripcion, repuestos, mano_obra, total, estado, presupuesto_id)
    )
    conexion.commit()
    conexion.close()


def borrar_presupuesto(presupuesto_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM presupuestos WHERE id = ?", (presupuesto_id,))
    conexion.commit()
    conexion.close()


def obtener_reparaciones(cliente_id, moto_id=None):
    conexion = conectar()
    cursor = conexion.cursor()
    if moto_id is None or moto_id == -1:
        cursor.execute(
            "SELECT r.id, c.nombre, m.marca || ' ' || m.modelo, r.problema, r.diagnostico, r.trabajo, r.repuestos, r.mano_obra, r.estado, r.fecha_ingreso, r.fecha_entrega, r.total "
            "FROM reparaciones r "
            "LEFT JOIN clientes c ON r.cliente_id = c.id "
            "LEFT JOIN motos m ON r.moto_id = m.id "
            "WHERE r.cliente_id = ? "
            "ORDER BY r.id",
            (cliente_id,)
        )
    else:
        cursor.execute(
            "SELECT r.id, c.nombre, m.marca || ' ' || m.modelo, r.problema, r.diagnostico, r.trabajo, r.repuestos, r.mano_obra, r.estado, r.fecha_ingreso, r.fecha_entrega, r.total "
            "FROM reparaciones r "
            "LEFT JOIN clientes c ON r.cliente_id = c.id "
            "LEFT JOIN motos m ON r.moto_id = m.id "
            "WHERE r.cliente_id = ? AND r.moto_id = ? "
            "ORDER BY r.id",
            (cliente_id, moto_id)
        )
    reparaciones = cursor.fetchall()
    conexion.close()
    return reparaciones


def obtener_reparacion_por_id(reparacion_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra, estado, fecha_ingreso, fecha_entrega, total "
        "FROM reparaciones WHERE id = ?",
        (reparacion_id,)
    )
    reparacion = cursor.fetchone()
    conexion.close()
    return reparacion


def crear_reparacion(cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra, estado, fecha_ingreso=None, fecha_entrega=None, total=None):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO reparaciones (cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra, estado, fecha_ingreso, fecha_entrega, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra, estado, fecha_ingreso, fecha_entrega, total)
    )
    reparacion_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return reparacion_id


def actualizar_reparacion(reparacion_id, cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra, estado, fecha_ingreso=None, fecha_entrega=None, total=None):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE reparaciones SET cliente_id = ?, moto_id = ?, problema = ?, diagnostico = ?, trabajo = ?, repuestos = ?, mano_obra = ?, estado = ?, fecha_ingreso = ?, fecha_entrega = ?, total = ? WHERE id = ?",
        (cliente_id, moto_id, problema, diagnostico, trabajo, repuestos, mano_obra, estado, fecha_ingreso, fecha_entrega, total, reparacion_id)
    )
    conexion.commit()
    conexion.close()


def borrar_reparacion(reparacion_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT repuesto_id, cantidad FROM reparacion_repuestos WHERE reparacion_id = ?", (reparacion_id,))
    relaciones = cursor.fetchall()
    for repuesto_id, cantidad in relaciones:
        cursor.execute("UPDATE repuestos SET stock = stock + ? WHERE id = ?", (cantidad, repuesto_id))
    cursor.execute("DELETE FROM reparacion_repuestos WHERE reparacion_id = ?", (reparacion_id,))
    cursor.execute("DELETE FROM reparaciones WHERE id = ?", (reparacion_id,))
    conexion.commit()
    conexion.close()


def obtener_repuestos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, codigo, marca, stock, precio_compra, precio_venta FROM repuestos ORDER BY nombre")
    repuestos = cursor.fetchall()
    conexion.close()
    return repuestos


def obtener_repuesto_por_id(repuesto_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, codigo, marca, stock, precio_compra, precio_venta FROM repuestos WHERE id = ?", (repuesto_id,))
    repuesto = cursor.fetchone()
    conexion.close()
    return repuesto


def crear_repuesto(nombre, codigo, marca, stock, precio_compra, precio_venta):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO repuestos (nombre, codigo, marca, stock, precio_compra, precio_venta) VALUES (?, ?, ?, ?, ?, ?)",
        (nombre, codigo, marca, stock, precio_compra, precio_venta),
    )
    conexion.commit()
    conexion.close()


def actualizar_repuesto(repuesto_id, nombre, codigo, marca, stock, precio_compra, precio_venta):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE repuestos SET nombre = ?, codigo = ?, marca = ?, stock = ?, precio_compra = ?, precio_venta = ? WHERE id = ?",
        (nombre, codigo, marca, stock, precio_compra, precio_venta, repuesto_id),
    )
    conexion.commit()
    conexion.close()


def borrar_repuesto(repuesto_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM repuestos WHERE id = ?", (repuesto_id,))
    conexion.commit()
    conexion.close()


def obtener_repuestos_de_reparacion(reparacion_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT rr.id, rr.repuesto_id, r.nombre, rr.cantidad, rr.precio_unitario "
        "FROM reparacion_repuestos rr "
        "LEFT JOIN repuestos r ON rr.repuesto_id = r.id "
        "WHERE rr.reparacion_id = ? "
        "ORDER BY rr.id",
        (reparacion_id,),
    )
    items = cursor.fetchall()
    conexion.close()
    return items


def agregar_repuesto_a_reparacion(reparacion_id, repuesto_id, cantidad, precio_unitario):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT stock FROM repuestos WHERE id = ?",
        (repuesto_id,),
    )
    stock_actual = cursor.fetchone()
    if not stock_actual or stock_actual[0] < cantidad:
        conexion.close()
        return False

    cursor.execute(
        "UPDATE repuestos SET stock = stock - ? WHERE id = ?",
        (cantidad, repuesto_id),
    )
    cursor.execute(
        "INSERT INTO reparacion_repuestos (reparacion_id, repuesto_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
        (reparacion_id, repuesto_id, cantidad, precio_unitario),
    )
    conexion.commit()
    conexion.close()
    return True


def eliminar_repuesto_de_reparacion(reparacion_id, reparacion_repuesto_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT repuesto_id, cantidad FROM reparacion_repuestos WHERE id = ? AND reparacion_id = ?",
        (reparacion_repuesto_id, reparacion_id),
    )
    relacion = cursor.fetchone()
    if relacion is None:
        conexion.close()
        return False

    repuesto_id, cantidad = relacion
    cursor.execute("UPDATE repuestos SET stock = stock + ? WHERE id = ?", (cantidad, repuesto_id))
    cursor.execute("DELETE FROM reparacion_repuestos WHERE id = ? AND reparacion_id = ?", (reparacion_repuesto_id, reparacion_id))
    conexion.commit()
    conexion.close()
    return True


def actualizar_reparacion_repuestos(reparacion_id, items):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT repuesto_id, cantidad FROM reparacion_repuestos WHERE reparacion_id = ?", (reparacion_id,))
    existentes = cursor.fetchall()
    for repuesto_id, cantidad in existentes:
        cursor.execute("UPDATE repuestos SET stock = stock + ? WHERE id = ?", (cantidad, repuesto_id))
    cursor.execute("DELETE FROM reparacion_repuestos WHERE reparacion_id = ?", (reparacion_id,))

    for repuesto_id, cantidad, precio_unitario in items:
        cursor.execute("SELECT stock FROM repuestos WHERE id = ?", (repuesto_id,))
        stock_actual = cursor.fetchone()
        if not stock_actual or stock_actual[0] < cantidad:
            conexion.close()
            return False
        cursor.execute("UPDATE repuestos SET stock = stock - ? WHERE id = ?", (cantidad, repuesto_id))
        cursor.execute(
            "INSERT INTO reparacion_repuestos (reparacion_id, repuesto_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
            (reparacion_id, repuesto_id, cantidad, precio_unitario),
        )

    conexion.commit()
    conexion.close()
    return True

if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada correctamente")
