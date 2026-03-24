import streamlit as st
import pandas as pd
import plotly.express as px
import base64, smtplib, random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scraping import AnalizadorCompetencia
from database import obtener_historial, crear_tabla, guardar_analisis 

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Arbitrage & BI Pro", page_icon="📈", layout="wide")
crear_tabla()

st.markdown("""
<style>
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .whatsapp-button {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #25D366; color: white !important; font-weight: bold;
        padding: 12px; border-radius: 10px; text-decoration: none !important;
        width: 100%; margin-top: 10px; transition: 0.3s;
    }
    .whatsapp-button:hover { background-color: #128C7E; transform: translateY(-2px); }
    .whatsapp-icon { width: 20px; height: 20px; margin-right: 10px; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def enviar_correo(destinatario, asunto, cuerpo):
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = remitente, destinatario, asunto
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

# 2. SISTEMA DE SESIÓN
if 'auth' not in st.session_state: st.session_state.auth = False
if 'verificado' not in st.session_state: st.session_state.verificado = False
if 'analisis_actual' not in st.session_state: st.session_state.analisis_actual = ""
if 'messages' not in st.session_state: st.session_state.messages = []

if not st.session_state.auth:
    st.title("🔐 Acceso al Monitor BI")
    u, p = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
    if st.button("INGRESAR AL TERMINAL", use_container_width=True):
        if u.lower() == "admin" and p == "1234":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Credenciales incorrectas")
else:
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.success("✅ Conexión Encriptada")
        nombre_empresa = st.text_input("Nombre Empresa:", value="Mi Negocio")
        email_cliente = st.text_input("Email para reportes:")
        
        if st.button("Enviar Código de Seguridad"):
            if email_cliente:
                codigo = str(random.randint(1000, 9999))
                st.session_state.codigo_sesion = codigo
                if enviar_correo(email_cliente, "Código de Acceso BI", f"Tu código es: {codigo}"):
                    st.info("Código enviado al correo.")
        
        if st.text_input("Verificar Código:") == st.session_state.get('codigo_sesion'):
            st.session_state.verificado = True
            st.success("Verificado ✅")

        st.markdown("---")
        wa_url = "https://wa.me/584120000000"
        wa_icon = "https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-button"><img src="{wa_icon}" class="whatsapp-icon"> SOPORTE WHATSAPP</a>', unsafe_allow_html=True)
        
        if st.button("Cerrar Sesión"):
            st.session_state.clear()
            st.rerun()

    # --- CUERPO PRINCIPAL ---
    st.title(f"📊 Dashboard de Arbitraje: {nombre_empresa}")

    # 3. MÉTRICAS Y PUNTO DE EQUILIBRIO
    st.markdown("---")
    col_pe1, col_pe2, col_pe3, col_pe4 = st.columns(4)
    gastos_f = col_pe1.number_input("Gastos Fijos ($):", value=1200.0)
    p_vta = col_pe2.number_input("Precio Venta ($):", value=50.0)
    p_cst = col_pe3.number_input("Costo Compra ($):", value=30.0)
    
    margen_u = p_vta - p_cst
    if margen_u > 0:
        pe_unidades = gastos_f / margen_u
        col_pe4.metric("Punto de Equilibrio", f"{int(pe_unidades)+1} Unidades", f"${margen_u} Margen/u")
    else: col_pe4.error("Ajusta los precios")

    # 4. RADAR DE PRODUCTOS Y TABLA FINANCIERA
    st.markdown("---")
    st.subheader("📦 Radar de Productos y Proyección de Capital")
    
    col_tab1, col_tab2 = st.columns([2, 1])
    
    with col_tab1:
        reventa_data = {
            "Producto": ["Audífonos Pro", "Teclado RGB", "Cámara 4K", "Monitor 144Hz"],
            "Costo Mayor ($)": [15, 25, 45, 120],
            "Venta Detalle ($)": [45, 65, 110, 220]
        }
        df_rev = pd.DataFrame(reventa_data)
        df_rev["Ganancia ($)"] = df_rev["Venta Detalle ($)"] - df_rev["Costo Mayor ($)"]
        df_rev["ROI %"] = (df_rev["Ganancia ($)"] / df_rev["Costo Mayor ($)"]) * 100
        st.write("**Oportunidades de Reventa:**")
        st.dataframe(df_rev, use_container_width=True)

    with col_tab2:
        inv_input = st.number_input("Inversión Inicial ($):", value=1000.0)
        porc_obj = st.slider("Margen Objetivo %:", 5, 100, 25)
        gan_estimada = inv_input * (porc_obj / 100)
        
        fin_data = {
            "Periodo": ["Semanal", "Mensual", "Anual"],
            "Ganancia Est. ($)": [gan_estimada, gan_estimada * 4, gan_estimada * 48]
        }
        st.write("**Rentabilidad Proyectada:**")
        st.table(pd.DataFrame(fin_data))

    # 5. SCANNER IA Y EXCEL
    st.markdown("---")
    c_scan, c_file = st.columns(2)
    
    with c_scan:
        st.subheader("🔗 AI Web Scanner")
        url_in = st.text_input("URL Competencia:", placeholder="https://tienda.com")
        if st.button("EJECUTAR ESCÁNER Y ENVIAR", use_container_width=True):
            if url_in:
                with st.spinner("IA analizando mercado..."):
                    bot = AnalizadorCompetencia()
                    res_web = bot.comparar_precios("Analiza precios y competencia", url_in, nombre_empresa)
                    st.session_state.analisis_actual = res_web.content
                    st.markdown(res_web.content)
                    
                    # Envío automático si está verificado
                    if st.session_state.verificado and email_cliente:
                        enviar_correo(email_cliente, f"Reporte Automático - {nombre_empresa}", res_web.content)
                        st.toast("✅ Reporte enviado al correo")
            else: st.warning("Pega una URL")

    with c_file:
        st.subheader("📁 Auditoría de Inventario")
        archivo = st.file_uploader("Sube Excel o CSV:", type=["xlsx", "csv"])
        if archivo:
            df_subido = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
            st.dataframe(df_subido.head(5), use_container_width=True)

    # 6. CONSULTORÍA IA (CHAT)
    st.markdown("---")
    st.subheader(f"🤖 Consultor Estratégico IA")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p_chat := st.chat_input("Pregúntale a la IA..."):
        st.session_state.messages.append({"role": "user", "content": p_chat})
        with st.chat_message("user"): st.markdown(p_chat)
        with st.chat_message("assistant"):
            bot_ia = AnalizadorCompetencia()
            ctx = f"Contexto previo: {st.session_state.analisis_actual}. Pregunta: {p_chat}"
            res_c = bot_ia.comparar_precios(ctx, url_in if url_in else "Mercado", nombre_empresa)
            st.markdown(res_c.content)
            st.session_state.messages.append({"role": "assistant", "content": res_c.content})
            guardar_analisis(nombre_empresa, inv_input, gan_estimada, res_c.content)

    # 7. TENDENCIAS E HISTORIAL
    st.markdown("---")
    col_g, col_h = st.columns([2, 1])
    with col_g:
        st.subheader("📈 Tendencia de Crecimiento")
        proyeccion = [inv_input + (gan_estimada * i) for i in range(13)]
        fig = px.area(y=proyeccion, x=list(range(13)), template="plotly_dark")
        fig.update_traces(line_color='#00c853', fillcolor='rgba(0, 200, 83, 0.3)')
        st.plotly_chart(fig, use_container_width=True)
    with col_h:
        st.subheader("📜 Reportes Guardados")
        h_data = obtener_historial()
        if h_data:
            for r in h_data[-3:]:
                with st.expander(f"📅 {r[1]}"): st.write(r[5])

    st.markdown(descargar_excel(df_rev), unsafe_allow_html=True)
