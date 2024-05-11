.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We utilized the Python (version 3.12) scripting language and the Ad-Hoc Computing (adhoccomputing) library while implementing the Shavit-Francez Termination Detection Algorithm. We also employed the networkx library to generate various network topologies and the matplotlib library to visualize them. Each component in the topology can be the initiator for the termination detection algorithm. It is up to us which component to choose the initiator/initiators. After that, we must send an event to the initiators to execute the termination detection algorithm. Either initiator components can send the event to themselves, or other non-initator nodes can send it to the initiators. Since termination detection is the algorithm that runs on top of the basic algorithm running in the system, we needed to simulate a basic algorithm by creating additional messages that we could send to the component externally. We use "*BECOMEPASSIVE*" message to simulate processes finishing their execution and "*SENDBASICMESSAGE*" to simulate messages that the basic algorithm exchanges on its execution. An important consideration is that one can only send these messages if the process is active. Another consideration is that, the components need to be aware of who is executing the control algorithm. Therefore, the process starting the algorithm send a message to its neighbors indicating that it is the initiator for this execution.

For a distributed system in that its processes never become passive, we should expect that the algorithm does not announce the termination and, therefore, no output in the command prompt. As an example, we can consider a system with deadlocks. Since none of the processes can continue because they need resources from others, the algorithm cannot announce the termination. To create this scenario, we could think that the "SENDBASICMESSAGE" event acts as a "REQUEST" and create a cyclic graph. In other cases, sending a "BECOMEPASSIVE" event to a process acts as if the process finishing its execution, and we should see that the algorithm announces the termination in the commant prompt.

We implemented both the Echo Algorithm and the Shavit-Francez Termination Detection Algorithm by employing the pseudocode descriptions given in [Fokking2013]_. We used the same message types given in the descriptions to achieve the message passing between the components. The make the component who is the initiator of the basic algorithm send itself "DETECTTERMINATION" message to trigger the algorithm. After that, depending on the basic-messages exchanged between the processes and the status of the processes, the algorithm announces the termination.

Results
~~~~~~~~

In order to evaluate the message complexity of the Shavit-Francez Termination Detection Algorithm, we designed three different experiments. For the first experiment, we generate ring topologies with various number of node counts. The node with the first index becomes the initiator for the algorithm. Each node in the topology sends basic messages to all of its neighbors and then becomes passive. According to this configuration, we execute the algorithm for 2, 3, 5, 10, 20, 30, 50, 100 and 500 number of nodes and examine how many wave messages and basic messages are exchanged along with time it takes to complete the execution. 

For a ring topology, if there are n number of nodes, then there exists n number of edges in the topology. On the table, we observe that the number of exchanged wave messages is exactly two terminates the number of edges. That means, it is consistent with the message complexity of the Echo Algorithm, which is O(2E). Since each node sends basic message to each of its neighbors, then there should be 2 * n basic messages exchanged in the topology. So, the results we get gives us the complexity of the underlying computation, which is O(M), where M is 2 * n. We also observe that, the time it takes to complete the execution of the algorithm is directly proportional to the number of nodes in the topology.

.. list-table:: Table 1: Message Complexity Analysis of Termination Detection Algorithm on a Ring Topology
   :widths: 25 25 50
   :header-rows: 1

   * - Node Count
     - Time Elapsed Until Termination
     - Number of Exchanged Messages
   * - 2
     - 1.207543134689331
     - 2 (wave) + 2 (basic)
   * - 5
     - 1.5333149433135986
     - 10 (wave) + 10 (basic)
   * - 10
     - 2.045008897781372
     - 20 (wave) + 20 (basic)
   * - 20
     - 3.0964579582214355
     - 40 (wave) + 40 (basic)
   * - 30
     - 4.135018825531006
     - 60 (wave) + 60 (basic)
   * - 50
     - 6.216088056564331
     - 100 (wave) + 100 (basic)
   * - 100
     - 11.443176984786987
     - 200 (wave) + 200 (basic)
   * - 500
     - 53.18007707595825
     - 1000 (wave) + 1000 (basic)

.. list-table:: 

    * - .. figure:: figures/exchanged_messages.png

          The Relationship Between Node Count and Number Of Exchanged Messages

      - .. figure:: figures/time_elapsed.png

          The Relationship Between the Node Count and the Elapsed Time


For the second experiment, we generate complete topologies with different node counts. As in the first configuration, there is one initiator and each node sends basic message to all of its neighbors. After executing the algorithm for topologies with 2,5, 10, 20, 30, 40 and 50 node counts, we conclude that, the same relationship between the number of edges and the exchanged messages exist in this experiment as well. It seems that, there are not much difference between elapsed time of this experiment with the first experiment. Note that, we could not execute the algorithm for node counts larger than 40 because adhoccomputing library could not create new threads.

.. list-table:: Table 2: Message Complexity Analysis of Termination Detection Algorithm on a Complete Topology
   :widths: 25 25 50
   :header-rows: 1

   * - Node Count
     - Time Elapsed Until Termination
   * - 2
     - 1.211822748184204
   * - 5
     - 1.5393249988555908
   * - 10
     - 2.0759570598602295
   * - 20
     - 3.2077481746673584
   * - 30
     - 4.605236291885376
   * - 40
     - 10.92475700378418
    
For the last experiment, since more than one node can trigger the termination detection algorithm, we analyze the message complexity of a complete topology of 10 nodes with 1 to 5 number of initiators. Other than that, the experiment setup is exactly like that in the first and second experiments. There are 90 wave messages and 90 basic messages exchanged between the nodes. Each of the initiator is able to announce termination so we present the best time elapsed among different initiator results. To conclude, even though the number of initiators change, number of exchanged messages stay the same. Since each initiator forms its own forest and the number of messages do not change, the elapsed time does not get affected by the initiator count. 

.. list-table:: Table 3: Message Complexity Analysis of Termination Detection Algorithm on a Complete Topology with Different Number of Initiators
   :widths: 25 25 50
   :header-rows: 1

   * - Initiator Count
     - Time Elapsed Until Termination
   * - 1
     - 2.073668956756592
   * - 2
     - 2.172826051712036
   * - 3
     - 2.1762309074401855
   * - 4
     - 2.169590950012207
   * - 5
     - 2.158134937286377

Discussion
~~~~~~~~~~
We run three distinct experiments to analyze the message and time complexity of the algorithm. To distinguish between the experiments, we did not change the underlying computation, that is, we make each process send each of its neighbors basic messages. By not changing the underlying computation, we could observe the changes in the elapsed time over different topologies. For a small number of nodes, less than 50, we observe that the topology does not affect the time elapsed to finish executing the algorithm. Unfortunately, due to the nature of the ad-hoc computing library, we could not compare two different topologies over a large number of nodes. Also, while running experiments, we had to add delays between the events because we observed that, in the absence of the delays, we could not see the exchange of all the messages we sent. To conduct experiments, we created an event to simulate some basic algorithms running in our topologies. Since the expectation is that the basic algorithm is to run separately from the control algorithm, having to add a specific function to pass basic messages to components may conflict with it. The experiment results demonstrated that the complexity of the underlying computation is proportional to the number of edges in the topology in all experiments. For the wave algorithm, our experiment results coincide with the worst-case complexity of the Echo Algorithm. To sum up, we see that the experiment results are in line with the worst-case complexity of the termination detection algorithm.  
