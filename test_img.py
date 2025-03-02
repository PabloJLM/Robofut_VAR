import cv2
import os

test_dir = "test_images"
if not os.path.exists(test_dir):
    os.makedirs(test_dir)
    print(f"Directorio creado: {test_dir}")

link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.20:554/stream1"
cap = cv2.VideoCapture(link)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

print("Presiona 'ESPACIO' para capturar y guardar la imagen. 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo capturar la imagen.")
        break

    cv2.imshow("Captura de Imagen", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):  
        test_image_path = os.path.join(test_dir, "test1.jpg")
        cv2.imwrite(test_image_path, frame)
        print(f"Imagen guardada: {test_image_path}")
        break

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

