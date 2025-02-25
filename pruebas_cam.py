import customtkinter
import cv2
import numpy as np
import time
import threading
from PIL import Image, ImageTk
import pupil_apriltags as apriltag

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_EXPOSURE, -5)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 100)

detector = apriltag.Detector(families="tag36h11", quad_decimate=2.0, quad_sigma=0.1)
grabando = False
frame_actual = None
lock = threading.Lock()
coordenadas = {}  

colores = [
    "red", "blue", "green", "orange", "purple", "cyan", "yellow", "magenta", "white"
]

def get_color(tag_id):
    return colores[tag_id % len(colores)]  

def capturar_frames():
    global frame_actual
    while True:
        ret, frame = cap.read()
        if ret:
            with lock:
                frame_actual = frame

threading.Thread(target=capturar_frames, daemon=True).start()

def detectar_apriltags(frame):
    global coordenadas
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    detecciones = detector.detect(gray)

    for tag in detecciones:
        (ptA, ptB, ptC, ptD) = tag.corners
        centro = np.mean([ptA, ptB, ptC, ptD], axis=0).astype(int)
        tag_id = tag.tag_id

        if tag_id not in coordenadas:
            coordenadas[tag_id] = []

        coordenadas[tag_id].append(tuple(centro))

        if len(coordenadas[tag_id]) > 50:
            coordenadas[tag_id].pop(0)

        ptA, ptB, ptC, ptD = map(lambda p: (int(p[0]), int(p[1])), [ptA, ptB, ptC, ptD])

        cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
        cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
        cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
        cv2.line(frame, ptD, ptA, (0, 255, 0), 2)

        cv2.putText(frame, f"ID: {tag_id}", (ptA[0], ptA[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return frame

def update_video():
    with lock:
        frame = frame_actual.copy() if frame_actual is not None else None

    if frame is not None:
        frame = detectar_apriltags(frame)

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
    cam_x, cam_y = 640, 480

    for tag_id, coords in coordenadas.items():
        color = get_color(tag_id)

        for i in range(1, len(coords)):
            x1, y1 = coords[i - 1]
            x2, y2 = coords[i]

            x1 = int(x1 / cam_x * x_campo)
            y1 = int(y1 / cam_y * y_campo)
            x2 = int(x2 / cam_x * x_campo)
            y2 = int(y2 / cam_y * y_campo)

            campo.create_line(x1, y1, x2, y2, fill=color, width=2)

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
            frame = detectar_apriltags(frame)
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
app.title("aaaa")
app.geometry("800x700")

app.grid_rowconfigure(0, weight=3)
app.grid_rowconfigure(1, weight=1)
app.grid_rowconfigure(2, weight=0)
app.grid_columnconfigure((0, 1, 2), weight=1)

video_canvas = customtkinter.CTkCanvas(app, bg="black", width=640, height=480)
video_canvas.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

campo = customtkinter.CTkCanvas(app, width=640, height=480, bg="white")
campo.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")


'''
record_button = customtkinter.CTkButton(app, text="Grabar 15s", command=grabar_video, width=200, height=50)
record_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

exit_button = customtkinter.CTkButton(app, text="Salir", command=cerrar_app, width=200, height=50)
exit_button.grid(row=2, column=2, padx=10, pady=10, sticky="ew")'''

update_video()
app.protocol("WM_DELETE_WINDOW", cerrar_app)
app.mainloop()
