from org.muscat.avx.controller.ControllerHelpers import deviceMethod


class ScanConverterController:

    @deviceMethod
    def toggleOverscan(self, scDevice, overscan):
        sc = self.devices[scDevice]
        if overscan:
            return sc.overscanOn()
        else:
            return sc.overscanOff()

    @deviceMethod
    def toggleFreeze(self, scDevice, freeze):
        sc = self.devices[scDevice]
        if freeze:
            return sc.freeze()
        else:
            return sc.unfreeze()

    @deviceMethod
    def toggleOverlay(self, scDevice, overlay):
        sc = self.devices[scDevice]
        if overlay:
            return sc.overlayOn()
        else:
            return sc.overlayOff()

    @deviceMethod
    def toggleFade(self, scDevice, fade):
        sc = self.devices[scDevice]
        if fade:
            return sc.fadeOut()
        else:
            return sc.fadeIn()

    @deviceMethod
    def recalibrate(self, scDevice):
        sc = self.devices[scDevice]
        return sc.recalibrate()
