from adhoccomputing.Experimentation.Topology import *
from adhoccomputing.Experimentation.Topology import Event
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessage
from enum import Enum
from adhoccomputing.Generics import *
from adhoccomputing.Generics import Event
from multiprocessing.pool import ThreadPool
import threading
import time

class LaiYangEventTypes(Enum):
    TAKESNAPSHOT = "TAKESNAPSHOT" # event that triggers the Lai-Yang Snapshot Algorithm


class LaiYangMessageTypes(Enum):
    PRESNAPSHOT = "PRESNAPSHOT"


class BrachaTouegEventTypes(Enum):
    DETECTDEADLOCK = "DETECTDEADLOCK" # event that triggers the Bracha-Toueg Deadlock Detection Algorithm
    CHECKDONEMESSAGES = "CHECKDONEMESSAGES"
    CHECKACKNOWLEDGEMESSAGES = "CHECKACKNOWLEDGEMESSAGES"
    
    
class BrachaTouegMessageTypes(Enum):
    REQUEST = "REQUEST"
    NOTIFY = "NOFIFY"
    DONE = "DONE"
    GRANT = "GRANT"
    ACKNOWLEDGE = "ACKNOWLEDGE"


class SnapshotState():
    def __init__(self, sent_requests, received_requests):
        self.sent_requests = sent_requests
        self.received_requests = received_requests
        

