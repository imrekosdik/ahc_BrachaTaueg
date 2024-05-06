import os
import sys
import time

sys.path.insert(0, os.getcwd())

import networkx as nx
import matplotlib.pyplot as plt
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from ShavitFrancez.ShavitFrancez.ShavitFrancez import ShavitFrancezComponentModel, ShavitFrancezEventTypes


def visualize_graph(G):
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.draw()
    plt.show()


def generate_complete_topology(node_count, component_model, channel_type):
    topology = Topology()
    G = nx.complete_graph(node_count)
    topology.construct_from_graph(G, component_model, channel_type)
    # visualize_graph(G)
    return topology


def generate_ring_topology(node_count, component_model, channel_type):
    topology = Topology()
    G = nx.cycle_graph(node_count)
    topology.construct_from_graph(G, component_model, channel_type)
    # visualize_graph(G)
    return topology
    