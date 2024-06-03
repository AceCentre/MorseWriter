import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtNetwork import QTcpServer, QHostAddress

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server = QTcpServer(self)
        self.server.listen(QHostAddress.Any, 8080)
        self.server.newConnection.connect(self.handle_new_connection)

    def handle_new_connection(self):
        client = self.server.nextPendingConnection()
        client.readyRead.connect(lambda: self.read_data(client))

    def read_data(self, client):
        data = client.readAll()
        print("Received:", data.data().decode())
        client.disconnectFromHost()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
