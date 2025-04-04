from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
from fpdf import FPDF
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Arquivo: {filename}")
    
    output_pdf = "documento_final.pdf"
    pdf.output(output_pdf)
    
    return send_file(output_pdf, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
