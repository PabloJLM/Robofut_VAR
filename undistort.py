import os
import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt
import random

# Visualizations will be shown in the notebook.
plt.rcParams["figure.figsize"] = [20, 15]  # Ajustar el tamaño de la ventana

# Directories to be created (except 'camera_cal' as it's assumed to exist)
directories = ['corners', 'calibration_wide', 'calibration_data', 'test_images']

# Create directories if they don't exist
for dir in directories:
    if not os.path.exists(dir):
        os.makedirs(dir)

# Load chessboard images for calibration
chessboards = []
for i in range(1, 21):
    file_name = f'camera_cal/calibration{i}.jpg'
    image = cv2.imread(file_name)
    chessboards.append(image)

# Prepare object points for the chessboard grid
obj_points = np.zeros((6 * 9, 3), np.float32)
obj_points[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

object_points = []  # 3D points in real-world space
image_points = []   # 2D points in image plane

# Find corners in chessboard images
for i in range(len(chessboards)):
    ret, corners = cv2.findChessboardCorners(chessboards[i], (9, 6), None)
    if ret:
        object_points.append(obj_points)
        image_points.append(corners)

        # Draw and display the corners
        cv2.drawChessboardCorners(chessboards[i], (9, 6), corners, ret)
        write_name = f'corners/corners_found{i}.jpg'
        cv2.imwrite(write_name, chessboards[i])

# Perform camera calibration
img = cv2.imread('camera_cal/calibration1.jpg')
img_size = (img.shape[1], img.shape[0])

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(object_points, image_points, img_size, None, None)

# Undistort an image using the calibration matrices
dst = cv2.undistort(img, mtx, dist, None, mtx)
cv2.imwrite('calibration_wide/test_undist.jpg', dst)

# Save the camera calibration result
dist_pickle = {"mtx": mtx, "dist": dist}
pickle.dump(dist_pickle, open("calibration_data/calibration_matrices.p", "wb"))

# Check if 'test_images' folder exists and contains 'test1.jpg'
test_image_path = 'test_images/test1.jpg'
if not os.path.exists('test_images'):
    os.makedirs('test_images')  # Create 'test_images' folder if it doesn't exist

if os.path.exists(test_image_path):
    image = cv2.imread(test_image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    u_image = cv2.undistort(image, mtx, dist, None, mtx)

    # Visualize the original, undistorted, and difference images in a single window
    plt.figure(figsize=(20, 15))

    # Original image
    plt.subplot(3, 4, 1)
    plt.imshow(image)
    plt.title('Original Image', fontsize=14)

    # Undistorted image
    plt.subplot(3, 4, 2)
    plt.imshow(u_image)
    plt.title('Undistorted Image', fontsize=14)

    # Difference between the original and undistorted images
    new_image = cv2.subtract(image, u_image)
    plt.subplot(3, 4, 3)
    plt.imshow(new_image, cmap="gray")
    plt.title('Difference Image', fontsize=14)

else:
    print(f"El archivo {test_image_path} no existe. Por favor, coloca la imagen allí.")

# Display some of the chessboard images with corners drawn
for i in range(4):  # Show 4 chessboard images
    index = random.randint(0, len(chessboards) - 1)
    image = chessboards[index].squeeze()
    plt.subplot(3, 4, 4 + i)  # Starting from the 4th column
    plt.imshow(image, cmap="gray")
    plt.title(f'Chessboard: {index}')

plt.tight_layout()  # Adjust the layout so images do not overlap
plt.show()