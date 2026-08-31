# MCIA (NeuroZip): Muestreo Compresivo e Inteligencia Artificial para Señales Biomédicas

NeuroZip (MCIA) es un sistema híbrido de telemetría médica diseñado para la compresión y el cifrado simultáneo de señales de electrocardiograma (ECG) en entornos de Internet de las Cosas (IoT). El proyecto resuelve el alto consumo de ancho de banda y batería en microcontroladores mediante el uso del Muestreo Compresivo (Compressive Sensing - CS), trasladando la carga computacional pesada del hardware hacia un servidor central.

## 🚀 Características Principales

* **Compresión Simultánea (CS):** Utiliza una matriz de medición aleatoria ($\Phi$) para reducir tramas de 256 muestras (N=256) directamente en el hardware, logrando ahorros de transmisión Wi-Fi de hasta el 60.9%.


* **Cifrado Físico Caótico (CS-Secrecy):** La matriz de compresión actúa inherentemente como una llave criptográfica. Adicionalmente, se aplica un algoritmo de mezcla caótica con llaves simétricas ($K_1, K_2, K_3$) para revolver los índices, volviendo los datos interceptados en ruido blanco.


* **Motor Dual de Reconstrucción:** Permite elegir entre un **Autoencoder de Deep Learning** para alta velocidad, o el algoritmo **OMP (Orthogonal Matching Pursuit)** minimizando la norma $L_1$ para obtener una precisión matemática exacta.


* **Auto-Ajuste IA (Sparsity Analyzer):** Analiza la dispersión (Sparsity) de los coeficientes de la Transformada Discreta del Coseno (DCT) de la señal y ajusta automáticamente la tasa de compresión óptima basándose en el límite de Candès & Tao.


* **Visor Clínico Integrado:** Renderizado fluido de grado médico que muestra exclusivamente los resultados finales (sin ruido original), exhibiendo la señal en el tiempo, matriz en malla 3D, espectrograma de calor y Transformada Rápida de Fourier (FFT).



## 🧠 Arquitectura del Sistema

El flujo de datos asimétrico se divide en dos fases operativas para maximizar la eficiencia:

* **Fase 1: Transmisor IoT (Hardware)**
* El sensor analógico AD8232 capta el potencial cardíaco a una frecuencia de muestreo aproximada de 200 Hz, respetando el Criterio de Nyquist en la adquisición.


* El microcontrolador ESP32-WROOM digitaliza la señal y aplica la DCT para asegurar que la señal sea matemáticamente dispersa.


* Multiplica la señal por la matriz de sensado aleatoria para comprimirla y aplica el cifrado caótico antes de transmitir el paquete de datos.




* **Fase 2: Servidor (Software Python)**
* La plataforma Python recibe la información, descifra y ordena los datos utilizando las llaves caóticas inversas.


* Reconstruye la morfología clínica de las ondas P, QRS y T utilizando OMP o redes neuronales artificiales.


* Aplica la Transformada Inversa (IDCT) para regresar la señal recuperada al dominio del tiempo.





## 🛠️ Tecnologías Utilizadas

* **Software Central:** Python 3.x, `numpy` (cálculos matriciales y DCT), `torch` (Autoencoder), `customtkinter` (interfaz UI), `matplotlib` (validación gráfica de grado clínico).


* **Hardware Externo:** Microcontrolador ESP32 WROOM-32, Sensor ECG AD8232, C++ (Arduino IDE).


* **Algoritmos Matemáticos:** Orthogonal Matching Pursuit (OMP), Programación Lineal (Minimización L1), Mapas Caóticos.



## 📊 Métricas de Validación Clínica

El sistema garantiza una calidad diagnóstica validada matemáticamente mediante las siguientes métricas, integradas en la interfaz de usuario:

* **PRD (Percentage Root-mean-square Difference):** Mantenido consistentemente por debajo del umbral clínico del 5% (ej. 2.10% - 2.90%), garantizando una fidelidad morfológica excelente para la interpretación médica.


* **Correlación de Pearson:** Típicamente superior a 0.98 o 0.99, demostrando una similitud estructural anatómica casi perfecta entre el latido capturado y el reconstruido.


* **SNR (Signal-to-Noise Ratio):** Medición en decibeles (dB) de la calidad y potencia de la señal recuperada frente al ruido residual.



## ⚙️ Instalación y Uso

1. Instale las dependencias necesarias ejecutando en su terminal: `pip install numpy torch customtkinter matplotlib scipy`.


2. Inicie la aplicación mediante `python app.py` (o ejecutando el archivo `.exe` compilado vía PyInstaller).


3. Cargue el archivo de datos `.txt` o `.csv` generado por el microcontrolador.


4. Ingrese las **Claves Numéricas (K1 y K2)** en el panel lateral de seguridad para generar la semilla principal y el offset.


5. Seleccione el motor de reconstrucción deseado (Autoencoder u OMP) y presione "Descifrar y Extraer".


6. Utilice el botón **Validación Clínica 📊** para que el software extraiga las métricas de PRD, SNR y Pearson, y renderice los gráficos médicos finales del electrocardiograma.
