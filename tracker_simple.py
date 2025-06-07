import cv2
import numpy as np

VIDEO_PATH = "Orange Bouncing Ball Animation.mp4"

lower_bound = np.array([0, 54, 0])  
upper_bound = np.array([179, 255, 255])

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("Error: No se pudo abrir el video")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue


    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(largest)

        if radius > 5:  

            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
            cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"({int(x)}, {int(y)})", (int(x)+10, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

    cv2.imshow("Tracker", frame)

    key = cv2.waitKey(30)
    if key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()
