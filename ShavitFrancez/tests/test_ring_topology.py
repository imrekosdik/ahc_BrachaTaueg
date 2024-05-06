from GenerateTopology import *

def main():
    node_count = 500
    topology = generate_ring_topology(node_count, ShavitFrancezComponentModel, GenericChannel)

    topology.start()

    components = list(topology.nodes.values())
    time.sleep(5)
    components[0].send_self(Event(components[0], ShavitFrancezEventTypes.DETECTTERMINATION, eventcontent="Initiator"))  
    for i in range(node_count):
        time.sleep(0.1)
        components[i].send_self(Event(components[i], ShavitFrancezEventTypes.SENDBASICMESSAGE, None))
    time.sleep(1)
    for i in range(node_count):
        components[i].send_self(Event(components[i], ShavitFrancezEventTypes.BECOMEPASSIVE, None))
    
    time.sleep(2)
    topology.exit()
    total_number_of_exchanged_wave_messages = 0
    total_number_of_exchanged_basic_messages = 0
    for i in range(node_count):
        total_number_of_exchanged_wave_messages += components[i].wave_exchanged_messages
        total_number_of_exchanged_basic_messages += components[i].basic_exchanged_messages
    print(f"Total number of exchanged wave messages: {total_number_of_exchanged_wave_messages}")
    print(f"Total number of exchanged basic messages: {total_number_of_exchanged_basic_messages}")
   

if __name__ == "__main__":
    exit(main())