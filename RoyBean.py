import networkx as nx
import random
from random import uniform
import pickle
import copy
import numpy as np

# input: distance (m); output: transmission (watt)
# According to CC2420 stats
def PowerforDist( d ):
    return np.sqrt(d)

# Generate a mac layer topology with given number of nodes
def BuildPHYTopology( n ):
    G = nx.Graph()
    
    # add sensor nodes and data sink
    for index in range(1,n):
        x = uniform(0, TotalLen)
        G.add_node(index, loc=x, battery=Battery)
    G.add_node(0,loc=0,battery=0)   

    # add edges
    for i in range(n):
        for j in range(i+1,n):
            dist = G.node[i]['loc']-G.node[j]['loc'] 
            dist = abs(dist)
            intendPow = PowerforDist(dist)
            if intendPow <= MaxPower:
                G.add_edge(i, j, weight = intendPow, flow = 0)
    return G

# Generate a directional initial overaly based on shortest path on the PHY topology
def BuildOverlay( P ):
    G = nx.DiGraph()    # resulting topology
    G.add_nodes_from(P.nodes(data=True))
    n = len(P.node)
    # from data sink to every other node
    path = nx.shortest_path(P,source = 0, weight='weight')
    #print (path);
    for i in P.nodes():
        pLen = len(path[i])
        for j in range (1,pLen): # notice that the direction is in reverse order
            a = path[i][j]
            b = path[i][j-1]
            if (a,b) in G.edges():
                G.edge[a][b]['flow']+=1
            else:
                G.add_edge(a, b, weight=P[a][b]['weight'], flow=1)

    return G
    
# Update the topology
def Update( G, P ):
    G = BuildOverlay( P )
    n = len(G.nodes())
    # consume battery
    for i in G.nodes():
        if i == 0:          # skip the sink
            continue
        for j in G.edge[i]:
            G.node[i]['battery'] -= G.edge[i][j]['weight'] * G.edge[i][j]['flow']
            P.node[i]['battery'] = G.node[i]['battery'] 
            if G.node[i]['battery'] < 0:
                print('battery:',G.node[i]['battery'])
                print('*****Delete node ',i,' *****')
                P.remove_node(i)
                break
    return (G,P)

# Discrete event simulation
# P and G should both be connected
def Simulation():
    while True:
        PHYTopology = BuildPHYTopology(NodeNum) 
        if nx.is_connected(PHYTopology):
            break
    G = BuildOverlay( PHYTopology )
    for time in range(1, MaxTime):
        print('====== Time ',time  ,'========')
        print(PHYTopology.nodes(data=True))
        print('---------------')
        print(G.nodes(data=True))
        print(G.edges(data=True))
        if not nx.is_connected(PHYTopology):
            break
        (G,PHYTopology) = Update(G,PHYTopology)
    return G

# Constants
NodeNum = 10                    # number of nodes
TotalLen = 1000                 # length of the whole area
Battery = 100                   # battery capacity
MaxPower = 20                   # max transmission power
MaxTime = 100                   # simulation duration                    
Simulation()

