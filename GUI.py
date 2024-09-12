import cv2 as cv
from PIL import Image, ImageDraw, ImageFont, ImageTk
import numpy as np
import tkinter as tk
import time


class CANVAS:
    # img_tk = None

    def __init__(self, resolution, bgcolor):
        self.resolution = resolution
        self.bgcolor = bgcolor

        self.img = None
        self.draw = None
        self.drawBG()

        self.window = tk.Tk()
        self.window.title('GUI')
        self.window.geometry(f'{resolution[0]}x{resolution[1]}')
        # self.window.configure(bg='red')

        self.img_tk = ImageTk.PhotoImage(image=self.img)
        self.label_img = tk.Label(master=self.window, image=self.img_tk)
        self.label_img.pack()

        self.controls = []

    def registerController(self, controlObject):
        self.controls.append(controlObject)

    def drawBG(self):
        # self.draw.rectangle((0, 0, self.resolution[0]-1, self.resolution[1]-1), fill=self.bgcolor)

        self.img = Image.new('RGBA', self.resolution, self.bgcolor)
        self.draw = ImageDraw.Draw(self.img)

    def update(self):
        for control in self.controls:
            control.update()

        self.img_tk = ImageTk.PhotoImage(image=self.img)
        self.label_img['image'] = self.img_tk
        self.label_img.image = self.img_tk
        self.window.update()

        self.drawBG()


class EVENTlISTENER:
    pass


class EVENT:
    pass


class CONTROLLER:
    def update(self):
        pass


class HOLDINGdETECTOR(CONTROLLER):
    def __init__(self, interface, listenType=None, activeTime_ms=3000, command=None):
        self.interface = interface
        self.interface.registerController(self)

        self.listenType = listenType
        self.activeTime_ms = activeTime_ms
        self.command = command

        self.holdTime = False
        self.progress = 0

        self.lastUpdateTimestamp = time.time()

    def loadType(self, gestureType):
        nowTime = time.time()
        if gestureType == self.listenType:
            self.holdTime += nowTime - self.lastUpdateTimestamp
        else:
            self.holdTime = 0
        self.lastUpdateTimestamp = nowTime

    def draw(self):
        img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.line([(0, 0), (self.interface.resolution[0]*self.progress, 0)], (0, 100, 255, 255), 10)

        self.interface.img = Image.alpha_composite(self.interface.img, img)

    def update(self):
        self.progress = (self.holdTime*1000)/self.activeTime_ms
        # print(self.holdTime)
        self.draw()
        if self.progress >= 1:
            self.progress = 0
            self.holdTime = 0
            self.command()


class CURSOR(CONTROLLER):
    def __init__(self, interface, style=None):
        self.interface = interface
        self.interface.registerController(self)

        self.pos1 = (0, 0)
        self.pos2 = (0, 0)
        self.cursorPos = (0, 0)

        if style is None:
            self.style = [{'fill': (255, 255, 255, 50), 'outlineColor': (255, 255, 255, 150), 'outlineWidth': 2, 'r': int(min(self.interface.resolution) / 75)},
                          {'fill': (255, 255, 255, 50), 'outlineColor': (255, 255, 255, 150), 'outlineWidth': 2, 'r': int(min(self.interface.resolution) / 75)},
                          {'fill': (255, 255, 255, 150), 'outlineColor': None, 'outlineWidth': 0, 'r': int(min(self.interface.resolution) / 100)},
                          {'lineColor': (255, 255, 255, 150), 'lineWidth': 2}]
        else:
            self.style = style

    def loadPos(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2
        self.cursorPos = (int((pos1[0]+pos2[0])/2), int((pos1[1]+pos2[1])/2))

    def mapCoordinate(self):
        pass

    def draw(self):
        r1 = self.style[0]['r']
        r2 = self.style[1]['r']
        r3 = self.style[2]['r']

        img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.line([self.pos1, self.pos2], fill=self.style[3]['lineColor'], width=self.style[3]['lineWidth'])
        draw.ellipse(xy=(self.pos1[0] - r1, self.pos1[1] - r1, self.pos1[0] + r1, self.pos1[1] + r1),
                     fill=self.style[0]['fill'],
                     outline=self.style[0]['outlineColor'],
                     width=self.style[0]['outlineWidth'])
        draw.ellipse(xy=(self.pos2[0] - r2, self.pos2[1] - r2, self.pos2[0] + r2, self.pos2[1] + r2),
                     fill=self.style[1]['fill'],
                     outline=self.style[1]['outlineColor'],
                     width=self.style[1]['outlineWidth'])
        draw.ellipse(xy=(self.cursorPos[0] - r3, self.cursorPos[1] - r3, self.cursorPos[0] + r3, self.cursorPos[1] + r3),
                     fill=self.style[2]['fill'],
                     outline=self.style[2]['outlineColor'],
                     width=self.style[2]['outlineWidth'])

        self.interface.img = Image.alpha_composite(self.interface.img, img)
        # draw.rectangle((0, 0, self.interface.resolution[0]-1, self.interface.resolution[1]-1), (0, 0, 0, 0))

        # if pos[0] == 200:
        #     img.show()

    def update(self):
        self.mapCoordinate()
        self.draw()


class BUTTON(CONTROLLER):
    def __init__(self, interface, pos, size, text, fillColor, bdThickness, bdColor):
        self.interface = interface
        self.interface.registerController(self)


class IMAGElABEL(CONTROLLER):
    def __init__(self, interface, imgBox=None):
        self.interface = interface
        self.interface.registerController(self)

        self.inputImg = None

        if imgBox is None:
            self.imgBox = (0, 0, *self.interface.resolution)
        else:
            self.imgBox = imgBox

    def loadImageArray(self, imgArray, mode=None, Alpha=None):
        self.inputImg = Image.fromarray(imgArray, mode=mode)
        # self.inputImg = self.inputImg.draft('RGBA', self.inputImg.size)

    def draw(self):
        img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        img.paste(self.inputImg, self.imgBox)

        self.interface.img = Image.alpha_composite(self.interface.img, img)

    def update(self):
        self.draw()


class INTERFACE:
    def __init__(self, interfaceResolution=(640, 480), interfaceBG_color=(0, 0, 255, 255)):
        self.canvas = CANVAS(interfaceResolution, interfaceBG_color)
        self.cursor = CURSOR(self.canvas)


if __name__ == '__main__':
    itf = CANVAS((640, 480), (0, 0, 255, 255))
    cur = CURSOR(itf)

    x, y = 50, 50
    while True:
        cur.loadPos((x, y), (x, y))
        cur.draw()
        itf.update()
        x += 1
        y += 1
        time.sleep(0.01)
