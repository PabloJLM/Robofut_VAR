import customtkinter
import cv2
import requests
import numpy as np
from PIL import Image, ImageTk
import pupil_apriltags as apriltag

url = "http://192.168.0.3/image.jpg" 
username = "admin"  
password = "admin" 

# usar la familia 36h11
detector = apriltag.Detector(families="tag36h11")

def get_frame_from_camera():

    try:
        response = requests.get(url, auth=(username, password), stream=True)
        response.raise_for_status()
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"Error al obtener la imagen: {e}")
        return None

def detectar_apriltags(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detecciones = detector.detect(gray)

    for tag in detecciones:
        (ptA, ptB, ptC, ptD) = tag.corners
        ptA, ptB, ptC, ptD = map(lambda p: (int(p[0]), int(p[1])), [ptA, ptB, ptC, ptD])

        cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
        cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
        cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
        cv2.line(frame, ptD, ptA, (0, 255, 0), 2)
        cv2.putText(frame, f"ID: {tag.tag_id}", (ptA[0], ptA[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return frame

def update_video():

    frame = get_frame_from_camera()

    if frame is not None:
        frame = detectar_apriltags(frame)  

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((video_canvas.winfo_width(), video_canvas.winfo_height()))
        img_tk = ImageTk.PhotoImage(img)

        video_canvas.create_image(0, 0, anchor="nw", image=img_tk)
        video_canvas.image = img_tk

    app.after(10, update_video) 

app = customtkinter.CTk()
app.title("Detección de AprilTags en Tiempo Real")
app.geometry("800x600")

app.grid_rowconfigure(0, weight=1)
app.grid_rowconfigure(1, weight=0)
app.grid_columnconfigure((0, 1, 2), weight=1)

video_canvas = customtkinter.CTkCanvas(app, bg="black")
video_canvas.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

'''button1 = customtkinter.CTkButton(app, text="Button 1", command=lambda: print("Button 1 pressed"), width=200, height=50)
button1.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

button2 = customtkinter.CTkButton(app, text="Button 2", command=lambda: print("Button 2 pressed"), width=200, height=50)
button2.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

button3 = customtkinter.CTkButton(app, text="Button 3", command=lambda: print("Button 3 pressed"), width=200, height=50)
button3.grid(row=1, column=2, padx=10, pady=10, sticky="ew")'''

update_video()

app.mainloop()
