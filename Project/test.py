from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4pydistr.master.variable_container import MasterVariableContainer
from pm4pydistr.master.master import Master
from pm4pydistr.slave.slave import Slave
import pm4pydistr
import requests
import json
import time
import shutil
import argparse
import os


# First events of a trace for testing the prediction
test_events = {
    "receipt": {'org:group': 'EMPTY',
                'concept:instance': 'task-20635',
                'org:resource': 'Resource17',
                'concept:name': 'Confirmation of receipt',
                'time:timestamp': '2011-04-21 15:55:07.600000',
                'lifecycle:transition': 'complete'},

    "roadtraffic100traces": {'amount': 32.8,
                             'org:resource': '820',
                             'dismissal': 'NIL',
                             'concept:name': 'Create Fine',
                             'vehicleClass': 'M',
                             'totalPaymentAmount': 0.0,
                             'lifecycle:transition': 'complete',
                             'time:timestamp': '2001-09-26 00:00:00',
                             'article': 171.0,
                             'points': 0.0,
                             'notificationType': None,
                             'lastSent': None}
}


# Clean a folder of its files
def refresh_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)


if __name__ == "__main__":
    # Refresh the master and training folders
    refresh_directory("master")
    refresh_directory("testing")

    # Declare parser for taking command line arguments
    parser = argparse.ArgumentParser(description="Choose functionality")
    parser.add_argument(dest="func", type=str)
    parser.add_argument(dest="evtlog", type=str)
    args = parser.parse_args()

    # Import event log and partition it
    log = xes_importer.apply("Data/Event Logs/" + args.evtlog + ".xes")
    parquet_exporter.apply(log, "master",
                           parameters={"auto_partitioning": True, "num_partitions": pm4pydistr.configuration.NUMBER_OF_PARTITIONS})

    # Move the training log to the training folder
    for i in range(int(pm4pydistr.configuration.NUMBER_OF_PARTITIONS * pm4pydistr.configuration.TRAINING_PART), pm4pydistr.configuration.NUMBER_OF_PARTITIONS):
        shutil.move("master\\@@partitioning=" + str(i), "testing\\@@partitioning=" + str(i))

    # Initialize master and slaves
    m = Master({"host": pm4pydistr.configuration.MASTER_HOST,
                "port": pm4pydistr.configuration.MASTER_PORT,
                "conf": "master"})

    s = {}
    for j in range(pm4pydistr.configuration.NUMBER_OF_SLAVES):
        refresh_directory("slave" + str(j))
        s["slave" + str(j)] = Slave({"host": pm4pydistr.configuration.THIS_HOST,
                                               "port": pm4pydistr.configuration.PORT + j + 1,
                                               "masterhost": pm4pydistr.configuration.MASTER_HOST,
                                               "masterport": pm4pydistr.configuration.MASTER_PORT,
                                               "conf": "slave" + str(j)})

    # Assign event logs to slaves
    requests.get(
        "http://" + pm4pydistr.configuration.MASTER_HOST + ":" + MasterVariableContainer.port + "/doLogAssignment" +
        "?keyphrase=" + pm4pydistr.configuration.KEYPHRASE)

    # Wait for files to be assigned
    time.sleep(1)

    if args.func == "train":
        q = requests.get(
            "http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(pm4pydistr.configuration.MASTER_PORT) + "/doTraining?keyphrase=" +
            pm4pydistr.configuration.KEYPHRASE + "&process=" + args.evtlog)
    elif args.func == "predict":
        r = requests.post(
            "http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(pm4pydistr.configuration.MASTER_PORT) + "/doPrediction?keyphrase=" +
            pm4pydistr.configuration.KEYPHRASE + "&process=" + args.evtlog, data=json.dumps(test_events[args.evtlog]))
        print(r.text)
    else:
        print("Invalid command line arguments")






