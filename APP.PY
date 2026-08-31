import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import os
import torch
import torch.nn as nn
import time

# 1. Configuración de Estilo Minimalista
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==========================================
# CEREBRO DE INTELIGENCIA ARTIFICIAL (Autoencoder)
# ==========================================
class CS_Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(CS_Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64)
        )
        self.decoder = nn.Sequential(
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

class AppMinimalista(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MCIA")
        self.geometry("850x560")
        self.minsize(750, 500)

        self.archivo_seleccionado = None
        self.menu_retraido = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 2. MENÚ RETRÁCTIL IZQUIERDO (Sidebar)
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#2b2b2b", "#121212"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1) 

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🧠 MCIA", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="w")

        self.lbl_seccion = ctk.CTkLabel(self.sidebar_frame, text="CONFIGURACIÓN IA", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray")
        self.lbl_seccion.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.combo_ia = ctk.CTkComboBox(self.sidebar_frame, values=["Autoencoder (Rápido)", "Deep CS-CNN"], width=180)
        self.combo_ia.grid(row=2, column=0, padx=20, pady=5)
        self.combo_ia.set("Autoencoder (Rápido)")

        self.lbl_slider = ctk.CTkLabel(self.sidebar_frame, text="Tasa de Compresión: 50%", font=ctk.CTkFont(size=12))
        self.lbl_slider.grid(row=3, column=0, padx=20, pady=(15, 5), sticky="w")

        self.slider = ctk.CTkSlider(self.sidebar_frame, from_=10, to=90, number_of_steps=80, command=self.actualizar_slider, width=180)
        self.slider.set(50)
        self.slider.grid(row=4, column=0, padx=20, pady=5)

        self.check_cifrado = ctk.CTkCheckBox(self.sidebar_frame, text="Cifrado Físico (CS-Secrecy)", font=ctk.CTkFont(size=12))
        self.check_cifrado.grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")
        self.check_cifrado.select()

        # DOBLE LLAVE DE SEGURIDAD (CS-Secrecy)
        self.entry_clave1 = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Clave 1 (K1)", width=180)
        self.entry_clave1.grid(row=6, column=0, padx=20, pady=5)
        
        self.entry_clave2 = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Clave 2 (K2)", width=180)
        self.entry_clave2.grid(row=7, column=0, padx=20, pady=5)

        # ==========================================
        # 3. PANEL CENTRAL PRINCIPAL
        # ==========================================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)

        self.btn_toggle = ctk.CTkButton(self.main_frame, text="≡", width=40, height=35, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), command=self.toggle_menu)
        self.btn_toggle.grid(row=0, column=0, sticky="w", pady=(0, 15))

        self.lbl_header = ctk.CTkLabel(self.main_frame, text="Comprime y descifra señales.", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_header.grid(row=1, column=0, sticky="w", pady=(0, 5))

        self.lbl_sub = ctk.CTkLabel(self.main_frame, text="Muestreo Compresivo (Estructura de tramas NT x N).", font=ctk.CTkFont(size=13), text_color="gray")
        self.lbl_sub.grid(row=2, column=0, sticky="w", pady=(0, 20))

        self.card_drop = ctk.CTkFrame(self.main_frame, corner_radius=12, border_width=2, border_color=("#3a3a3a", "#2a2a2a"), fg_color=("#f4f4f5", "#18181b"))
        self.card_drop.grid(row=3, column=0, sticky="nsew", pady=(0, 20))
        self.card_drop.grid_columnconfigure(0, weight=1)
        self.card_drop.grid_rowconfigure(0, weight=1)

        self.lbl_drop_text = ctk.CTkLabel(self.card_drop, text="📁 Arrastra tu archivo aquí (.csv, .txt, .csx)\n\n(o haz clic para explorar)", font=ctk.CTkFont(size=14), text_color="gray")
        self.card_drop.bind("<Button-1>", lambda e: self.explorar_archivo())
        self.lbl_drop_text.bind("<Button-1>", lambda e: self.explorar_archivo())
        self.lbl_drop_text.grid(row=0, column=0)

        self.frame_acciones = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_acciones.grid(row=4, column=0, sticky="ew")

        self.btn_comprimir = ctk.CTkButton(self.frame_acciones, text="Comprimir y Cifrar", height=40, font=ctk.CTkFont(weight="bold"), fg_color="#2563eb", hover_color="#1d4ed8", command=self.comprimir_datos)
        self.btn_comprimir.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.btn_reconstruir = ctk.CTkButton(self.frame_acciones, text="Descifrar y Extraer", height=40, font=ctk.CTkFont(weight="bold"), fg_color="#059669", hover_color="#047857", command=self.reconstruir_datos)
        self.btn_reconstruir.pack(side="left", expand=True, fill="x", padx=(5, 5))

        self.btn_graficar = ctk.CTkButton(self.frame_acciones, text="Validación Clínica 📊", height=40, font=ctk.CTkFont(weight="bold"), fg_color="#d97706", hover_color="#b45309", command=self.graficar_resultados)
        self.btn_graficar.pack(side="right", expand=True, fill="x", padx=(5, 0))

    # --- Funciones de Interfaz ---
    def actualizar_slider(self, valor):
        self.lbl_slider.configure(text=f"Tasa de Compresión: {int(valor)}%")

    def toggle_menu(self):
        if self.menu_retraido:
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
            self.menu_retraido = False
        else:
            self.sidebar_frame.grid_forget()
            self.menu_retraido = True

    def explorar_archivo(self):
        tipos_archivo = [("Archivos Soportados", "*.csv *.txt *.dat *.csx"), ("Todos los archivos", "*.*")]
        ruta = filedialog.askopenfilename(title="Seleccionar Archivo", filetypes=tipos_archivo)
        if ruta:
            self.archivo_seleccionado = ruta
            nombre = ruta.split("/")[-1]
            tamano_kb = os.path.getsize(ruta) / 1024
            tiempo_estimado = tamano_kb * 0.003
            texto_tiempo = "< 1 segundo" if tiempo_estimado < 1.0 else f"~{tiempo_estimado:.1f} segundos"

            self.lbl_drop_text.configure(
                text=f"📄 Archivo seleccionado:\n{nombre}\n\nTiempo est. de procesamiento: {texto_tiempo}", 
                text_color=("#059669", "#10b981")
            )

    def obtener_semilla_combinada(self):
        c1 = self.entry_clave1.get()
        c2 = self.entry_clave2.get()
        if not c1.isdigit() or not c2.isdigit():
            messagebox.showerror("Falta Clave", "Por favor ingresa ambas Claves Numéricas en el menú lateral.")
            return None
        return int(c1) + (int(c2) * 997)

    # Funciones auxiliares nativas para DCT
    def calcular_dct(self, x):
        N = len(x)
        n = np.arange(N)
        k = np.arange(N).reshape(-1, 1)
        matrix = np.cos(np.pi * (2 * n + 1) * k / (2 * N))
        return np.dot(matrix, x)

    def calcular_idct(self, X):
        N = len(X)
        k = np.arange(N)
        n = np.arange(N).reshape(-1, 1)
        matrix = np.cos(np.pi * (2 * k + 1) * n / (2 * N))
        matrix[0, :] = matrix[0, :] / np.sqrt(2)
        return np.dot(matrix, X) * (2 / N)

    # --- MOTOR MATEMÁTICO: COMPRESIÓN ---
    def comprimir_datos(self):
        if not self.archivo_seleccionado: return messagebox.showerror("Error", "Selecciona un archivo.")
        semilla = self.obtener_semilla_combinada()
        if semilla is None: return

        ruta_salida = filedialog.asksaveasfilename(defaultextension=".csx", filetypes=[("NeuroZip", "*.csx")])
        if not ruta_salida: return

        try:
            matriz_datos = np.genfromtxt(self.archivo_seleccionado, delimiter=None, skip_header=0)
            if np.isnan(matriz_datos).all(): matriz_datos = np.genfromtxt(self.archivo_seleccionado, skip_header=1)
            
            tiempo_orig = matriz_datos[:, 0] if matriz_datos.ndim > 1 else np.array([])
            voltaje_orig = matriz_datos[:, 1] if matriz_datos.ndim > 1 else matriz_datos.flatten()
            voltaje_orig = voltaje_orig[~np.isnan(voltaje_orig)]
            voltaje_orig = voltaje_orig - np.mean(voltaje_orig)

            N = 256 
            porcentaje = self.slider.get()
            NT = max(1, int((len(voltaje_orig) / N) * (1.0 - (porcentaje / 100.0))))
            
            total = NT * N
            x1 = np.tile(voltaje_orig, int(np.ceil(total / len(voltaje_orig))))[:total] if len(voltaje_orig) < total else voltaje_orig[:total]
            x2 = x1.reshape((NT, N))

            rng = np.random.default_rng(semilla)
            A = rng.standard_normal((NT, N)) / np.sqrt(NT)

            xc = np.zeros((NT, NT), dtype=np.float32)
            for k in range(NT):
                xc[k, :] = np.dot(A, self.calcular_dct(x2[k, :]))

            with open(ruta_salida, 'wb') as f:
                np.savez(f, measurements=xc, NT=NT, N=N, tiempo_orig=tiempo_orig[:total])

            messagebox.showinfo("Éxito", f"Compresión {int(porcentaje)}% aplicada.\nGuardado en: {ruta_salida}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- DESCIFRADO ---
    def reconstruir_datos(self):
        if not self.archivo_seleccionado or not self.archivo_seleccionado.endswith(".csx"):
            return messagebox.showerror("Error", "Selecciona el archivo comprimido (.csx).")
        semilla = self.obtener_semilla_combinada()
        if semilla is None: return

        ruta_salida = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT/CSV", "*.txt *.csv")])
        if not ruta_salida: return

        try:
            with open(self.archivo_seleccionado, 'rb') as f:
                paquete = np.load(f, allow_pickle=True)
                xc, NT, N, tiempo_orig = paquete['measurements'], int(paquete['NT']), int(paquete['N']), paquete['tiempo_orig']

            rng = np.random.default_rng(semilla)
            A2 = rng.standard_normal((NT, N)) / np.sqrt(NT)
            A2_pseudo = np.linalg.pinv(A2)
            
            xc1 = np.zeros((NT, N), dtype=np.float32)
            for k in range(NT):
                xc1[k, :] = self.calcular_idct(np.dot(A2_pseudo, xc[k, :]))

            xr = np.nan_to_num(xc1.flatten(), nan=0.0, posinf=0.0, neginf=0.0)
            tiempo_final = tiempo_orig if len(tiempo_orig) == len(xr) else np.arange(len(xr)) * 0.002

            np.savetxt(ruta_salida, np.column_stack((tiempo_final, xr)), delimiter="\t", fmt="%.6f")
            messagebox.showinfo("Éxito", "Descifrado completado y exportado.")
        except Exception as e:
            messagebox.showerror("Error", "Claves incorrectas o archivo corrupto.")

    # --- VISOR CLÍNICO FLUIDO ESTILO MATLAB ---
    def graficar_resultados(self):
        try:
            import matplotlib.pyplot as plt
            import matplotlib as mpl
            from matplotlib import mlab
        except ImportError:
            return messagebox.showerror("Error", "Falta matplotlib.")

        # Configurar el estilo gráfico igual a MATLAB (Fondo blanco, líneas claras)
        mpl.rcParams['axes.grid'] = True
        mpl.rcParams['grid.color'] = '#DDDDDD'
        mpl.rcParams['grid.linestyle'] = '-'
        mpl.rcParams['figure.facecolor'] = 'white'
        mpl.rcParams['axes.facecolor'] = 'white'

        ruta_rec = filedialog.askopenfilename(title="Selecciona el ECG RECONSTRUIDO para visualizar (.txt / .csv)")
        if not ruta_rec: return

        try:
            mat_r = np.genfromtxt(ruta_rec, skip_header=0)
            if np.isnan(mat_r).all():
                mat_r = np.genfromtxt(ruta_rec, skip_header=1)

            xr = mat_r[:, 1] if mat_r.ndim > 1 else mat_r.flatten()
            xr = xr - np.mean(xr)
            
            if mat_r.ndim > 1:
                dt = np.mean(np.diff(mat_r[:, 0]))
                fs = int(round(1/dt)) if dt > 0 else 500
            else:
                fs = 500

            messagebox.showinfo("Generando Análisis", "Renderizando gráficos fluidos. Presiona Aceptar.")
            
            # --- 1. MATRIZ ECG (Mesh 3D Suave) ---
            N = 256
            NT = len(xr) // N
            if NT > 0:
                fig1 = plt.figure("Fig 1: Matriz ECG (Resultado Final)")
                ax1 = fig1.add_subplot(111, projection='3d')
                X_mesh, Y_mesh = np.meshgrid(np.arange(N), np.arange(NT))
                matriz_3d = xr[:NT*N].reshape(NT, N)
                
                # rstride=1, cstride=1, edgecolor='none' y antialiased hace que corra idéntico a MATLAB (Fluido y suave)
                ax1.plot_surface(X_mesh, Y_mesh, matriz_3d, cmap='jet', edgecolor='none', rstride=1, cstride=1, antialiased=True, alpha=0.9)
                ax1.set_title("Estructura de la Señal ECG Final")
                ax1.set_xlabel("Muestras por Trama (N)")
                ax1.set_ylabel("Número de Trama (NT)")

            # --- 2. SEÑAL EN EL TIEMPO ---
            fig2 = plt.figure("Fig 2: Señal en el Tiempo")
            muestras_visibles = min(25000, len(xr))
            tiempo_eje = np.arange(muestras_visibles) / fs
            plt.plot(tiempo_eje, xr[:muestras_visibles], color='#D95319', linewidth=1.2) # Color clásico de MATLAB
            plt.title("Electrocardiograma (ECG) Reconstruido")
            plt.xlabel("Tiempo (s)"); plt.ylabel("Amplitud (mV)")
            plt.xlim([0, tiempo_eje[-1]])
            plt.tight_layout()

            # --- 3. ESPECTROGRAMA FINAL (Pcolormesh Fluido 2D) ---
            # En MATLAB usabas view(0,90). En Python, pcolormesh es lo mismo pero corre muchísimo más rápido.
            fig3 = plt.figure("Fig 3: Espectrograma Clínico")
            ax3 = fig3.add_subplot(111)
            
            # Aplicamos ventana de Hamming exacta como en MATLAB
            Pxx_r, freqs_r, bins_r = mlab.specgram(xr, NFFT=256, Fs=fs, window=np.hamming(256), noverlap=128)
            mmsr = 10 * np.log10(Pxx_r + 1e-10)
            
            # shading='gouraud' hace el degradado suave y fluido
            c3 = ax3.pcolormesh(bins_r, freqs_r, mmsr, cmap='jet', shading='gouraud')
            fig3.colorbar(c3, ax=ax3, label="Potencia (dB)")
            ax3.set_title("Espectrograma - Señal Reconstruida")
            ax3.set_xlabel("Tiempo (s)"); ax3.set_ylabel("Frecuencia (Hz)")
            ax3.set_ylim([0, 50])
            plt.tight_layout()

            # --- 4. TRANSFORMADA DE FOURIER (FFT) ---
            fig4 = plt.figure("Fig 4: Espectro de Frecuencias")
            min_len = len(xr)
            f_axis = fs * np.arange(min_len//2 + 1) / min_len
            P1_r = np.abs(np.fft.fft(xr) / min_len)[:min_len//2 + 1]
            P1_r[1:-1] *= 2
            
            plt.plot(f_axis, P1_r, color='#0072BD', linewidth=1.5) # Color azul estándar de MATLAB
            plt.xlim([0, 50])
            plt.title("Espectro de Frecuencias (FFT)")
            plt.xlabel("Frecuencia (Hz)"); plt.ylabel("Magnitud")
            plt.tight_layout()

            plt.show()

        except Exception as e:
            messagebox.showerror("Error al Graficar", f"Ocurrió un error:\n{str(e)}")

if __name__ == "__main__":
    app = AppMinimalista()
    app.mainloop()