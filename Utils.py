from enum import Enum
import numpy as np

class Net(Enum):
    efficiency = 'eff'
    x = 'x'
    law = 'law'
    distance = 'distance'
    price = 'price'
    people = 'people'
    Q = 'Q'
    useCost = 'use cost'
    prodCost = 'production cost'
    carCost = 'car cost'
    sales = 'sales'
    benefits = 'benefits'
    lci = 'Life cycle impact'
    spendings = 'Spendings'
    spending = 'Spending / unit'
    indi = 'Indirect impact'
    itot = 'Total impacts'
    budget = 'budget'
    socialWellBeing = 'Social well being'
    t = 't'

class Block():
    """Represent a model.
    Take nets at the input (i.e variables) and output net (variables)"""
    
    def __init__(self, name, fct, inNets, outNets):
        """'inNets' : list of the inputs net
        'outNets: list of the output net"""

        self.name = name
        self.inNets = inNets
        self.outNets = outNets
        self.fct = fct

    def compute(self, inputs):
        return self.fct(*inputs)

    def getInputs(self):
        """Return the inputs"""
        return self.inNets
    
    def getOutputs(self):
        """REturn the outputs"""
        return self.outNets
    
    def getName(self):
        """Return the block's name"""
        return self.name

class ImposedNet():
    def __init__(self, name, net):
        self.name = name
        self.net = net

    def getValue(self, t):
        """Return the value of the net at t"""
        pass

    def getNet(self):
        """Return the net"""
        return self.net
    
class OverrideNet():
    def __init__(self, c):
        self.c = c

    def getC(self):
        """return the component"""
        return self.c

class Constant(ImposedNet):
    """Represent a constant input"""
    def __init__(self, name, net, value):
        super().__init__(name, net)
        self.value = value

    def getValue(self, t):
        """Return the value of the net at t"""
        return self.value
    
class Sweep(ImposedNet):
    """Add a sweep"""
    def __init__(self, name, net, f):
        super().__init__(name, net)
        self.f = f

    def getValue(self, t):
        """Return the value of the net at t"""
        return self.f(t)
    
class SweepBetween(Sweep):
    def __init__(self, name, net, xi, xf):
        super().__init__(name, net, lambda t: (np.array(xf)-np.array(xi))*t+np.array(xi))

class Netlist():
    """Represents the model connexion"""

    def __init__(self):
        self.content = []

    def add(self, c):
        """Add a component to the netlist"""
        self.content.append(c)

    def image(self, t):
        """Run the simulation at time t"""

        """
        Start from the constants. Check which leaf are now accesible. update and continue
        """
        computedNet = {Net.t:t}
        overridedNet = set()
        toCompute = set()
        for c in self.content:
            if isinstance(c, ImposedNet) and c.getNet() not in overridedNet:
                computedNet[c.getNet()] = c.getValue(t)
            elif isinstance(c, OverrideNet):
                computedNet[c.getC().getNet()] = c.getC().getValue(t)
                overridedNet.add(c.getC().getNet())
            else:
                toCompute.add(c)
        
        computedBlock = None
        while (len(toCompute) > 0):
            # Then, propagated
            for c in toCompute:
                # if input are know, compute the output and add them to the computedNet
                computedBlock = c
                if (set(c.getInputs()).issubset(set(computedNet.keys()))):
                    # All the inputs are know
                    outs = c.compute([computedNet[net] for net in c.getInputs()])
                    # Add the output to the list of knowed nets
                    for i in range(len(c.getOutputs())):
                        net = c.getOutputs()[i]
                        if net not in overridedNet:
                            computedNet[net] = outs[i]
                    # break
                    break
            # Remove the computed block
            toCompute.remove(computedBlock)
        
        # Save the reults
        self.computedNet = computedNet

    def run(self):
        """Run the simulation for t in [0, 1]"""
        self.computedNetOnInterval = {}
        for t in np.linspace(0, 1):
            self.image(t)
            # Save
            for net in self.computedNet:
                if net not in self.computedNetOnInterval:
                    self.computedNetOnInterval[net] = []
                self.computedNetOnInterval[net].append(self.computedNet[net])

        for net in self.computedNetOnInterval:
            self.computedNetOnInterval[net] = np.array(self.computedNetOnInterval[net])


    def get(self, net):
        """Return a net value"""
        return self.computedNetOnInterval[net]