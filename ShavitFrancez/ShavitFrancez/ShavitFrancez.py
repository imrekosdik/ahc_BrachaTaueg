from adhoccomputing.Experimentation.Topology import Event
from adhoccomputing.GenericModel import GenericModel
from enum import Enum
from adhoccomputing.Generics import *
from adhoccomputing.Generics import Event
from adhoccomputing.DistributedAlgorithms.Waves.TreeAlgorithm import TreeNode

class ShavitFrancezEventTypes(Enum):
    DETECTTERMINATION = "DETECTTERMINATION"

class ShavitFrancezMessageTypes(Enum):
    ACKNOWLEDGE = "ACKNOWLEDGE"

class TreeEventTypes(Enum):
    STARTWAVE = "STARTVAWE"
    DECIDE = "DECIDE"

class TreeMessageTypes(Enum):
    WAVE = "WAVE"
    INFO = "INFO"

class ShavitFrancezComponentModel(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None, child_conn=None, node_queues=None, channel_queues=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology, child_conn, node_queues, channel_queues)
        # event that triggers the initiation of the termination detection algorithm
        self.eventhandlers[ShavitFrancezEventTypes.DETECTTERMINATION] = self.on_receiving_detect_termination 
        # event that triggers the initiation of the Tree Wave algorithm
        self.eventhandlers[TreeEventTypes.STARTWAVE] = self.on_receiving_start_wave
        # self.eventhandlers[TreeEventTypes.DECIDE] = self.on_receiving_decide
        
        # attributes related with the termination detection
        self.is_active = False; # states whether the process is active
        self.parent = None; # if another process makes the process active, that process becomes the parent of the process
        self.number_of_children = 0 # keeps track of the number of children of a process

        # attributes related with the wave algorithm
        self.received_wave = dict() # keys are the neighboring components and values are boolean
        self.neighbors = [] # consists of component instance numbers
        self.wave_parent = None
        
        
    def on_connected_to_component(self, name, channel):
        super().on_connected_to_component(name, channel)
        self.neighbors.append(channel.componentinstancenumber)
        self.received_wave[channel.componentinstancenumber] = False
    
    def on_receiving_detect_termination(self, eventobj: Event):
        self.is_active = True
        self.send_basic_message()

    def send_basic_message(self):
        self.number_of_children += 1
        self.send_down(Event(self, EventTypes.MFRT, None))
        self.send_self(Event(self, EventTypes.MFRP, None))
    
    # state transition from ACTIVE to PASSIVE after sending BASIC message
    def on_message_from_peer(self, eventobj: Event):
        self.is_active = False
        self.leave_tree()

    # receiving BASIC message
    def on_message_from_bottom(self, eventobj: Event):
        if not self.is_active:
            self.is_active = True
            self.parent = eventobj.eventsource
        else:
            ack_message = GenericMessage(
                GenericMessageHeader(ShavitFrancezMessageTypes.ACKNOWLEDGE, self, eventobj.eventsource),
                None)
            self.send_up(Event(self, EventTypes.MFRB, ack_message))
    
    # receiving ACKNOWLEGE message
    def on_message_from_top(self, event: Event):
        self.number_of_children -= 1
        self.leave_tree()
    
    def leave_tree(self):
        if not self.is_active and self.number_of_children == 0:
            if self.parent is not None:
                ack_message = GenericMessage(
                GenericMessageHeader(ShavitFrancezMessageTypes.ACKNOWLEDGE, self, self.parent),
                None)
                self.send_up(Event(self, EventTypes.MFRP, ack_message))
                self.parent = None
            else:
                for neighbor in self.neighbors:
                    self.send_wave(neighbor) # not sure about that TBD
    
    def on_receiving_start_wave(self, event : Event):
        if not self.is_active and self.number_of_children == 0:
            self.received_wave[event.eventsource_componentinstancenumber] = True
            self.send_wave(self, event.eventsource_componentinstancenumber)
            if event.eventcontent == TreeEventTypes.DECIDE:
                pass # call Announce - not sure about that TBD

    def send_wave(self, component_instance_number):
        # Each agent u can send only one message. Moreover, it can do it only when either 
        # 1. it has received a message from each of its neighbors except one denoted by v or 
        # 2. it has received a message from all its neighbors.        
        is_received_from_all_except_one = False
        is_received_from_all = False
        received_counter = 0
        for neighbor in self.neighbors:
            if self.received_wave[neighbor]:
                received_counter += 1
            if neighbor == component_instance_number and not self.received_wave[neighbor]:
                if received_counter == self.neighbors.count - 1:
                    is_received_from_all_except_one = True
                    break

        if received_counter == self.neighbors.count:
            is_received_from_all = True
        
        # send wave to the neighbor that the component received a wave message from
        if is_received_from_all_except_one: 
            wave_message = GenericMessage(
                GenericMessageHeader(TreeMessageTypes.WAVE, self.componentinstancenumber, component_instance_number),
                None)
            self.send_down(Event(self, EventTypes.MFRP, wave_message))
            self.wave_parent = component_instance_number
        # send info to all of component's neighbors except its parent
        elif is_received_from_all:
            self.send_down(Event(self, TreeEventTypes.DECIDE, None))
            for neighbor in self.neighbors:
                if self.wave_parent != neighbor: 
                    info_message = GenericMessage(
                        GenericMessageHeader(TreeMessageTypes.INFO, self.componentinstancenumber, neighbor),
                        None)
                    self.send_down(Event(self, EventTypes.MFRP, info_message))
