The script "main.py" implements the rudimentary functionality of a slave node.

It should be run on the command line with two arguments: the first one is either "train" or "test", and determines
the executed functionality. The second one determines the name of the event log on which the ensemble will be trained
(without ".xes"). The available event logs can be seen in the "Event Logs" folder (roadtraffic is still not available).

Example: $python main.py train running-example