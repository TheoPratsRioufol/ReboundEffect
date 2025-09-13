"""Schematic of the rebound effect"""

from Utils import *
from Physics import *
import numpy as np
import matplotlib.pyplot as plt

netlist = Netlist()


b_i = 0.5
netlist.addLegend("alpha", ["urbain", "rural"])

x_i = [45, 75, 485]
netlist.addLegend("x", ["Vmax (km/h)", "Autonomie (kWh)", "mass (kg)"])

p_i = 990 # Initial price

loi_i = [0.14, 150]
netlist.addLegend("loi", ["Prix energie ($/km)", "Subvention ($/voiture)"])

netlist.addLegend("SR", ["Rendement (kW/km)", "Distance max (km)"])

netlist.addLegend("$r", ["$ en bus", "$ en train"])
netlist.addLegend("Dr", ["km en bus", "km en train"])


netlist.add(Constant("Balance Marché", "b", b_i))
netlist.add(Constant("Choix Techniques", "x", x_i))
netlist.add(Constant("Prix", "p", p_i))
netlist.add(Constant("Politique publique", "loi", loi_i))

netlist.add(Block("Pop.Visée", lambda x: [[x, 1-x]], ["b"], ["alpha"]))
netlist.add(Block("Modèle d'ingénérie", lambda x:[0], ["x"], ["SR"]))

netlist.add(Block("Ménage", lambda a,b,c,d:[0]*6, ["SR", "loi", "alpha", "p"], ["Q", "D", "Davg", "Dr", "$r", "$autre"]))

netlist.add(Block("Bénéfice economique", lambda a,b,c:[0], ["Q", "p", "Davg"], ["$"]))

netlist.add(Block("Impact de la voiture", lambda a,b,c:[0], ["Q", "D", "Davg"], ["iv"]))
netlist.add(Block("Impact des autres transports", lambda a,b:[0], ["$r", "Dr"], ["iav"]))
netlist.add(Block("Impact redirection des dépenses", lambda c:[0], ["$autre"], ["ia"]))

netlist.add(Block("Somme", lambda a,b,c:[a+b+c], ["iv", "ia", "iav"], ["itot"]))


traces = postProdNetlist(netlist)