import sqlite3 #Librería para base de datos
from pathlib import Path #Librería para trabajar con rutas de archivos y directorios y que sea compatible con windows y linux

def registrar_asiento(fecha, descripcion_general, detalles): #Primera funcion: registrar_asiento
    """
    Registra un asiento contable completo en el Libro Diario aplicando partida doble.
    
    'detalles' debe ser una lista de diccionarios con este formato: #Aqui se define como debe ser el formato de los detalles del asiento
    [
        {"cuenta_id": 1, "descripcion": "Aporte inicial", "debe": 1000.0, "haber": 0.0}, 
        {"cuenta_id": 5, "descripcion": "Aporte inicial", "debe": 0.0, "haber": 1000.0}
    ]#Nota:Debemos diseñar una interfaz que cumpla con esta estructura de datos para garantizar que los asientos se registren correctamente.
    """
    # Para la logica del programa es necesario validar la Partida Doble antes de tocar la Base de Datos
    total_debe = sum(item.get("debe", 0.0) for item in detalles)
    total_haber = sum(item.get("haber", 0.0) for item in detalles)
    
    # Usamos round() a 2 decimales para evitar errores
    if round(total_debe, 2) != round(total_haber, 2): #si el debe es diferente al haber, entonces no se puede registrar
        return False, f"Error: El asiento no está cuadrado. Debe: {total_debe} | Haber: {total_haber}"
    
    if len(detalles) < 2: #Si solo afecctamos el debe o solo el haber, entonces no se puede registrar
        return False, "Error: Un asiento contable requiere al menos dos cuentas (debe y haber)."

    ruta_db = Path(__file__).parent / "contabilidad.db" #Crea una ruta absoluta y compatible 
    conexion = sqlite3.connect(ruta_db) #Se conecta a la base de datos
    cursor = conexion.cursor() #Crea un cursor
    
    try:
        # Habilitar claves foráneas
        cursor.execute("PRAGMA foreign_keys = ON;") #Habilita las claves foráneas
        
        # Iniciar una transacción explícita. Si algo falla, nada se guarda para conservar la integridad de los datos
        cursor.execute("BEGIN TRANSACTION;")
        
        # Insertar la cabecera del asiento
        cursor.execute("""
            INSERT INTO asientos (fecha, descripcion) 
            VALUES (?, ?);
        """, (fecha, descripcion_general))
        
        # Obtener el ID asignado automáticamente al asiento recién creado
        asiento_id = cursor.lastrowid #Obtiene el id autoincremento del ultimo registro en la tabla asientos
        
        # Insertar cada renglón del detalle
        for item in detalles: #Recorre cada renglón del detalle
            cursor.execute("""
                INSERT INTO detalle_asientos (asiento_id, cuenta_id, descripcion, debe, haber)
                VALUES (?, ?, ?, ?, ?);
            """, (
                asiento_id,
                item["cuenta_id"],
                item.get("descripcion", ""), #Si no se proporciona una descripcion, se inserta una cadena vacia
                item.get("debe", 0.0), #Si no se proporciona un debe, se inserta 0.0
                item.get("haber", 0.0) #Si no se proporciona un haber, se inserta 0.0
            ))
        
        # Si todo se ejecutó bien, guardamos permanentemente en el archivo local
        conexion.commit() #Guarda permanentemente en el archivo local
        return True, f"¡Asiento #{asiento_id} registrado con éxito y cuadrado correctamente!"
        
    except sqlite3.Error as e: #Si ocurre un error de base de datos, cancelamos toda la operación (Rollback)
        conexion.rollback() #Cancela toda la operación
        return False, f"Error en la base de datos al registrar: {e}"
    finally:
        conexion.close() #Cierra la conexión a la base de datos

# BLOQUE DE PRUEBA LOCAL: sirve para probar la función directamente desde la terminal
if __name__ == "__main__":
    print("--- Probando registro de un asiento CUADRADO ---")
    # Ejemplo: Apertura de caja chica con dinero del banco por 500$
    asiento_valido = [
        {"cuenta_id": 1, "descripcion": "Ingreso a caja chica", "debe": 500.0, "haber": 0.0},  # Caja Chica (id 1)
        {"cuenta_id": 2, "descripcion": "Salida de banco", "debe": 0.0, "haber": 500.0}       # Banco (id 2)
    ]
    exito, mensaje = registrar_asiento("2026-05-27", "Apertura de fondos de caja chica", asiento_valido)
    print(mensaje)

    print("\n--- Probando registro de un asiento DESCUADRADO ---")
    asiento_invalido = [
        {"cuenta_id": 1, "descripcion": "Error intencional", "debe": 300.0, "haber": 0.0},
        {"cuenta_id": 2, "descripcion": "Error intencional", "debe": 0.0, "haber": 250.0}
    ]
    exito_2, mensaje_2 = registrar_asiento("2026-05-27", "Asiento de prueba erróneo", asiento_invalido)
    print(mensaje_2)