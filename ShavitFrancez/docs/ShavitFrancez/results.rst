.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We utilized the *Python* (version 3.12) scripting language and the Ad-Hoc Computing (*adhoccomputing*) library while implementing the Shavit-Francez Termination Detection Algorithm. We also employed the *networkx* library to generate various network topologies and the *matplotlib* library to visualize them. Each component in the topology can be the initiator for the termination detection algorithm. It is up to us which component to choose the initiator/initiators. After that, we must send an event to the initiators to execute the termination detection algorithm. Either initiator components can send the event to themselves, or other non-initator nodes can send it to the initiators. Since termination detection is the algorithm that runs on top of the basic algorithm running in the system, we needed to simulate a basic algorithm by creating additional messages that we could send to the component externally. We use "*BECOMEPASSIVE*" message to simulate processes finishing their execution and "*SENDBASICMESSAGE*" to simulate messages that the basic algorithm exchanges on its execution. An important consideration is that one can only send these messages if the process is active. Another consideration is that, the components need to be aware of who is executing the control algorithm. Therefore, the process starting the algorithm send a message to its neighbors indicating that it is the initiator for this execution.

For a distributed system in that its processes never become passive, we should expect that the algorithm does not announce the termination and, therefore, no output in the command prompt. As an example, we can consider a system with deadlocks. Since none of the processes can continue because they need resources from others, the algorithm cannot announce the termination. To create this scenario, we could think that the "SENDBASICMESSAGE" event acts as a "REQUEST" and create a cyclic graph. In other cases, sending a "BECOMEPASSIVE" event to a process acts as if the process finishing its execution, and we should see that the algorithm announces the termination in the commant prompt.

We implemented both the Echo Algorithm and the Shavit-Francez Termination Detection Algorithm by employing the pseudocode descriptions given in [Fokking2013]_. We used the same message types given in the descriptions to achieve the message passing between the components. The make the component who is the initiator of the basic algorithm send itself "DETECTTERMINATION" message to trigger the algorithm. After that, depending on the basic-messages exchanged between the processes and the status of the processes, the algorithm announces the termination.

Results
~~~~~~~~



Discussion
~~~~~~~~~~
