"""Global Navigation Satellite System

The `gnss` module contains classes to control the GNSS and acquire positioning information."""

from __future__ import annotations

import time
from typing import List, Union

class GNSS:
    """Get updated positioning information from Global Navigation Satellite System (GNSS)

    Usage::

        import gnss
        import time

        nav = gnss.GNSS([gnss.SatelliteSystem.GPS, gnss.SatelliteSystem.GLONASS])
        last_print = time.monotonic()
        while True:
            nav.update()
            current = time.monotonic()
            if current - last_print >= 1.0:
                last_print = current
                if nav.fix is gnss.PositionFix.INVALID:
                    print("Waiting for fix...")
                    continue
                print("Latitude: {0:.6f} degrees".format(nav.latitude))
                print("Longitude: {0:.6f} degrees".format(nav.longitude))"""

    def __init__(self, system: Union[SatelliteSystem, List[SatelliteSystem]]) -> None:
        """Turn on the GNSS.

        :param system: satellite system to use"""
        ...
    def deinit(self) -> None:
        """Turn off the GNSS."""
        ...
    def update(self) -> None:
        """Update GNSS positioning information."""
        ...
    latitude: float
    """Latitude of current position in degrees (float)."""

    longitude: float
    """Longitude of current position in degrees (float)."""

    altitude: float
    """Altitude of current position in meters (float)."""

    timestamp: time.struct_time
    """Time when the position data was updated."""

    fix: PositionFix
    """Fix mode."""

class PositionFix:
    """Position fix mode"""

    def __init__(self) -> None:
        """Enum-like class to define the position fix mode."""
    INVALID: PositionFix
    """No measurement."""

    FIX_2D: PositionFix
    """2D fix."""

    FIX_3D: PositionFix
    """3D fix."""

class SatelliteSystem:
    """Satellite system type"""

    def __init__(self) -> None:
        """Enum-like class to define the satellite system type."""
    GPS: SatelliteSystem
    """Global Positioning System."""

    GLONASS: SatelliteSystem
    """GLObal NAvigation Satellite System."""

    SBAS: SatelliteSystem
    """Satellite Based Augmentation System."""

    QZSS_L1CA: SatelliteSystem
    """Quasi-Zenith Satellite System L1C/A."""

    QZSS_L1S: SatelliteSystem
    """Quasi-Zenith Satellite System L1S."""
