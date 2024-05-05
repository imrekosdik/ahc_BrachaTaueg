.. include:: substitutions.rst

|ShavitFrancezAlg|
=========================================


Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Global termination in a distributed system occurs when all processes reach the local termination state, no messages are in transit, and processes do not send or receive any message. Local termination is the state where the process completed its execution, meaning it is passive (idle) and is ready to continue its computation upon receiving any message. A process is active when it is performing some computation. In a distributed system, only the active processes can send messages. Therefore, a computation in a distributed system terminates when all its processes are idle.

The primary consideration behind the termination detection algorithms is adding a control algorithm to the system running to detect whether the basic algorithm has reached a termination state. The basic algorithm is the one currently running in the distributed system. Initiators of the basic algorithm are active processes and can trigger the execution of the control algorithm. The control algorithm consists of the termination detection and the announcement phases. The messages that the control algorithm sends or receives are control messages. Ideally, the termination detection algorithm should not need additional communication channels to send or receive its control messages, and should not interfere with the basic algorithm running on the system.

:ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` [ShavitFrancez1986]_ is the generalization of Dijkstra-Scholten Termination Detection Algorithm [DijkstraSholten1980]_ for distributed systems. In Dijkstra-Scholten Algorithm, the initiator of the basic algorithm maintains a tree of active processes. If a process makes another process active by sending a message, that process joins the tree as a child of the process. A process can only leave the tree if it transitions to passive state and it has no children in the tree. Once the tree becomes empty, the initiator announces the termination. :ref:`Shavit-Francez Termination Detection Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` [ShavitFrancez1986]_ maintains a forest instead of a single tree due to the nature of the distributed system. Each initiator maintains its tree and constitutes it to the forest. The condition for a process to join a tree is that it is not already a member of any of the trees in the forest. Other than that, the algorithm continues as in the Dijkstra-Scholten Algorithm. Instead, it starts a wave in which only those processes not part of a tree participate. Because each initiator is only aware of the emptiness of its tree, an empty tree does not guarantee that the whole forest is empty. The wave algorithm ensures that all the trees in the forest collapse before announcing termination. Once the wave decides, the initiator can then announce the termination. A wave algorithm is not complete unless all the processes take part in its execution. Following this property, the algorithm ensures that if none of the waves started by the processes are complete because a process refuses to take part, the initiator maintaining the last tree to be empty will start a wave that eventually decides and announces the termination. [Fokking2013]_ 

The wave algorithm we choose for the implementation in :ref:`Shavit-Francez Termination Detection Algorithm <ShavitFrancezTerminationDetectionAlgorithm>`  is :ref:`Echo Algorithm <EchoAlgorithm>` [Fokking2013]_. The :ref:`Echo Algorithm <EchoAlgorithm>` initiator begins by sending messages to all of its neighbors. If a non-initiator receives a message for the first time, it sets its parent as the sender process and sends a message to all its neighbors except its parent. After receiving messages from all its neighbors, the non-initiator notifies its parent. Finally, the initiator receives messages from all its neighbors and decides.


Shavit-Francez Termination Detection Algorithm: |ShavitFrancezAlg| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The :ref:`Shavit-Francez Termination Detection Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` is proposed by Nir Shavit and Nissim Francez to detect termination in the distributed system algorithms. General flow of execution of the algorithm is as follows:

1. If a process is the initiator of the basic algorithm, it sets its active property to true, indicating that it is doing some computation at the time. (Line 5)
2. If a process sends a basic message while executing the basic algorithm, then it increases its number of children by 1, because the process that is sent message becomes its children. (Line 8)
3. If a process receives a basic message while it is passive, then it becomes active (Line 12) and sets its parent to the process sending the basic message (Line 13). If it was already active, then it informs the sending process with an ACKNOWLEDGE message. (Line 15)
4. If a process receives an ACKNOWLEDGE message, it decreases its number of children by 1 (Line 19), calls the LeaveTree procedure. (Line 20)
5. If at some point a process becomes passive then it sets its active property to false (Line 23), calls the LeaveTree procedure. (Line 24)
6. Inside the LeaveTree procedure, a passive process with no children sends its parent an ACKNOWLEDGE message (Line 29), and then sets its parent to None (Line 30). 
7. If a passive process with no children has no parent at all, it starts a wave inside the LeaveTree procedure. (Line 32).
8. A a passive process with no children receiving a wave message acts as what the wave algorithm dictates (Line 37) and if the wave algorithm decides, it announces termination. (Line 38) 

.. _ShavitFrancezTerminationDetectionAlgorithm:

.. code-block:: RST
    :linenos:
    :caption: Shavit-Francez Termination Detection Algorithm
    
    1   bool active<p> // set when p becomes active, and reset when p becomes passive
    2   nat cc<p> // keeps track of the number of children of p in its tree
    3   proc parent<p> // the parent of p in a tree in the forest
    
    4   if p is an initiator then
    5       active<p> <- true
    6   end if

    7   if p sends a basic message then
    8       cc<p> <- cc<p> + 1
    9   end if

    10  if p receives a basic message from a neighbor q then
    11    if active<p> = false then
    12        active<p> <- true
    13        parent<p> <- q
    14    else 
    15        send <ack> to q
    16    end if
    17  end if

    18  if p receives <ack>
    19      cc<p> <- cc<p> - 1
    20      perform procedure LeaveTree<p>
    21  end if

    22  if p becomes passive
    23      active<p> <- false
    24      perform procedure LeaveTree<p>;
    25  end if

    26  Procedure LeaveTree<p>
    27      if active<p> = false and cc<p> = 0 then
    28          if parent<p> != ┴ then 
    29              send <ack> to parent<p>
    30              parent<p> <- ┴
    31          else
    32              start a wave, tagged with p
    33          end if
    34      end if
    
    35  if p receives a wave message then
    36      if active<p> = false and cc<p> = 0 then
    37          act according to the wave algorithm
    38          in the case of a decive event, call Announce
    39      end if
    40  end if


Echo Algorithm:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The :ref:`Echo Algorithm <EchoAlgorithm>` [Fokking2013]_ takes part in making sure that all the trees in the forest collapsed and thus, concluding that the basic algorithm terminated. Since this paper focuses on the implementation details of the :ref:`Shavit-Francez Termination Detection Algorithm <ShavitFrancezTerminationDetectionAlgorithm>`, we do not explicitly describe the pseudocode we provided for the wave algorithm. We only add the pseudocode here because we make use of this algorithm while implementing the :ref:`Shavit-Francez Termination Detection Algorithm <ShavitFrancezTerminationDetectionAlgorithm>`.

.. _EchoAlgorithm:

.. code-block:: RST 
    :linenos:
    :caption: Echo Algorithm

    1   nat received<p>;
    2   proc parent<p>;

    3   if p is the initiator then
    4       send <wave> to each r in Neighbors<p>
    5   end if
    
    6   if p receives a <wave> from neighbor q then
    7       received<p> <- received<p> + 1
    8       if parent<p> != ┴ and p is a non-initiator then 
    9           parent<p> <- q
    10          if |Neighbors<p>| > 1 then
    11              send <wave> to each r in Neighbors<p>\{q}
    12          else
    13              send <wave> to q
    14          end if
    15      else if received<p> = |Neighbors<p>| then
    16          if parent<p> != ┴ then 
    17              send <wave> to parent<p>
    18          else
    19              decide
    20          end if
    21      end if
    22  end if


Example With Terminating Distributed System Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: 

    * - .. figure:: figures/shavit_step1.png

           Step 1

      - .. figure:: figures/shavit_step2.png

           Step 2

    * - .. figure:: figures/shavit_step3.png

           Step 3
           
      - .. figure:: figures/shavit_step4.png

           Step 4

    * - .. figure:: figures/shavit_step5.png

            Step 5

      - .. figure:: figures/shavit_step6.png

           Step 6


Assume that there are three processes p, q, r in an undirected network. One way to execute the :ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` is as follows:

