import cv2
import numpy as np

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    minimo1 = np.array([0, 150, 255])
    maximo1 = np.array([179, 255, 255])
    mask1 = cv2.inRange(hsv, minimo1, maximo1)
    
    
    minimo2 = np.array([0, 0, 255])
    maximo2 = np.array([90, 200, 255])
    mask2 = cv2.inRange(hsv, minimo2, maximo2)
    
    combined_mask = cv2.bitwise_or(mask1, mask2)
    result = cv2.bitwise_or(frame, frame, mask=combined_mask)
    
    cv2.imshow("Original", frame)
    cv2.imshow("Mask 1", mask1)
    cv2.imshow("Mask 2", mask2)
    cv2.imshow("combinada", combined_mask)
    cv2.imshow("final", result)
    
    
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()