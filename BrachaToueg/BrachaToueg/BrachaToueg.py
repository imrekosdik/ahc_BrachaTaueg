from adhoccomputing.Experimentation.Topology import *
from adhoccomputing.Experimentation.Topology import Event
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessage
from enum import Enum
from adhoccomputing.Generics import *
from adhoccomputing.Generics import Event

class LaiYangEventTypes(Enum):
    TAKESNAPSHOT = "TAKESNAPSHOT" # event that triggers the Lai-Yang Snapshot Algorithm


class LaiYangMessageTypes(Enum):
    PRESNAPSHOT = "PRESNAPSHOT"

class BrachaTouegEventTypes(Enum):
    DETECTDEADLOCK = "DETECTDEADLOCK" # event that triggers the Bracha-Toueg Deadlock Detection Algorithm

class BrachaTouegMessageTypes(Enum):
    REQUEST = "REQUEST"
    NOTIFY = "NOFIFY"
    DONE = "DONE"
    GRANT = "GRANT"
    ACKNOWLEDGE = "ACKNOWLEDGE"

class SnapshotState():
    def __init__(self, snapshot_recorded, counter, state, outgoing_channels, incoming_channels):
        self.snapshot_recorded = snapshot_recorded
        self.counter = counter
        self.state = state
        self.outgoing_channels = outgoing_channels
        self.incoming_channels = incoming_channels