1. At the start, the initiators p and q both send a basic message to r, and set cc<p> and cc<q> to 1. Next, p and q become passive.(See Figure 1)
2. Upon receipt of the basic message from p, r becomes active and makes p its parent. Next, r receives the basic message from q, and sends back an acknowledgment, which causes q to decrease cc<q> to 0.(See Figure 2)
3. Since q became passive as the root of a tree, and cc<q> = 0, it starts a wave. This wave does not complete, because p and r refuse to participate.(See Figure 3)
4. r sends a basic message to q, and sets cc<r> to 1. Next, r becomes passive.(See Figure 4)
5. Upon receipt of the basic message from r, q becomes active, and makes r its parent. Next, q becomes passive, and sends an acknowledgment to its parent r, which causes r to decrease cc<r> to 0. Since r is passive and cc<r> = 0, it sends an acknowledgment to its parent p, which causes p to decrease cc<p> to 0.(See Figure 5)
6. Since p became passive as the root of a tree, and cc<p> = 0, it starts a wave. This wave completes, so that p calls Announce.(See Figure 6)

Example With Non-Terminating Distributed System Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: 

    * - .. figure:: figures/shavit_ex2_step1.png

           Step 1

      - .. figure:: figures/shavit_ex2_step2.png

           Step 2

    * - .. figure:: figures/shavit_ex2_step3.png

           Step 3

