"""Wrapper for the espcamera library

This library enables access to any camera sensor supported by the library,
including OV5640 and OV2640.

.. seealso::

    Non-Espressif microcontrollers use the `imagecapture` module together with wrapper libraries such as `adafruit_ov5640 <https://circuitpython.readthedocs.io/projects/ov5640/en/latest/>`_.

"""

from __future__ import annotations

from typing import List, Optional

import busio
import displayio
import microcontroller
from circuitpython_typing import ReadableBuffer

class GrabMode:
    """Controls when a new frame is grabbed."""

    WHEN_EMPTY: GrabMode
    """Fills buffers when they are empty. Less resources but first ``fb_count`` frames might be old"""

    LATEST: GrabMode
    """Except when 1 frame buffer is used, queue will always contain the last ``fb_count`` frames"""

class PixelFormat:
    """Format of data in the captured frames"""

    RGB565: PixelFormat
    """A 16-bit format with 5 bits of Red and Blue and 6 bits of Green"""

    GRAYSCALE: PixelFormat
    """An 8-bit format with 8-bits of luminance"""

    JPEG: PixelFormat
    """A compressed format"""

class FrameSize:
    """The pixel size of the captured frames"""

    R96X96: FrameSize
    """96x96"""

    QQVGA: FrameSize
    """160x120"""

    QCIF: FrameSize
    """176x144"""

    HQVGA: FrameSize
    """240x176"""

    R240X240: FrameSize
    """240x240"""

    QVGA: FrameSize
    """320x240 """

    CIF: FrameSize
    """400x296"""

    HVGA: FrameSize
    """480x320"""

    VGA: FrameSize
    """640x480"""

    SVGA: FrameSize
    """800x600"""

    XGA: FrameSize
    """1024x768"""

    HD: FrameSize
    """1280x720"""

    SXGA: FrameSize
    """1280x1024"""

    UXGA: FrameSize
    """1600x1200"""

    FHD: FrameSize
    """1920x1080"""

    P_HD: FrameSize
    """ 720x1280"""

    P_3MP: FrameSize
    """ 864x1536"""

    QXGA: FrameSize
    """2048x1536"""

    QHD: FrameSize
    """2560x1440"""

    WQXGA: FrameSize
    """2560x1600"""

    P_FHD: FrameSize
    """1080x1920"""

    QSXGA: FrameSize
    """2560x1920"""

class GainCeiling:
    """The maximum amount of gain applied to raw sensor data.

    Higher values are useful in darker conditions, but increase image noise."""

    GAIN_2X: GainCeiling
    GAIN_4X: GainCeiling
    GAIN_8X: GainCeiling
    GAIN_16X: GainCeiling
    GAIN_32X: GainCeiling
    GAIN_64X: GainCeiling
    GAIN_128X: GainCeiling

