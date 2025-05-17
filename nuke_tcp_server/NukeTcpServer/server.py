# -*- coding: utf-8 -*-
import nuke
if nuke.NUKE_VERSION_MAJOR < 11:
    # PySide for Nuke up to 10
    from PySide import QtCore, QtNetwork 
    pyside_version = 1
elif nuke.NUKE_VERSION_MAJOR < 16:
    # PySide2 for default Nuke 11
    from PySide2 import QtCore, QtNetwork 
    pyside_version = 2
else:
    # PySide6 for Nuke 16+
    from PySide6 import QtCore, QtNetwork 
    pyside_version = 6

import nkLogger

logger = nkLogger.getLogger(__name__)

class NukeTcpServer(QtCore.QObject):
    serverStateChanged = QtCore.Signal(bool)

    def __init__(self, port=8080, parent=None):
        super(NukeTcpServer, self).__init__(parent)
        self.port = port
        self.server = QtNetwork.QTcpServer(self)
        self.server.newConnection.connect(self.handle_new_connection)

        if not self.server.listen(QtNetwork.QHostAddress.LocalHost, self.port):
            logger.error(f"Could not start server on port {self.port}")
        else:
            logger.info(f"Nuke Connect TCP server started on port {self.port}")

        self.connections = []

    def handle_new_connection(self):
        client_socket = self.server.nextPendingConnection()
        client_socket.readyRead.connect(lambda: self.read_data(client_socket))
        client_socket.disconnected.connect(lambda: self.remove_connection(client_socket))
        self.connections.append(client_socket)
        print("New connection accepted.")

    def read_data(self, socket):
        while socket.bytesAvailable():
            data = socket.readAll().data()
            print(f"Received: {data}")
            if len(data) >= 8:
                expected_len = int(data[:8].decode())
                if len(data) >= expected_len + 8:
                    message = data[8:expected_len+8].decode()
                    self.execute_command(message)
            
    def remove_connection(self, socket):
        print("Connection closed.")
        if socket in self.connections:
            self.connections.remove(socket)
            socket.deleteLater()

    def execute_command(self, command):
        """
        Ejecuta el comando recibido como código Python dentro de Nuke.
        """
        try:
            exec(command, globals(), locals())
        except Exception as e:
            nuke.message(f"Error executing command:\n{e}")
            print(e)

