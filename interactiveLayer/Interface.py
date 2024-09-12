from PIL import Image
from interactiveLayer.Canvas import Canvas
from interactiveLayer.Controller import Cursor, HoldingDetector
from interactiveLayer.Widget import ImageLabel


class Interface:
    def __init__(self, interfaceResolution=(640, 480), interfaceBG_color=(0, 0, 255, 255)):
        self.resolution = interfaceResolution
        self.canvas = Canvas(interfaceResolution, interfaceBG_color)
        # self.img = self.canvas.img
        # self.cursor = Cursor(self.canvas)

        self.controllerList = []
        self.widgetList = []

        self.eventList = []
        self.controllerImgList = []
        self.widgetImgList = []

        self.isActivating = False

    def registerController(self, controllerObject, tab: list = None):
        if tab is None:
            tab = []
        # print(f'register {controllerObject}')
        self.controllerList.append([controllerObject, tab])
        # self.canvas.registerController(controlObject=controllerObject)

    def registerWidget(self, widgetObject, tab: list = None):
        if tab is None:
            tab = []
        self.widgetList.append([widgetObject, tab])

    def setVisibility(self, visibility: bool, exceptions: list = None, exceptionTabs: list = None):
        """
        set enable of all controllers and widgets that are not in exceptions or have a tab in exceptionTabs to visibility.

        :param visibility:
        :param exceptions:
        :param exceptionTabs:
        :return:
        """
        # print(self.controllerList, self.widgetList)
        if exceptions is None:
            exceptions = []
        if exceptionTabs is None:
            exceptionTabs = []

        for controller, tab in self.controllerList:
            if controller not in exceptions and len([t for t in exceptionTabs if t in tab]) == 0:
                controller.enable = visibility
        for widget, tab in self.widgetList:
            # print(widget, tab)
            if widget not in exceptions and len([t for t in exceptionTabs if t in tab]) == 0:
                widget.enable = visibility

    def sleep(self):
        """
        set all controllers and widgets enable False,
        turn on activate checker.

        :return:
        """
        self.setVisibility(True)
        self.setVisibility(False, exceptionTabs=['activateChecker', 'keepWhileSleep'])
        self.isActivating = False

    def activate(self):
        """
        set controllers and widgets enable True, except activate checker.

        :return:
        """
        self.setVisibility(False)
        self.setVisibility(True, exceptionTabs=['activateChecker'])
        self.isActivating = True

    def update(self):
        """
        call update function in all controllers and widgets registered,
        compose graphic returned by each controller and widget to final image,
        update canvas to display new image.

        :return:
        """
        for controller, tab in self.controllerList:
            # print(controller)
            eventList, img = controller.update()
            self.eventList += eventList
            self.controllerImgList.append(img)
        for widget, tab in self.widgetList:
            # print(widget)
            self.widgetImgList.append(widget.update(self.eventList))

        for img in self.widgetImgList:
            self.canvas.img = Image.alpha_composite(self.canvas.img, img)
        for img in self.controllerImgList:
            self.canvas.img = Image.alpha_composite(self.canvas.img, img)

        self.canvas.update()
        self.eventList = []
        self.controllerImgList = []
        self.widgetImgList = []
