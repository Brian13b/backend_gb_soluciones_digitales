import os
from dotenv import load_dotenv
from openai import OpenAI
from src.services.servicio_manager import ServicioManager

load_dotenv()

class BotLogic:
    def __init__(self):
        self.manager = ServicioManager()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.startswith("sk-"):
            self.client = OpenAI(api_key=api_key)
            print("✅ Conexión con OpenAI establecida.")
        else:
            self.client = None

    def procesar(self, mensaje):
        if not self.client:
            return "Modo offline activado."

        catalogo = self.manager.obtener_catalogo_completo()

        system_prompt = f"""Eres el asistente virtual experto de GB Soluciones Digitales.
        Tu trabajo es atender a los clientes de forma amable, profesional y concisa.

        NUESTRO CATÁLOGO DE SERVICIOS:
        {catalogo}

        REGLAS DE RESPUESTA:
        1. Consulta de Servicios: Si preguntan por nuestros servicios, usa la información del catálogo para asesorarlos.
        2. Fuera de alcance: Si preguntan por algo que NO hacemos (ej. "venden tornillos", ropa, hardware), responde amablemente que somos una agencia de desarrollo de software y no ofrecemos esos productos.
        3. Traspaso Humano: Si el cliente pide hablar con un humano, un desarrollador o una persona real, responde EXACTAMENTE esto: "Ya notifiqué a uno de nuestros desarrolladores. En cuanto se desocupe, te escribirá por este medio para asesorarte personalmente."
        4. E-commerce: Si consultan por tiendas virtuales, aclara que la modalidad de trabajo para estos proyectos no incluye pasarelas de pago automatizadas, sino que se integran con WhatsApp para que el comercio cierre la venta en trato directo con su cliente.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": mensaje}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error de conexión con OpenAI: {e}")
            return "Hubo un error al procesar tu consulta."