import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


import datetime
from time import sleep
from pymeasure.log import console_log, file_log
from pymeasure.instruments.instrutech.igm401 import IGM401
from pymeasure.experiment import Procedure, Results, Worker
from pymeasure.experiment import IntegerParameter
import serial.tools.list_ports

class SimpleProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations')

    DATA_COLUMNS = ['Iteration','Time']

    def startup(self):
        log.info("Searching for RS485 Adapter")
        ports = serial.tools.list_ports.comports()
        myport = None
        for port, desc, hwid in sorted(ports):
            log.debug("{}: {} [{}]".format(port, desc, hwid))
            if "PID=0403:6001" in hwid:
                myport = port
        if myport is None:
            log.error('No USB to RS485 Adapter found')
        else:
            log.info('Found RS485 Adapter on ' + str(myport))

        log.info("Connecting and configuring the instrument")
        self.sourcemeter = IGM401(myport)
        log.info('Hardware Version = ' + str(self.sourcemeter.hardware_ver))
        log.info('Software Version = ' + str(self.sourcemeter.software_ver))
        log.info('Last Shutdown Reason = ' + str(self.sourcemeter.module_status()))

        self.sourcemeter.ion_gauge_on()


    def execute(self):
        log.info("Starting the loop of %d iterations" % self.iterations)
        for i in range(self.iterations):
            this_time = datetime.datetime.now()

            pressure  = self.sourcemeter.read_pressure()
            emission_current_status = self.sourcemeter.emission_current_status()
            degas_status = self.sourcemeter.degas_status()

            data = {'Iteration': i, 'Time': this_time}
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            sleep(1)
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break

    def shutdown(self):
        self.sourcemeter.ion_gauge_off()
        log.info("Finished measuring")


if __name__ == "__main__":
    console_log(log)
    file_log(log, "igm401_no_degas.log",level=logging.DEBUG)
    log.info("Constructing a SimpleProcedure")
    procedure = SimpleProcedure()
    procedure.iterations = 3600

    data_filename = 'igm401_no_degas.csv'
    log.info("Constructing the Results with a data file: %s" % data_filename)
    results = Results(procedure, data_filename)

    log.info("Constructing the Worker")
    worker = Worker(results)
    worker.start()
    log.info("Started the Worker")

    log.info("Joining with the worker in at most 1 hr")
    worker.join(timeout=3600) # wait at most 1 hr (3600 sec)
    log.info("Finished the measurement")