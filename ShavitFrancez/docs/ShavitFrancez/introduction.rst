.. include:: substitutions.rst

Introduction
============

When a problem requires more than one process to be solved, distributed systems are a good candidate. These processes work together to solve subproblems. Therefore, it is crucial to identify when a process has completed its execution because its output is used as input to another process to continue its execution. Termination detection in distributed computing is a challenging task in distributed systems because processes are unaware of the global state of the system due to communication delays, and there is no shared global system.

Termination detection algorithms have a significant role in ensuring a consistent state where all processes complete their computations and are ready to proceed with the upcoming tasks. Achieving a consistent state also preserves the correctness of the system. Termination detection can also take part in efficient resource management by releasing not-needed resources. Additionally, efficient resource management may be beneficial in preventing deadlocks since their primary cause is indefinitely waiting to acquire resources.

Termination is a property of the global state of distributed computing. However, due to the decentralized and asynchronous nature of distributed systems, acquiring the global state of the system is a significant challenge. Since termination detection algorithms rely on additional control messages, the message overhead can thoroughly impact the system's performance. Also, as the distributed system expands, the complexity and overhead of maintaining the algorithm can result in scalability issues. Additionally, designing algorithms such that the underlying computation does not interfere with the ongoing executions is another challenge.

:ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` is an effective way to detect termination without interfering with the overall execution of the distributed system. The algorithm doesn't rely on synchronous communication, simplifying the design and implementation of the system. In contrast to the increasing number of nodes, the message-sharing overhead from the algorithm remains low, which means it has less impact on the system's performance. In this paper, we aim to comprehensively explain the implementation details of :ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` and present the results of experiments we conducted on the algorithm related to its time and message complexity.

We contribute to the field of distributed systems by:

    - Implementating :ref:`Shavit-Francez Algorithm <ShavitFrancezTerminationDetectionAlgorithm>` on the AHCv2 platform. We explain the implementation details in Section 1.3.
    - Conducting experiments on the algorithm over different network topologies and node counts. We discuss the experiment setup and results in Section 1.4
