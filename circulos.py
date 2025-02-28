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
        self.cam_index.insert(0, "1")
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
        self.root.title("Calibrador de HSV y Detección de Círculos")
        self.sliders = {}
        self.labels = {}
        self.entries = {}
        self.switches = {}
        
        values = {"Hue Min": (0, 179), "Hue Max": (0, 179), "Sat Min": (0, 255),
                  "Sat Max": (0, 255), "Val Min": (0, 255), "Val Max": (0, 255)}
        
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
            
        switch_frame = ctk.CTkFrame(root)
        switch_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ns")
        
        for i, color in enumerate(["Pelotas Naranjas", "Pelotas Blancas", "LEDs Rojos", "LEDs Azules"]):
            self.switches[color] = ctk.CTkSwitch(switch_frame, text=color)
            self.switches[color].grid(row=i, column=0, padx=5, pady=5, sticky="w")
        
        self.image_label = ctk.CTkLabel(root, text="")
        self.image_label.grid(row=0, column=1, padx=10, pady=10)
        self.cap = cv2.VideoCapture(cam_index)
        self.update_frame()
    
    def update_values(self, _=None):
        for name in self.labels:
            val = int(self.sliders[name].get())
            self.labels[name].configure(text=f"{val}")
            self.entries[name].delete(0, ctk.END)
            self.entries[name].insert(0, str(val))
        
        # Actualizar switches basados en sliders
        self.switches["Pelotas Naranjas"].select() if self.sliders["Hue Min"].get() < 20 else self.switches["Pelotas Naranjas"].deselect()
        self.switches["Pelotas Blancas"].select() if self.sliders["Sat Min"].get() < 50 else self.switches["Pelotas Blancas"].deselect()
        self.switches["LEDs Rojos"].select() if self.sliders["Hue Min"].get() > 160 else self.switches["LEDs Rojos"].deselect()
        self.switches["LEDs Azules"].select() if 80 < self.sliders["Hue Min"].get() < 130 else self.switches["LEDs Azules"].deselect()

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
            gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 50, param1=50, param2=30, minRadius=5, maxRadius=50)
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i in circles[0, :]:
                    cv2.circle(result, (i[0], i[1]), i[2], (0, 255, 0), 2)
            img = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
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
