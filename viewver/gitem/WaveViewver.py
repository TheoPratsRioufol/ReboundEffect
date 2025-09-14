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

class WaveViewver(tk.Toplevel):
    def __init__(self, schematicViewver, net):
        super().__init__()
        """Create a wave controller object.
        net: the net contromonitored"""
        self.wm_title("Waveform")
        self.geometry("400x400")
        self.protocol("WM_DELETE_WINDOW", self.kill)

        self.schematicViewver = schematicViewver
        self.monitoredNet = net
        self.name = tk.StringVar()
        self.netname = self.monitoredNet.getName()

        fig = Figure(figsize = (5, 5), dpi = 100)
        self.ax = fig.add_subplot(111)
        self.ax.plot()

        self.canvas = FigureCanvasTkAgg(fig, master=self)  
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()

        self.canvas.get_tk_widget().pack(fill=tk.X)

        self.updateGraph()

    def updateGraph(self):
        """Update the plotted graph"""
        self.ax.cla()
        self.ax.set_title(self.netname)
        xs = self.schematicViewver.getForcedXTrace()
        ys = self.schematicViewver.getForcedYTrace()[self.netname]
        if len(xs) > 0:
            if (isinstance(ys[0], list) or isinstance(ys[0], np.ndarray)):
                # Vectorized output
                for k in range(len(ys[0])):
                    self.ax.plot(xs, [i[k] for i in ys], '.-', label=f'{self.schematicViewver.getComponentName(self.netname, k)}')
                    self.ax.plot(xs[self.schematicViewver.getLastForcedIdx()], 
                                ys[self.schematicViewver.getLastForcedIdx()][k], 'ro')
                self.ax.legend()
            else:
                # Scalar output
                self.ax.plot(xs, ys, '.-')
                self.ax.plot(xs[self.schematicViewver.getLastForcedIdx()], 
                            ys[self.schematicViewver.getLastForcedIdx()], 'ro')
            
        self.ax.set_xlabel(self.schematicViewver.getForcedTraceLabel())
        self.canvas.draw()

    def refreshWave(self):
        """Refresh the wave value"""
        self.updateGraph()

    def kill(self):
        self.schematicViewver.closeViewver(self)
        self.destroy()
        print("killed")