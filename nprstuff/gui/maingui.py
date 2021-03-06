import os, sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from nprstuff.gui import newyorker, nytimes, vqronline, medium, lightspeed

class MainGui(QTabWidget):
    def __init__(self):
        super(MainGui, self).__init__()
        self.setWindowIcon( QIcon('icons/maingui.png') )
        self.setStyleSheet('QTabWidget {background-color: #f4faff; }')
        nyf = newyorker.NewYorkerFrame(showFrame = False)
        self.addTab( nyf,
                     QIcon('icons/newyorker.png'), 'New Yorker Printer' )
        self.addTab( nytimes.NYTimesFrame(showFrame = False),
                     QIcon('icons/nytimes.png'), 'NYTimes Printer' )
        self.addTab( vqronline.VQROnlineFrame(showFrame = False),
                     QIcon('icons/vqr.png'), 'VQR Online Printer')
        self.addTab( medium.MediumFrame(showFrame = False),
                     QIcon('icons/medium.png'), 'Medium.com')
        self.addTab( lightspeed.LightSpeedFrame(showFrame = False),
                     QIcon('icons/lightspeed.png'), 'Lightspeed Magazine')
        self.setWindowTitle('Main Printing GUI')
        self.setCurrentIndex(0)
        #
        # Ctrl-Q
        exitAction = QAction(self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        self.addAction(exitAction)
        #
        # Move-Right
        nextTabAction = QAction(self)
        nextTabAction.setShortcut('Ctrl+Right')
        nextTabAction.triggered.connect(self.nextTab)
        self.addAction(nextTabAction)
        #
        # Move-Left
        prevTabAction = QAction(self)
        prevTabAction.setShortcut('Ctrl+Left')
        prevTabAction.triggered.connect(self.prevTab)
        self.addAction(prevTabAction)
        #
        # Ctrl+1 -> newyorker
        firstTabAction = QAction(self)
        firstTabAction.setShortcut('Ctrl+1')
        firstTabAction.triggered.connect(self.firstIndex)
        self.addAction(firstTabAction)
        #
        # Ctrl+2 -> nytimes
        secondTabAction = QAction(self)
        secondTabAction.setShortcut('Ctrl+2')
        secondTabAction.triggered.connect(self.secondIndex)
        self.addAction(secondTabAction)
        #
        # Ctrl+3 -> vqr online
        thirdTabAction = QAction(self)
        thirdTabAction.setShortcut('Ctrl+3')
        thirdTabAction.triggered.connect(self.thirdIndex)
        self.addAction(thirdTabAction)
        #
        # Ctrl+4 -> medium.com
        fourthTabAction = QAction(self)
        fourthTabAction.setShortcut('Ctrl+4')
        fourthTabAction.triggered.connect(self.fourthIndex)
        self.addAction(fourthTabAction)
        #
        # Ctrl+5 -> lightspeed magazine
        fifthTabAction = QAction(self)
        fifthTabAction.setShortcut('Ctrl+5')
        fifthTabAction.triggered.connect(self.fifthIndex)
        self.addAction(fifthTabAction)
        
        #
        # make visible
        qfm = QFontMetrics( nyf.qf )
        wdth = int( 70 * qfm.averageCharWidth() * 1.25 )
        self.resize( wdth, 900)
        self.setFixedWidth( wdth )
        self.show()

    def firstIndex(self):
        self.setCurrentIndex(0)

    def secondIndex(self):
        self.setCurrentIndex(1)
        
    def thirdIndex(self):
        self.setCurrentIndex(2)
        
    def fourthIndex(self):
        self.setCurrentIndex(3)

    def fifthIndex(self):
        self.setCurrentIndex(4)
        
    def nextTab(self):
        cIndx = self.currentIndex()
        if cIndx == self.count() - 1: nIndx = 0
        else: nIndx = cIndx + 1
        self.setCurrentIndex( nIndx )
    
    def prevTab(self):
        cIndx = self.currentIndex()
        if cIndx == 0: nIndx = self.count() - 1
        else: nIndx = cIndx - 1
        self.setCurrentIndex( nIndx )
