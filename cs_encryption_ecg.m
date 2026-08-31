clear all;
% cs_encryption.  Cifrado y compresion simultanea de electrocardiograma
% usando muestreo compresivo y matrices caoticas.  La descomroesion se
% realiza usando el esquema Test out l1eq code 
% (l1 minimization with equality constraints).
%
%Captura de la señal a ser comprimida
%rng.  llave de usuario
%NT. Numero de tramas de la señal de entrada, cada trama de 256 muestras
%se comprime a 100 muestras.
%
x = load('RegistroECG.txt');
x1=double(x);
figure(1);                                         %Figura 1
plot(x1); axis([1 1024 -0.2 0.5]);
title('Señal original');

[M1,N1]=size(x1);  %Duración de la señal ded EGC
Na=max(M1,N1);

%La señal de EGC se divide en NT tramas, donde NT es la dimensión de
%la trama comprimida.  Esto permite almancenar la señal compromido en NT
%tramas de NT muestras cada una, resultando en una matriz de NtXNT, la cual
%es procesada por un esquema de mezclas caoticas lo que permite incrementar
%la seguridad del sistema al mezclar caóticmente la matriz compromida
%resultante.
%
%Generación de las NT tramas de la señal de ECG a se compromida.
NT=100;   %NT.  Número de tramas.
N=256;    %N Dimensión de la trama
%
% Arreglar la señal de entrada en forma de matriz de (NT x N)
for k=1:NT
    for m1=1:N
        x2(k,m1)=x1((k-1)*N+m1);
    end
end
figure(2);                                      %Figura 2
mesh(x2);
title('matriz ha ser comprimida y cifrada');
%
%  Comprimir por separado cada uno de los renglones de la matriz x2
%
for k=1:NT
    for m1=1:N
        xd2(m1)=x2(k,m1);
    end
