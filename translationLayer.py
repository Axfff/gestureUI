import numpy as np
import threading
from extractionLayer import HANDeXTRACTOR, CAMERA
import time


class GestureRecognizer:
    def __init__(self, buildModelFunction, modelWeightsPath=None):
        self.model = buildModelFunction()
        if modelWeightsPath:
            self.model.load_weights(modelWeightsPath)

        self.x = None

    def loadData(self, x):
        self.x = x
        self.__normalize()

    def __normalize(self):
        # # get edge 3D
        # x_max = self.x[0][0]
        # x_min = self.x[0][0]
        # y_max = self.x[0][1]
        # y_min = self.x[0][1]
        # z_min = self.x[0][2]
        # z_max = self.x[0][2]
        # for p in self.x[1:]:
        #     x_max = max(x_max, p[0])
        #     x_min = min(x_min, p[0])
        #     y_max = max(y_max, p[1])
        #     y_min = min(y_min, p[1])
        #     z_max = max(z_max, p[2])
        #     z_min = min(z_min, p[2])
        # edge = ((x_min, y_min, z_min), (x_max, y_max, z_max))
        #
        # # coordinate remap 3D
        # points_new = []
        # remapRange = ((0, 0, 0), (1, 1, 1))
        # for p in self.x:
        #     points_new.append(
        #         ((remapRange[1][0] - remapRange[0][0]) * (p[0] - edge[0][0]) / (edge[1][0] - edge[0][0]),
        #          (remapRange[1][1] - remapRange[0][1]) * (p[1] - edge[0][1]) / (edge[1][1] - edge[0][1]),
        #          (remapRange[1][2] - remapRange[0][2]) * (p[2] - edge[0][2]) / (edge[1][2] - edge[0][2]))
        #     )
        points_new = np.array(self.x)
        xs = points_new[:, 0]
        ys = points_new[:, 1]
        zs = points_new[:, 2]
        x_max = np.max(xs)
        x_min = np.min(xs)
        y_max = np.max(ys)
        y_min = np.min(ys)
        z_max = np.max(zs)
        z_min = np.min(zs)
        xs = (xs-x_min)/(x_max - x_min)
        ys = (ys-y_min)/(y_max - y_min)
        zs = (zs-z_min)/(z_max - z_min)
        pCount = len(xs)
        points_new = np.concatenate((np.reshape(xs, (pCount, 1)), np.reshape(ys, (pCount, 1)), np.reshape(zs, (pCount, 1))), axis=1)
        # print(points_new)

        # transform to model use
        self.x = np.array(
            [points_new]
        )

    def getGestureType(self):
        return np.argmax(self.model.predict(self.x)[0])


class HandCoorCalculator:
    def __init__(self, handExtractorObject: HANDeXTRACTOR, cameraObject: CAMERA, keyPointIndexes: list = None):
        self.camera = cameraObject

        if keyPointIndexes is None:
            self.keyPointIndexes = np.array([i for i in range(21)])
        else:
            self.keyPointIndexes = np.array(keyPointIndexes)
        # print(self.keyPointIndexes)
        self.statusShape = (1, self.keyPointIndexes.shape[0], 3)

        self.extractor = handExtractorObject
        self.enable_calculationThread = True
        self.extractorResult = np.full(self.statusShape, np.nan)
        self.extractorResultTimeStamp = time.time()
        self.calculationThread = threading.Thread(target=self.__func_calculationThread)
        self.calculationThread.setDaemon(True)
        self.calculationThread.start()
        self.v = np.zeros(self.statusShape)

        self.extractorLossJudge_s = 0.2

    def __func_calculationThread(self):
        lostTime = 0
        lastRes = np.full(self.statusShape, np.nan)
        currentTimeStamp = time.time()
        lastTimeStamp = currentTimeStamp

        while self.enable_calculationThread:
            currentTimeStamp = time.time()
            delta_t = currentTimeStamp - lastTimeStamp
            lastTimeStamp = currentTimeStamp

            # print('calculationThreadRunning')
            success, image = self.camera.getCorrectedImage()
            # ignore error frame
            if not success:
                continue
            self.extractor.loadImage(image)
            extRes = self.extractor.getHandLandmarks()
            # print(self.extractorResult, type(self.extractorResult))

            if extRes.size != 0:
                extRes = extRes[0, self.keyPointIndexes, ...]  # only use the 1st hand
                self.extractorResult = extRes.reshape(self.statusShape)
                self.extractorResultTimeStamp = time.time()
                lostTime = 0
                if True not in np.isnan(lastRes):
                    self.v = (extRes - lastRes)/delta_t
                lastRes = extRes
            else:
                lostTime += delta_t
                if lostTime > self.extractorLossJudge_s:
                    self.extractorResult = np.full(self.statusShape, np.nan)
                    self.v = np.zeros(self.statusShape)

    def get_pos(self):
        # print(type(self.extractorResult), type(self.v))
        if True in np.isnan(self.extractorResult):
            res = np.full(self.statusShape, np.nan)
        else:
            # print(self.extractorResult, self.v)
            # print(self.v)
            res = self.extractorResult + self.v*(time.time()-self.extractorResultTimeStamp)
        return res


