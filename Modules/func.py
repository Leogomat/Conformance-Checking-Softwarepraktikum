from pm4pypred.algo.prediction import factory as pred_factory
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.log import Trace
import pickle
import os


# Training functionality
def training_func(log, path):
    # Declare list that stores the total time of each case in the training log
    training_time_vector = []

    # Create an event log with only the first event of each case of the training log
    log_first_event = EventLog()
    for case in log:
        new_case = Trace()

        new_case.append(case[0])

        log_first_event.append(new_case)

        # Store total time of case
        training_time_vector.append([(case[-1]["time:timestamp"] - case[0]["time:timestamp"]).total_seconds()])

    # Train and persist the ensemble
    model = pred_factory.train(log_first_event, variant="elasticnet", parameters={"y_orig": training_time_vector})

    persist_model(model, path)

    print("Training of ensemble complete.")

    return model


# Testing functionality
def test_func(log, path):
    # Declare list that stores the total time of each case in the test log
    test_time_vector = []

    # Create an event log with only the first event of each case of the test log
    log_first_event = EventLog()
    for case in log:
        new_case = Trace()

        new_case.append(case[0])

        log_first_event.append(new_case)

        test_time_vector.append((case[-1]["time:timestamp"] - case[0]["time:timestamp"]).total_seconds())

    # Load the persisted ensemble and predict completion time for each case
    model = load_model(path)
    average = 0
    for i in range(len(log_first_event)):
        prediction = pred_factory.test(model, log_first_event[i])
        real_value = test_time_vector[i]
        error = int(prediction - real_value)
        average = average + abs(error)
        print("Predicted time for case " + str(i) + ": " + str(prediction) + "; Real value: " + str(
            real_value) + "; Relative error: " + str(error))
    print("Average error: " + str(average / len(log_first_event)))


# Store a trained model
def persist_model(model, path):
    with open(path, "wb") as output:
        pickle.dump(model, output, pickle.HIGHEST_PROTOCOL)


# Load a model from memory
def load_model(path):
    with open(path, "rb") as input:
        return pickle.load(input)
