clc; clear all; close all;
% =========================================================================
% PROYECTO DE TITULACIÓN: COMPRESIÓN Y CIFRADO SIMULTÁNEO DE SEÑALES ECG
% ALGORITMO PRINCIPAL: MUESTREO COMPRESIVO CON RECONSTRUCCIÓN OMP
% =========================================================================

% =========================================================================
% FASE 1: ADQUISICIÓN Y ACONDICIONAMIENTO DE DATOS (Simulación de Hardware)
% =========================================================================
% Leemos el archivo generado por el ESP32
datos_completos = readmatrix('C:\Users\danie\OneDrive\Documentos\ECG\beta 2 muestreo compresivo\descomprimido2.txt'); 

% Extraemos obligatoriamente el Tiempo (Col 1) y el Voltaje (Col 2)
tiempo = datos_completos(:, 1); 
voltaje = datos_completos(:, 2); 

% --- NUEVA CORRECCIÓN: CÁLCULO DINÁMICO DE FRECUENCIA DE MUESTREO ---
% Calculamos el periodo de muestreo (dt) promediando la diferencia entre tiempos
dt = mean(diff(tiempo));
fs = round(1/dt); % Frecuencia de muestreo real (Fs) calculada matemáticamente
disp(['--> Frecuencia de Muestreo (fs) calculada del hardware: ', num2str(fs), ' Hz']);
% --------------------------------------------------------------------

% Reemplazamos cualquier error de lectura (NaN) por ceros
voltaje(isnan(voltaje)) = 0; 

% REGLA MÉDICA VITAL: Restamos la media para centrar la señal en cero (Offset).
voltaje1 = voltaje - mean(voltaje); 

% --- CORRECCIÓN DEL PROFESOR: FILTRADO DIGITAL FIR (ENE/25) ---
N_filt = 100;  % Orden del filtro
fm = fs;       % Vinculamos la frecuencia dinámica del hardware al filtro
fc = 57;       % Frecuencia de Corte

% Filtro Ventana Rectangular (Sinc)
h = zeros(N_filt, 1);
for k=1:N_filt  
    h(k,1) = 2*((fc/fm)) * sinc(2*(k-round(N_filt/2))*(fc/fm));
end
win = hamming(N_filt); 

% Filtro Ventana de Hamming
CoefFil = win.*h;

% Filtrado de la señal
voltaje = filter(CoefFil, 1, voltaje1);
% -----------------------------------------------------------------

% Configuración de la estructura de bloques del Muestreo Compresivo
N = 256;   % Tamaño de cada trama original
NT = 128;  % Factor de compresión al 50%

% Validamos tener datos suficientes para la simulación
total_muestras = NT * N;
if length(voltaje) < total_muestras
    repeticiones = ceil(total_muestras / length(voltaje));
    x1 = repmat(voltaje, repeticiones, 1);
    x1 = x1(1:total_muestras);
else
    x1 = voltaje(1:total_muestras);
end

x2 = zeros(NT, N);
for k=1:NT
    for m1=1:N
        x2(k,m1) = x1((k-1)*N + m1);
    end
end

figure(1);
mesh(x2);
title('Matriz ECG Estructurada (Antes de Compresión)');
xlabel('Muestras por Trama (N)'); ylabel('Número de Trama (NT)'); zlabel('Voltaje');

