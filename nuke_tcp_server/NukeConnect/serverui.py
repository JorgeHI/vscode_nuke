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
import nuke

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

def add_nuke_connect_prefs_tab():
    prefs = nuke.toNode('preferences')
    if prefs is None:
        return
    # Avoid duplicate tab
    if prefs.knob('dev_tab') is not None:
        return
    tab_knob = nuke.Tab_Knob('dev_tab', 'Development')
    label_knob = nuke.Text_Knob('nuke_connect', 'Nuke Connect')
    port_knob = nuke.Int_Knob('nuke_connect_port', 'Port')
    port_knob.setTooltip('Port number for Nuke Connect server.')
    port_knob.setValue(8080)
    auto_startup_knob = nuke.Boolean_Knob('nuke_connect_auto_startup', 'Auto Startup')
    auto_startup_knob.setTooltip('Automatically start Nuke Connect server on launch.')
    auto_startup_knob.setValue(False)
    prefs.addKnob(tab_knob)
    prefs.addKnob(label_knob)
    prefs.addKnob(port_knob)
    prefs.addKnob(auto_startup_knob)