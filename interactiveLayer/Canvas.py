from PIL import Image, ImageTk, ImageDraw
import tkinter as tk

class Canvas:
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
        # for control in self.controls:
        #     control.update()

        self.img_tk = ImageTk.PhotoImage(image=self.img)
        self.label_img['image'] = self.img_tk
        self.label_img.image = self.img_tk
        self.window.update()

        self.drawBG()
