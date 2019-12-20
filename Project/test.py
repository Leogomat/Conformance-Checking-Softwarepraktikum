from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4pydistr.configuration import PYTHON_PATH
import pm4pydistr
import requests
from threading import Thread
import json
import time
import shutil
import argparse
import os

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


class ExecutionThread(Thread):
    def __init__(self, command):
        self.command = command
        Thread.__init__(self)

    def run(self):
        os.system(self.command)


# Clean a folder of its files
def refresh_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)


if __name__ == "__main__":
    # Refresh the master, training, and slave folders
    refresh_directory("master")
    refresh_directory("testing")
    refresh_directory("slave1")
    refresh_directory("slave2")

    # Declare parser for taking command line arguments
    parser = argparse.ArgumentParser(description="Choose event log")
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
    t1 = ExecutionThread(PYTHON_PATH + " launch.py type master conf master port 5001")
    t1.start()
    t2 = ExecutionThread(
        PYTHON_PATH + " launch.py type slave conf slave1 autoport 1 masterhost 127.0.0.1 masterport 5001")
    t2.start()
    t3 = ExecutionThread(
        PYTHON_PATH + " launch.py type slave conf slave2 autoport 1 masterhost 127.0.0.1 masterport 5001")
    t3.start()

    # Wait for nodes to be initialized
    time.sleep(20)

    # Assign event logs to slaves
    r = requests.get(
        "http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(5001) + "/doLogAssignment" +
        "?keyphrase=" + pm4pydistr.configuration.KEYPHRASE)
    print("Log assignment done")

    # Wait for files to be assigned
    time.sleep(1)

    while (1):

        # Ask user to input desired functionality
        i = input("\n Input functionality (train/predict): ")

        if i == "train":
            q = requests.get(
                "http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(
                    pm4pydistr.configuration.MASTER_PORT) + "/doTraining?keyphrase=" +
                pm4pydistr.configuration.KEYPHRASE + "&process=" + args.evtlog)
        elif i == "predict":
            r = requests.post(
                "http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(
                    pm4pydistr.configuration.MASTER_PORT) + "/doPrediction?keyphrase=" +
                pm4pydistr.configuration.KEYPHRASE + "&process=" + args.evtlog,
                data=json.dumps(test_events[args.evtlog]))
            print(r.text)
        else:
            print("Invalid command line arguments")








