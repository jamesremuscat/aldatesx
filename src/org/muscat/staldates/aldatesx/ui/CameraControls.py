from PySide.QtGui import QButtonGroup, QGridLayout, QLabel, QWidget, QIcon, QMessageBox, QSizePolicy, QVBoxLayout
from PySide.QtCore import QSize, Qt
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton
from org.muscat.staldates.aldatesx.Controller import CameraMove, CameraFocus, CameraZoom
from Pyro4.errors import NamingError, ProtocolError
from org.muscat.staldates.aldatesx.StringConstants import StringConstants


class CameraButton(ExpandingButton):
    def __init__(self, cameraBinding):
        super(CameraButton, self).__init__()
        self.cameraBinding = cameraBinding
        self.setIconSize(QSize(64, 64))


class PlusMinusButtons(QWidget):

    def __init__(self, caption, upBinding, downBinding):
        super(PlusMinusButtons, self).__init__()
        self.upButton = CameraButton(upBinding)
        self.upButton.setIcon(QIcon("icons/gtk-add.svg"))

        self.downButton = CameraButton(downBinding)
        self.downButton.setIcon(QIcon("icons/gtk-remove.svg"))

        self.caption = QLabel("<b>" + caption + "</b>")
        self.caption.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.initLayout()

    def initLayout(self):

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.upButton, 0, 0)
        layout.addWidget(self.caption, 1, 0)
        layout.addWidget(self.downButton, 2, 0)

        layout.setRowStretch(0, 2)
        layout.setRowStretch(1, 2)
        layout.setRowStretch(2, 2)

    def connectPressed(self, connection):
        self.upButton.pressed.connect(connection)
        self.downButton.pressed.connect(connection)

    def connectReleased(self, connection):
        self.upButton.released.connect(connection)
        self.downButton.released.connect(connection)

    def connectClicked(self, connection):
        self.upButton.clicked.connect(connection)
        self.downButton.clicked.connect(connection)


class PlusMinusAutoButtons(PlusMinusButtons):

    def __init__(self, caption, upBinding, downBinding, autoBinding):
        self.autoButton = CameraButton(autoBinding)
        self.autoButton.setText("Auto")
        super(PlusMinusAutoButtons, self).__init__(caption, upBinding, downBinding)

    def initLayout(self):
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.upButton, 0, 0)
        layout.addWidget(self.caption, 1, 0)
        layout.addWidget(self.autoButton, 2, 0)
        layout.addWidget(self.downButton, 3, 0)

        layout.setRowStretch(0, 2)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 2)