class PerspectiveMapping:
    def __init__(self, p00, p01, p10, p11):
        self.p00 = None
        self.p01 = None
        self.p10 = None
        self.p11 = None
        self.a0 = None
        self.a1 = None

        self.setParameter(p00, p01, p10, p11)

    def __decompositionVectorInSourceQuadrilateral(self, p11, p01, p10):
        r01 = (p01[0]-self.p00[0], p01[1]-self.p00[1])
        r10 = (p10[0]-self.p00[0], p10[1]-self.p00[1])
        r11 = (p11[0]-self.p00[0], p11[1]-self.p00[1])

        alpha0 = (r10[0]*r11[1]-r10[1]*r11[0])/(r10[0]*r01[1]-r01[0]*r10[1])
        alpha1 = (r01[0]*r11[1]-r11[0]*r01[1])/(r01[0]*r10[1]-r10[0]*r01[1])

        return alpha0, alpha1

    def loadRangeEdgePos(self, xs, ys):
        pass

    def setParameter(self, p00, p01, p10, p11):
        self.p00 = p00
        self.p01 = p01
        self.p10 = p10
        self.p11 = p11

        self.a0, self.a1 = self.__decompositionVectorInSourceQuadrilateral(p11, p01, p10)

    def remap(self, pos):
        y0, y1 = self.__decompositionVectorInSourceQuadrilateral(pos, self.p01, self.p10)

        x0 = (self.a1 * (self.a0 + self.a1 - 1) * y0) / (self.a0*self.a1 + self.a1*(self.a1-1)*y0 + self.a0*(self.a0-1)*y1)
        x1 = (self.a0 * (self.a0 + self.a1 - 1) * y1) / (self.a0*self.a1 + self.a1*(self.a1-1)*y0 + self.a0*(self.a0-1)*y1)

        return x0, x1


if __name__ == '__main__':
    from buildModel import buildModel
    import time
    from extractionLayer import CAMERA, HANDeXTRACTOR
    import cv2

    cam = CAMERA()
    extractor = HANDeXTRACTOR()
    recognizer = GestureRecognizer(buildModel, r'models/v0.1_1024epochs.h5')

    t = time.time()
    # fpss = []
    while cam.isOpened():
        success, image = cam.getCorrectedImage()
        if not success:
            continue

        extractor.loadImage(image)
        results = extractor.getHandLandmarks()

        for handCoors in results:
            recognizer.loadData(handCoors)
            gestureType = recognizer.getGestureType()
            print(gestureType)

        showImg = extractor.getShowImage(zoomFactor=0.25)
        dt = time.time() - t
        t = time.time()
        # print(dt, t)
        fps = 1/dt

        # fpss.append(fps)
        # if len(fpss) >= 100:
        #     print(numpy.mean(fpss))
        #     break
        cv2.putText(showImg, f'FPS: {round(fps, 2)}', (5, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', showImg)
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cam.release()