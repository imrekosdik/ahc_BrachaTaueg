.. include:: substitutions.rst

Introduction
============

When a problem requires more than one process to be solved, distributed systems come in handy. These processes work together to solve subproblems. Therefore, it is crucial to identify when a process has completed its execution because its output is used as input to another process to continue its execution. Termination detection in distributed computing is a challenging task in distributed systems because processes are unaware of the global state of the system due to communication delays, and there is no shared global system.

Termination detection algorithms are both interesting and important because they have a significant role in ensuring a consistent state where all processes finished their computations and are ready to proceed with the upcoming tasks. Achieving a consistent state also preserves the correctness of the system. Since resources are shared by many processes in distributed systems, termination detection can also take part in efficient resource management by releasing resources that are no longer needed. Additionally, efficient resource management may  also be useful in preventing deadlocks since the main cause of deadlocks is indefinitely waiting to acquire resources.  

Termination is a property of the global state of distributed computing. However, due to the decentralized and asynchronous nature of distributed systems, acquiring the global state of the system is a significant challenge. Naive approaches fail due to the issues related to scalability, concurrency, consistency, and fault tolerance. Since termination detection algorithms rely on additional control messages, the message overhead can greatly impact the performance of the system. Also, as the distributed system expands, the complexity and overhead of maintaining the algorithm can increase resulting in scalability issues. Additionally, designing algorithms such that the underlying computation does not interfere with the ongoing executions is another challenge.  

The challenge in detecting termination lies in distributed computing. Previous attempts may have failed due to the complexities arising from concurrency management, achieving scalability, and communication delays. Unlike the previous attempts, The Shavit-Francez Algorithm is not constrained by predetermined processor setups, doesn't rely on synchronized communication or basic computation, and doesn't depend on global information in any process.  Moreover, the :ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` is a worst-case optimal algorithm.

The :ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` is an effective way to detect termination without interfering with the overall execution of the distributed system. The algorithm doesn't rely on synchronous communication, simplifying the design and implementation of the system. In contrast to the increasing number of nodes, the message-sharing overhead from the algorithm remains low, which means it has less impact on the system's performance. In summary, the :ref:`Shavit-Francez Algorithm <ShavitFranchesTerminationDetectionAlgorithm>` is a foundational method for detecting termination in distributed computing.

Our primary contributions consist of the following: 

    -  Implementation of the :ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` on the AHCv2 platform. 
    -  Examination of the performance of the algorithm across diverse topologies and usage scenarios.
