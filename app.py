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
        "Costo Mayor ($)": [15, 25, 45, 120],
        "Venta Detalle ($)": [45, 65, 110, 220]
    }
    
    df_rev = pd.DataFrame(reventa_data)
    df_rev["Ganancia ($)"] = df_rev["Venta Detalle ($)"] - df_rev["Costo Mayor ($)"]
    df_rev["ROI %"] = (df_rev["Ganancia ($)"] / df_rev["Costo Mayor ($)"]) * 100
    
    st.dataframe(df_rev, use_container_width=True)

    # --- 5. PROYECCIÓN DE CAPITALIZACIÓN ---
    st.markdown("---")
    st.header("📈 Proyección de Crecimiento")
    col_t1, col_t2 = st.columns(2)
    inv_input = col_t1.number_input("Inversión Inicial ($):", value=1000.0)
    porcentaje = col_t2.slider("Margen Objetivo (%):", 5, 100, 25)
    gan_s = inv_input * (porcentaje / 100)
    
    # --- 6. CONSULTORÍA IA & HISTORIAL ---
    st.markdown("---")
    st.header(f"🤖 Consultoría IA para {nombre_empresa}")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if p_chat := st.chat_input("Pregúntale a la IA sobre tu negocio..."):
        st.session_state.messages.append({"role": "user", "content": p_chat})
        with st.chat_message("user"):
            st.markdown(p_chat)
        
        with st.chat_message("assistant"):
            bot_ia = AnalizadorCompetencia()
            res = bot_ia.comparar_precios(p_chat, url_in if url_in else "Mercado", nombre_empresa)
            st.session_state['analisis_actual'] = res.content
            st.markdown(res.content)
            st.session_state.messages.append({"role": "assistant", "content": res.content})
            guardar_analisis(nombre_empresa, inv_input, gan_s, res.content)

    # --- 7. TENDENCIAS E HISTORIAL SQL ---
    st.markdown("---")
    col_g, col_h = st.columns([2, 1])
    
    with col_g:
        st.subheader("Tendencia Estimada")
        proyeccion = [inv_input + (gan_s * i) for i in range(13)]
        fig = px.area(y=proyeccion, x=list(range(13)), template="plotly_dark")
        fig.update_traces(line_color='#00c853', fillcolor='rgba(0, 200, 83, 0.3)')
        st.plotly_chart(fig, use_container_width=True)
        
    with col_h:
        st.subheader("📜 Últimos Análisis")
        h_data = obtener_historial()
        if h_data:
            for r in h_data[-3:]:
                with st.expander(f"📅 {r[1]}"):
                    st.write(r[5])
        else:
            st.write("No hay registros previos.")

    # Botón de descarga al final
    st.markdown(descargar_excel(df_rev), unsafe_allow_html=True)
    
