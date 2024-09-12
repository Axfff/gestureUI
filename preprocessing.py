import cv2 as cv
import numpy as np


def getEdge2D(points):
    x_max = points[0][0]
    x_min = points[0][0]
    y_max = points[0][1]
    y_min = points[0][1]
    for p in points[1:]:
        x_max = max(x_max, p[0])
        x_min = min(x_min, p[0])
        y_max = max(y_max, p[1])
        y_min = min(y_min, p[1])
    return (x_min, y_min), (x_max, y_max)


def coordinateRemap2D(points, remapRange):
    edge = getEdge2D(points)
    points_new = []
    for p in points:
        points_new.append(
            ((remapRange[1][0] - remapRange[0][0]) * (p[0] - edge[0][0]) / (edge[1][0] - edge[0][0]),
             (remapRange[1][1] - remapRange[0][1]) * (p[1] - edge[0][1]) / (edge[1][1] - edge[0][1]),
             p[2])
        )
    return points_new


def getEdge3D(points):
    x_max = points[0][0]
    x_min = points[0][0]
    y_max = points[0][1]
    y_min = points[0][1]
    z_min = points[0][2]
    z_max = points[0][2]
    for p in points[1:]:
        x_max = max(x_max, p[0])
        x_min = min(x_min, p[0])
        y_max = max(y_max, p[1])
        y_min = min(y_min, p[1])
        z_max = max(z_max, p[2])
        z_min = min(z_min, p[2])
    return (x_min, y_min, z_min), (x_max, y_max, z_max)


def coordinateRemap3D(points, remapRange=((0, 0, 0), (1, 1, 1))):
    edge = getEdge3D(points)
    points_new = []
    for p in points:
        points_new.append(
            ((remapRange[1][0] - remapRange[0][0]) * (p[0] - edge[0][0]) / (edge[1][0] - edge[0][0]),
             (remapRange[1][1] - remapRange[0][1]) * (p[1] - edge[0][1]) / (edge[1][1] - edge[0][1]),
             (remapRange[1][2] - remapRange[0][2]) * (p[2] - edge[0][2]) / (edge[1][2] - edge[0][2]))
        )
    return points_new


def getCameraProperties():
    with open('camera_property_mtx', 'rb') as f:
        mtx = np.frombuffer(f.read(), dtype=float)
        mtx = mtx.reshape((3, 3))
        # print(mtx)
    with open('camera_property_dist', 'rb') as f:
        dist = np.frombuffer(f.read(), dtype=float)
        dist = dist.reshape((1, 5))
        # print(dist)
    return mtx, dist


def imgCorrection(img, mtx, dist):
    h, w = img.shape[:2]
    newCameraMtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # undistort
    dst = cv.undistort(img, mtx, dist, None, newCameraMtx)

    return dst


if __name__ == '__main__':
    import os

    if input('This Operation will change files, sure to continue? (Y/n)') != 'Y':
        exit()
    for fileName in os.listdir(r'datasets_withoutNormalize'):
        filePath = r'datasets_withoutNormalize/' + fileName
        writePath = r'datasets/' + fileName
        if filePath[-3:] != 'txt':
            continue
        with open(filePath, 'r') as f:
            print(f'loading file: {filePath}')
            # print(len(f.readlines()))
            for ind, line in enumerate(f.readlines()):
                # print(line[:-2])
                try:
                    data = eval(line[:-1])
                except:
                    continue
                if ind == 0:
                    len_data = len(data)
                else:
                    if len_data != len(data):
                        continue
                data = coordinateRemap3D(data, ((0, 0, 0), (1, 1, 1)))
                with open(writePath, 'a') as fn:
                    fn.write(str(data))
                    fn.write('\n')


