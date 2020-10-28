"""Network Interface Management

This module provides a registry of configured NICs.
It is used by the 'socket' module to look up a suitable
NIC when a socket is created."""

def route() -> Any:
    """Returns a list of all configured NICs."""
    ...

