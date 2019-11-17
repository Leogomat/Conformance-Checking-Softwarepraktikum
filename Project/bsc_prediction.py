from pm4py.objects.log.importer.xes import factory as xes_importer
import os
from sklearn.linear_model import ElasticNet
from pm4py.objects.log.log import EventLog, Trace

from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util import get_log_representation
from pm4py.objects.log.util import sorting
from pm4py.objects.log.util import xes
from pm4py.objects.log.util.get_prefixes import get_log_with_log_prefixes
from pm4py.util import constants
from pm4py.util.business_hours import BusinessHours


def train(log, parameters=None):
    """
    Train the prediction model
    Parameters
    -----------
    log
        Event log
    parameters
        Possible parameters of the algorithm
    Returns
    ------------
    model
        Trained model
    """
    if parameters is None:
        parameters = {}

    parameters["enable_sort"] = False
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    business_hours = parameters["business_hours"] if "business_hours" in parameters else False
    worktiming = parameters["worktiming"] if "worktiming" in parameters else [7, 17]
    weekends = parameters["weekends"] if "weekends" in parameters else [6, 7]

    y_orig = parameters["y_orig"] if "y_orig" in parameters else None

    log = sorting.sort_timestamp(log, timestamp_key)

    str_evsucc_attr = [activity_key]
    if "str_ev_attr" in parameters:
        str_tr_attr = parameters["str_tr_attr"] if "str_tr_attr" in parameters else []
        str_ev_attr = parameters["str_ev_attr"] if "str_ev_attr" in parameters else []
        num_tr_attr = parameters["num_tr_attr"] if "num_tr_attr" in parameters else []
        num_ev_attr = parameters["num_ev_attr"] if "num_ev_attr" in parameters else []
    else:
        str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr = attributes_filter.select_attributes_from_log_for_tree(log)
        if activity_key not in str_ev_attr:
            str_ev_attr.append(activity_key)

    ext_log, change_indexes = get_log_with_log_prefixes(log)
    data, feature_names = get_log_representation.get_representation(ext_log, str_tr_attr, str_ev_attr, num_tr_attr,
                                                                    num_ev_attr, str_evsucc_attr=str_evsucc_attr)

    if y_orig is not None:
        remaining_time = [y for x in y_orig for y in x]
    else:
        if business_hours:
            remaining_time = []
            for trace in ext_log:
                if trace:
                    timestamp_et = trace[-1][timestamp_key]
                    timestamp_st = trace[0][timestamp_key]

                    bh = BusinessHours(timestamp_st.replace(tzinfo=None), timestamp_et.replace(tzinfo=None),
                                       worktiming=worktiming, weekends=weekends)
                    remaining_time.append(bh.getseconds())
                else:
                    remaining_time.append(0)
        else:
            remaining_time = []
            for trace in ext_log:
                if trace:
                    remaining_time.append((trace[-1][timestamp_key] - trace[0][timestamp_key]).total_seconds())
                else:
                    remaining_time.append(0)
    regr = ElasticNet(max_iter=10000, l1_ratio=0.7)
    regr.fit(data, remaining_time)

    return {"str_tr_attr": str_tr_attr, "str_ev_attr": str_ev_attr, "num_tr_attr": num_tr_attr,
            "num_ev_attr": num_ev_attr, "str_evsucc_attr": str_evsucc_attr, "feature_names": feature_names,
            "remaining_time": remaining_time, "regr": regr, "variant": "elasticnet"}

def test(model, obj, parameters=None):
    """
    Test the prediction model
    Parameters
    ------------
    model
        Prediction model
    obj
        Object to predict (Trace / EventLog)
    parameters
        Possible parameters of the algorithm
    Returns
    ------------
    pred
        Result of the prediction (single value / list)
    """
    if parameters is None:
        parameters = {}

    str_tr_attr = model["str_tr_attr"]
    str_ev_attr = model["str_ev_attr"]
    num_tr_attr = model["num_tr_attr"]
    num_ev_attr = model["num_ev_attr"]
    str_evsucc_attr = model["str_evsucc_attr"]
    feature_names = model["feature_names"]
    regr = model["regr"]

    if type(obj) is EventLog:
        log = obj
    else:
        log = EventLog([obj])
    data, feature_names = get_log_representation.get_representation(log, str_tr_attr, str_ev_attr, num_tr_attr,
                                                                    num_ev_attr, str_evsucc_attr=str_evsucc_attr,
                                                                    feature_names=feature_names)

    pred = regr.predict(data)

    if len(pred) == 1:
        # prediction on a single case
        return pred[0]
    else:
        return pred


if __name__ == "__main__":
    log = xes_importer.apply("Event Logs/roadtraffic100traces.xes")

    test_log_size = int(len(log) * 0.34)
    training_log_complete = EventLog(log[test_log_size:len(log)])
    test_log_complete = EventLog(log[0:test_log_size])

    remaining_time_train = []
    training_log_only_first_event = EventLog()
    test_log_only_first_event = EventLog()

    for trace in training_log_complete:
        new_trace = Trace()

        new_trace.append(trace[0])

        remaining_time_train.append((trace[-1]["time:timestamp"] - trace[0]["time:timestamp"]).total_seconds())

        training_log_only_first_event.append(new_trace)

    remaining_time_test = []

    for trace in test_log_complete:
        new_trace = Trace()

        new_trace.append(trace[0])

        remaining_time_test.append((trace[-1]["time:timestamp"] - trace[0]["time:timestamp"]).total_seconds())

        test_log_only_first_event.append(new_trace)

    print(remaining_time_train)

    model = train(log, parameters={"y_origin": remaining_time_train})

    print(model)

    for i in range(len(test_log_only_first_event)):
        case_to_predict = test_log_only_first_event[i]

        correct_value = remaining_time_test[i]

        predicted_value = test(model, case_to_predict)

        print(correct_value, predicted_value)
