from flask import Flask, render_template, request, send_from_directory
import cv2
import easyocr
import os
import random

app = Flask(__name__)

# Configurar el lector de EasyOCR
reader = easyocr.Reader(["es", "en", "fr", "de"], gpu=False)

# Configurar la carpeta de carga de archivos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.filters['uniform'] = random.uniform
# Ruta de la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para servir las imágenes cargadas
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Ruta para procesar la imagen cargada por el usuario
@app.route('/analyze', methods=['POST'])
def analyze():
    # Verifica si se ha enviado una imagen
    if 'file' not in request.files:
        return render_template('index.html', error='No se ha enviado ninguna imagen')
    
    # Obtiene la imagen cargada por el usuario
    file = request.files['file']
    
    # Verifica si el archivo tiene un nombre y es permitido
    if file.filename == '':
        return render_template('index.html', error='No se ha seleccionado ningún archivo')
    if not allowed_file(file.filename):
        return render_template('index.html', error='Tipo de archivo no permitido')
    
    # Guarda la imagen cargada en la carpeta de uploads
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    
    # Lee el texto de la imagen
    image = cv2.imread(filename)
    result = reader.readtext(image)
    text_results = [res[1] for res in result]
    
    # Renderiza los resultados en la plantilla result.html
    return render_template('result.html', text_results=text_results, filename=file.filename)

# Función para verificar si el tipo de archivo es permitido
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

if __name__ == '__main__':
    app.run(debug=True)
