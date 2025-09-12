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

class WaveController(tk.Toplevel):
    def __init__(self, schematicViewver):
        super().__init__()
        self.wm_title("Waveform Controller")
        self.geometry("400x400")
        self.netname = tk.StringVar()
        self.selection = None

        self.schematicViewver = schematicViewver
        tk.Label(self, textvariable=self.netname).pack()

    def setSelection(self, c):
        """Set the currently selected item"""
        if isinstance(c, GraphicalNet):
            netname = c.getName()
            self.selection = c