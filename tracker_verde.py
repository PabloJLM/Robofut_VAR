import cv2
import numpy as np

# Configuraciones
max_objetos_verde = 1
max_objetos_rojo = 1

# Abrir stream RTSP
cap = cv2.VideoCapture("rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2")

if not cap.isOpened():
    print("Error: No se pudo abrir el stream RTSP")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se recibió frame")
        break

    # Filtro HSV inicial para eliminar blancos
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    low_hsv = np.array([0, 76, 90])
    up_hsv = np.array([179, 255, 255])
    mask_hsv = cv2.inRange(hsv, low_hsv, up_hsv)
    result_hsv = cv2.bitwise_and(frame, frame, mask=mask_hsv)

    # Limpieza
    blurred = cv2.GaussianBlur(result_hsv, (9, 9), 0)
    kernel = np.ones((5, 5), np.uint8)
    limpieza = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel)
    limpieza_rgb = cv2.cvtColor(limpieza, cv2.COLOR_BGR2RGB)

    dibujo = frame

    ### TRACKER VERDE ###
    rgb_low_verde = np.array([0, 138, 0])
    rgb_up_verde = np.array([104, 255, 150])
    mask_verde = cv2.inRange(limpieza_rgb, rgb_low_verde, rgb_up_verde)
    contornos_verde, _ = cv2.findContours(mask_verde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_verde = sorted(contornos_verde, key=cv2.contourArea, reverse=True)

    objetos_procesados_verde = 0
    for contorno in contornos_verde:
        if objetos_procesados_verde >= max_objetos_verde:
            break
        area = cv2.contourArea(contorno)
        if area > 50:
            x, y, w, h = cv2.boundingRect(contorno)
            cx = x + w // 2
            cy = y + h // 2
            cv2.rectangle(dibujo, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Verde
            cv2.circle(dibujo, (cx, cy), 4, (0, 0, 255), -1)  # Centro rojo
            cv2.putText(dibujo, f"V({cx},{cy})", (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            objetos_procesados_verde += 1

    ### TRACKER ROJO ###
    rgb_low_rojo = np.array([215, 86, 0])   # R, G, B
    rgb_up_rojo = np.array([255, 140, 180])
    mask_rojo = cv2.inRange(limpieza_rgb, rgb_low_rojo, rgb_up_rojo)
    contornos_rojo, _ = cv2.findContours(mask_rojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_rojo = sorted(contornos_rojo, key=cv2.contourArea, reverse=True)

    objetos_procesados_rojo = 0
    for contorno in contornos_rojo:
        if objetos_procesados_rojo >= max_objetos_rojo:
            break
        area = cv2.contourArea(contorno)
        if area > 50:
            x, y, w, h = cv2.boundingRect(contorno)
            cx = x + w // 2
            cy = y + h // 2
            cv2.rectangle(dibujo, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Rojo
            cv2.circle(dibujo, (cx, cy), 4, (0, 255, 255), -1)  # Centro amarillo
            cv2.putText(dibujo, f"R({cx},{cy})", (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            objetos_procesados_rojo += 1

    # Mostrar frame con ambos rastreos
    cv2.imshow("Tracking verde y rojo", dibujo)

    # Salir con ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