% =========================================================================
% FASE 2: COMPRESIÓN Y CIFRADO SIMULTÁNEO (Se ejecuta en el ESP32)
% =========================================================================
disp('Generando Matriz de Sensado Ortogonalizada...');
rng(19540516); 
A = randn(NT, N);
A = orth(A')'; 
disp('Hecho.');

xc = zeros(NT, NT);
K_spars = 45; 
for k=1:NT
    xd2 = x2(k,:);
    x3 = dct(xd2); 
    
    [~, sortIndex] = sort(abs(x3), 'descend');
    xd = zeros(N,1);
    xd(sortIndex(1:K_spars)) = x3(sortIndex(1:K_spars)); 
    
    y = A * xd;
    xc(k,:) = y'; 
end

% Criptografía caótica
k2 = 56; k3 = 26;
xc2 = caot_mezcla(NT, k2, k3, xc); 

% =========================================================================
% FASE 3: DESCOMPRESIÓN Y RECONSTRUCCIÓN CRÍTICA (Servidor Web)
% =========================================================================
k21 = 56; k31 = 26;
xca = caot_mezcla_dec(NT, k21, k31, xc2);

rng(19540516); 
A2 = randn(NT, N);
A2 = orth(A2')';
xc1 = zeros(NT, N);
disp('Iniciando Motor de Reconstrucción Voraz OMP...');

for k=1:NT
    y1 = xca(k,:)';
    
    residual = y1; 
    indx = [];     
    xp = zeros(N,1);
    
    for iter = 1:K_spars
        proj = abs(A2' * residual);
        [~, pos] = max(proj); 
        indx = [indx, pos];   
        
        A_sub = A2(:, indx);
        x_est = A_sub \ y1;   
        
        residual = y1 - A_sub * x_est;
    end
    xp(indx) = x_est; 
    
    xrec = idct(xp);
    xc1(k,:) = xrec';
end
disp('Señal Reconstruida con Éxito.');

xo = zeros(1, total_muestras);
xr = zeros(1, total_muestras);
for k=1:NT
    for m1=1:N
        xo((k-1)*N+m1) = x2(k,m1);
        xr((k-1)*N+m1) = xc1(k,m1);
    end
end

% =========================================================================
% FASE 4: VALIDACIÓN CLÍNICA Y MÉTRICAS DE RENDIMIENTO
% =========================================================================
xop = mean(xo); xrp = mean(xr);
num = sum((xo - xop) .* (xr - xrp));
den = sqrt(sum((xo - xop).^2) * sum((xr - xrp).^2));
pearson = num / den;
disp('-------------------------------------------');
disp(['Correlación de Pearson: ', num2str(pearson)]);

pxo = sum(xo.^2);
per = sum((xo - xr).^2);
snr = 10 * log10(pxo/per);
disp(['Calidad de Señal SNR (dB): ', num2str(snr)]);

prd = sqrt(per/pxo) * 100;
disp(['Error Clínico PRD (%): ', num2str(prd)]);
disp('-------------------------------------------');

% =========================================================================
% FASE 5: GENERACIÓN DE GRÁFICAS PROFESIONALES PARA EXPOSICIÓN
% =========================================================================
% (Nota: Ya no forzamos fs=500 aquí, toma el fs dinámico calculado en Fase 1)

figure(2);
muestras_zoom = min(25000, length(xo)); 
plot(xo(1:muestras_zoom), 'b', 'LineWidth', 2.5); 
hold on;
plot(xr(1:muestras_zoom), 'r', 'LineWidth', 1.2);  
hold off;
title(['Comparación en el Tiempo: Original vs OMP (PRD: ', num2str(prd, '%.2f'), ' %)']);
xlabel('Muestras'); ylabel('Amplitud (V)');
legend('Señal Original (Filtrada)', 'Señal Recuperada (OMP)');
grid on;

figure(3);
scatter(xo(1:muestras_zoom), xr(1:muestras_zoom), 15, 'b', '+');
hold on;
lim_min = min(min(xo(1:muestras_zoom)), min(xr(1:muestras_zoom))); 
lim_max = max(max(xo(1:muestras_zoom)), max(xr(1:muestras_zoom)));
plot([lim_min, lim_max], [lim_min, lim_max], 'k', 'LineWidth', 1.5); 
hold off;
title(['Gráfico de Dispersión (Error PRD: ', num2str(prd, '%.2f'), ' %)']);
xlabel('Amplitud Original'); ylabel('Amplitud Recuperada');
grid on;

so = stft(xo, fs); sr = stft(xr, fs);
mmso = 10*log10(abs(so)); mmsr = 10*log10(abs(sr));
figure(4);                                   
subplot(1,2,1); 
surf(mmso, 'EdgeColor', 'none'); 
title('Espectrograma Señal Original'); zlabel('Potencia (dB)');
colormap jet; 
subplot(1,2,2); 
surf(mmsr, 'EdgeColor', 'none'); 
title('Espectrograma Señal Recuperada'); zlabel('Potencia (dB)');
colormap jet;

figure(5);
surf(abs(mmso - mmsr), 'EdgeColor', 'none'); 
title('Diferencia Absoluta entre Espectrogramas (Error Residual)');
zlabel('Magnitud del Error');
colormap hot; 

L = length(xo);
f = fs*(0:(L/2))/L; 
Y_orig = fft(xo); P2_orig = abs(Y_orig/L); P1_orig = P2_orig(1:floor(L/2)+1);
P1_orig(2:end-1) = 2*P1_orig(2:end-1);
Y_rec = fft(xr); P2_rec = abs(Y_rec/L); P1_rec = P2_rec(1:floor(L/2)+1);
P1_rec(2:end-1) = 2*P1_rec(2:end-1);

figure(6);
plot(f, P1_orig, 'b', 'LineWidth', 2.5); 
hold on;
plot(f, P1_rec, 'r', 'LineWidth', 1.2);   
hold off;
title('Espectro de Frecuencias (FFT)');
xlabel('Frecuencia (Hz)'); ylabel('Magnitud');
legend('Espectro Original', 'Espectro Recuperado');
xlim([0 45]); 
grid on;

figure(7);
tamano_ventana = min(1024, length(xr));
traslape = floor(tamano_ventana / 2);

% Usamos rot90 y la variable xr directa según corrección del profesor
[Cxy, F_coh] = mscohere(rot90(x1), xr, hamming(tamano_ventana), traslape, tamano_ventana, fs);

plot(F_coh, Cxy, 'LineWidth', 2, 'Color', [0.1 0.6 0.2]); 
hold on;
area(F_coh, Cxy, 'FaceColor', [0.1 0.6 0.2], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
title('Coherencia Espectral: Señal Original vs. Reconstruida');
xlabel('Frecuencia (Hz)');
ylabel('Magnitud de Coherencia (0 a 1)');
grid on;
axis([0 (fs/2) 0 1.1]);
yline(0.9, '--r', 'Alta Fidelidad (>0.9)', 'LabelHorizontalAlignment', 'left');
hold off;