from adhoccomputing.GenericModel import GenericModel
from enum import Enum
from adhoccomputing.Generics import *

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
        self.eventhandlers[BrachaTouegEventTypes.DETECTDEADLOCK] = self.detect_deadlock
        
    


