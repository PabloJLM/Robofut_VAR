import cv2



link = "rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2"
cap = cv2.VideoCapture(link)

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Resolución detectada: {w}x{h}")

if not cap.isOpened():
    print("Error al abrir la transmisión RTSP")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al recibir el frame")
        break

    cv2.imshow("cam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
