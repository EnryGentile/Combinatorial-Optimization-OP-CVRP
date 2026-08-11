import math
import random
import matplotlib.pyplot as plt
import random

class nodo(object):
    def __init__(self,index):
        self._index = index
        self._X = 0
        self._Y = 0
        self._richiesta = 0

    def setX(self,X):
        self._X = X
    
    def setY(self,Y):
        self._Y = Y

    def setRichiesta(self,ric):
        self._richiesta = ric  

    def getX(self):
        return self._X
    
    def getY(self):
        return self._Y
    
    def getRichiesta(self):
        return self._richiesta
    
    def getIndex(self):
        return self._index
    
class Cluster(object):
    def __init__(self,deposito):
        self._domandaMax = 0
        self._costoPercorso = 0
        self._ClusterNodi = []
        self._ClusterNodi.append(deposito)

    def reset_Costo(self):
        self._costoPercorso = 0

    def setNodo(self,nuovo_nodo):
        self._ClusterNodi.append(nuovo_nodo)
        self._domandaMax += nuovo_nodo.getRichiesta()

    def setcostoPercorso(self,costo):
        self._costoPercorso += costo

    def getCostoPercorso(self):
        return self._costoPercorso
    
    def getDimNodi(self):
        return len(self._ClusterNodi)
    
    def getNodo(self,index):
        if index < len(self._ClusterNodi):
            return self._ClusterNodi[index]
        
    def getDomandaTotale(self):
        richiesta_max = 0
        for nodo in self._ClusterNodi:
            richiesta_max += nodo.getRichiesta()

        return richiesta_max
        
    def getCostoRitorno(self):
        return distanza_euclidea(self._ClusterNodi[len(self._ClusterNodi)-1].getX(), self._ClusterNodi[len(self._ClusterNodi)-1].getY(),
                                 self._ClusterNodi[0].getX(), self._ClusterNodi[0].getY())
    
    def getCostoArrivo(self):
        return distanza_euclidea(self._ClusterNodi[0].getX(), self._ClusterNodi[0].getY(), self._ClusterNodi[1].getX(), self._ClusterNodi[1].getY())
    
def distanza_euclidea(x1,y1,x2,y2): 
    return round(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))

def lettura_problema(path_problem_file):
    with open(path_problem_file,"r") as file:
        righe=file.readlines()
    nodi=[]    
    veicoli = None 
    depositi=1
    capacita=None

    sezione = None
    for riga in righe:
        riga = riga.strip()
        if riga.startswith("CAPACITY"):
            sezione = "capacita" 
        if riga.find("COMMENT") != -1:
            inizio = riga.find("Min no of trucks:") + len("Min no of trucks:")
            resto = riga[inizio:].strip()
            numero_str = resto.split(",")[0].strip()
            veicoli = int(numero_str)
            continue
        if riga == "NODE_COORD_SECTION":
            sezione = "coordinate"      
            continue
        elif riga == "DEMAND_SECTION":
            sezione = "domande"         
            continue
        elif riga == "DEPOT_SECTION":
            sezione = "deposito"        
            continue
        elif riga == "EOF":
            break                     

        if sezione == "coordinate":             
            riga_splittata = riga.split()     
            curr_nodo = nodo(float(riga_splittata[0]))
            curr_nodo.setX(float(riga_splittata[1]))
            curr_nodo.setY(float(riga_splittata[2]))
            nodi.append(curr_nodo)

        elif sezione == "domande":
            riga_splittata = riga.split()
            id_nodo = int(riga_splittata[0])
            domanda = int(riga_splittata[1])
            nodi[id_nodo-1].setRichiesta(domanda)

        elif sezione == "deposito":
            if int(riga) != -1:         
                depositi = int(riga)

        elif sezione == "capacita":
            riga_splittata = riga.split()
            capacita=int(riga_splittata[2])
        
    return nodi, veicoli, capacita, depositi

def matrice_vicinanze(cluster):
    vicinanze = {}
    nodi = [cluster.getNodo(i) for i in range(cluster.getDimNodi())]

    for nodo_i in nodi:
        id_i = nodo_i.getIndex() 
        distanze = []
        for nodo_j in nodi:
            id_j = nodo_j.getIndex()
            if id_i != id_j:
                d = distanza_euclidea(nodo_i.getX(), nodo_i.getY(), nodo_j.getX(), nodo_j.getY())
                distanze.append((id_j, d))
        # Ordina per distanza crescente
        distanze.sort(key=lambda x: x[1])
        vicinanze[id_i] = distanze

    return vicinanze

