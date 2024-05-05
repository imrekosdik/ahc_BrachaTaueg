.. include:: substitutions.rst

Introduction
============

Distributed systems are desirable because they allow resource sharing, a critical concept that determines how existing resources are shared and accessed across the network. However, resource sharing comes at a price - namely, deadlocks. A deadlock is a condition that the processes request access to resources held by other processes in the system. Deadlocks can cause significant delays and affect the system's performance, making it crucial to resolve them as soon as possible. 

Deadlock detection algorithms are crucial and intriguing due to their role in concurrency and control mechanisms in distributed systems. Since they help identify and resolve the deadlocks, they prevent system failures and waste of resources. Moreover, they improve the system’s reliability by resolving the deadlocks. The absence of deadlock detection algorithms causes execution halts since deadlocks state that the processes cannot continue their work. Also, it wastes resources because resources held by the processes are neither used nor released. Therefore, this can affect the system’s scalability, response time, and throughput. Overall, deadlocks are inherent risks in concurrent and distributed computing environments, and effective detection mechanisms are essential for mitigating their impact and ensuring the smooth operation of distributed applications.

Deadlock detection is a challenging problem due to various reasons. Because deadlock detection requires storing the system state as a graph, the lack of shared memory becomes a bottleneck for constructing and maintaining the graphs. Another issue is to ensure that each process needs to have an accurate knowledge of the system state. However, in distributed systems, communication delays and failures are almost inevitable. Since distributed systems are large and complex, designing an efficient and scalable deadlock detection algorithm is also challenging. To conclude, naive approaches fail due to scalability, lack of global knowledge, and communication delays. 

Several deadlock detection algorithms for distributed systems were proposed other than the :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`. Some of those algorithms were proven incorrect, and proof of the others was too complex. The complexity of these algorithms comes from the nature of the distributed systems. What makes the Bracha-Taueg special is that its time and space complexity is lower than the best previously known deadlock detection algorithm. It also overcomes the challenges of the dynamic system environment by taking a snapshot of the system and then running the algorithm on that snapshot. This approach does not affect the system throughput since the cycle detection process can proceed concurrently with other system activities. 

The :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`, is a global state-based deadlock detection algorithm, assuming that a consistent global state is determinable without suspending or halting the system. One notable aspect of this algorithm is its ability to provide each process with knowledge of whether or not it is in a deadlocked state, as it always terminates. 

Our primary contributions consist of the following: 

    -  Implementation of the :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>` on the AHCv2 platform. 
    -  Examination of the performance of the algorithm across diverse topologies and usage scenarios.

   