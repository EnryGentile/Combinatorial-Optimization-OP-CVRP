import gurobipy as gp
from gurobipy import GRB
import math

def distanza_euclidea(x1,y1,x2,y2):    
    return round(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))


def lettura_file_OP(path_problem_file):
    with open(path_problem_file, "r") as file:
        righe = file.readlines()

    nodi = {}         
    punteggi = {}    
    deposito = None
    cost_limit = None   #Distanza massima/Limite Tempo

    sezione = None
    for riga in righe:
        riga = riga.strip()

        # Leggo i parametri principali
        if riga.startswith("COST_LIMIT"):
            cost_limit = float(riga.split(":")[1].strip())
        elif riga == "NODE_COORD_SECTION":
            sezione = "coordinate"
            continue
        elif riga == "NODE_SCORE_SECTION":
            sezione = "punteggi"
            continue
        elif riga == "DEPOT_SECTION":
            sezione = "deposito"
            continue
        elif riga == "EOF":
            break

        # Leggo le sezioni
        if sezione == "coordinate":
            splitted = riga.split()
            id_nodo = int(splitted[0])
            x = float(splitted[1])
            y = float(splitted[2])
            nodi[id_nodo] = (x, y)

        elif sezione == "punteggi":
            splitted = riga.split()
            if len(splitted) >= 2:
                id_nodo = int(splitted[0])
                score = float(splitted[1])
                punteggi[id_nodo] = score

        elif sezione == "deposito":
            if riga != "-1":
                deposito = int(riga)

    return nodi, punteggi, deposito, cost_limit


#LAZY COSTRAINT
def GeneraLazyConstr(model, where) :
    if where == GRB.Callback.MIPSOL :  #quando gurobi trova una soluzione intera, richiama questa funzione
        SOL = []
        Xvals = model.cbGetSolution(model._x)
        for (i,j) in Xvals:
            if Xvals[i,j] > 0.5 :
                SOL.append((i,j))
        feasible, Tour = LookForMinSubTour(SOL,nodi,deposito)   #chiamata alla funzione per cercare i subtours senza deposito
        
        if not feasible :           #se ci sono sottogiri che rendono la soluzione inammissibile aggiunge i vincoli su quel subtour
                model.cbLazy(gp.quicksum(x[i,j] for i in Tour for j in Tour if i != j) <= len(Tour) -1)




# PROVA CON ROW GEN/ CHIAMATE ANCHE CON LA LAZY CONSTRAINTS
############################################################################################

def LookForSubTours(SOL, FirstNode,Nodes):

    feasible = True

    UnVisited = list(Nodes.keys())
    Visited = []
    NextNode = FirstNode
    
    while NextNode not in Visited :
        
        CurrentNode = NextNode
        UnVisited.remove(CurrentNode)
        Visited.append(CurrentNode)
        
        for (i,j) in SOL :
            if i == CurrentNode :
                NextNode = j
                break
    if len(UnVisited) > 0:
        feasible = False
    
    
    return feasible, Visited


def LookForMinSubTour(SOL,Nodes, depot):
    UnVisited = list(Nodes.keys())
    MinTour = list(Nodes.keys())
    feasible=True

    while len(UnVisited) > 0 :
        FirstNode = UnVisited[0]
        SubTour = LookForSubTours(SOL, FirstNode,Nodes,depot)[1]
        # Considera solo subtour che NON contengono il deposito
        if depot not in SubTour:
            if len(SubTour)>=2 and len(SubTour) < len(MinTour):
                MinTour = SubTour
                feasible = False  # se troviamo un subtour senza deposito, soluzione non fattibile
        
        for i in SubTour :
            UnVisited.remove(i)
        
    return feasible, MinTour

############################################################################################


    # Lettura file
nodi, punteggi, deposito, cost_limit = lettura_file_OP("Orienteering\eil51_gen2.txt")
V = list(nodi.keys())
E = [(i, j) for i in V for j in V if i != j]

    # Calcolo distanze
c = {(i, j): distanza_euclidea(nodi[i][0],nodi[i][1],nodi[j][0],nodi[j][1]) for i, j in E}
p = punteggi
s = t = deposito  # partenza e arrivo coincidono (tour chiuso)

    # Modello
model = gp.Model("Orienteering")

    # Variabili
x = model.addVars(E, vtype=GRB.BINARY, name="x")  # arco usato
y = model.addVars(V, vtype=GRB.BINARY, name="y")  # nodo visitato
u = model.addVars(V, vtype=GRB.CONTINUOUS, lb=1, ub=len(V), name="u")  # MTZ
model.addConstr(u[s] == 1)  # Punto di partenza ha livello 0

    # Obiettivo: massimizzare profitto
model.setObjective(gp.quicksum(p[i] * y[i] for i in V), GRB.MAXIMIZE)  

    # Vincoli: partenza/arrivo
model.addConstr(gp.quicksum(x[s, j] for j in V if j != s) == 1)
model.addConstr(gp.quicksum(x[i, t] for i in V if i != t) == 1)

    # Flusso in = flusso out per nodi visitati
for k in V:
    if k != s:
        model.addConstr(
            gp.quicksum(x[i, k] for i in V if i != k) ==
            gp.quicksum(x[k, j] for j in V if j != k)
        )
        model.addConstr(
            gp.quicksum(x[i, k] for i in V if i != k) == y[k]
        )

    # Budget massimo
model.addConstr(gp.quicksum(c[i, j] * x[i, j] for i, j in E) <= cost_limit)

# Subtour elimination (MTZ)  APPLICAZIONE A TUTTI I NODI DEI VINCOLI MTZ
for i in V:
    for j in V:
        if i!=j and j!=1:
            model.addConstr(u[j]-u[i]>=1-len(V)*(1-x[i,j]))


    # Il deposito è sempre visitato
model.addConstr(y[s] == 1)
model.setParam("TimeLimit", 60)
model.optimize()


# PROVA CON ROW GEN
############################################################################################
stop = False
while stop==False:
    model.optimize()
    SOL = []
    for (i,j) in x :
        if x[i,j].X > 0.5 :
            SOL.append((i,j))
                
    feasible, Tour = LookForMinSubTour(SOL, nodi, s)
        
    if feasible :
        stop = True 
    else:  
        model.addConstr(gp.quicksum(x[i,j] for i in Tour for j in Tour if i != j) <= len(Tour) -1)
        print(Tour)

############################################################################################


#LAZY CONSTRAINTS
model._x=x
model.Params.LazyConstraints = 1  #ABILITA LA LAZY CONSTRAINTS
model.optimize(GeneraLazyConstr)


#################################################


    # Output
if model.SolCount > 0:
    selected_edges = [(i, j) for (i, j) in E if x[i, j].X > 0.5]
    selected_nodes = [i for i in V if y[i].X > 0.5]
    # print(selected_nodes)
    print(selected_edges)
    print(model.ObjVal)
else:
    print("Nessuna soluzione ottimale trovata.")

