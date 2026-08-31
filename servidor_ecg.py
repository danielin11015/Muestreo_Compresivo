import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, request
import threading
import queue
from scipy.fftpack import dct
import time

# =========================================================================
# 1. CONFIGURACIÓN DE PARÁMETROS GLOBALES
# =========================================================================
N = 50          # Tamaño de la trama original
M = 25          # Muestras comprimidas que envía el ESP32
sparsity = 10   # Nivel de esparsidad para OMP
K1_original = 50.0 / 100.0  # Llave caótica 1 (0.50)
NI = 1          # Iteraciones del caos

# Diccionario DCT (Psi)
Psi = dct(np.eye(N), axis=0, norm='ortho')

# Reemplaza esto con los números de tu matriz Phi generada en MATLAB
# Una matriz aleatoria de ejemplo, pero DEBE ser idéntica a la del ESP32
np.random.seed(42)
Phi = np.random.randn(M, N)
Phi, _ = np.linalg.qr(Phi.T)
Phi = Phi.T 

# Matriz de reconstrucción A
A_matrix = np.dot(Phi, Psi)

# Cola de datos para no congelar la interfaz gráfica
cola_datos = queue.Queue()
app = Flask(__name__)

# =========================================================================
# 2. FUNCIONES MATEMÁTICAS Y DE SEGURIDAD
# =========================================================================
def descifrar_1d(y_cifrado, M_dim, K1, iters):
    """ Descifra el arreglo invirtiendo el algoritmo de ordenamiento caótico """
    z = np.zeros(M_dim)
    for _ in range(iters):
        z[0] = K1
        for i in range(M_dim - 1):
            z[i+1] = 1.0 - 2.0 * z[i]**2
        
        # Obtener los índices originales del ordenamiento
        indices = np.argsort(z)
        
        # Revertir la mezcla
        y_descifrado = np.zeros(M_dim)
        for i in range(M_dim):
            y_descifrado[indices[i]] = y_cifrado[i]
            
    return y_descifrado

def omp(y, A, sparsity_level):
    """ Algoritmo Orthogonal Matching Pursuit """
    residual = y.copy()
    idx = []
    alpha = np.zeros(A.shape[1])
    for _ in range(sparsity_level):
        proyecciones = np.abs(np.dot(A.T, residual))
        pos = np.argmax(proyecciones)
        idx.append(pos)
        
        A_k = A[:, idx]
        x_k, _, _, _ = np.linalg.lstsq(A_k, y, rcond=None)
        residual = y - np.dot(A_k, x_k)
        
    for i, p in enumerate(idx):
        alpha[p] = x_k[i]
    return alpha

# =========================================================================
# 3. SERVIDOR WEB FLASK (Corre en segundo plano)
# =========================================================================
@app.route('/upload', methods=['POST'])
def upload():
    datos_crudos = request.data.decode('utf-8')
    cola_datos.put(datos_crudos) # Mandamos los datos al hilo principal
    return "OK", 200

def iniciar_servidor():
    # Desactivamos el reloader para evitar conflictos con hilos
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# =========================================================================
# 4. HILO PRINCIPAL: PROCESAMIENTO Y GRÁFICAS
# =========================================================================
if __name__ == '__main__':
    print("Iniciando Servidor Flask en segundo plano...")
    threading.Thread(target=iniciar_servidor, daemon=True).start()
    
    print("Iniciando Monitor Médico...")
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    buffer_ecg = np.zeros(300) # Mostraremos 300 muestras en pantalla (1.5 seg)
    
    linea_ecg, = ax.plot(buffer_ecg, color='red', linewidth=1.5)
    ax.set_ylim(-3.0, 3.0) # Rango de voltajes (ajústalo según tu sensor)
    ax.set_xlim(0, 300)
    ax.set_title("Monitor ECG: Reconstrucción OMP en Tiempo Real")
    ax.set_ylabel("Amplitud Centrada")
    ax.set_xlabel("Muestras")
    ax.grid(True)
    
    while True:
        try:
            # Procesar datos solo si hay paquetes nuevos
            while not cola_datos.empty():
                datos = cola_datos.get()
                y_recibido = np.array([float(val) for val in datos.strip().split('\n')])
                
                if len(y_recibido) == M:
                    # 1. Descifrar
                    y_descifrado = descifrar_1d(y_recibido, M, K1_original, NI)
                    
                    # 2. Descomprimir (OMP)
                    s_recuperado = omp(y_descifrado, A_matrix, sparsity)
                    
                    # 3. Transformada inversa (Señal en el tiempo)
                    ecg_recuperado = np.dot(Psi, s_recuperado)
                    
                    # 4. Actualizar pantalla (Desplazar buffer y meter datos nuevos)
                    buffer_ecg = np.roll(buffer_ecg, -N)
                    buffer_ecg[-N:] = ecg_recuperado
                    
                    linea_ecg.set_ydata(buffer_ecg)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                    print("Trama procesada y graficada.")
                    
        except Exception as e:
            print(f"Error procesando trama: {e}")
            
        plt.pause(0.01) # Mantiene viva la ventana gráfica