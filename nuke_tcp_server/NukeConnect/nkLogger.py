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
import logging

class NukeHandler(logging.Handler):
    """
    Custom logging handler that outputs log messages to Nuke's Script Editor.

    This handler uses the standard 'print()' function so that messages appear
    inside Nuke's internal script editor panel.

    Inherits from:
        logging.Handler
    """
    def emit(self, record):
        """
        Emit a log record by formatting it and printing to stdout.

        Args:
            record (logging.LogRecord): The log record to output.
        """
        try:
            msg = self.format(record)
            print(msg)
        except Exception:
            pass

def getLogger(module_name):
    """
    Creates and configures a logger instance for the given module name.

    The logger is configured with:
      - A standard stream handler that outputs to the console.
      - A custom NukeHandler that prints to Nuke's Script Editor.
      - A consistent formatter with time, level, and module info.

    Args:
        module_name (str): The name of the module using the logger.

    Returns:
        logging.Logger: A configured logger instance for use.
    """
    # Create a logger for this module
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)  # Set minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.propagate = False
    # Create console handler and set its log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter and attach it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s:NkSE:%(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    nh = NukeHandler()
    nh.setLevel(logging.DEBUG)
    nh.setFormatter(formatter)
    logger.addHandler(nh)

    return logger
