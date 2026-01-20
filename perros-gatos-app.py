from flask import Flask, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

# Función de procesamiento (adapta esto a tu lógica del Colab)
def procesar_imagen(imagen_bytes):
    # Convertir bytes a imagen OpenCV
    nparr = np.frombuffer(imagen_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"error": "No se pudo leer la imagen"}
    
    # Ejemplo muy simple de "clasificación" (sustituye por tu modelo real)
    # Por ejemplo: detección de bordes o color promedio
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 100, 200)
    
    # Dummy: si hay muchos bordes → asumimos "perro", sino "gato"
    densidad_bordes = np.mean(edges) / 255
    animal = "perro" if densidad_bordes > 0.12 else "gato"
    
    # Resultado
    return {
        "animal": animal,
        "confianza": round(float(densidad_bordes), 3),
        "dimensiones": f"{img.shape[1]}x{img.shape[0]}",
        "tamaño_kb": round(len(imagen_bytes)/1024, 1)
    }

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>App Perros y Gatos con OpenCV</h1>
    <p>Sube una foto a: <code>/analizar</code> (POST multipart/form-data, campo 'imagen')</p>
    <p>Ejemplo con curl:</p>
    <pre>curl -X POST -F "imagen=@tu_foto.jpg" https://tu-app.vercel.app/analizar</pre>
    """

@app.route('/analizar', methods=['POST'])
def analizar():
    if 'imagen' not in request.files:
        return jsonify({"error": "Falta el campo 'imagen'"}), 400
    
    file = request.files['imagen']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó archivo"}), 400
    
    try:
        imagen_bytes = file.read()
        resultado = procesar_imagen(imagen_bytes)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Muy importante para Vercel (exporta la app como variable global)
# No uses app.run() aquí