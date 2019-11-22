from pm4py.objects.log.importer.xes import factory as xes_importer
from Modules import func
from Modules import constants
from pm4py.objects.log.log import EventLog
import argparse
import os

# Event log considered
event_log = "roadtraffic100traces"

if __name__ == "__main__":
    # Declare parser for taking command line arguments
    parser = argparse.ArgumentParser(description="Choose functionality")
    parser.add_argument(dest="func", type=str)
    args = parser.parse_args()

    # Import the log
    log = xes_importer.apply(os.path.join("Event Logs", event_log + ".xes"))

    # Define the amount of the event log that will be used for training the ensemble
    training_size = int(len(log) * constants.TRAINING_PART)

    # Define the training and test logs
    training_log = EventLog(log[0:training_size])
    test_log = EventLog(log[training_size:len(log)])

    # Execute functionality depending on given argument
    if args.func == "train":
        model = func.training_func(log, constants.MODEL_PATH + "/" + event_log + ".pkl")
    elif args.func == "test":
        func.test_func(log, constants.MODEL_PATH + "/" + event_log + ".pkl")
    else:
        print("Error: Invalid command line argument, please read the \"script_README.txt\" file")