import cv2

#depende de la cam
link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.20:554/stream1"

cap = cv2.VideoCapture(link)
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"Resolución detectada: {int(w)}x{int(h)}")


if not cap.isOpened():
    print("Error al abrir la transmisión RTSP")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al recibir el frame")
        break

    cv2.imshow("RTSP Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
