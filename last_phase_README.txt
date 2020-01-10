The following tests are performed in the file "Project/test.py"

Test 1: Here we test if the service is able to perform a prediction when there is no ensemble available. This shouldn't
be possible, so the test is passed if the status code of the request indicates failure (405)"""


Test 2: Here we test if the service is able to train an ensemble on the event log. The test is passed if the status code
of the request indicates success (200)"""


Test 3: Here we test if the service is able to replace an old ensemble trained on the the event log. The test is passed
if the status code of the request indicates success (200)"""

Test 4: Here we test if the service is able to perform a prediction using the trained ensemble. The test is passed if the
status code of the request indicates success (200)"""


Test 5: Here we test if the service is able to perform a prediction using the trained ensemble when a first event with a
wrong attribute name is provided. This should be possible, because the prediction algorithm only uses the desired
attributes if they are available. The test is passed if the status code of the request indicates success (200)"""

Test 6: Here we test if the service is able to perform a prediction using the trained ensemble when an empty first event
is provided. This should be possible, because the prediction algorithm does not need any of the desired attributes
to perform a prediction. The test is passed if the status code of the request indicates success (200)"""
