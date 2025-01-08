"""
network configuration.

Descriptions taken from:
https://raw.githubusercontent.com/micropython/micropython/master/docs/library/network.rst.
****************************************

.. module:: network
   :synopsis: network configuration

This module provides network drivers and routing configuration. To use this
module, a MicroPython variant/build with network capabilities must be installed.
Network drivers for specific hardware are available within this module and are
used to configure hardware network interface(s). Network services provided
by configured interfaces are then available for use via the :mod:`socket`
module.

For example::

    # connect/ show IP config a specific network interface
    # see below for examples of specific drivers
    import network
    import time
    nic = network.Driver(...)
    if not nic.isconnected():
        nic.connect()
        print("Waiting for connection...")
        while not nic.isconnected():
            time.sleep(1)
    print(nic.ifconfig())

    # now use socket as usual
    import socket
    addr = socket.getaddrinfo('micropython.org', 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(b'GET / HTTP/1.1\r\nHost: micropython.org\r\n\r\n')
    data = s.recv(1000)
    s.close()
"""

__author__ = "Howard C Lovatt"
__copyright__ = "Howard C Lovatt, 2020 onwards."
__license__ = "MIT https://opensource.org/licenses/MIT (as used by MicroPython)."
__version__ = "7.3.9"  # Version set by https://github.com/hlovatt/tag2ver

from abc import abstractmethod
from typing import Protocol, Callable, overload, Any, ClassVar, Final

import pyb

MODE_11B: Final[int] = ...
"""IEEE 802.11b"""

MODE_11G: Final[int] = ...
"""IEEE 802.11g"""

MODE_11N: Final[int] = ...
"""IEEE 802.11n"""
@overload
def phy_mode(self) -> int:
    """
    Get or set the PHY mode.
    
    If the *mode* parameter is provided, sets the mode to its value. If
    the function is called without parameters, returns the current mode.
    
    The possible modes are defined as constants:
        * ``MODE_11B`` -- IEEE 802.11b,
        * ``MODE_11G`` -- IEEE 802.11g,
        * ``MODE_11N`` -- IEEE 802.11n.
    
    Availability: ESP8266.
   """

@overload
def phy_mode(self, mode: int, /) -> None:
    """
    Get or set the PHY mode.
    
    If the *mode* parameter is provided, sets the mode to its value. If
    the function is called without parameters, returns the current mode.
    
    The possible modes are defined as constants:
        * ``MODE_11B`` -- IEEE 802.11b,
        * ``MODE_11G`` -- IEEE 802.11g,
        * ``MODE_11N`` -- IEEE 802.11n.
    
    Availability: ESP8266.
   """

