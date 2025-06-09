import customtkinter
from tkinter import filedialog, messagebox
from PIL import Image
import os
import cv2
import threading

class VideoPlayer(customtkinter.CTkToplevel):
    def __init__(self, video_path):
        super().__init__()
        self.title(f"Reproduciendo: {os.path.basename(video_path)}")
        self.geometry("800x600")
        self.configure(fg_color="black")

        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)

        self.label = customtkinter.CTkLabel(self, text="")
        self.label.pack(fill="both", expand=True)

        self.running = True
        threading.Thread(target=self.reproducir_video, daemon=True).start()

        self.protocol("WM_DELETE_WINDOW", self.cerrar)

    def reproducir_video(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (800, 600))
            img = Image.fromarray(frame)
            img_tk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(800, 600))
            self.label.configure(image=img_tk)
            self.label.image = img_tk
            self.update()
            cv2.waitKey(30)

    def cerrar(self):
        self.running = False
        self.cap.release()
        self.destroy()


def generar_miniatura(video_path, output_path, tamaño=(160, 90)):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_n = total_frames // 4
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img = img.resize(tamaño, Image.Resampling.LANCZOS)
    img.save(output_path)
    return output_path


class VentanaGrabaciones(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Grabaciones VAR")
        self.geometry("900x600")
        self.configure(fg_color="#1b1f2b")

        self.var_folder = None

        self.label = customtkinter.CTkLabel(self, text="Selecciona la carpeta con grabaciones", font=("Arial", 16))
        self.label.pack(pady=10)

        self.boton_seleccionar = customtkinter.CTkButton(self, text="Seleccionar carpeta", command=self.seleccionar_carpeta)
        self.boton_seleccionar.pack(pady=5)

        self.scroll = customtkinter.CTkScrollableFrame(self, width=850, height=450)
        self.scroll.pack(pady=10, expand=True)

        self.boton_refrescar = customtkinter.CTkButton(self, text="Refrescar lista", command=self.mostrar_videos)
        self.boton_refrescar.pack(pady=5)

    def seleccionar_carpeta(self):
        ruta = filedialog.askdirectory(title="Selecciona la carpeta con grabaciones")
        if not ruta:
            return
        self.var_folder = ruta
        self.mostrar_videos()

    def mostrar_videos(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not self.var_folder:
            messagebox.showwarning("Atención", "Primero selecciona una carpeta.")
            return

        archivos = [f for f in os.listdir(self.var_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

        if not archivos:
            customtkinter.CTkLabel(self.scroll, text="No hay videos en esta carpeta.", font=("Arial", 14)).pack(pady=10)
            return

        for archivo in archivos:
            ruta_video = os.path.join(self.var_folder, archivo)
            ruta_thumb = os.path.join(self.var_folder, f"{archivo}_thumb.jpg")

            if not os.path.exists(ruta_thumb):
                generar_miniatura(ruta_video, ruta_thumb)

            try:
                img = Image.open(ruta_thumb)
                img_ctk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(160, 90))
            except:
                continue

            frame = customtkinter.CTkFrame(self.scroll)
            frame.pack(padx=10, pady=5, fill="x")

            label = customtkinter.CTkLabel(frame, image=img_ctk, text="", width=160, height=90)
            label.image = img_ctk
            label.pack(side="left", padx=10)

            boton = customtkinter.CTkButton(frame, text=archivo, command=lambda r=ruta_video: VideoPlayer(r), width=600, anchor="w")
            boton.pack(side="left", fill="x", expand=True, padx=5)


if __name__ == "__main__":
    app = customtkinter.CTk()
    app.withdraw()
    VentanaGrabaciones()
    app.mainloop()
