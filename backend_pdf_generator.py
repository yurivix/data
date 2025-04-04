from flask import Flask, request, send_file, render_template_string
from werkzeug.utils import secure_filename
from fpdf import FPDF
from PyPDF2 import PdfMerger
from PIL import Image
import os
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
TEMP_PDF_FOLDER = "temp_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_PDF_FOLDER, exist_ok=True)

HTML_FORM = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Gerador de PDF</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 0 12px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        input, button {
            display: block;
            width: 100%;
            margin-top: 10px;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 16px;
        }
        button {
            background-color: #2e8b57;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #246b45;
        }
    </style>
</head>
<body>
    <h1>Gerador de PDF</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label for="files">Selecione arquivos PDF ou imagens:</label>
        <input type="file" name="files" multiple required>
        <label for="filename">Nome do PDF final:</label>
        <input type="text" name="filename" placeholder="documento_final.pdf">
        <button type="submit">Gerar PDF</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_FORM)

@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")
    output_name = request.form.get("filename") or "documento_final.pdf"
    if not output_name.endswith(".pdf"):
        output_name += ".pdf"

    pdf_merger = PdfMerger()
    temp_pdfs = []

    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(filepath)
            image_rgb = image.convert("RGB")
            temp_pdf_path = os.path.join(TEMP_PDF_FOLDER, filename + ".pdf")
            image_rgb.save(temp_pdf_path)
            temp_pdfs.append(temp_pdf_path)
        elif filename.lower().endswith(".pdf"):
            temp_pdfs.append(filepath)

    final_pdf_path = os.path.join(TEMP_PDF_FOLDER, output_name)
    pdf_merger.write(final_pdf_path)
    pdf_merger.close()

    response = send_file(final_pdf_path, as_attachment=True)

    @app.after_request
    def cleanup(response):
        try:
            shutil.rmtree(UPLOAD_FOLDER)
            shutil.rmtree(TEMP_PDF_FOLDER)
        except Exception as e:
            app.logger.error(f"Erro ao limpar pastas: {e}")
        finally:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            os.makedirs(TEMP_PDF_FOLDER, exist_ok=True)
        return response

    return response

if __name__ == "__main__":
    app.run(debug=True)
