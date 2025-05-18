import nuke

import NukeTcpServer.nkLogger as nkLogger
logger = nkLogger.getLogger(__name__)


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

