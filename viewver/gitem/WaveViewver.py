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
    def __init__(self, schematicViewver):
        super().__init__()
        self.wm_title("Waveform")
        self.geometry("400x400")

        self.schematicViewver = schematicViewver
        self.name = tk.StringVar()
        self.visible = True

        #tk.Label(self, textvariable=self.name).pack()

        fig = Figure(figsize = (5, 5), dpi = 100)
        self.ax = fig.add_subplot(111)
        self.ax.plot()

        self.canvas = FigureCanvasTkAgg(fig, master=self)  
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()

        self.canvas.get_tk_widget().pack(fill=tk.X)

    def updateGraph(self):
        """Update the plotted graph"""
        self.canvas.draw()

    def show(self):
        """Display the window at a specific coordinate"""
        self.deiconify()
        self.visible = True

    def hide(self):
        """Hide the window"""
        self.withdraw()
        self.visible = False

    def setSelection(self, c):
        """Set the currently selected item"""
        if isinstance(c, GraphicalNet):
            netname = c.getName()
            if netname in traces:
                # plot
                self.ax.cla()
                self.ax.set_title(netname)
                self.ax.plot(traces[netname]['x'], traces[netname]['y'])
        
        self.updateGraph()