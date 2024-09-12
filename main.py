import cv2
from buildModel import buildModel
import numpy as np
import time
from extractionLayer import CAMERA, HANDeXTRACTOR
from translationLayer import HandCoorCalculator
from translationLayer import GestureRecognizer
from interactiveLayer.Controller import HoldingDetector
from interactiveLayer.Controller import Cursor
from interactiveLayer.Controller import FixedLengthNumInput
from interactiveLayer.Controller import FixedLengthNumListener
from interactiveLayer.Widget import ImageLabel
from interactiveLayer.Widget import RectangleButton
from interactiveLayer.Interface import Interface
from executiveLayer.DataTransmit import TcpSocket, UdpSocket

cam = CAMERA(capNum=0, resolution=(640, 480))
extractor = HANDeXTRACTOR()
recognizer = GestureRecognizer(buildModel, r'models/v0.1_1024epochs.h5')
handCoorCalculator = HandCoorCalculator(extractor, cam)

# hassTcp = TcpSocket()
# ptzUdp = UdpSocket()

# set GUI
interface = Interface((1280, 720), (0, 0, 0, 255))
cursor = Cursor(interface=interface)
butt1 = RectangleButton(interface, pos=(300, 400), size=(150, 150), radius=75,
                        command=lambda: hassTcp.sendData('lamp_light_toggle'))
butt2 = RectangleButton(interface, pos=(510, 400), size=(150, 150), radius=75,
                        command=lambda: hassTcp.sendData('hanging_light_toggle'))
butt3 = RectangleButton(interface, pos=(720, 400), size=(150, 150), radius=75,
                        command=lambda: hassTcp.sendData('bed_light_toggle'))
butt4 = RectangleButton(interface, pos=(600, 50), size=(195, 200), radius=15,
                        command=lambda: hassTcp.sendData('cover_open'))
butt5 = RectangleButton(interface, pos=(800, 50), size=(195, 200), radius=15,
                        command=lambda: hassTcp.sendData('cover_stop'))
butt6 = RectangleButton(interface, pos=(1000, 50), size=(195, 200), radius=15,
                        command=lambda: hassTcp.sendData('cover_close'))
camView = ImageLabel(interface=interface, imgBox=(10, 10), tab=['keepWhileSleep'])
camView.enable = True
activateChecker = FixedLengthNumListener(interface=interface, length=4, answer=[2, 0, 2, 0], tab=['activateChecker'],
                                      command=lambda: interface.activate())  # print('hahahaha') sendData('hanging_light_toggle')
activateChecker.enable = True
holdingListener1 = HoldingDetector(interface=interface, listenType=1, activeTime_ms=1200,
                                   command=lambda: hassTcp.sendData('lamp_light_toggle'))  # print('hahahaha') cursor.clearMap())
sleepListener = HoldingDetector(interface=interface, listenType=7, activeTime_ms=1200,
                                command=lambda: interface.sleep())  # print('hahahaha') sendData('lamp_light_toggle')

t = time.time()  # use to calculate fps
# mainloop
while cam.isOpened():
    success, image = cam.getCorrectedImage()
    # ignore error frame
    if not success:
        continue

    results = handCoorCalculator.get_pos()
    # print(results)
    
    cx1, cy1 = 0, 0
    cx2, cy2 = 0, 0
    gestureType = None
    for handCoors in results:
        recognizer.loadData(handCoors)
        gestureType = recognizer.getGestureType()
        print(gestureType)
        # if True in np.isnan(handCoors):
        #     if interface.isActivating:
        #         ptzUdp.sendData(f'Stop;Stop', targetAddr=("192.168.31.25", 1234))
        #     else:
        #         # print('None; None')
        #         ptzUdp.sendData(f'None;None', targetAddr=("192.168.31.25", 1234))
        # else:
        #     if not interface.isActivating:
        #         ex_hand, ey_hand = 0.5 - handCoors[9][0], 0.5 - handCoors[9][1]
        #         ptzUdp.sendData(f'{ex_hand};{ey_hand}', targetAddr=("192.168.31.25", 1234))
        #     else:
        #         ptzUdp.sendData(f'Stop;Stop', targetAddr=("192.168.31.25", 1234))

        if gestureType == 2 or gestureType == 10:
            cx1, cy1 = (1 - handCoors[8][0]) * 1280, handCoors[8][1] * 720
            cx2, cy2 = (1 - handCoors[12][0]) * 1280, handCoors[12][1] * 720
            # print(((handCoors[8][0] - handCoors[12][0]) ** 2 + (handCoors[8][1] - handCoors[12][1]) ** 2) /
            #       ((handCoors[5][0] - handCoors[9][0]) ** 2 + (handCoors[5][1] - handCoors[9][1]) ** 2))
            if ((handCoors[8][0] - handCoors[12][0]) ** 2 + (handCoors[8][1] - handCoors[12][1]) ** 2) >= 1.7 * (
                    (handCoors[5][0] - handCoors[9][0]) ** 2 + (handCoors[5][1] - handCoors[9][1]) ** 2):
                gestureType = 2
            else:
                gestureType = 10
        break  # just now, only use the first result detected.
    if len(results) == 0:
        if interface.isActivating:
            ptzUdp.sendData(f'Stop;Stop', targetAddr=("192.168.31.25", 1234))
        else:
            # print('None; None')
            ptzUdp.sendData(f'None;None', targetAddr=("192.168.31.25", 1234))

    showImg = extractor.getShowImage(zoomFactor=0.5)
    # print(showImg.shape)

    # calculate fps
    dt = time.time() - t
    t = time.time()
    fps = 1 / dt

    cv2.putText(showImg, f'FPS: {round(fps, 2)}', (5, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # update GUI
    camView.loadImageArray(cv2.cvtColor(showImg, cv2.COLOR_BGR2RGBA), mode='RGBA')
    cursor.loadData((cx1, cy1), (cx2, cy2), gestureType)
    activateChecker.loadData(gestureType=gestureType)
    sleepListener.loadData(gestureType=gestureType)
    holdingListener1.loadData(gestureType=gestureType)

    interface.update()

cam.release()