def ottimizzazione_cluster_vicini(cluster):

    cluster_ott = Cluster(cluster.getNodo(0))
    visitati = set()

    vicini = matrice_vicinanze(cluster)
    
    nodo_corrente = cluster.getNodo(0)
    visitati.add(nodo_corrente.getIndex())

    for _ in range(1, cluster.getDimNodi()):
        id_corrente = nodo_corrente.getIndex()
        vicini_corrente = vicini[id_corrente]

        for id_vicino, _ in vicini_corrente:
            if id_vicino not in visitati:
                for i in range(cluster.getDimNodi()):
                    nodo = cluster.getNodo(i)
                    if nodo.getIndex() == id_vicino:
                        cluster_ott.setNodo(nodo)
                        nodo_corrente = nodo
                        visitati.add(id_vicino)
                        break
                break  

    return cluster_ott

def costo_clusters(cluster):
    cluster.reset_Costo()
    for i in range (cluster.getDimNodi()):
        nodo = cluster.getNodo(i)
        if i == cluster.getDimNodi() - 1:
            nodo_succ = cluster.getNodo(0)
        else:
            nodo_succ = cluster.getNodo(i+1)
        cluster.setcostoPercorso(distanza_euclidea(nodo.getX(), nodo.getY(), nodo_succ.getX(), nodo_succ.getY()))

def ottimizzazione_cluster_2opt(cluster):
    best_cost = cluster.getCostoPercorso()
    miglioramento = True

    while miglioramento:
        miglioramento = False
        dim = cluster.getDimNodi()

        for i in range(1, dim - 1):
            for j in range(i + 1, dim - 1):
                nuovi_nodi = cluster._ClusterNodi[:i] + cluster._ClusterNodi[i:j+1][::-1] + cluster._ClusterNodi[j+1:]

                nuovo_cluster = Cluster(nuovi_nodi[0])
                for nodo in nuovi_nodi[1:]:
                    nuovo_cluster.setNodo(nodo)

                # Calcoliamo il costo del nuovo cluster
                nuovo_cluster.reset_Costo()
                costo_clusters(nuovo_cluster)
                nuovo_costo = nuovo_cluster.getCostoPercorso()

                if nuovo_costo < best_cost:
                    cluster._ClusterNodi = nuovi_nodi
                    cluster.reset_Costo()
                    costo_clusters(cluster)
                    best_cost = nuovo_costo
                    miglioramento = True
                    break
            if miglioramento:
                break

    return cluster

def Fusione_cluster(cluster1,cluster2,capacità_max):

    cluster_new = None
    
    domanda_totale = cluster1.getDomandaTotale() + cluster2.getDomandaTotale()
    if domanda_totale > capacità_max:
        return None

    cluster_new = Cluster(cluster1.getNodo(0))
    for i in range(1, cluster1.getDimNodi()):
        cluster_new.setNodo(cluster1.getNodo(i))
    for i in range(1, cluster2.getDimNodi()):
        cluster_new.setNodo(cluster2.getNodo(i))

    #ottimizzazione_cluster_vicini(cluster_new)
    #ottimizzazione_cluster_2opt(cluster_new)
    costo_clusters(cluster_new)
    
    return cluster_new

def calcola_savings_greedy(clusters):
    savings = []
    depot = clusters[0].getNodo(0)

    n = len(clusters)
    for i in range(n):
        for j in range(i+1, n):
            nodo_i = clusters[i].getNodo(clusters[i].getDimNodi()-1)  
            nodo_j = clusters[j].getNodo(1)

            dist_i_depot = distanza_euclidea(nodo_i.getX(), nodo_i.getY(), depot.getX(), depot.getY())
            dist_depot_j = distanza_euclidea(depot.getX(), depot.getY(), nodo_j.getX(), nodo_j.getY())
            dist_i_j = distanza_euclidea(nodo_i.getX(), nodo_i.getY(), nodo_j.getX(), nodo_j.getY())

            #saving: quanto guadagno aggiungengo il nuovo collegamento rispetto ai due vecchi
            saving = dist_i_depot + dist_depot_j - dist_i_j

            domanda_i = clusters[i].getDomandaTotale()
            domanda_j = clusters[j].getDomandaTotale()

            # Cost: distanza i-j pesata per domanda
            costo = dist_i_j * (domanda_i + domanda_j)

            if costo != 0:
                ratio = saving / costo
            else:
                ratio = float('inf')  # priorità assoluta

            savings.append((i, j, ratio))

    # ordina savings in ordine decrescente di saving
    savings.sort(key=lambda x: x[2], reverse=True)
    return savings

