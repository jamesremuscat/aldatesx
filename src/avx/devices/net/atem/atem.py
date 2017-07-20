from avx.devices import Device
from .constants import CMD_ACK, CMD_ACKREQUEST, CMD_HELLOPACKET, SIZE_OF_HEADER
from .utils import byteArrayToString
from .sender import ATEMSender
from .receiver import ATEMReceiver

import logging
import socket
import struct
import threading
import time

# Standing on the shoulders of giants:
# Much of this module derives from previous work including:
# - http://skaarhoj.com/fileadmin/BMDPROTOCOL.html
# - https://github.com/mraerino/PyATEM


class ATEM(Device, ATEMSender, ATEMReceiver):

    def __init__(self, deviceID, ipAddr, port=9910, **kwargs):
        super(ATEM, self).__init__(deviceID, **kwargs)
        self.ipAddr = ipAddr
        self.port = port
        self.log = logging.getLogger(deviceID)
        self.recv_thread = None

    def initialise(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('0.0.0.0', self.port))

        self._initialiseState()

        self.run_receive = True
        if not (self.recv_thread and self.recv_thread.is_alive()):
            self.recv_thread = threading.Thread(target=self._receivePackets)
            self.recv_thread.daemon = True
            self.recv_thread.start()

        threading.Thread(target=self._connectToSwitcher).start()

    def _initialiseState(self):
        self._packetCounter = 0
        self._isInitialized = False
        self._currentUid = 0x1337

        self._system_config = {'inputs': {}, 'audio': {}}
        self._status = {}
        self._config = {'multiviewers': {}, 'mediapool': {}, 'transitions': {}}
        self._state = {
            'program': {},
            'preview': {},
            'keyers': {},
            'dskeyers': {},
            'aux': {},
            'mediaplayer': {},
            'mediapool': {},
            'audio': {},
            'tally_by_index': {},
            'tally': {},
            'transition': {}
        }
        self._cameracontrol = {}

        self._state['booted'] = True

    def deinitialise(self):
        self.run_receive = False
        self._state['booted'] = False

    def _receivePackets(self):
        while self.run_receive:
            data, remoteIP = self._socket.recvfrom(2048)
            # self.log.debug("Received {} from {}:{}".format(data.encode('hex_codec'), *remoteIP))

            if remoteIP == (self.ipAddr, self.port):
                self._handlePacket(data)

    def _handlePacket(self, data):
                header = self._parseCommandHeader(data)
                if header:
                    self.log.debug(data.encode('hex_codec'))
                    self._currentUid = header['uid']
                    if header['bitmask'] & CMD_HELLOPACKET:
                        # print('not initialized, received HELLOPACKET, sending ACK packet')
                        self._isInitialized = False
                        ackDatagram = self._createCommandHeader(CMD_ACK, 0, header['uid'], 0x0)
                        self._sendDatagram(ackDatagram)

                    elif (header['bitmask'] & CMD_ACKREQUEST) and (self._isInitialized or len(data) == SIZE_OF_HEADER):
                        # print('initialized, received ACKREQUEST, sending ACK packet')
                        # print("Sending ACK for packageId %d" % header['packageId'])
                        ackDatagram = self._createCommandHeader(CMD_ACK, 0, header['uid'], header['packageId'])
                        self._sendDatagram(ackDatagram)
                        if not self._isInitialized:
                            self._isInitialized = True
                            self.log.info("Connection to ATEM initialised")

                    if len(data) > SIZE_OF_HEADER + 2 and not (header['bitmask'] & CMD_HELLOPACKET):
                        self._handlePayload(data[SIZE_OF_HEADER:])

    def _parseCommandHeader(self, datagram):
        header = {}

        if len(datagram) >= SIZE_OF_HEADER:
            header['bitmask'] = struct.unpack('B', datagram[0:1])[0] >> 3
            header['size'] = struct.unpack('!H', datagram[0:2])[0] & 0x07FF
            header['uid'] = struct.unpack('!H', datagram[2:4])[0]
            header['ackId'] = struct.unpack('!H', datagram[4:6])[0]
            header['packageId'] = struct.unpack('!H', datagram[10:12])[0]
            return header
        return False

    def _handlePayload(self, data):
        while len(data) > 0:
            size = struct.unpack('!H', data[0:2])[0]
            packet = data[0:size]
            data = data[size:]

            # skip size and 2 unknown bytes
            packet = packet[4:]
            ptype = packet[:4]
            payload = packet[4:]
            self.log.debug("{}: {}".format(ptype, payload.encode('hex_codec')))
            handler_method = "_recv_{}".format(ptype.encode('utf-8'))
            if handler_method in dir(self):
                func = getattr(self, handler_method)
                if callable(func):
                    payload_bytes = bytearray()
                    payload_bytes.extend(payload)  # Note: In Python2 need to ensure we have a byte array - or else it's a string
                    func(payload_bytes)
                else:
                    self.log.warning("Received {} but method {} is not callable".format(ptype, handler_method))
            else:
                self.log.warning("Unhandled ATEM packet type {}".format(ptype))

    def _connectToSwitcher(self):
        while not self._isInitialized:
            self.log.info("Attempting to connect to ATEM at {}:{}".format(self.ipAddr, self.port))
            datagram = self._createCommandHeader(CMD_HELLOPACKET, 8, self._currentUid, 0x0)
            datagram += struct.pack('!I', 0x01000000)
            datagram += struct.pack('!I', 0x00)
            self._sendDatagram(datagram)

            time.sleep(5)

    def _createCommandHeader(self, bitmask, payloadSize, uid, ackId):
        buf = b''
        packageId = 0

        if not (bitmask & (CMD_HELLOPACKET | CMD_ACK)):
            self._packetCounter += 1
            packageId = self._packetCounter

        val = bitmask << 11
        val |= (payloadSize + SIZE_OF_HEADER)
        buf += struct.pack('!H', val)
        buf += struct.pack('!H', uid)
        buf += struct.pack('!H', ackId)
        buf += struct.pack('!I', 0)
        buf += struct.pack('!H', packageId)
        return buf

    def _sendCommand(self, command, payload):

        if not isinstance(payload, str):
            payload = byteArrayToString(payload)

        size = len(command) + len(payload) + 4
        dg = self._createCommandHeader(CMD_ACKREQUEST, size, self._currentUid, 0)
        dg += struct.pack('!H', size)
        dg += "\x00\x00"
        dg += command
        dg += payload
        self._sendDatagram(dg)

    def _sendDatagram(self, datagram):
        self.log.debug("Sending packet {} to {}:{}".format(datagram.encode('hex_codec'), self.ipAddr, self.port))
        self._socket.sendto(datagram, (self.ipAddr, self.port))