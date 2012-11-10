from PySide.QtGui import *
from PySide.QtCore import *

class ExpandingButton(QPushButton):
    def __init__(self, parent):
        super(ExpandingButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
class InputButton(ExpandingButton):
    def __init__(self, parent):
        super(InputButton, self).__init__(parent)
        self.setCheckable(True)
        
class OutputButton(ExpandingButton):
    def __init__(self, parent, ID):
        super(OutputButton, self).__init__(parent)
        self.ID = ID

class VideoSwitcher(QWidget):
    def __init__(self, controller):
        super(VideoSwitcher, self).__init__()
        self.setupUi(self)
        self.controller = controller
        
    def setupUi(self, VideoSwitcher):
        self.setWindowTitle("Video Switcher")
        self.resize(1024, 768)
        self.centralwidget = QWidget(self)
        self.centralwidget.setGeometry(0, 0, 1024, 768)
        gridlayout = QGridLayout(self.centralwidget)
        
        ''' Buttons added to inputs should have a numeric ID set equal to their input number on the Aldates main switcher. '''
        self.inputs = QButtonGroup()
        
        self.btnDVD = InputButton(self.centralwidget)
        self.btnDVD.setText("DVD")
        gridlayout.addWidget(self.btnDVD, 0, 0)
        self.inputs.addButton(self.btnDVD, 4)
        
        self.btnCamera1 = InputButton(self.centralwidget)
        self.btnCamera1.setText("Camera 1")
        gridlayout.addWidget(self.btnCamera1, 0, 1)
        self.inputs.addButton(self.btnCamera1, 1)
        
        self.btnCamera2 = InputButton(self.centralwidget)
        self.btnCamera2.setText("Camera 2")
        gridlayout.addWidget(self.btnCamera2, 0, 2)
        self.inputs.addButton(self.btnCamera2, 2)
        
        self.btnCamera3 = InputButton(self.centralwidget)
        self.btnCamera3.setText("Camera 3")
        gridlayout.addWidget(self.btnCamera3, 0, 3)
        self.inputs.addButton(self.btnCamera3, 3)
        
        self.btnExtras = InputButton(self.centralwidget)
        self.btnExtras.setText("Extras")
        gridlayout.addWidget(self.btnExtras, 0, 4)
        self.inputs.addButton(self.btnExtras, 5)
        
        self.btnVisualsPC = InputButton(self.centralwidget)
        self.btnVisualsPC.setText("Visuals PC")
        gridlayout.addWidget(self.btnVisualsPC, 0, 5)
        self.inputs.addButton(self.btnVisualsPC, 6)
        
        blank = QWidget(self.centralwidget)
        gridlayout.addWidget(blank, 1, 0, 1, 5)
        
        outputsGrid = QGridLayout()
        
        self.btnProjectors = OutputButton(self.centralwidget, ID=2)
        self.btnProjectors.setText("Projectors")
        outputsGrid.addWidget(self.btnProjectors, 0, 1)

        self.btnChurch = OutputButton(self.centralwidget, ID=4)
        self.btnChurch.setText("Church")
        outputsGrid.addWidget(self.btnChurch, 1, 0)
        self.btnSpecial = OutputButton(self.centralwidget, ID=7)
        self.btnSpecial.setText("Special")
        outputsGrid.addWidget(self.btnSpecial, 1, 1)
        
        self.btnGallery = OutputButton(self.centralwidget, ID=6)
        self.btnGallery.setText("Gallery")
        outputsGrid.addWidget(self.btnGallery, 2, 0)
        self.btnWelcome = OutputButton(self.centralwidget, ID=5)
        self.btnWelcome.setText("Welcome")
        outputsGrid.addWidget(self.btnWelcome, 2, 1)

        self.btnFont = OutputButton(self.centralwidget, ID=3)
        self.btnFont.setText("Font")
        outputsGrid.addWidget(self.btnFont, 3, 0)
        self.btnRecord = OutputButton(self.centralwidget, ID=8)
        self.btnRecord.setText("Record")
        outputsGrid.addWidget(self.btnRecord, 3, 1)

        self.btnPCMix = ExpandingButton(self.centralwidget)
        self.btnPCMix.setText("PC Mix")
        outputsGrid.addWidget(self.btnPCMix, 4, 0)
        self.btnAll = OutputButton(self.centralwidget, ID=0)
        self.btnAll.setText("All")
        outputsGrid.addWidget(self.btnAll, 4, 1)
        
        outputsGrid.setColumnMinimumWidth(0, 100)
        outputsGrid.setColumnMinimumWidth(1, 100)
        outputsGrid.setColumnStretch(0, 1)
        outputsGrid.setColumnStretch(1, 1)
        
        gridlayout.addLayout(outputsGrid, 1, 6)

        gridlayout.setRowMinimumHeight(1, 500)      
        gridlayout.setRowStretch(0, 1)  
        gridlayout.setRowStretch(1, 5)  
        QMetaObject.connectSlotsByName(self)
        self.setInputClickHandlers()
        self.setOutputClickHandlers()
        
    def setInputClickHandlers(self):
        self.btnCamera1.clicked.connect(self.handleInputSelect)
        self.btnCamera2.clicked.connect(self.handleInputSelect)
        self.btnCamera3.clicked.connect(self.handleInputSelect)
        self.btnDVD.clicked.connect(self.handleInputSelect)
        self.btnExtras.clicked.connect(self.handleInputSelect)
        self.btnVisualsPC.clicked.connect(self.handleInputSelect)
        
    def setOutputClickHandlers(self):
        self.btnProjectors.clicked.connect(self.handleOutputSelect)
        self.btnChurch.clicked.connect(self.handleOutputSelect)
        self.btnSpecial.clicked.connect(self.handleOutputSelect)
        self.btnGallery.clicked.connect(self.handleOutputSelect)
        self.btnWelcome.clicked.connect(self.handleOutputSelect)
        self.btnFont.clicked.connect(self.handleOutputSelect)
        self.btnAll.clicked.connect(self.handleOutputSelect)
        ''' btnPCMix is a special case since that's on a different switcher '''
        
    def handleInputSelect(self):
        print "Input selected: " + str(self.inputs.checkedId())
        
    def handleOutputSelect(self):
        sender = self.sender()
        switcher = self.controller.getDevice("Main")
        switcher.sendInputToOutput(self.inputs.checkedId(), sender.ID)
        
