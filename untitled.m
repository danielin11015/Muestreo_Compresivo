% =========================================================================
% SCRIPT DE VISUALIZACIÓN EN MATLAB PARA ARCHIVOS DESCOMPRIMIDOS DE NEUROZIP
% =========================================================================
clear all; close all; clc;

% 1. Seleccionar o definir el nombre del archivo extraído por la app de Python
% (Asegúrate de que esté en la misma carpeta o pon la ruta completa)
nombre_archivo = 'descomprimido.txt'; 

% Si tu archivo usa comas (.csv) en lugar de tabulaciones (.txt), 
% puedes usar readmatrix o cambiar el delimitador. 
% Como nuestra app guarda con doble columna flexible, lo leemos directo:
datos_recuperados = readmatrix(nombre_archivo);

% Extraemos las columnas (Columna 1: Tiempo, Columna 2: Voltaje/Señal)
tiempo = datos_recuperados(:, 1);
voltaje_recuperado = datos_recuperados(:, 2);

% Calculamos la frecuencia de muestreo (Fs) de forma dinámica a partir del tiempo
dt = mean(diff(tiempo));
fs = round(1/dt);
disp(['--> Frecuencia de muestreo leída del archivo: ', num2str(fs), ' Hz']);
disp(['--> Número total de muestras: ', num2str(length(voltaje_recuperado))]);

% =========================================================================
% GENERACIÓN DE GRÁFICAS DE ANÁLISIS
% =========================================================================

% Gráfica 1: Señal de ECG en el Tiempo
figure('Name', 'NeuroZip - Señal ECG Recuperada', 'Color', 'w');
plot(tiempo, voltaje_recuperado, 'r', 'LineWidth', 1.5);
title(['Señal ECG Reconstruida por IA (Fs = ', num2str(fs), ' Hz)']);
xlabel('Tiempo (s)');
ylabel('Amplitud (mV / V)');
grid on;
xlim([tiempo(1), min(tiempo(1) + 10, tiempo(end))]); % Muestra los primeros 10 segundos para detalle

% Gráfica 2: Espectro de Frecuencias (FFT)
L = length(voltaje_recuperado);
f = fs * (0:(L/2)) / L;
Y = fft(voltaje_recuperado);
P2 = abs(Y / L);
P1 = P2(1:floor(L/2) + 1);
P1(2:end-1) = 2 * P1(2:end-1);

figure('Name', 'NeuroZip - Espectro de Frecuencias', 'Color', 'w');
plot(f, P1, 'b', 'LineWidth', 1.5);
title('Espectro de Frecuencias (FFT) de la Señal Descomprimida');
xlabel('Frecuencia (Hz)');
ylabel('Magnitud');
xlim([0 50]); % Enfocado en el rango clínico del ECG (0 a 50 Hz)
grid on;

% Gráfica 3: Espectrograma (Tiempo-Frecuencia)
figure('Name', 'NeuroZip - Espectrograma', 'Color', 'w');
[s, w, t] = stft(voltaje_recuperado, fs);
surf(t, w, 10*log10(abs(s)), 'EdgeColor', 'none');
title('Espectrograma de la Señal Recuperada');
xlabel('Tiempo (s)');
ylabel('Frecuencia (Hz)');
zlabel('Potencia (dB)');
axis tight;
view(0, 90);
colormap jet;
colorbar;