class AbstractNIC(Protocol):
    """
   Common network adapter interface
   ================================
   
   This section describes an (implied) abstract base class for all network
   interface classes implemented by :term:`MicroPython ports <MicroPython port>`
   for different hardware. This means that MicroPython does not actually
   provide ``AbstractNIC`` class, but any actual NIC class, as described
   in the following sections, implements methods as described here.
   """

    @abstractmethod
    def __init__(self, id: Any = None, /, *args: Any, **kwargs: Any):
        """
      Instantiate a network interface object. Parameters are network interface
      dependent. If there are more than one interface of the same type, the first
      parameter should be `id`.
      """
    @overload
    @abstractmethod
    def active(self, /) -> bool:
        """
           Activate ("up") or deactivate ("down") the network interface, if
           a boolean argument is passed. Otherwise, query current state if
           no argument is provided. Most other methods require an active
           interface (behaviour of calling them on inactive interface is
           undefined).
      """
    @overload
    @abstractmethod
    def active(self, is_active: bool, /) -> None:
        """
           Activate ("up") or deactivate ("down") the network interface, if
           a boolean argument is passed. Otherwise, query current state if
           no argument is provided. Most other methods require an active
           interface (behaviour of calling them on inactive interface is
           undefined).
      """
    @overload
    @abstractmethod
    def connect(self, key: str | None = None, /, **kwargs: Any) -> None:
        """
          Connect the interface to a network. This method is optional, and
          available only for interfaces which are not "always connected".
          If no parameters are given, connect to the default (or the only)
          service. If a single parameter is given, it is the primary identifier
          of a service to connect to. It may be accompanied by a key
          (password) required to access said service. There can be further
          arbitrary keyword-only parameters, depending on the networking medium
          type and/or particular device. Parameters can be used to: a)
          specify alternative service identifier types; b) provide additional
          connection parameters. For various medium types, there are different
          sets of predefined/recommended parameters, among them:
          
          * WiFi: *bssid* keyword to connect to a specific BSSID (MAC address)
      """
    @overload
    @abstractmethod
    def connect(
        self, service_id: Any, key: str | None = None, /, **kwargs: Any
    ) -> None:
        """
          Connect the interface to a network. This method is optional, and
          available only for interfaces which are not "always connected".
          If no parameters are given, connect to the default (or the only)
          service. If a single parameter is given, it is the primary identifier
          of a service to connect to. It may be accompanied by a key
          (password) required to access said service. There can be further
          arbitrary keyword-only parameters, depending on the networking medium
          type and/or particular device. Parameters can be used to: a)
          specify alternative service identifier types; b) provide additional
          connection parameters. For various medium types, there are different
          sets of predefined/recommended parameters, among them:
          
          * WiFi: *bssid* keyword to connect to a specific BSSID (MAC address)
      """
    @abstractmethod
    def disconnect(self) -> None:
        """
          Disconnect from network.
      """
    @abstractmethod
    def isconnected(self) -> bool:
        """
          Returns ``True`` if connected to network, otherwise returns ``False``.
      """
    @abstractmethod
    def scan(self, **kwargs: Any) -> list[tuple[str, ...]]:
        """
          Scan for the available network services/connections. Returns a
          list of tuples with discovered service parameters. For various
          network media, there are different variants of predefined/
          recommended tuple formats, among them:
          
          * WiFi: (ssid, bssid, channel, RSSI, authmode, hidden). There
            may be further fields, specific to a particular device.
          
          The function may accept additional keyword arguments to filter scan
          results (e.g. scan for a particular service, on a particular channel,
          for services of a particular set, etc.), and to affect scan
          duration and other parameters. Where possible, parameter names
          should match those in connect().
      """
    @overload
    @abstractmethod
    def status(self) -> Any:
        """
          Query dynamic status information of the interface.  When called with no
          argument the return value describes the network link status.  Otherwise
          *param* should be a string naming the particular status parameter to
          retrieve.
          
          The return types and values are dependent on the network
          medium/technology.  Some of the parameters that may be supported are:
          
          * WiFi STA: use ``'rssi'`` to retrieve the RSSI of the AP signal
          * WiFi AP: use ``'stations'`` to retrieve a list of all the STAs
            connected to the AP.  The list contains tuples of the form
            (MAC, RSSI).
      """
    @overload
    @abstractmethod
    def status(self, param: str, /) -> Any:
        """
          Query dynamic status information of the interface.  When called with no
          argument the return value describes the network link status.  Otherwise
          *param* should be a string naming the particular status parameter to
          retrieve.
          
          The return types and values are dependent on the network
          medium/technology.  Some of the parameters that may be supported are:
          
          * WiFi STA: use ``'rssi'`` to retrieve the RSSI of the AP signal
          * WiFi AP: use ``'stations'`` to retrieve a list of all the STAs
            connected to the AP.  The list contains tuples of the form
            (MAC, RSSI).
      """
    @overload
    @abstractmethod
    def ifconfig(self) -> tuple[str, str, str, str]:
        """
          Get/set IP-level network interface parameters: IP address, subnet mask,
          gateway and DNS server. When called with no arguments, this method returns
          a 4-tuple with the above information. To set the above values, pass a
          4-tuple with the required information.  For example::
          
           nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
      """
    @overload
    @abstractmethod
    def ifconfig(self, ip_mask_gateway_dns: tuple[str, str, str, str], /) -> None:
        """
          Get/set IP-level network interface parameters: IP address, subnet mask,
          gateway and DNS server. When called with no arguments, this method returns
          a 4-tuple with the above information. To set the above values, pass a
          4-tuple with the required information.  For example::
          
           nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
      """
    @overload
    @abstractmethod
    def config(self, param: str, /) -> Any:
        """
          Get or set general network interface parameters. These methods allow to work
          with additional parameters beyond standard IP configuration (as dealt with by
          `ifconfig()`). These include network-specific and hardware-specific
          parameters. For setting parameters, the keyword argument
          syntax should be used, and multiple parameters can be set at once. For
          querying, a parameter name should be quoted as a string, and only one
          parameter can be queried at a time::
          
           # Set WiFi access point name (formally known as ESSID) and WiFi channel
           ap.config(essid='My AP', channel=11)
           # Query params one by one
           print(ap.config('essid'))
           print(ap.config('channel'))
      """
    @overload
    @abstractmethod
    def config(self, **kwargs: Any) -> None:
        """
          Get or set general network interface parameters. These methods allow to work
          with additional parameters beyond standard IP configuration (as dealt with by
          `ifconfig()`). These include network-specific and hardware-specific
          parameters. For setting parameters, the keyword argument
          syntax should be used, and multiple parameters can be set at once. For
          querying, a parameter name should be quoted as a string, and only one
          parameter can be queried at a time::
          
           # Set WiFi access point name (formally known as ESSID) and WiFi channel
           ap.config(essid='My AP', channel=11)
           # Query params one by one
           print(ap.config('essid'))
           print(ap.config('channel'))
      """

