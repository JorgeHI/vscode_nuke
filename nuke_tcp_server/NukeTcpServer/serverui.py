import nuke

# Compatibilidad con PySide2 / PySide6
try:
    from PySide2 import QtWidgets, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtGui

# Paths a los iconos
import os
base_path = os.path.dirname(__file__)
on_icon = os.path.join(base_path, "icons/icon_on.png")
off_icon = os.path.join(base_path, "icons/icon_off.png")


class NukeTcpServerMenu:
    def __init__(self, server):
        self.server = server
        self.create_menu()

    def create_menu(self):
        # Buscar el menú "Dev" o crearlo si no existe
        main_menu = nuke.menu("Nuke")
        self.dev_menu = main_menu.findItem("Dev") or main_menu.addMenu("Dev")

        # Añadir al menú Dev
        if self.server.is_running():
            self.update_command(on_icon)
        else:
            self.update_command(off_icon)

    def update_command(self, icon):
        """Actualiza el comando en el menú Dev."""
        self.dev_menu.addCommand("Nuke Connect", self.toggle_server, icon=icon)

    def toggle_server(self):
        """Activa o desactiva el servidor y actualiza el icono."""
        global server_running

        if self.server.is_running():
            # Detener servidor aquí si es necesario
            self.server.stop()
            self.update_command(off_icon)
        else:
            # Iniciar servidor aquí si es necesario
            self.server.start()
            self.update_command(on_icon)

