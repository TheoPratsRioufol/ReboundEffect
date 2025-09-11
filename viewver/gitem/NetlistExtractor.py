"""Read a netlist file"""

import sys
import pathlib
_parentdir = pathlib.Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_parentdir))

from viewver.gitem.GraphicalItem import *

def parseLine(line):
    """Parse a netlist line. Return name, nets, type"""
    type = [e for e in line.split(')')[1].split(' ') if e != ''][0]
    nets = [e for e in line.split('(')[1].split(')')[0].split(' ') if e != '']
    name = [e for e in line.split(' ') if e != ''][0]
    return name, nets, type

def parseTemplate(rawtemplate):
    """Parse a raw template file"""
    template = {}
    for line in rawtemplate.split('\n'):
        line = line.replace('\n','')
        line = [e for e in line.split(' ') if e != '']
        if (len(line) != 3):
            continue
        template[line[0]] = [int(line[1]), int(line[2])]
    return template

def updateNets(nets, cname, inNets, outNets):
    for net in inNets + outNets:
        if (net not in nets):
            nets[net] = set()
        nets[net].add(cname)

class NetlistExtractor():
    def extract(netlist, rawtemplate):
        """Turn a netlist into a graphical representation"""
        gitems = {}
        template = parseTemplate(rawtemplate)
        netdic = {}
        
        for line in netlist.split('\n'):
            line = line.replace('\n','')
            if (len(line) == 0):
                continue

            # Then extract
            name, nets, type = parseLine(line)
            assert type in template, f"{type} is an unknow block (not specified in the templates)"
            inNets = nets[0:template[type][0]]
            outNets = nets[template[type][0]:]
            updateNets(netdic, name, inNets, outNets)

            gitems[name] = Component(name, inNets, outNets)
            
        return gitems, netdic