class WLAN:
    """
   This class provides a driver for WiFi network processors.  Example usage::
   
       import network
       # enable station interface and connect to WiFi access point
       nic = network.WLAN(network.STA_IF)
       nic.active(True)
       nic.connect('your-ssid', 'your-password')
       # now use sockets as usual
   """

    def __init__(self, interface_id: int, /):
        """
      Create a WLAN network interface object. Supported interfaces are
      ``network.STA_IF`` (station aka client, connects to upstream WiFi access
      points) and ``network.AP_IF`` (access point, allows other WiFi clients to
      connect). Availability of the methods below depends on interface type.
      For example, only STA interface may `WLAN.connect()` to an access point.
      """
    @overload
    def active(self, /) -> bool:
        """
       Activate ("up") or deactivate ("down") network interface, if boolean
       argument is passed. Otherwise, query current state if no argument is
       provided. Most other methods require active interface.
      """
    @overload
    def active(self, is_active: bool, /) -> None:
        """
       Activate ("up") or deactivate ("down") network interface, if boolean
       argument is passed. Otherwise, query current state if no argument is
       provided. Most other methods require active interface.
      """
    def connect(
        self,
        ssid: str | None = None,
        password: str | None = None,
        /,
        *,
        bssid: bytes | None = None,
    ) -> None:
        """
       Connect to the specified wireless network, using the specified password.
       If *bssid* is given then the connection will be restricted to the
       access-point with that MAC address (the *ssid* must also be specified
       in this case).
      """
    def disconnect(self) -> None:
        """
       Disconnect from the currently connected wireless network.
      """
    def scan(self) -> tuple[str, bytes, int, int, int]:
        """
       Scan for the available wireless networks.
       Hidden networks -- where the SSID is not broadcast -- will also be scanned
       if the WLAN interface allows it.
       
       Scanning is only possible on STA interface. Returns list of tuples with
       the information about WiFi access points:
       
           (ssid, bssid, channel, RSSI, authmode, hidden)
       
       *bssid* is hardware address of an access point, in binary form, returned as
       bytes object. You can use `binascii.hexlify()` to convert it to ASCII form.
       
       There are five values for authmode:
       
           * 0 -- open
           * 1 -- WEP
           * 2 -- WPA-PSK
           * 3 -- WPA2-PSK
           * 4 -- WPA/WPA2-PSK
       
       and two for hidden:
       
           * 0 -- visible
           * 1 -- hidden
      """
    @overload
    def status(self) -> int:
        """
       Return the current status of the wireless connection.
       
       When called with no argument the return value describes the network link status.
       The possible statuses are defined as constants:
       
           * ``STAT_IDLE`` -- no connection and no activity,
           * ``STAT_CONNECTING`` -- connecting in progress,
           * ``STAT_WRONG_PASSWORD`` -- failed due to incorrect password,
           * ``STAT_NO_AP_FOUND`` -- failed because no access point replied,
           * ``STAT_CONNECT_FAIL`` -- failed due to other problems,
           * ``STAT_GOT_IP`` -- connection successful.
       
       When called with one argument *param* should be a string naming the status
       parameter to retrieve.  Supported parameters in WiFI STA mode are: ``'rssi'``.
      """
    @overload
    def status(self, param: str, /) -> int:
        """
       Return the current status of the wireless connection.
       
       When called with no argument the return value describes the network link status.
       The possible statuses are defined as constants:
       
           * ``STAT_IDLE`` -- no connection and no activity,
           * ``STAT_CONNECTING`` -- connecting in progress,
           * ``STAT_WRONG_PASSWORD`` -- failed due to incorrect password,
           * ``STAT_NO_AP_FOUND`` -- failed because no access point replied,
           * ``STAT_CONNECT_FAIL`` -- failed due to other problems,
           * ``STAT_GOT_IP`` -- connection successful.
       
       When called with one argument *param* should be a string naming the status
       parameter to retrieve.  Supported parameters in WiFI STA mode are: ``'rssi'``.
      """
    def isconnected(self) -> bool:
        """
       In case of STA mode, returns ``True`` if connected to a WiFi access
       point and has a valid IP address.  In AP mode returns ``True`` when a
       station is connected. Returns ``False`` otherwise.
      """
    @overload
    def ifconfig(self) -> tuple[str, str, str, str]:
        """
      Get/set IP-level network interface parameters: IP address, subnet mask,
      gateway and DNS server. When called with no arguments, this method returns
      a 4-tuple with the above information. To set the above values, pass a
      4-tuple with the required information.  For example::
      
       nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
      """
    @overload
    def ifconfig(self, ip_mask_gateway_dns: tuple[str, str, str, str], /) -> None:
        """
      Get/set IP-level network interface parameters: IP address, subnet mask,
      gateway and DNS server. When called with no arguments, this method returns
      a 4-tuple with the above information. To set the above values, pass a
      4-tuple with the required information.  For example::
      
       nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
      """
    @overload
    def config(self, param: str, /) -> Any:
        """
      Get or set general network interface parameters. These methods allow to work
      with additional parameters beyond standard IP configuration (as dealt with by
      `WLAN.ifconfig()`). These include network-specific and hardware-specific
      parameters. For setting parameters, keyword argument syntax should be used,
      multiple parameters can be set at once. For querying, parameters name should
      be quoted as a string, and only one parameter can be queries at time::
      
       # Set WiFi access point name (formally known as ESSID) and WiFi channel
       ap.config(essid='My AP', channel=11)
       # Query params one by one
       print(ap.config('essid'))
       print(ap.config('channel'))
      
      Following are commonly supported parameters (availability of a specific parameter
      depends on network technology type, driver, and :term:`MicroPython port`).
      
      =============  ===========
      Parameter      Description
      =============  ===========
      mac            MAC address (bytes)
      essid          WiFi access point name (string)
      channel        WiFi channel (integer)
      hidden         Whether ESSID is hidden (boolean)
      authmode       Authentication mode supported (enumeration, see module constants)
      password       Access password (string)
      dhcp_hostname  The DHCP hostname to use
      reconnects     Number of reconnect attempts to make (integer, 0=none, -1=unlimited)
      =============  ===========
      """
    @overload
    def config(self, **kwargs: Any) -> None:
        """
      Get or set general network interface parameters. These methods allow to work
      with additional parameters beyond standard IP configuration (as dealt with by
      `WLAN.ifconfig()`). These include network-specific and hardware-specific
      parameters. For setting parameters, keyword argument syntax should be used,
      multiple parameters can be set at once. For querying, parameters name should
      be quoted as a string, and only one parameter can be queries at time::
      
       # Set WiFi access point name (formally known as ESSID) and WiFi channel
       ap.config(essid='My AP', channel=11)
       # Query params one by one
       print(ap.config('essid'))
       print(ap.config('channel'))
      
      Following are commonly supported parameters (availability of a specific parameter
      depends on network technology type, driver, and :term:`MicroPython port`).
      
      =============  ===========
      Parameter      Description
      =============  ===========
      mac            MAC address (bytes)
      essid          WiFi access point name (string)
      channel        WiFi channel (integer)
      hidden         Whether ESSID is hidden (boolean)
      authmode       Authentication mode supported (enumeration, see module constants)
      password       Access password (string)
      dhcp_hostname  The DHCP hostname to use
      reconnects     Number of reconnect attempts to make (integer, 0=none, -1=unlimited)
      =============  ===========
      """

