import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from bot.services.servicio_manager import ServicioManager

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

    def _cargar_system_prompt(self):
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_prompt = os.path.join(ruta_actual, "SYSTEM_PROMPT.md")
        try:
            with open(ruta_prompt, "r", encoding="utf-8") as archivo:
                return archivo.read()
        except Exception as e:
            print(f"❌ Error cargando System Prompt: {e}")
            return "Eres el asistente de GB Soluciones Digitales."
        
    def _parse_extraction_json(self, text: str) -> dict:
        pattern = r'\[CONTACT_EXTRACTION\](.*?)\[\/CONTACT_EXTRACTION\]'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            json_str = match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️ Error parseando el JSON de extracción: {e}")
                return {}
        return {}
    
    def _strip_extraction_markers(self, text: str) -> str:
        pattern = r'\[CONTACT_EXTRACTION\].*?\[\/CONTACT_EXTRACTION\]'
        clean_text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE).strip()
        return clean_text

    def procesar(self, mensaje, history=[], channel="web", datos_confirmados=None, webhook_phone=None):
        if not self.client:
            return {
                "respuesta": "Modo offline activado.",
                "extracted_contact": {}
            }

        catalogo = self.manager.obtener_catalogo_completo()
        system_prompt_base = self._cargar_system_prompt()

        system_prompt = system_prompt_base.replace("{catalogo}", catalogo)
        system_prompt += f"\n\nCONTEXTO DE CANAL: El usuario se comunica a través de {channel}."

        if webhook_phone:
            system_prompt += f"\nEl número de teléfono de origen del usuario es: {webhook_phone}. Si el usuario indica 'este mismo', 'el mío' o similar al pedirle su número, DEBES extraer exactamente este número en el JSON."

        if datos_confirmados:
            system_prompt += f"\n\nREGLA ESTRICTA - DATOS YA CONFIRMADOS DEL USUARIO:\n"
            for campo, valor in datos_confirmados.items():
                if valor:
                    system_prompt += f"- {campo.capitalize()}: {valor} (NO vuelvas a pedir esta información bajo ninguna circunstancia)\n"
                    
        mensajes_api = [{"role": "system", "content": system_prompt}]
        mensajes_api.extend(history)
        mensajes_api.append({"role": "user", "content": mensaje})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=mensajes_api,
                temperature=0.3,
                max_tokens=400
            )
            raw_response = response.choices[0].message.content
            
            extracted_data = self._parse_extraction_json(raw_response)
            
            respuesta_visible = self._strip_extraction_markers(raw_response)
            
            return {
                "respuesta": respuesta_visible,
                "extracted_contact": extracted_data
            }
            
        except Exception as e:
            print(f"Error de conexión con OpenAI: {e}")
            return {
                "respuesta": "Hubo un error al procesar tu consulta.",
                "extracted_contact": {}
            }