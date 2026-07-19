import win32com.client
import os

doc_path = os.path.abspath(r"C:\Users\Admin\.gemini\antigravity\scratch\resolucion_temp_exp2190.docx")
out_path = os.path.abspath(r"D:\CC1\productos (resoluciones) elaborada por google antigravity\ADM 2190-2026 R2 v5.docx")

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

doc = word.Documents.Open(doc_path)

footnotes_data = {
    "__F1__": "Ley N° 29571, Código de Protección y Defensa del Consumidor.\nArtículo 18°.- Idoneidad\nSe entiende por idoneidad la correspondencia entre lo que un consumidor espera y lo que efectivamente recibe, en función a lo que se le hubiera ofrecido, la publicidad e información transmitida, las condiciones y circunstancias de la transacción, las características y naturaleza del producto o servicio, el precio, entre otros factores, atendiendo a las circunstancias del caso.\nLa idoneidad es evaluada en función a la propia naturaleza del producto o servicio y a su aptitud para satisfacer la finalidad para la cual ha sido puesto en el mercado.\nLas autorizaciones por parte de los organismos del Estado para la fabricación de un producto o la prestación de un servicio, en los casos que sea necesario, no eximen de responsabilidad al proveedor frente al consumidor.\n\nArtículo 19°.- Obligación de los proveedores\nEl proveedor responde por la idoneidad y calidad de los productos y servicios ofrecidos; por la autenticidad de las marcas y leyendas que exhiben sus productos o del signo que respalda al prestador del servicio, por la falta de conformidad entre la publicidad comercial de los productos y servicios y éstos, así como por el contenido y la vida útil del producto indicado en el envase, en lo que corresponda.",
    "__F2__": "Decreto Supremo N° 006-2026-JUS, que aprueba el Texto Único Ordenado de la Ley N° 27444, Ley del Procedimiento Administrativo General.\nArtículo 20°.- Modalidades de notificación\n20.1 Las notificaciones serán efectuadas a través de las siguientes modalidades, según este respectivo orden de prelación:\n(...)\n20.1.2. Mediante correo electrónico u otro medio electrónico, siempre que el administrado haya autorizado expresamente y por escrito a la autoridad administrativa para ello. El plazo para la confirmación de recepción es de dos (2) días hábiles.\n(...)\n20.4 (...) El administrado que autorice la notificación electrónica asume la obligación de comunicar cualquier cambio de dirección electrónica y de confirmarla conforme a lo dispuesto en el numeral 20.1.2."
}

for key, footnote_text in footnotes_data.items():
    word.Selection.HomeKey(Unit=6) # wdStory
    find = word.Selection.Find
    find.Text = key
    find.Execute()
    if find.Found:
        # Delete the marker
        word.Selection.Delete()
        # Add footnote
        word.Selection.Footnotes.Add(Range=word.Selection.Range, Text=footnote_text)

# Set footers font size and name (Arial Narrow 10)
for fn in doc.Footnotes:
    fn.Range.Font.Name = "Arial Narrow"
    fn.Range.Font.Size = 10
    fn.Range.ParagraphFormat.Alignment = 3 # wdAlignParagraphJustify

doc.SaveAs(out_path)
doc.Close()
word.Quit()
print("Footnotes added and document saved successfully.")
