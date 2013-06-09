from org.muscat.staldates.aldatesx.Sequencer import Sequencer, Event
import logging
from logging import Handler
import Pyro4


class Controller(object):
    '''
    A Controller is essentially a bucket of devices, each identified with a string deviceID.
    '''
    pyroName = "aldates.alix.controller"

    def __init__(self):
        self.devices = {}
        self.sequencer = Sequencer()
        self.sequencer.start()
        self.logHandler = ControllerLogHandler()
        logging.getLogger().addHandler(self.logHandler)
        self.clients = {}

    def registerClient(self, clientURI):
        client = Pyro4.Proxy(clientURI)
        self.clients[clientURI] = client
        logging.info("Registered client at " + client.getHostIP())
        logging.info(str(len(self.clients)) + " client(s) now connected")

    def unregisterClient(self, clientURI):
        client = self.clients.pop(clientURI)
        logging.info("Unregistered client at " + client.getHostIP())
        logging.info(str(len(self.clients)) + " client(s) still connected")

    def callAllClients(self, function):
        ''' function should take a client and do things to it'''
        for uri, client in self.clients.iteritems():
            try:
                logging.debug("Calling function " + function.__name__ + " with client at " + str(uri))
                function(client)
            except:
                logging.exception("Failed to call function on registered client " + str(uri))

    def addDevice(self, device):
        self.devices[device.deviceID] = device

    def hasDevice(self, deviceID):
        return deviceID in self.devices

    def initialise(self):
        for device in self.devices.itervalues():
            device.initialise()

    def switch(self, deviceID, inChannel, outChannel):
        '''If a device with the given ID exists, perform a video switch. If not then return -1.'''
        if self.hasDevice(deviceID):
            logging.debug("Switching device " + deviceID + ": " + str(inChannel) + "=>" + str(outChannel))
            return self.devices[deviceID].sendInputToOutput(inChannel, outChannel)
        else:
            logging.warn("No device with ID " + deviceID)
            return -1

    def move(self, camDeviceID, direction):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if direction == CameraMove.Left:
                return camera.moveLeft()
            elif direction == CameraMove.Right:
                return camera.moveRight()
            elif direction == CameraMove.Up:
                return camera.moveUp()
            elif direction == CameraMove.Down:
                return camera.moveDown()
            elif direction == CameraMove.Stop:
                return camera.stop()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def zoom(self, camDeviceID, zoomType):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if zoomType == CameraZoom.Tele:
                return camera.zoomIn()
            elif zoomType == CameraZoom.Wide:
                return camera.zoomOut()
            elif zoomType == CameraZoom.Stop:
                return camera.zoomStop()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def focus(self, camDeviceID, focusType):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if focusType == CameraFocus.Auto:
                return camera.focusAuto()
            elif focusType == CameraFocus.Near:
                return camera.focusNear()
            elif focusType == CameraFocus.Far:
                return camera.focusFar()
            elif focusType == CameraFocus.Stop:
                return camera.focusStop()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def exposure(self, camDeviceID, exposureType):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if exposureType == CameraExposure.Brighter:
                return camera.brighter()
            elif exposureType == CameraExposure.Darker:
                return camera.darker()
            elif exposureType == CameraExposure.Auto:
                return camera.autoExposure()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def backlightComp(self, camDeviceID, compensation):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if compensation:
                return camera.backlightCompOn()
            else:
                return camera.backlightCompOff()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def savePreset(self, camDeviceID, preset):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Saving preset " + str(preset) + " on device " + camDeviceID)
            camera.storePreset(preset)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def recallPreset(self, camDeviceID, preset):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Recalling preset " + str(preset) + " on device " + camDeviceID)
            camera.recallPreset(preset)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def whiteBalance(self, camDeviceID, wbSetting):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if wbSetting == CameraWhiteBalance.Auto:
                return camera.whiteBalanceAuto()
            elif wbSetting == CameraWhiteBalance.Indoor:
                return camera.whiteBalanceIndoor()
            elif wbSetting == CameraWhiteBalance.Outdoor:
                return camera.whiteBalanceOutdoor()
            elif wbSetting == CameraWhiteBalance.OnePush:
                return camera.whiteBalanceOnePush()
            elif wbSetting == CameraWhiteBalance.Trigger:
                return camera.whiteBalanceOnePushTrigger()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def getPosition(self, camDeviceID):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Querying position of device " + camDeviceID)
            return camera.getPosition()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return None

    def goto(self, camDeviceID, pos, panSpeed, tiltSpeed):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Setting position of device " + camDeviceID)
            return camera.goto(pos, panSpeed, tiltSpeed)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return None

    def cameraCommand(self, camDeviceID, command):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            return camera.execute(command)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def toggleOverscan(self, scDevice, overscan):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if overscan:
                sc.overscanOn()
            else:
                sc.overscanOff()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleFreeze(self, scDevice, freeze):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if freeze:
                sc.freeze()
            else:
                sc.unfreeze()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleOverlay(self, scDevice, overlay):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if overlay:
                sc.overlayOn()
            else:
                sc.overlayOff()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleFade(self, scDevice, fade):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if fade:
                sc.fadeOut()
            else:
                sc.fadeIn()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def recalibrate(self, scDevice):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            sc.recalibrate()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def raiseUp(self, device, number):
        if self.hasDevice(device):
            logging.debug("Raising " + device + ":" + str(number))
            d = self.devices[device]
            d.raiseUp(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def lower(self, device, number):
        if self.hasDevice(device):
            logging.debug("Lowering " + device + ":" + str(number))
            d = self.devices[device]
            d.lower(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def stop(self, device, number):
        if self.hasDevice(device):
            logging.debug("Stopping " + device + ":" + str(number))
            d = self.devices[device]
            d.stop(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def systemPowerOn(self):
        if self.hasDevice("Power"):
            power = self.devices["Power"]
            logging.info("Turning ON system power")
            self.sequencer.sequence(
                Event(lambda: self.callAllClients(lambda c: c.showPowerOnDialog())),
                Event(power.on, 1),
                self.sequencer.wait(3),
                Event(power.on, 2),
                self.sequencer.wait(3),
                Event(power.on, 5),
                Event(power.on, 3),
                self.sequencer.wait(3),
                Event(power.on, 6),
                Event(self.initialise),  # By this time all things we care about to initialise will have been switched on
                Event(lambda: self.callAllClients(lambda c: c.hidePowerDialog())),
            )

    def systemPowerOff(self):
        if self.hasDevice("Power"):
            power = self.devices["Power"]
            logging.info("Turning OFF system power")
            self.sequencer.sequence(
                Event(lambda: self.callAllClients(lambda c: c.showPowerOffDialog())),
                Event(power.off, 6),
                self.sequencer.wait(3),
                Event(power.off, 5),
                Event(power.off, 3),
                self.sequencer.wait(3),
                Event(power.off, 2),
                self.sequencer.wait(3),
                Event(power.off, 1),
                Event(lambda: self.callAllClients(lambda c: c.hidePowerDialog())),
            )

    def getLog(self):
        return self.logHandler.entries

    def updateOutputMappings(self, mapping):
        self.callAllClients(lambda c: c.updateOutputMappings(mapping))


class CameraMove():
    Left, Right, Up, Down, Stop = range(5)


class CameraZoom():
    Tele, Wide, Stop = range(3)


class CameraFocus():
    Near, Far, Auto, Stop = range(4)


class CameraExposure():
    Brighter, Darker, Auto = range(3)


class CameraWhiteBalance():
    Auto, Indoor, Outdoor, OnePush, Trigger = range(5)


class ControllerLogHandler(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.entries = []

    def emit(self, record):
        self.entries.append(record)
        if len(self.entries) > 100:
            self.entries.pop(0)
