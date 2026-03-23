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

# --- ESTILOS CSS (BOTÓN WHATSAPP Y UI) ---
st.markdown("""
<style>
    .whatsapp-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #25D366;
        color: white !important;
        font-weight: bold;
        padding: 12px 20px;
        border-radius: 10px;
        text-decoration: none !important;
        width: 100%;
        margin-top: 10px;
        border: none;
    }
    .whatsapp-button:hover { background-color: #128C7E; }
    .whatsapp-icon { width: 22px; height: 22px; margin-right: 10px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
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
        st.error(f"Error Email: {e}")
        return False

def descargar_excel(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="auditoria_pro.csv"><button style="background-color:#00c853; color:white; border-radius:8px; border:none; padding:12px; cursor:pointer; width:100%; font-weight:bold;">📥 DESCARGAR AUDITORÍA COMPLETA</button></a>'

# 2. LOGIN NATIVO
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'verificado' not in st.session_state: st.session_state['verificado'] = False
if 'codigo_sesion' not in st.session_state: st.session_state['codigo_sesion'] = None
if 'analisis_actual' not in st.session_state: st.session_state['analisis_actual'] = ""

if not st.session_state['auth']:
    st.title("🔐 Terminal de Inteligencia Corporativa")
    col_l, col_r = st.columns([1, 2])
    with col_l:
        u, p = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
        if st.button("ACCEDER AL MONITOR", use_container_width=True):
            if u.lower() == "admin" and p == "1234":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Credenciales incorrectas")
else:
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.success("✅ Conexión Encriptada")
        st.header("🏢 Configuración")
        nombre_empresa = st.text_input("Nombre Empresa:", value="Empresa Pro")
        
        st.header("📧 Verificación")
        email_cliente = st.text_input("Email Reportes:")
        if st.button("Enviar Código"):
            if email_cliente:
                codigo = str(random.randint(1000, 9999))
                st.session_state['codigo_sesion'] = codigo
                if enviar_correo(email_cliente, "Tu Código BI Pro", f"Código: {codigo}"):
                    st.info("Código enviado.")
        
        cod_in = st.text_input("Introduce el código:")
        if st.button("Verificar"):
            if cod_in == st.session_state['codigo_sesion']:
                st.session_state['verificado'] = True
                st.success("Verificado ✅")

        st.markdown("---")
        whatsapp_url = "https://wa.me/584142486557" # TU NÚMERO AQUÍ
        whatsapp_icon = "https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg"
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-button"><img src="{whatsapp_icon}" class="whatsapp-icon">SOPORTE WHATSAPP</a>', unsafe_allow_html=True)
        
        if st.button("Cerrar Sesión"):
            st.session_state['auth'] = False
            st.rerun()

    st.title(f"🌎 Monitor de Arbitraje: {nombre_empresa}")

    # --- 3. DASHBOARD DE MÁRGENES ---
    st.markdown("---")
    col_b1, col_b2, col_b3 = st.columns(3)
    fijos = col_b1.number_input("Gastos Fijos ($):", value=1500.0)
    vta = col_b2.number_input("Precio Promedio ($):", value=100.0)
    cst = col_b3.number_input("Costo Compra ($):", value=60.0)
    
    if (vta - cst) > 0:
        pe = fijos / (vta - cst)
        st.metric("Punto de Equilibrio", f"{int(pe)+1} Ventas", delta=f"${vta-cst} Margen/u")
    
    # --- 4. SCANNER IA & EXCEL ---
    st.markdown("---")
    c_web, c_excel = st.columns(2)
    with c_web:
        st.header("🔗 AI Web Scanner")
        url_in = st.text_input("URL Competencia (Daka, Amazon, etc):")
        if st.button("EJECUTAR ESCÁNER"):
            if url_in:
                with st.spinner("Analizando mercado en tiempo real..."):
                    bot = AnalizadorCompetencia()
                    res_web = bot.comparar_precios("Analiza precios y stock", url_in, nombre_empresa)
                    st.session_state['analisis_actual'] = res_web.content
                    st.markdown(res_web.content)
            else: st.warning("Ingresa una URL")

    with c_excel:
        st.header("📁 Auditoría Interna")
        archivo = st.file_uploader("Sube tu Inventario (Excel/CSV):", type=["xlsx", "csv"])
        if archivo:
            df_subido = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
            st.dataframe(df_subido.head(5), use_container_width=True)

    # --- 5. CHAT CONSULTOR IA ---
    st.markdown("---")
    st.header("🤖 Consultoría Estratégica IA")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p_chat := st.chat_input("¿Cómo puedo mejorar mis márgenes?"):
        st.session_state.messages.append({"role": "user", "content": p_chat})
        with st.chat_message("user"): st.markdown(p_chat)
        with st.chat_message("assistant"):
            bot_ia = AnalizadorCompetencia()
            res = bot_ia.comparar_precios(p_chat, url_in if url_in else "Mercado General", nombre_empresa)
            st.session_state['analisis_actual'] = res.content
            st.markdown(res.content)
            st.session_state.messages.append({"role": "assistant", "content": res.content})
            guardar_analisis(nombre_empresa, vta, cst, res.content)

    # --- 6. ENVÍO Y REPORTES ---
    if st.session_state['verificado'] and st.session_state['analisis_actual']:
        st.markdown("---")
        if st.button("📩 ENVIAR INFORME PDF/TEXTO AL CLIENTE", use_container_width=True):
            if enviar_correo(email_cliente, f"Reporte Estratégico - {nombre_empresa}", st.session_state['analisis_actual']):
                st.toast("Reporte enviado con éxito!")

    # --- 7. HISTORIAL Y GRÁFICAS ---
    st.markdown("---")
    st.header("📊 Historial de Inteligencia")
    h_data = obtener_historial()
    if h_data:
        for r in h_data[-3:]:
            with st.expander(f"Análisis del {r[1]}"):
                st.write(r[5])
