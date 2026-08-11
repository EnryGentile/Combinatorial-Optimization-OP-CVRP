import gurobipy as gp
from gurobipy import GRB
import math
import matplotlib.pyplot as plt
import random

def distanza_euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def lettura_problema(path_problem_file):  #Legge i dati di input 
    with open(path_problem_file,"r") as file:
        righe=file.readlines()
    nodi={}     #dizionario-->associamo ad una chiave i valori-->associamo tramite id le coordinate
    domande={}  #"" "" "" associamo all'id la quantità di domanda
    deposito=None
    capacita=None

    sezione = None
    for riga in righe:
        riga = riga.strip()
        if riga.startswith("CAPACITY"):
            sezione = "capacita" 
        if riga == "NODE_COORD_SECTION":
            sezione = "coordinate"      #siamo entrati nella sezione del file che ci elenca le coordinate
            continue
        elif riga == "DEMAND_SECTION":
            sezione = "domande"         #sezione relativa alla richiesta dei clienti
            continue
        elif riga == "DEPOT_SECTION":
            sezione = "deposito"        #indica qual è il nodo deposito (il -1 indica la fine della lista dei depositi pocihé potrebbero essercene più di uno)
            continue
        elif riga == "EOF":
            break                       #Mi serve per uscire dal ciclo for-->siamo arrivati alla fine del file e abbiamo riscontrato la riga "EOF"

        if sezione == "coordinate":             #Facciamo due sezioni diverse nonostante splittiamo in entrambi i casi perché
            riga_splittata = riga.split()       #nella sezione coordinate abbiamo bisogno di 3 split (id,x,y) mentre nella sezione domanda solo 2 (id,domanda)
            id_nodo = int(riga_splittata[0])
            x = (float(riga_splittata[1]))
            y = (float(riga_splittata[2]))
            nodi[id_nodo] = (x, y)

        elif sezione == "domande":
            riga_splittata = riga.split()
            id_nodo = int(riga_splittata[0])
            domanda = int(riga_splittata[1])
            domande[id_nodo] = domanda

        elif sezione == "deposito":
            if int(riga) != -1:         #se troviamo il valore -1 abbiamo finito la lista, in questo caso abbiamo solo un deposito, per questo è un valo
                deposito = int(riga)

        elif sezione == "capacita":
            riga_splittata = riga.split()
            capacita=int(riga_splittata[2])
        
    return nodi, domande, deposito, capacita

def plot_percorsi(nodi, percorsi, nome_file="soluzione_cvrp.png"):
    plt.figure(figsize=(10, 6))

    for id_nodo, coord in nodi.items():
        plt.plot(coord[0], coord[1], 'ko' if id_nodo == 1 else 'bo')
        plt.text(coord[0], coord[1], str(id_nodo), fontsize=8, ha='right')

    colori = plt.cm.get_cmap('tab10', len(percorsi))
    for idx, percorso in enumerate(percorsi):
        x = [nodi[n][0] for n in percorso]
        y = [nodi[n][1] for n in percorso]
        plt.plot(x, y, color=colori(idx), label=f"Veicolo {idx+1}")

    plt.title("Soluzione CVRP")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(nome_file)
    plt.close()

def ricostruisci_percorsi(x, deposito, C):
    archi_attivi = [(i, j) for (i, j) in x.keys() if x[i, j].X > 0.5]
    percorsi = []

    while True:
        arco = next((a for a in archi_attivi if a[0] == deposito), None)
        if arco is None:
            break

        percorso = [arco[0], arco[1]]
        archi_attivi.remove(arco)

        while percorso[-1] != deposito:
            prossimo = next((a for a in archi_attivi if a[0] == percorso[-1]), None)
            if prossimo is None:
                break
            percorso.append(prossimo[1])
            archi_attivi.remove(prossimo)

        percorsi.append(percorso)

    return percorsi



def solve_cvrp(nodi, domande, deposito, capacita, num_vehicles):
    N = list(nodi.keys())  
    C = [i for i in N if i != deposito]
    V = N

    distanze = {(i, j): distanza_euclid(nodi[i], nodi[j]) for i in V for j in V if i != j}

    m = gp.Model("CVRP")
    m.setParam('TimeLimit', 60)

    x = m.addVars(distanze.keys(), vtype=GRB.BINARY, name="x")

    u = m.addVars(C, vtype=GRB.CONTINUOUS, lb=domande[min(C)], ub=capacita, name="u")

    m.setObjective(gp.quicksum(distanze[i, j] * x[i, j] for i, j in distanze), GRB.MINIMIZE)

    for j in C:
        m.addConstr(gp.quicksum(x[i, j] for i in V if i != j) == 1)
        m.addConstr(gp.quicksum(x[j, k] for k in V if k != j) == 1)

    m.addConstr(gp.quicksum(x[deposito, j] for j in C) == num_vehicles, name="num_veicoli")

    for i in C:
        for j in C:
            if i != j:
              m.addConstr(u[i] - u[j] + capacita * x[i, j] <= capacita - domande[j] * x[i, j], name=f"mtz_{i}_{j}") #u[i] - u[j] + <= - d[j]*x[i,j] +Q(1-x[i,j])--> 
                

    m.optimize()

    if m.SolCount > 0:
        print(f"{m.ObjVal:.2f}")

        percorsi = ricostruisci_percorsi(x, deposito, C)
        plot_percorsi(nodi, percorsi, "soluzione_cvrp.png")  # Salva il plot
    else:
        print("Nessuna soluzione trovata.")




nodi,domande,deposito,capacita= lettura_problema("CVRP\F-n135-k7.txt")

solve_cvrp(nodi, domande, deposito, capacita, 14)
