import tkinter as tk
from tkinter import ttk
import numpy as np
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
    
    def getSaveDic(self):
        """Return the save dictionnary of this component"""
        return {'pos': [self.x, self.y]}
    
    def updateFromSave(self, save):
        """Update a component from information in a save file"""
        self.x, self.y = save['pos']

    def drawHighlight(self, canvas, camera):
        """draw the Highligth this component (if selected for instance)"""


class GraphicalNet(GraphicalItem):
    def __init__(self, name, components):
        super().__init__()
        """Represent a net"""
        self.components = components
        self.name = name
        self.fill = "purple"
        self.linew = 1
        self.updateLines()

    def getName(self):
        """Return the name of this component"""
        return self.name

    def updateLines(self):
        self.pts = []
        self.terminals = []
        for c in self.components:
            self.pts.append(c.getNet2D(self.name))
            self.terminals.append(c.getNetTerminal4D(self.name))

    def draw(self, canvas, camera):
        """Draw the item on the canvas"""
        self.updateLines()
        for i in range(1, len(self.pts)):
            canvas.create_line(camera.convert4D(*self.pts[i-1], *self.pts[i]), fill=self.fill, width=self.linew)

    def isSelected(self, x, y):
        """Check if the component is selected at the coordinate x,y. If yes, return the hitbox, else return False"""
        if False:
            # Check for line hover
            M = np.array([x, y])
            for i in range(1, len(self.pts)):
                A = np.array(self.pts[i-1])
                B = np.array(self.pts[i])
                
                if (np.linalg.norm(A-M) + np.linalg.norm(B-M) - np.linalg.norm(A-B) < HITBOX_LINE):
                    return True
        # Check for teminal hover
        for t4d in self.terminals:
            if (t4d[0] < x) and (t4d[2] > x) and (t4d[1] < y) and (t4d[3] > y):
                return True
        return False
    
    def drawHighlight(self, canvas, camera):
        """draw the Highligth this component (if selected for instance)"""
        oldw = self.linew
        self.linew = 4
        self.draw(canvas, camera)
        # Then draw the terminals
        for t4d in self.terminals:
            canvas.create_rectangle(camera.convert4D(*t4d), fill="white", outline=self.fill, width=self.linew)
        
        self.linew = oldw


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
        self.w = 3*COMPONENT_TEXT_MARGIN + COMPONENT_TEXT_WIDTH*(max([len(net) for net in inputNets] + [0]) + max([len(net) for net in outputNets] + [0])) # width of the box

    def getName(self):
        """Return the name of the component"""
        return self.name

    def getNet2D(self, name):
        """Return the 2D position of the net name"""

        for i in range(len(self.inputNets)):
            ylabel = (self.h/(len(self.inputNets)+1))*(i+1)
            if (name == self.inputNets[i]):
                return self.x, self.y+ylabel
            
        for i in range(len(self.outputNets)):
            ylabel = (self.h/(len(self.outputNets)+1))*(i+1)
            if (name == self.outputNets[i]):
                return self.x + self.w, self.y+ylabel
        return None
    
    def getNetTerminal4D(self, name):
        """Return the 4D position of a net terminal"""
        pos = self.getNet2D(name)
        if pos == None:
            return None
        return [pos[0] - NET_PIN_HSIZE,
                pos[1] - NET_PIN_HSIZE,
                pos[0] + NET_PIN_HSIZE,
                pos[1] + NET_PIN_HSIZE,]

    def draw(self, canvas, camera):
        """Draw the item on the canvas"""
        canvas.create_rectangle(camera.convert4D(self.x, self.y, self.x+self.w, self.y+self.h), fill=self.fill, outline=self.outline, width=self.linew)
        # Draw input nets
        for i in range(len(self.inputNets)):
            ylabel = (self.h/(len(self.inputNets)+1))*(i+1)
            canvas.create_text(*camera.convert2D(self.x+COMPONENT_TEXT_MARGIN, self.y + ylabel), 
                               text=self.inputNets[i], 
                               font=("Consolas", int(COMPONENT_TEXT_HEIGHT*camera.zoom), tk.NORMAL),
                               anchor="w")
            canvas.create_rectangle(camera.convert4D(self.x-NET_PIN_HSIZE, self.y + ylabel-NET_PIN_HSIZE, self.x+NET_PIN_HSIZE, self.y + ylabel+NET_PIN_HSIZE), fill=self.fill, outline=self.outline, width=self.linew)
        
        # Draw output nets
        for i in range(len(self.outputNets)):
            ylabel = (self.h/(len(self.outputNets)+1))*(i+1)
            canvas.create_text(*camera.convert2D(self.x+self.w-COMPONENT_TEXT_MARGIN, self.y + ylabel), 
                               text=self.outputNets[i], 
                               font=("Consolas", int(COMPONENT_TEXT_HEIGHT*camera.zoom), tk.NORMAL),
                               anchor="e")
            canvas.create_rectangle(camera.convert4D(self.x+self.w-NET_PIN_HSIZE, self.y + ylabel-NET_PIN_HSIZE, self.x+self.w+NET_PIN_HSIZE, self.y + ylabel+NET_PIN_HSIZE), fill=self.fill, outline=self.outline, width=self.linew)
        # Add name
        canvas.create_text(*camera.convert2D(self.x+self.w/2, self.y-COMPONENT_TEXT_MARGIN), 
                               text=self.name, 
                               font=("Consolas", int(COMPONENT_TEXT_HEIGHT*camera.zoom), tk.NORMAL),
                               anchor="center")
        
    def isSelected(self, x, y):
        """Check if the component is selected at the coordinate x,y."""
        if (x > self.x) and (x < self.x + self.w) and (y > self.y) and (y < self.y + self.h):
            return True
        return False
    
    def drawHighlight(self, canvas, camera):
        """draw the Highligth this component (if selected for instance)"""
        canvas.create_rectangle(camera.convert4D(*self.getHitbox()), outline="blue", width=3)

    def getHitbox(self):
        """Return the hitbox of the component: x0,y0, x1,y1"""
        return [self.x, self.y, self.x + self.w, self.y + self.h]
    
    def updateFromSave(self, save):
        """Update a component from information in a save file"""
        super().updateFromSave(save)

    def initFromSave(save):
        """return a Component object from a saving dictionnary"""
        1/0

    def getSaveDic(self):
        save = super().getSaveDic()
        save['name'] = self.name
        return save
        
