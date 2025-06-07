import customtkinter
import cv2
import numpy as np
from PIL import Image, ImageTk
import time

mascara_inf = np.array([0, 54, 0])  
mascara_sup = np.array([179, 255, 255])
VIDEO_PATH = "Orange Bouncing Ball Animation.mp4"
LOGO_PATH = "logo.png"   
CAMPO_PATH = "campo.jpg"   

cap = cv2.VideoCapture(VIDEO_PATH)

app = customtkinter.CTk()
app.title("Pelota Rastreadora")
app.geometry("800x700")
app.configure(fg_color="#03539e")

titulo_frame = customtkinter.CTkFrame(app, fg_color="#03539e")
titulo_frame.pack(fill="x", pady=10)

# Logo
logo_img = Image.open(LOGO_PATH).resize((200, 85), Image.Resampling.LANCZOS)
logo_tk = ImageTk.PhotoImage(logo_img)
logo_label = customtkinter.CTkLabel(titulo_frame, image=logo_tk, text="")
logo_label.image = logo_tk
logo_label.pack(side="left", padx=10)

# Título
titulo = customtkinter.CTkLabel(titulo_frame, text="Panel de Control", font=("Arial Black", 24, "bold"), text_color="white")
titulo.pack(side="left", expand=True)

# Reloj
reloj_label = customtkinter.CTkLabel(titulo_frame, text="", font=("Arial", 24, "bold"), text_color="white")
reloj_label.pack(side="right", padx=10)

def actualizar_reloj():
    hora_actual = time.strftime("%H:%M:%S")
    reloj_label.configure(text=hora_actual)
    app.after(1000, actualizar_reloj)

actualizar_reloj()

# ------------------ VIDEO ------------------
video_canvas = customtkinter.CTkCanvas(app, bg="black", width=640, height=360)
video_canvas.pack(pady=10)

# ------------------ MAPA ------------------
campo = customtkinter.CTkCanvas(app, width=640, height=240, bg="white")
campo.pack(pady=10)

def update_video():
    ret, frame = cap.read()

    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return app.after(10, update_video)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)

    canvas_w = video_canvas.winfo_width()
    canvas_h = video_canvas.winfo_height()
    img = img.resize((canvas_w, canvas_h))
    img_tk = ImageTk.PhotoImage(img)

    video_canvas.create_image(0, 0, anchor="nw", image=img_tk)
    video_canvas.image = img_tk

    update_map(frame)
    app.after(10, update_video)

def update_map(frame):
    campo.delete("all")

    x_campo = campo.winfo_width()
    y_campo = campo.winfo_height()

    img_PIL = Image.open(CAMPO_PATH).resize((x_campo, y_campo))
    img_campo = ImageTk.PhotoImage(img_PIL)
    campo.create_image(0, 0, anchor="nw", image=img_campo)
    campo.image = img_campo
    campo.lower("all")

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, mascara_inf, mascara_sup)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)

        if radius > 5:
            frame_h, frame_w = frame.shape[:2]
            map_x = int((x / frame_w) * x_campo)
            map_y = int((y / frame_h) * y_campo)
            campo.create_oval(map_x - 25, map_y - 25, map_x + 25, map_y + 25, fill="orange", outline="")

def cerrar_app():
    cap.release()
    cv2.destroyAllWindows()
    app.destroy()

app.protocol("WM_DELETE_WINDOW", cerrar_app)
app.after(100, update_video)
app.mainloop()
