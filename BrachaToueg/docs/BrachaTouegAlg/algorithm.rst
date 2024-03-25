.. include:: substitutions.rst

|BrachaTouegAlg|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A deadlock occurs when a group of processes waits for each other to acquire resources to continue their execution. One of the deadlock models is N-out-of-M Requests, where N is less than or equal to M. In this model, a process makes M requests and can continue execution only if it obtains at least N resources. 

Wait-for-graphs model the resource dependencies in distributed systems.[Kshemkalyani2008]_ In these graphs, nodes represent processes, and there is a directed edge from one process to another if the first process is waiting to acquire a resource that the second process is currently holding. A process can be either active or blocked. An active process has all the resources it needs and is either executing or ready to execute. On the other hand, a blocked process is waiting to acquire the resources it needs.

An active node in a WFG can send an N-out-of-M request. After sending the request, the node becomes blocked until at least N of the requests are granted. Once the node becomes blocked, it cannot send any more requests. Directed edges are included in the graph to indicate the requests, and they go from the node to each node containing the required resources. As nodes grant the resources to the blocked node, the system removes the directed edges correspondingly. Once N requests are approved, the node becomes active again and sends notifications to M-N nodes to dismiss the remaining requests. After that, the system removes the remaining directed edges accordingly.[Bracha1987]_[Fokking2013]_

Deadlock detection is a fundamental problem in distributed computing, which requires examining the system’s WFG for cyclic dependencies. For this purpose, the processes in the system periodically check whether the system contains any deadlock by taking a snapshot of the global state of the system. According to Knapp’s deadlock detection algorithm classification, this approach falls under the global state-based algorithms. The Bracha-Toueg deadlock detection algorithm is also one of them. Next, we will discuss the implementation details, the correctness, and the complexity analysis of the Bracha-Toueg algorithm. 


Bracha-Toueg Deadlock Detection Algorithm: |BrachaTouegAlg| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Bracha-Toueg Deadlock Detection:ref:`Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`[Bracha1987]_, proposed by Gabriel Bracha and Sam Toueg, aims to detect the deadlocks in the system. The algorithm operates on the N-out-of-M deadlock model and is under the assumption that it is possible to capture the consistent global state of the system without halting the system execution. The algorithm starts execution when a node, named initiator, suspects that it may be in a deadlocked state. This can happen after a long wait for a request to be satisfied. The initiator starts a Lai-Yang snapshot to compute the WFG. To differentiate between snapshots invoked by different initiators, the algorithm associates each snapshot, along with its messages, with the initiator's identity. After a node v constructs its snapshot, it computes two sets of nodes:

1. **OUTv**: The set of nodes *u* for which *v*'s request has not been granted or relinquished. 
2. **INv**: The set of nodes requesting a service from *v*, according to *v*’s point of view. The node *v* received requests from a set of nodes, but *v* has not yet granted or dismissed the requests. 

After computing each set of nodes, the algorithm consists of two phases. *Notify* - where processes are notified that the algorithm started execution - and *Grant* in which active processes simulate the granting of requests. The *initiator* node starts by sending a notify message to all its outgoing edges and then executes *Grant*. Other non-initiator nodes that receive the notify message from the initiator execute *Notify*. Once the nodes become unblocked, they also grant the pending requests by executing *Grant*. The *Grant* phase is nested inside the *Notify* phase. Therefore, *Notify* terminates only after *Grant* terminates. It terminates when *Notify* terminates. At termination, the *initiator* is not deadlocked if and only if its *free* value is true. 

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
		requests <- requestv – 1
        if requests = 0 then
			Perform procedure Grant
		end if
    end if
    send<ack> to w


Example
~~~~~~~~

.. list-table:: 

    * - .. figure:: figures/bracha_example_step1.jpg

           Fig 1. Step 1

      - .. figure:: figures/bracha_example_step2.jpeg

           Fig 2. Step 2

Assume a system with three processes, A, B and C. The wait-for graph consists of three 1-out-of-1 requests, has been computed in a snapshot. Initially *requests<A>* = *requests<B>* = *requests<C>* = 1 
The walkthrough of Bracha-Toueg:ref:`Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`[Bracha1987]_ is as follows: 

1. The initiator A, sets *notified<A>* to true and sends <**notify**> to B. A awaits <**done**> from B. (See Figure 1) 
2. B receives <**notify**> from A and sets *notified<B>* to true. In order to send <**done**> to A, B sends <**nofity**> to C and awaits <**done**> from C. (See Figure 1) 
3. C receives <**notify**> from B and sets *notified<C>* to true. In order to send <**done**> to B, C sends <**nofity**> to A and awaits <**done**> from A. (See Figure 1) 
4. Since *notified<A>* is true, A does not send any <**notify**> messages. It directly sends <**done**> to C. (See Figure 2)
5. C sends <**done**> to B because C is already notified. (See Figure 2)
6. B sends <**done**> to A because B is already notified. (See Figure 2)
7. Once A receives <**done**> from all its OUT, consisting of B, it checks the *free<A>*, and since *free<A>* is false, it concludes that the resources are never granted and it is deadlocked. 
  
 
Correctness
~~~~~~~~~~~

 
Complexity 
~~~~~~~~~~
1. **Time Complexity:** The Bracha-Toueg:ref:`Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`[Bracha1987]_  has time complexity of 4 * d hops, where d is the diameter of a given WFG.[Kshemkalyani1994]_
2. **Message Complexity:**The Bracha-Toueg:ref:`Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`[Bracha1987]_  has message complexity of 4 * e messages, where e is the number of the edges in a given WFG.[Kshemkalyani1994]_


.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
.. [Bracha1987] G. Bracha and S. Toeug, "Distributed Deadlock detection". Distributed Comput., vol. 2, pp. 127-138, 1987.
.. [Kshemkalyani2008] Ajay D. Kshemkalyani, Mukesh Singhal, Distributed Computing: Principles, Algorithms and Systems, Cambridge Univeristy Press, New York, USA, 2008 
.. [Kshemkalyani1994] A. D. Kshemkalyani and M. Singhal, "Efficient detection and resolution of generalized distributed deadlocks," in IEEE Transactions on Software Engineering, vol. 20, no. 1, pp. 43-54, Jan. 1994,