class CameraControl(QWidget):
    '''
    GUI to control a camera.
    '''

    def __init__(self, controller, cameraID):
        super(CameraControl, self).__init__()
        self.controller = controller
        self.cameraID = cameraID
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.btnUp = CameraButton(CameraMove.Up)
        layout.addWidget(self.btnUp, 0, 1, 2, 1)
        self.btnUp.pressed.connect(self.move)
        self.btnUp.released.connect(self.stop)
        self.btnUp.setIcon(QIcon("icons/up.svg"))

        self.btnLeft = CameraButton(CameraMove.Left)
        layout.addWidget(self.btnLeft, 1, 0, 2, 1)
        self.btnLeft.pressed.connect(self.move)
        self.btnLeft.released.connect(self.stop)
        self.btnLeft.setIcon(QIcon("icons/back.svg"))

        self.btnDown = CameraButton(CameraMove.Down)
        layout.addWidget(self.btnDown, 2, 1, 2, 1)
        self.btnDown.pressed.connect(self.move)
        self.btnDown.released.connect(self.stop)
        self.btnDown.setIcon(QIcon("icons/down.svg"))

        self.btnRight = CameraButton(CameraMove.Right)
        layout.addWidget(self.btnRight, 1, 2, 2, 1)
        self.btnRight.pressed.connect(self.move)
        self.btnRight.released.connect(self.stop)
        self.btnRight.setIcon(QIcon("icons/forward.svg"))

        zoomInOut = PlusMinusButtons("Zoom", CameraZoom.Tele, CameraZoom.Wide)
        zoomInOut.connectPressed(self.zoom)
        zoomInOut.connectReleased(self.stopZoom)
        layout.addWidget(zoomInOut, 0, 3, 4, 1)

        focus = PlusMinusAutoButtons("Focus", CameraFocus.Far, CameraFocus.Near, CameraFocus.Auto)
        focus.connectPressed(self.focus)
        focus.connectReleased(self.stopFocus)
        focus.autoButton.clicked.connect(self.focus)
        layout.addWidget(focus, 0, 4, 4, 1)

        brightness = PlusMinusButtons("Brightness", True, False)
        brightness.connectClicked(self.exposure)
        layout.addWidget(brightness, 0, 5, 4, 1)

        presets = QGridLayout()
        presets.setRowStretch(0, 2)
        presets.setRowStretch(1, 1)

        self.presetGroup = QButtonGroup()

        for i in range(0, 6):
            btnPresetRecall = CameraButton(i)
            presets.addWidget(btnPresetRecall, 0, i, 1, 1)
            btnPresetRecall.setText(str(i + 1))
            btnPresetRecall.clicked.connect(self.recallPreset)
            btnPresetRecall.setCheckable(True)
            self.presetGroup.addButton(btnPresetRecall, i)

            btnPresetSet = CameraButton(i)
            presets.addWidget(btnPresetSet, 1, i, 1, 1)
            btnPresetSet.setText("Set")
            btnPresetSet.clicked.connect(self.storePreset)

        layout.addLayout(presets, 4, 0, 3, 6)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.btnLeft.pressed.emit()
        elif e.key() == Qt.Key_Right:
            self.btnRight.pressed.emit()
        elif e.key() == Qt.Key_Up:
            self.btnUp.pressed.emit()
        elif e.key() == Qt.Key_Down:
            self.btnDown.pressed.emit()

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.btnLeft.released.emit()
        elif e.key() == Qt.Key_Right:
            self.btnRight.released.emit()
        elif e.key() == Qt.Key_Up:
            self.btnUp.released.emit()
        elif e.key() == Qt.Key_Down:
            self.btnDown.released.emit()

    def move(self):
        sender = self.sender()
        try:
            result = self.controller.move(self.cameraID, sender.cameraBinding)
            self.deselectPreset()
            return result
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def stop(self):
        try:
            self.controller.move(self.cameraID, CameraMove.Stop)
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def focus(self):
        sender = self.sender()
        try:
            result = self.controller.focus(self.cameraID, sender.cameraBinding)
            self.deselectPreset()
            return result
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def stopFocus(self):
        try:
            self.controller.focus(self.cameraID, CameraFocus.Stop)
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def zoom(self):
        sender = self.sender()
        try:
            result = self.controller.zoom(self.cameraID, sender.cameraBinding)
            self.deselectPreset()
            return result
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def stopZoom(self):
        try:
            self.controller.zoom(self.cameraID, CameraZoom.Stop)
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def exposure(self):
        sender = self.sender()
        try:
            result = self.controller.backlightComp(self.cameraID, sender.cameraBinding)
            self.deselectPreset()
            return result
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def storePreset(self):
        sender = self.sender()
        try:
            result = self.controller.savePreset(self.cameraID, sender.cameraBinding)
            self.presetGroup.buttons()[sender.cameraBinding].setChecked(True)
            return result
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def recallPreset(self):
        sender = self.sender()
        try:
            return self.controller.recallPreset(self.cameraID, sender.cameraBinding)
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def deselectPreset(self):
        # Yuck.
        self.presetGroup.setExclusive(False)
        while (self.presetGroup.checkedId() >= 0):
            self.presetGroup.checkedButton().setChecked(False)
        self.presetGroup.setExclusive(True)

    def errorBox(self, text):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec_()


class AdvancedCameraControl(QWidget):

    def __init__(self, controller, cameraID, parent=None):
        super(AdvancedCameraControl, self).__init__(parent)
        self.controller = controller
        self.cameraID = cameraID

        layout = QVBoxLayout(self)

        title = QLabel(self.cameraID)
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btnGetPos = ExpandingButton()
        btnGetPos.setText("Get Position")
        btnGetPos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(btnGetPos)
        btnGetPos.clicked.connect(self.displayPosition)

        self.posDisplay = QGridLayout()

        self.posDisplay.addWidget(QLabel("Pan:"), 0, 0)
        self.posDisplay.addWidget(QLabel("Tilt:"), 1, 0)
        self.posDisplay.addWidget(QLabel("Zoom:"), 2, 0)

        layout.addLayout(self.posDisplay)

        self.b = ExpandingButton()
        self.b.setText("Back")
        self.b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.b)

    def displayPosition(self):
        pos = self.controller.getPosition(self.cameraID)

        self.posDisplay.addWidget(QLabel(str(pos.pan)), 0, 1)
        self.posDisplay.addWidget(QLabel(str(pos.tilt)), 1, 1)
        self.posDisplay.addWidget(QLabel(str(pos.zoom)), 2, 1)
