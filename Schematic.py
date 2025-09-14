"""Schematic of the rebound effect"""

from Utils import *
from Physics import *
import numpy as np
import matplotlib.pyplot as plt

netlist = Netlist()


b_i = 0.3
netlist.addLegend("alpha", ["urbain", "rural"])
netlist.addLegend("x", ["Vmax (km/h)", "Autonomie (kWh)", "mass (kg)"])
netlist.addLegend("loi", ["Prix energie ($/km)", "Subvention ($/voiture)"])

netlist.addLegend("SR", ["Rendement (kW/km)", "Distance max (km)"])

netlist.addLegend("$r", ["$ en bus", "$ en train"])
netlist.addLegend("Dr", ["km en bus", "km en train"])

netlist.addLegend("Burbain", ["Prix de revient ($/km)", "km en ville", "km hors ville"])
netlist.addLegend("Brural", ["Prix de revient ($/km)", "km en ville", "km hors ville"])
netlist.addLegend("Srural", ["Prix de revient ($/km)", "km en ville", "km hors ville"])
netlist.addLegend("Surbain", ["Prix de revient ($/km)", "km en ville", "km hors ville"])

netlist.addLegend("Drrural", ["km en bus", "km en train"])
netlist.addLegend("Drurbain", ["km en bus", "km en train"])

netlist.addLegend("$rrural", ["$ en bus", "$ en train"])
netlist.addLegend("$rurbain", ["$ en bus", "$ en train"])

# add bounds
netlist.addBounds("b", 0, 1)
netlist.addBounds("x", [30, 0.3*autonomie_i, 0.5*mass_i], [140, 3*autonomie_i, 2*mass_i])
netlist.addBounds("loi", [prixKwh*0.5, 0], [prixKwh*8, subvention_i*2])
netlist.addBounds("p", p_i*0.5, p_i*2)

PAurbain_i = 10000 # pouvoir achat urbain
PArural_i = 9000 # rural

netlist.add(Constant("Balance Marché", "b", b_i))
netlist.add(Constant("Choix Techniques", "x", x_i))
netlist.add(Constant("Prix", "p", p_i))
netlist.add(Constant("Politique publique", "loi", loi_i))
netlist.add(Constant("Pondération Rural", "pondrural", pondrural_i))
netlist.add(Constant("Pondération Urbain", "pondurbain", pondurbain_i))

netlist.add(Block("Pop.Visée", lambda x: [[x, 1-x]], ["b"], ["alpha"]))
netlist.add(Block("Modèle d'ingénérie", modele_ingénerie, ["x"], ["SR"]))

netlist.add(Block("Bénéfice economique", benefice_economique, ["Q", "p", "D"], ["$"]))

netlist.add(Block("Impact de la voiture", impact_voiture, ["Q", "D", "SR"], ["iv"]))
netlist.add(Block("Impact des autres transports", impact_autre_transports, ["$R", "Dr"], ["iav"]))
netlist.add(Block("Impact redirection des dépenses", impact_redirection_dépense, ["$autre"], ["ia"]))

netlist.add(Block("Somme", lambda a,b,c:[a+b+c], ["iv", "ia", "iav"], ["itot"]))


"""Block Ménage"""
#netlist.add(Block("Ménage", lambda a,b,c,d:[0]*6, ["SR", "loi", "alpha", "p"], ["Q", "D", "Davg", "Dr", "$r", "$autre"]))


netlist.add(Constant("Besoins Urbain", "Burbain", Burbain_i))
netlist.add(Constant("Besoins Rural", "Brural", Brural_i))

netlist.add(Constant("PA Urbain", "PAurbain", PAurbain_i))
netlist.add(Constant("PA Rural", "PArural", PArural_i))

netlist.add(Block("Prix efficace", prix_efficace, ["p", "loi"], ["peff"]))

netlist.add(Block("Satisfaction Urbaine", satisfaction_pop, ["Burbain", "PAurbain", "peff", "SR", "loi","pondurbain"], ["Surbain"]))
netlist.add(Block("Satisfaction Rurale", satisfaction_pop, ["Brural", "PArural", "peff", "SR", "loi","pondrural"], ["Srural"]))

netlist.add(Block("Ventes Rurale", lambda a,b:[np.linalg.norm(a)*b[1]*Pi_rural], ["Srural", "alpha"], ["Qrural"]))
netlist.add(Block("Ventes Urbaine", lambda a,b:[np.linalg.norm(a)*b[0]*Pi_urbain], ["Surbain", "alpha"], ["Qurbain"]))

netlist.add(Block("Distance Rurale", lambda a,b,c:distance_avec_satisfaction(a, b, c, 1), ["Srural", "alpha", "Brural"], ["Drural"]))
netlist.add(Block("Distance Urbaine", lambda a,b,c:distance_avec_satisfaction(a, b, c, 0), ["Surbain", "alpha", "Burbain"], ["Durbain"]))

netlist.add(Block("BE rural", lambda a,b,c:bien_etre(a,b,c,1), ["$rural", "$rrural", "alpha"], ["BErural"]))
netlist.add(Block("BE urbain", lambda a,b,c:bien_etre(a,b,c,0), ["$urbain", "$rurbain", "alpha"], ["BEurbain"]))

netlist.add(Block("BE pondéré", lambda a,b:[a+b], ["BErural", "BEurbain"], ["BE"]))

netlist.add(Block("Coût rural", cout_user_voiture, ["Qrural", "peff", "Drural", "loi", "SR"], ["$rural", "Davg"]))
netlist.add(Block("Coût urbain", cout_user_voiture, ["Qurbain", "peff", "Durbain", "loi", "SR"], ["$urbain", "Davg"]))

netlist.add(Block("Coût voiture Pondéré", lambda a,b,alpha:[a*alpha[0]+b*alpha[1]], ["$urbain", "$rural", "alpha"], ["$voiture"]))

netlist.add(Block("Coût Report Modal Rural", cout_report_modal, ["Drrural"], ["$rrural"]))
netlist.add(Block("Coût Report Modal Urbain", cout_report_modal, ["Drurbain"], ["$rurbain"]))

netlist.add(Block("Distance Report Modal Rural", distance_avec_report_modal, ["Rrural", "Brural"], ["Drrural"]))
netlist.add(Block("Distance Report Modal Urbain", distance_avec_report_modal, ["Rurbain", "Burbain"], ["Drurbain"]))

netlist.add(Block("Coût Report Modal Pondéré", lambda a,b,alpha:[a*alpha[0]+b*alpha[1]], ["$rurbain", "$rrural", "alpha"], ["$R"]))
netlist.add(Block("Distance Report Modal Pondéré", lambda a,b,alpha:[a*alpha[0]+b*alpha[1]], ["Drurbain", "Drrural", "alpha"], ["Dr"]))

netlist.add(Block("$Transport", lambda a,b:[a[0]+a[1]+b], ["$R", "$voiture"], ["$transport"]))

netlist.add(Block("Autre dépenses", autre_depenses, ["$transport"], ["$autre"]))

netlist.add(Block("Ventes totales", lambda a,b:[a+b], ["Qrural", "Qurbain"], ["Q"]))
netlist.add(Block("Distance totales", lambda a,b:[a+b], ["Drural", "Durbain"], ["D"]))

netlist.add(Block("Report Modal Rural", lambda x:[1-x], ["Srural"], ["Rrural"]))
netlist.add(Block("Report Modal Urbain", lambda x:[1-x], ["Surbain"], ["Rurbain"]))


traces = postProdNetlist(netlist)