import sqlite3
from pathlib import Path

def inicializar_base_datos():
    # Usamos pathlib para asegurar compatibilidad absoluta de rutas entre Linux (ChromeOS) y Windows
    ruta_db = Path(__file__).parent / "contabilidad.db"
    
    # Conexión local (creará el archivo .db si no existe)
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    
    # Habilitar el soporte de llaves foráneas para integridad referencial
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Tabla de Catálogo de Cuentas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cuentas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,      -- Ej: '1.1.01' para Caja Chica
        nombre TEXT NOT NULL,             -- Ej: 'Caja Chica'
        tipo TEXT NOT NULL                -- 'Activo', 'Pasivo', 'Capital', 'Ingreso', 'Egreso'
    );
    """)
    
    # 2. Tabla de Asientos Contables (Cabecera del Libro Diario)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,              -- Formato ISO: YYYY-MM-DD
        descripcion TEXT NOT NULL         -- Ej: 'Registro de ventas del día'
    );
    """)
    
    # 3. Tabla de Detalles del Asiento (Partida Doble)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_asientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asiento_id INTEGER NOT NULL,
        cuenta_id INTEGER NOT NULL,
        descripcion TEXT,                 -- Detalle específico por renglón
        debe REAL DEFAULT 0.0,
        haber REAL DEFAULT 0.0,
        FOREIGN KEY (asiento_id) REFERENCES asientos(id) ON DELETE CASCADE,
        FOREIGN KEY (cuenta_id) REFERENCES cuentas(id)
    );
    """)
    
    # Insertar un catálogo de cuentas básico para pruebas iniciales
    cuentas_por_defecto = [
        ('1.1.01', 'Caja Chica', 'Activo'),
        ('1.1.02', 'Banco Mercantil', 'Activo'),
        ('1.2.01', 'Inventario de Mercancía', 'Activo'),
        ('2.1.01', 'Cuentas por Pagar', 'Pasivo'),
        ('3.1.01', 'Capital Social', 'Capital'),
        ('4.1.01', 'Ingresos por Ventas', 'Ingreso'),
        ('5.1.01', 'Gastos de Alquiler', 'Egreso')
    ]
    
    try:
        cursor.executemany("""
        INSERT OR IGNORE INTO cuentas (codigo, nombre, tipo) 
        VALUES (?, ?, ?);
        """, cuentas_por_defecto)
        
        conexion.commit()
        print(f"¡Base de datos inicializada con éxito localmente en: {ruta_db.resolve()}!")
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        conexion.close()

if __name__ == "__main__":
    inicializar_base_datos()