%
%   Generacion del vector disperso
%
    %signal length
    xd=zeros(N,1);
    x3=dct(xd2);                    %DCT de la señal x2
    xmax=max(max(x3));             %Valor maximo de la trama           
    nz=0;

    %Elimnacion de las muestras menores que el umbral.  Se define un valor
    %de umbral, el cual es un porcentaje del valor máximo del segmento 
    %bajo análisis
    %
    for m1=1:N
        xd3=x3(1,m1);
        x21=abs(xd3);
        xm1=0.02*xmax;             % Valor del umbral 
        %% 
        if x21>xm1
            nz=nz+1;
            xd(m1,1)=xd3;           %x señal de entrada dispersa
        end
    end    
    % number of spikes in the signal T. Este es el número total de 
    % valores menores al umbral, en el intervslo de interés.  K es la
    % dimensión experimental del vector a ser comprimido.
    %
    T =nz;  %Valor estimado de muestras menores que el umbral.
    %
    % numero de observaciones 
    K = NT;
    %
    % Crear la matriz de sensado, A, usando un generador de numeros 
    % aleatorios usando una llave rhb.
    % measurement matrix
    disp('Creating measurment matrix A..');
    rng(19540516);                %lava de usuario
    A = randn(NT,N);               %Matrix de sensado aleatoria
    A = orth(A')';                %Matrix de sensado ortonormal
    disp('Done.');

    %Compresion de la señal dispersa
    y = A*xd;

    % Almacenamiento de la señal comprimida y cifrada en la matriz 
    % de información, xc, a ser mezclada
    for m2=1:NT
        xc(k,m2)=y(m2,1);
    end
end
%
% Para incrementar la seguridad de la sewguridad de la información 
% la matriz conteniendo la informacion cifrada y comprimida, se 
% la información contenida en la matriz xc,se mezcla usando el esquema
% de mezclas caóticas, usando las llaves k3, k3
k2=56;                %llave de mezclad0
k3=26;                %llave de mezclado
N1=NT;                %Numero de muestras
xc2=caot_mezcla(N1,k2,k3,xc);
%
%  Procedimiento de descompresion y decodificacion.   Para decodificar 
%  las señales compromidas y cifradas, inicialmente se aplica una 
%  operación de mezclado inverso para recuperar el orden original de las 
%  tramas comprimidas
%
k21=56;               %Llave de mezclado inverso
k31=26;               %Llave de mezclado inverso
                      %N1 Tamaño de la trama
%
xca=caot_mezcla_dec(N1,k21,k31,xc2);
%
%  Una vez aplicada la operacion de mexclado caotico inverso, se procederá
%  a descomprimir cada trama de la señal dada por cada renglón de la 
%  matriz xc2.  Para lo cual se aplica la operacion de inversa de muestreo
%  compresivo a la señal una vez que el orden ha sido corregido.
%
disp('Creating decompression matrix A2..');
%
rng(19540516);                     % Llave de decodificación
A2 = randn(NT,N);               %Matrix de sensado aleatoria
A2 = orth(A2')';               %Matrix de sensado ortonormal
disp('Done.');

disp('Decompressed sparse signal');
for k=1:NT
    for m2=1:NT
        y1(m2,1)=xca(k,m2);
    end
    % initial guess = min energy
    x0 = A2'*y1;   %Señal intermedia descomprimida

    % solve the LP
    tic
    xp = l1eq_pd(x0, A2, [], y1, 1e-3); %dct de la señal recuparad
    toc
    xrec=idct(xp);   %Señal recuperada
    for m1=1:N
        xc1(k,m1)=xrec(m1);
    end
end
%
%señales codificadas y decodificadas
for k=1:NT
    for m1=1:N
        xo((k-1)*N+m1)=x2(k,m1);
        xr((k-1)*N+m1)=xc1(k,m1);
    end
end
figure(3);                                   %Figura 3
plot(xo); axis([1 1024 -0.2 0.5]);
title('señal original)');
figure(4);                                   %Figura 4
plot(xr); axis([1 1024 -0.2 0.5]);
title('Señal recuperada');

%____________________________ Evaluación del Sistema _____________________

%Coefficiente de correlación de Pearson e la trama 1 a 1024
NP=256;
xop=0.0;
xrp=0.0;
for k=1:NP
    xop=xop+xo(k);
    xrp=xrp+xr(k);
end
xop=xop/NP;
xrp=xrp/NP;

xo1=0.0;
xr1=0.0;
xor=0.0;
for k=1:NP
    xo1=xo1+(xo(k)-xop)^2;
    xr1=xr1+(xr(k)-xrp)^2;
    xor=xor+(xo(k)-xop)*(xr(k)-xrp);
end
xccp=xor/sqrt(xo1*xr1);
disp('correlacion de Pearson.'); xccp

%Coefficiente de correlación de Pearson entre muestras adyacentes
%en la trama 1 a 1024
NP=256;
xop=0.0;
xrp=0.0;
for k=1:NP
    xop=xop+xo(k);
    xrp=xrp+xr(k);
end
xop=xop/NP;
xrp=xrp/NP;

xo1=0.0;
xr1=0.0;
xor=0.0;
for k=1:NP
    xo1=xo1+(xr(k)-xop)^2;
    xr1=xr1+(xr(k+1)-xrp)^2;
    xor=xor+(xr(k)-xop)*(xr(k+1)-xrp);
end
xccpa=xor/sqrt(xo1*xr1);
disp('correlacion de Pearson entre muestras adyancentes.'); xccpa
%
%_________________________  SNR y PRD ___________________________________
pxo=0.0;
per=0.0;
for k=1:NP
    per=per+(xo(k)-xr(k))^2;
    pxo=pxo+(xo(k)^2);
end

% Calcular SNR (En decibeles - dB)
snr = 10*log10(pxo/per);
disp('Calidad de señal (SNR en dB):'); disp(snr);

% Calcular PRD (Porcentaje de Error) -> ESTE ES EL QUE QUIERES MOSTRAR
prd = sqrt(per/pxo) * 100;
disp('Error de Reconstrucción (PRD en %):'); disp(prd);

%__________________________ Histograma y Gráfico de Error _______________
% Vamos a cambiar el gráfico raro de "audio" por un gráfico de error médico
figure(5);
plot(xo - xr, 'r', 'LineWidth', 1.5);
title(['Error de Reconstrucción (Diferencia). PRD = ', num2str(prd), ' %']);
xlabel('Muestras'); ylabel('Amplitud del Error');
grid on;
%_________________  Espectrograma de la señales ___________________
fs=200;
so=stft(xo,fs);
sr=stft(xr,fs);
mso=abs(so);
msr=abs(sr);
mmso=10*log10(mso);
mmsr=10*log10(msr);
figure(7);                                   %Figura 7
mesh(mmso);
title('Espectrograma de la señal original')
figure(8);                                   %Figura 8
mesh(mmsr);
title('Espectrograma de la señal recuperada'); 
%
figure(9);                                  %Figura 9
plot(xo,xr,'+'); 
title('Plot señal recuperada vs señal original');

%__________________________ Gráficas de Comparación ____________________
%
% 1. Gráfica Superpuesta (Original vs Recuperada)
figure(6);
plot(xo, 'b', 'LineWidth', 1.5);      % Señal original en color azul
hold on;
plot(xr, 'r--', 'LineWidth', 1.2);    % Señal recuperada en rojo punteado
hold off;
title('Comparación Visual: Señal Original vs Señal Recuperada');
xlabel('Muestras');
ylabel('Amplitud');
legend('Señal Original', 'Señal Recuperada');
grid on;

% 2. Gráfica de Dispersión (Correlación)
figure(7);
scatter(xo, xr, 15, 'b', '+');        % Puntos de comparación
hold on;
% Dibujar línea diagonal de referencia (Reconstrucción 100% perfecta)
lim_min = min(min(xo), min(xr));
lim_max = max(max(xo), max(xr));
plot([lim_min, lim_max], [lim_min, lim_max], 'k--', 'LineWidth', 1.5);
hold off;
title('Gráfico de Dispersión: Fidelidad de la Reconstrucción');
xlabel('Amplitud Original');
ylabel('Amplitud Recuperada');
legend('Muestras reconstruidas', 'Línea de perfección (0% Error)');
grid on;