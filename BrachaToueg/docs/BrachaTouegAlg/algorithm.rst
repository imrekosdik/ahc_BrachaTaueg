.. include:: substitutions.rst

|BrachaTouegAlg|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A deadlock occurs when a group of processes waits for each other to acquire resources to continue their execution. One of the deadlock models is N-out-of-M Requests, where N is less than or equal to M. In this model, a process makes M requests and can continue execution only if it obtains at least N resources. 

Wait-for-graphs model the resource dependencies in distributed systems. In these graphs, nodes represent processes, and there is a directed edge from one process to another if the first process is waiting to acquire a resource that the second process is currently holding. A process can be either active or blocked. An active process has all the resources it needs and is either executing or ready to execute. On the other hand, a blocked process is waiting to acquire the resources it needs.

An active node in a WFG can send an N-out-of-M request. After sending the request, the node becomes blocked until at least N of the requests are granted. Once the node becomes blocked, it cannot send any more requests. Directed edges are included in the graph to indicate the requests, and they go from the node to each node containing the required resources. As nodes grant the resources to the blocked node, the system removes the directed edges correspondingly. Once N requests are approved, the node becomes active again and sends notifications to M-N nodes to dismiss the remaining requests. After that, the system removes the remaining directed edges accordingly.

Deadlock detection is a fundamental problem in distributed computing, which requires examining the system’s WFG for cyclic dependencies. For this purpose, the processes in the system periodically check whether the system contains any deadlock by taking a snapshot of the global state of the system. According to Knapp’s deadlock detection algorithm classification, this approach falls under the global state-based algorithms. The Bracha-Toueg deadlock detection algorithm is also one of them. Next, we will discuss the implementation details, the correctness, and the complexity analysis of the Bracha-Toueg algorithm. 


Distributed Algorithm: |BrachaTouegAlg| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Bracha-Toueg Deadlock Detection:ref:`Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`[Bracha1987]_, proposed by Gabriel Bracha and Sam Toueg, aims to detect the deadlocks in the system. The algorithm operates on the N-out-of-M deadlock model and is under the assumption that it is possible to capture the consistent global state of the system without halting the system execution. The algorithm starts execution when a node, named initiator, suspects that it may be in a deadlocked state. This can happen after a long wait for a request to be satisfied. The initiator starts a Lai-Yang snapshot to compute the WFG. To differentiate between snapshots invoked by different initiators, the algorithm associates each snapshot, along with its messages, with the initiator's identity. After a node v constructs its snapshot, it computes two sets of nodes:

OUTv: The set of nodes u for which v's request has not been granted or relinquished.\n
INv: The set of nodes requesting a service from v, according to v’s point of view. The node v received requests from a set of nodes, but v has not yet granted or dismissed the requests. 

After computing each set of nodes, the algorithm consists of two phases. Notify - where processes are notified that the algorithm started execution - and Grant in which active processes simulate the granting of requests. The initiator node starts by sending a notify message to all its outgoing edges and then executes Grant. Other non-initiator nodes that receive the notify message from the initiator execute Notify. Once the nodes become unblocked, they also grant the pending requests by executing Grant. The Grant phase is nested inside the Notify phase. Therefore, Notify terminates only after Grant terminates. It terminates when Notify terminates. At termination, the initiator is not deadlocked if and only if its free value is true. 

.. _BrachaTouegDeadlockDetectionAlgorithm:

.. code-block:: RST
    :linenos:
    :caption: Bracha-Toueg Deadlock Detection Algorithm [Bracha1987]_.
    
    Procedure Notify
    notified <- true
    send<notify> to all w ∈  OUT
    if requests = 0 then
		perform Procedure Grant
	end if
    await<done> from all w ∈ OUT

    Upon receipt by v of Notify from a neighbor w:
    If notified = false then
		Perform Procedure Notify
    end if
    send<done> to w

    Procedure Grant
    free <- true
    send<grant> to all w ∈ IN
    await<ack> from all w ∈ IN

    Upon receipt by v of Grant from a neighbor w:
    If requests > 0 then
		Requests <- requestv – 1
        if requests = 0 then
			Perform procedure Grant
		end if
    end if
    send<ack> to w



Example
~~~~~~~~

Provide an example for the distributed algorithm.

Correctness
~~~~~~~~~~~

Present Correctness, safety, liveness and fairness proofs.


Complexity 
~~~~~~~~~~

Present theoretic complexity results in terms of number of messages and computational complexity.




