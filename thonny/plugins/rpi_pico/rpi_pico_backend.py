import datetime
import logging
from textwrap import dedent, indent

from thonny.plugins.micropython.bare_metal_backend import BareMetalMicroPythonBackend

logger = logging.getLogger(__name__)


class RaspberryPiPicoBackend(BareMetalMicroPythonBackend):
    def _sync_time(self):
        """Sets the time to match the time on the host."""

        logger.info("Syncing time in Pico")

        # RTC works on UTC
        now = self._get_time_for_rtc()

        specific_script = dedent(
            """
            try:
                __th_dt_ts = {datetime_ts}
                from machine import RTC as __thonny_RTC
                try:
                    __thonny_RTC().datetime(__th_dt_ts)
                except:
                    __thonny_RTC().init({init_ts})
                del __thonny_RTC
            except ImportError:
                assert __thonny_helper.os.uname().sysname == 'rp2'
                from machine import mem32 as __th_mem32
                __th_mem32[0x4005c004] =  __th_dt_ts[0] << 12 | __th_dt_ts[1] << 8 | __th_dt_ts[2]
                __th_mem32[0x4005c008] = (__th_dt_ts[3] % 7) << 24 | __th_dt_ts[4] << 16 | __th_dt_ts[5] << 8 | __th_dt_ts[6]
                __th_mem32[0x4005c00c] |= 0x10
                del __th_mem32
            finally:
                del __th_dt_ts
                    
        """
        ).format(
            datetime_ts=(
                now.tm_year,
                now.tm_mon,
                now.tm_mday,
                now.tm_wday + 1,
                now.tm_hour,
                now.tm_min,
                now.tm_sec,
                0,
            ),
            init_ts=tuple(now)[:6] + (0, 0),
        )

        script = (
            dedent(
                """
            try:
            %s
                __thonny_helper.print_mgmt_value(True)
            except Exception as e:
                import sys
                sys.print_exception(e)
                __thonny_helper.print_mgmt_value(str(e))
        """
            )
            % indent(specific_script, "    ")
        )

        val = self._evaluate(script)
        if isinstance(val, str):
            print("WARNING: Could not sync device's clock: " + val)
