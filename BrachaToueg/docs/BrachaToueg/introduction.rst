.. include:: substitutions.rst

Introduction
============

Distributed systems are desirable because they allow resource sharing, a critical concept determining how existing resources are shared and accessed across the network. However, resource sharing comes at a price - namely, deadlocks. A deadlock is a condition that the processes request access to resources held by other processes in the system. Deadlocks can cause significant delays and affect a distributed system's performance, making it crucial to resolve them as soon as possible.

Deadlock detection algorithms are crucial due to their role in concurrency and control mechanisms in distributed systems. Since they help identify and resolve the deadlocks, they prevent system failures and waste of resources. Moreover, they improve systems' reliability by contributing to deadlock resolution. The absence of deadlock detection algorithms causes execution halts since deadlocks state that the processes cannot continue their work. Also, it wastes resources because resources held by the processes are neither used nor released. Therefore, this can affect a system's scalability, response time, and throughput. Overall, deadlocks are inherent risks in concurrent and distributed computing environments, and effective detection mechanisms are essential for mitigating their impact and ensuring the smooth operation of distributed applications.

Because deadlock detection requires storing the system state as a graph, the lack of shared memory becomes a bottleneck for constructing and maintaining the graphs. Another issue is to ensure that each process needs to have an accurate knowledge of the system state. However, in distributed systems, communication delays and failures are almost inevitable. Since distributed systems are large and complex, designing an efficient and scalable deadlock detection algorithm is also challenging. 

In this paper, we aim to thoroughly explain the implementation details of :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`, discuss how the algorithm overcomes the challenges arising from the nature of distributed systems, and present the results of experiments we conducted on the algorithm related to its time and message complexity. The experiments prove the algorithm is a valuable asset in detecting deadlocks due to its efficiency and simplicity.

We contribute to the field of distributed systems by:

    - Implementating :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>` on the AHCv2 platform. We explain the implementation details in Section 1.3.
    - Conducting experiments on the algorithm over different network topologies and node counts. We discuss the experiment setup and results in Section 1.4 


   