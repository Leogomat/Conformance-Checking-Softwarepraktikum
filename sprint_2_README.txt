In this sprint we have integrated the functionalities from sprint 1 into the pm4py distributed engine.

The test script is Project/test.py. The first argument of the script determines the desired functionality to be tested,
and it should be either "train" or "predict". The second argument should be the name of the event log that the test uses,
in this case either "receipt" or "roadtraffic100traces".

Examples:

python test.py train receipt
python test.py predict receipt
python test.py train roadtraffic100traces
python test.py predict roadtraffic100traces