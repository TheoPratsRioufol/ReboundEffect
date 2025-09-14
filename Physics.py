""" File defining the schematic functions """

import numpy as np

"""
    Catégorie de population:
        - urbain, Pop = ?, Pouvoir d'achat: 10000 
        - rural,  Pop = ?, Pouvoir d'achat: 9000 

    Besoins:
        - ["Prix de revient ($/km)", "km en ville", "km hors ville"]
            =>  Burbain_i = [0.2, 150, 50]
                Brural_i = [0.13, 50, 220]

    Vecteur de design x:
        - ["Vmax (km/h)", "Autonomie (kWh)", "mass (kg)"]
     => Service rendu:
        - ["Rendement (kW/km)", "Distance max (km)"]

    Vecteur de l'état:
        - ["Prix energie ($/kW)", "Subvention ($/voiture)"]

    Autre moyen de transport:
        - ["$ en bus", "$ en train"]

    Coût d'entretient :
        - Révision annuelle (check complet, diagnostic batterie, niveaux fluides)	Tous les 12 mois ou 10 000 km	De 120 € à 180 €
        - Remplacement des pneus (4 roues en 14″)	Tous les 20 000 à 30 000 km	De 180 € à 240 €
        - Freins avant/arrière (kit plaquettes tambours)	Tous les 15 000 à 25 000 km	De 100 € à 160 €
        - Amortisseurs (usure normale sur routes urbaines)	Tous les 40 000 à 60 000 km	De 250 € à 350 €
        - Essuie-glaces / Lave-glace / Ampoules	Selon usure saisonnière	De 20 € à 50 €
        - Pare-brise (remplacement complet)	Si fissure ou impact majeur	Environ 250 €
        - Recharge du liquide de frein et purge circuit	Tous les 2 ans	De 50 € à 70 €
        - Remplacement batterie auxiliaire 12V (si équipée)	Tous les 5 à 6 ans	De 90 € à 130 €
"""

mass_i = 485

# Vitesse et masse au rendement maximal
vmax_optimal = 40
mass_optimal = 400

eff_i = 7.3/100 # rendement initial kW/km
x_i = [45, 75*eff_i, 485] # design initial

p_i = 7990 # Initial price
prodCost_i = 7990*0.5 # Initial production price

dlife = 100000 # Distance (km) sur la vie de la voiture
savMax = 500 # Côut maximal de sav au bout de dlife

""" Impact Carbone """
GESkWh = 0.014 # Coût carbone par kgCo2e/kWh en France
GESprod = 3700 # Coût carbone de production en kgCo2e
GESkmAutreMobilite = np.array([0.113, 0.016]) # Emission carbone par km des autres mobilités (bus, train)
GESautreDepenseParEUR = 1000/250 # Emission GES par euro dépensé. Paris newYork Avion -> 1 Tonne Co2, ~250$

""" Ménages """
loi_i = [0.14, 150] # Prix energie, subvention voiture
Pi_urbain = 8000# pop urbaine
Pi_rural = 5000# pop rurale
ptransport_i = 8000 # Prix initial mis dans les transport


""" Report modal """
CostKmBus   = 2/10 # coût par km de bus (~10km 91.06, 2$)
CostKmTrain = 70/1000 # cout par km de train (marseille lille, 1000km, 70$)

def savCost(distance):
    """Coût de SAV pour l'entreprise"""
    return savMax*(1-np.exp(-3*distance/dlife))

def maintenance(distance):
    cost  = 150*int(distance/10000) # revision
    cost += 200*int(distance/25000) # pneu
    cost += 150*int(distance/20000) # frein
    cost += 300*int(distance/50000) # Amortisseur
    cost += 40*int(distance/5000)   # Accastillage
    return cost

