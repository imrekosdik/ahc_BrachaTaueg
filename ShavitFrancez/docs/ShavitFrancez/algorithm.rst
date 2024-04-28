.. include:: substitutions.rst

|ShavitFrancezAlg|
=========================================


Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Global termination in a distributed system occurs when all processes reach the local termination state, no messages are in transit, and processes do not send or receive any message. Local termination is the state where the process completed its execution, meaning it is passive (idle) and is ready to continue its computation upon receiving any message. A process is active when it is performing some computation. In a distributed system, only the active processes can send messages. Therefore, a computation in a distributed system terminates when all its processes are idle.

The primary consideration behind the termination detection algorithms is adding a control algorithm to the system running to detect whether the basic algorithm has reached a termination state. The basic algorithm is the one currently running in the distributed system. Initiators of the basic algorithm are active processes and can trigger the execution of the control algorithm. The control algorithm consists of the termination detection and the announcement phases. The messages that the control algorithm sends or receives are control messages. Ideally, the termination detection algorithm should not need additional communication channels to send or receive its control messages, and should not interfere with the basic algorithm running on the system.

:ref:`Shavit-Francez Termination Detection Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` maintains a forest instead of a single tree due to the nature of the distributed system. Each initiator maintains its tree and constitutes it to the forest. The condition for a process to join a tree is that it is not already a member of any of the trees in the forest. Other than that, the algorithm continues as in the Dijkstra-Scholten Algorithm. Instead, it starts a wave in which only those processes not part of a tree participate. Because each initiator is only aware of the emptiness of its tree, an empty tree does not guarantee that the whole forest is empty. The wave algorithm ensures that all the trees in the forest collapse before announcing termination. Once the wave decides, the initiator can then announce the termination. A wave algorithm is not complete unless all the processes take part in its execution. Following this property, the algorithm ensures that if none of the waves started by the processes are complete because a process refuses to take part, the initiator maintaining the last tree to be empty will start a wave that eventually decides and announces the termination. [Fokking2013]_ 


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