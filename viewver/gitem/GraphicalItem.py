import tkinter as tk
from tkinter import ttk
import sys
import pathlib
_parentdir = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_parentdir))

from viewver.config.Config import *

class GraphicalItem():
    def __init__(self):
        self.x = 0
        self.y = 0

    def moveTo(self, x, y):
        """Move the component"""
        self.x = x
        self.y = y

    def draw(self, canvas, camera):
        """Draw the item on the canvas"""
        canvas.create_rectangle(camera.convert4D(50, 50, 200, 150), fill="blue", outline="black", width=2)

    def isSelected(self, x, y):
        """Check if the component is selected at the coordinate x,y. If yes, return the hitbox, else return False"""
    
    def getHitbox(self):
        """Return the hitbox of the component"""

    def getPos(self):
        """Return the component position"""
        return self.x, self.y

class Component(GraphicalItem):
    def __init__(self, name, inputNets, outputNets):
        super().__init__()
        """Input nets on the right, output on the left"""
        self.inputNets = inputNets
        self.outputNets = outputNets
        self.name = name
        self.fill = "white"
        self.outline = "black"
        self.linew = 2

        self.h = COMPONENT_TEXT_MARGIN*(max(len(inputNets), len(outputNets))+1) # heigth of the box
        self.w = 3*COMPONENT_TEXT_MARGIN + COMPONENT_TEXT_WIDTH*(max([len(net.value) for net in inputNets]) + max([len(net.value) for net in outputNets])) # width of the box

    def draw(self, canvas, camera):
        """Draw the item on the canvas"""
        canvas.create_rectangle(camera.convert4D(self.x, self.y, self.x+self.w, self.y+self.h), fill=self.fill, outline=self.outline, width=self.linew)
        # Draw input nets
        for i in range(len(self.inputNets)):
            ylabel = (self.h/(len(self.inputNets)+1))*(i+1)
            canvas.create_text(*camera.convert2D(self.x+COMPONENT_TEXT_MARGIN, self.y + ylabel), 
                               text=self.inputNets[i].value, 
                               font=("Consolas", int(COMPONENT_TEXT_HEIGHT*camera.zoom), tk.NORMAL),
                               anchor="w")
            canvas.create_rectangle(camera.convert4D(self.x-NET_PIN_HSIZE, self.y + ylabel-NET_PIN_HSIZE, self.x+NET_PIN_HSIZE, self.y + ylabel+NET_PIN_HSIZE), fill=self.fill, outline=self.outline, width=self.linew)
        
        # Draw output nets
        for i in range(len(self.outputNets)):
            ylabel = (self.h/(len(self.outputNets)+1))*(i+1)
            canvas.create_text(*camera.convert2D(self.x+self.w-COMPONENT_TEXT_MARGIN, self.y + ylabel), 
                               text=self.outputNets[i].value, 
                               font=("Consolas", int(COMPONENT_TEXT_HEIGHT*camera.zoom), tk.NORMAL),
                               anchor="e")
            canvas.create_rectangle(camera.convert4D(self.x+self.w-NET_PIN_HSIZE, self.y + ylabel-NET_PIN_HSIZE, self.x+self.w+NET_PIN_HSIZE, self.y + ylabel+NET_PIN_HSIZE), fill=self.fill, outline=self.outline, width=self.linew)
        # Add name
        canvas.create_text(*camera.convert2D(self.x+self.w/2, self.y-COMPONENT_TEXT_MARGIN), 
                               text=self.name, 
                               font=("Consolas", int(COMPONENT_TEXT_HEIGHT*camera.zoom), tk.NORMAL),
                               anchor="center")
        
    def isSelected(self, x, y):
        """Check if the component is selected at the coordinate x,y. If yes, return the hitbox, else return False"""
        if (x > self.x) and (x < self.x + self.w) and (y > self.y) and (y < self.y + self.h):
            return self.getHitbox()
        return False

    def getHitbox(self):
        """Return the hitbox of the component: x0,y0, x1,y1"""
        return [self.x, self.y, self.x + self.w, self.y + self.h]
