import os
import sys
import time

sys.path.insert(0, os.getcwd())

import networkx as nx
import matplotlib.pyplot as plt
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from BrachaToueg.BrachaToueg.BrachaToueg import BrachaTouegComponentModel, BrachaTouegEventTypes


def create_undirected_ring():
    undirectedRing = nx.Graph() # initialize the empty graph
    # add three nodes to the graph named as p, q, r
    undirectedRing.add_node(1)
    undirectedRing.add_node(2)
    undirectedRing.add_node(3)
    # crate an undirecred ring from three of the nodes
    undirectedRing.add_edge(1, 2)
    undirectedRing.add_edge(2, 3)
    undirectedRing.add_edge(1, 3)

    # nx.draw(undirectedRing, with_labels=True, font_weight='bold')
    # plt.draw()
    # plt.show()

    return undirectedRing


def main():
    setAHCLogLevel(INFO)
    undirectedRing = create_undirected_ring()
    topology = Topology()
    topology.construct_from_graph(undirectedRing, BrachaTouegComponentModel, GenericChannel)
    topology.start()
    time.sleep(5)
    components = list(topology.nodes.values())
    time.sleep(10)
    components[0].send_request_to_component(components[1])
    components[1].send_request_to_component(components[2])
    components[2].send_request_to_component(components[0])
    time.sleep(10)
    components[0].send_self(Event(components[0], BrachaTouegEventTypes.DETECTDEADLOCK, eventcontent="Initiator"))   
    
    time.sleep(60)
if __name__ == "__main__":
    exit(main())