.. include:: substitutions.rst

Conclusion
==========

The Shavit-Francez algorithm is a reliable and versatile solution for detecting the termination of distributed computations across various network topologies. In our research, we have emphasized the importance of this algorithm by exploring its implementation details and analyzing its message complexity. Our study of the algorithm's message complexity has revealed its favorable features. Using the ad-hoc computing library, we observed a message complexity of O(M + 2E), where M represents the complexity of the fundamental computation. Our experimental results closely match this complexity measure, highlighting the algorithm's efficiency and low overhead in actual distributed systems. If the algorithm is included in the ad-hoc computing library, anyone can use it in their research. We discussed how we implemented the underlying computation logic in Section 1.4.3. In future work, we could approach the issue differently and change the implementation to accept any message kind to reflect the variety of algorithms and make the message-passing mechanism independent from the termination-detection algorithm.
