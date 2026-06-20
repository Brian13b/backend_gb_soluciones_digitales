import json
import os
import difflib

class ServicioManager:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'data_servicios.json')
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def obtener_respuesta_inteligente(self, query):
        nombres_servicios = [info['nombre'] for info in self.data.values()]
        
        mejor_coincidencia = difflib.get_close_matches(query, nombres_servicios, n=1, cutoff=0.3)
        
        if mejor_coincidencia:
            nombre = mejor_coincidencia[0]
            for key, info in self.data.items():
                if info['nombre'] == nombre:
                    return f"💡 *{info['nombre']}*: {info['descripcion']} - {info['detalles']}"
        
        return "No estoy seguro de qué servicio buscas. ¿Te refieres a Sistemas a medida, E-commerce, PWA, Gestión, SPA o Integración de APIs?"