def modele_ingénerie(x):
    """Modèle d'ingénérie. Return [SR] : [rendement (kW/km), dmax (km)]"""
    vmax, autonomie, mass = x
    # Le rendement dépend de vmax et de la masse
    eff = eff_i/(np.exp(-np.abs(-1*(vmax-vmax_optimal)/vmax_optimal))*np.exp(-np.abs(-0.4*(mass-mass_optimal)/mass_optimal)))
    dmax = autonomie/eff
    SR = [eff, dmax]
    return [SR]

def benefice_economique(Q, p, D):
    """Modèle de bénéfice économique. Renvoie le bénéfice"""
    CA = Q*p
    Davg = D/Q
    prodCost = Q*prodCost_i + savCost(Davg)*Q
    return [CA - prodCost]

def impact_voiture(Q, D, SR):
    """Impact de la voiture. On considère que le GES pour simplifier"""
    eff = SR[0]
    kwh = eff*D
    ges = GESkWh*kwh + GESprod*Q
    return [ges]

def impact_autre_transports(EURr, Dr):
    """Impact des autre transport avec l'argent dépense et la distance parcourue (bus et train)"""
    return [GESkmAutreMobilite[0]*Dr[0] + GESkmAutreMobilite[1]*Dr[1]]

def impact_redirection_dépense(EUR):
    """Impact de la redirection des dépenses dans d'autre biens"""
    return [EUR*GESautreDepenseParEUR]

def prix_efficace(p, loi):
    """Renvoie le prix efficace après subvention"""
    return [p - loi[1]]

def satisfaction_pop(B, PA, peff, SR, loi):
    """Renvoie la satisfaction d'une population"""
    # ["Prix de revient ($/km)", "km en ville", "km hors ville"]
    # ["Rendement (kW/km)", "Distance max (km)"]
    # ["Prix energie ($/kW)", "Subvention ($/voiture)"]
    # On commence par transcrire les services rendu vers les besoins
    def fb(SR):
        eff, dmax = SR
        pkm = eff*loi[0]
        kmville = dmax*0.7
        kmautre = dmax*0.3
        return [pkm, kmville, kmautre]
    
    def dsat(a, b):
        """Distance saturée entre a et b: =1 si a<b"""
        return np.where(a < b, np.ones_like(a), np.exp(-3*(a-b)/a))
    
    def d(a, b):
        """Calcule la distance entre les besoins et leur réalisation"""
        return np.array([dsat(b[0], a[0]),
                         dsat(a[1], b[1]),
                         dsat(a[2], b[2])])
    
    S = d(B, fb(SR))*dsat(peff, PA)

    return [S]


def distance_avec_satisfaction(S, alpha, B, pop):
    """Calcule la distance parcourue en fonction de la satisfaction
    pop = 0: urbain,
    pop = 1: rural """

    return [alpha[pop]*B[1+pop]*np.linalg.norm(S)*dlife]

def distance_avec_report_modal(R, B):
    """Calcule la distance parcourue en fonction de la satisfaction"""
    # ["Prix de revient ($/km)", "km en ville", "km hors ville"]
    # ["$ en bus", "$ en train"]
    Dr = np.array([B[1]*np.linalg.norm(R)*dlife, B[2]*np.linalg.norm(R)*dlife])
    return [Dr]

def cout_report_modal(Dr):
    """Calcule le cout du report modal avec la distance"""
    return [np.array([Dr[0]*CostKmBus, Dr[1]*CostKmTrain])]

def bien_etre(CostV, CostR, alpha, pop):
    """Calcule le bien être"""
    return [alpha[pop]**2/(CostV + CostR)]

def cout_user_voiture(Q, peff, D, loi, SR):
    """Coût d'utilisation de la voiture pour le consomateur"""
    # ["Rendement (kW/km)", "Distance max (km)"]
    # ["Prix energie ($/kW)", "Subvention ($/voiture)"]
    kmCost = loi[0]*SR[0]
    return [Q*peff + maintenance(D/Q)*Q + kmCost*D, D/Q]

def autre_depenses(ptransport):
    """Calcule l'argent mis dans les autre dépenses que le transport"""
    return ptransport_i - ptransport