import json
import codecs

f2_text = """Ley N° 29571, Código de Protección y Defensa del Consumidor.\\nArtículo 1°.- Derechos de los consumidores\\n1.1 En los términos establecidos por el presente Código, los consumidores tienen los siguientes derechos:\\n(…)\\nb) Derecho a acceder a información oportuna, suficiente, veraz y fácilmente accesible, relevante para tomar una decisión o realizar una elección de consumo que se ajuste a sus intereses, así como para efectuar un uso o consumo adecuado de los productos o servicios.\\n(…)\\n\\nArtículo 2°.- Información relevante\\n2.1 El proveedor tiene la obligación de ofrecer al consumidor toda la información relevante para tomar una decisión o realizar una elección adecuada de consumo, así como para efectuar un uso o consumo adecuado de los productos o servicios.\\n2.2 La información debe ser veraz, suficiente, de fácil comprensión, apropiada, oportuna y fácilmente accesible, debiendo ser brindada en idioma castellano.\\n2.3 Sin perjuicio de las exigencias concretas de las normas sectoriales correspondientes, para analizar la información relevante se tiene en consideración a los consumidores a los que se dirige, la clase y características de los productos o servicios, así como toda otra circunstancia o dato objetivo que permita a los consumidores establecer una elección de consumo racional y reflexiva o su uso o consumo adecuado.\\n2.4 La información relevante sobre bienes o servicios que por su naturaleza puedan tener una alta probabilidad de predecibilidad en cuanto a los efectos de su uso se brinda en términos comprobables.\\n2.5 Se presume que todo consumidor es racional y reflexivo respecto de los productos y servicios que en la experiencia común le son conocidos. En ningún caso se asume que un consumidor puede razonablemente acceder a información adicional que no le hubiese sido provista, sobre lo cual el proveedor debe asumir las consecuencias."""

with open('automatizacion_antigravity/casos/2190-2026.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The user wants the footnote on the first mention.
# Paragraph 5 in the Word doc corresponds to imputaciones_analisis index 2.
if not data['imputaciones_analisis'][2].endswith('__F2__'):
    data['imputaciones_analisis'][2] = data['imputaciones_analisis'][2] + '__F2__'

data['footnotes']['__F2__'] = f2_text.replace('\\n', '\n')

with open('automatizacion_antigravity/casos/2190-2026.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