class WLANWiPy:
    """
   .. note::
   
       This class is a non-standard WLAN implementation for the WiPy.
       It is available simply as ``network.WLAN`` on the WiPy but is named in the
       documentation below as ``network.WLANWiPy`` to distinguish it from the
       more general :ref:`network.WLAN <network.WLAN>` class.
   
   This class provides a driver for the WiFi network processor in the WiPy. Example usage::
   
       import network
       import time
       # setup as a station
       wlan = network.WLAN(mode=WLAN.STA)
       wlan.connect('your-ssid', auth=(WLAN.WPA2, 'your-key'))
       while not wlan.isconnected():
           time.sleep_ms(50)
       print(wlan.ifconfig())
   
       # now use socket as usual
       ...
   """

    STA: ClassVar[int] = ...
    """
selects the WLAN mode
   """

    AP: ClassVar[int] = ...
    """
selects the WLAN mode
   """

    WEP: ClassVar[int] = ...
    """
selects the network security
   """

    WPA: ClassVar[int] = ...
    """
selects the network security
   """

    WPA2: ClassVar[int] = ...
    """
selects the network security
   """

    INT_ANT: ClassVar[int] = ...
    """
selects the antenna type
   """

    EXT_ANT: ClassVar[int] = ...
    """
selects the antenna type
   """
    @overload
    def __init__(self, id: int = 0, /):
        """
      Create a WLAN object, and optionally configure it. See `init()` for params of configuration.
      
      .. note::
      
      The ``WLAN`` constructor is special in the sense that if no arguments besides the id are given,
      it will return the already existing ``WLAN`` instance without re-configuring it. This is
      because ``WLAN`` is a system feature of the WiPy. If the already existing instance is not
      initialized it will do the same as the other constructors an will initialize it with default
      values.
      """
    @overload
    def __init__(
        self,
        id: int,
        /,
        *,
        mode: int,
        ssid: str,
        auth: tuple[str, str],
        channel: int,
        antenna: int,
    ):
        """
      Create a WLAN object, and optionally configure it. See `init()` for params of configuration.
      
      .. note::
      
      The ``WLAN`` constructor is special in the sense that if no arguments besides the id are given,
      it will return the already existing ``WLAN`` instance without re-configuring it. This is
      because ``WLAN`` is a system feature of the WiPy. If the already existing instance is not
      initialized it will do the same as the other constructors an will initialize it with default
      values.
      """
    def init(
        self,
        mode: int,
        /,
        *,
        ssid: str,
        auth: tuple[str, str],
        channel: int,
        antenna: int,
    ) -> bool:
        """
      Set or get the WiFi network processor configuration.
      
      Arguments are:
      
        - *mode* can be either ``WLAN.STA`` or ``WLAN.AP``.
        - *ssid* is a string with the ssid name. Only needed when mode is ``WLAN.AP``.
        - *auth* is a tuple with (sec, key). Security can be ``None``, ``WLAN.WEP``,
          ``WLAN.WPA`` or ``WLAN.WPA2``. The key is a string with the network password.
          If ``sec`` is ``WLAN.WEP`` the key must be a string representing hexadecimal
          values (e.g. 'ABC1DE45BF'). Only needed when mode is ``WLAN.AP``.
        - *channel* a number in the range 1-11. Only needed when mode is ``WLAN.AP``.
        - *antenna* selects between the internal and the external antenna. Can be either
          ``WLAN.INT_ANT`` or ``WLAN.EXT_ANT``.
      
      For example, you can do::
      
         # create and configure as an access point
         wlan.init(mode=WLAN.AP, ssid='wipy-wlan', auth=(WLAN.WPA2,'www.wipy.io'), channel=7, antenna=WLAN.INT_ANT)
      
      or::
      
         # configure as an station
         wlan.init(mode=WLAN.STA)
      """
    def connect(
        self,
        ssid: str,
        /,
        *,
        auth: tuple[str, str] | None = None,
        bssid: bytes | None = None,
        timeout: int | None = None,
    ) -> None:
        """
      Connect to a WiFi access point using the given SSID, and other security
      parameters.
      
         - *auth* is a tuple with (sec, key). Security can be ``None``, ``WLAN.WEP``,
           ``WLAN.WPA`` or ``WLAN.WPA2``. The key is a string with the network password.
           If ``sec`` is ``WLAN.WEP`` the key must be a string representing hexadecimal
           values (e.g. 'ABC1DE45BF').
         - *bssid* is the MAC address of the AP to connect to. Useful when there are several
           APs with the same ssid.
         - *timeout* is the maximum time in milliseconds to wait for the connection to succeed.
      """
    def scan(self) -> tuple[str, bytes, int, int | None, int]:
        """
      Performs a network scan and returns a list of named tuples with (ssid, bssid, sec, channel, rssi).
      Note that channel is always ``None`` since this info is not provided by the WiPy.
      """
    def disconnect(self) -> None:
        """
      Disconnect from the WiFi access point.
      """
    def isconnected(self) -> bool:
        """
      In case of STA mode, returns ``True`` if connected to a WiFi access point and has a valid IP address.
      In AP mode returns ``True`` when a station is connected, ``False`` otherwise.
      """
    @overload
    def ifconfig(self, if_id: int = 0, /) -> tuple[str, str, str, str]:
        """
      With no parameters given returns a 4-tuple of *(ip, subnet_mask, gateway, DNS_server)*.
      
      if ``'dhcp'`` is passed as a parameter then the DHCP client is enabled and the IP params
      are negotiated with the AP.
      
      If the 4-tuple config is given then a static IP is configured. For instance::
      
         wlan.ifconfig(config=('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
      """
    @overload
    def ifconfig(
        self, if_id: int = 0, /, *, config: str | tuple[str, str, str, str]
    ) -> None:
        """
      With no parameters given returns a 4-tuple of *(ip, subnet_mask, gateway, DNS_server)*.
      
      if ``'dhcp'`` is passed as a parameter then the DHCP client is enabled and the IP params
      are negotiated with the AP.
      
      If the 4-tuple config is given then a static IP is configured. For instance::
      
         wlan.ifconfig(config=('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
      """
    @overload
    def mode(self) -> int:
        """
      Get or set the WLAN mode.
      """
    @overload
    def mode(self, mode: int, /) -> None:
        """
      Get or set the WLAN mode.
      """
    @overload
    def ssid(self) -> str:
        """
      Get or set the SSID when in AP mode.
      """
    @overload
    def ssid(self, ssid: str, /) -> None:
        """
      Get or set the SSID when in AP mode.
      """
    @overload
    def auth(self) -> int:
        """
      Get or set the authentication type when in AP mode.
      """
    @overload
    def auth(self, auth: int, /) -> None:
        """
      Get or set the authentication type when in AP mode.
      """
    @overload
    def channel(self) -> int:
        """
      Get or set the channel (only applicable in AP mode).
      """
    @overload
    def channel(self, channel: int, /) -> None:
        """
      Get or set the channel (only applicable in AP mode).
      """
    @overload
    def antenna(self) -> int:
        """
      Get or set the antenna type (external or internal).
      """
    @overload
    def antenna(self, antenna: int, /) -> None:
        """
      Get or set the antenna type (external or internal).
      """
    @overload
    def mac(self) -> bytes:
        """
      Get or set a 6-byte long bytes object with the MAC address.
      """
    @overload
    def mac(self, mac: bytes, /) -> None:
        """
      Get or set a 6-byte long bytes object with the MAC address.
      """
    def irq(self, *, handler: Callable[[], None], wake: int) -> Any:
        """
       Create a callback to be triggered when a WLAN event occurs during ``machine.SLEEP``
       mode. Events are triggered by socket activity or by WLAN connection/disconnection.
       
           - *handler* is the function that gets called when the IRQ is triggered.
           - *wake* must be ``machine.SLEEP``.
       
       Returns an IRQ object.
      """

