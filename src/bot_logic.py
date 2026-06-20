from src.services.servicio_manager import ServicioManager

class BotLogic:
    def __init__(self):
        self.manager = ServicioManager()

    def procesar(self, mensaje):
        # Aquí es donde, en el futuro, llamarás a GPT-4o
        # Por ahora, usamos el ServicioManager que ya es "inteligente"
        return self.manager.obtener_respuesta_inteligente(mensaje)