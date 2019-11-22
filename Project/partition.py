from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4pydistr.master.variable_container import MasterVariableContainer
from Modules import constants, nodes
import pm4pydistr
import requests
import os

# Event log to be used
event_log = "receipt"


def master_request(request):
    return requests.get(
        "http://" + master.host + ":" + MasterVariableContainer.port + "/" + request + "?keyphrase=" + pm4pydistr.configuration.KEYPHRASE)


if __name__ == "__main__":
    nodes.refresh_directory("master")
    nodes.refresh_directory("training")

    # Import event log and partition it
    log = xes_importer.apply("Event Logs/" + event_log + ".xes")
    parquet_exporter.apply(log, "master",
                           parameters={"auto_partitioning": True, "num_partitions": constants.NUMBER_OF_PARTITIONS})

    # Move the training log to the training folder
    for i in range(int(constants.NUMBER_OF_PARTITIONS * constants.TRAINING_PART), constants.NUMBER_OF_PARTITIONS):
        os.rename("master\\@@partitioning=" + str(i), "training\\@@partitioning=" + str(i))

    # Initialize master and slaves
    master, slaves = nodes.initialize_nodes()

    # Assign event logs to slaves
    master_request("doLogAssignment")

    r = master_request("getSlavesList")

    q = master_request("getSublogsCorrespondence")

    t = master_request("getSublogsId")

    print(t.text)

    print(r.text)

    print(q.text)

