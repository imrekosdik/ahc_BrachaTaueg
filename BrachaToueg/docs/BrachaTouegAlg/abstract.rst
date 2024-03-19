.. include:: substitutions.rst
========
Abstract
========

In distributed systems, deadlocks occur due to resource sharing - the concept determines how existing resources are shared and accessed across the system. A deadlock is a condition that the processes request access to resources held by other processes in the system. Resolving the deadlocks are crucial because processes involved in the deadlock are blocked processes and they are waiting indefinitely to acquire resource from the others. Deadlock handling is a challenging problem in distributed systems because no site knows the system state,  and the communication involves finite and unpredictable delays. Deadlock detection is one of the approaches to handling deadlocks. It involves examining the system if it contains a cyclic wait.  Some proposed deadlock detection algorithms are proven incorrect or too complicated to prove their correctness. The Bracha-Toueg algorithm is a simple and efficient method for the M-OUT-OF-N model and is under global state detection-based algorithms. The main idea behind the algorithm is that deadlocks are detectable by taking a snapshot of the system. Moreover, the algorithm's complexity outperforms the previously introduced algorithms for the AND-OR model.
// TBD: what is my contribution and summarization of the learning points referring to the results.
 
