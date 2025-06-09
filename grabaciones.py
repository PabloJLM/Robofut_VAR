import customtkinter
import os
from tkinter import filedialog
import tkinter.messagebox
import webbrowser

class VentanaGrabaciones(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Grabaciones VAR")
        self.geometry("700x500")
        self.configure(fg_color="#1b1f2b")
        
        self.var_folder = None

        self.label = customtkinter.CTkLabel(self, text="Selecciona la carpeta para las grabaciones", font=("Arial", 16))
        self.label.pack(pady=10)

        self.boton_seleccionar = customtkinter.CTkButton(self, text="Seleccionar carpeta", command=self.seleccionar_carpeta)
        self.boton_seleccionar.pack(pady=5)

        self.lista_videos = customtkinter.CTkTextbox(self, height=350, width=600)
        self.lista_videos.pack(pady=10)

        self.boton_refrescar = customtkinter.CTkButton(self, text="Refrescar lista", command=self.mostrar_videos)
        self.boton_refrescar.pack(pady=5)

    def seleccionar_carpeta(self):
        ruta_base = filedialog.askdirectory(title="Selecciona carpeta base")
        if not ruta_base:
            return
        
        ruta_var = os.path.join(ruta_base, "var")
        os.makedirs(ruta_var, exist_ok=True)

        self.var_folder = ruta_var
        self.mostrar_videos()

    def mostrar_videos(self):
        if not self.var_folder:
            tkinter.messagebox.showwarning("Atención", "Primero selecciona una carpeta.")
            return

        archivos = [f for f in os.listdir(self.var_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        self.lista_videos.delete("1.0", "end")

        if not archivos:
            self.lista_videos.insert("end", "No hay grabaciones en esta carpeta.")
            return

        for archivo in archivos:
            ruta = os.path.join(self.var_folder, archivo)
            self.lista_videos.insert("end", f"{archivo}\n")

            # También podrías hacer que se pueda abrir haciendo clic, si lo deseas.
