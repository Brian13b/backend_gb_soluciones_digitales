import os
from openai import OpenAI
from src.services.servicio_manager import ServicioManager

class BotLogic:
    def __init__(self):
        self.manager = ServicioManager()
        self.client = OpenAI()

    def procesar(self, mensaje):
        # Obtenemos el catalogo de servicios relevante para la consulta
        contexto_servicios = self.manager.obtener_respuesta_inteligente(mensaje)
        
        # Armamos el Prompt (La personalidad del bot)
        system_prompt = f"""Eres el asistente virtual de GB Soluciones Digitales.
        Tu objetivo es responder consultas técnicas y comerciales sobre nuestros servicios de forma profesional y clara.
        Utiliza estrictamente la siguiente información para responder:
        {contexto_servicios}
        Si te preguntan algo que no está en la información, ofrece derivar la consulta a un desarrollador de nuestro equipo."""

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
            # Fallback de seguridad si falla la API
            return contexto_servicios