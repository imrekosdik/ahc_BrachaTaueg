.. include:: substitutions.rst

|BrachaTouegAlg|
=========================================

Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A deadlock occurs when a group of processes waits for each other to acquire resources to continue their execution. One of the deadlock models is N-out-of-M Requests, where N is less than or equal to M. In this model, a process makes M requests and can continue execution only if it obtains at least N resources. 

Wait-for-graphs model the resource dependencies in distributed systems. [Kshemkalyani2008]_ In these graphs, nodes represent processes, and there is a directed edge from one process to another if the first process is waiting to acquire a resource that the second process is currently holding. A process can be either active or blocked. An active process has all the resources it needs and is either executing or ready to execute. On the other hand, a blocked process is waiting to acquire the resources it needs.

An active node in a WFG can send an N-out-of-M request. After sending the request, the node becomes blocked until at least N of the requests are granted. Once the node becomes blocked, it cannot send any more requests. Directed edges are included in the graph to indicate the requests, and they go from the node to each node containing the required resources. As nodes grant the resources to the blocked node, the system removes the directed edges correspondingly. Once N requests are approved, the node becomes active again and sends notifications to M-N nodes to dismiss the remaining requests. After that, the system removes the remaining directed edges accordingly. [Bracha1987]_ [Fokking2013]_

Deadlock detection is a fundamental problem in distributed computing, which requires examining the system’s WFG for cyclic dependencies. For this purpose, the processes in the system periodically check whether the system contains any deadlock by taking a snapshot of the global state of the system.  According to Knapp’s deadlock detection algorithm classification [Knapp1987]_, this approach falls under the global state-based algorithms. These algorithms including the :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>` is based on Lai-Yang Snapshot Algorithm [Fokking2013]_ because the algorithm computes WFG depending on the global snapshot of the system.


Bracha-Toueg Deadlock Detection Algorithm: |BrachaTouegAlg| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`, proposed by Gabriel Bracha and Sam Toueg [Bracha1987]_, aims to detect the deadlocks in the system. The algorithm operates on the N-out-of-M deadlock model and is under the assumption that it is possible to capture the consistent global state of the system without halting the system execution. The algorithm starts execution when a node, named initiator, suspects that it may be in a deadlocked state. This can happen after a long wait for a request to be satisfied. The initiator starts a Lai-Yang snapshot :ref:`Lai-Yang Snapshot Algorithm <LaiYangSnapshotAlgorithm>` to compute the WFG. To differentiate between snapshots invoked by different initiators, the algorithm associates each snapshot, along with its messages, with the initiator's identity. After a node v constructs its snapshot, it computes two sets of nodes:

-  **OUTv**: The set of nodes *u* for which *v*'s request has not been granted or relinquished. 
-  **INv**: The set of nodes requesting a service from *v*, according to *v*’s point of view. The node *v* received requests from a set of nodes, but *v* has not yet granted or dismissed the requests. 

After computing each set of nodes, the algorithm consists of two phases. *Notify* - where processes are notified that the algorithm started execution - and *Grant* in which active processes simulate the granting of requests. 

-  The process initiating the deadlock detection algorithm sends NOTIFY messages to all processes in *Outv*. (Line 2)
-  If the initiator process does not need any resources, it grants its resources to processes needing them by sending *GRANT* messages (Line 19) and makes itself free. (Line 18) It then waits for *ACKNOWLEDGE* messages from these processes indicating that they received the *GRANT* message.(Line 20)
-  After performing the *GRANT* operation, it waits *DONE* messages from the processes it sent *NOTIFY* message to. (Line 7)
-  If a process receives *NOTIFY* from another for the first time, it sends NOTIFY messages to all processes in its *Outv*. (Line 14). Then, it sends *DONE* message to the process sending the *NOTIFY* message. (Line 16)
-  If a process receives *GRANT* message from another, it checks whether it needs additional resources to continue execution. (Line 22). Once it does not need any resources, it grants its resources to waiting processes by executing grant. (Line 25) After that, it sends *ACKNOWLEDGE* message to the process sending the *GRANT* message. (Line 28)
-  Once the initiator process receives done from all processes in *Outv*,(Line 7) it checks the value of *free* and decides whether it is deadlocked. (Line 9)


