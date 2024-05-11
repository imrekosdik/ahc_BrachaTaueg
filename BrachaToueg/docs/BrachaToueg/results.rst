.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We utilized the Python (version 3.12) scripting language and the Ad-Hoc Computing (adhoccomputing) library while implementing the Bracha-Toueg Detection Algorithm. We also employed the networkx library to generate various network topologies and the matplotlib library to visualize them. Each component in the topology can be the initiator for the deadlock detection algorithm. We implemented a function for which we can simulate processes requesting resources from one another. This function "send_request_to_component" is called for processes before starting the deadlock detection algorithm by sending "DETECTDEADLOCK" event to the initiator process. Once we started the deadlock detection algorithm, we first take the Lai-Yang snapshot of the initiator process. We are only interested in the exchanged "REQUEST" messages for deadlock detection, so we ignore other types of exchanged messages. Once the initiator process completes the Lai-Yang snapshot algorithm, it uses its previously recorded state to understand what processes it is waiting to receive resources and what processes waiting for it to grant resources. This means that, the initiator process computes a WFG graph for itself. Then, it continues with notifying the processes in "OUT" and waits for receiving DONE message from all of them. Once it receives DONE from all processes in OUT, it checks whether it is deadlocked by looking at its local variable "free". An importing to mention here is that, the grant procedure is embedded inside the notify. This enables a process to need to receive ACKNOWLEDGE messages from all processes in IN, before sending any "DONE" messages. 

If there is a cyclic dependency in the WFG, then we should expect that, the variable "free" for the initiator process can never be True. If there is no cyclic dependency in the WFG involving the initiator process, than we see that the variable "free" becomes True because the initiator process is able to grant some resources to other processes.

We implemented the Lai-Yang Snapshot Algorithm and the Bracha-Toueg Deadlock Detection Algorithm by employing the pseudocode descriptions given by in [Fokking2013]_. We used the same message types given in the descriptions to achieve the message passing between the components. The make the component who is the initiator of the basic algorithm send itself "DETECTDEADLOCK" message to trigger the algorithm. Depending on whether the initiator process can set the variable "free" to True, the algorithm detects the deadlock. An important note here is that, waiting for DONE and ACKNOWLEDGE messages should not prevent receiving and sending GRANT and NOTIFY messages. Therefore, we increased the number of threads executing in a component to 3 to reflect the asynchronous wait operations.

Results
~~~~~~~~
We designed two distinct scenarios to evaluate the message complexity of the Bracha-Toueg Deadlock Detection Algorithm. For the first scenario, we considered ring topologies with node counts as deadlock occurrence is guaranteed once each node passes a request to one of its neighbors in the same direction. In this scheme, the network topology guarantees that every node in the topology is part of the deadlock as well. Once each component sends a request to its neighbor, we start executing the algorithm through the initiator of the topology. After that, we measure the time elapsed until the initiator component detects the deadlock in the distributed system. Table 1 presents the elapsed time along with the number of control message components exchanged while running the algorithm. Note that we do not include the control messages of the Lai-Yang snapshot algorithm as it is not part of the deadlock detection algorithm.

.. list-table:: Table 1: Message Complexity Analysis of Deadlock Detection Algorithm on a Ring Topology
   :widths: 25 25 50
   :header-rows: 1

   * - Node Count
     - Number of Exchanged Control Messages
     - Time Elapsed Until Detection
   * - 5
     - 12
     - 0.5193710327148438
   * - 10
     - 22
     - 0.10675311088562012
   * - 20
     - 42
     - 0.11047983169555664
   * - 50
     - 72
     - 4.122158050537109
   * - 100
     - 123
     - 7.982053995132446

The plots below shows the relationship between the node count in the network with the time elapsed until detection and number of exchanged control messages.

.. list-table:: 

    * - .. figure:: figures/number_exchanged_messages.png

           The Relationship Between Node Count and Number Of Exchanged Messages

      - .. figure:: figures/time_elapsed.png

           The Relationship Between the Node Count and the Elapsed Time

In the second scenario, we considered a complete topology of 10 nodes. In such a topology, there are different cycles with different participating nodes. Before executing the algorithm, we found random cycles with 9, 8, 7, 5, and 3 nodes and made each component send a request to its neighbors in the same direction. After that, we start executing the algorithm through a participating node of the cycles. Table 2 presents the time elapsed until an initiator detects the deadlock of the same cycle in the system.

.. list-table:: Table 2: Message Complexity Analysis of Deadlock Detection Algorithm on a Complete Topology
   :widths: 25 25 50
   :header-rows: 1

   * - Cycles in the Topology
     - Initiator Node
     - Time Elapsed Until Detection
   * - [0, 2, 3, 4, 5, 6, 7, 8, 9]
     - 7
     - 0.1082148551940918
   * - [0, 1, 2, 3, 6, 7, 8, 9]
     - 8
     - 0.10948896408081055
   * - [2, 3, 4, 5, 6, 7, 8]
     - 2
     - 0.7286171913146973
   * - [0, 2, 4, 8, 9]
     - 4
     - 0.5165529251098633
   * - [0, 3, 6]
     - 6
     - 0.31595897674560547

Discussion
~~~~~~~~~~
We conducted two separate experiments to analyze the message and time complexity of an algorithm. To distinguish between the experiments, we did not modify the underlying computation. Instead, we made each process send a request to one of its neighbors in the same direction. By not changing the underlying computation, we could observe the changes in elapsed time over different topologies.

During the experiments, we had to add delays between events because we observed that, in the absence of the delays, we could not see the exchange of all the messages we sent. Additionally, we simulated some processes waiting to acquire resources as requests running in our topologies to conduct experiments.

Since we were only interested in generating a Wait-For-Graph (WFG), we ignored other exchanged messages in the distributed system while taking the Lai-Yang Snapshot. As a result, the algorithm became heavily dependent on the custom event.

Despite the challenges, we observed that as the number of nodes participating in a cycle increased, the time it took to detect the cycle in the topology went up proportionally.