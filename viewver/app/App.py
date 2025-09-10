import tkinter as tk
from tkinter import ttk

import sys
import pathlib
_parentdir = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_parentdir))

from viewver.gitem.SchematicViewver import *
from viewver.gitem.GraphicalItem import *
from Utils import *

if __name__ == '__main__':
    import Main

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Netlist Viewver")
        self.geometry(f"600x600+{50}+{50}")
        self.mainPane = tk.Frame(self)
        self.mainPane.pack(fill=tk.BOTH, expand=True)
        self.build()

    def build(self):
        self.schematicViewver = ShematicViewver(self.mainPane)
        self.schematicViewver.pack(fill=tk.BOTH, expand=True)

        self.schematicViewver.add(Component("fct 1", [Net.price, Net.Q], [Net.distance]))