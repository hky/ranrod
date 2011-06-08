#! /usr/bin/env python
#                         _______
#   ____________ _______ _\__   /_________       ___  _____
#  |    _   _   \   _   |   ____\   _    /      |   |/  _  \
#  |    /   /   /   /   |  |     |  /___/   _   |   |   /  /
#  |___/___/   /___/____|________|___   |  |_|  |___|_____/
#          \__/                     |___|
#

__author__    = 'Wijnand Modderman-Lenstra'
__email__     = 'maze@pyth0n.org'
__copyright__ = 'Copyright 2011, maze.io labs'
__license__   = 'MIT'


# Constants
BYTE = dict(
    NULL        = chr(0),
    ECHO        = chr(1),
    SUPPRESS_GO_AHEAD = chr(3),
    STATUS      = chr(5),
    LF          = chr(10),
    CR          = chr(13),
    TERM_TYPE   = chr(24),
    WIN_SIZE    = chr(31),
    TERM_SPEED  = chr(32),
    RFC         = chr(33),  # Remote Flow Control
    LM          = chr(34),  # Line Mode
    XDL         = chr(35),  # X Display Location
    ENV         = chr(36),  # Environment_variables
    NEO         = chr(37),  # New Environment Option
    SE          = chr(240), # End of subnegotiation parameters.
    NOP         = chr(241), # No operation.
    DM          = chr(242), # The data stream portion of a Synch.
    BREAK       = chr(243), # NVT character BRK.
    IP          = chr(244), # Interrupt Process
    AO          = chr(245), # Abort Output
    AYT         = chr(246), # Are You There
    EC          = chr(247), # Erase Character
    EL          = chr(248), # Erase Line
    GA          = chr(249), # Go Ahead
    SB          = chr(250), # Indicates that what follows is subnegotiation of
                            # the indicated option.
    WILL        = chr(251), # Indicates the desire to begin performing, or
                            # confirmation that you are now performing, the
                            # indicated option.
    WONT        = chr(252), # Indicates the refusal to perform,or continue
                            # performing, the indicated option.
    DO          = chr(253), # Indicates the request that the other party
                            # perform, or confirmation that you are expecting
                            # the other party to perform, the indicated
                            # option.
    DONT        = chr(254), # Indicates the demand that the other party stop
                            # performing, or confirmation that you are no
                            # longer expecting the other party to perform, the
                            # indicated option.
    IAC         = chr(255), # Data Byte 255.
)

# Dictionary by name
NAME = dict((v, k) for k, v in BYTE.iteritems())
IS = chr(0) # Special one

# Export BYTEs to global namespace
for name in BYTE:
    globals()[name] = BYTE[name]
