from facturas import FacturaProcessor

# 1. Inicializamos el procesador
procesador = FacturaProcessor()

# 2. Ruta de la factura que quieres probar
# (Asegúrate de tener una imagen llamada 'factura_test.jpg' en la carpeta)
ruta_imagen = "factura_test.jpg"

print("Iniciando la extracción de datos...")

try:
    # 3. Llamamos a la función
    datos = procesador.extraer_datos_factura(ruta_imagen)
    print("Datos extraídos con éxito:")
    print(datos)
except Exception as e:
    print(f"Ups, algo salió mal: {e}")