Assume that there are three processes p, q, r in an undirected network. One way to execute the :ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` is as follows:

1. At the start, the initiators p and r both send a basic message to q, and set cc<p> and cc<r> to 1. (See Figure 7)
2. Upon receipt of the basic message from p, q becomes active and makes p its parent. Next, q receives the basic message from r, and sends back an acknowledgment, which causes r to decrease cc<r> to 0.(See Figure 2)
4. Next, r becomes passive.
5. Since r became passive as the root of a tree, and cc<r> = 0, it starts a wave. This wave does not complete, because p and q refuse to participate.(See Figure 3)
6. Since neither p nor q becomes passive at some point, the algorithm cannot complete the wave and cannot announce termination.

Correctness
~~~~~~~~~~~
1. **Safety**: The *Announce* is called when a decision occurs in the wave algorithm. This implies that each process p has sent a wave message or has decided, and the algorithm implies that cc<p> was 0 when p did so. No action makes cc<p> more than 0 again, so (for each p) cc<p> is 0 when *Announce* is called. [Tel2001]_
2. **Liveness**: Assume that the basic computation has terminated. Within a finite number of steps the termination-detection algorithm reaches a terminal configuration, and as in the correctness statement below it can be shown that in this configuration the forest is empty. Consequently, all events of the wave are enabled in every process, and that the configuration is terminal now implies that all events of the wave have been executed, including at least one decision, which caused a call to *Announce*. [Tel2001]_
3. **Correctness**: Define S to be the sum of all cc<p> for each process p. Initially S is zero, S is incremented when a basic message is sent, S is decremented when a control message is received, and S is never negative. This implies that the number of control messages never exceeds the number of basic messages in any computation. [Tel2001]_


Complexity 
~~~~~~~~~~
1. :ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>`: The worst case message complexity  is O(M + W) where M is the number of the messages sent by the underlying computation and W is a message exchange complexity of the wave algorithm, which is 2E for :ref:`Echo Algorithm <EchoAlgorithm>` where E is. [Tel2001]_ 
2. :ref:`Echo Algorithm <EchoAlgorithm>`: The message complexity is O(2E), where E is the number of edges. [Fokking2013]_


References 
~~~~~~~~~~
.. [ShavitFrancez1986] Shavit, N. and Francez, N. A new approach to the detection of locally indicative stability. In proc. Int. Colloq. Automata, Languages, and Programming (1986), L. Kott (ed.), vol. 226 of Lecture Notes in Computer Science, Springer-Verlag, pp. 344-358.
.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [DijkstraSholten1980] Dijkstra, E. W. and Scholten, C. S. Termination detection for diffusing computations. Inf. Proc. Lett. 11, 1 (1980), 1-4.
.. [Tel2001] Tel, G, Introduction To Distributed Algorithms, The Cambridge University Press, Cambridge, United Kingdom, 2001