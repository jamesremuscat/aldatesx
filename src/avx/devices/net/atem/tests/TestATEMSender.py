from avx.devices.net.atem.constants import SIZE_OF_HEADER, VideoSource,\
    TransitionStyle
from avx.devices.net.atem.tests import BaseATEMTest
from avx.devices.net.atem.utils import byteArrayToString,\
    NotInitializedException
from avx.devices.Device import InvalidArgumentException


def bytes_of(val):
    return [(val >> 8), (val & 0xFF)]


class TestATEMSender(BaseATEMTest):
    def assert_sent_packet(self, cmd, payload):
        self.assertFalse(self.atem._socket.sendto.call_args is None, '_socket.sendto never called!')
        args = self.atem._socket.sendto.call_args[0]
        self.assertEqual(2, len(args))
        packet = args[0]

        if not isinstance(payload, str):
            payload = byteArrayToString(payload)

        self.assertEqual(cmd, packet[SIZE_OF_HEADER + 4:SIZE_OF_HEADER + 8])
        self.assertEqual(payload, packet[SIZE_OF_HEADER + 8:])

    def setUp(self):
        BaseATEMTest.setUp(self)
        self.atem._handlePacket(byteArrayToString([0x08, 0x0c, 0xab, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x12]))
        self.send_command('_top', [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.send_command(
            'InPr',
            bytes_of(VideoSource.COLOUR_BARS.value) +
            map(ord, 'Input Long Name') + [0, 0, 0, 0, 0] +  # Long name always 20 bytes
            map(ord, 'InLN') +  # Short name always 4 bytes
            [0, 0x0F, 0, 1, 2, 0, 0x1E, 0x02, 0, 0]
        )
        self.atem._socket.reset_mock()

    def testSetAuxSourceWithoutInit(self):
        self.atem._isInitialized = False

        try:
            self.atem.setPreview("Not initialised so going to fail", 0)
            self.fail("Should have thrown an exception as not initialised")
        except NotInitializedException:
            pass

    def testSetAuxSource(self):
        try:
            self.atem.setAuxSource(2, 0)
            self.fail("Aux 2 shouldn't exist!")
        except InvalidArgumentException:
            pass

        self.atem.setAuxSource(1, VideoSource.COLOUR_BARS)
        self.assert_sent_packet('CAuS', [1, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

    def testSetPreview(self):
        try:
            self.atem.setPreview(VideoSource.COLOUR_BARS, 2)
            self.fail("ME 2 shouldn't exist!")
        except InvalidArgumentException:
            pass

        self.atem.setPreview(VideoSource.COLOUR_BARS, 1)
        self.assert_sent_packet('CPvI', [0, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

# OK, I think we've tested the @requiresInit and @assertTopology decorators enough now...

    def testSetProgram(self):
        self.atem.setProgram(VideoSource.COLOUR_BARS)
        self.assert_sent_packet('CPgI', [0, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

    def testPerformCut(self):
        self.atem.performCut(1)
        self.assert_sent_packet('DCut', [0, 0, 0, 0])

    def testPerformAutoTake(self):
        self.atem.performAutoTake()
        self.assert_sent_packet('DAut', [0, 0, 0, 0])

    def testSetNextTransition(self):
        self.atem.setNextTransition(TransitionStyle.MIX, bkgd=True, key1=True, key2=False, key3=False, key4=False, me=1)
        self.assert_sent_packet('CTTp', [0x03, 0, 0, 0x03])

        self.atem._socket.reset_mock()
        self.atem.setNextTransition(TransitionStyle.WIPE)
        self.assert_sent_packet('CTTp', [0x01, 0, 2, 0x00])

        self.atem._socket.reset_mock()
        self.atem.setNextTransition(TransitionStyle.DIP, True, True, True, True, True)
        self.assert_sent_packet('CTTp', [0x03, 0, 1, 0x1F])