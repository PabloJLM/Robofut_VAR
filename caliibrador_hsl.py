import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

RTSP_URL = "rtsp://PabloJ1012:PabloJ1012@192.168.0.3:554/stream1"

class CalibradorHSL:
    def __init__(self, root):
        self.root = root
        self.root.title("Calibrador de HSL")

        # Configuración inicial de tamaño
        self.frame_width = 640
        self.frame_height = 480

        self.sliders = {}
        self.labels = {}
        self.entries = {}

        valores = {
            "Hue Min": (0, 179),  # Hue en OpenCV va de 0 a 179
            "Hue Max": (0, 179),
            "Light Min": (0, 255),  # Lightness de 0 a 255
            "Light Max": (0, 255),
            "Sat Min": (0, 255),  # Saturación de 0 a 255
            "Sat Max": (0, 255)
        }

        frame_controles = ctk.CTkFrame(root)
        frame_controles.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        for i, (nombre, (min_val, max_val)) in enumerate(valores.items()):
            ctk.CTkLabel(frame_controles, text=nombre).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.sliders[nombre] = ctk.CTkSlider(frame_controles, from_=min_val, to=max_val, command=self.actualizar_valores)
            self.sliders[nombre].grid(row=i, column=1, padx=5, pady=5)
            self.labels[nombre] = ctk.CTkLabel(frame_controles, text=f"{int(self.sliders[nombre].get())}")
            self.labels[nombre].grid(row=i, column=2, padx=5, pady=5)

            self.entries[nombre] = ctk.CTkEntry(frame_controles, width=50)
            self.entries[nombre].grid(row=i, column=3, padx=5, pady=5)
            self.entries[nombre].insert(0, str(int(self.sliders[nombre].get())))
            self.entries[nombre].bind("<Return>", self.actualizar_desde_entrada)
            
        self.sliders["Hue Min"].set(0)
        self.sliders["Hue Max"].set(179)
        self.sliders["Light Min"].set(0)
        self.sliders["Light Max"].set(255)
        self.sliders["Sat Min"].set(0)
        self.sliders["Sat Max"].set(255)

        self.etiqueta_imagen = ctk.CTkLabel(root, text="")
        self.etiqueta_imagen.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.camara = cv2.VideoCapture(RTSP_URL)
        if not self.camara.isOpened():
            print("Error: No se pudo conectar a la cámara IP")

        # Detectar cambios de tamaño de ventana
        self.root.bind("<Configure>", self.redimensionar_ventana)
        
        self.actualizar_frame()

    def redimensionar_ventana(self, event=None):
        """ Ajusta el tamaño del frame según el tamaño de la ventana """
        self.frame_width = self.root.winfo_width() - 20  
        self.frame_height = self.root.winfo_height() - 50  

    def actualizar_valores(self, _=None):
        for nombre in self.labels:
            val = int(self.sliders[nombre].get())
            self.labels[nombre].configure(text=f"{val}")
            self.entries[nombre].delete(0, ctk.END)
            self.entries[nombre].insert(0, str(val))

    def actualizar_desde_entrada(self, event):
        for nombre in self.entries:
            try:
                val = int(self.entries[nombre].get())
                min_val, max_val = (0, 179) if "Hue" in nombre else (0, 255)
                val = max(min_val, min(val, max_val))
                self.sliders[nombre].set(val)
            except ValueError:
                pass

    def actualizar_frame(self):
        ret, frame = self.camara.read()
        if ret:
            # Redimensiona el frame al tamaño de la ventana
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))

            # Convertir BGR a HSL
            hsl = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

            # Obtener valores de los sliders
            limite_inferior = np.array([int(self.sliders["Hue Min"].get()), 
                                        int(self.sliders["Light Min"].get()), 
                                        int(self.sliders["Sat Min"].get())])
            limite_superior = np.array([int(self.sliders["Hue Max"].get()), 
                                        int(self.sliders["Light Max"].get()), 
                                        int(self.sliders["Sat Max"].get())])

            mascara = cv2.inRange(hsl, limite_inferior, limite_superior)
            resultado = cv2.bitwise_and(frame, frame, mask=mascara)

            img = cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(img)

            self.etiqueta_imagen.configure(image=img)
            self.etiqueta_imagen.image = img

        self.root.after(10, self.actualizar_frame)

    def ejecutar(self):
        self.root.mainloop()
        self.camara.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.geometry("800x600")  
    root.attributes('-fullscreen', False)  
    app = CalibradorHSL(root)
    app.ejecutar()
