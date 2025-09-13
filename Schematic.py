"""Schematic of the rebound effect"""

from Utils import *
from Physics import *
import numpy as np
import matplotlib.pyplot as plt

netlist = Netlist()

# Constante x0, d0?

"""netlist.add(Block("Voiture", car, [Net.x], [Net.efficiency]))
netlist.add(Block("Comportement Routier", userDrivingModel, [Net.law, Net.efficiency], [Net.distance]))
netlist.add(Block("Comportement Achats", userBuyingModel, [Net.law, Net.efficiency, Net.price], [Net.Q, Net.people]))

netlist.add(Block("Usage cost", usageCost, [Net.law, Net.efficiency, Net.distance], [Net.useCost]))
netlist.add(Block("Owner cost", summator, [Net.useCost, Net.price], [Net.budget]))

netlist.add(Block("Direct Impact", LCA, [Net.x, Net.Q], [Net.lci]))
netlist.add(Block("Spending model", MCM, [Net.budget], [Net.spending]))
netlist.add(Block("Spendings", multiplier, [Net.spending, Net.people], [Net.spendings]))
netlist.add(Block("Indirect Impact", HLCA, [Net.spendings, Net.people], [Net.indi]))
netlist.add(Block("Total impacts", summator, [Net.indi, Net.lci], [Net.itot]))

netlist.add(Block("Production cost", productionCost, [Net.x, Net.law, Net.Q], [Net.prodCost]))
netlist.add(Block("C.A", multiplier, [Net.price, Net.Q], [Net.sales]))
netlist.add(Block("Benefits", substractor, [Net.sales, Net.prodCost], [Net.benefits]))

netlist.add(Block("Social well being", socialWellBeing, [Net.x], [Net.socialWellBeing]))


netlist.add(Constant(str(Net.law), Net.law, law_i))
netlist.add(Constant(str(Net.x), Net.x, x_i))
netlist.add(Constant(str(Net.price), Net.price, p0))"""

def fa(x):
    return [x, np.array([x**2, x])]

def fb(x):
    return [x**2]

netlist.add(Constant(str(Net.x), Net.x, 1))
netlist.add(Block("A", fa, [Net.x], [Net.law, Net.budget]))
netlist.add(Block("B", fb, [Net.law], [Net.Q]))
netlist.add(Block("C", fb, [Net.budget], [Net.itot]))

netlist.addLegend(Net.budget, ["budA", "budB"])

with open('netlist.txt', 'w') as f:
    f.write(netlist.serialize())

with open('blockTemplate.txt', 'w') as f:
    f.write(netlist.generateTemplate())

netlist.setRunInterval([0])
netlist.run()
traces = {str(net):{'x':netlist.getXtrace(),
                    'y':netlist.get(net)} for net in netlist.getAllNets()}