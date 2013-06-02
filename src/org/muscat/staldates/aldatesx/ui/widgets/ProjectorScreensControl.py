from PySide.QtCore import Qt, QSize
from PySide.QtGui import QButtonGroup, QIcon, QLabel, QGridLayout, QWidget
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton,\
    IDedButton
from Pyro4.errors import NamingError, ProtocolError
from org.muscat.staldates.aldatesx.StringConstants import StringConstants


class ProjectorScreensControl(QWidget):
    '''
    Controls for the projector screens.
    '''

    def __init__(self, controller, mainWindow):
        super(ProjectorScreensControl, self).__init__()
        self.controller = controller
        self.mainWindow = mainWindow

        layout = QGridLayout()

        title = QLabel("Projector Screens")
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 7)

        self.screens = QButtonGroup()

        btnLeft = IDedButton(1)
        btnLeft.setText("Left")
        layout.addWidget(btnLeft, 1, 0, 1, 2)
        btnLeft.setCheckable(True)
        self.screens.addButton(btnLeft, 0)

        btnAll = IDedButton(0)
        btnAll.setText("Both")
        layout.addWidget(btnAll, 1, 2, 1, 3)
        btnAll.setCheckable(True)
        btnAll.setChecked(True)
        self.screens.addButton(btnAll, 0)

        btnRight = IDedButton(2)
        btnRight.setText("Right")
        layout.addWidget(btnRight, 1, 5, 1, 2)
        btnRight.setCheckable(True)
        self.screens.addButton(btnRight, 0)

        iconSize = QSize(96, 96)

        btnRaise = ExpandingButton()
        btnRaise.setText("Raise")
        btnRaise.setIcon(QIcon("icons/go-up.svg"))
        btnRaise.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnRaise, 2, 1, 1, 3)
        btnRaise.setIconSize(iconSize)
        btnRaise.clicked.connect(self.raiseUp)

        btnLower = ExpandingButton()
        btnLower.setText("Lower")
        btnLower.setIcon(QIcon("icons/go-down.svg"))
        btnLower.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnLower, 3, 1, 1, 3)
        btnLower.setIconSize(iconSize)
        btnLower.clicked.connect(self.lowerDown)

        btnStop = ExpandingButton()
        btnStop.setText("Stop")
        btnStop.setIcon(QIcon("icons/process-stop.svg"))
        btnStop.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnStop, 2, 4, 2, 2)
        btnStop.setIconSize(iconSize)
        btnStop.clicked.connect(self.stop)

        self.b = ExpandingButton()
        self.b.setText("Back")
        layout.addWidget(self.b, 4, 1, 1, 5)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 2)
        layout.setRowStretch(2, 2)
        layout.setRowStretch(3, 2)
        layout.setRowStretch(4, 1)

        self.setLayout(layout)

    def raiseUp(self):
        screenID = self.screens.checkedId()
        try:
            self.controller.raiseUp("Screens", screenID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def lowerDown(self):
        screenID = self.screens.checkedId()
        try:
            self.controller.lower("Screens", screenID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def stop(self):
        screenID = self.screens.checkedId()
        try:
            self.controller.stop("Screens", screenID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)