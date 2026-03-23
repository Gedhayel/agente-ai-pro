import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

class AnalizadorCompetencia:
    def __init__(self):
        # Conexión con los Secrets de Streamlit
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=st.secrets["GROQ_API_KEY"]
        )

    def comparar_precios(self, mis_productos, url_competencia, nombre_empresa="Mi Negocio"):
        # 1. Extraer datos de la web (Web Scraping real)
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url_competencia, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Sacamos el texto limpio de la web para que la IA lo analice
            datos_competencia = soup.get_text()[:5000] # Limitamos a 5000 carácteres para no saturar
        except Exception as e:
            datos_competencia = f"No se pudo extraer datos de la web. Error: {e}"

        # 2. Configurar el Prompt para la IA
        template = """
        Eres un experto analista de BI para la empresa {nombre_empresa}. 
        Analiza la siguiente información:
        
        MIS PRODUCTOS/CONSULTA: {mis_productos}
        DATOS EXTRAÍDOS DE LA COMPETENCIA: {datos_competencia}
        URL ANALIZADA: {url_competencia}

        INSTRUCCIONES:
        1. Identifica productos similares y compara precios.
        2. Dime dónde estamos más caros o baratos.
        3. Dame 3 estrategias de 'Arbitraje' para maximizar ganancia.
        4. Responde con un tono profesional y directo.
        """
        
        prompt = PromptTemplate.from_template(template)
        cadena = prompt | self.llm
        
        # 3. Ejecutar y devolver resultado
        return cadena.invoke({
            "mis_productos": mis_productos, 
            "datos_competencia": datos_competencia,
            "url_competencia": url_competencia,
            "nombre_empresa": nombre_empresa
        })