class CC3K:
    """
   This class provides a driver for CC3000 WiFi modules.  Example usage::
   
       import network
       nic = network.CC3K(pyb.SPI(2), pyb.Pin.board.Y5, pyb.Pin.board.Y4, pyb.Pin.board.Y3)
       nic.connect('your-ssid', 'your-password')
       while not nic.isconnected():
           pyb.delay(50)
       print(nic.ifconfig())
   
       # now use socket as usual
       ...
   
   For this example to work the CC3000 module must have the following connections:
   
       - MOSI connected to Y8
       - MISO connected to Y7
       - CLK connected to Y6
       - CS connected to Y5
       - VBEN connected to Y4
       - IRQ connected to Y3
   
   It is possible to use other SPI buses and other pins for CS, VBEN and IRQ.
   """

    WEP: ClassVar[int] = ...
    """
security type to use
   """

    WPA: ClassVar[int] = ...
    """
security type to use
   """

    WPA2: ClassVar[int] = ...
    """
security type to use
   """
    def __init__(
        self, spi: pyb.SPI, pin_cs: pyb.Pin, pin_en: pyb.Pin, pin_irq: pyb.Pin, /
    ):
        """
      Create a CC3K driver object, initialise the CC3000 module using the given SPI bus
      and pins, and return the CC3K object.
      
      Arguments are:
      
        - *spi* is an :ref:`SPI object <pyb.SPI>` which is the SPI bus that the CC3000 is
          connected to (the MOSI, MISO and CLK pins).
        - *pin_cs* is a :ref:`Pin object <pyb.Pin>` which is connected to the CC3000 CS pin.
        - *pin_en* is a :ref:`Pin object <pyb.Pin>` which is connected to the CC3000 VBEN pin.
        - *pin_irq* is a :ref:`Pin object <pyb.Pin>` which is connected to the CC3000 IRQ pin.
      
      All of these objects will be initialised by the driver, so there is no need to
      initialise them yourself.  For example, you can use::
      
        nic = network.CC3K(pyb.SPI(2), pyb.Pin.board.Y5, pyb.Pin.board.Y4, pyb.Pin.board.Y3)
      """
    def connect(
        self,
        ssid: str,
        key: str | None = None,
        /,
        *,
        security: int = WPA2,
        bssid: bytes | None = None,
    ) -> None:
        """
      Connect to a WiFi access point using the given SSID, and other security
      parameters.
      """
    def disconnect(self) -> None:
        """
      Disconnect from the WiFi access point.
      """
    def isconnected(self) -> bool:
        """
      Returns True if connected to a WiFi access point and has a valid IP address,
      False otherwise.
      """
    def ifconfig(self) -> tuple[str, str, str, str, str, str, str]:
        """
      Returns a 7-tuple with (ip, subnet mask, gateway, DNS server, DHCP server,
      MAC address, SSID).
      """
    def patch_version(self) -> str:
        """
      Return the version of the patch program (firmware) on the CC3000.
      """
    def patch_program(self, cmd: str, /) -> None:
        """
      Upload the current firmware to the CC3000.  You must pass 'pgm' as the first
      argument in order for the upload to proceed.
      """

