The script "Project/services.py" implements the base functionalities a slave node offers, which are training a model on an
event log and testing it. The script should be run with the arguments "train" or "test", in order to specify the desired
functionality. The default event log is "receipt.xes", but it can be changed in the variable "event_log".

The script "Project/partition.py" implements the initialization of a master and a slave node, as well as the
partitioning of an event log (also specified in the variable "event_log") and the assignment of the logs to the slave.
Here we also separate part of the partitioned event log for training, hence moving 20% of the event log to the folder
"Project/training".