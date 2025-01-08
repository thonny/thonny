# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Renode Cortex-M0+
 - port: renode
 - board_id: renode_cortex_m0plus
 - NVM size: Unknown
 - Included modules: array, board, builtins, busio, busio.UART, collections, math, microcontroller, os, rainbowio, struct, supervisor, sys, time
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO0
RX: microcontroller.Pin  # GPIO1


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
