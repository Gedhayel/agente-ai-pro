import sqlite3
from datetime import datetime

def crear_tabla():
    conn = sqlite3.connect('precios.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            producto TEXT,
            mi_precio REAL,
            precio_competencia REAL,
            analisis_ia TEXT
        )
    ''')
    conn.commit()
    conn.close()

def guardar_analisis(producto, mi_p, comp_p, ai_text):
    conn = sqlite3.connect('precios.db')
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO analisis (fecha, producto, mi_precio, precio_competencia, analisis_ia)
        VALUES (?, ?, ?, ?, ?)
    ''', (fecha_actual, producto, mi_p, comp_p, ai_text))
    conn.commit()
    conn.close()

def obtener_historial():
    conn = sqlite3.connect('precios.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM analisis ORDER BY fecha DESC')
    datos = cursor.fetchall()
    conn.close()
    return datos

