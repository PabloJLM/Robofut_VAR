import customtkinter
from PIL import Image, ImageTk
import time
import subprocess
import sys
import os

logo_path = "logo.png"
imagen_central = "centro.png"

def wifi():
    try:
        wifi = subprocess.check_output("netsh wlan show interfaces", shell=True).decode("utf-8")
        for linea in wifi.splitlines():
            if "SSID" in linea and "BSSID" not in linea:
                return linea.split(":")[1].strip()
        return "No conectado"
    except:
        return "Error!"

def actualizar_reloj():
    hora_actual = time.strftime("%H:%M:%S")
    reloj_label.configure(text=hora_actual)
    app.after(1000, actualizar_reloj)

# Funciones de prueba que no abren nada
def abrir_seleccion_campo():
    print("Simulando abrir selección de campo")

def ver_campo():
    print("Simulando ver campo")

def seleccion_porterias():
    print("Simulando selección de porterías")

def Abrir_VAR():
    print("Simulando apertura de VAR")

def abrir_grabaciones():
    from grabaciones import VentanaGrabaciones
    ventana = VentanaGrabaciones()
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

def update_imagen_central(event=None):
    canvas_central.delete("all")
    w = canvas_central.winfo_width()
    h = canvas_central.winfo_height()
    resized = img_central_pil.resize((w, h), Image.Resampling.LANCZOS)
    img_central_tk = ImageTk.PhotoImage(resized)
    canvas_central.create_image(0, 0, anchor="nw", image=img_central_tk)
    canvas_central.image = img_central_tk

# Crear ventana principal
app = customtkinter.CTk()
app.title("Ventana Principal")
ancho = app.winfo_screenwidth()
alto = app.winfo_screenheight()
app.geometry(f"{ancho}x{alto}+0+0")
app.configure(fg_color="#1725a5")

# Configurar la cuadrícula
for i in range(4):
    app.grid_columnconfigure(i, weight=1)
app.grid_rowconfigure(1, weight=3)
app.grid_rowconfigure(0, weight=1)
app.grid_rowconfigure(2, weight=1)

# Fila 0: logo - red - reloj
logo_img = Image.open(logo_path).resize((150, 150), Image.Resampling.LANCZOS)
logo_tk = ImageTk.PhotoImage(logo_img)
logo_label = customtkinter.CTkLabel(app, image=logo_tk, text="")
logo_label.image = logo_tk
logo_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

red_label = customtkinter.CTkLabel(app, text="🛜" + wifi(), font=("Arial", 20, "bold"), text_color="white", anchor="center")
red_label.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=10)

reloj_label = customtkinter.CTkLabel(app, text="", font=("Arial", 20, "bold"), text_color="white")
reloj_label.grid(row=0, column=3, sticky="e", padx=10)

# Fila 1: imagen central
img_central_pil = Image.open(imagen_central)
canvas_central = customtkinter.CTkCanvas(app, bg="white")
canvas_central.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=20, pady=20)
canvas_central.bind("<Configure>", update_imagen_central)

# Fila 2: botones
boton_seleccion = customtkinter.CTkButton(app, text="Seleccion de campo", command=abrir_seleccion_campo, width=200, height=60, font=("Arial", 18), corner_radius=10, fg_color="#02080F", hover_color="#022E51", text_color="white")
boton_VAR = customtkinter.CTkButton(app, text="VAR", command=Abrir_VAR, width=200, height=60, font=("Arial", 18), corner_radius=10, fg_color="#02080F", hover_color="#022E51", text_color="white")
boton_porterias = customtkinter.CTkButton(app, text="Porterias", command=seleccion_porterias, width=200, height=60, font=("Arial", 18), corner_radius=10, fg_color="#02080F", hover_color="#022E51", text_color="white")
boton_vercampo = customtkinter.CTkButton(app, text="Ver Campo", command=ver_campo, width=200, height=60, font=("Arial", 18), corner_radius=10, fg_color="#02080F", hover_color="#022E51", text_color="white")
boton_grabaciones = customtkinter.CTkButton(app, text="Grabaciones", command=abrir_grabaciones, width=200, height=60, font=("Arial", 18), corner_radius=10, fg_color="#02080F", hover_color="#022E51", text_color="white")

# Posicionar botones
boton_seleccion.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
boton_VAR.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
boton_porterias.grid(row=2, column=2, padx=10, pady=10, sticky="ew")
boton_vercampo.grid(row=2, column=3, padx=10, pady=10, sticky="ew")
boton_grabaciones.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

# Iniciar reloj y mainloop
actualizar_reloj()
app.mainloop()
