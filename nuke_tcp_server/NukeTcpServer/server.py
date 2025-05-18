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

import NukeTcpServer.nkLogger as nkLogger
logger = nkLogger.getLogger(__name__)

class NukeTcpServer(QtCore.QObject):
    serverStateChanged = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(NukeTcpServer, self).__init__(parent)
        self.server = QtNetwork.QTcpServer(self)

        self.port = 8080
        self.connection = None
        self.server.newConnection.connect(self.handle_connection)
        self.running = False

    def init(self):
        prefs = nuke.toNode('preferences')
        if prefs is None:
            logger.warning("Preferences node not found. Nuke Connect server will not start.")
            return
        port_knob = prefs.knob("nuke_connect_port")
        startup_on = prefs.knob("nuke_connect_auto_startup")
        if port_knob is not None:
            self.port = port_knob.value()
        if startup_on is not None:
            if startup_on.value():
                self.start()

    def start(self):
        if not self.server.listen(QtNetwork.QHostAddress.LocalHost, self.port):
            logger.error(f"Could not start server on port {self.port}")
            self.running =  False
        logger.info(f"Nuke Connect TCP server listening on port {self.port}")
        self.running =  True
        return self.running

    def stop(self):
        self.server.close()
        self.running = False
        logger.info("Nuke Connect TCP server stopped.")
        return self.running
    
    def is_running(self):
        return self.running

    def handle_connection(self):
        self.connection = self.server.nextPendingConnection()
        self.connection.readyRead.connect(self.read_data)

    def read_data(self, socket):
        if self.connection:
            data = socket.readAll().data()
            if len(data) >= 8:
                expected_len = int(data[:8].decode())
                if len(data) >= expected_len + 8:
                    message = data[8:expected_len+8].decode()
                    self.execute_command(message)

    def execute_command(self, command):
        """
        Ejecuta el comando recibido como código Python dentro de Nuke.
        """
        try:
            exec(command, globals(), locals())
        except Exception as e:
            logger.error(f"Error executing command:\n{e}")

