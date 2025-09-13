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

p_i = 7990 # Initial price

loi_i = [0.14, 150]
netlist.addLegend("loi", ["Prix energie ($/km)", "Subvention ($/voiture)"])

netlist.addLegend("SR", ["Rendement (kW/km)", "Distance max (km)"])

netlist.addLegend("$r", ["$ en bus", "$ en train"])
netlist.addLegend("Dr", ["km en bus", "km en train"])

Burbain_i = [0.2, 150, 50]
Brural_i = [0.13, 50, 220]
netlist.addLegend("Burbain", ["Prix de revient ($/km)", "km en ville", "km hors ville"])
netlist.addLegend("Brural", ["Prix de revient ($/km)", "km en ville", "km hors ville"])

PAurbain_i = 10000 # pouvoir achat urbain
PArural_i = 9000 # rural

netlist.add(Constant("Balance Marché", "b", b_i))
netlist.add(Constant("Choix Techniques", "x", x_i))
netlist.add(Constant("Prix", "p", p_i))
netlist.add(Constant("Politique publique", "loi", loi_i))

netlist.add(Block("Pop.Visée", lambda x: [[x, 1-x]], ["b"], ["alpha"]))
netlist.add(Block("Modèle d'ingénérie", lambda x:[0], ["x"], ["SR"]))

netlist.add(Block("Bénéfice economique", lambda a,b,c:[0], ["Q", "p", "D"], ["$"]))

netlist.add(Block("Impact de la voiture", lambda a,b:[0], ["Q", "D"], ["iv"]))
netlist.add(Block("Impact des autres transports", lambda a,b:[0], ["$R", "Dr"], ["iav"]))
netlist.add(Block("Impact redirection des dépenses", lambda c:[0], ["$autre"], ["ia"]))

netlist.add(Block("Somme", lambda a,b,c:[a+b+c], ["iv", "ia", "iav"], ["itot"]))


"""Block Ménage"""
#netlist.add(Block("Ménage", lambda a,b,c,d:[0]*6, ["SR", "loi", "alpha", "p"], ["Q", "D", "Davg", "Dr", "$r", "$autre"]))


netlist.add(Constant("Besoins Urbain", "Burbain", Burbain_i))
netlist.add(Constant("Besoins Rural", "Brural", Brural_i))

netlist.add(Constant("PA Urbain", "PAurbain", PAurbain_i))
netlist.add(Constant("PA Rural", "PArural", PArural_i))

netlist.add(Block("Prix efficace", lambda a,b:[0], ["p", "loi"], ["peff"]))

netlist.add(Block("Satisfaction Urbaine", lambda a,b,c,d:[0], ["Burbain", "PAurbain", "peff", "SR"], ["Surbain"]))
netlist.add(Block("Satisfaction Rurale", lambda a,b,c,d:[0], ["Brural", "PArural", "peff", "SR"], ["Srural"]))

netlist.add(Block("Ventes Rurale", lambda a,b:[0], ["Srural", "alpha"], ["Qrural"]))
netlist.add(Block("Ventes Urbaine", lambda a,b:[0], ["Surbain", "alpha"], ["Qurbain"]))

netlist.add(Block("Distance Rurale", lambda a,b,c:[0], ["Srural", "alpha", "Brural"], ["Drural"]))
netlist.add(Block("Distance Urbaine", lambda a,b,c:[0], ["Surbain", "alpha", "Burbain"], ["Durbain"]))

netlist.add(Block("BE rural", lambda a:[0], ["Qrural"], ["BErural"]))
netlist.add(Block("BE urbain", lambda a:[0], ["Qurbain"], ["BEurbain"]))

netlist.add(Block("BE pondéré", lambda a,b,c:[0], ["BErural", "BEurbain", "alpha"], ["BE"]))

netlist.add(Block("Coût rural", lambda a,b,c:[0], ["Qrural", "peff", "Drural"], ["$rural"]))
netlist.add(Block("Coût urbain", lambda a,b,c:[0], ["Qurbain", "peff", "Durbain"], ["$urbain"]))

netlist.add(Block("Coût voiture Pondéré", lambda a,b,c:[0], ["$urbain", "$rural", "alpha"], ["$voiture"]))

netlist.add(Block("Coût Report Modal Rural", lambda a,b:[0], ["Rrural", "Brural"], ["$rrural"]))
netlist.add(Block("Coût Report Modal Urbain", lambda a,b:[0], ["Rurbain", "Burbain"], ["$rurbain"]))

netlist.add(Block("Distance Report Modal Rural", lambda a,b:[0], ["Rrural", "Brural"], ["Drrural"]))
netlist.add(Block("Distance Report Modal Urbain", lambda a,b:[0], ["Rurbain", "Burbain"], ["Drurbain"]))

netlist.add(Block("Coût Report Modal Pondéré", lambda a,b,c:[0], ["$rrural", "$rurbain", "alpha"], ["$R"]))
netlist.add(Block("Distance Report Modal Pondéré", lambda a,b,c:[0], ["Drrural", "Drurbain", "alpha"], ["Dr"]))

netlist.add(Block("$Transport", lambda a,b:[a+b], ["$R", "$voiture"], ["$transport"]))

netlist.add(Block("Autre dépenses", lambda a:[0], ["$transport"], ["$autre"]))

netlist.add(Block("Ventes totales", lambda a,b:[a+b], ["Qrural", "Qurbain"], ["Q"]))
netlist.add(Block("Distance totales", lambda a,b:[a+b], ["Drural", "Durbain"], ["D"]))

netlist.add(Block("Report Modal Rural", lambda x:[1-x], ["Srural"], ["Rrural"]))
netlist.add(Block("Report Modal Urbain", lambda x:[1-x], ["Surbain"], ["Rurbain"]))


traces = postProdNetlist(netlist)