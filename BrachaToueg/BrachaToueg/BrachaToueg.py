from adhoccomputing.Experimentation.Topology import *
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessage
from enum import Enum
from adhoccomputing.Generics import *
from adhoccomputing.DistributedAlgorithms.Snapshot.Snapshot import LaiYangComponentModel
from adhoccomputing.DistributedAlgorithms.Snapshot.Snapshot import SnapshotEventTypes

class BrachaTouegEventTypes(Enum):
    DETECTDEADLOCK = "DETECTDEADLOCK"


class BrachaTouegMessageTypes(Enum):
    ACKNOWLEDGE = "ACKNOWLEDGE"
    DONE = "DONE"
    NOTIFY = "NOTIFY"
    GRANT = "GRANT"
    

class BrachaTouegComponentModel(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None, child_conn=None, node_queues=None, channel_queues=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology, child_conn, node_queues, channel_queues)
        self.eventhandlers[BrachaTouegEventTypes.DETECTDEADLOCK] = self.on_receiving_detect_deadlock
        self.snapshotModel = LaiYangComponentModel(self.componentname, self.componentinstancenumber)

    def on_receiving_detect_deadlock(self, eventobj: Event):
        self.snapshotModel.take_snapshot(Event(self, SnapshotEventTypes.TS, None))
        snapshot = self.snapshotModel
        print(snapshot.sent)
