import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

logging.basicConfig(filename='example.log',level=logging.DEBUG)
import datetime
from time import sleep
from pymeasure.log import console_log, file_log

from pymeasure.experiment import Procedure, Results, Worker
from pymeasure.experiment import IntegerParameter
import serial.tools.list_ports

class SimpleProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations')


    DATA_COLUMNS = ['Iteration','Time']

    def startup(self):
        my_startup_info = 'Start up info A'
        startup_info = {'StartStringA':my_startup_info }
        #self.emit('results', startup_info)
        log.info("Connecting and configuring the instrument")


    def execute(self):
        log.info("Starting the loop of %d iterations" % self.iterations)
        for i in range(self.iterations):
            this_time = datetime.datetime.now()

            data = {'Iteration': i, 'Time': this_time}
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            sleep(.01)
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break

    def shutdown(self):
        log.info("Finished measuring")


if __name__ == "__main__":
    console_log(log,level=logging.DEBUG)
    file_log(log, "example_extended.log",level=logging.INFO)
    log.info("Constructing a SimpleProcedure")
    procedure = SimpleProcedure()
    procedure.iterations = 100

    data_filename = 'example_extended.csv'
    log.info("Constructing the Results with a data file: %s" % data_filename)
    results = Results(procedure, data_filename)

    log.info("Constructing the Worker")
    worker = Worker(results)
    worker.start()
    log.info("Started the Worker")

    log.info("Joining with the worker in at most 1 hr")
    worker.join(timeout=3600) # wait at most 1 hr (3600 sec)
    log.info("Finished the measurement")