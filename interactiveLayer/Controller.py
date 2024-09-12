from typing import Tuple
import numpy as np

from PIL import Image, ImageDraw

from interactiveLayer.EventListener import FiniteHoldingEventsListener
from interactiveLayer.EventListener import InfiniteHoldingEventsListener
from interactiveLayer.EventListener import CursorEventsListener
from interactiveLayer.Event import *
from translationLayer import PerspectiveMapping


class CONTROLLER:
    def update(self) -> list:
        return []


class HoldingDetector(CONTROLLER):
    def __init__(self, interface, listenType, tab: list = None, activeTime_ms=1000, command=None):
        self.interface = interface
        self.interface.registerController(self, tab)
        self.enable = False

        self.eventListener = FiniteHoldingEventsListener(listenType=listenType, targetTime_ms=activeTime_ms)
        self.eventList = []
        self.command = command

        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))

    def loadData(self, gestureType):
        self.eventListener.loadData(gestureType)

    def draw(self):
        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.img)

        if self.enable:
            for event in self.eventList:
                if type(event) == Holding:
                    draw.line([(0, 0), (self.interface.resolution[0] * event.progress, 0)], (0, 80, 230, 255), 20)

        # self.interface.canvas.img = Image.alpha_composite(self.interface.canvas.img, img)

    def update(self) -> Tuple[list, Image.Image]:
        if self.enable:
            self.eventList = self.eventListener.update()

            self.draw()

            if HoldingFinish in map(lambda x: type(x), self.eventList):
                self.command()

        # print(self.eventList)
        return self.eventList, self.img


