from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4pydistr.configuration import PYTHON_PATH
import pm4pydistr
import requests
from threading import Thread
import json
import time
import shutil
import os

test_events = {
    "receipt": {'org:group': 'EMPTY',
                'concept:instance': 'task-20635',
                'org:resource': 'Resource17',
                'concept:name': 'Confirmation of receipt',
                'time:timestamp': '2011-04-21 15:55:07.600000',
                'lifecycle:transition': 'complete'},

    "receipt_wrong": {'org:grou': 'EMPTY',
                      'concept:instance': 'task-20635',
                      'org:resource': 'Resource17',
                      'concept:name': 'Confirmation of receipt',
                      'time:timestamp': '2011-04-21 15:55:07.600000',
                      'lifecycle:transition': 'complete'},

    "receipt_empty": {}
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
    refresh_directory("Data/Ensembles")

    # Import event log and partition it
    log = xes_importer.apply("Data/Event Logs/receipt.xes")
    parquet_exporter.apply(log, "master",
                           parameters={"auto_partitioning": True,
                                       "num_partitions": pm4pydistr.configuration.NUMBER_OF_PARTITIONS})

    # Move the training log to the training folder
    for i in range(int(pm4pydistr.configuration.NUMBER_OF_PARTITIONS * pm4pydistr.configuration.TRAINING_PART),
                   pm4pydistr.configuration.NUMBER_OF_PARTITIONS):
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
    print("Log assignment done\n")
    print("Performing tests with 2 slaves:\n")

    # Wait for files to be assigned
    time.sleep(1)

    # Here we test the service functionalities.

    """Here we test if the service is able to perform a prediction when there is no ensemble available. This shouldn't
    be possible, so the test is passed if the status code of the request indicates failure (405)"""
    try:
        print("Test 1: Perform prediction using nonexistent ensemble")
        request = requests.get("http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(
                          pm4pydistr.configuration.MASTER_PORT) + "/doPrediction?keyphrase=" +
                          pm4pydistr.configuration.KEYPHRASE + "&process=receipts",
                          data=json.dumps(test_events["receipt"]))

        print("Status code: " + str(request.status_code))
        print("Request text: " + request.text)
        request.raise_for_status()
        print("Test 1: Failed\n")
    except:
        print("Test 1: Passed\n")

    """Here we test if the service is able to train an ensemble on the event log. The test is passed if the status code
    of the request indicates success (200)"""
    try:
        print("Test 2: Training ensemble on event log")
        request = requests.get("http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(
                          pm4pydistr.configuration.MASTER_PORT) + "/doTraining?keyphrase=" +
                          pm4pydistr.configuration.KEYPHRASE + "&process=receipt")

        print("Status code: " + str(request.status_code))
        print("Request text: " + request.text)
        request.raise_for_status()
        print("Test 2: Passed\n")
    except:
        print("Test 2: Failed\n")

    """Here we test if the service is able to replace an old ensemble trained on the the event log. The test is passed
    if the status code of the request indicates success (200)"""
    try:
        print("Test 3: Training ensemble on event log again (replace old ensemble)")
        request = requests.get("http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(
                          pm4pydistr.configuration.MASTER_PORT) + "/doTraining?keyphrase=" +
                          pm4pydistr.configuration.KEYPHRASE + "&process=receipt")

        print("Status code: " + str(request.status_code))
        print("Request text: " + request.text)
        request.raise_for_status()
        print("Test 3: Passed\n")
    except:
        print("Test 3: Failed\n")

    """Here we test if the service is able to perform a prediction using the trained ensemble. The test is passed if the
    status code of the request indicates success (200)"""
    try:
        print("Test 4: Performing prediction using existing ensemble")
        request = requests.post("http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(
                          pm4pydistr.configuration.MASTER_PORT) + "/doPrediction?keyphrase=" +
                          pm4pydistr.configuration.KEYPHRASE + "&process=receipt",
                          data=json.dumps(test_events["receipt"]))

        print("Status code: " + str(request.status_code))
        print("Request text: " + request.text)
        request.raise_for_status()
        print("Test 4: Passed\n")
    except:
        print("Test 4: Failed\n")

    """Here we test if the service is able to perform a prediction using the trained ensemble when a first event with a
    wrong attribute name is provided. This should be possible, because the prediction algorithm only uses the desired
     attributes if they are available. The test is passed if the status code of the request indicates success (200)"""
    try:
        print("Test 5: Providing wrong event attribute name for prediction")
        request = requests.post("http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(
                          pm4pydistr.configuration.MASTER_PORT) + "/doPrediction?keyphrase=" +
                          pm4pydistr.configuration.KEYPHRASE + "&process=receipt",
                          data=json.dumps(test_events["receipt_wrong"]))

        print("Status code: " + str(request.status_code))
        print("Request text: " + request.text)
        request.raise_for_status()
        print("Test 5: Passed\n")
    except:
        print("Test 5: Failed\n")

    """Here we test if the service is able to perform a prediction using the trained ensemble when an empty first event
    is provided. This should be possible, because the prediction algorithm does not need any of the desired attributes
    to perform a prediction. The test is passed if the status code of the request indicates success (200)"""
    try:
        print("Test 6: Providing empty event for prediction")
        request = requests.post("http://" + pm4pydistr.configuration.MASTER_HOST + ":" + str(
            pm4pydistr.configuration.MASTER_PORT) + "/doPrediction?keyphrase=" +
                                pm4pydistr.configuration.KEYPHRASE + "&process=receipt",
                                data=json.dumps(test_events["receipt_empty"]))

        print("Status code: " + str(request.status_code))
        print("Request text: " + request.text)
        request.raise_for_status()
        print("Test 6: Passed\n")
    except:
        print("Test 6: Failed\n")







