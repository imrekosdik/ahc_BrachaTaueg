.. include:: substitutions.rst

|ShavitFrancezAlg|
=========================================


Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Global termination in a distributed system occurs when all processes reach the local termination state, no messages are in transit, and processes do not send or receive any message. Local termination is the state where the process completed its execution, meaning it is passive (idle) and is ready to continue its computation upon receiving any message. A process is active when it is performing some computation. In a distributed system, only the active processes can send messages. Therefore, a computation in a distributed system terminates when all its processes are idle.

The primary consideration behind the termination detection algorithms is adding a control algorithm to the system running to detect whether the basic algorithm has reached a termination state. The basic algorithm is the one currently running in the distributed system. Initiators of the basic algorithm are active processes and can trigger the execution of the control algorithm. The control algorithm consists of the termination detection and the announcement phases. The messages that the control algorithm sends or receives are control messages. Ideally, the termination detection algorithm should not need additional communication channels to send or receive its control messages, and should not interfere with the basic algorithm running on the system.

:ref:`Shavit-Francez Termination Detection Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` maintains a forest instead of a single tree due to the nature of the distributed system. Each initiator maintains its tree and constitutes it to the forest. The condition for a process to join a tree is that it is not already a member of any of the trees in the forest. Other than that, the algorithm continues as in the Dijkstra-Scholten Algorithm. Instead, it starts a wave in which only those processes not part of a tree participate. Because each initiator is only aware of the emptiness of its tree, an empty tree does not guarantee that the whole forest is empty. The wave algorithm ensures that all the trees in the forest collapse before announcing termination. Once the wave decides, the initiator can then announce the termination. A wave algorithm is not complete unless all the processes take part in its execution. Following this property, the algorithm ensures that if none of the waves started by the processes are complete because a process refuses to take part, the initiator maintaining the last tree to be empty will start a wave that eventually decides and announces the termination. [Fokking2013]_ 

The wave algorithm we choose for the implementation in :ref:`Shavit-Francez Termination Detection Algorithm <ShavitFranchesTerminationDetectionAlgorithm>`  is :ref:`Echo Algorithm <EchoAlgorithm>` [Fokking2013]_. The :ref:`Echo Algorithm <EchoAlgorithm>` initiator begins by sending messages to all of its neighbors. If a non-initiator receives a message for the first time, it sets its parent as the sender process and sends a message to all its neighbors except its parent. After receiving messages from all its neighbors, the non-initiator notifies its parent. Finally, the initiator receives messages from all its neighbors and decides.


Shavit-Francez Termination Detection Algorithm: |ShavitFrancezAlg| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. _ShavitFranchesTerminationDetectionAlgorithm:

.. code-block:: RST
    :linenos:
    :caption: Shavit-Francez Termination Detection Algorithm
    
    bool active<p> // set when p becomes active, and reset when p becomes passive
    nat cc<p> // keeps track of the number of children of p in its tree
    proc parent<p> // the parent of p in a tree in the forest
    
    if p is an initiator then
        active<p> <- true
    end if

    if p sends a basic message then
        cc<p> <- cc<p> + 1
    end if

    if p receives a basic message from a neighbor q then
        if active<p> = false then
            active<p> <- true
            parent<p> <- q
        else 
            send <ack> to q
        end if
    end if

    if p receives <ack>
        cc<p> <- cc<p> - 1
        perform procedure LeaveTree<p>
    end if

    if p becomes passive
        active<p> <- false
        perform procedure LeaveTree<p>;
    end if

    Procedure LeaveTree<p>
        if active<p> = false and cc<p> = 0 then
            if parent<p> != ┴ then 
                send <ack> to parent<p>
                parent<p> <- ┴
            else
                start a wave, tagged with p
            end if
        end if
    
    if p receives a wave message then
        if active<p> = false and cc<p> = 0 then
            act according to the wave algorithm
            in the case of a decive event, call Announce
        end if


Echo Algorithm:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. _EchoAlgorithm:

