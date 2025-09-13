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
        self.geometry("300x200")

        self.dim = 1 # dimention

        self.controlledNet = net
        self.schematicViewver = schematicViewver

        self.protocol("WM_DELETE_WINDOW", self.kill)

        self.netname = net.getName()
        value_i = self.getNetValue()

        if isinstance(value_i, list) or isinstance(value_i, np.ndarray):
            # Vectorized input
            self.dim = len(value_i)

        self.vartitle = []
        self.value_i = []
        self.min = []
        self.max = []
        self.scaleVar = []
        for i in range(self.dim):
            self.vartitle.append(tk.StringVar())
            self.min.append(tk.StringVar())
            self.max.append(tk.StringVar())
            self.scaleVar.append(tk.DoubleVar(value=0.5))
        
            # Extract the initial value
            if self.dim == 1:
                value = value_i
            else:
                value = value_i[i]

            self.value_i.append(value)
            
            if value != 0:
                self.min[i].set('{:.2f}'.format(value*0.1))
                self.max[i].set('{:.2f}'.format(value*10))
            else:
                self.min[i].set(0)
                self.max[i].set(1)

            scaleFrame = tk.Frame(self)
            tk.Label(scaleFrame, textvariable=self.vartitle[i]).pack(fill=tk.X)
            # Add min, max entry
            tk.Entry(scaleFrame, textvariable=self.min[i], width=8).pack(side=tk.LEFT, fill=tk.X)
            ttk.Scale(scaleFrame, orient=tk.HORIZONTAL, from_=0, to=1, variable=self.scaleVar[i], command=lambda v, idx=i: self.valueChanged(idx)).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Entry(scaleFrame, textvariable=self.max[i], width=8).pack(side=tk.LEFT, fill=tk.X)
            scaleFrame.pack(fill=tk.X, expand=True)
            
        self.setValue(value_i)

        self.wm_title(f">>{self.netname}<< Controller")


    def sliderToValue(self, index):
        alpha = int(NB_STEP_FORCED_VALUE*self.scaleVar[index].get())/NB_STEP_FORCED_VALUE
        min = varToFloat(self.min[index])
        max = varToFloat(self.max[index])
        return alpha*(max - min) + min
    
    def valueToSlider(self, index, value):
        min = varToFloat(self.min[index])
        max = varToFloat(self.max[index])
        if (value < min):
            min = value
            self.min[index].set(value)
        if (value > max):
            max = value
            self.max[index].set(value)
        # min < value < max
        alpha = (value - min)/(max - min)
        alpha = np.clip(alpha, 0, 1)
        self.scaleVar[index].set(alpha)

    def readValueFromGUI(self):
        if self.dim == 1:
            return self.sliderToValue(0)
        else:
            out = np.zeros(self.dim)
            for i in range(self.dim):
                out[i] = self.sliderToValue(i)
            return out

    def valueChanged(self, index):
        """Triggered when the forced value has changed"""
        v = self.readValueFromGUI()
        self.setValue(v)
        if self.dim == 1:
            self.schematicViewver.forcedInput(self.controlledNet.getName(), v)
        else:
            self.schematicViewver.forcedInput(self.controlledNet.getName(), v, forcedValue=v[index], label=f'{self.netname}, comp. {self.schematicViewver.getComponentName(self.netname, index)}')

    def setValue(self, v, forceSlider=False):
        """Set the value of the controlled net"""
        if self.dim == 1:
            v = [v]
        for i in range(self.dim):
            self.vartitle[i].set('Component {}, initial: {:.2f}, current: {:.2f}'.format(self.schematicViewver.getComponentName(self.netname, i), self.value_i[i], v[i]))
            if forceSlider:
                self.valueToSlider(i, v[i])

    def refreshWave(self):
        """Refresh the wave value"""
        self.setValue(self.getNetValue(), forceSlider=True)

    def getNetValue(self):
        """Return the value of the controlled net"""
        # default one
        default = traces[self.netname]['y'][0]
        
        if self.netname in self.schematicViewver.getForcedYTrace():
            ys = self.schematicViewver.getForcedYTrace()[self.netname]
            if len(ys) == 0:
                return default
            return ys[self.schematicViewver.getLastForcedIdx()]
        
        return default
    
    def kill(self):
        self.schematicViewver.closeController(self)
        self.destroy()

    def getControlledNetName(self):
        return self.netname
