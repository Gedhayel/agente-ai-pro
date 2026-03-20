import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq # Cambiamos esto
from dotenv import load_dotenv
import os

load_dotenv()

class AnalizadorCompetencia:
    def __init__(self):
        # Usamos Groq que es gratis y vuela
        self.llm = ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY") # Pon tu llave en el .env
        )

    def comparar_precios(self, mis_productos, datos_competencia):
        prompt_template = """
        Eres un experto analista de precios.
        MIS PRODUCTOS: {mis_productos}
        COMPETENCIA: {datos_competencia}
        
        Crea una tabla comparativa y dime qué estrategia usar para ganarles.
        """
        prompt = PromptTemplate(input_variables=["mis_productos", "datos_competencia"], template=prompt_template)
        cadena = prompt | self.llm
        return cadena.invoke({"mis_productos": mis_productos, "datos_competencia": datos_competencia})