class BrachaTouegComponentModel(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=3, topology=None, child_conn=None, node_queues=None, channel_queues=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology, child_conn, node_queues, channel_queues)
        
        # attributes related with Lai-Yang Snapshot Algorithm
        self.eventhandlers[LaiYangEventTypes.TAKESNAPSHOT] = self.on_receiving_take_snapshot
        self.snapshot_recorded = False # states whether the component has taken its local snapshot
        self.counter = dict() # keys: componentinstancenumber - values: how many messages that the component sent to/received from the key component
        self.state = dict() # keys: componentinstancenumber - values: messages received from incoming channels 
        self.saved_snapshot_state = None
        self.outgoing_channels = dict() # stores components that this component sent a request to
        self.incoming_channels = dict() # stores components that this component received a request from

        # attributes related with Bracha-Toueg Deadlock Detection Algorithm
        self.eventhandlers[BrachaTouegEventTypes.DETECTDEADLOCK] = self.on_receiving_detect_deadlock
        self.deadlock_detection_initiator = False
        self.notified = False
        self.free = False
        self.number_of_requests = 0
        self.number_of_received_ack_messages = 0
        self.number_of_received_done_messages = 0

        self.start_time = None
        self.end_time = None
        self.received_messages = 0

    def on_receiving_detect_deadlock(self, eventobj: Event):
        '''
        This method triggers the Bracha-Toueg Deadlock Detection Algorithm
        by first taking a local snapshot of the component starting the algorithm.
        ''' 
        self.start_time = time.time()
        self.deadlock_detection_initiator = True
        self.send_self(Event(self, LaiYangEventTypes.TAKESNAPSHOT, None))
    

    def on_receiving_take_snapshot(self, eventobj: Event):
        '''
        This method triggers the Lai-Yang Snapshot Algorithm
        '''
        self.take_snapshot()
    

    def send_request_to_component(self, component):
        '''
        This method sends a request to the given component in the arguments, simulating 
        that this process requires some resource/communication from the given component
        REQUEST is part of the basic algorithm and independent of the detection algorithm. 
        '''
        instance_number = component.componentinstancenumber
        self.number_of_requests += 1
        if instance_number not in self.outgoing_channels:
            self.outgoing_channels[instance_number] = 0
        self.outgoing_channels[instance_number] += 1
        # send the request to the component - simulates a communication request
        # payload appends the information of whether this process has taken a local snapshot to the REQUEST message
        message = self.generate_message(BrachaTouegMessageTypes.REQUEST, self.componentinstancenumber, instance_number, self.snapshot_recorded)
        self.send_down(Event(self, EventTypes.MFRT, message))
        # if the component previously did not send any messages to the given component
        if instance_number not in self.counter.keys(): 
            self.counter[instance_number] = 0            
        if not self.snapshot_recorded: # as long as the process did not take its local snapshot
            self.counter[instance_number] += 1 
    
    
    def on_receiving_request_from_component(self, eventobj: Event):
        '''
        This method receives the request by comparing the process sending the request's local snapshot and the process receiving 
        the request. If process sending this request has already taken the snapshot, this process also takes it. If this process
        took its snapshot then, it proceeds to check the condition for termination
        '''
        sending_process = eventobj.eventcontent.header.messagefrom
        if sending_process not in self.state.keys():
                self.state[sending_process] = []
        if sending_process not in self.incoming_channels:
            self.incoming_channels[sending_process] = 0
        self.incoming_channels[sending_process] += 1
        is_snapshot_recorded = eventobj.eventcontent.payload.messagepayload
        if is_snapshot_recorded: # process sending the request took the snapshot 
            self.take_snapshot()
        else:
            if sending_process not in self.counter.keys(): 
                self.counter[sending_process] = 0  
            self.counter[sending_process] -= 1 
            if self.snapshot_recorded: # process receiving the request took the snapshot
                self.state[sending_process].append(eventobj) # append the request to the sending process's state
                logger.critical(f"state of {self.componentinstancenumber} = {self.state}")
                if self.check_termination_condition():
                    self.terminate_snapshot()
    
    
    def on_receiving_presnapshot(self, eventobj: Event):
        '''
        The component receiving the presnapshot control message starts to take its own local snapshot. 
        After that, if the termination condition is satisfied, the component terminates the snapshot algorithm.
        ''' 
        messagefrom = eventobj.eventcontent.header.messagefrom
        if messagefrom not in self.counter.keys(): 
            self.counter[messagefrom] = 0  
        self.counter[messagefrom] += int(eventobj.eventcontent.payload.messagepayload)
        self.take_snapshot()
        if self.check_termination_condition():
            self.terminate_snapshot()
    

    def on_message_from_bottom(self, eventobj: Event):
        '''
        This function processes the message from top events by calling related
        functions according to the message's header.
        '''
        if eventobj.eventcontent.header.messageto == self.componentinstancenumber:
            messagetype = eventobj.eventcontent.header.messagetype
            if messagetype == BrachaTouegMessageTypes.ACKNOWLEDGE:
                self.received_messages += 1
                self.on_receiving_acknowledge(eventobj)
            elif messagetype == LaiYangMessageTypes.PRESNAPSHOT:
                self.on_receiving_presnapshot(eventobj)
            elif messagetype == BrachaTouegMessageTypes.REQUEST:
                self.on_receiving_request_from_component(eventobj)
            elif messagetype == BrachaTouegMessageTypes.NOTIFY:
                self.received_messages += 1
                self.on_receiving_notify(eventobj)
            elif messagetype == BrachaTouegMessageTypes.DONE:
                self.received_messages += 1
                self.on_receiving_done(eventobj)
            elif messagetype == BrachaTouegMessageTypes.GRANT:
                self.received_messages += 1
                self.on_receiving_grant(eventobj)
    

    def take_snapshot(self):
        '''
        This method takes a local snapshot of the component after sending presnapshot messages to all its outgoing 
        channels by storing *self.incoming_channels*, *self.outgoing_channels*, *self.state* and *self.counter*.
        '''
        if not self.snapshot_recorded:
            self.snapshot_recorded = True
            for channel in self.outgoing_channels:
                message = self.generate_message(LaiYangMessageTypes.PRESNAPSHOT, self.componentinstancenumber, channel, self.counter[channel] + 1)
                self.send_down(Event(self, EventTypes.MFRT, message))
            for channel in self.incoming_channels:
                message = self.generate_message(LaiYangMessageTypes.PRESNAPSHOT, self.componentinstancenumber, channel, self.counter[channel] + 1)
                self.send_down(Event(self, EventTypes.MFRT, message))
            self.saved_snapshot_state = SnapshotState(self.snapshot_recorded, self.counter, self.state, self.outgoing_channels, self.incoming_channels)
    

    def terminate_snapshot(self):
        '''
        This method notifies the component by calling the deadlock detection algorithm
        to proceed with since the WFG is computed.
        '''
        if self.deadlock_detection_initiator:
            self.notify() 


    def check_termination_condition(self):
        '''
        This function compares the number of incoming and outgoing messages of a given component 
        with its incoming message set length and reaches a conclusion about the algorithm termination
        '''
        termination_condition = True
        for channel in self.incoming_channels:
            if len(self.state[channel]) + 1 != self.counter[channel]:
                termination_condition = False
                break
        return termination_condition
    
    
    def generate_message(self, messagetype, messagefrom, messageto, payload):
        '''
        This function generates a GenericMessage object given the type of the message,
        the payload of the message and the message source and destination
        '''
        header = GenericMessageHeader(messagetype, messagefrom, messageto)
        return GenericMessage(header, GenericMessagePayload(payload))
    

    def notify(self):
        '''
        Process sends notify to all its outgoing messages and if it does not wait for
        any resources, it starts granting the resources. After receiving DONE messages
        from its outgoing channels, it checks the value of free and decides whether it
        is deadlocked.
        '''
        self.notified = True
        for component in self.saved_snapshot_state.outgoing_channels:
            header = GenericMessageHeader(BrachaTouegMessageTypes.NOTIFY, self.componentinstancenumber, component)
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None), component))
        if self.number_of_requests == 0: # grant if the process does not wait for any resources
            self.grant()
        
        # stop execution until the component received DONE message from all of its outgoing channels
        while (self.number_of_received_done_messages != len(self.outgoing_channels)):
            time.sleep(0.1)
        
        if self.deadlock_detection_initiator:
            if self.free:
                logger.critical(f"{self.componentname}.{self.componentinstancenumber} concludes that it is not deadlocked.")
            else:
                logger.critical(f"{self.componentname}.{self.componentinstancenumber} concludes that it is deadlocked.")
            self.end_time = time.time()
            logger.critical(f"Time Elapsed: {self.end_time - self.start_time}")

    
    def grant(self):
        '''
        Process that is able to grant resource to its incoming channels becomes a free process and
        waits for ACKNOWLEDGE message from its incoming channels before proceeding.
        '''
        self.free = True
        for component in self.saved_snapshot_state.incoming_channels:
            header = GenericMessageHeader(BrachaTouegMessageTypes.GRANT, self.componentinstancenumber, component)
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None), component))
        
        # stop execution until the component received ACKNOWLEDGE message from all of its incoming channels
        while (self.number_of_received_ack_messages != len(self.saved_snapshot_state.incoming_channels)):
            time.sleep(0.1)


    def on_receiving_notify(self, eventobj: Event):
        '''
        Process receiving the notify message notifies its outgoing components
        if it is not notified earlier. After that it sends DONE message to the
        process sending the notify message.
        '''
        messagefrom = eventobj.eventcontent.header.messagefrom
        if not self.notified:
            self.notify()
        header = GenericMessageHeader(BrachaTouegMessageTypes.DONE, self.componentinstancenumber, messagefrom)
        self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None), messagefrom))
  

    def on_receiving_grant(self, eventobj: Event):
        '''
        Process receiving the grant message grants resources to its incoming channels
        if it does not wait for any resources. After that, it sends ACKNOWLEDGE message
        to the process granting the resource to it.
        '''
        messagefrom = eventobj.eventcontent.header.messagefrom
        if self.number_of_requests > 0:
            self.number_of_requests -= 1
            if self.number_of_requests == 0:
                self.grant()
        header = GenericMessageHeader(BrachaTouegMessageTypes.ACKNOWLEDGE, self.componentinstancenumber, messagefrom)
        self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None)))
        

    def on_receiving_acknowledge(self, eventobj: Event):
        messagefrom = eventobj.eventcontent.header.messagefrom
        if messagefrom in self.saved_snapshot_state.incoming_channels:
            self.number_of_received_ack_messages += 1

      
    def on_receiving_done(self, eventobj: Event):
        messagefrom = eventobj.eventcontent.header.messagefrom
        if messagefrom in self.saved_snapshot_state.outgoing_channels:
            self.number_of_received_done_messages += 1
    