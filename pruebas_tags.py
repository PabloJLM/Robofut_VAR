import cv2
import pupil_apriltags as apriltag

# Cargar imagen
imagen = cv2.imread("apriltag_prueba.jpg", cv2.IMREAD_GRAYSCALE)

# Crear detector
detector = apriltag.Detector()

# Detectar tags
resultados = detector.detect(imagen)

# Dibujar los resultados
for r in resultados:
    for p in r.corners:
        p = tuple(map(int, p))  # Convertir a enteros
        cv2.circle(imagen, p, 5, (0, 255, 0), -1)  # Dibujar puntos de las esquinas

    # Mostrar el ID del tag
    centro = tuple(map(int, r.center))
    cv2.putText(imagen, str(r.tag_id), centro, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

# Mostrar imagen con detecciones
cv2.imshow("Detección de AprilTags", imagen)
cv2.waitKey(0)
cv2.destroyAllWindows()
