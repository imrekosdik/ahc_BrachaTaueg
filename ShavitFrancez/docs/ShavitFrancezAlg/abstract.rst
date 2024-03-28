.. include:: substitutions.rst
========
Abstract
========

A computation of a distributed algortihm terminates when the algorithm reaches a state that there are no possible applicable steps. In distributed systems, determining whether a particular computation has terminated is a crucial need because execution of other computations may depend on completion of the computation. Due to the fact that the processes in a distributed system have no knowledge about the global state of the system and do not share any global clock inferring if a distributed computation has ended is a challenging problem. The Shavit-Francez algorithm, is a fundamental termination detection algorithm that addresses these issues, ensuring that the system reaches a consistent state where all the processes completed their computations before proceeding with other tasks. 