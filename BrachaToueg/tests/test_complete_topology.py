from GenerateTopology import *



def main():
    node_count = 10
    topology, random_cycle = generate_complete_graph_with_random_cycle(node_count, BrachaTouegComponentModel, GenericChannel)
    topology.start()
    time.sleep(1)
    components = list(topology.nodes.values())
    print(random_cycle)
    for i in range(len(random_cycle) - 1):
        x = random_cycle[i]
        y = random_cycle[i + 1]
        components[x].send_request_to_component(components[y])
    components[random_cycle[-1]].send_request_to_component(components[random_cycle[0]])
    time.sleep(10)
    initiator = random.choice(random_cycle)
    components[initiator].send_self(Event(components[initiator], BrachaTouegEventTypes.DETECTDEADLOCK, eventcontent="Initiator"))   
    
    time.sleep(20)
    topology.exit()
   
if __name__ == "__main__":
    exit(main())