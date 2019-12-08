from pm4pydistr.master.master import Master
from pm4pydistr.slave.slave import Slave
from Modules import constants
import pm4pydistr
import shutil
import os


# Initialize the master and the slaves
def initialize_nodes():
    m = Master({"host": pm4pydistr.configuration.MASTER_HOST,
                                           "port": pm4pydistr.configuration.MASTER_PORT,
                                           "conf": "Data/master"})
    s = initialize_slaves()

    return m, s


# Initialize the slaves
def initialize_slaves():
    slaves_dict = {}

    for j in range(constants.NUMBER_OF_SLAVES):
        refresh_directory("Data/slave" + str(j))
        slaves_dict["slave" + str(j)] = Slave({"host": pm4pydistr.configuration.THIS_HOST,
                                          "port": pm4pydistr.configuration.PORT + j + 1,
                                          "masterhost": pm4pydistr.configuration.MASTER_HOST,
                                          "masterport": pm4pydistr.configuration.MASTER_PORT,
                                          "conf": "Data/slave" + str(j)})
    return slaves_dict


# Clean a folder of its files
def refresh_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
