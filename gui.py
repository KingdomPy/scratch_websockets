import sys, urllib.request, json
from PyQt5 import QtWidgets, QtGui, QtCore
from twisted.internet import reactor, protocol

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005

class kingdomNet(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.thumbnailUrl = "http://cdn2.scratch.mit.edu/get_image/project/"
        self.projectId = 0
        
        self.launchApp()

    def launchApp(self):
        self.screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.setFixedSize(self.screen.width()*0.2,self.screen.height()*0.4)
        self.setGeometry(self.screen.width()*0.795,self.screen.height()*0.555,self.screen.width()*0.2,self.screen.height()*0.4)
        self.setWindowTitle("Kingdom Net")
        
        #QtWidgets.QStyleFactory.create('Fusion')
        self.setStyleSheet("background-color: #41b7f2;")

        self.thumbnailImage = QtWidgets.QPushButton(self)
        self.thumbnailImage.setStyleSheet("""
                                background-color: black;
                                font-size: 18px;
                            """)
        self.reloadThumbnail()
        
        self.label = QtWidgets.QLineEdit(self)
        self.label.setFixedSize(self.screen.width()*0.15,self.screen.height()*0.03)
        self.label.move(self.screen.width()*0.025,self.screen.height()*0.24)
        self.label.setStyleSheet("""
                                background-color: white;
                                font-size: 18px;
                                border: 1px solid transparent;
                            """)
        self.label.setMaxLength(10)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.button = QtWidgets.QPushButton('Join', self)
        self.button.setFixedSize(self.screen.width()*0.15,self.screen.height()*0.08)
        self.button.move(self.screen.width()*0.025,self.screen.height()*0.29)
        self.button.setStyleSheet("""
                                box-style: border-box;
                                border: 1px solid transparent;
                                border-radius: 10%;
                                color: white;
                                font-size:30px;
                                font-weight: bold;
                                background-color: #f7c24f;
                            """)

        self.button.clicked.connect(lambda:self.fetchThumbnail())
                
        self.show()

    def fetchThumbnail(self):
        projectId = self.label.text()
        if self.projectId != projectId:
            self.projectId = projectId
            try:
                print(self.thumbnailUrl+projectId+"_480x360.png")
                urllib.request.urlretrieve(self.thumbnailUrl+projectId+"_480x360.png", "thumbnail.png")
                self.reloadThumbnail()
                #self.serverConnection.send(json.dumps({"method":"join", "projectId": projectId}))
            except Exception as e:
                print(e)

    def reloadThumbnail(self):
        iconPath = "thumbnail.png"
        pixmap = QtGui.QPixmap(iconPath)
        pixmapIcon = pixmap.scaledToWidth(self.screen.width()*0.15)
        self.thumbnailImage.setIcon(QtGui.QIcon(pixmapIcon))
        self.thumbnailImage.setIconSize(QtCore.QSize(pixmapIcon.width(), pixmapIcon.height()))
        self.thumbnailImage.move(self.screen.width()*0.025, self.screen.height()*0.02)
        self.thumbnailImage.setFixedSize(pixmapIcon.width(), pixmapIcon.height())

class twistedThread(QtCore.QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        factory = MyClientFactory()
        reactor.connectTCP(SERVER_IP, SERVER_PORT, factory)
        reactor.run(installSignalHandlers=0)
        
    def send(self, message):
        self.myClientChannel.send(message)

class MyClient(protocol.Protocol):
    def connectionMade(self):
        self.transport.write("test".encode())

    def dataReceived(self, data):
        print(data.decode())

    def send(self, message):
        self.transport.write(message.encode())

class MyClientFactory(protocol.ClientFactory):
    protocol = MyClient
    
if __name__ == "__main__":
    executable = QtWidgets.QApplication(sys.argv)
    app = kingdomNet()
    sys.exit(executable.exec_())
    """factory = MyClientFactory()
    reactor.connectTCP(SERVER_IP, SERVER_PORT, factory)
    reactor.run(installSignalHandlers=0)"""
    

    
