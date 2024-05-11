from GenerateTopology import *



def main():
    node_count = 10
    topology = generate_ring_topology(node_count, BrachaTouegComponentModel, GenericChannel)
    topology.start()
    time.sleep(1)
    components = list(topology.nodes.values())
    for i in range(len(components)):
        components[i].send_request_to_component(components[(i + 1) % node_count])
    time.sleep(10)
    components[0].send_self(Event(components[0], BrachaTouegEventTypes.DETECTDEADLOCK, eventcontent="Initiator"))   
    
    time.sleep(2)
    topology.exit()
    total_number_of_received_messages = 0
    for i in range(node_count):
        total_number_of_received_messages += components[i].received_messages
    print(f"Total number of exchanged  messages: {total_number_of_received_messages}")

if __name__ == "__main__":
    exit(main())