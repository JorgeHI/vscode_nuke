import NukeTcpServer.server as server
import NukeTcpServer.serverui as menu
import NukeTcpServer.pref as pref

# Preferences tab
pref.add_nuke_connect_prefs_tab()
# Server
tcp_server = server.NukeTcpServer()
tcp_server.init()
# Menu
tcp_server_menu = menu.NukeTcpServerMenu(tcp_server)
