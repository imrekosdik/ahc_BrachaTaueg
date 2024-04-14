.. include:: substitutions.rst

|ShavitFrancezAlg|
=========================================


Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Global termination in a distributed system occurs when all the processes are in the local termination state and processes do not send or receive any messages. Local termination means a process completes its execution and starts computation again upon receiving any message. Processes under this condition are passive (idle) and become active upon receiving any message. Only the active processes can perform the send event. Therefore, a distributed system terminates when its processes are idle. Note that the act of sending the message and receipt of it is atomic. 

The primary consideration behind the termination detection algorithms is adding a control algorithm to the system running to detect whether the basic algorithm has reached a termination state. [Fokking2013]_ Typically, the control algorithm has two phases: termination detection and the announcement "*Announce*" phase. This announcement algorithm brings the processes in a terminated state. Additionally, the control algorithm receives and sends control messages.  By preference, the termination detection part should not interfere with the ongoing activities in the distributed system and should not need new communication channels between the processes. 

:ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` [Shavit1986]_ is the generalization of Dijkstra-Scholten [Dijkstra1980]_ Termination Detection Algorithm for distributed systems. Maintaining trees of active processes is the core idea behind both algorithms. The difference is that the Dijkstra-Sholten Algorithm maintains a tree for one node, called the initiator, whereas the :ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` maintains a forest of trees, one for each initiator. The iniator nodes are the ones that start the execution of their local algorithms in the event related with the initiator itself. Non-initiator nodes are the ones that become involved in the algorithm only when a message of the algorithm arrives and triggers the execution of the process algorithm. [Tel2001]_. Lastly, the termination is detected when the computation graph, the trees and the messages in transit, is empty.

Distributed Algorithm: |ShavitFrancezAlg| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

F = (V, E) is the computation graph of the algorithm, where

	1. **F** is a forest of which each tree is rooted in an initiator
	2. **V** includes all active processes and the basic messages.

The algorithm terminates when the computation graph becomes empty. Since the algorithm maintains a forest of trees, each initiator is only aware of the emptiness of their own tree. Hovewer, this does not mean that the forest is empty. A single wave verifies that all of the trees have collapsed. A computation of a wave algorithm is a wave. The forest is  managed in a way where a tree, Tp, that becomes empty will remain empty permanently. It's important to note that this doesn't stop the initiator, p, from becoming active again. However, if p does become active again after its tree has collapsed, it will be placed into another initiator's tree. The wave is started by one of the initiators and the wave is tagged with the initator's ID. Only the processes whose tree has collapsed participate to the wave, and when the wave makes a decision, Announce is called. 

Wave Algorithm [Tel2001]_: A wave algorithm is a distributed algorithm that satisfies the following three requirements:

	1. **Termination:** Each computation is finite.
	2. **Decision:** Each computation contains at least one decide event.
	3. **Dependence:** In each computation each decide event is causally preceded by an event in each process.

For this implementation, we choose the Cidon's Depth First Search Algorithm [Fokking2013]_ as the wave algorithm. We do not give the implementation details of this algorithm in this paper, however, we briefly explain the working principle of the algorithm. Starting with the initiator, a process forwards a token to a process which has not yet held the token and it stores the process to which it sends the token to. If, at any point, it receives the token from a process A that has not in its list of forwarded processes, then it just does not take into the token and sets the channel between them as the front edge. The process A itself also sets the channes as the front edge and continues to forward the token to other processes.   

.. _ShavitFranchesTerminationDetectionAlgorithm:

.. code-block:: RST
    :linenos:
    :caption: Shavit-Francez Termination Detection Algorithm
    
    bool active<p> // set when p becomes active, and reset when p becomes passive
    nat cc<p> // keeps track of the number of children of p in its tree
    proc parent<p> // the parent of p in a tree in the forest
    
    If p is an initiator then
        active<p> <- true;
    end if

    If p sends a basic message then
        cc<p> <- cc<p> + 1
    end if

    If p receives a basic message from a neighbor q then
        If active<p> = false then
            active<p> <- true
            parent<p> <- q
        else 
            send <ack> to q
        end if
    end if

    If p receives <ack>
        cc<p> <- cc<p> - 1
        perform procedure LeaveTree<p>
    end if

    If p becomes passive
        active<p> <- false
        perform procedure LeaveTree<p>;
    end if

    Procedure LeaveTree<p>
        If active<p> = false and cc<p> = 0 then
            If parent<p> != ┴ then 
                send <ack> to parent<p>
                parent<p> <- ┴
            else
                start a wave, tagged with p
            end if
        end if
    
    If p receives a wave message then
        If active<p> = false and cc<p> = 0 then
            act according to the wave algorithm
            in the case of a decive event, call Announce
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
2. **Liveness**: Assume that the basic computation has terminated. Within a finite number of steps the termination-detection algorithm reaches a terminal configuration, and as in the correctness statement below it can be shown that in this configuration F is empty. Consequently, all events of the wave are enabled in every process, and that the configuration is terminal now implies that all events of the wave have been executed, including at least one decision, which caused a call to *Announce*. [Tel2001]_
3. **Correctness**: Define S to be the sum of all sun-counts. Initially S is zero, S is incremented when a basic message is sent, S is decremented when a control message is received, and S is never negative. This implies that the number of control messages never exceeds the number of basic messages in any computation. [Tel2001]_

Complexity 
~~~~~~~~~~
The worst case message complexity of the :ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` is O(M + W) where M is the number of the messages sent by the underlying computation and W is a message exchange complexity of the wave algorithm. The algorithm is a worst-case optimal algorithm for termination detection of decentralized computations (if an optimal wave algorithm is supplied). [Tel2001]_ 

.. [Shavit1986] Shavit, N. and Francez, N. A new approach to the detection of locally indicative stability. In proc. Int. Colloq. Automata, Languages, and Programming (1986), L. Kott (ed.), vol. 226 of Lecture Notes in Computer Science, Springer-Verlag, pp. 344-358.
.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [Dijkstra1980] Dijkstra, E. W. and Scholten, C. S. Termination detection for diffusing computations. Inf. Proc. Lett. 11, 1 (1980), 1-4.
.. [Tel2001] Tel, G, Introduction To Distributed Algorithms, The Cambridge University Press, Cambridge, United Kingdom, 2001