import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

class AnalizadorCompetencia:
    def __init__(self):
        # Este es el "puente" que busca la clave en el panel de Secrets de Streamlit
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            
    groq_api_key=st.secrets["GROQ_API_KEY"]
        )

    def comparar_precios(self, mis_productos, datos_competencia):
        template = """
        Eres un experto analista de precios. 
        Compara mis productos con los de la competencia:
        Mis productos: {mis_productos}
        Competencia: {datos_competencia}
        Dame un análisis breve de dónde estoy caro o barato.
        """
        prompt = PromptTemplate.from_template(template)
        cadena = prompt | self.llm
        return cadena.invoke({"mis_productos": mis_productos, "datos_competencia": datos_competencia})
