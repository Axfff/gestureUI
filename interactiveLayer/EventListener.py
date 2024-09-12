from interactiveLayer.Event import *
from time import time


class EventListener:
    pass


class CursorEventsListener(EventListener):
    def __init__(self):
        self.suspendGestureType = 2
        self.tapGestureType = 10

        self.activateFilterTime_ms = 20
        self.releaseFilterTime_ms = 20
        self.tapHoldTimeRange_ms = 400
        self.pressStartJudge_ms = 1600
        self.dragStartPosRadius_px = 50
        self.suspendStartJudge_ms = 1000

        self.isActivate = False
        self.touchTime = 0
        self.lostTime = 0
        self.activeTime = 0
        self.isTap = False
        self.isDrag = 0
        self.startPos = (False, False)
        self.isPress = False

        self.lastUpdateTimestamp = time() * 1000

        self.eventList = []

    def loadData(self, pos, gestureType):
        self.eventList = []

        nowTime = time() * 1000
        dt = nowTime - self.lastUpdateTimestamp
        self.lastUpdateTimestamp = nowTime

        if gestureType == self.tapGestureType:
            if self.isActivate:
                self.activeTime += dt
                if self.isDrag:
                    self.eventList.append(Dragging(pos, (pos[0] - self.startPos[0], pos[1] - self.startPos[1])))
                else:
                    # print(self.startPos, pos)
                    # print((pos[0]-self.startPos[0])**2+(pos[1]-self.startPos[1])**2, self.dragStartPosRadius_px**2)
                    if (pos[0] - self.startPos[0]) ** 2 + (
                            pos[1] - self.startPos[1]) ** 2 >= self.dragStartPosRadius_px ** 2:
                        self.eventList.append(
                            DraggingStart(pos, (pos[0] - self.startPos[0], pos[1] - self.startPos[1])))
                        self.isDrag = True
                        self.isTap = False
                        self.isPress = False
                    else:
                        if self.activeTime >= self.tapHoldTimeRange_ms:
                            if self.isTap:
                                self.eventList.append(TapTimeOut(pos))
                                self.isTap = False
                            # print(self.activeTime)
                            if self.activeTime >= self.pressStartJudge_ms:
                                if self.isPress:
                                    self.eventList.append(Press(pos, self.activeTime - self.pressStartJudge_ms))
                                else:
                                    self.eventList.append(PressStart(pos))
                                    self.isPress = True
                            else:
                                self.eventList.append(
                                    PressWaiting(pos,
                                                 (self.activeTime-self.tapHoldTimeRange_ms)/(self.pressStartJudge_ms-self.tapHoldTimeRange_ms)))
                        else:
                            self.eventList.append(Tap(pos, self.activeTime))
            else:
                self.touchTime += dt
                if self.touchTime >= self.activateFilterTime_ms:
                    self.isActivate = True
                    self.touchTime = 0
                    self.activeTime = 0
                    self.eventList.append(TapStart(pos))
                    self.isTap = True
                    self.startPos = pos
        else:
            if self.isActivate:
                self.lostTime += dt
                if self.lostTime >= self.releaseFilterTime_ms:
                    self.isActivate = False
                    self.lostTime = 0
                    if self.isTap:
                        self.eventList.append(TapEnd(pos, self.activeTime))
                        self.isTap = False
                    elif self.isPress:
                        self.eventList.append(PressEnd(pos, self.activeTime - self.pressStartJudge_ms))
                        self.isPress = False
                    elif self.isDrag:
                        self.eventList.append(DraggingEnd(pos, (pos[0] - self.startPos[0], pos[1] - self.startPos[1])))
                        self.startPos = (False, False)
                        self.isDrag = False
                else:
                    self.touchTime = 0
                    self.eventList.append(Suspending(pos))
            else:
                self.touchTime = 0
                if gestureType == self.suspendGestureType:
                    self.eventList.append(Suspending(pos))

    def update(self) -> list:
        return self.eventList


class FiniteHoldingEventsListener(EventListener):
    def __init__(self, listenType, targetTime_ms=3000):
        self.listenType = listenType
        self.targetTime_ms = targetTime_ms

        self.activateFilterTime_ms = 20
        self.releaseFilterTime_ms = 20

        self.isActivate = False
        self.touchTime = 0
        self.lostTime = 0
        self.holdTime = 0
        self.progress = 0

        self.lastUpdateTimestamp = time() * 1000

        self.eventList = []

    def loadData(self, gestureType):
        self.eventList = []

        nowTime = time() * 1000
        dt = nowTime - self.lastUpdateTimestamp
        self.lastUpdateTimestamp = nowTime

        if gestureType == self.listenType:
            if self.isActivate:
                self.holdTime += dt
                if self.holdTime >= self.targetTime_ms:
                    self.eventList.append(HoldingFinish())
                    self.progress = 0
                    self.holdTime = 0
                    self.isActivate = False
                else:
                    self.progress = self.holdTime / self.targetTime_ms
                    self.eventList.append(Holding(self.progress, self.holdTime))
            else:
                self.touchTime += dt
                if self.touchTime >= self.activateFilterTime_ms:
                    self.eventList.append(HoldingStart())
                    self.holdTime = 0
                    self.touchTime = 0
                    self.isActivate = True
        else:
            if self.isActivate:
                self.lostTime += dt
                if self.lostTime >= self.releaseFilterTime_ms:
                    self.eventList.append(HoldingCancel())
                    self.holdTime = 0
                    self.lostTime = 0
                    self.isActivate = False
                else:
                    self.touchTime = 0
            else:
                self.touchTime = 0

    def update(self) -> list:
        return self.eventList


class InfiniteHoldingEventsListener(EventListener):
    def __init__(self, listenType):
        self.listenType = listenType

        self.activateFilterTime_ms = 200
        self.releaseFilterTime_ms = 200

        self.isActivate = False
        self.touchTime = 0
        self.lostTime = 0
        self.holdTime = 0

        self.lastUpdateTimestamp = time() * 1000

        self.eventList = []

    def loadData(self, gestureType):
        self.eventList = []

        nowTime = time() * 1000
        dt = nowTime - self.lastUpdateTimestamp
        self.lastUpdateTimestamp = nowTime

        if gestureType == self.listenType:
            if self.isActivate:
                self.holdTime += dt
                self.eventList.append(Holding(0, self.holdTime))
            else:
                self.touchTime += dt
                if self.touchTime >= self.activateFilterTime_ms:
                    self.eventList.append(HoldingStart())
                    self.holdTime = 0
                    self.touchTime = 0
                    self.isActivate = True
        else:
            if self.isActivate:
                self.lostTime += dt
                if self.lostTime >= self.releaseFilterTime_ms:
                    self.eventList.append(HoldingFinish_infinite(self.holdTime))
                    self.holdTime = 0
                    self.lostTime = 0
                    self.isActivate = False
                else:
                    self.touchTime = 0
            else:
                self.touchTime = 0

    def update(self) -> list:
        return self.eventList
