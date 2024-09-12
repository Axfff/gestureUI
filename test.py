import time

'''
import tensorflow as tf

print(tf.test.is_gpu_available())
'''

from translationLayer import HandCoorCalculator
from extractionLayer import CAMERA
from extractionLayer import HANDeXTRACTOR
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
# plt.ion()

cam = CAMERA(capNum=0, resolution=(640, 480))
extractor = HANDeXTRACTOR()
hcc1 = HandCoorCalculator(handExtractorObject=extractor, cameraObject=cam, keyPointIndexes=[8])
preList = []
extList = []
for i in range(256):
    res = hcc1.get_pos()
    print(res)
    ext = hcc1.extractorResult

    if True not in np.isnan(res):
        preList.append(res[0, 0, [0, 1]])
    if True not in np.isnan(ext):
        extList.append(ext[0, 0, [0, 1]])

    # try:
    #     cv.imshow('camView', hcc1.extractor.getShowImage(1))
    # except:
    #     pass

    # plt.clf()
    # plt.xlim(0, 1)
    # plt.ylim(0, 1)
    # plt.gca().invert_xaxis()
    # plt.gca().invert_yaxis()
    # if res is not None:
    #     if np.nan not in res:
    #         plt.scatter(res[0, 0, 0], res[0, 0, 1])
    # plt.pause(0.001)

    time.sleep(0.01)

# plt.xlim(0, 1)
# plt.ylim(0, 1)
plt.gca().invert_xaxis()
plt.gca().invert_yaxis()
preList = np.array(preList)
extList = np.array(extList)
print(preList)
print(extList)
plt.scatter(preList[..., 0], preList[..., 1])
plt.scatter(extList[..., 0], extList[..., 1])
plt.show()

