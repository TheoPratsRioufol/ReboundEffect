import tkinter as tk
from tkinter import ttk
import numpy as np

import sys
import pathlib
_parentdir = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_parentdir))

from viewver.config.Config import *
from viewver.gitem.GraphicalItem import *
from viewver.gitem.NetlistExtractor import *
from viewver.gitem.WaveViewver import *
from viewver.gitem.WaveController import *


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
        self.gitem = {} # dic of graphical items
        self.currentSelection = None
        self.idcounter = 0
        
        self.waveControllers = set()
        self.waveViewvers = set()

        self.lastForcedNet = None # Last forced input net
        self.resetForcedTrace()

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind_all("<MouseWheel>", self.mouseWheel)
        self.canvas.bind("<B3-Motion>", self.mousePressedRigthMove)
        self.canvas.bind("<B1-Motion>", self.mousePressedLeftMove)
        self.canvas.bind("<Motion>", self.mouseMove)
        self.canvas.bind("<Button-1>", self.mouseLeftDown)
        self.canvas.bind("<Button-3>", self.mouseRigthDown)
        self.canvas.bind("<ButtonRelease-1>", self.mouseLeftUp)

    def getUniqueId(self):
        """Return an unique id for a gitem"""
        self.idcounter += 1
        return self.idcounter

    def add(self, b, gid=None):
        """Add a Graphical item to be displayed"""
        assert isinstance(b, GraphicalItem), "b must be an graphical item"
        if gid == None:
            gid = self.getUniqueId()
        self.gitem[gid] = b
        # Refresh
        self.redraw()

    def redraw(self):
        """Redraw the canvas"""
        self.canvas.delete("all")

        for gid in self.gitem:
            self.gitem[gid].draw(self.canvas, self.camera)
        
        if self.currentSelection != None:
            self.currentSelection.drawHighlight(self.canvas, self.camera)

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
            # Sate the component original position
            self.selectionOrigin = self.currentSelection.getPos()

            # If net, actions are available:
            if isinstance(self.currentSelection, GraphicalNet):
                if event.state & 0x4:
                    # If Crt down
                    self.waveControllers.add(WaveController(self, self.currentSelection))
                else:
                    self.waveViewvers.add(WaveViewver(self, self.currentSelection))
        
    def mouseRigthDown(self, event):
        """Mouse Rigth click down"""
        self.saveMouseStartingPos(event)

    def mouseLeftUp(self, event):
        """Mouse left click up"""
        self.cameraStartingPt = None

    def mousePressedRigthMove(self, event):
        """Mouse motion + Rigth down"""
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
            self.redraw()

    def mouseMove(self, event):
        """Mouse motion"""
        # Get the mouse position in the absolute referential
        xmabs, ymabs = self.camera.inverse2D(event.x, event.y)
        selected = None
        for gid in self.gitem:
            c = self.gitem[gid]
            if c.isSelected(xmabs, ymabs):
                selected = c
                # bypass if net
                if isinstance(c, GraphicalNet):
                    self.setSelected(selected)
                    return
        # No selection
        self.setSelected(selected)

    def setSelected(self, component):
        """Select a component and draw the hitbox"""
        if (component == self.currentSelection):
            # Nothing to do
            return
        self.currentSelection = component
        self.redraw()

    def reset(self):
        """Reset this component"""
        self.setSelected(None)
        self.gitem = {}
        self.canvas.delete("all")
                
    def getSaveDic(self):
        """Return the saving dic of this component"""
        save = {}
        save['components'] = {}
        save['idcounter'] = self.idcounter
        for gid in self.gitem:
            c = self.gitem[gid]
            if isinstance(c, Component):
                save['components'][gid] = c.getSaveDic()

        return save

    def load(self, save):
        """Load a save dic"""
        self.idcounter = save['idcounter']
        for gid in save['components']:
            # Try to find the gitem
            if (gid in self.gitem):
                # the component already exist
                self.gitem[gid].updateFromSave(save['components'][gid])
            else:
                print("[NOT IMPLEMENTED]")
                #self.add(Component.initFromSave(save['components'][gid]))
        self.autoCenter()

    def loadNetlistFromPath(self, netistPath, templatePath):
        """Load a netlist from a path"""
        with open(netistPath, 'r') as f:
            netlist = f.read()
        with open(templatePath, 'r') as f:
            template = f.read()
        self.reset()
        extractedGitem, netdic = NetlistExtractor.extract(netlist, template)
        for gid in extractedGitem:
            self.add(extractedGitem[gid], gid)

        for net in netdic:
            self.add(GraphicalNet(net, [self.gitem[gid] for gid in netdic[net]]))
        
    def refreshMonitors(self):
        """Refresh all the monitors"""
        for monitor in self.waveViewvers:
            monitor.refreshWave()
        for monitor in self.waveControllers:
            monitor.refreshWave()

    def forcedInput(self, fnet, value):
        """Force one imput of the simulation to be changed"""
        if (self.lastForcedNet != fnet):
            self.resetForcedTrace()
        self.lastForcedNet = fnet
        if (value not in self.forcedXtrace):
            netlist.forcedImage(Net.getNetFromName(fnet), value)
            self.forcedXtrace.append(value)
            self.lastForcedIdx = -1
            for e in netlist.computedNet:
                self.traces[str(e)].append(netlist.computedNet[e])
        else:
            self.lastForcedIdx = self.forcedXtrace.index(value)
        self.refreshMonitors()
        
    def getForcedTraceName(self):
        return self.lastForcedNet

    def getForcedXTrace(self):
        return self.forcedXtrace
    
    def getForcedYTrace(self):
        return self.traces
    
    def getLastForcedIdx(self):
        return self.lastForcedIdx
    
    def resetForcedTrace(self):
        self.forcedXtrace = []
        self.traces = {str(e):[] for e in netlist.getAllNets()}
        self.lastForcedIdx = 0

    def closeViewver(self, wv):
        """Close a wave viewver"""
        self.waveViewvers.remove(wv)

    def closeController(self, wc):
        """Close a wave controller"""
        self.waveControllers.remove(wc)

    def autoCenter(self):
        """Auto center on the schematic"""
        sum = np.zeros(2)
        n = 0
        for gid in self.gitem:
            c = self.gitem[gid]
            if isinstance(c, Component):
                sum += np.array(c.getPos())
                n += 1
        if n == 0:
            return
        self.camera.x, self.camera.y = -sum/n + np.array(self.camera.inverse2D(*WINDOW_SIZE))/2