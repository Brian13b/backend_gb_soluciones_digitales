import json
import os

class ServicioManager:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'data_servicios.json')
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def obtener_catalogo_completo(self):
        catalogo_texto = ""
        for key, info in self.data.items():
            catalogo_texto += f"- {info['nombre']}: {info['descripcion']}\n"
        return catalogo_texto