class WIZNET5K:
    """
   This class allows you to control WIZnet5x00 Ethernet adaptors based on
   the W5200 and W5500 chipsets.  The particular chipset that is supported
   by the firmware is selected at compile-time via the MICROPY_PY_WIZNET5K
   option.
   
   Example usage::
   
       import network
       nic = network.WIZNET5K(pyb.SPI(1), pyb.Pin.board.X5, pyb.Pin.board.X4)
       print(nic.ifconfig())
   
       # now use socket as usual
       ...
   
   For this example to work the WIZnet5x00 module must have the following connections:
   
       - MOSI connected to X8
       - MISO connected to X7
       - SCLK connected to X6
       - nSS connected to X5
       - nRESET connected to X4
   
   It is possible to use other SPI buses and other pins for nSS and nRESET.
   """

    def __init__(self, spi: pyb.SPI, pin_cs: pyb.Pin, pin_rst: pyb.Pin, /):
        """
      Create a WIZNET5K driver object, initialise the WIZnet5x00 module using the given
      SPI bus and pins, and return the WIZNET5K object.
      
      Arguments are:
      
        - *spi* is an :ref:`SPI object <pyb.SPI>` which is the SPI bus that the WIZnet5x00 is
          connected to (the MOSI, MISO and SCLK pins).
        - *pin_cs* is a :ref:`Pin object <pyb.Pin>` which is connected to the WIZnet5x00 nSS pin.
        - *pin_rst* is a :ref:`Pin object <pyb.Pin>` which is connected to the WIZnet5x00 nRESET pin.
      
      All of these objects will be initialised by the driver, so there is no need to
      initialise them yourself.  For example, you can use::
      
        nic = network.WIZNET5K(pyb.SPI(1), pyb.Pin.board.X5, pyb.Pin.board.X4)
      """
    def isconnected(self) -> bool:
        """
      Returns ``True`` if the physical Ethernet link is connected and up.
      Returns ``False`` otherwise.
      """
    @overload
    def ifconfig(self) -> tuple[str, str, str, str]:
        """
      Get/set IP address, subnet mask, gateway and DNS.
      
      When called with no arguments, this method returns a 4-tuple with the above information.
      
      To set the above values, pass a 4-tuple with the required information.  For example::
      
       nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
      """
    @overload
    def ifconfig(self, config: tuple[str, str, str, str], /):
        """
      Get/set IP address, subnet mask, gateway and DNS.
      
      When called with no arguments, this method returns a 4-tuple with the above information.
      
      To set the above values, pass a 4-tuple with the required information.  For example::
      
       nic.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
      """
    def regs(self) -> Any:
        """
      Dump the WIZnet5x00 registers.  Useful for debugging.
      """
