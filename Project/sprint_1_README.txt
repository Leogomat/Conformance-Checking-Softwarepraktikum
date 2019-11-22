The script "Project/services.py" tests the base functionalities a slave node offers, which are training a model on an
event log and testing it. These functionalities are implemented in the module "Modules/func.py". The script should be run with the arguments "train" or "test", in order to specify the desired
functionality to be tested. The default event log is "receipt.xes", but it can be changed in the variable "event_log".

The script "Project/partition.py" tests the initialization of a master and a slave node (implemented in the module "Modules/nodes.py"), as well as the partitioning of an event log (also specified in the variable "event_log") and the assignment of the logs to the slave.
Here we also separate part of the partitioned event log for training, hence moving 20% of the event log to the folder
"Project/training".
