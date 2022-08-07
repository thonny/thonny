import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Any, Dict
import urllib.request

from thonny import ui_utils
from thonny.languages import tr
from thonny.misc_utils import list_volumes
from thonny.ui_utils import MappingCombobox, AutoScrollbar, scrollbar_style, create_url_label
from thonny.workdlg import WorkDialog
from logging import getLogger

logger = getLogger(__name__)

FAKE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"

class BaseFlasher(WorkDialog):
    def __init__(self, master, autostart=False):
        self._variants: List[Dict[str, Any]] = []
        threading.Thread(target=self._download_variants, daemon=True).start()

        super().__init__(master, autostart)


    def populate_main_frame(self):
        epadx = self.get_large_padding()
        ipadx = self.get_small_padding()
        epady = epadx
        ipady = ipadx

        target_label = ttk.Label(self.main_frame, text="Target volume")
        target_label.grid(row=1, column=1, sticky="e", padx=(epadx, 0), pady=(epady, 0))
        self._target_combo = MappingCombobox(self.main_frame, exportselection=False)
        self._target_combo.grid(row=1, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(epady, 0))

        variant_label = ttk.Label(self.main_frame, text="MicroPython variant")
        variant_label.grid(row=2, column=1, sticky="e", padx=(epadx, 0), pady=(ipady, 0))
        self._variant_combo = MappingCombobox(self.main_frame, exportselection=False)
        self._variant_combo.grid(row=2, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(ipady, 0))

        info_label = ttk.Label(self.main_frame, text="info")
        info_label.grid(row=4, column=1, sticky="e", padx=(epadx, 0), pady=(ipady, 0))
        self._info_url_label = create_url_label(self.main_frame, "https://circuitpython.org/board/lilygo_ttgo_t8_s2/")
        self._info_url_label.grid(row=4, column=2, sticky="w", padx=(ipadx, epadx), pady=(ipady, 0))

        version_label = ttk.Label(self.main_frame, text="version")
        version_label.grid(row=3, column=1, sticky="e", padx=(epadx, 0), pady=(ipady, 0))
        self._version_combo = MappingCombobox(self.main_frame, exportselection=False)
        self._version_combo.grid(row=3, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(ipady, 0))

        """
        # Filter
        filter_label = ttk.Label(self.main_frame, text="Filter")
        filter_label.grid(row=2, column=1, sticky="w", padx=(epadx, 0), pady=(epady, 0))

        self._filter_entry = ttk.Entry(self.main_frame, width=50)
        self._filter_entry.grid(row=2, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(epady, 0))

        # Variants
        variant_label = ttk.Label(self.main_frame, text="Choose\nvariant")
        variant_label.grid(row=3, column=1, sticky="nw", padx=(epadx, 0), pady=(ipady, 0))

        listframe = ttk.Frame(self.main_frame, relief="flat", borderwidth=1)
        listframe.rowconfigure(0, weight=1)
        listframe.columnconfigure(0, weight=1)

        self.listbox = ui_utils.ThemedListbox(
            listframe,
            activestyle="dotbox",
            width=80,
            height=10,
            selectborderwidth=0,
            relief="flat",
            # highlightthickness=4,
            # highlightbackground="red",
            # highlightcolor="green",
            borderwidth=0,
        )
        self.listbox.bind("<<ListboxSelect>>", self._on_variant_select, True)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.listbox.insert("end", " BBC - micro:bit v2")
        self.listbox.insert("end", " BBC - micro:bit v2 (original simplified API)")
        list_scrollbar = AutoScrollbar(
            listframe, orient=tk.VERTICAL, style=scrollbar_style("Vertical")
        )
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        list_scrollbar["command"] = self.listbox.yview
        self.listbox["yscrollcommand"] = list_scrollbar.set

        listframe.grid(row=3, column=2, sticky="nsew", padx=(ipadx, epadx), pady=(ipady, 0))
        """

        self.main_frame.columnconfigure(2, weight=1)

    def _get_variants_url(self) -> str:
        return "https://raw.githubusercontent.com/thonny/thonny/master/data/micropython-variants.json"

    def _download_variants(self):
        import json
        from urllib.request import urlopen

        try:
            req = urllib.request.Request(
                self._get_variants_url(),
                data=None,
                headers={
                    "User-Agent": FAKE_USER_AGENT,
                    "Cache-Control": "no-cache",
                },
            )
            with urlopen(req) as fp:
                json_str = fp.read().decode("UTF-8")
                #logger.debug("Variants info: %r", json_str)
                self._variants = json.loads(json_str)
        except Exception as e:
            self.append_text("Could not download variants info from %s\n" % self._get_variants_url())
            self.set_action_text("Error!")
            self.grid_progress_widgets()

    def get_ok_text(self):
        return tr("Install")

    @classmethod
    def get_possible_targets(cls, board_id: Optional[str] = None):
        all_vol_infos = [
            (vol, cls.find_device_board_id_and_model(vol))
            for vol in list_volumes(skip_letters=["A"])
        ]

        return [
            (info[0], info[1][0], info[1][1])
            for info in all_vol_infos
            if info[1] is not None and (info[1][0] == board_id or board_id is None)
        ]



    def get_instructions(self) -> Optional[str]:
        return (
            "Here you can install or update MicroPython for devices having an UF2 bootloader\n"
            "(this includes most boards meant for beginners).\n"
            "\n"
            "1. Put your device into bootloader mode: \n"
            "     - some devices have to be plugged in while holding the BOOTSEL button,\n"
            "     - some require double-tapping the RESET button with proper rythm.\n"
            "2. Wait for couple of seconds until the target volume appears.\n"
            "3. Select desired variant and version.\n"
            "4. Click 'Install' and wait for some seconds until done.\n"
            "5. Close the dialog and start programming!"
        )

    def _on_variant_select(self, *args):
        pass

