from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.log import Trace
from pm4pypred.algo.prediction import factory as pred_factory
import argparse
import os
import pickle


# Global variables
training_part = 0.8


# Store a trained model
def persist_model(model, event_log):
    with open(os.path.join("Ensembles", event_log + ".pkl"), "wb") as output:
        pickle.dump(model, output, pickle.HIGHEST_PROTOCOL)


# Load a model from memory
def load_model(event_log):
    with open(os.path.join("Ensembles", event_log + ".pkl"), "rb") as input:
        return pickle.load(input)


# Training functionality
def training_func(complete_log, log_size, event_log):
    # Instantiate training log
    training_log = EventLog(complete_log[0:log_size])

    # Declare list that stores the total time of each case in the training log
    training_time_vector = []

    # Create an event log with only the first event of each case of the training log
    training_first_event = EventLog()
    for case in training_log:
        new_case = Trace()

        new_case.append(case[0])

        training_first_event.append(new_case)

        # Store total time of case
        training_time_vector.append((case[-1]["time:timestamp"] - case[0]["time:timestamp"]).total_seconds())

    # Train and persist the ensemble
    model = pred_factory.train(log, variant="elasticnet", parameters={"y_origin": training_time_vector})
    persist_model(model, event_log)

    print("Training on " + args.evtlog + " done.")


# Testing functionality
def test_func(complete_log, log_size, event_log):
    # Instantiate test log
    test_log = EventLog(complete_log[log_size:len(log)])

    # Declare list that stores the total time of each case in the test log
    test_time_vector = []

    # Create an event log with only the first event of each case of the test log
    test_first_event = EventLog()
    for case in test_log:
        new_case = Trace()

        new_case.append(case[0])

        test_first_event.append(new_case)

        test_time_vector.append((case[-1]["time:timestamp"] - case[0]["time:timestamp"]).total_seconds())

    # Load the persisted ensemble and predict completion time for each case
    model = load_model(event_log)
    average = 0
    for i in range(len(test_first_event)):
        prediction = pred_factory.test(model, test_first_event[i])
        real_value = test_time_vector[i]
        error = int(prediction - real_value)
        average = average + error
        print("Predicted time for case " + str(i) + ": " + str(prediction) + "; Real value: " + str(
            real_value) + "; Relative error: " + str(error))
    print("Average error: " + str(average / len(test_first_event)))


if __name__ == "__main__":
    # Declare parser for taking command line arguments
    parser = argparse.ArgumentParser(description="Choose functionality")
    parser.add_argument(dest="func", type=str)
    parser.add_argument(dest="evtlog", type=str)
    args = parser.parse_args()

    # Import the log given in the arguments
    log = xes_importer.apply(os.path.join("Event Logs", args.evtlog + ".xes"))

    # Define the amount of the event log that will be used for training the ensemble
    training_size = int(len(log) * training_part)

    # Execute functionality depending on given argument
    if args.func == "train":
        training_func(log, training_size, args.evtlog)
    elif args.func == "test":
        try:
            test_func(log, training_size, args.evtlog)
        except EOFError:
            print("Error: No ensemble for the given event log is stored.")
    else:
        print("Error: Invalid command line argument")