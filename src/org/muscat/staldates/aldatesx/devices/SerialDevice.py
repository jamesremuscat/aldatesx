from org.muscat.staldates.aldatesx.devices.Device import Device
from serial import Serial

class SerialDevice(Device):
    '''
    A device we connect to over a serial port.
    '''

    def __init__(self, deviceID, serialDevice, baud=9600):
        super(SerialDevice, self).__init__(deviceID)
        if isinstance(serialDevice, str):
            self.port = Serial(serialDevice, baud)
        else:
            self.port = serialDevice
        
    def sendCommand(self, commandString):
        print "Sending " + commandString.encode('hex_codec') + " to " + self.port.portstr
        sentBytes = self.port.write(commandString)
        print str(sentBytes) + " bytes sent"
        return sentBytes
        
    @staticmethod
    def byteArrayToString(byteArray):
        return ''.join(chr(b) for b in byteArray)
        