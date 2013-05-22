'''
Created on 13 Nov 2012

@author: jrem
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice,\
    SerialListener
import logging


class Kramer602(SerialDevice):
    '''
    The Kramer 602 (preview) switcher. Reverse-engineered from the AMX code, this is apparently not Protocol 2000...
    '''

    def __init__(self, deviceID, serialDevice):
        super(Kramer602, self).__init__(deviceID, serialDevice, 1200)

    def sendInputToOutput(self, inChannel, outChannel):
        if outChannel > 2:
            logging.error("Output channel " + str(outChannel) + " does not exist on switcher " + self.deviceID)
        else:
            code = [0, 0x80 + (2 * inChannel) - (2 - outChannel)]
            self.sendCommand(SerialDevice.byteArrayToString(code))


class Kramer602Listener(SerialListener):
    ''' Class to listen to and interpret incoming messages from a VP88. '''

    dispatchers = []

    def __init__(self, port, machineNumber=1):
        ''' Initialise this Kramer602 listener. port should be the same Serial that's already been passed to a Kramer602. '''
        super(Kramer602Listener, self).__init__(port)
        self.machineNumber = machineNumber

    def process(self, message):
        if ((message[0] & 0x7) == (self.machineNumber - 1)):
            outp = (((message[1] & 0x1F) - 1) % 2) + 1
            inp = (((message[1] & 0x1F) - outp) / 2) + 1  # int(math.ceil((message[1] & 0x1F) + (2 / 2)) - 1)
            for d in self.dispatchers:
                d.updateOutputMappings({outp: inp})