class Cursor(CONTROLLER):
    def __init__(self, interface, style=None, tab: list = None):
        self.interface = interface
        self.interface.registerController(self, tab)
        self.enable = False

        # self.perspectiveMap = PerspectiveMapping((0, 0),
        #                                          (self.interface.resolution[0], 0),
        #                                          (0, self.interface.resolution[1]),
        #                                          (self.interface.resolution[0], self.interface.resolution[1]))

        self.pos1 = (0, 0)
        self.pos2 = (0, 0)
        self.cursorPos = (0, 0)
        self.eventListener = CursorEventsListener()
        self.eventList = []

        self.isMapAvailable = True
        self.eventListener.releaseFilterTime_ms = 400
        self.rangeEdgePos = []
        self.perspectiveMap = PerspectiveMapping((585, 310), (880, 295), (445, 550), (930, 450))

        if style is None:
            self.style = [{'fill': (255, 255, 255, 50), 'outlineColor': (255, 255, 255, 150), 'outlineWidth': 2,
                           'r': int(min(self.interface.resolution) / 75)},
                          {'fill': (255, 255, 255, 50), 'outlineColor': (255, 255, 255, 150), 'outlineWidth': 2,
                           'r': int(min(self.interface.resolution) / 75)},
                          {'fill': (255, 255, 255, 150), 'outlineColor': None, 'outlineWidth': 0,
                           'r': int(min(self.interface.resolution) / 100)},
                          {'lineColor': (255, 255, 255, 150), 'lineWidth': 2},
                          {'fill': (255, 20, 0, 150), 'outlineColor': None, 'outlineWidth': 0,
                           'r': int(min(self.interface.resolution) / 100)},
                          {'arcColor': (255, 255, 255, 150), 'width': 4, 'r': int(min(self.interface.resolution) / 50)},
                          {'fill': (255, 255, 255, 100), 'outlineColor': (255, 255, 255, 150), 'outlineWidth': 1,
                           'r': int(min(self.interface.resolution) / 45)},
                          {'fill': (0, 0, 255, 150), 'outlineColor': (255, 255, 255, 150), 'outlineWidth': 1,
                           'r': int(min(self.interface.resolution) / 70)}
                          ]
        else:
            self.style = style

        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))

    def clearMap(self):
        self.isMapAvailable = False
        self.eventListener.releaseFilterTime_ms = 400
        self.interface.setVisibility(False, [self])

    def loadData(self, pos1, pos2, gestureType):
        self.pos1 = pos1
        self.pos2 = pos2
        self.cursorPos = (int((pos1[0] + pos2[0]) / 2), int((pos1[1] + pos2[1]) / 2))
        if self.isMapAvailable:
            self.cursorPos = self.mapCursorPos(self.cursorPos)
            self.pos1, self.pos2 = self.mapFingerPos(self.pos1, self.pos2)
        self.eventListener.loadData(self.cursorPos, gestureType)

    def mapCursorPos(self, pos):
        # print(pos)
        pos = self.perspectiveMap.remap(pos)
        w, h = self.interface.resolution

        px = pos[0] * w
        py = pos[1] * h

        # print(px, py)
        # print()
        return px, py

    def mapFingerPos(self, pos1, pos2):
        dx = int((pos1[0] - pos2[0]) / 2)
        dy = int((pos1[1] - pos2[1]) / 2)
        pos1x = self.cursorPos[0] + dx
        pos1y = self.cursorPos[1] + dy
        pos2x = self.cursorPos[0] - dx
        pos2y = self.cursorPos[1] - dy
        return (pos1x, pos1y), (pos2x, pos2y)

    def draw(self):
        r1 = self.style[0]['r']
        r2 = self.style[1]['r']
        r3 = self.style[2]['r']
        r4 = self.style[4]['r']
        r5 = self.style[5]['r']
        r6 = self.style[6]['r']
        r7 = self.style[7]['r']

        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.img)

        draw.line([self.pos1, self.pos2], fill=self.style[3]['lineColor'], width=self.style[3]['lineWidth'])
        draw.ellipse(xy=(self.pos1[0] - r1, self.pos1[1] - r1, self.pos1[0] + r1, self.pos1[1] + r1),
                     fill=self.style[0]['fill'],
                     outline=self.style[0]['outlineColor'],
                     width=self.style[0]['outlineWidth'])
        draw.ellipse(xy=(self.pos2[0] - r2, self.pos2[1] - r2, self.pos2[0] + r2, self.pos2[1] + r2),
                     fill=self.style[1]['fill'],
                     outline=self.style[1]['outlineColor'],
                     width=self.style[1]['outlineWidth'])
        # print(self.eventList)
        for event in self.eventList:
            if type(event) in [TapStart, Tap, TapEnd]:
                draw.ellipse(
                    xy=(self.cursorPos[0] - r4, self.cursorPos[1] - r4, self.cursorPos[0] + r4, self.cursorPos[1] + r4),
                    fill=self.style[4]['fill'],
                    outline=self.style[4]['outlineColor'],
                    width=self.style[4]['outlineWidth'])
            elif type(event) in [PressStart, Press, PressEnd]:
                draw.ellipse(
                    xy=(self.cursorPos[0] - r6, self.cursorPos[1] - r6, self.cursorPos[0] + r6, self.cursorPos[1] + r6),
                    fill=self.style[6]['fill'],
                    outline=self.style[6]['outlineColor'],
                    width=self.style[6]['outlineWidth'])
            elif type(event) in [DraggingStart, Dragging, DraggingEnd]:
                draw.ellipse(
                    xy=(self.cursorPos[0] - r7, self.cursorPos[1] - r7, self.cursorPos[0] + r7, self.cursorPos[1] + r7),
                    fill=self.style[7]['fill'],
                    outline=self.style[7]['outlineColor'],
                    width=self.style[7]['outlineWidth'])
            else:
                draw.ellipse(
                    xy=(self.cursorPos[0] - r3, self.cursorPos[1] - r3, self.cursorPos[0] + r3, self.cursorPos[1] + r3),
                    fill=self.style[2]['fill'],
                    outline=self.style[2]['outlineColor'],
                    width=self.style[2]['outlineWidth'])
                if type(event) == PressWaiting:
                    # print(f'pressWaiting {event.progress}')
                    draw.arc(xy=(
                        self.cursorPos[0] - r5, self.cursorPos[1] - r5, self.cursorPos[0] + r5, self.cursorPos[1] + r5),
                        start=0,
                        end=int(event.progress * 360),
                        fill=self.style[5]['arcColor'],
                        width=self.style[5]['width'])

        # self.interface.canvas.img = Image.alpha_composite(self.interface.canvas.img, img)
        # draw.rectangle((0, 0, self.interface.resolution[0]-1, self.interface.resolution[1]-1), (0, 0, 0, 0))

        # if pos[0] == 200:
        #     img.show()

    def update(self) -> Tuple[list, Image.Image]:
        if self.enable:
            self.eventList = self.eventListener.update()
            # print(self.eventList)
            if self.isMapAvailable:
                self.draw()
        # print(self.eventList)
        if self.isMapAvailable:
            return self.eventList, self.img
        else:
            for event in self.eventList:
                if type(event) in (Dragging, DraggingStart):
                    self.rangeEdgePos.append(event.absolutePos)
                    print(f'added {event.absolutePos}')
                elif type(event) == DraggingEnd:
                    # print(self.rangeEdgePos)
                    # print(np.array(self.rangeEdgePos).T)
                    xs, ys = np.array(self.rangeEdgePos).T
                    print(xs, ys)
                    self.perspectiveMap.loadRangeEdgePos(xs, ys)

                    self.isMapAvailable = True
                    self.eventListener.releaseFilterTime_ms = 20
                    self.rangeEdgePos = []
                    self.interface.setVisibility(True, exceptionTabs=['activateChecker'])
            return [], Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))


