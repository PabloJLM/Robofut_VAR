import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

class Seleccion_Cam:
    def __init__(self, root):
        self.root = root
        self.root.title("Seleccionar Cámara")

        ctk.CTkLabel(root, text="Índice de Cámara:").grid(row=0, column=0, padx=10, pady=10)
        self.cam_index = ctk.CTkEntry(root, width=50)
        self.cam_index.grid(row=0, column=1, padx=10, pady=10)
        self.cam_index.insert(0, "0")

        ctk.CTkButton(root, text="Aceptar", command=self.confirm).grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.selected_index = None

    def confirm(self):
        try:
            self.selected_index = int(self.cam_index.get())
            self.root.destroy()
        except ValueError:
            pass

    def get_index(self):
        self.root.mainloop()
        return self.selected_index

class Principal:
    def __init__(self, root, cam_index):
        self.root = root
        self.root.title("Calibrador de HSV")

        self.sliders = {}
        self.labels = {}
        self.entries = {}

        values = {
            "Hue Min": (0, 179),
            "Hue Max": (0, 179),
            "Sat Min": (0, 255),
            "Sat Max": (0, 255),
            "Val Min": (0, 255),
            "Val Max": (0, 255)
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
            
        self.sliders["Hue Min"].set(0)
        self.sliders["Hue Max"].set(179)
        self.sliders["Sat Min"].set(0)
        self.sliders["Sat Max"].set(255)
        self.sliders["Val Min"].set(0)
        self.sliders["Val Max"].set(255)

        self.image_label = ctk.CTkLabel(root, text="")
        self.image_label.grid(row=0, column=1, padx=10, pady=10)


        self.cap = cv2.VideoCapture(cam_index)
        self.update_frame()

        table_frame = ctk.CTkFrame(self.root)
        table_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ns")

        ctk.CTkLabel(table_frame, text="Valores HSV para colores", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, padx=10, pady=5)

        ctk.CTkLabel(table_frame, text="Color", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="H", font=("Arial", 12, "bold")).grid(row=1, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="S", font=("Arial", 12, "bold")).grid(row=1, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="V", font=("Arial", 12, "bold")).grid(row=1, column=3, padx=5, pady=2)

        ctk.CTkLabel(table_frame, text="Rojo", font=("Arial", 12), text_color="red").grid(row=2, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="125-180").grid(row=2, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=2, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=2, column=3, padx=5, pady=2)

        ctk.CTkLabel(table_frame, text="Naranja", font=("Arial", 12), text_color="orange").grid(row=3, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="0-10").grid(row=3, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=3, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="0-255").grid(row=3, column=3, padx=5, pady=2)

        ctk.CTkLabel(table_frame, text="Amarillo", font=("Arial", 12), text_color="yellow").grid(row=4, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="25-35").grid(row=4, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=4, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=4, column=3, padx=5, pady=2)

        ctk.CTkLabel(table_frame, text="Verde", font=("Arial", 12), text_color="green").grid(row=5, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="40-85").grid(row=5, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=5, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=5, column=3, padx=5, pady=2)

        ctk.CTkLabel(table_frame, text="Azul", font=("Arial", 12), text_color="blue").grid(row=6, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="85-130").grid(row=6, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=6, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=6, column=3, padx=5, pady=2)

        ctk.CTkLabel(table_frame, text="Morado", font=("Arial", 12), text_color="purple").grid(row=7, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="130-160").grid(row=7, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=7, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="100-255").grid(row=7, column=3, padx=5, pady=2)

        ctk.CTkLabel(table_frame, text="Negro", font=("Arial", 12)).grid(row=8, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="Cualquier H").grid(row=8, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="0-50").grid(row=8, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="0-50").grid(row=8, column=3, padx=5, pady=2)

        ctk.CTkLabel(table_frame, text="Blanco", font=("Arial", 12)).grid(row=9, column=0, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="Cualquier H").grid(row=9, column=1, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="0-50").grid(row=9, column=2, padx=5, pady=2)
        ctk.CTkLabel(table_frame, text="170-255").grid(row=9, column=3, padx=5, pady=2)


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
                min_val, max_val = 0, 179 if "Hue" in name else 255
                val = max(min_val, min(val, max_val))
                self.sliders[name].set(val)
            except ValueError:
                pass

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lower_bound = np.array([int(self.sliders["Hue Min"].get()), 
                                    int(self.sliders["Sat Min"].get()), 
                                    int(self.sliders["Val Min"].get())])
            upper_bound = np.array([int(self.sliders["Hue Max"].get()), 
                                    int(self.sliders["Sat Max"].get()), 
                                    int(self.sliders["Val Max"].get())])

            mask = cv2.inRange(hsv, lower_bound, upper_bound)
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
    
    cam_selection_root = ctk.CTk()
    cam_selection = Seleccion_Cam(cam_selection_root)
    cam_index = cam_selection.get_index()

    root = ctk.CTk()
    app = Principal(root, cam_index)
    app.run()
