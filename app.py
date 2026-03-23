import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scraping import AnalizadorCompetencia
from database import obtener_historial, crear_tabla, guardar_analisis 

# 1. SETUP Y ESTILO CORPORATIVO
st.set_page_config(page_title="Arbitrage & BI Pro", page_icon="🌎", layout="wide")
crear_tabla()

# --- FUNCIONES AGREGADAS (CORREO) ---
def enviar_correo(destinatario, asunto, cuerpo):
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar correo: {e}")
        return False

# Función para descarga de reportes
def descargar_excel(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="auditoria_pro.csv"><button style="background-color:#00c853; color:white; border-radius:8px; border:none; padding:12px; cursor:pointer; width:100%; font-weight:bold;">📥 DESCARGAR AUDITORÍA COMPLETA</button></a>'

# 2. LOGIN NATIVO Y VERIFICACIÓN
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'verificado' not in st.session_state: st.session_state['verificado'] = False
if 'codigo_sesion' not in st.session_state: st.session_state['codigo_sesion'] = None
if 'analisis_actual' not in st.session_state: st.session_state['analisis_actual'] = ""

if not st.session_state['auth']:
    st.title("🔐 Terminal de Inteligencia Corporativa")
    u, p = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
    if st.button("ACCEDER AL MONITOR", use_container_width=True):
        if u.lower() == "admin" and p == "1234":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Credenciales incorrectas")
else:
    # --- BARRA LATERAL (CON REGISTRO Y VERIFICACIÓN) ---
    with st.sidebar:
        st.success("✅ Conexión Encriptada")
        
        st.header("🏢 Datos de la Empresa")
        nombre_empresa = st.text_input("Nombre Empresa:", value="Mi Negocio")
        rif_empresa = st.text_input("RIF / ID Fiscal:")
        
        st.header("📧 Verificación de Email")
        email_cliente = st.text_input("Email para reportes:")
        if st.button("Enviar Código"):
            codigo = str(random.randint(1000, 9999))
            st.session_state['codigo_sesion'] = codigo
            if enviar_correo(email_cliente, "Tu Código BI Pro", f"Código: {codigo}"):
                st.info("Código enviado.")
        
        cod_in = st.text_input("Introduce el código:")
        if st.button("Verificar"):
            if cod_in == st.session_state['codigo_sesion']:
                st.session_state['verificado'] = True
                st.success("Verificado ✅")

        st.header("📖 Guía de Uso IA")
        with st.expander("Instrucciones Rápidas"):
            st.write("1. **Scanner:** Pega una URL para ver a la competencia.")
            st.write("2. **Excel:** Sube tus ventas para auditar márgenes.")
            st.write("3. **Chat:** Pregunta estrategias de precios.")
        st.markdown("[🚀 SOPORTE WHATSAPP](https://wa.me/584120000000)")
        if st.button("Cerrar Sesión"):
            st.session_state['auth'] = False
            st.session_state['verificado'] = False
            st.rerun()

    st.title(f"🌎 Monitor de Arbitraje: {nombre_empresa}")

    # --- REGALO BI: PUNTO DE EQUILIBRIO ---
    st.markdown("---")
    st.header("🎁 Regalo BI: Punto de Equilibrio")
    col_b1, col_b2, col_b3 = st.columns(3)
    fijos = col_b1.number_input("Gastos Fijos ($):", value=100.0)
    vta = col_b2.number_input("Precio Venta ($):", value=20.0)
    cst = col_b3.number_input("Costo Compra ($):", value=10.0)
    if (vta - cst) > 0:
        pe = fijos / (vta - cst)
        st.metric("Unidades para Punto de Equilibrio", f"{int(pe)+1} Unids")

    # --- 3. CONEXIÓN WEB & EXCEL (BI) ---
    st.markdown("---")
    c_web, c_excel = st.columns(2)
    with c_web:
        st.header("🔗 Conexión Web (AI Scanner)")
        url_in = st.text_input("URL del Catálogo Competencia:", placeholder="https://tienda.com")
        if st.button("ESCANEAR MERCADO"):
            if url_in:
                with st.spinner("IA analizando web de competencia..."):
                    bot = AnalizadorCompetencia()
                    res_web = bot.comparar_precios("Analiza esta web de competencia", url_in, nombre_empresa)
                    st.session_state['analisis_actual'] = res_web.content
                    st.markdown(res_web.content)
            else: st.warning("Pega una URL primero")

    with c_excel:
        st.header("📁 Auditoría de Empresa (Excel)")
        archivo = st.file_uploader("Sube tu inventario/ventas:", type=["xlsx", "csv"])
        if archivo: 
            df_subido = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
            st.success("Archivo procesado.")
            st.dataframe(df_subido.head(5), use_container_width=True)

    # --- 4. LISTADO DE PRODUCTOS PARA REVENTA ---
    st.markdown("---")
    st.header("📦 Radar de Productos (Reventa & Márgenes)")
    reventa_data = {
        "Producto": ["Audífonos Pro", "Teclado RGB", "Cámara 4K", "Monitor 144Hz"],
        "
