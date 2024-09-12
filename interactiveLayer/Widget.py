from PIL import Image, ImageDraw
from interactiveLayer.Event import *


class WIDGET:
    def update(self, eventList: list):
        pass


class RectangleButton(WIDGET):
    def __init__(self, interface, tab=None, pos=(0, 0), size=None, text: str = '', radius: int = 0,
                 fillColor=(255, 255, 255, 150), bdThickness: int = 1, bdColor=(255, 255, 255, 255),
                 command=lambda: None):
        self.interface = interface
        self.interface.registerWidget(self, tab=tab)
        self.enable = False

        self.pos = pos
        if size is None:
            size = (int(self.interface.resolution[0] / 20), int(self.interface.resolution[1] / 20))
        self.size = size
        self.radius = radius
        self.text = text
        self.fillColor = fillColor
        self.bdThickness = bdThickness
        self.bdColor = bdColor

        halfScaleFactor1 = 0.05
        self.pos1 = (pos[0]-int(size[0]*halfScaleFactor1), pos[1]-int(size[1]*halfScaleFactor1))
        self.size1 = (size[0]+2*int(size[0]*halfScaleFactor1), size[1]+2*int(size[1]*halfScaleFactor1))
        self.radius1 = radius+2*int(radius*halfScaleFactor1)
        self.text1 = text
        self.fillColor1 = (50, 100, 220, 150)
        self.bdThickness1 = bdThickness
        self.bdColor1 = bdColor

        halfScaleFactor2 = -0.03
        self.pos2 = (pos[0]-int(size[0]*halfScaleFactor2), pos[1]-int(size[1]*halfScaleFactor2))
        self.size2 = (size[0]+2*int(size[0]*halfScaleFactor2), size[1]+2*int(size[1]*halfScaleFactor2))
        self.radius2 = radius+2*int(radius*halfScaleFactor2)
        self.text2 = text
        self.fillColor2 = (150, 150, 150, 240)
        self.bdThickness2 = bdThickness
        self.bdColor2 = bdColor

        self.status = 0
        self.lastStatus = 0
        self.command = command

        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))

    def draw(self):
        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(self.img)

        if self.enable:
            if self.status == 0:
                draw.rounded_rectangle(xy=(self.pos[0], self.pos[1], self.pos[0]+self.size[0], self.pos[1]+self.size[1]),
                                       radius=self.radius,
                                       fill=self.fillColor,
                                       outline=self.bdColor,
                                       width=self.bdThickness)
            elif self.status == 1:
                draw.rounded_rectangle(xy=(self.pos1[0], self.pos1[1], self.pos1[0]+self.size1[0], self.pos1[1]+self.size1[1]),
                                       radius=self.radius1,
                                       fill=self.fillColor1,
                                       outline=self.bdColor1,
                                       width=self.bdThickness1)
            elif self.status == 2:
                draw.rounded_rectangle(xy=(self.pos2[0], self.pos2[1], self.pos2[0]+self.size2[0], self.pos2[1]+self.size2[1]),
                                       radius=self.radius2,
                                       fill=self.fillColor2,
                                       outline=self.bdColor2,
                                       width=self.bdThickness2)

    def update(self, eventList: list) -> Image.Image:
        if self.enable:
            self.lastStatus = self.status
            self.status = 0
            for event in eventList:
                if type(event) in (Tap, TapStart, TapEnd, Suspending):
                    # print(event.position)
                    if min(self.pos[0], self.pos[0]+self.size[0]) <= event.position[0] <= max(self.pos[0], self.pos[0]+self.size[0]) and min(self.pos[1], self.pos[1] + self.size[1]) <= event.position[1] <= max(self.pos[1], self.pos[1] + self.size[1]):
                        if type(event) == Suspending:
                            self.status = 1
                        elif type(event) == TapEnd:
                            self.status = 1
                            if self.lastStatus == 2:
                                self.command()
                        else:
                            self.status = 2

            # print(self.status)
        self.draw()

        return self.img


class ImageLabel(WIDGET):
    def __init__(self, interface, imgBox=None, tab: list = None):
        self.interface = interface
        self.interface.registerWidget(self, tab=tab)
        self.enable = False

        self.inputImg = None

        if imgBox is None:
            self.imgBox = (0, 0, *self.interface.resolution)
        else:
            self.imgBox = imgBox

        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))

    def loadImageArray(self, imgArray, mode=None, Alpha=None):
        self.inputImg = Image.fromarray(imgArray, mode=mode)
        # self.inputImg = self.inputImg.draft('RGBA', self.inputImg.size)

    def draw(self):
        self.img = Image.new('RGBA', self.interface.resolution, (0, 0, 0, 0))

        if self.enable:
            self.img.paste(self.inputImg, self.imgBox)

        # self.interface.canvas.img = Image.alpha_composite(self.interface.canvas.img, img)

    def update(self, eventList: list) -> Image.Image:
        if self.enable:
            pass
        self.draw()
        return self.img
