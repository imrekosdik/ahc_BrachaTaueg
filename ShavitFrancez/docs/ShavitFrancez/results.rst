.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
I utilized the *Python* (version 3.12) scripting language and the Ad-Hoc Computing (*adhoccomputing*) library while implementing the Shavit-Francez Termination Detection Algorithm. I also employ the *networkx* library to generate various network topologies and the *matplotlib* library to visualize them. Each component in the topology can be the initiator for the termination detection algorithm. It is up to us which component to choose the initiator/initiators. Once we select the initiator component, we must provide the component instance number of the initiator to the other nodes in the topologies before triggering the termination-detection algorithm. After that, we must send an event to the initiators to execute the termination detection algorithm. Either initiator components can send the event to themselves, or other non-initator nodes can send it to the initiators. Additionally, we created a message by which sending the message makes the process transition to the passive state to simulate processes finishing their execution. 


Results
~~~~~~~~

Discussion
~~~~~~~~~~
