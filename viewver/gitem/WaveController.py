import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import sys
import pathlib
_parentdir = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_parentdir))


from viewver.gitem.SchematicViewver import *
from viewver.gitem.GraphicalItem import *

from Schematic import *

def varToFloat(v):
    """Turn a variable to a float"""
    try:
        return float(v.get())
    except:
        return 0

class WaveController(tk.Toplevel):
    def __init__(self, schematicViewver, net):
        """Create a wave controller object.
        net: the net controlled"""
        super().__init__()
        self.wm_title("Waveform Controller")
        self.geometry("300x100")
        self.titlevar = tk.StringVar()
        self.valuevar = tk.StringVar()
        self.min = tk.StringVar()
        self.max = tk.StringVar()
        self.scaleVar = tk.DoubleVar(value=0.5)
        self.scaleVar.trace_add("write", self.valueChanged)
        self.controlledNet = net
        self.schematicViewver = schematicViewver

        netname = self.controlledNet.getName()
        value = traces[netname]['y'][0]
        self.titlevar.set(f'>>{netname}<<, inital value: {value}')
        self.setValue(value)

        # set the value for min and max
        if value != 0:
            self.min.set('{:.2f}'.format(value*0.1))
            self.max.set('{:.2f}'.format(value*10))
        else:
            self.min.set(0)
            self.max.set(1)

        tk.Label(self, textvariable=self.titlevar).pack(fill=tk.X)
        tk.Label(self, textvariable=self.valuevar).pack(fill=tk.X)
        
        scaleFrame = tk.Frame(self)
        # Add min, max entry
        tk.Entry(scaleFrame, textvariable=self.min, width=8).pack(side=tk.LEFT, fill=tk.X)
        ttk.Scale(scaleFrame, orient=tk.HORIZONTAL, from_=0, to=1, variable=self.scaleVar).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Entry(scaleFrame, textvariable=self.max, width=8).pack(side=tk.LEFT, fill=tk.X)

        scaleFrame.pack(fill=tk.X, expand=True)

    def valueChanged(self, a, b, c):
        """Triggered when the forced value has changed"""
        alpha = self.scaleVar.get()
        min = varToFloat(self.min)
        max = varToFloat(self.max)
        v = alpha*(max - min) + min
        self.setValue(v)

    def setValue(self, v):
        """Set the value of the controlled net"""
        self.valuevar.set('Current value: {:.2f}'.format(v))