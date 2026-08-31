function [X2] = caot_mezcla(N,k2,k3,X1)
%Realización del esquema de mezclas caoticas, codificación
%Variables de entrada 
% k2. LLave 1
% k3. Lave 
% X1. Matriz a ser mezclada

%Iterar k3 veces
for k=1:k3
    for n=1:N
        for m=1:N
            n0=n-1;
            m0=m-1;
            n1=n0+m0;
            m1=k2*n0+(k2+1)*m0;
            n2=mod(n1,N)+1;
            m2=mod(m1,N)+1;
            X2(n2,m2)=X1(n,m);
        end
    end
    X1=X2;
end