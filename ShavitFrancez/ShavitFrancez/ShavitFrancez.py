from adhoccomputing.Experimentation.Topology import *
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessage
from enum import Enum
from adhoccomputing.Generics import *
from adhoccomputing.DistributedAlgorithms.Waves.TreeAlgorithm import TreeNode


class ShavitFrancezEventTypes(Enum):
    DETECTTERMINATION = "DETECTTERMINATION"
    
class ShavitFrancezMessageTypes(Enum):
    ACKNOWLEDGE = "ACKNOWLEDGE"
    BASICMESSAGE = "BASICMESSAGE"
    PASSIVE = "PASSIVE"

class ShavitFrancezComponentModel(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None, child_conn=None, node_queues=None, channel_queues=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology, child_conn, node_queues, channel_queues)
        # event that triggers the initiation of the termination detection algorithm
        self.eventhandlers[ShavitFrancezEventTypes.DETECTTERMINATION] = self.on_receiving_detect_termination 
        self.eventhandlers["passive"] = self.on_receiving_passive
        self.treeNode = None
        self.is_active = False; # states whether the process is active
        self.parent = None; # if another process makes the process active, that process becomes the parent of the process
        self.number_of_children = 0 # keeps track of the number of children of a process
        self.neighbors = [] # consists of component instance numbers


    def on_init(self, eventobj: Event):
        self.treeNode = TreeNode(self.componentname, self.componentinstancenumber)
        logger.info(f"Initializing the iniator {self.componentname}.{self.componentinstancenumber} with its treeNode")


    # Only the initiator node can start the termination algorithms   
    def on_receiving_detect_termination(self, eventobj: Event):
        logger.info(f"Initiator {self.componentname}.{self.componentinstancenumber} started termination detection algorithm by sending basic messages to its neighbors")
        self.is_active = True
        self.parent = self.componentinstancenumber
        self.send_basic_message()
    

    def generateMessage(self, messagetype, messageto):
        header = GenericMessageHeader(messagetype, self.componentinstancenumber, messageto)
        return GenericMessage(header, GenericMessagePayload(self.componentinstancenumber))


    def send_basic_message(self):
        self.number_of_children += 1
        self.send_down(Event(self, EventTypes.MFRT, self.generateMessage(ShavitFrancezMessageTypes.BASICMESSAGE, None), None))
        logger.info("processing PASSIVE message")
        self.send_self(Event(self, "passive", self.generateMessage(ShavitFrancezMessageTypes.PASSIVE, self), None))


    def on_message_from_bottom(self, eventobj: Event):
        try:
            message = eventobj.eventcontent.header.messagetype 
            if message == ShavitFrancezMessageTypes.ACKNOWLEDGE:
                logger.info("processing ACKNOWLEDGE message")
                self.on_receiving_acknowledge(eventobj)
            elif message == ShavitFrancezMessageTypes.BASICMESSAGE:
                logger.info("processing BASICMESSAGE message")
                self.on_receiving_basic_message(eventobj)
        except AttributeError:
            logger.error("Attribute Error")
   

    def on_receiving_passive(self, eventobj: Event):
        self.is_active = False
        logger.info(f"{self.componentname}.{self.componentinstancenumber} received passive message and became passive")
        self.leave_tree()


    def on_receiving_acknowledge(self, eventobj: Event):
        logger.info(f"{self.componentname}.{self.componentinstancenumber} received acknowledge from {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
        self.number_of_children -= 1
        logger.info(f"call leave tree for {self.componentname}.{self.componentinstancenumber}")
        self.leave_tree()  
    

    def on_receiving_basic_message(self, eventobj: Event):
        if not self.is_active:
            self.is_active = True
            self.parent = eventobj.eventsource_componentinstancenumber  
            self.send_down(Event(self, EventTypes.MFRT, self.generateMessage(ShavitFrancezMessageTypes.BASICMESSAGE, None), None))
            logger.info(f"{self.componentname}.{self.componentinstancenumber} received a basic message from {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber} making its parent {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
        else:
            self.send_down(Event(self, EventTypes.MFRT, self.generateMessage(ShavitFrancezMessageTypes.ACKNOWLEDGE, None)))
            logger.info(f"{self.componentname}.{self.componentinstancenumber} received a basic message from {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
            logger.info(f"{self.componentname}.{self.componentinstancenumber} sends acknowledge to {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")


    def leave_tree(self):  
        logger.info(f"parent of {self.componentname}.{self.componentinstancenumber} is {self.parent} and number of children is {self.number_of_children}")
        if not self.is_active and self.number_of_children == 0:
            logger.info(f"Leave tree procedure started for {self.componentname}.{self.componentinstancenumber}")
            if self.parent is not None:
                self.send_down(Event(self, EventTypes.MFRT, self.generateMessage(ShavitFrancezMessageTypes.ACKNOWLEDGE, None)))
                self.parent = None
            else:
                logger.info(f"{self.componentname}.{self.componentinstancenumber} do not have parent, starts a wave")
                self.treeNode.startTreeAlgorithm()