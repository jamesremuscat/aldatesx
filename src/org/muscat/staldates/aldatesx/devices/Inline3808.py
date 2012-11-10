from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice

class Inline3808(SerialDevice):
    '''
    An Inline 3808 8x4 switcher.
    '''

    def __init__(self, deviceID, serialDevice):
        super(Inline3808, self).__init__(deviceID, serialDevice, 1200)
        self.sendCommand("[CNF290000]") # All boards to group 1. Copying what the AMX does currently though this should be the default.
        
    def sendInputToOutput(self, inChannel, outChannel):
        self.sendCommand("[PT1O0" + str(outChannel) + "I0" + str(inChannel) + "]")