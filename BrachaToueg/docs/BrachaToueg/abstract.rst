.. include:: substitutions.rst
========
Abstract
========

In distributed systems, deadlocks occur due to resource sharing - the concept determines how existing resources are shared and accessed across the system. A deadlock is a condition that the processes request access to resources held by other processes in the system. Resolving the deadlocks is crucial because the processes involved are blocked and waiting indefinitely to acquire resources from the others. Deadlock handling is a challenging problem in distributed systems because no site knows the system state, and the communication involves finite and unpredictable delays. :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>` offers a simple and efficient way of detecting deadlocks in distributed systems. Implementing :ref:`Bracha-Toueg Deadlock Detection Algorithm <BrachaTouegDeadlockDetectionAlgorithm>`, along with analyzing the message and time complexity by running the algorithm on different network topologies and various numbers of nodes, provides valuable insights into the algorithm's wide-range applicability due to its efficiency and scalability. 