.. _BrachaTouegDeadlockDetectionAlgorithm:

.. code-block:: RST
    :linenos:
    :caption: Bracha-Toueg Deadlock Detection Algorithm [Fokking2013]_.
    
    Procedure Notify
    notified <- true
    send<notify> to all w ∈  OUT
    if requests = 0 then
	    perform Procedure Grant
	end if
    await<done> from all w ∈ OUT
    if free then:
        conclude that it is not deadlocked
    end if

    Upon receipt by v of Notify from a neighbor w:
    if notified = false then
	    Perform Procedure Notify
    end if
    send<done> to w

    Procedure Grant
    free <- true
    send<grant> to all w ∈ IN
    await<ack> from all w ∈ IN

    Upon receipt by v of Grant from a neighbor w:
    if requests > 0 then
	    requests <- request - 1
        if requests = 0 then
	        Perform procedure Grant
	    end if
    end if
    send<ack> to w


Lai-Yang Snapshot Algorithm:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`, utilizes :ref:`Lai-Yang Snapshot Algorithm <LaiYangSnapshotAlgorithm>` to compute the WFG graph. Therefore, the process starting the deadlock detection algorithm first executes the Lai-Yang snapshot algorithm. The deadlock detection algorithm uses the global state information captured with :ref:`Lai-Yang Snapshot Algorithm <LaiYangSnapshotAlgorithm>` to detect deadlocks. Since this paper focuses on implementing the :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`, we do no explicitly explain the pseudocode given for :ref:`Lai-Yang Snapshot Algorithm <LaiYangSnapshotAlgorithm>` below. We give the pseudocode here since we implemented the algorithm as a part of  :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`. 

.. _LaiYangSnapshotAlgorithm:

.. code-block:: RST
    :linenos:
    :caption: Lai-Yang Snapshot Algorithm [Fokking2013]_
    
    bool recorded
    nat counter[c] for all channels c of p
    mess-set State[c] for all incoming channels of p
    
    if p wants to initiate a snapshot
    perform Procedure TakeSnapshot

    if p sends a basic message m into an outgoing channel c<0>
    send<m,recorded> into c<0>
    if recorded is False then
        counter[c<0>] <- counter[c<0>] + 1
    end if

    if p receives <m, b> through an incomming channel c<0>
    if b = True then
        perform Procedure TakeSnapshot
    else
        counter[c<0>] <- counter[c<0>] - 1 
        if recorded = True then
            State[c<0>] <- State[c<0>] U {m}
            if |State[c]| + 1 = counter[c<0>] for all incoming channels c of p then
                terminate
            end if
        end if
    efficiencynd if

    
    if p receives <presnap, l> through an incoming channel c<0>
    counter[c<0>] <- counter[c<0>] + L
    if |State[c]| + 1 = counter[c<0>] for all incoming channels c of p then
        terminate
    end if 

    Procedure TakeSnapshot
    if recorded = false then
        recorded <- True
        send <presnap, counter<c0>> into each outgoing channel c
        take a local snapshot state of p
    end if 

Example With Deadlock Present in The System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
.. list-table:: 

    * - .. figure:: figures/brachaToueg_Ex1_step1.png

           Step 1

      - .. figure:: figures/brachaToueg_Ex1_step2.png

           Step 2

Assume a system with three processes, P, Q and R. The wait-for graph consists of three 1-out-of-1 requests, has been computed in a snapshot. Initially *requests<P>* = *requests<Q>* = *requests<R>* = 1.
The walkthrough of the :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>` is as follows: 

1. The initiator P, sets *notified<A>* to true and sends <**notify**> to Q. P awaits <**done**> from Q. (See Figure 1) 
2. Q receives <**notify**> from P and sets *notified<Q>* to true. In order to send <**done**> to P, Q sends <**nofity**> to R and awaits <**done**> from R. (See Figure 1) 
3. R receives <**notify**> from Q and sets *notified<R>* to true. In order to send <**done**> to Q, R sends <**nofity**> to P and awaits <**done**> from P. (See Figure 1) 
4. Since *notified<P>* is true, P does not send any <**notify**> messages. It directly sends <**done**> to R. (See Figure 2)
5. R sends <**done**> to Q because R is already notified. (See Figure 2)
6. Q sends <**done**> to P because Q is already notified. (See Figure 2)
7. Once P receives <**done**> from all its OUT, consisting of Q, it checks the *free<A>*, and since *free<P>* is false, it concludes that the resources are never granted and it is deadlocked. 


