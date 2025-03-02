import cv2
import pickle
import os


calibration_file = "calibration_data/calibration_matrices.p"
if not os.path.exists(calibration_file):
    print(f"Error: No se encontró {calibration_file}. Primero calibra la cámara.")
    exit()

with open(calibration_file, "rb") as f:
    calib_data = pickle.load(f)
    mtx = calib_data["mtx"]
    dist = calib_data["dist"]

link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.20:554/stream1"
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
    correccion = cv2.undistort(frame, mtx, dist, None, mtx)
    
    diferencia = cv2.absdiff(frame, correccion)

    diferencia = cv2.normalize(diferencia, None, 0, 255, cv2.NORM_MINMAX)

    cv2.imshow("cam", correccion)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
