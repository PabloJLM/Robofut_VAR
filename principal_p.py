import customtkinter
import cv2
import numpy as np
import time
import threading
from PIL import Image, ImageTk

logo_path = "logo.png"
cap = cv2.VideoCapture(0)


grabando = False
frame_actual = None
lock = threading.Lock()

def capturar_frames():
    global frame_actual
    while True:
        ret, frame = cap.read()
        if ret:
            with lock:
                frame_actual = frame

threading.Thread(target=capturar_frames, daemon=True).start()

def update_video():
    with lock:
        frame = frame_actual.copy() if frame_actual is not None else None

    if frame is not None:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((video_canvas.winfo_width(), video_canvas.winfo_height()))
        img_tk = ImageTk.PhotoImage(img)

        video_canvas.create_image(0, 0, anchor="nw", image=img_tk)
        video_canvas.image = img_tk

    update_map()
    app.after(10, update_video)

def update_map():
    campo.delete("all")

    x_campo = campo.winfo_width()
    y_campo = campo.winfo_height()

    img_PIL = Image.open("campo.jpg").resize((x_campo, y_campo))
    img_campo = ImageTk.PhotoImage(img_PIL)

    campo.create_image(0, 0, anchor="nw", image=img_campo)
    campo.image = img_campo
    campo.lower("all")

def grabar_video():
    global grabando

    if grabando:
        return

    grabando = True
    time.sleep(3)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("grabacion.mp4", fourcc, 30.0, (640, 480))

    start_time = time.time()
    while time.time() - start_time < 15:
        with lock:
            frame = frame_actual.copy() if frame_actual is not None else None
        if frame is not None:
            out.write(frame)
            cv2.imshow("Grabando...", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    out.release()
    cv2.destroyAllWindows()
    grabando = False

def cerrar_app():
    cap.release()
    cv2.destroyAllWindows()
    app.destroy()

app = customtkinter.CTk()
app.configure(fg_color="#03539e")
app.title("aaaa")
app.geometry("800x700")

titulo_frame = customtkinter.CTkFrame(app)
titulo_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
titulo_frame.columnconfigure([0, 1, 2], weight=1)
titulo_frame.configure(fg_color="#03539e")

logo_img = Image.open(logo_path).resize((200, 85), Image.Resampling.LANCZOS)
logo_tk = ImageTk.PhotoImage(logo_img)
logo_label = customtkinter.CTkLabel(titulo_frame, image=logo_tk, text="")
logo_label.image = logo_tk
logo_label.grid(row=0, column=0, sticky="w", padx=5)

titulo = customtkinter.CTkLabel(titulo_frame, text="Panel de Control", font=("Arial Black", 24, "bold"), text_color="white")
titulo.grid(row=0, column=1, sticky="nsew")

reloj_label = customtkinter.CTkLabel(titulo_frame, text="", font=("Arial", 24, "bold"), text_color="white")
reloj_label.grid(row=0, column=2, padx=10, sticky="e")

def actualizar_reloj():
    hora_actual = time.strftime("%H:%M:%S")
    reloj_label.configure(text=hora_actual)
    app.after(1000, actualizar_reloj)

actualizar_reloj()

app.grid_rowconfigure(1, weight=1)
app.grid_rowconfigure(2, weight=1)
app.grid_columnconfigure(0, weight=1)

video_canvas = customtkinter.CTkCanvas(app, bg="black", width=640, height=480)
video_canvas.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

campo = customtkinter.CTkCanvas(app, width=640, height=480, bg="white")
campo.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

'''
record_button = customtkinter.CTkButton(app, text="Grabar 15s", command=grabar_video, width=200, height=50)
record_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

exit_button = customtkinter.CTkButton(app, text="Salir", command=cerrar_app, width=200, height=50)
exit_button.grid(row=2, column=2, padx=10, pady=10, sticky="ew")
'''

update_video()
app.protocol("WM_DELETE_WINDOW", cerrar_app)
app.mainloop()
