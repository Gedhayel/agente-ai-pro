import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class ProcesadorFacturas:
    def __init__(self):
        # Usamos Llama 3.3 70B: es increíblemente preciso para leer datos estructurados
        self.llm = ChatGroq(
            temperature=0, # 0 para que sea exacto con los números y no invente nada
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def extraer_datos_factura(self, texto_factura):
        prompt_template = """
        Eres un experto contable y auditor de sistemas. Tu tarea es extraer información 
        clave de este texto de factura y organizarla.

        TEXTO DE LA FACTURA:
        {texto_factura}

        POR FAVOR, RESPONDE CON ESTE FORMATO:
        ---
        ### 📄 Resumen de Factura
        * **Nro de Factura:** [Número]
        * **Fecha de Emisión:** [Fecha]
        * **Proveedor:** [Nombre de la empresa/persona]
        * **RIF/Identificación:** [Número fiscal]
        
        ### 💰 Desglose Financiero
        * **Subtotal:** [Monto]
        * **Impuestos (IVA):** [Monto]
        * **Monto Total:** [Monto Final]

        ### 🔍 Comentario del Auditor:
        [Escribe aquí si detectas algo extraño o si la factura es válida]
        ---
        """
        
        prompt = PromptTemplate(
            input_variables=["texto_factura"],
            template=prompt_template
        )
        
        cadena = prompt | self.llm
        
        respuesta = cadena.invoke({
            "texto_factura": texto_factura
        })
        
        return respuesta.content # .content para que solo nos de el texto limpio

# Ejemplo de uso:
# procesador = ProcesadorFacturas()
# print(procesador.extraer_datos_factura("Factura #001 - Tienda Tech - Total: 150$"))