def calcola_savings(clusters):
    savings = []
    depot = clusters[0].getNodo(0)

    n = len(clusters)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            
            nodo_i = clusters[i].getNodo(clusters[i].getDimNodi()-1)  
            nodo_j = clusters[j].getNodo(1)

            dist_i_depot = distanza_euclidea(nodo_i.getX(), nodo_i.getY(), depot.getX(), depot.getY())
            dist_depot_j = distanza_euclidea(depot.getX(), depot.getY(), nodo_j.getX(), nodo_j.getY())
            dist_i_j = distanza_euclidea(nodo_i.getX(), nodo_i.getY(), nodo_j.getX(), nodo_j.getY())

            saving = dist_i_depot + dist_depot_j - dist_i_j
            savings.append((i, j, saving))

    # ordina savings in ordine decrescente di saving
    savings.sort(key=lambda x: x[2], reverse=True)
    return savings

def ottimizzazione_soluzione(soluzione):
    for i in range (len(soluzione)):
        #cluster_ott = ottimizzazione_cluster_vicini(soluzione[i])
        cluster_ott = ottimizzazione_cluster_2opt(soluzione[i])
        costo_clusters(cluster_ott)
        soluzione[i] = cluster_ott

    return soluzione

def Clark_and_Wright(nodi, veicoli, capacità_Max, deposito):

    clusters = []
    for nodo in nodi:
        cluster = Cluster(deposito)
        cluster.setNodo(nodo)
        costo_clusters(cluster)
        clusters.append(cluster)

    savings = calcola_savings(clusters)

    while len(clusters) > veicoli:
        if not savings:
            break 

        i, j, best_saving = savings[0]

        cluster_i = clusters[i]
        cluster_j = clusters[j]
        cluster_new = Fusione_cluster(cluster_i, cluster_j, capacità_Max)

        if cluster_new != None:
            clusters.pop(max(i, j))
            clusters.pop(min(i, j))
            clusters.append(cluster_new)
            savings = calcola_savings(clusters)
        else:
            savings.pop(0)
            if not savings:
                break

    ottimizzazione_soluzione(clusters)
    return clusters

def Costo_Soluzione(soluzione):
    costo_totale = 0
    for cluster in soluzione:
        costo_totale += cluster.getCostoPercorso()

    return costo_totale
        
def plot_soluzione(clusters, deposito):
    plt.figure(figsize=(10,8))

    # Plotto deposito
    plt.scatter(deposito.getX(), deposito.getY(), c='red', marker='s', s=100, label='Deposito')

    colors = plt.cm.get_cmap('tab20', len(clusters))  # palette di colori

    for i, cluster in enumerate(clusters):
        x = [nodo.getX() for nodo in cluster._ClusterNodi]
        y = [nodo.getY() for nodo in cluster._ClusterNodi]

        # Per chiudere il ciclo nel percorso torno al deposito (primo nodo)
        x.append(cluster._ClusterNodi[0].getX())
        y.append(cluster._ClusterNodi[0].getY())

        plt.plot(x, y, color=colors(i), marker='o', label=f'Veicolo {i+1} - Domanda: {cluster.getDomandaTotale()}')

        # Etichette nodi (opzionale)
        for nodo in cluster._ClusterNodi:
            plt.text(nodo.getX(), nodo.getY(), str(int(nodo.getIndex())), fontsize=8)

    plt.title("Soluzione Clark & Wright - VRP")
    plt.xlabel("Coordinata X")
    plt.ylabel("Coordinata Y")
    plt.legend()
    plt.grid(True)
    plt.savefig("plot.png", dpi=300)
    plt.show()
    
def main():
    nodi, veicoli, capacità, depositi = lettura_problema("E-n101-k14.txt")
    deposito = []
    for i in range(depositi):
        deposito.append(nodi.pop(i))

    soluzione = Clark_and_Wright(nodi,veicoli,capacità, deposito[0])
    risultato_soluzione = Costo_Soluzione(soluzione)

    print(f"Numero Veicoli: {veicoli}")
    print(f"Capacità Veicoli: {capacità}")

    print(f"soluzione trovata con {len(soluzione)} veicoli: \nValore ottenuto: {risultato_soluzione}")
    for i in range(len(soluzione)):
        print(f"domanda rispettata dal {i}-esimo cluster: {soluzione[i].getDomandaTotale()}")



    # Aggiungo la visualizzazione
    plot_soluzione(soluzione, deposito[0])



    #PARTE CHE PRINTA COME SONO COMPOSTE LE VARIE LISTE
    # print("\nDepositi:")

    # for i in range(len(deposito)):
    #     print(f"\n{deposito[i].getIndex()}, {deposito[i].getX()}, {deposito[i].getY()}, {deposito[i].getRichiesta()}")

    # print("-----------------------------------\nClienti")

    # for i in range(len(nodi)):
    #     print(f"\n{nodi[i].getIndex()}, {nodi[i].getX()}, {nodi[i].getY()}, {nodi[i].getRichiesta()}")

if __name__ == "__main__":
    main()
