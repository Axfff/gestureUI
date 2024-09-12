import numpy as np
import cv2 as cv
import glob


# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*8, 3), np.float32)
objp[:, :2] = np.mgrid[0:6, 0:8].T.reshape(-1, 2)
# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
images = glob.glob('*.jpg')
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (6, 8), None)
    # print(ret, corners)
    # If found, add object points, image points (after refining them)
    if ret is True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (6, 8), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

cv.destroyAllWindows()


img = cv.imread('28.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print(f'{ret},\n {mtx},\n {dist},\n {rvecs},\n {tvecs}')
with open('camera_property_mtx', 'wb') as f:
    print(mtx.tobytes())
    f.write(mtx.tobytes())
with open('camera_property_dist', 'wb') as f:
    print(dist.tobytes())
    f.write(dist.tobytes())





