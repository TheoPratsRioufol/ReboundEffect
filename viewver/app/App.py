import tkinter as tk
from tkinter import ttk

import sys
import pathlib
_parentdir = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_parentdir))

from viewver.gitem.SchematicViewver import *
from viewver.gitem.GraphicalItem import *
from Utils import *
import json

if __name__ == '__main__':
    import Main

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Netlist Viewver")
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}+{800}+{50}")
        self.mainPane = tk.Frame(self)
        self.mainPane.pack(fill=tk.BOTH, expand=True)
        self.buildMenu()
        self.build()

    def build(self):
        """Add the main components of the window"""
        self.schematicViewver = ShematicViewver(self.mainPane)
        self.schematicViewver.pack(fill=tk.BOTH, expand=True)

        self.schematicViewver.loadNetlistFromPath('netlist.txt', 'blockTemplate.txt')
        self.load()
        self.schematicViewver.redraw()

    def buildMenu(self):
        """Build a menubar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar)

        file_menu.add_command(label='Load', command=self.load)
        file_menu.add_command(label='Save', command=self.save)

        menubar.add_cascade(label="File", menu=file_menu)

    def load(self):
        """Load a netlist"""
        # Load to file
        with open('save.json', 'r') as f:
            save = json.load(f)
        self.schematicViewver.load(save['schematicViewver'])

    def save(self):
        """Save a netlist"""
        save = {}
        save['schematicViewver'] = self.schematicViewver.getSaveDic()
        # Save to file
        with open('save.json', 'w') as f:
            json.dump(save, f, indent=4)