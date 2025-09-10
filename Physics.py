""" File defining the schematic functions """

import numpy as np

"""
    Simplified vector:
        x: [Vmax (km/h), Range (km), mass (kg)]
        law: [energy price ($/kWh), subvention ($/car)]
        impact: [C02, Materials]

    Initial condition: (AMI Car)
        price: 7990
        x: [45 km/h, 75km, 485kg]
        law: [0.1952, 0]
        c0: 7,3 kWh/100 mean consumption
        kmtot: 100 000 # Total number of km on the car's life

    Cost :
        - Révision annuelle (check complet, diagnostic batterie, niveaux fluides)	Tous les 12 mois ou 10 000 km	De 120 € à 180 €
        - Remplacement des pneus (4 roues en 14″)	Tous les 20 000 à 30 000 km	De 180 € à 240 €
        - Freins avant/arrière (kit plaquettes tambours)	Tous les 15 000 à 25 000 km	De 100 € à 160 €
        - Amortisseurs (usure normale sur routes urbaines)	Tous les 40 000 à 60 000 km	De 250 € à 350 €
        - Essuie-glaces / Lave-glace / Ampoules	Selon usure saisonnière	De 20 € à 50 €
        - Pare-brise (remplacement complet)	Si fissure ou impact majeur	Environ 250 €
        - Recharge du liquide de frein et purge circuit	Tous les 2 ans	De 50 € à 70 €
        - Remplacement batterie auxiliaire 12V (si équipée)	Tous les 5 à 6 ans	De 90 € à 130 €
"""

def maintenance(distance):
    cost  = 150*int(distance/10000) # revision
    cost += 200*int(distance/25000) # pneu
    cost += 150*int(distance/20000) # frein
    cost += 300*int(distance/50000) # Amortisseur
    cost += 40*int(distance/5000)   # Accastillage
    return cost

x_i = [45, 75, 485]
law_i = [0.1952, 0]
kmtot_i = 100000
eff_i = 7.3
Q_i = 4720 #January/july 2024
p0 = 7990 # Initial price
avgLifefuelPrice_i = (kmtot_i/100)*eff_i*law_i[0]

def car(x):
    """Return the Defficiency depending a D(design vector) Dx"""
    eff = eff_i*np.exp(-0.5*(x[1]-x_i[0])/x_i[0])
    return [eff]

def userDrivingModel(law, efficiency):
    """Driving model of the user,
    Return distance"""
    # Hyp: spend almost the same amount of money in the fuel on the car's life (for different efficiency)
    new_kmtot = 100*avgLifefuelPrice_i/(efficiency*law[0])
    if (efficiency > eff_i):
        # drive a bit less km than exactly the same amount of money
        new_kmtot = (new_kmtot - kmtot_i)*0.9 + kmtot_i
    else:
        # drive a bit more km than exactly the same amount of money
        new_kmtot = (kmtot_i - new_kmtot)*1.1 + new_kmtot
    return [new_kmtot]

def userBuyingModel(law, efficiency, price):
    """Buying model of the user.
    Return Q, people"""
    # Elasticity / price: -0.6
    # Elasticity / spend in fuel: -0.2 (less obvious)
    netPrice = price - law[1]
    avgLifefuelPrice = (kmtot_i/100)*efficiency*law[0]
    Q = Q_i + (netPrice - p0)*(-0.6) + (avgLifefuelPrice - avgLifefuelPrice_i)*(-0.2)
    return [Q, 1.05*Q]

def usageCost(law, efficiency, distance):
    """Cost ($) relative to the car usage model
    Return useCost"""
    fuelPrice = (distance/100)*efficiency*law[0]
    useCost = fuelPrice + maintenance(distance)
    return [useCost]

def productionCost(x, law, Q):
    """Cost ($) to produce the cars
    Return prodCost"""
    prodCost = p0*0.7*(1 - min(0.1*Q/Q_i, 0.5))*(1 - min(0.1*x[1]/x_i[1], 0.2))
    return [prodCost]

def LCA(x, Q):
    """LCA Model.
    Return the Life Cycle impact (lci)"""
    return [0]

def HLCA(x, people):
    """HLCA Model.
    Return the indirect impacts (lci)"""
    return [0]

def MCM(budget):
    """MCM Model
    Return the spending in different categories"""
    return [0]

def socialWellBeing(x):
    """Return the social well"""
    swb = x[0] * x[1] * x[2]
    return [swb]

def summator(a, b):
    return [a + b]

def multiplier(a, b):
    return [a*b]

def substractor(a, b):
    return [a - b]