.. admonition:: EXAMPLE 

    Snapshot algorithms are fundamental tools in distributed systems, enabling the capture of consistent global states during system execution. These snapshots provide insights into the system's behavior, facilitating various tasks such as debugging, recovery from failures, and monitoring for properties like deadlock or termination. In this section, we delve into snapshot algorithms, focusing on two prominent ones: the Chandy-Lamport algorithm and the Lai-Yang algorithm. We will present the principles behind these algorithms, their implementation details, and compare their strengths and weaknesses.

    **Chandy-Lamport Snapshot Algorithm:**

    The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` [Lamport1985]_ , proposed by Leslie Lamport and K. Mani Chandy, aims to capture a consistent global state of a distributed system without halting its execution. It operates by injecting markers into the communication channels between processes, which propagate throughout the system, collecting local states as they traverse. Upon reaching all processes, these markers signify the completion of a global snapshot. This algorithm requires FIFO channels. There are no failures and all messages arrive intact and only once. Any process may initiate the snapshot algorithm. The snapshot algorithm does not interfere with the normal execution of the processes. Each process in the system records its local state and the state of its incoming channels.

    1. **Marker Propagation:** When a process initiates a snapshot, it sends markers along its outgoing communication channels.
    2. **Recording Local States:** Each process records its local state upon receiving a marker and continues forwarding it.
    3. **Snapshot Construction:** When a process receives markers from all incoming channels, it captures its local state along with the incoming messages as a part of the global snapshot.
    4. **Termination Detection:** The algorithm ensures that all markers have traversed the system, indicating the completion of the snapshot.


    .. _ChandyLamportSnapshotAlgorithm:

    .. code-block:: RST
        :linenos:
        :caption: Chandy-Lamport Snapshot Algorithm [Fokking2013]_.
                
        bool recordedp, markerp[c] for all incoming channels c of p; 
        mess-queue statep[c] for all incoming channels c of p;

        If p wants to initiate a snapshot 
            perform procedure TakeSnapshotp;

        If p receives a basic message m through an incoming channel c0
        if recordedp = true and markerp[c0] = false then 
            statep[c0] ← append(statep[c0],m);
        end if

        If p receives ⟨marker⟩ through an incoming channel c0
            perform procedure TakeSnapshotp;
            markerp[c0] ← true;
            if markerp[c] = true for all incoming channels c of p then
                terminate; 
            end if

        Procedure TakeSnapshotp
        if recordedp = false then
            recordedp ← true;
            send ⟨marker⟩ into each outgoing channel of p; 
            take a local snapshot of the state of p;
        end if


    **Example**

    DRAW FIGURES REPRESENTING THE EXAMPLE AND EXPLAIN USING THE FIGURE. Imagine a distributed system with three processes, labeled Process A, Process B, and Process C, connected by communication channels. When Process A initiates a snapshot, it sends a marker along its outgoing channel. Upon receiving the marker, Process B marks its local state and forwards the marker to Process C. Similarly, Process C marks its state upon receiving the marker. As the marker propagates back through the channels, each process records the messages it sends or receives after marking its state. Finally, once the marker returns to Process A, it collects the markers and recorded states from all processes to construct a consistent global snapshot of the distributed system. This example demonstrates how the Chandy-Lamport algorithm captures a snapshot without halting the system's execution, facilitating analysis and debugging in distributed environments.


    **Correctness:**
    
    *Termination (liveness)*: As each process initiates a snapshot and sends at most one marker message, the snapshot algorithm activity terminates within a finite timeframe. If process p has taken a snapshot by this point, and q is a neighbor of p, then q has also taken a snapshot. This is because the marker message sent by p has been received by q, prompting q to take a snapshot if it hadn't already done so. Since at least one process initiated the algorithm, at least one process has taken a snapshot; moreover, the network's connectivity ensures that all processes have taken a snapshot [Tel2001]_.

    *Correctness*: We need to demonstrate that the resulting snapshot is feasible, meaning that each post-shot (basic) message is received during a post-shot event. Consider a post-shot message, denoted as m, sent from process p to process q. Before transmitting m, process p captured a local snapshot and dispatched a marker message to all its neighbors, including q. As the channels are FIFO (first-in-first-out), q received this marker message before receiving m. As per the algorithm's protocol, q took its snapshot upon receiving this marker message or earlier. Consequently, the receipt of m by q constitutes a post-shot event [Tel2001]_.

    **Complexity:**

    1. **Time Complexity**  The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` takes at most O(D) time units to complete where D is ...
    2. **Message Complexity:** The Chandy-Lamport :ref:`Algorithm <ChandyLamportSnapshotAlgorithm>` requires 2|E| control messages.


    **Lai-Yang Snapshot Algorithm:**

    The Lai-Yang algorithm also captures a consistent global snapshot of a distributed system. Lai and Yang proposed a modification of Chandy-Lamport's algorithm for distributed snapshot on a network of processes where the channels need not be FIFO. ALGORTHM, FURTHER DETAILS

.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [Tel2001] Gerard Tel, Introduction to Distributed Algorithms, CAMBRIDGE UNIVERSITY PRESS, 2001
.. [Lamport1985] Leslie Lamport, K. Mani Chandy: Distributed Snapshots: Determining Global States of a Distributed System. In: ACM Transactions on Computer Systems 3. Nr. 1, Februar 1985.