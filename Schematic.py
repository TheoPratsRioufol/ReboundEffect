"""Schematic of the rebound effect"""

from Utils import *
from Physics import *
import numpy as np
import matplotlib.pyplot as plt

netlist = Netlist()

# Constante x0, d0?

netlist.add(Block("Voiture", car, ["x"], ["efficiency"]))
netlist.add(Block("Comportement Routier", userDrivingModel, ["law", "efficiency"], ["distance"]))
netlist.add(Block("Comportement Achats", userBuyingModel, ["law", "efficiency", "price"], ["Q", "people"]))

netlist.add(Block("Usage cost", usageCost, ["law", "efficiency", "distance"], ["useCost"]))
netlist.add(Block("Owner cost", summator, ["useCost", "price"], ["budget"]))

netlist.add(Block("Direct Impact", LCA, ["x", "Q"], ["lci"]))
netlist.add(Block("Spending model", MCM, ["budget"], ["spending"]))
netlist.add(Block("Spendings", multiplier, ["spending", "people"], ["spendings"]))
netlist.add(Block("Indirect Impact", HLCA, ["spendings", "people"], ["indi"]))
netlist.add(Block("Total impacts", summator, ["indi", "lci"], ["itot"]))

netlist.add(Block("Production cost", productionCost, ["x", "law", "Q"], ["prodCost"]))
netlist.add(Block("C.A", multiplier, ["price", "Q"], ["sales"]))
netlist.add(Block("Benefits", substractor, ["sales", "prodCost"], ["benefits"]))

netlist.add(Block("Social well being", socialWellBeing, ["x"], ["socialWellBeing"]))


netlist.add(Constant("law", "law", law_i))
netlist.add(Constant("x", "x", x_i))
netlist.add(Constant("price", "price", p0))

"""def fa(x):
    return [x, np.array([x**2, x])]

def fb(x):
    return [x**2]

netlist.add(Constant("a", "a", 1))
netlist.add(Block("A", fa, ["a"], ["a1", "a2"]))
netlist.add(Block("B", fb, ["a1"], ["o1"]))
netlist.add(Block("C", fb, ["a2"], ["o2"]))"""

#netlist.addLegend("a2", ["budA", "budB"])

with open('netlist.txt', 'w') as f:
    f.write(netlist.serialize())

with open('blockTemplate.txt', 'w') as f:
    f.write(netlist.generateTemplate())

netlist.setRunInterval([0])
netlist.run()
traces = {str(net):{'x':netlist.getXtrace(),
                    'y':netlist.get(net)} for net in netlist.getAllNets()}