import cv2 as cv
import numpy as np


def getCameraProperties():
    with open('camera_property_mtx', 'rb') as f:
        mtx = np.frombuffer(f.read(), dtype=float)
        mtx = mtx.reshape((3, 3))
        print(mtx)
    with open('camera_property_dist', 'rb') as f:
        dist = np.frombuffer(f.read(), dtype=float)
        dist = dist.reshape((1, 5))
        print(dist)
    return mtx, dist


def imgCorrection(img):
    h, w = img.shape[:2]
    newCameraMtx, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, DistortionCoefficients, (w, h), 1, (w, h))

    # undistort
    dst = cv.undistort(img, cameraMatrix, DistortionCoefficients, None, newCameraMtx)

    return dst


if __name__ == '__main__':
    cameraMatrix, DistortionCoefficients = getCameraProperties()

    image = cv.imread('t.jpg')
    imageNew = imgCorrection(image)

    # crop the image
    # x, y, w, h = roi
    # dst = dst[y:y+h, x:x+w]
    cv.imshow('afterCorrection', imageNew)
    cv.waitKey()
    cv.imwrite('calibresult.png', imageNew)



