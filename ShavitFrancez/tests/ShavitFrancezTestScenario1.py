import os
import sys
import time

sys.path.insert(0, os.getcwd())

import networkx as nx
import matplotlib.pyplot as plt
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from ShavitFrancez.ShavitFrancezImplementation.ShavitFrancez import ShavitFrancezComponentModel, ShavitFrancezEventTypes


def create_undirected_ring():
    undirectedRing = nx.Graph() # initialize the empty graph
    # add three nodes to the graph named as p, q, r
    undirectedRing.add_node(1)
    undirectedRing.add_node(2)
    # crate an undirecred ring from three of the nodes
    undirectedRing.add_edge(1, 2)

    # nx.draw(undirectedRing, with_labels=True, font_weight='bold')
    # plt.draw()
    # plt.show()

    return undirectedRing


def main():
    setAHCLogLevel(INFO)
    undirectedRing = create_undirected_ring()
    topology = Topology()
    topology.construct_from_graph(undirectedRing, ShavitFrancezComponentModel, GenericChannel)
    topology.start()
    time.sleep(10)
    components = list(topology.nodes.values())
    components[0].termination_initiators.append(components[0].componentinstancenumber)
    components[1].termination_initiators.append(components[0].componentinstancenumber)
    components[0].send_self(Event(components[0], ShavitFrancezEventTypes.DETECTTERMINATION, eventcontent="Initiator"))   
    components[0].send_self(Event(components[0], ShavitFrancezEventTypes.SENDBASICMESSAGE, None))
    components[1].send_self(Event(components[1], ShavitFrancezEventTypes.SENDBASICMESSAGE, None))
    components[0].send_self(Event(components[0], ShavitFrancezEventTypes.BECOMEPASSIVE, eventcontent="PASSIVE"))
    time.sleep(10)
    components[1].send_self(Event(components[1], ShavitFrancezEventTypes.BECOMEPASSIVE, eventcontent="PASSIVE"))
    time.sleep(20)
    topology.exit()
if __name__ == "__main__":
    exit(main())