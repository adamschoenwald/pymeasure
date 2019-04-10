#
# InstruTech Hot Cathode Ionization Vacuum Gauge IGM401 Module
# Modified danfysik8500.py the PyMeasure package.
# Adam Schoenwald
#

from pymeasure.instruments import Instrument, RangeException
from pymeasure.adapters import SerialAdapter

from time import sleep
import numpy as np
import re


class IGM401(Instrument):
    """ InstruTech Hot Cathode Ionization Vacuum Gauge IGM401 Module
    and provides a high-level interface for interacting with the
    instrument

    The user should verify DIGI/RS485 is selected in the IG CNTL submenu of the SETUP UNIT menu.

    To switch IGM401 to RS485 mode, send IG off (or on) and on receipt of command it should switch.

    If the IGM401 is already on and we want to stay on, send on command to switch from DIGI to RS485.

    Trying to send READ commands while in DIGI mode will not work until we switch to RS485 mode.

    To leave RS485, either send reset command or power cycle .


    All commands sent to the module start with a ‘#’ character.
    All normal responses from the module start with a ‘*’ character.
    Error responses start with a “?”.
    All responses are 13 charachters long.
    """
    xx_address = '01'

    def __init__(self,  port):
        super(IGM401, self).__init__(
            SerialAdapter(port, 19200, timeout=0.5),
            "InstruTech IGM401 Ionization Vacuum Gauge",
            includeSCPI=False,
        )
        hw, sw = self.module_version()
        self.hardware_ver = hw
        self.software_ver = sw

    def write(self, command):
        """ Overwrites the Insturment.write command to provide the correct
        line break syntax
        """
        self.connection.write('#' + self.xx_address + command + "\r")

    def verify_succesfull(self, response):
        """ Verify that response contains the [*xx_PROGM_OK<CR>] string"""
        regex_pattern = '(?P < response_char > \ * {1})(?P < address >\d{2})\s[P][R][O][G][M]\s[O][K][\\][r]'
        match = re.search(regex_pattern , response)
        if match is None:
            return False
        else:
            return True

    def module_status(self):
        """Finds out the cause of the controller shutdown"""
        response = self.ask('RS')
        regex_pattern = '(?P<response_char>\*{1})(?P<address>\d{2})\s(?P<status>(ST\sOK|OVPRS|EMISS|POWER|ION\sC))'
        match = re.search(regex_pattern, response)
        if match is None:
            raise Exception("Unexpected response value = <" + str(response) + ">")
        else:
            return int(match.group('status'))

    def module_version(self):
        """Read the part number and revision number (version) of the firmware."""
        response = self.ask('RS')
        regex_pattern = '(?P<response_char>\*{1})(?P<address>\d{2})\s(?P<part_number>\d+)\-{1}(?P<version_number>\d+)'
        match = re.search(regex_pattern, response)
        if match is None:
            raise Exception("Unexpected response value = <" + str(response) + ">")
        else:
            return match.group('part_number'), match.group('version_number')

    def reset(self):
        """ Reset the device as if power was cycled (Required to complete some of the commands). No response is given."""
        self.write('RST')

    def defaults(self):
        """Force unit to return ALL settings back to the way the factory programmed them before shipment"""
        response = self.ask('FAC')
        if self.verify_succesfull(response):
            pass
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def iog_gauge_status(self):
        """ Find out if filament is powered up and gauge is reading.
        0 = OFF
        1 = ON"""
        response = self.ask('IGS')
        regex_pattern = '(?P<response_char>\*{1})(?P<address>\d{2})\s(?P<status_int>(1|0))\s[I][G]\s(?P<status_string>(ON|OFF))'
        match = re.search(regex_pattern,response)
        if match is None:
            raise Exception("Unexpected response value = <" + str(response) + ">")
        else:
            return int(match.group('status'))

    def ion_gauge_on(self):
        response = self.ask('IG1')
        if self.verify_succesfull(response):
            pass
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def ion_gauge_off(self):
        response = self.ask('IG0')
        if self.verify_succesfull(response):
            pass
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def emission_current_status(self):
        """ Find out emission current level.
        Return emission current setting in ma, either 0.1 or 4.0"""
        response = self.ask('SES')
        regex_pattern = '(?P<response_char>\*{1})(?P<address>\d{2})\s(?P<emission_current>(0.1|4.0))[M][A]\s[E][M]'
        match = re.search(regex_pattern, response)
        if match is None:
            raise Exception("Unexpected response value = <" + str(response) + ">")
        else:
            return int(match.group('emission_current'))

    def emission_current_4ma(self):
        response = self.ask('SE1')
        if self.verify_succesfull(response):
            pass
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def emission_current_100ua(self):
        response = self.ask('SE0')
        if self.verify_succesfull(response):
            pass
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def degas_status(self):
        """ Find out if the module is currently degassing.
        0 = OFF
        1 = ON"""
        response = self.ask('DGS')
        regex_pattern = '(?P<response_char>\*{1})(?P<address>\d{2})\s(?P<status_int>(1|0))\s[D][G]\s(?P<status_string>(ON|OFF))'
        match = re.search(regex_pattern, response)
        if match is None:
            raise Exception("Unexpected response value = <" + str(response) + ">")
        else:
            return int(match.group('status'))

    def degas_start(self):
        response = self.ask('DG1')
        if self.verify_succesfull(response):
            pass
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def degas_off(self):
        response = self.ask('DG0')
        if self.verify_succesfull(response):
            pass
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def filament_one(self):
        """ Choose Filament 1 """
        response = self.ask('SF1')
        if self.verify_succesfull(response):
            pass
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def filament_two(self):
        """ Choose Filament 2 """
        response = self.ask('SF2')
        if self.verify_succesfull(response):
            return 0
        else:
            raise Exception("Unexpected response value = <" + str(response) + ">")

    def read_pressure(self):
        response = self.ask('RD')
        regex_pattern = '(?P<response_char>\*{1})(?P<address>\d{2})\s(?P<mantissa>\d\.\d\d)[E](?P<exponent>[+|-]\d\d)'
        match = re.search(regex_pattern, response)
        if match is None:
            raise Exception("Unexpected response value = <" + str(response) + ">")
        else:
            pressure = float(m.group('mantissa')) * 10 ** (float(m.group('exponent')))
            return pressure


    # @property
    # def polarity(self):
    #     """ The polarity of the current supply, being either
    #     -1 or 1. This property can be set by suppling one of
    #     these values.
    #     """
    #     return 1 if self.ask("PO").strip() == '+' else -1
    #
    # @polarity.setter
    # def polarity(self, value):
    #     polarity = "+" if value > 0 else "-"
    #     self.write("PO %s" % polarity)
    #
