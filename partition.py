from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.importer.parquet import factory as parquet_importer
from pm4pydistr.master.variable_container import MasterVariableContainer
from Modules import constants, nodes
from 
import requests
import time
import os

# Event log to be used
event_log = "receipt"


def master_request(request):
    return requests.get(
        "http://" + pm4pydistr.configuration.MASTER_HOST + ":" + MasterVariableContainer.port + "/" + request +
        "?keyphrase=" + pm4pydistr.configuration.KEYPHRASE + "&process=@@partitioning=0")


def slave_request(request, index):
    return requests.get(
        "http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(5002 + index) + "/" + request + "?keyphrase=" +
        pm4pydistr.configuration.KEYPHRASE)


if __name__ == "__main__":
    nodes.refresh_directory("master")
    nodes.refresh_directory("testing")

    # Import event log and partition it
    log = xes_importer.apply("Data/Event Logs/" + event_log + ".xes")
    parquet_exporter.apply(log, "master",
                           parameters={"auto_partitioning": True, "num_partitions": constants.NUMBER_OF_PARTITIONS})

    # Move the training log to the training folder
    for i in range(int(constants.NUMBER_OF_PARTITIONS * constants.TRAINING_PART), constants.NUMBER_OF_PARTITIONS):
        os.rename("master\\@@partitioning=" + str(i), "testing\\@@partitioning=" + str(i))

    # Initialize master and slaves
    master, slaves = nodes.initialize_nodes()

    # Assign event logs to slaves
    master_request("doLogAssignment")

    r = slave_request("doTraining", 0)



