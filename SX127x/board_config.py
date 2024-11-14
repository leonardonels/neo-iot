""" Defines the BOARD class that contains the board pin mappings. """

# Copyright 2015 Mayer Analytics Ltd.
#
# This file is part of pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.


import spidev
from gpiozero import InputDevice


class BOARD:
    """ Board initialisation/teardown and pin configuration is kept here.
        This is the Raspberry Pi board with one LED and a modtronix inAir9B
    """
    # Define GPIO pins
    cs_pin_number = 25
    rst_pin_number = 22
    dio0_pin_number = 27
    dio1_pin_number = 23
    dio2_pin_number = 24
    dio3_pin_number = 18

    spi = None
    dio0 = None
    dio1 = None
    dio2 = None
    dio3 = None

    @staticmethod
    def setup():
        """ Configure the Raspberry GPIOs
        :rtype : None
        """
        # DIOx
        BOARD.dio0=InputDevice(BOARD.dio0_pin_number)
        BOARD.dio1=InputDevice(BOARD.dio1_pin_number)
        BOARD.dio2=InputDevice(BOARD.dio2_pin_number)
        BOARD.dio3=InputDevice(BOARD.dio3_pin_number)

    @staticmethod
    def teardown():
        """ Cleanup GPIO and SpiDev """
        BOARD.spi.close()

    @staticmethod
    def SpiDev(spi_bus=0, spi_cs=0):
        """ Init and return the SpiDev object
        :return: SpiDev object
        :param spi_bus: The RPi SPI bus to use: 0 or 1
        :param spi_cs: The RPi SPI chip select to use: 0 or 1
        :rtype: SpiDev
        """
        BOARD.spi = spidev.SpiDev()
        BOARD.spi.open(spi_bus, spi_cs)
        return BOARD.spi
    

    @staticmethod
    def add_event_detect(dio_number, callback):
        """ Wraps around the gpiozero.add_event_detect function
        :param dio_number: DIO pin 0...5
        :param callback: The function to call when the DIO triggers an IRQ.
        :return: None
        """
        if dio_number == BOARD.dio0:
            BOARD.dio0.is_active = callback

    @staticmethod
    def add_events(cb_dio0, cb_dio1, cb_dio2, cb_dio3, cb_dio4, cb_dio5, switch_cb=None):
        BOARD.add_event_detect(BOARD.dio0, callback=cb_dio0)
        BOARD.add_event_detect(BOARD.dio1, callback=cb_dio1)
        BOARD.add_event_detect(BOARD.dio2, callback=cb_dio2)
        BOARD.add_event_detect(BOARD.dio3, callback=cb_dio3)