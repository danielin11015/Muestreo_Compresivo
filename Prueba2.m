% 1. se cargar archivo completo
ruta = 'C:\Users\danie\Documents\ECG\ascii_ecg_data.txt';
ecg = load(ruta);
ecg = double(ecg(:));   % se asegura el vector columna

% 2. Mostrar rango de valores
disp('Rango de valores [min max]:');
disp([min(ecg) max(ecg)]);

% 3. se graficar la señal original del archivo
figure;
plot(ecg, 'blue');
title('ECG original del archivo ASCII');
xlabel('Milivolts');
ylabel('Amplitud');
grid on;

% 4. se normaliza mediante la formula de normalizacion min-max
ecg_norm = (ecg - min(ecg)) / (max(ecg) - min(ecg));

% 5. Graficar señal normalizada
figure;
plot(ecg_norm, 'red');
title('ECG normalizado');
xlabel('Milivolts');
ylabel('Amplitud');
grid on;

% 6. obtenemos TODOS los valores unicos, sirve para calcular probabilidades y entropia 
[valores_unicos, ~, idx] = unique(ecg);

% mide cuanta infomracion contiene la señal
% idx es el símbolo de cada muestra
% valores_unicos es el alfabeto completo de la fuente

% 7. se cuenta cuantas veces aparece cada valor unico 
counts = accumarray(idx, 1);


% 8. se convierten las frecuencias en probabilidades reales
p = counts / sum(counts);
%se divide cada frecuencia entre el total de muestras, esto convierte las 
% frecuencias en probabilidades reales, lo que ayudara a calcular la
% entropia de Shannon

% 9. Entropía de Shannon
p_nozero = p(p > 0); %se eleiminan probabilidades 0 para evitar errores numericos
H = -sum(p_nozero .* log2(p_nozero)); %formula de Shannon

fprintf('Número de valores únicos: %d\n', length(valores_unicos));
fprintf('Entropía de Shannon: %.4f bits\n', H);

% 10. histograma usando TODOS los valores reales
figure;
bar(valores_unicos, counts, 'k');   % barras negras
title('Histograma con TODOS los valores reales del ECG');
xlabel('Valor');
ylabel('Frecuencia');
grid on;