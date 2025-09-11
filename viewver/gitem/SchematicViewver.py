import tkinter as tk
from tkinter import ttk
import numpy as np

import sys
import pathlib
_parentdir = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_parentdir))

from viewver.config.Config import *
from viewver.gitem.GraphicalItem import *


class Camera():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1

    def zoomArround(self, x, y, zoomin):
        """Zoom around a point"""
        xlast, ylast = self.inverse2D(x, y) # get x,y from the camera world
        if zoomin > 0:
            self.zoom *= 1 + ZOOM_SPEED
        else:
            self.zoom *= 1 - ZOOM_SPEED
        xnew, ynew = self.inverse2D(x, y) # get x,y from the new camera world
        self.x += (xnew - xlast)
        self.y += (ynew - ylast)

    def convert2D(self, x, y):
        """Convert a 2D point from the normal space to the camera one"""
        return np.array([(x + self.x)*self.zoom, (y + self.y)*self.zoom])
    
    def inverse2D(self, x, y):
        """Convert a 2D point from the window to the absolute referential"""
        return x/self.zoom - self.x, y/self.zoom - self.y

    def convert4D(self, x0, y0, x1, y1):
        """Convert a 4D point from the normal space to the camera one"""
        return *self.convert2D(x0, y0), *self.convert2D(x1, y1)
    

class ShematicViewver(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.camera = Camera()
        self.gitem = set() # set of graphical items
        self.currentSelection = None

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind_all("<MouseWheel>", self.mouseWheel)
        self.canvas.bind("<B2-Motion>", self.mousePressedMiddleMove)
        self.canvas.bind("<B1-Motion>", self.mousePressedLeftMove)
        self.canvas.bind("<Motion>", self.mouseMove)
        self.canvas.bind("<Button-1>", self.mouseLeftDown)
        self.canvas.bind("<Button-2>", self.mouseMiddleDown)
        self.canvas.bind("<ButtonRelease-1>", self.mouseLeftUp)

    def add(self, b):
        assert isinstance(b, GraphicalItem), "b must be an graphical item"
        self.gitem.add(b)
        # Refresh
        self.redraw()

    def redraw(self):
        """Redraw the canvas"""
        self.canvas.delete("all")

        for gitem in self.gitem:
            gitem.draw(self.canvas, self.camera)
        
        if self.currentSelection != None:
            self.canvas.create_rectangle(self.camera.convert4D(*self.selectionHitbox), outline="blue", width=3)

    def mouseWheel(self, event):
        """Mouse wheel event (zoom)"""
        # Check if inside the canvas
        if (event.widget != self.canvas):
            return
        self.camera.zoomArround(event.x, event.y, event.delta > 0)
        self.redraw()

    def saveMouseStartingPos(self, event):
        """Save the mouse starting position"""
        self.cameraStartingPt = [-self.camera.x*self.camera.zoom + event.x, 
                                 -self.camera.y*self.camera.zoom + event.y]

    def mouseLeftDown(self, event):
        """Mouse left click down"""
        self.saveMouseStartingPos(event)
        if (self.currentSelection != None):
            # Sate the component orifinal position
            self.selectionOrigin = self.currentSelection.getPos()
        
    def mouseMiddleDown(self, event):
        """Mouse Middle click down"""
        self.saveMouseStartingPos(event)

    def mouseLeftUp(self, event):
        """Mouse left click up"""
        self.cameraStartingPt = None

    def mousePressedMiddleMove(self, event):
        """Mouse motion + Middle down"""
        if self.cameraStartingPt == None:
            return
        self.camera.x = (event.x - self.cameraStartingPt[0])/self.camera.zoom
        self.camera.y = (event.y - self.cameraStartingPt[1])/self.camera.zoom
        self.redraw()
        self.mouseMove(event)

    def mousePressedLeftMove(self, event):
        """Mouse motion + Left down"""
        # get the translation in the absolute referential
        xabs, yabs = self.camera.inverse2D(event.x - self.cameraStartingPt[0], event.y - self.cameraStartingPt[1])
        if (self.currentSelection != None):
            x0, y0 = self.selectionOrigin
            self.currentSelection.moveTo(xabs + x0, yabs + y0)
            # Update the hitbox
            self.selectionHitbox = self.currentSelection.getHitbox()
            self.redraw()

    def mouseMove(self, event):
        """Mouse motion"""
        # Get the mouse position in the absolute referential
        xmabs, ymabs = self.camera.inverse2D(event.x, event.y)
        for c in self.gitem:
            selection = c.isSelected(xmabs, ymabs)
            if selection != False:
                self.setSelected(c, selection)
                return
        # No selection
        self.setSelected(None)

    def setSelected(self, component, hitbox=None):
        """Select a component and draw the hitbox"""
        if (component == self.currentSelection):
            # Nothing to do
            return
        self.currentSelection = component
        self.selectionHitbox = hitbox
        self.redraw()
                