class BrachaTouegComponentModel(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None, child_conn=None, node_queues=None, channel_queues=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology, child_conn, node_queues, channel_queues)

        self.eventhandlers[LaiYangEventTypes.TAKESNAPSHOT] = self.on_receiving_take_snapshot
        self.eventhandlers[BrachaTouegEventTypes.DETECTDEADLOCK] = self.on_receiving_detect_deadlock
        
        self.counter = dict() 
        self.sent_requests = dict() # OUT - the nodes process sent a request that were not yet purged or granted (key: componentinstancenumber, value: count of sent requests)
        self.received_requests = dict() # IN - the nodes the process has received a request from that that were not yet purged or granted 
        self.component_states = dict() # key: componentinstancenumber, value: list of received requests from the 'key' component
        self.snapshot_recorded = False # states whether the component has taken its local snapshot      
        self.local_snapshot = None # stores the local snapshot of the component as SnapshotState
        self.snapshot_terminated = False

        self.deadlock_detection_initiator = False
        self.notified = False
        self.number_of_requests = 0
        self.free = False
        self.received_notify = []


    def on_receiving_detect_deadlock(self, eventobj: Event):
        '''
        This method triggers the Bracha-Toueg Deadlock Detection Algorithm
        by first taking a local snapshot of the component starting the algorithm.
        '''
        logger.info(f"{self.componentname}.{self.componentinstancenumber} starts the deadlock detection algorithm.")
        self.deadlock_detection_initiator = True
        self.send_self(Event(self, LaiYangEventTypes.TAKESNAPSHOT, None))
    
    
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
        if component not in self.counter.keys():
            self.counter[component] = 0
        logger.info(f"{self.componentname}.{self.componentinstancenumber} sent request to the {self.componentname}.{component}")
        header = GenericMessageHeader(BrachaTouegMessageTypes.REQUEST, self.componentinstancenumber, component)
        message = GenericMessage(header, GenericMessagePayload(self.snapshot_recorded))
        if component not in self.sent_requests.keys():
            self.sent_requests[component] = []
        self.sent_requests[component].append(Event(self, EventTypes.MFRT, message))
        self.number_of_requests += 1
        self.send_down(Event(self, EventTypes.MFRT, message))
        if not self.snapshot_recorded:
            self.counter[component] += 1
            
    
    def on_receiving_request_from_component(self, eventobj: Event):
        '''
        This method receives the request by comparing the process sending the request's local snapshot and the process receiving 
        the request. If process sending this request has already taken the snapshot, this process also takes it. If this process
        took its snapshot then, it proceeds to check the condition for termination
        '''
        logger.info(f"{self.componentname}.{self.componentinstancenumber} received a request from {self.componentname}.{eventobj.eventcontent.header.messagefrom}.")
        sending_process = eventobj.eventcontent.header.messagefrom
        if sending_process not in self.received_requests.keys():
            self.received_requests[sending_process] = []
        self.received_requests[sending_process].append(eventobj)
        is_snapshot_recorded = eventobj.eventcontent.payload.messagepayload
        if is_snapshot_recorded: # process sending the request took the snapshot 
            logger.info(f"{self.componentname}.{self.componentinstancenumber} starts to take snapshot because {self.componentname}.{eventobj.eventcontent.header.messagefrom} took its local snapshot before.")
            self.take_snapshot()
        else:
            if sending_process not in self.counter.keys():
                self.counter[sending_process] = 0
            self.counter[sending_process] -= 1
            if self.snapshot_recorded: # process receiving the request took the snapshot
                sending_process = eventobj.eventcontent.header.messagefrom
                if sending_process not in self.component_states.keys():
                    self.component_states[sending_process] = []
                self.component_states[sending_process].append(eventobj) # append the request to the sending process's state
                is_termination = True # denotes the termination condition
                for component in self.component_states:
                    if len(self.component_states[component]) + 1 != self.counter[component]:
                        is_termination = False
                        break
                if is_termination and not self.snapshot_terminated:
                    logger.info(f"{self.componentname}.{self.componentinstancenumber} terminates the snapshot algorithm.")
                    self.terminate_snapshot()
    
    
    def on_receiving_presnapshot(self, eventobj: Event):
        '''
        The component receiving the presnapshot control message starts to take its own local snapshot. 
        After that, if the termination condition is satisfied, the component terminates the snapshot algorithm.
        ''' 
        messagefrom = eventobj.eventcontent.header.messagefrom
        logger.info(f"{self.componentname}.{self.componentinstancenumber} received presnapshot from {messagefrom}")
        if messagefrom not in self.counter.keys():
            self.counter[messagefrom] = 0
        self.counter[messagefrom] += int(eventobj.eventcontent.payload.messagepayload)
        self.take_snapshot()
        is_termination = True
        for component in self.component_states:
            if len(self.component_states[component]) + 1 != self.counter[component]:
                is_termination = False
                break
        if is_termination and not self.snapshot_terminated:
            logger.info(f"{self.componentname}.{self.componentinstancenumber} terminates the snapshot algorithm.")
            self.terminate_snapshot()
    
    
    def on_message_from_bottom(self, eventobj: Event):
        '''
        This function processes the message from top events by calling related
        functions according to the message's header.
        '''
        if eventobj.eventcontent.header.messageto == self.componentinstancenumber:
            messagetype = eventobj.eventcontent.header.messagetype
            if messagetype == BrachaTouegMessageTypes.ACKNOWLEDGE:
                self.on_receiving_acknowledge(eventobj)
            elif messagetype == LaiYangMessageTypes.PRESNAPSHOT:
                self.on_receiving_presnapshot(eventobj)
            elif messagetype == BrachaTouegMessageTypes.REQUEST:
                self.on_receiving_request_from_component(eventobj)
            elif messagetype == BrachaTouegMessageTypes.NOTIFY:
                self.on_receiving_notify(eventobj)
            elif messagetype == BrachaTouegMessageTypes.DONE:
                self.on_receiving_done(eventobj)
            elif messagetype == BrachaTouegMessageTypes.GRANT:
                self.on_receiving_grant(eventobj)
  
        
    def take_snapshot(self):
        '''
        This method takes a local snapshot of the component after sending presnapshot messages to all its outgoing 
        channels by storing the received and sent messages.
        '''
        if not self.snapshot_recorded:
            self.snapshot_recorded = True
            logger.info(f"{self.componentname}.{self.componentinstancenumber} sends presnapshot message to its outgoing channels.")
            self.send_presnapshot()
            self.local_snapshot = SnapshotState(self.sent_requests, self.received_requests)
            logger.info(f"{self.componentname}.{self.componentinstancenumber} local snapshot is saved")
    
    
    def send_presnapshot(self):
        '''
        This method sends the presnap control message to the component's all 
        outgoing channel. The payload of the message contains the number of messages
        that the component sent to each of the channels.
        '''
        for component in self.counter:
            logger.info(f"sending presnaphot to {component}")
            header = GenericMessageHeader(LaiYangMessageTypes.PRESNAPSHOT, self.componentinstancenumber, component)
            payload = GenericMessagePayload(self.counter[component] + 1)
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, payload), None))
    
    
    def terminate_snapshot(self):
        '''
        This method notifies the component by calling the deadlock detection algorithm
        to proceed with since the WFG is computed.
        '''
        logger.info(f"Lai-Yang Snapshot Algorithm terminated for {self.componentname}.{self.componentinstancenumber}")
        self.snapshot_terminated = True
        if self.deadlock_detection_initiator:
            time.sleep(10)
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} starts detecting deadlocks")
            self.notify()   


    def notify(self):
        self.notified = True
        for component in self.sent_requests:
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} sent NOTIFY to {self.componentname}.{component}")
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} awaiting DONE from {self.componentname}.{component}")
            header = GenericMessageHeader(BrachaTouegMessageTypes.NOTIFY, self.componentinstancenumber, component)
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None), component))
        if self.number_of_requests == 0:
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} calls GRANT method")
            self.grant()
        
       
    def grant(self):
        self.free = True
        for component in self.received_requests:
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} sent GRANT to {self.componentname}.{component}")
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} awaiting ACKNOWLEDGE {self.componentname}.{component}")
            header = GenericMessageHeader(BrachaTouegMessageTypes.GRANT, self.componentinstancenumber, component)
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None), component))


    def on_receiving_notify(self, eventobj: Event):
        messagefrom = eventobj.eventcontent.header.messagefrom
        self.received_notify.append(messagefrom)
        logger.critical(f"{self.componentname}.{self.componentinstancenumber} received notify from {self.componentname}.{messagefrom}")
        if not self.notified:
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} calls notify")
            self.notify()
    
        logger.critical(f"{self.componentname}.{self.componentinstancenumber} sent DONE to {self.componentname}.{messagefrom}")
        header = GenericMessageHeader(BrachaTouegMessageTypes.DONE, self.componentinstancenumber, messagefrom)
        self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None), messagefrom))
  

    def on_receiving_grant(self, eventobj: Event):
        messagefrom = eventobj.eventcontent.header.messagefrom
        logger.critical(f"{self.componentname}.{self.componentinstancenumber} received grant from {self.componentname}.{messagefrom}")
        if self.number_of_requests > 0:
            self.number_of_requests -= 1
            if self.number_of_requests == 0:
                logger.critical(f"{self.componentname}.{self.componentinstancenumber} calls grant from on receiving grant")
                self.grant()

        logger.critical(f"{self.componentname}.{self.componentinstancenumber} sent ACKNOWLEDGE to {self.componentname}.{messagefrom}")
        header = GenericMessageHeader(BrachaTouegMessageTypes.ACKNOWLEDGE, self.componentinstancenumber, messagefrom)
        self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None)))
        
        
    
    def on_receiving_acknowledge(self, eventobj: Event):
        messagefrom = eventobj.eventcontent.header.messagefrom
        if messagefrom in self.received_requests:
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} received ACKNOWLEDGE from {self.componentname}.{messagefrom}")
            self.received_requests[messagefrom] = None

      
    def on_receiving_done(self, eventobj: Event):
        messagefrom = eventobj.eventcontent.header.messagefrom
        if messagefrom in self.sent_requests:
            logger.critical(f"{self.componentname}.{self.componentinstancenumber} received DONE from {self.componentname}.{messagefrom}")
            self.sent_requests[messagefrom] = None

        if all(value is None for value in self.sent_requests.values()):
            if self.deadlock_detection_initiator:
                if not self.free:
                    logger.critical(f"{self.componentname}.{self.componentinstancenumber} concludes that it is deadlocked.")
                else:
                    logger.critical(f"{self.componentname}.{self.componentinstancenumber} concludes that it is not deadlocked.")