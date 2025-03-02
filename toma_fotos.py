import cv2
import os

calibration_dir = "camera_cal"
test_dir = "test_images"

if not os.path.exists(calibration_dir):
    os.makedirs(calibration_dir)
    print(f"Directorio creado: {calibration_dir}")

if not os.path.exists(test_dir):
    os.makedirs(test_dir)
    print(f"Directorio creado: {test_dir}")

# Iniciar CAM
link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.20:554/stream1"
cap = cv2.VideoCapture(link)
#cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

print("Presiona 'ESPACIO' para capturar una imagen. 'q' para salir.")

calibration_count = 0
while calibration_count < 20:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo capturar la imagen.")
        break
    
    cv2.putText(frame, f"Capturas: {calibration_count}/20", (1024,50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Captura de Tablero", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '): 
        file_path = os.path.join(calibration_dir, f"calibration{calibration_count+1}.jpg")
        cv2.imwrite(file_path, frame)
        print(f"Imagen guardada: {file_path}")
        calibration_count += 1

    elif key == ord('q'): 
        break

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo capturar la imagen de prueba.")
        break

    cv2.imshow("Captura de Imagen de Prueba", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        test_image_path = os.path.join(test_dir, "test1.jpg")
        cv2.imwrite(test_image_path, frame)
        print(f"Imagen de prueba guardada: {test_image_path}")
        break

    elif key == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
print("Proceso finalizado.")
