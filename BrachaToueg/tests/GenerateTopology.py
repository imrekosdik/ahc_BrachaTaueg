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

import networkx as nx
import random

def all_cycles_complete_graph(n):
    G = nx.complete_graph(n)
    cycles = list(nx.simple_cycles(G))
    unique_cycles = set(frozenset(cycle) for cycle in cycles)
    return G, [set(cycle) for cycle in unique_cycles]


def generate_complete_graph_with_random_cycle(node_count, component_model, channel_type):
    topology = Topology()
    G, cycles = all_cycles_complete_graph(node_count)
    random_cycle = random.choice(cycles)
    topology.construct_from_graph(G, component_model, channel_type)
    return topology, list(random_cycle)


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
    