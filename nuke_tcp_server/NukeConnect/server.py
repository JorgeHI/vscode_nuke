# -----------------------------------------------------------------------------
# VSCode connection to Nuke plugin
# Copyright (c) 2025 Jorge Hernandez Ibañez
#
# This file is part of the Nuke connect for vscode project.
# Repository: https://github.com/JorgeHI/vscode_nuke
#
# This file is licensed under the MIT License.
# See the LICENSE file in the root of this repository for details.
# -----------------------------------------------------------------------------
import sys
import io
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

import NukeConnect.nkLogger as nkLogger
logger = nkLogger.getLogger(__name__)

SERVER_GLOBALS = {"nuke": nuke}

class NukeTcpServer(QtCore.QObject):
    """
    TCP server for handling connections between VSCode and Nuke.
    Listens for incoming commands, executes them in Nuke, and returns the output.
    """
    serverStateChanged = QtCore.Signal(bool)

    def __init__(self, parent=None):
        """
        Initialize the NukeTcpServer instance, set up the TCP server and default parameters.
        """
        super(NukeTcpServer, self).__init__(parent)
        self.server = QtNetwork.QTcpServer(self)

        self.port = 8080
        self.connection = None
        self.server.newConnection.connect(self.handle_connection)
        self.running = False

    def init(self):
        """
        Initialize the server using preferences from Nuke.
        Reads the port and auto-startup settings from the preferences node.
        """
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
        """
        Start the TCP server and listen for incoming connections on the specified port.
        Returns True if the server started successfully, False otherwise.
        """
        if not self.server.listen(QtNetwork.QHostAddress.LocalHost, self.port):
            logger.error(f"Could not start server on port {self.port}")
            self.running =  False
        logger.info(f"Nuke Connect TCP server listening on port {self.port}")
        self.running =  True
        return self.running

    def stop(self):
        """
        Stop the TCP server and close all connections.
        Returns False after stopping the server.
        """
        self.server.close()
        self.running = False
        logger.info("Nuke Connect TCP server stopped.")
        return self.running
    
    def is_running(self):
        """
        Check if the server is currently running.
        Returns True if running, False otherwise.
        """
        return self.running

    def handle_connection(self):
        """
        Handle a new incoming connection from a client.
        Sets up the connection to read incoming data.
        """
        self.connection = self.server.nextPendingConnection()
        self.connection.readyRead.connect(self.read_data)

    def read_data(self):
        """
        Read incoming data from the client, extract the command, execute it, and send back the output.
        """
        if self.connection:
            data = self.connection.readAll().data()
            if len(data) >= 8:
                expected_len = int(data[:8].decode())
                if len(data) >= expected_len + 8:
                    message = data[8:expected_len+8].decode()
                    out = self.execute_command(message)
                    if out is not None:
                        try:
                            logger.debug(f"Sending output back to client: {out[:200]}{'...' if len(out) > 200 else ''}")
                            self.send_output_msg(out)
                        except Exception as e:
                            logger.error(f"Output submition failed: {e}")

    def execute_command(self, command, scope="global"):
        """
        Execute a Python command in the specified scope.
        Captures and returns stdout and stderr output, including any exceptions.
        
        Args:
            command (str): The Python command to execute.
            scope (str): The scope in which to execute the command ("global" or other).
        
        Returns:
            str: The combined output and error messages from execution.
        """
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            if scope == "global":
                exec(command, SERVER_GLOBALS)
            else:
                exec(command, {})
            output = sys.stdout.getvalue() + sys.stderr.getvalue()
        except Exception as e:
            output = sys.stdout.getvalue() + sys.stderr.getvalue()
            output += f"\n[Nuke Connect] Exception: {e}"
            logger.error(f"Error executing command:\n{e}")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        return output
    
    def send_output_msg(self, output):
        """
        Send the output message back to the connected client.
        The message is prefixed with its length as an 8-byte header.
        
        Args:
            output (str): The output string to send to the client.
        """
        if not self.connection:
            return
        try:
            msg_data = output.encode("utf-8")
            length_header = str(len(msg_data)).zfill(8).encode("utf-8")
            self.connection.write(length_header + msg_data)
            logger.debug(f"Output sent to client ({len(msg_data)} bytes)")
        except Exception as e:
            logger.error(f"Error sending output to client: {e}")

