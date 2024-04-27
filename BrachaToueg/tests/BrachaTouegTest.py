import os
import sys
import time

sys.path.insert(0, os.getcwd())

from BrachaToueg.BrachaToueg.BrachaToueg import BrachaTouegEventTypes, Node
from adhoccomputing.Experimentation.Topology import *
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel


# Wrap Snapshot in a node model!
def main():
    setAHCLogLevel(DEBUG)
    topology = Topology()
    topology.construct_winslab_topology_with_channels(3, Node, GenericChannel)
    topology.start()
    time.sleep(1)
    components = list(topology.nodes.values())
    components[0].send_self(Event(components[0], BrachaTouegEventTypes.DETECTDEADLOCK, eventcontent="Initiator"))
    time.sleep(20)
    topology.exit()

if __name__ == "__main__":
    exit(main())