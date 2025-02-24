import cv2
import numpy as np
import os

def generar_apriltags(n=10, family=cv2.aruco.DICT_APRILTAG_36h11, size=1000, folder="apriltags"):
    os.makedirs(folder, exist_ok=True)

    aruco_dict = cv2.aruco.getPredefinedDictionary(family)

    for tag_id in range(n):
        tag_img = cv2.aruco.generateImageMarker(aruco_dict, tag_id, size)

        filename = f"{folder}/apriltag_{tag_id}.png"
        cv2.imwrite(filename, tag_img)
        print(f" Tag {tag_id} guardado como {filename}")

generar_apriltags(n=10)
