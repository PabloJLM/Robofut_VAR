import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

VIDEO_PATH = "Orange Bouncing Ball Animation.mp4"  # Cambia esto por la ruta a tu video

class Principal:
    def __init__(self, root):
        self.root = root
        self.root.title("Calibrador de HSV")

        self.frame_width = 640
        self.frame_height = 480

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

        # Valores por defecto iniciales
        self.sliders["Hue Min"].set(0)
        self.sliders["Hue Max"].set(179)
        self.sliders["Sat Min"].set(0)
        self.sliders["Sat Max"].set(255)
        self.sliders["Val Min"].set(0)
        self.sliders["Val Max"].set(255)

        self.image_label = ctk.CTkLabel(root, text="")
        self.image_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.cap = cv2.VideoCapture(VIDEO_PATH)
        if not self.cap.isOpened():
            print("Error: No se pudo abrir el video")
            exit()

        self.root.bind("<Configure>", self.resize_window)
        self.update_frame()

    def resize_window(self, event=None):
        self.frame_width = self.root.winfo_width() - 20
        self.frame_height = self.root.winfo_height() - 50

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
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reiniciar video
            ret, frame = self.cap.read()

        if ret:
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lower_bound = np.array([
                int(self.sliders["Hue Min"].get()), 
                int(self.sliders["Sat Min"].get()), 
                int(self.sliders["Val Min"].get())
            ])
            upper_bound = np.array([
                int(self.sliders["Hue Max"].get()), 
                int(self.sliders["Sat Max"].get()), 
                int(self.sliders["Val Max"].get())
            ])

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
    root = ctk.CTk()
    root.geometry("800x600")
    app = Principal(root)
    app.run()
