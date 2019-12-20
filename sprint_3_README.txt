In this sprint we fixed the bug that caused the event logs not to be assigned to the slave nodes. The problem came from
the fact that we hadn't initialized each node in their own threads, therefore causing all logs to be assigned to the
first slave.

The test script is found in "Project/test.py". As the only argument one should give the name of the event log on which
the services will be applied (for example: python test.py receipt). The supported event logs are "receipt" and
"roadtraffic100traces". The nodes take around 20 seconds to be initialized,
and the user will be notified that the log assignment to the slaves is done. The user will then be prompted to choose a
functionality (train or predict), and the service will be executed.