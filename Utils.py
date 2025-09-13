from enum import Enum
import numpy as np


def noSpace(txt):
    return txt.replace(' ', '_')

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
    
    def getAllNets(self):
        """Return a set of all the nets"""
        nets = set()
        nets.update(self.getInputs())
        nets.update(self.getOutputs())
        return nets
    
    def getName(self):
        """Return the block's name"""
        return self.name
    
    def serialize(self):
        """Return a serialized version of this bloc"""
        return f"{noSpace(self.name)} (" + " ".join([str(n) for n in self.inNets]) + ' ' + " ".join([str(n) for n in self.outNets]) + f") {noSpace(self.name)}"

    def generateTemplate(self):
        return f"{noSpace(self.name)} {len(self.inNets)} {len(self.outNets)}"

class ImposedNet():
    def __init__(self, name, net):
        self.name = name
        self.net = net

    def getName(self):
        return self.name

    def getAllNets(self):
        """Return a set of all the nets"""
        return set([self.net])

    def getValue(self, t):
        """Return the value of the net at t"""
        pass

    def getNet(self):
        """Return the net"""
        return self.net
    
    def serialize(self):
        """Return a serialized version of this bloc"""
        return None
    
class OverrideNet():
    def __init__(self, c):
        self.c = c

    def getC(self):
        """return the component"""
        return self.c
    
    def getAllNets(self):
        """Return a set of all the nets"""
        return self.c.getAllNets()
    
    def serialize(self):
        """Return a serialized version of this bloc"""
        return self.c.serialize()
    
    def generateTemplate(self):
        """Generate a template for the model block"""
        return self.c.generateTemplate()

class Constant(ImposedNet):
    """Represent a constant input"""
    def __init__(self, name, net, value):
        super().__init__(name, net)
        self.value = value

    def getValue(self, t):
        """Return the value of the net at t"""
        return self.value
    
    def setValue(self, v):
        self.value = v
    
    def serialize(self):
        """Return a serialized version of this bloc"""
        return f"{noSpace(self.name)} ({self.net}) vsource dc=" + str(self.value)
    
    def generateTemplate(self):
        """Generate a template for the model block"""
        return f"vsource 0 1"

class Sweep(ImposedNet):
    """Add a sweep"""
    def __init__(self, name, net, f):
        super().__init__(name, net)
        self.f = f

    def getValue(self, t):
        """Return the value of the net at t"""
        return self.f(t)
    
    def generateTemplate(self):
        """Generate a template for the model block"""
        return f"vsweep 0 1"
    
    
class SweepBetween(Sweep):
    def __init__(self, name, net, xi, xf):
        super().__init__(name, net, lambda t: (np.array(xf)-np.array(xi))*t+np.array(xi))
        self.xi = xi
        self.xf = xf

    def serialize(self):
        """Return a serialized version of this bloc"""
        return f"{noSpace(self.name)} ({self.net}) vsweep x0={self.xi} x0={self.xf}"
    
class Netlist():
    """Represents the model connexion"""

    def __init__(self):
        self.content = []
        self.legend = {}
        self.xTrace = np.linspace(0,1)

    def setRunInterval(self, xTrace):
        self.xTrace = xTrace

    def add(self, c):
        """Add a component to the netlist"""
        self.content.append(c)

    def addLegend(self, net, legend):
        """Add a legend of a net"""
        self.legend[net] = legend

    def getLegend(self):
        return self.legend

    def forcedImage(self, fnet, netv):
        """Compute the net value while forcing the value of fnet"""
        # save the value if possible (voltage source)
        for c in self.content:
            if isinstance(c, Constant) and c.getNet() == fnet:
                c.setValue(netv)
                
        self.image(0, forcedNets={fnet:netv})

    def image(self, t, forcedNets={}):
        """Run the simulation at time t"""

        """
        Start from the constants. Check which leaf are now accesible. update and continue
        """
        computedNet = {'t':t}
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

        """
        Forced net: dictionary netname:value of imposed values
        """
        for e in forcedNets:
            computedNet[e] = forcedNets[e]
            overridedNet.add(e)
        
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
        for t in self.getXtrace():
            self.image(t)
            # Save
            for net in self.computedNet:
                if net not in self.computedNetOnInterval:
                    self.computedNetOnInterval[net] = []
                self.computedNetOnInterval[net].append(self.computedNet[net])

        for net in self.computedNetOnInterval:
            self.computedNetOnInterval[net] = np.array(self.computedNetOnInterval[net])

    def getXtrace(self):
        """Return the time trace of the simulation"""
        return self.xTrace

    def getAllNets(self):
        """Return a set of all the net of the circuit"""
        nets = set(['t'])
        for c in self.content:
            nets.update(c.getAllNets())
        return nets

    def get(self, net):
        """Return a net value"""
        return self.computedNetOnInterval[net]
    
    def getInstantanedNetValue(self, net):
        """Return instantenous net value"""
        return self.computedNet[net]
    
    def serialize(self):
        """Return a writen netlist"""
        text = ""
        for c in self.content:
            text += c.serialize() + "\n"
        return text
    
    def generateTemplate(self):
        """Generate a template for the model block"""
        text = ""
        for c in self.content:
            text += c.generateTemplate() + '\n'
        return text