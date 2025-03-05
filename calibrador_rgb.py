import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

RTSP_URL = "rtsp://PabloJ1012:PabloJ1012@192.168.0.3:554/stream1"

class Principal:
    def __init__(self, root):
        self.root = root
        self.root.title("Calibrador de RGB")

        self.frame_width = 640
        self.frame_height = 480

        self.sliders = {}
        self.labels = {}
        self.entries = {}

        values = {
            "Red Min": (0, 255),
            "Red Max": (0, 255),
            "Green Min": (0, 255),
            "Green Max": (0, 255),
            "Blue Min": (0, 255),
            "Blue Max": (0, 255)
        }

        slider_frame = ctk.CTkFrame(root)
        slider_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        for i, (name, (min_val, max_val)) in enumerate(values.items()):
            ctk.CTkLabel(slider_frame, text=name).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.sliders[name] = ctk.CTkSlider(slider_frame, from_=min_val, to=max_val, command=self.update_values)
            self.sliders[name].grid(row=i, column=1, padx=5, pady=5)
            self.labels[name] = ctk.CTkLabel(slider_frame, text=f"{int(self.sliders[name].get())}")
            self.labels[name].grid(row=i, column=2, padx=5, pady=5)

            self.entries[name] = ctk.CTkEntry(slider_frame, width=50)
            self.entries[name].grid(row=i, column=3, padx=5, pady=5)
            self.entries[name].insert(0, str(int(self.sliders[name].get())))
            self.entries[name].bind("<Return>", self.update_from_entry)
            
        # Valores iniciales
        self.sliders["Red Min"].set(0)
        self.sliders["Red Max"].set(255)
        self.sliders["Green Min"].set(0)
        self.sliders["Green Max"].set(255)
        self.sliders["Blue Min"].set(0)
        self.sliders["Blue Max"].set(255)

        self.image_label = ctk.CTkLabel(root, text="")
        self.image_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.cap = cv2.VideoCapture(RTSP_URL)
        if not self.cap.isOpened():
            print("Error: No se pudo conectar a la cámara IP")

        # Detectar cambios de tamaño de ventana
        self.root.bind("<Configure>", self.resize_window)
        
        self.update_frame()

    def resize_window(self, event=None):
        """ Ajusta el tamaño del frame según el tamaño de la ventana """
        self.frame_width = self.root.winfo_width() - 20  # Ajuste de margen
        self.frame_height = self.root.winfo_height() - 50  # Ajuste de margen

    def update_values(self, _=None):
        for name in self.labels:
            val = int(self.sliders[name].get())
            self.labels[name].configure(text=f"{val}")
            self.entries[name].delete(0, ctk.END)
            self.entries[name].insert(0, str(val))

    def update_from_entry(self, event):
        for name in self.entries:
            try:
                val = int(self.entries[name].get())
                val = max(0, min(val, 255))  # Asegurar que esté en rango
                self.sliders[name].set(val)
            except ValueError:
                pass

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Redimensiona el frame al tamaño de la ventana
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))

            # Convertir a RGB (OpenCV usa BGR por defecto)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            lower_bound = np.array([int(self.sliders["Red Min"].get()), 
                                    int(self.sliders["Green Min"].get()), 
                                    int(self.sliders["Blue Min"].get())])
            upper_bound = np.array([int(self.sliders["Red Max"].get()), 
                                    int(self.sliders["Green Max"].get()), 
                                    int(self.sliders["Blue Max"].get())])

            mask = cv2.inRange(frame_rgb, lower_bound, upper_bound)
            result = cv2.bitwise_and(frame, frame, mask=mask)

            img = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(img)

            self.image_label.configure(image=img)
            self.image_label.image = img

        self.root.after(10, self.update_frame)

    def run(self):
        self.root.mainloop()
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.geometry("800x600")  # Tamaño inicial
    root.attributes('-fullscreen', False)  # Puedes cambiarlo a True para iniciar en pantalla completa
    app = Principal(root)
    app.run()
