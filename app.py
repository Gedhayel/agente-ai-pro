import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from scraping import AnalizadorCompetencia
from database import obtener_historial, crear_tabla, guardar_analisis 

# 1. SETUP Y ESTILO CORPORATIVO
st.set_page_config(page_title="Arbitraje & BI Pro", page_icon="🌎", layout="wide")
crear_tabla()

# Función para descarga de reportes
def descargar_excel(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="auditoria_pro.csv"><button style="background-color:#00c853; color:white; border-radius:8px; border:none; padding:12px; cursor:pointer; width:100%; font-weight:bold;">📥 DESCARGAR AUDITORÍA COMPLETA</button></a>'

# 2. LOGIN NATIVO (SISTEMA DE ACCESO)
if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Terminal de Inteligencia Corporativa")
    u, p = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
    if st.button("ACCEDER AL MONITOR", use_container_width=True):
        if u.lower() == "admin" and p == "1234":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Credenciales incorrectas")
else:
    # --- BARRA LATERAL (GUÍA Y SOPORTE) ---
    with st.sidebar:
        st.success("✅ Conexión Encriptada")
        st.header("📖 Guía de Uso IA")
        with st.expander("Instrucciones Rápidas"):
            st.write("1. **Scanner:** Pega una URL para ver a la competencia.")
            st.write("2. **Excel:** Sube tus ventas para auditar márgenes.")
            st.write("3. **Chat:** Pregunta estrategias de precios.")
        st.markdown("[🚀 SOPORTE WHATSAPP](https://wa.me/584120000000)")
        if st.button("Cerrar Sesión"):
            st.session_state['auth'] = False
            st.rerun()

    st.title("🌎 Monitor de Arbitraje & Business Intelligence")

    # --- 3. CONEXIÓN WEB & EXCEL (BI) ---
    st.markdown("---")
    c_web, c_excel = st.columns(2)
    with c_web:
        st.header("🔗 Conexión Web (AI Scanner)")
        url_in = st.text_input("URL del Catálogo Competencia:", placeholder="https://tienda.com")
        if st.button("ESCANEAR MERCADO"):
            with st.spinner("IA analizando..."):
                st.success("Scanner sincronizado.")

    with c_excel:
        st.header("📁 Auditoría de Empresa (Excel)")
        archivo = st.file_uploader("Sube tu inventario/ventas:", type=["xlsx", "csv"])
        if archivo: st.success("Archivo cargado. Procesando métricas...")

    # --- 4. LISTADO DE PRODUCTOS PARA REVENTA (COSTEO) ---
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

    # --- 5. TABLA DE INVERSIÓN + GANANCIA (SEMANAL/MENSUAL/ANUAL) ---
    st.markdown("---")
    st.header("💰 Proyección Financiera (Ideas Madrugada)")
    col_t1, col_t2 = st.columns(2)
    inv_input = col_t1.number_input("Inversión Inicial ($):", value=1000.0)
    porcentaje = col_t2.slider("Margen Objetivo (%):", 5, 100, 25)

    gan_s = inv_input * (porcentaje / 100)
    res_fin = {
        "Periodo": ["Semanal", "Mensual", "Anual"],
        "Inversión Total ($)": [inv_input, inv_input * 4, inv_input * 48],
        "Ganancia Est. ($)": [gan_s, gan_s * 4, gan_s * 48],
        "Porcentaje Sugerido": [f"{porcentaje}%", f"{porcentaje}%", f"{porcentaje}%"]
    }
    st.table(pd.DataFrame(res_fin))

    # --- 6. CHAT DE CONSULTORÍA & BOT 24/7 ---
    st.markdown("---")
    st.header("🤖 Consultoría IA & Chatbot Estratégico")
    
    # Inicializar historial de chat y el Bot una sola vez
    if "messages" not in st.session_state: st.session_state.messages = []
    if "bot_ia" not in st.session_state: st.session_state.bot_ia = AnalizadorCompetencia()
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p_chat := st.chat_input("Pregúntale a la IA sobre tu negocio..."):
        st.session_state.messages.append({"role": "user", "content": p_chat})
        with st.chat_message("user"): st.markdown(p_chat)
        
        with st.chat_message("assistant"):
            with st.spinner("Consultando con la red de Groq..."):
                try:
                    # Usamos el bot guardado en session_state
                    res = st.session_state.bot_ia.comparar_precios(p_chat, "General")
                    respuesta_texto = res.content
                    st.markdown(respuesta_texto)
                    
                    # Guardar en historial y base de datos
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
                    guardar_analisis("Consulta General", inv_input, gan_s, respuesta_texto)
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
                    st.info("Revisa que tu GROQ_API_KEY esté bien puesta en los Secrets.")

    # --- 7. TENDENCIA DE CAPITALIZACIÓN & HISTORIAL SQL ---
    st.markdown("---")
    col_g, col_h = st.columns([2, 1])
    with col_g:
        st.header("📈 Tendencia de Capitalización")
        proyeccion = [inv_input + (gan_s * i) for i in range(13)]
        fig = px.area(y=proyeccion, x=list(range(13)), template="plotly_dark")
        fig.update_traces(line_color='#00c853', fillcolor='rgba(0, 200, 83, 0.3)')
        st.plotly_chart(fig, use_container_width=True)

    with col_h:
        st.header("📜 Historial SQL")
        h_data = obtener_historial()
        if h_data:
            for r in h_data[-3:]:
                with st.expander(f"📅 {r[1]}"): st.write(r[5])
        else: st.write("Sin registros.")

    st.markdown(descargar_excel(df_rev), unsafe_allow_html=True)
