from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.log import Trace
from pm4pypred.algo.prediction import factory as pred_factory
import os

if __name__ == "__main__":
    # Import the roadtraffic log
    log = xes_importer.apply(os.path.join("Event Logs", "running-example.xes"))

    # Define the amount of the event log that will be used for training the ensemble
    training_size = int(len(log) * 0.8)

    # Instantiate both training and testing logs
    training_log = EventLog(log[0:training_size])
    test_log = EventLog(log[training_size:len(log)])

    # Declare lists that store the total time of each case in the training and test logs
    training_time_vector = []
    test_time_vector = []

    # Create an event log with only the first event of each case of the training log
    training_first_event = EventLog()
    for case in training_log:
        new_case = Trace()

        new_case.append(case[0])

        training_first_event.append(new_case)

        # Store total time of case
        training_time_vector.append((case[-1]["time:timestamp"] - case[0]["time:timestamp"]).total_seconds())

    # Do the same for the test log
    test_first_event = EventLog()
    for case in test_log:
        new_case = Trace()

        new_case.append(case[0])

        test_first_event.append(new_case)

        test_time_vector.append((case[-1]["time:timestamp"] - case[0]["time:timestamp"]).total_seconds())

    print(training_time_vector)
    print(log[0][1]["Costs"])
    #model = pred_factory.train(log, variant="elasticnet", parameters={"y_origin": training_time_vector})

    #print(model)