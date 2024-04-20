from adhoccomputing.Experimentation.Topology import *
from adhoccomputing.Experimentation.Topology import Event
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessage
from enum import Enum
from adhoccomputing.Generics import *


class ShavitFrancezEventTypes(Enum):
    DETECTTERMINATION = "DETECTTERMINATION" # event that triggers the termination detection algorithm
    STARTWAVE = "STARTWAVE" # event that triggers the wave algorithm
    BECOMEPASSIVE = "BECOMEPASSIVE" # event that makes an active process transition to passive state
    BECOMEACTIVE = "BECOMEACTIVE" # event that makes a passive process transition to active state
    
class ShavitFrancezMessageTypes(Enum):
    ACKNOWLEDGE = "ACKNOWLEDGE"
    BASICMESSAGE = "BASICMESSAGE"
    WAVE = "WAVE"

class ShavitFrancezComponentModel(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None, child_conn=None, node_queues=None, channel_queues=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology, child_conn, node_queues, channel_queues)

        self.eventhandlers[ShavitFrancezEventTypes.DETECTTERMINATION] = self.on_receiving_detect_termination 
        self.eventhandlers[ShavitFrancezEventTypes.BECOMEPASSIVE] = self.on_receiving_become_passive
        self.eventhandlers[ShavitFrancezEventTypes.BECOMEACTIVE] = self.on_receiving_become_active
        self.eventhandlers[ShavitFrancezEventTypes.STARTWAVE] = self.on_receiving_start_wave

        self.neighbors = []
        self.is_active = False
        self.termination_parent = None
        self.termination_initiators = []
        self.number_of_children = 0

        self.wave_parent = None
        self.wave_initiators = []
        self.number_of_received_wave_messages = 0


    def on_init(self, eventobj: Event):
        self.neighbors = self.connectors[ConnectorTypes.DOWN]
        logger.info(f"{self.componentname}.{self.componentinstancenumber} is initialized")
    
    
    def on_receiving_detect_termination(self, eventObj : Event):
        '''
        This method makes the proces receiving the DETECTTERMINATION event
        active and sets its parent to itself. Then it makes the process send
        basic messages to all of its neighbors.
        '''
        logger.info(f"Initiator {self.componentname}.{self.componentinstancenumber} started termination detection algorithm by sending basic messages to its neighbors")
        if not self.is_active:
            self.is_active = True
        self.termination_parent = self.componentinstancenumber
        self.termination_initiators.append(self)
        self.send_basic_message()


    def on_receiving_basic_message(self, eventobj: Event):
        '''
        This method makes the process receiving the basic message active if not already and sets its parent
        to the process sending the basic message. If the process was already active, then it sends an 
        acknowledge message to the process sending the basic message.
        '''
        if not self.is_active:
            logger.info(f"{self.componentname}.{self.componentinstancenumber} received a basic message from {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber} making its parent {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
            self.is_active = True
            self.parent = eventobj.eventsource_componentinstancenumber  
        else:
            logger.info(f"{self.componentname}.{self.componentinstancenumber} received a basic message from {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
            logger.info(f"{self.componentname}.{self.componentinstancenumber} sends acknowledge to {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
            self.send_down(Event(self, EventTypes.MFRT, self.generate_message(ShavitFrancezMessageTypes.ACKNOWLEDGE, eventobj.eventsource_componentinstancenumber)))
            

    def on_receiving_acknowledge_message(self, eventobj: Event):
        '''
        This method decreases the number of children of the process receiving 
        the acknowledge message by one and calls the leave tree procedure for it.
        '''
        logger.info(f"{self.componentname}.{self.componentinstancenumber} received acknowledge from {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
        self.number_of_children -= 1
        logger.info(f"{self.componentname}.{self.componentinstancenumber} calls the Leave Tree procedure.")
        self.leave_tree()  


    def on_receiving_become_active(self, eventobj: Event):
        if not self.is_active:
            self.is_active = True
        self.send_basic_message()


    def on_receiving_become_passive(self, eventobj: Event):
        if self.is_active:
            self.is_active = False
        self.leave_tree()


    def on_receiving_start_wave(self, eventobj: Event):
        '''
        This method implements the Echo algorithm on processes that
        are currently not active and do not have any children.
        '''
        if self.is_active == False and self.number_of_children == 0: 
            self.number_of_received_wave_messages += 1
            if self.wave_parent is None and self not in self.wave_initiators:
                self.wave_parent = eventobj.eventsource_componentinstancenumber
                if len(self.neighbors) > 1:
                    for neighbor in self.neighbors:
                        if neighbor.componentinstancenumber != self.wave_parent:
                            self.send_down(Event(self, ShavitFrancezEventTypes.STARTWAVE, self.generate_message(ShavitFrancezMessageTypes.WAVE, neighbor.componentinstancenumber)))
                        else:
                            self.send_down(Event(self, ShavitFrancezEventTypes.STARTWAVE, self.generate_message(ShavitFrancezMessageTypes.WAVE, self.wave_parent)))
                elif len(self.neighbors) == self.number_of_received_wave_messages:
                    if self.wave_parent is not None:
                        self.send_down(Event(self, ShavitFrancezEventTypes.STARTWAVE, self.generate_message(ShavitFrancezMessageTypes.WAVE, self.wave_parent)))
                    else:
                        self.decide()


    def on_message_from_bottom(self, eventobj: Event):
        '''
        This method calls the related methods according to the message type of
        the MFRT event.
        '''
        try:
            message = eventobj.eventcontent.header.messagetype 
            if message == ShavitFrancezMessageTypes.ACKNOWLEDGE:
                logger.info(f"Processing ACKNOWLEDGE message received from {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
                self.on_receiving_acknowledge_message(eventobj)
            elif message == ShavitFrancezMessageTypes.BASICMESSAGE:
                logger.info(f"Processing BASICMESSAGE message received from {eventobj.eventsource_componentname}.{eventobj.eventsource_componentinstancenumber}")
                self.on_receiving_basic_message(eventobj)
        except AttributeError:
            logger.error("Attribute Error")
    
    
    def send_basic_message(self):
        '''
        This method increases the number of children of the process
        and makes the process send basic messages to its neighbors
        '''
        self.number_of_children += 1
        self.send_down(Event(self, EventTypes.MFRT, self.generate_message(ShavitFrancezMessageTypes.BASICMESSAGE, None), None))


    def send_wave_message(self):
        '''
        This method sends wave messages to the process' all its neighbors
        '''
        logger.info(f"{self.componentname}.{self.componentinstancenumber} sends wave messages to all of its neighbors")
        self.wave_initiators.append(self)
        self.send_down(Event(self, ShavitFrancezEventTypes.STARTWAVE, self.generate_message(ShavitFrancezMessageTypes.WAVE, None)))


    def generate_message(self, messagetype: any, messageto: any):
        header = GenericMessageHeader(messagetype, self.componentinstancenumber, messageto)
        return GenericMessage(header, GenericMessagePayload(self.componentinstancenumber))
    

    def leave_tree(self):
        '''
        This method checks if the process is not currenty active and does not have any children.
        According to that, if also the process has a parent, it sends acknowledge message to its
        parent and leaves the parent's tree. If the process does not have any parent, then it
        starts a wave.
        '''
        if not self.is_active and self.number_of_children == 0:
            logger.info(f"Leave tree procedure started for {self.componentname}.{self.componentinstancenumber}")
            if self.termination_parent is not None:
                self.send_down(Event(self, EventTypes.MFRT, self.generateMessage(ShavitFrancezMessageTypes.ACKNOWLEDGE, self.termination_parent)))
                self.termination_parent = None
            else:
                logger.info(f"{self.componentname}.{self.componentinstancenumber} do not have parent, starts a wave")
                self.send_wave_message()


    def decide(self):
        logger.info(f"{self.componentname}.{self.componentinstancenumber} decided and calls Announce.")
        self.announce()
    

    def announce(self):
        logger.info(f"{self.componentname}.{self.componentinstancenumber} announces Termination.")
