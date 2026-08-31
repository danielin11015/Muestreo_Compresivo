#include <WiFi.h>
#include <HTTPClient.h>

// =========================================================================
// 1. CONFIGURACIÓN DE RED
// =========================================================================
const char* ssid = "TU_WIFI";             // Cambia por tu WiFi
const char* password = "TU_PASSWORD";     // Cambia por tu Password
// IP de tu computadora donde corre Python
const char* serverName = "http://192.168.100.6:5000/upload"; 

// =========================================================================
// 2. PARÁMETROS DEL ECG Y MUESTREO COMPRESIVO
// =========================================================================
const int PIN_SENSOR = 34; 
const int fs = 200;        
const int delayMuestreo = 1000 / fs; 

const int N = 50; 
const int M = 25; 

// Llaves de Cifrado Caótico (Idénticas a Python)
float K1_original = 50.0 / 100.0; // 0.50
int NI = 1; 

float x_original[N];
float y_comprimido[M];
float y_cifrado[M];

// =========================================================================
// 3. MATRIZ DE MEDICIÓN PHI (25x50)
// =========================================================================
// aquí tu matriz generada. Por ahora pongo ceros.
// DEBE ser idéntica a la matriz del código en Python.
const float Phi[M][N] = {
  {0.0, 0.0, 0.0 /*... rellena con los 50 valores de la fila 1 ...*/},
  // ... rellena hasta la fila 25 ...
};

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // ADC a 12 bits
  
  Serial.print("Conectando a WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nWiFi Conectado.");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    
    // --- FASE A: ADQUISICIÓN Y REMOCIÓN DE OFFSET ---
    float suma_voltajes = 0;
    for (int i = 0; i < N; i++) {
      int lectura = analogRead(PIN_SENSOR);
      float voltaje = (lectura * 3.3) / 4095.0; 
      x_original[i] = voltaje;
      suma_voltajes += voltaje;
      delay(delayMuestreo); // 5ms para Nyquist
    }
    
    float media_voltaje = suma_voltajes / N;
    for (int i = 0; i < N; i++) {
      x_original[i] = x_original[i] - media_voltaje; // Centramos la señal
    }

    // --- FASE B: COMPRESIÓN (Y = Phi * X) ---
    for (int i = 0; i < M; i++) {
      y_comprimido[i] = 0;
      for (int j = 0; j < N; j++) {
        y_comprimido[i] += Phi[i][j] * x_original[j];
      }
    }

    // --- FASE C: CIFRADO CAÓTICO (Mapeo Logístico 1D) ---
    float z[M];
    int indices[M];
    
    for (int iter = 0; iter < NI; iter++) {
      z[0] = K1_original;
      for (int i = 0; i < M - 1; i++) {
        z[i+1] = 1.0 - 2.0 * z[i] * z[i];
      }
      
      for (int i = 0; i < M; i++) indices[i] = i;
      
      // Ordenamiento de burbuja para obtener índices caóticos
      for (int i = 0; i < M-1; i++) {
        for (int j = 0; j < M-i-1; j++) {
          if (z[j] > z[j+1]) {
            float tempZ = z[j]; z[j] = z[j+1]; z[j+1] = tempZ;
            int tempI = indices[j]; indices[j] = indices[j+1]; indices[j+1] = tempI;
          }
        }
      }
      
      // Revuelve la señal
      for (int i = 0; i < M; i++) {
        y_cifrado[i] = y_comprimido[indices[i]];
      }
    }

    // --- FASE D: TRANSMISIÓN WI-FI ---
    String payload = "";
    for (int i = 0; i < M; i++) {
      payload += String(y_cifrado[i], 6);
      if (i < M - 1) payload += "\n";
    }

    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "text/plain");
    int httpResponseCode = http.POST(payload);
    Serial.println("Código HTTP: " + String(httpResponseCode));
    http.end();

  } else {
    Serial.println("Reconectando WiFi...");
    WiFi.reconnect();
  }
}