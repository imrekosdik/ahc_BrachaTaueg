.. include:: substitutions.rst

|ShavitFranchezAlg|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Global termination in a distributed system occurs when all the processes are in the local termination state and processes do not send or receive any messages. Local termination means a process completes its execution and starts computation again upon receiving any message. Processes under this condition are passive (idle) and become active upon receiving any message. Only the active processes can perform the send event. Therefore, a distributed system terminates when its processes are idle. Note that the act of sending the message and receipt of it is atomic. 

The primary consideration behind the termination detection algorithms is adding a control algorithm to the system running to detect whether the basic algorithm has reached a termination state. [Fokking2013]_Typically, the control algorithm has two phases: termination detection and the announcement "*Announce*" phase. This announcement algorithm brings the processes in a terminated state. Additionally, the control algorithm receives and sends control messages.  By preference, the termination detection part should not interfere with the ongoing activities in the distributed system and should not need new communication channels between the processes. 

:ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` [Shavit1986]_ is the generalization of Dijkstra-Scholten [Dijkstra1980]_ Termination Detection Algorithm for distributed systems. Maintaining trees of active processes is the core idea behind both algorithms. The difference is that the Dijkstra-Sholten Algorithm maintains a tree for one node, called the initiator, whereas the :ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>`  maintains a forest of trees, one for each initiator. Except the algorithm is mostly the same as the Dijkstra-Sholten algorithm. The termination is detected when the computation graph, the trees and the messages in transit, is empty.


Distributed Algorithm: |ShavitFranchezAlg| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _ShavitFranchesTerminationDetectionAlgorithm:

.. code-block:: RST
    :linenos:
    :caption: Shavit-Francez Termination Detection Algorithm.
    
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
            act accrding to the wave algorithm
            in the case of a decive event, call Announce
        end if


Example
~~~~~~~~



Correctness
~~~~~~~~~~~
1. **Safety**: The *Announce* is called when a decision occurs in the wave algorithm. This implies that each process p has sent a wave message or has decided, and the algorithm implies that empty_p was true when p did so. No action makes empty_p false again, so (for each p) empty_p is true when *Announce* is called.[Tel2001]_
2. **Liveness**: Assume that the basic computation has terminated. Within a finite number of steps the termination-detection algorithm reaches a terminal configuration, and as in the correctness statement below it can be shown that in this configuration F is empty. Consequently, all events of the wave are enabled in every process, and that the configuration is terminal now implies that all events of the wave have been executed, including at least one decision, which caused a call to *Announce*.[Tel2001]_
3. **Correctness**: Define S to be the sum of all sun-counts. Initially S is zero, S is incremented when a basic message is sent, S is decremented when a control message is received, and S is never negative.This implies that the number of control messages never exceeds the number of basic messages in any computation.[Tel2001]_

Complexity 
~~~~~~~~~~
The worst case message complexity of the :ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` is O(M + W) where M is the number of the messages sent by the underlying computation and W is a message exchange complexity of the wave algorithm. The algorithm is a worst-case optimal algorithm for termination detection of decentralized computations (if an optimal wave algorithm is supplied).[Tel2001]_ 

.. [Shavit1986] Shavit, N. and Francez, N. A new approach to the detection of locally indicative stability. In proc. Int. Colloq. Automata, Languages, and Programming (1986), L. Kott (ed.), vol. 226 of Lecture Notes in Computer Science, Springer-Verlag, pp. 344-358.
.. [Kshemkalyani2008] Ajay D. Kshemkalyani, Mukesh Singhal, Distributed Computing: Principles, Algorithms and Systems, Cambridge Univeristy Press, New York, USA, 2008 
.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [Dijkstra1980] Dijkstra, E. W. and Scholten, C. S. Termination detection for diffusing computations. Inf. Proc. Lett. 11, 1 (1980), 1-4.
.. [Tel2001] Tel, G, Introduction To Distributed Algorithms, The Cambridge University Press, Cambridge, United Kingdom, 2001