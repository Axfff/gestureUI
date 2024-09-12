import cv2
import mediapipe as mp
import numpy


class CAMERA:
    def __init__(self, resolution=None, capNum=None):
        if resolution is None:
            resolution = (1920, 1080)
        if capNum is None:
            capNum = 0

        self.cap = cv2.VideoCapture(capNum)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        self.image = None
        self.corrected_image = None

        self.mtx, self.dist = None, None
        self.loadCamProperties()

    def loadCamProperties(self):
        with open('camera_property_mtx', 'rb') as f:
            self.mtx = numpy.frombuffer(f.read(), dtype=float)
            self.mtx = self.mtx.reshape((3, 3))
            # print(mtx)
        with open('camera_property_dist', 'rb') as f:
            self.dist = numpy.frombuffer(f.read(), dtype=float)
            self.dist = self.dist.reshape((1, 5))
            # print(dist)
        return self.mtx, self.dist

    def isOpened(self):
        return self.cap.isOpened()

    def captureImage(self):
        isSucceed, self.image = self.cap.read()

        if not isSucceed:
            print("Ignoring empty camera frame.")
            return False, False

        self.image.flags.writeable = False
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        return True, self.image

    def undistort(self):
        h, w = self.image.shape[:2]
        newCameraMtx, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (w, h), 1, (w, h))

        # undistort
        self.corrected_image = cv2.undistort(self.image, self.mtx, self.dist, None, newCameraMtx)

        return self.corrected_image

    def getCorrectedImage(self):
        if self.captureImage()[0] is False:
            return False, False
        return True, self.undistort()

    def release(self):
        self.cap.release()


class HANDeXTRACTOR:
    def __init__(self, model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
                        model_complexity=model_complexity,
                        min_detection_confidence=min_detection_confidence,
                        min_tracking_confidence=min_tracking_confidence)

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.image = None
        self.imageShow = None

        # data returned by mediapipe
        self.results = None

    def loadImage(self, img):
        self.image = img

    def getHandLandmarks(self):
        self.results = self.hands.process(self.image)
        detectedHands = []

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                coors = []
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    coors.append((landmark.x, landmark.y, landmark.z))
                detectedHands.append(coors)

        detectedHands = numpy.array(detectedHands)

        return detectedHands

    def getShowImage(self, zoomFactor):
        self.imageShow = self.image
        self.imageShow.flags.writeable = True
        self.imageShow = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    self.imageShow,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())

        showResolution = (int(self.image.shape[1] * zoomFactor), int(self.image.shape[0] * zoomFactor))
        return cv2.flip(cv2.resize(self.imageShow, showResolution), 1)


if __name__ == '__main__':
    from translationLayer import GestureRecognizer
    from buildModel import buildModel
    import time

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
        fps = 1 / dt

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
