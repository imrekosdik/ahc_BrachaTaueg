.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We utilized the Python (version 3.12) scripting language and the Ad-Hoc Computing (adhoccomputing) library while implementing the Bracha-Toueg Detection Algorithm. We also employed the networkx library to generate various network topologies and the matplotlib library to visualize them. Each component in the topology can be the initiator for the deadlock detection algorithm. We implemented a function for which we can simulate processes requesting resources from one another. This function "send_request_to_component" is called for processes before starting the deadlock detection algorithm by sending "DETECTDEADLOCK" event to the initiator process. Once we started the deadlock detection algorithm, we first take the Lai-Yang snapshot of the initiator process. We are only interested in the exchanged "REQUEST" messages for deadlock detection, so we ignore other types of exchanged messages. Once the initiator process completes the Lai-Yang snapshot algorithm, it uses its previously recorded state to understand what processes it is waiting to receive resources and what processes waiting for it to grant resources. This means that, the initiator process computes a WFG graph for itself. Then, it continues with notifying the processes in "OUT" and waits for receiving DONE message from all of them. Once it receives DONE from all processes in OUT, it checks whether it is deadlocked by looking at its local variable "free". An importing to mention here is that, the grant procedure is embedded inside the notify. This enables a process to need to receive ACKNOWLEDGE messages from all processes in IN, before sending any "DONE" messages. 

If there is a cyclic dependency in the WFG, then we should expect that, the variable "free" for the initiator process can never be True. If there is no cyclic dependency in the WFG involving the initiator process, than we see that the variable "free" becomes True because the initiator process is able to grant some resources to other processes.

We implemented the Lai-Yang Snapshot Algorithm and the Bracha-Toueg Deadlock Detection Algorithm by employing the pseudocode descriptions given by in [Fokking2013]_. We used the same message types given in the descriptions to achieve the message passing between the components. The make the component who is the initiator of the basic algorithm send itself "DETECTDEADLOCK" message to trigger the algorithm. Depending on whether the initiator process can set the variable "free" to True, the algorithm detects the deadlock. 

Results
~~~~~~~~

Discussion
~~~~~~~~~~