.. code-block:: RST 
    :linenos:
    :caption: Echo Algorithm

    nat received<p>;
    proc parent<p>;

    if p is the initiator then
        send <wave> to each r in Neighbors<p>
    end if
    
    if p receives a <wave> from neighbor q then
        received<p> <- received<p> + 1
        if parent<p> != ┴ and p is a non-initiator then 
            parent<p> <- q
            if |Neighbors<p>| > 1 then
                send <wave> to each r in Neighbors<p>\{q}
            else
                send <wave> to q
            end if
        else if received<p> = |Neighbors<p>| then
            if parent<p> != ┴ then 
                send <wave> to parent<p>
            else
                decide
            end if
        end if
    end if


Example
~~~~~~~~
.. list-table:: 

    * - .. figure:: figures/step1.jpg

           Step 1

      - .. figure:: figures/step2.jpg

           Step 2

    * - .. figure:: figures/step3.jpg

           Step 3
           
      - .. figure:: figures/step4.jpg

           Step 4

    * - .. figure:: figures/step5.jpg

            Step 5

      - .. figure:: figures/step6.jpg

           Step 6

Assume that there are three processes p, q, r in an undirected network. One way to execute the :ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` is as follows:

1. At the start, the initiators p and q both send a basic message to r, and set cc<p> and cc<q> to 1. Next, p and q become passive.(See Figure 1)
2. Upon receipt of the basic message from p, r becomes active and makes p its parent. Next, r receives the basic message from q, and sends back an acknowledgment, which causes q to decrease cc<q> to 0.(See Figure 2)
3. Since q became passive as the root of a tree, and cc<q> = 0, it starts a wave. This wave does not complete, because p and r refuse to participate.(See Figure 3)
4. r sends a basic message to q, and sets cc<r> to 1. Next, r becomes passive.(See Figure 4)
5. Upon receipt of the basic message from r, q becomes active, and makes r its parent. Next, q becomes passive, and sends an acknowledgment to its parent r, which causes r to decrease cc<r> to 0. Since r is passive and cc<r> = 0, it sends an acknowledgment to its parent p, which causes p to decrease cc<p> to 0.(See Figure 5)
6. Since p became passive as the root of a tree, and cc<p> = 0, it starts a wave. This wave completes, so that p calls Announce.(See Figure 6)


Correctness
~~~~~~~~~~~
1. **Safety**: The *Announce* is called when a decision occurs in the wave algorithm. This implies that each process p has sent a wave message or has decided, and the algorithm implies that cc<p> was 0 when p did so. No action makes cc<p> more than 0 again, so (for each p) cc<p> is 0 when *Announce* is called. [Tel2001]_
2. **Liveness**: Assume that the basic computation has terminated. Within a finite number of steps the termination-detection algorithm reaches a terminal configuration, and as in the correctness statement below it can be shown that in this configuration the forest is empty. Consequently, all events of the wave are enabled in every process, and that the configuration is terminal now implies that all events of the wave have been executed, including at least one decision, which caused a call to *Announce*. [Tel2001]_
3. **Correctness**: Define S to be the sum of all cc<p> for each process p. Initially S is zero, S is incremented when a basic message is sent, S is decremented when a control message is received, and S is never negative. This implies that the number of control messages never exceeds the number of basic messages in any computation. [Tel2001]_


Complexity 
~~~~~~~~~~
1. :ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>`: The worst case message complexity  is O(M + W) where M is the number of the messages sent by the underlying computation and W is a message exchange complexity of the wave algorithm, which is 2E for :ref:`Echo Algorithm <EchoAlgorithm>` where E is. [Tel2001]_ 
2. :ref:`Echo Algorithm <EchoAlgorithm>`: The message complexity is O(2E), where E is the number of edges. [Fokking2013]_


References 
~~~~~~~~~~
.. [Shavit1986] Shavit, N. and Francez, N. A new approach to the detection of locally indicative stability. In proc. Int. Colloq. Automata, Languages, and Programming (1986), L. Kott (ed.), vol. 226 of Lecture Notes in Computer Science, Springer-Verlag, pp. 344-358.
.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [Dijkstra1980] Dijkstra, E. W. and Scholten, C. S. Termination detection for diffusing computations. Inf. Proc. Lett. 11, 1 (1980), 1-4.
.. [Tel2001] Tel, G, Introduction To Distributed Algorithms, The Cambridge University Press, Cambridge, United Kingdom, 2001