class FixedLengthNumInput:
    def __init__(self, interface, length, answer: list = None, tab: list = None, command=None):
        self.interface = interface
        self.interface.registerController(self, tab)
        self.enable = False

        self.length = length
        self.answer = answer
        if answer is not None:
            self.length = len(answer)
        self.command = command

        self.NumListeners = []
        for listenType in range(10):
            self.NumListeners.append(InfiniteHoldingEventsListener(listenType=listenType))
        self.isHolding = True
        self.inputs = []
        self.eventList = []

        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        self.style = [{'fillColor': (0, 30, 200, 255), 'gapLength': 3, 'lineWidth': 20},
                      {'fillColor': (0, 60, 255, 255), 'gapLength': 3, 'lineWidth': 20}]

    def loadData(self, gestureType):
        for listener in self.NumListeners:
            listener.loadData(gestureType=gestureType)

    def draw(self):
        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.img)

        if self.enable:
            blockLength = int(self.interface.resolution[0] / self.length)
            inputLength = len(self.inputs)
            for i in range(inputLength):
                draw.line([(i * blockLength + self.style[0]['gapLength'], 0),
                           ((i + 1) * blockLength - self.style[0]['gapLength'], 0)],
                          self.style[0]['fillColor'], self.style[0]['lineWidth'])
            if self.isHolding:
                draw.line([(inputLength * blockLength + self.style[1]['gapLength'], 0),
                           ((inputLength + 1) * blockLength - self.style[1]['gapLength'], 0)],
                          self.style[1]['fillColor'], self.style[1]['lineWidth'])

    def update(self) -> Tuple[list, Image.Image]:
        if self.enable:
            for listenType, listener in enumerate(self.NumListeners):
                events = list(map(type, listener.update()))
                # print(list(events))

                # if Holding in events:
                #     self.isHolding = True

                if HoldingStart in events:
                    # print(listenType)
                    self.inputs.append(listenType)
                    if len(self.inputs) >= self.length:
                        self.inputs = self.inputs[:self.length]

                        # if answer and command exists, execute command
                        if self.answer is not None and self.command is not None:
                            # print(self.inputs, self.answer)
                            if self.inputs == list(self.answer):
                                # print('do command...')
                                self.command()
                                self.inputs = []
                                break
                            # if answer not correct, clean answer and listen again
                            else:
                                self.inputs = []

                        return [FixedLengthNumInput_event(self.inputs)], self.img

            # print(self.enable)
            self.draw()
            print(self.inputs)
            return [], self.img

        # print(self.eventList)
        return [], self.img


class FixedLengthNumListener:
    def __init__(self, interface, length, answer: list, tab: list = None, command=None):
        self.interface = interface
        self.interface.registerController(self, tab)
        self.enable = False

        self.length = length
        self.answer = answer
        if answer is not None:
            self.length = len(answer)
        self.command = command

        self.NumListeners = []
        for listenType in range(10):
            self.NumListeners.append(InfiniteHoldingEventsListener(listenType=listenType))
        self.isHolding = True
        self.inputs = []
        self.eventList = []

        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        self.style = [{'fillColor': (0, 30, 200, 255), 'gapLength': 3, 'lineWidth': 20},
                      {'fillColor': (0, 60, 255, 255), 'gapLength': 3, 'lineWidth': 20}]

    def loadData(self, gestureType):
        for listener in self.NumListeners:
            listener.loadData(gestureType=gestureType)

    def draw(self):
        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.img)

        if self.enable:
            blockLength = int(self.interface.resolution[0] / self.length)
            inputLength = len(self.inputs)
            for i in range(inputLength):
                draw.line([(i * blockLength + self.style[0]['gapLength'], 0),
                           ((i + 1) * blockLength - self.style[0]['gapLength'], 0)],
                          self.style[0]['fillColor'], self.style[0]['lineWidth'])
            if self.isHolding:
                draw.line([(inputLength * blockLength + self.style[1]['gapLength'], 0),
                           ((inputLength + 1) * blockLength - self.style[1]['gapLength'], 0)],
                          self.style[1]['fillColor'], self.style[1]['lineWidth'])

    def update(self) -> Tuple[list, Image.Image]:
        if self.enable:
            for listenType, listener in enumerate(self.NumListeners):
                events = list(map(type, listener.update()))
                # print(list(events))

                # if Holding in events:
                #     self.isHolding = True

                if HoldingStart in events:
                    # print(listenType)
                    self.inputs.append(listenType)
                    if len(self.inputs) >= self.length:
                        self.inputs = self.inputs[:self.length]

                        # if answer and command exists, execute command
                        if self.command is not None:
                            # print(self.inputs, self.answer)
                            if self.inputs == list(self.answer):
                                # print('do command...')
                                self.command()
                                self.inputs = []
                                break
                            # if answer not correct, clean answer and listen again
                            else:
                                self.inputs = []

                    # print(self.inputs, self.answer[:len(self.inputs)])
                    if self.inputs != self.answer[:len(self.inputs)]:
                        self.inputs = []

                    return [FixedLengthNumInput_event(self.inputs)], self.img

            # print(self.enable)
            self.draw()
            # print(self.inputs)
            return [], self.img

        # print(self.eventList)
        return [], self.img
