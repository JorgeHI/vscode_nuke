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

# Estado inicial del servidor
server_running = False

def toggle_server():
    """Activa o desactiva el servidor y actualiza el icono."""
    global server_running

    if server_running:
        # Detener servidor aquí si es necesario
        server_running = False
        dev_menu.addCommand("Nuke Connect", toggle_server, icon=off_icon) 
        print("Nuke Connect: Server OFF")
    else:
        # Iniciar servidor aquí si es necesario
        server_running = True
        dev_menu.addCommand("Nuke Connect", toggle_server, icon=on_icon)  # Para menú de texto
        print("Nuke Connect: Server ON")

# Buscar el menú "Dev" o crearlo si no existe
main_menu = nuke.menu("Nuke")
dev_menu = main_menu.findItem("Dev") or main_menu.addMenu("Dev")

# Añadir al menú Dev
dev_menu.addCommand("Nuke Connect", toggle_server, icon=off_icon)  # Para menú de texto
