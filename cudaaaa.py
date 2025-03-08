import cv2
import numpy as np

link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.3:554/stream2"
cap = cv2.VideoCapture(link, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print("Error: No se pudo abrir el video.")
    exit()

lower_bound = (0, 0, 0)  
upper_bound = (179, 52, 255)  

gpu_frame = cv2.cuda_GpuMat()   # Imagen en GPU
gpu_hsv = cv2.cuda_GpuMat()     # Imagen HSV en GPU
gpu_mask = cv2.cuda_GpuMat()    # Máscara en GPU

while True:
    ret, frame = cap.read()
    if not ret:
        break 

    gpu_frame.upload(frame)

    gpu_hsv = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2HSV)

    gpu_mask = cv2.cuda.inRange(gpu_hsv, lower_bound, upper_bound)
    
    gpu_mask_3channels = cv2.cuda_GpuMat(gpu_hsv.size(), cv2.CV_8UC3)
    cv2.cuda.cvtColor(gpu_mask, cv2.COLOR_GRAY2BGR, gpu_mask_3channels)

    mezcla = cv2.cuda_GpuMat(gpu_hsv.size(), gpu_hsv.type())

    gpu_bgr = cv2.cuda.cvtColor(gpu_hsv, cv2.COLOR_HSV2BGR)

    cv2.cuda.bitwise_and(gpu_bgr, gpu_mask_3channels, mezcla)


    #mask = gpu_mask_3channels.download()

    cv2.imshow("Original", frame)
    cv2.imshow("Máscara de Color", mezcla.download()) 
    if cv2.waitKey(1) & 0xFF == ord('q' or 'Q'):
        break

cap.release()
cv2.destroyAllWindows()