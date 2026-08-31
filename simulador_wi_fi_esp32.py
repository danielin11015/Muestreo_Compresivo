import requests
import time

# Configuración de red
# Si tu servidor está en otra computadora, cambia 127.0.0.1 por la IP de esa computadora
URL_SERVIDOR = 'http://127.0.0.1:5000/upload' 
ARCHIVO_A_ENVIAR = 'paquete_wifi.mat'

print("==================================================")
print(" MÓDULO WI-FI ESP32 - INICIANDO TRANSMISIÓN")
print("==================================================")

try:
    print(f"[*] Buscando paquete comprimido: '{ARCHIVO_A_ENVIAR}'...")
    
    # Abrimos el archivo binario generado por MATLAB
    with open(ARCHIVO_A_ENVIAR, 'rb') as f:
        archivos = {'file': (ARCHIVO_A_ENVIAR, f)}
        
        print(f"[*] Estableciendo conexión TCP/IP con el servidor: {URL_SERVIDOR} ...")
        time.sleep(1) # Pequeña pausa dramática para la presentación
        
        # Hacemos la petición POST (Exactamente igual a como la haría la librería HTTPClient.h del ESP32 real)
        respuesta = requests.post(URL_SERVIDOR, files=archivos)
        
        if respuesta.status_code == 200:
            print("\n[+] ¡ÉXITO! Los datos ECG han sido cifrados, comprimidos y enviados por la red.")
            print(f"[+] Respuesta del servidor: {respuesta.text}")
        else:
            print(f"\n[-] Error en la transmisión. Código HTTP: {respuesta.status_code}")

except FileNotFoundError:
    print(f"\n[-] ERROR CRÍTICO: No se encontró el archivo '{ARCHIVO_A_ENVIAR}'.")
    print("[-] Asegúrate de correr primero el script 'ESP32_Transmisor.m' en MATLAB.")
except requests.exceptions.ConnectionError:
    print(f"\n[-] ERROR DE RED: No se pudo conectar al servidor en {URL_SERVIDOR}.")
    print("[-] Asegúrate de que 'servidor_iot.py' esté corriendo y escuchando.")