Example With Deadlock Not Present in The System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: 

    * - .. figure:: figures/brachaToueg_Ex2_step1.png

           Step 1

      - .. figure:: figures/brachaToueg_Ex2_step2.png

           Step 2
           
    * - .. figure:: figures/brachaToueg_Ex2_step3.png

           Step 3
      
      - .. figure:: figures/brachaToueg_Ex2_step4.png

           Step 4

Assume a system with three processes, P, Q and R. The wait-for graph consists of three 1-out-of-1 requests, has been computed in a snapshot. Initially *requests<P>* = 2, *requests<Q>* = 1 and *requests<R>* = 0. 
The walkthrough of the :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>` is as follows: 

1. The initiator P, sets *notified<P>* to true and sends <**notify**> to Q and R. A awaits <**done**> from Q and R. (See Figure 3) 
2. Q receives <**notify**> from P and sets *notified<Q>* to true. In order to send <**done**> to P, Q sends <**nofity**> to R and awaits <**done**> from R. (See Figure 3) 
3. R receives <**notify**> from Q and P and sets *notified<R>* to true. Since requests<R> = 0. It sends <**grant**> to P and R and awaits <**ack**> from them. (See Figure 4) 
4. P receives <**grant**> from Q and sets *requests<P>* to 1. P sends <**ack**> to Q. (See Figure 4) 
5. Q receives <**grant**> from R and sets *requests<Q>* to 0. It first sends <**ack**> to R, and then sends <**grant**> to P. (See Figure 5) 
6. P receives <**grant**> from Q and sets *requests<P>* to 0. It sends <**ack**> to Q. (See Figure 6) 
7. R receives <**ack**> from Q and P, it sends <**done**> to P. (See Figure 6) 
8. Q receives <**ack**> from P, it sends <**done**> to P. (See Figure 6) 
9. P receives <**done**> from Q and R, checks the value of *free<P>* and concludes that it is not deadlocked.

Correctness
~~~~~~~~~~~
Deadlock is detected if and only if the initiator node belongs to a cycle of the WFG. Every process forwards the message to each of its successors in the WFG. Therefore, in a bounded number of steps, the initiator process i receives the message and detects that it is deadlocked. If the initiator does not belong to the cycle, then it will never receive its own message, so deadlock will not be detected. [Ghosh2015]_  

Complexity 
~~~~~~~~~~
1. **Time Complexity:** The :ref:`Bracha-Toueg Deadlock Detection <BrachaTouegDeadlockDetectionAlgorithm>` has time complexity of 4 * d hops, where d is the diameter of a given WFG. [Kshemkalyani1994]_
2. **Message Complexity:** In thhe :ref:`Bracha-Toueg Deadlock Detection <BrachaTouegDeadlockDetectionAlgorithm>`, at most four messages are sent over each edge, i.e., at most a total of 4e mes- sages are sent. The size of each message is a small constant number of bits. A node v of degree k needs o(k) bits of local storage, and spends o(k) time in local computation. [Bracha1987]_


.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [Bracha1987] G. Bracha and S. Toeug, "Distributed Deadlock detection". Distributed Comput., vol. 2, pp. 127-138, 1987
.. [Kshemkalyani2008] Ajay D. Kshemkalyani, Mukesh Singhal, Distributed Computing: Principles, Algorithms and Systems, Cambridge Univeristy Press, New York, USA, 2008 
.. [Kshemkalyani1994] A. D. Kshemkalyani and M. Singhal, "Efficient detection and resolution of generalized distributed deadlocks," in IEEE Transactions on Software Engineering, vol. 20, no. 1, pp. 43-54, Jan. 1994,
.. [Knapp1987] E. Knapp, "Deadlock Detection in Distributed Databases", ACM Computing Surveys, Volume 19, Issue 4, pp 303-328, 1987
.. [Ghosh2015] S. Ghosh, "Distributed Systems: An Algorithmic Approach, 2nd Edition", CRC Press pp. 184, 2015