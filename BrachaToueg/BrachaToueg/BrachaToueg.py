from adhoccomputing.Experimentation.Topology import *
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessage
from enum import Enum
from adhoccomputing.Generics import *

class LaiYangEventTypes(Enum):
    TAKESNAPSOT = "TAKESNAPSOT" # event that triggers the Lai-Yang Snapshot Algorithm


class LaiYangMessageTypes(Enum):
    PRESNAPSHOT = "PRESNAPSHOT"


class BrachaTouegEventTypes(Enum):
    DETECTDEADLOCK = "DETECTDEADLOCK" # event that triggers the Bracha-Toueg Deadlock Detection Algorithm
    
    
class BrachaTouegMessageTypes(Enum):
    REQUEST = "REQUEST"


class SnapshotState():
    def __init__(self, sent_requests, received_requests, component_states):
        self.sent_requests = sent_requests
        self.received_requests = received_requests
        self.component_states = component_states
        

class BrachaTouegComponentModel(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None, child_conn=None, node_queues=None, channel_queues=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology, child_conn, node_queues, channel_queues)

        self.eventhandler[LaiYangEventTypes.TAKESNAPSHOT] = self.on_receiving_take_snapshot
        self.eventhandler[BrachaTouegEventTypes.DETECTDEADLOCK] = self.on_receiving_detect_deadlock
        
        self.sent_requests = dict() # OUT - the nodes process sent a request that were not yet purged or granted (key: componentinstancenumber, value: count of sent requests)
        self.received_requests = dict() # IN - the nodes the process has received a request from that that were not yet purged or granted 
        self.component_states = dict() # key: componentinstancenumber, value: list of received requests from the 'key' component
        self.snapshot_recorded = False # states whether the component has taken its local snapshot      
        self.local_snapshot = None # stores the local snapshot of the component as SnapshotState
        
    
    def on_receiving_detect_deadlock(self, eventobj: Event):
        '''
        This method triggers the Bracha-Toueg Deadlock Detection Algorithm
        by first taking a local snapshot of the component starting the algorithm.
        '''
        logger.info(f"{self.componentname}.{self.componentinstancenumber} starts the deadlock detection algorithm.")
        self.send_self(Event(self, LaiYangEventTypes.TAKESNAPSHOT, None), None)
    
    
    def on_receiving_take_snapshot(self, eventobj: Event):
        '''
        This method triggers the Lai-Yang Snapshot Algorithm
        '''
        logger.info(f"{self.componentname}.{self.componentinstancenumber} starts the Lai-Yang snapshot algorithm after starting the deadlock detection")
        self.take_snapshot()
    
    
    def send_request_to_component(self, component):
        '''
        This method sends a request to the component specified with its *component instance number*. The payload of this 
        request contains the information of whether the process sending this request has taken a snapshot.
        '''
        logger.info(f"{self.componentname}.{self.componentinstancenumber} sent request to the {self.componentname}.{component}")
        header = GenericMessageHeader(BrachaTouegMessageTypes.REQUEST, self.componentinstancenumber, component)
        message = GenericMessage(header, GenericMessagePayload(self.snapshot_recorded))
        self.send_down(Event(self, EventTypes.MFRT, message), None)
        if not self.snapshot_recorded:
            self.sent_requests[component] += 1
            
    
    def on_receiving_request_from_component(self, eventobj: Event):
        '''
        This method receives the request by comparing the process sending the request's local snapshot and the process receiving 
        the request. If process sending this request has already taken the snapshot, this process also takes it. If this process
        took its snapshot then, it proceeds to check the condition for termination
        '''
        logger.info(f"{self.componentname}.{self.componentinstancenumber} received a request from {self.componentname}.{eventobj.eventcontent.header.messagefrom}.")
        is_snapshot_recorded = eventobj.eventcontent.payload
        if is_snapshot_recorded: # process sending the request took the snapshot 
            logger.info(f"{self.componentname}.{self.componentinstancenumber} starts to take snapshot because {self.componentname}.{eventobj.eventcontent.header.messagefrom} took its local snapshot before.")
            self.take_snapshot()
        elif self.snapshot_recorded: # process receiving the request took the snapshot
            sending_process = eventobj.eventcontent.header.messagefrom
            self.component_state[sending_process].append(eventobj) # append the request to the sending process's state
            is_termination = True # denotes the termination condition
            for component in self.component_state:
                if len(self.component_state[component]) + 1 != self.sent_requests[component]:
                    is_termination = False
                    break
            if is_termination:
                logger.info(f"{self.componentname}.{self.componentinstancenumber} terminates the snapshot algorithm.")
                self.terminate_snapshot()
    
    
    def on_receiving_presnapshot(self, eventobj: Event):
        '''
        The component receiving the presnapshot control message starts to take its own local snapshot. 
        After that, if the termination condition is satisfied, the component terminates the snapshot algorithm.
        '''
        messagefrom = eventobj.eventcontent.header.messagefrom
        self.sent_requests[messagefrom] = eventobj.eventcontent.payload
        self.take_snapshot()
        is_termination = True
        for component in self.component_state:
            if len(self.component_state[component]) + 1 != self.sent_requests[component]:
                is_termination = False
                break
        if is_termination:
            logger.info(f"{self.componentname}.{self.componentinstancenumber} terminates the snapshot algorithm.")
            self.terminate_snapshot()
    
    
    def on_message_from_bottom(self, eventobj: Event):
        '''
        This function processes the message from top events by calling related
        functions according to the message's header.
        '''
        if eventobj.eventcontent.header.messageto == self.componentinstancenumber:
            messagetype = eventobj.eventcontent.header.messagetype
            if messagetype == LaiYangMessageTypes.PRESNAPSHOT:
                self.on_receiving_presnapshot(eventobj)
            elif messagetype == BrachaTouegMessageTypes.REQUEST:
                self.on_receiving_request_from_component()
        else:
            logger.info(f"{eventobj.eventcontent.header.messagetype} is discarded because it is not supposed to be sent to {self.componentname}.{self.componentinstancenumber}")    

  
    def take_snapshot(self):
        '''
        This method takes a local snapshot of the component after sending presnapshot messages to all its outgoing 
        channels by storing the received and sent messages.
        '''
        if not self.snapshot_recorded:
            self.snapshot_recorded = True
            logger.info(f"{self.componentname}.{self.componentinstancenumber} sends presnapshot message to its outgoing channels.")
            self.send_presnapshot()
            self.local_snapshot = SnapshotState(self.sent_requests, self.received_requests, self.component_states)
            logger.info(f"{self.componentname}.{self.componentinstancenumber} local snapshot is saved")
    
    
    def send_presnapshot(self):
        '''
        This method sends the presnap control message to the component's all 
        outgoing channel. The payload of the message contains the number of messages
        that the component sent to each of the channels.
        '''
        for component in self.sent_requests:
            header = GenericMessageHeader(LaiYangMessageTypes.PRESNAPSHOT, self.componentinstancenumber, component)
            payload = GenericMessagePayload(self.sent_requests[component] + 1)
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, payload), None))
    
    
    def terminate_snapshot(self):
        '''
        This method notifies the component by calling the deadlock detection algorithm
        to proceed with since the WFG is computed.
        '''
        logger.info(f"Lai-Yang Snapshot Algorithm terminated for {self.componentname}.{self.componentinstancenumber}, continuing with deadlock detection")
        self.detect_deadlock()   
