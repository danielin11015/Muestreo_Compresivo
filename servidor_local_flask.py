from flask import Flask, request
import os

app = Flask(__name__)

# Imprimimos el banner de inicio
print("==================================================")
print(" SERVIDOR IOT - SISTEMA HÍBRIDO ECG")
print(" Esperando datos del ESP32...")
print("==================================================")

@app.route('/upload', methods=['POST'])
def upload_file():
    # Verificamos si la petición contiene un archivo
    if 'file' not in request.files:
        print("Error: Petición recibida sin archivo.")
        return "No file part", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 400
    
    # Guardamos el paquete que llegó por Wi-Fi con un nuevo nombre
    nuevo_nombre = "paquete_recibido.mat"
    file.save(nuevo_nombre)
    
    print("\n[+] ¡ALERTA! Paquete de datos biomédicos recibido.")
    print(f"[+] Archivo guardado como: {nuevo_nombre}")
    print("[+] Listo para reconstrucción OMP en MATLAB.\n")
    
    return "Datos recibidos correctamente por el Servidor", 200

if __name__ == '__main__':
    # El servidor se levanta en el puerto 5000 (Localhost)
    # Si quieres que escuche en toda tu red Wi-Fi (para enviar desde otra PC), 
    # cambia host='127.0.0.1' a host='0.0.0.0'
    app.run(host='127.0.0.1', port=5000)