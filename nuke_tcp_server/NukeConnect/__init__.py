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
import NukeConnect.server as server
from NukeConnect import serverui 

# Preferences tab
serverui.add_nuke_connect_prefs_tab()
# Server
tcp_server = server.NukeTcpServer()
tcp_server.init()
# Menu
tcp_server_menu = serverui.NukeTcpServerMenu(tcp_server)