class Camera:
    def __init__(
        self,
        *,
        data_pins: List[microcontroller.Pin],
        pixel_clock_pin: microcontroller.Pin,
        vsync_pin: microcontroller.Pin,
        href_pin: microcontroller.Pin,
        i2c: busio.I2C,
        external_clock_pin: Optional[microcontroller.Pin] = None,
        external_clock_frequency: int = 20_000_000,
        powerdown_pin: Optional[microcontroller.Pin] = None,
        reset_pin: Optional[microcontroller.Pin] = None,
        pixel_format: PixelFormat = PixelFormat.RGB565,
        frame_size: FrameSize = FrameSize.QQVGA,
        jpeg_quality: int = 15,
        framebuffer_count: int = 1,
        grab_mode: GrabMode = GrabMode.WHEN_EMPTY,
    ) -> None:
        """
        Configure and initialize a camera with the given properties

        .. important::

            Not all supported sensors have all
            of the properties listed below. For instance, the
            OV5640 supports `denoise`, but the
            OV2640 does not. The underlying esp32-camera
            library does not provide a reliable API to check
            which settings are supported. CircuitPython makes
            a best effort to determine when an unsupported
            property is set and will raise an exception in
            that case.

        :param data_pins: The 8 data data_pins used for image data transfer from the camera module, least significant bit first
        :param pixel_clock_pin: The pixel clock output from the camera module
        :param vsync_pin: The vertical sync pulse output from the camera module
        :param href_pin: The horizontal reference output from the camera module
        :param i2c: The I2C bus connected to the camera module
        :param external_clock_pin: The pin on which to generate the external clock
        :param external_clock_frequency: The frequency generated on the external clock pin
        :param powerdown_pin: The powerdown input to the camera module
        :param reset_pin: The reset input to the camera module
        :param pixel_format: The pixel format of the captured image
        :param frame_size: The size of captured image
        :param jpeg_quality: For `PixelFormat.JPEG`, the quality. Higher numbers increase quality. If the quality is too high, the JPEG data will be larger than the available buffer size and the image will be unusable or truncated. The exact range of appropriate values depends on the sensor and must be determined empirically.
        :param framebuffer_count: The number of framebuffers (1 for single-buffered and 2 for double-buffered)
        :param grab_mode: When to grab a new frame
        """

    def deinit(self) -> None:
        """Deinitialises the camera and releases all memory resources for reuse."""
        ...

    def __enter__(self) -> Camera:
        """No-op used by Context Managers."""
        ...

    def __exit__(self) -> None:
        """Automatically deinitializes the hardware when exiting a context. See
        :ref:`lifetime-and-contextmanagers` for more info."""
        ...
    frame_available: bool
    """True if a frame is available, False otherwise"""
    def take(
        self, timeout: Optional[float] = 0.25
    ) -> Optional[displayio.Bitmap | ReadableBuffer]:
        """Record a frame. Wait up to 'timeout' seconds for a frame to be captured.

        In the case of timeout, `None` is returned.
        If `pixel_format` is `PixelFormat.JPEG`, the returned value is a read-only `memoryview`.
        Otherwise, the returned value is a read-only `displayio.Bitmap`.
        """

    def reconfigure(
        self,
        frame_size: Optional[FrameSize] = None,
        pixel_format: Optional[PixelFormat] = None,
        grab_mode: Optional[GrabMode] = None,
        framebuffer_count: Optional[int] = None,
    ) -> None:
        """Change multiple related camera settings simultaneously

        Because these settings interact in complex ways, and take longer than
        the other properties to set, they are set together in a single function call.

        If an argument is unspecified or None, then the setting is unchanged."""
    pixel_format: PixelFormat
    """The pixel format of captured frames"""
    frame_size: FrameSize
    """The size of captured frames"""
    contrast: int
    """The sensor contrast.  Positive values increase contrast, negative values lower it. The total range is device-specific but is often from -2 to +2 inclusive."""
    brightness: int
    """The sensor brightness.  Positive values increase brightness, negative values lower it. The total range is device-specific but is often from -2 to +2 inclusive."""
    saturation: int
    """The sensor saturation.  Positive values increase saturation (more vibrant colors), negative values lower it (more muted colors).  The total range is device-specific but the value is often from -2 to +2 inclusive."""
    sharpness: int
    """The sensor sharpness.  Positive values increase sharpness (more defined edges), negative values lower it (softer edges).  The total range is device-specific but the value is often from -2 to +2 inclusive."""
    denoise: int
    """The sensor 'denoise' setting.  Any camera sensor has inherent 'noise', especially in low brightness environments. Software algorithms can decrease noise at the expense of fine detail.  A larger value increases the amount of software noise removal.  The total range is device-specific but the value is often from 0 to 10."""
    gain_ceiling: GainCeiling
    """The sensor 'gain ceiling' setting. "Gain" is an analog multiplier applied to the raw sensor data.  The 'ceiling' is the maximum gain value that the sensor will use. A higher gain means that the sensor has a greater response to light, but also makes sensor noise more visible."""
    quality: int
    """The 'quality' setting when capturing JPEG images.  This is similar to the quality setting when exporting a jpeg image from photo editing software.  Typical values range from 5 to 40, with higher numbers leading to larger image sizes and better overall image quality. However, when the quality is set to a high number, the total size of the JPEG data can exceed the size of an internal buffer, causing image capture to fail."""
    colorbar: bool
    """When `True`, a test pattern image is captured and the real sensor data is not used."""
    whitebal: bool
    """When `True`, the camera attempts to automatically control white balance.  When `False`, the `wb_mode` setting is used instead."""
    gain_ctrl: bool
    """When `True`, the camera attempts to automatically control the sensor gain, up to the value in the `gain_ceiling` property.  When `False`, the `agc_gain` setting is used instead."""
    exposure_ctrl: bool
    """When `True` the camera attempts to automatically control the exposure. When `False`, the `aec_value` setting is used instead."""
    hmirror: bool
    """When `True` the camera image is mirrored left-to-right"""
    vflip: bool
    """When `True` the camera image is flipped top-to-bottom"""
    aec2: bool
    """When `True` the sensor's "night mode" is enabled, extending the range of automatic gain control."""
    awb_gain: bool
    """Access the awb_gain property of the camera sensor"""
    agc_gain: int
    """Access the gain level of the sensor. Higher values produce brighter images.  Typical settings range from 0 to 30. """
    aec_value: int
    """Access the exposure value of the camera.  Higher values produce brighter images.  Typical settings range from 0 to 1200."""
    special_effect: int
    """Enable a "special effect". Zero is no special effect.  On OV5640, special effects range from 0 to 6 inclusive and select various color modes."""
    wb_mode: int
    """The white balance mode.  0 is automatic white balance.  Typical values range from 0 to 4 inclusive."""
    ae_level: int
    """The exposure offset for automatic exposure.  Typical values range from -2 to +2."""
    dcw: bool
    """When `True` an advanced white balance mode is selected."""
    bpc: bool
    """When `True`, "black point compensation" is enabled. This can make black parts of the image darker."""
    wpc: bool
    """When `True`, "white point compensation" is enabled.  This can make white parts of the image whiter."""
    raw_gma: bool
    """When `True`, raw gamma mode is enabled."""
    lenc: bool
    """Enable "lens correction". This can help compensate for light fall-off at the edge of the sensor area."""
    max_frame_size: FrameSize
    """The maximum frame size that can be captured"""
    address: int
    """The I2C (SCCB) address of the sensor"""
    sensor_name: str
    """The name of the sensor"""
    supports_jpeg: bool
    """True if the sensor can capture images in JPEG format"""
    height: int
    """The height of the image being captured"""
    width: int
    """The width of the image being captured"""
    grab_mode: GrabMode
    """The grab mode of the camera"""
    framebuffer_count: int
    """True if double buffering is used"""
