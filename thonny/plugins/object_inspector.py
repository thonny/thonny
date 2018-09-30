import ast
import logging
import tkinter as tk
from tkinter import ttk

import thonny.memory
from thonny import get_runner, get_workbench, ui_utils
from thonny.common import InlineCommand
from thonny.misc_utils import shorten_repr
from thonny.tktextext import TextFrame
import base64


class ObjectInspector(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master, style="ViewBody.TFrame")

        self.object_id = None
        self.object_info = None

        # self._create_general_page()
        self._create_content_page()
        self._create_attributes_page()
        self.active_page = self.content_page
        self.active_page.grid(row=1, column=0, sticky="nsew")

        toolbar = self._create_toolbar()
        toolbar.grid(row=0, column=0, sticky="nsew", pady=(0, 1))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        get_workbench().bind("ObjectSelect", self.show_object, True)
        get_workbench().bind(
            "get_object_info_response", self._handle_object_info_event, True
        )
        get_workbench().bind("DebuggerResponse", self._handle_progress_event, True)
        get_workbench().bind("ToplevelResponse", self._handle_progress_event, True)

        # self.demo()

    def _create_toolbar(self):
        toolbar = ttk.Frame(self, style="ViewToolbar.TFrame")

        self.title_label = ttk.Label(
            toolbar,
            style="ViewToolbar.TLabel",
            text=""
            # borderwidth=1,
            # background=ui_utils.get_main_background()
        )
        self.title_label.grid(row=0, column=3, sticky="nsew", pady=5, padx=5)
        toolbar.columnconfigure(3, weight=1)

        self.tabs = []

        def create_tab(col, caption, page):
            if page == self.active_page:
                style = "Active.ViewTab.TLabel"
            else:
                style = "Inactive.ViewTab.TLabel"
            tab = ttk.Label(toolbar, text=caption, style=style)
            tab.grid(row=0, column=col, pady=5, padx=5, sticky="nsew")
            self.tabs.append(tab)
            page.tab = tab

            def on_click(event):
                if self.active_page == page:
                    return
                else:
                    if self.active_page is not None:
                        self.active_page.grid_forget()
                        self.active_page.tab.configure(style="Inactive.ViewTab.TLabel")

                    self.active_page = page
                    page.grid(row=1, column=0, sticky="nsew", padx=0)
                    tab.configure(style="Active.ViewTab.TLabel")
                    if self.active_page == self.attributes_page and (
                        self.object_info is None or self.object_info["attributes"] == {}
                    ):
                        self.request_object_info()

            tab.bind("<1>", on_click)

        # create_tab(1, "Overview", self.general_page)
        create_tab(5, "Data", self.content_page)
        create_tab(6, "Atts", self.attributes_page)

        def create_navigation_link(col, image_filename, action, tooltip, padx=0):
            button = ttk.Button(
                toolbar,
                # command=handler,
                image=get_workbench().get_image(image_filename),
                style="ViewToolbar.Toolbutton",  # TODO: does this cause problems in some Macs?
                state=tk.NORMAL,
            )
            ui_utils.create_tooltip(button, tooltip)

            button.grid(row=0, column=col, sticky=tk.NE, padx=padx, pady=4)
            button.bind("<Button-1>", action)
            return button

        def configure(event):
            if event.width > 20:
                self.title_label.configure(wraplength=event.width - 10)

        self.title_label.bind("<Configure>", configure, True)

        self.back_button = create_navigation_link(
            1, "nav-backward", self.navigate_back, "Previous object", (5, 0)
        )
        self.forward_button = create_navigation_link(
            2, "nav-forward", self.navigate_forward, "Next object"
        )
        self.back_links = []
        self.forward_links = []

        return toolbar

    def _create_content_page(self):
        self.content_page = ttk.Frame(self, style="ViewBody.TFrame")
        # type-specific inspectors
        self.current_content_inspector = None
        self.content_inspectors = []
        # load custom inspectors
        for insp_class in get_workbench().content_inspector_classes:
            self.content_inspectors.append(insp_class(self.content_page))

        # read standard inspectors
        self.content_inspectors.extend(
            [
                FileHandleInspector(self.content_page),
                FunctionInspector(self.content_page),
                StringInspector(self.content_page),
                ElementsInspector(self.content_page),
                DictInspector(self.content_page),
                ImageInspector(self.content_page),
                ReprInspector(self.content_page),  # fallback content inspector
            ]
        )

        self.content_page.columnconfigure(0, weight=1)
        self.content_page.rowconfigure(0, weight=1)

    def _create_attributes_page(self):
        self.attributes_page = AttributesFrame(self)

    def navigate_back(self, event):
        if len(self.back_links) == 0:
            return

        self.forward_links.append(self.object_id)
        self._show_object_by_id(self.back_links.pop(), True)

    def navigate_forward(self, event):
        if len(self.forward_links) == 0:
            return

        self.back_links.append(self.object_id)
        self._show_object_by_id(self.forward_links.pop(), True)

    def show_object(self, event):
        self._show_object_by_id(event.object_id)

    def _show_object_by_id(self, object_id, via_navigation=False):

        if self.winfo_ismapped() and self.object_id != object_id:
            if not via_navigation and self.object_id is not None:
                if self.object_id in self.back_links:
                    self.back_links.remove(self.object_id)
                self.back_links.append(self.object_id)
                del self.forward_links[:]

            self.object_id = object_id
            self.set_object_info(None)
            self._set_title("object @ " + thonny.memory.format_object_id(object_id))
            self.request_object_info()

    def _set_title(self, text):
        self.title_label.configure(text=text)

    def _handle_object_info_event(self, msg):
        if self.winfo_ismapped():
            if msg.info["id"] == self.object_id:
                if hasattr(msg, "not_found") and msg.not_found:
                    self.object_id = None
                    self.set_object_info(None)
                else:
                    self.set_object_info(msg.info)

    def _handle_progress_event(self, event):
        if self.object_id is not None:
            self.request_object_info()

    def request_object_info(self):
        # current width and height of the frame are required for
        # some content providers
        if self.active_page is not None:
            frame_width = self.active_page.winfo_width()
            frame_height = self.active_page.winfo_height()

            # in some cases measures are inaccurate
            if frame_width < 5 or frame_height < 5:
                frame_width = None
                frame_height = None
            # print("pa", frame_width, frame_height)
        else:
            frame_width = None
            frame_height = None

        get_runner().send_command(
            InlineCommand(
                "get_object_info",
                object_id=self.object_id,
                include_attributes=self.active_page == self.attributes_page,
                all_attributes=False,
                frame_width=frame_width,
                frame_height=frame_height,
            )
        )

    def set_object_info(self, object_info):
        self.object_info = object_info
        if object_info is None or "error" in object_info:
            if object_info is None:
                self._set_title("")
            else:
                self._set_title(object_info["error"])
            if self.current_content_inspector is not None:
                self.current_content_inspector.grid_remove()
                self.current_content_inspector = None
            self.attributes_page.clear()
        else:
            self._set_title(
                object_info["full_type_name"]
                + " @ "
                + thonny.memory.format_object_id(object_info["id"])
            )
            self.attributes_page.update_variables(object_info["attributes"])
            self.update_type_specific_info(object_info)

            # update layout
            # self._expose(None)
            # if not self.grid_frame.winfo_ismapped():
            #    self.grid_frame.grid()

        """
        if self.back_links == []:
            self.back_label.config(foreground="lightgray", cursor="arrow")
        else:
            self.back_label.config(foreground="blue", cursor="hand2")
    
        if self.forward_links == []:
            self.forward_label.config(foreground="lightgray", cursor="arrow")
        else:
            self.forward_label.config(foreground="blue", cursor="hand2")
        """

    def update_type_specific_info(self, object_info):
        content_inspector = None
        for insp in self.content_inspectors:
            if insp.applies_to(object_info):
                content_inspector = insp
                break

        # print("TYPSE", content_inspector)
        if content_inspector != self.current_content_inspector:
            if self.current_content_inspector is not None:
                self.current_content_inspector.grid_remove()  # TODO: or forget?
                self.current_content_inspector = None

            if content_inspector is not None:
                content_inspector.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 0))

            self.current_content_inspector = content_inspector

        if self.current_content_inspector is not None:
            self.current_content_inspector.set_object_info(object_info)

    def goto_type(self, event):
        if self.object_info is not None:
            get_workbench().event_generate(
                "ObjectSelect", object_id=self.object_info["type_id"]
            )


class ContentInspector:
    def __init__(self, master):
        pass

    def set_object_info(self, object_info):
        pass

    def get_tab_text(self):
        return "Data"

    def applies_to(self, object_info):
        return False


class FileHandleInspector(TextFrame, ContentInspector):
    def __init__(self, master):
        ContentInspector.__init__(self, master)
        TextFrame.__init__(self, master, read_only=True)
        self.cache = {}  # stores file contents for handle id-s
        self.config(borderwidth=1)
        self.text.configure(background="white")
        self.text.tag_configure("read", foreground="lightgray")

    def applies_to(self, object_info):
        return "file_content" in object_info or "file_error" in object_info

    def set_object_info(self, object_info):

        if "file_content" not in object_info:
            logging.exception("File error: " + object_info["file_error"])
            return

        assert "file_content" in object_info
        content = object_info["file_content"]
        line_count_sep = len(content.split("\n"))
        # line_count_term = len(content.splitlines())
        # char_count = len(content)
        self.text.configure(height=min(line_count_sep, 10))
        self.text.set_content(content)

        assert "file_tell" in object_info
        # f.tell() gives num of bytes read (minus some magic with linebreaks)

        file_bytes = content.encode(encoding=object_info["file_encoding"])
        bytes_read = file_bytes[0 : object_info["file_tell"]]
        read_content = bytes_read.decode(encoding=object_info["file_encoding"])
        read_char_count = len(read_content)
        # read_line_count_term = (len(content.splitlines())
        #                        - len(content[read_char_count:].splitlines()))

        pos_index = "1.0+" + str(read_char_count) + "c"
        self.text.tag_add("read", "1.0", pos_index)
        self.text.see(pos_index)

        # TODO: show this info somewhere
        """
        label.configure(text="Read %d/%d %s, %d/%d %s" 
                        % (read_char_count,
                           char_count,
                           "symbol" if char_count == 1 else "symbols",  
                           read_line_count_term,
                           line_count_term,
                           "line" if line_count_term == 1 else "lines"))
        """


class FunctionInspector(TextFrame, ContentInspector):
    def __init__(self, master):
        ContentInspector.__init__(self, master)
        TextFrame.__init__(self, master, read_only=True)
        self.text.configure(background="white")

    def applies_to(self, object_info):
        return "source" in object_info

    def get_tab_text(self):
        return "Code"

    def set_object_info(self, object_info):
        line_count = len(object_info["source"].split("\n"))
        self.text.configure(height=min(line_count, 15))
        self.text.set_content(object_info["source"])


class StringInspector(TextFrame, ContentInspector):
    def __init__(self, master):
        ContentInspector.__init__(self, master)
        TextFrame.__init__(self, master, read_only=True)
        # self.config(borderwidth=1)
        # self.text.configure(background="white")

    def applies_to(self, object_info):
        return object_info["type"] == repr(str)

    def set_object_info(self, object_info):
        # TODO: don't show too big string
        content = ast.literal_eval(object_info["repr"])
        line_count_sep = len(content.split("\n"))
        # line_count_term = len(content.splitlines())
        self.text.configure(height=min(line_count_sep, 10))
        self.text.set_content(content)
        """ TODO:
        label.configure(text="%d %s, %d %s" 
                        % (len(content),
                           "symbol" if len(content) == 1 else "symbols",
                           line_count_term, 
                           "line" if line_count_term == 1 else "lines"))
        """


class ReprInspector(TextFrame, ContentInspector):
    def __init__(self, master):
        ContentInspector.__init__(self, master)
        TextFrame.__init__(self, master, read_only=True)
        # self.config(borderwidth=1)
        # self.text.configure(background="white")

    def applies_to(self, object_info):
        return True

    def set_object_info(self, object_info):
        # TODO: don't show too big string
        content = object_info["repr"]
        self.text.set_content(content)
        """
        line_count_sep = len(content.split("\n"))
        line_count_term = len(content.splitlines())
        self.text.configure(height=min(line_count_sep, 10))
        label.configure(text="%d %s, %d %s" 
                        % (len(content),
                           "symbol" if len(content) == 1 else "symbols",
                           line_count_term, 
                           "line" if line_count_term == 1 else "lines"))
        """


class ElementsInspector(thonny.memory.MemoryFrame, ContentInspector):
    def __init__(self, master):
        ContentInspector.__init__(self, master)
        thonny.memory.MemoryFrame.__init__(self, master, ("index", "id", "value"))

        # self.vert_scrollbar.grid_remove()
        self.tree.column("index", width=40, anchor=tk.W, stretch=False)
        self.tree.column("id", width=750, anchor=tk.W, stretch=True)
        self.tree.column("value", width=750, anchor=tk.W, stretch=True)

        self.tree.heading("index", text="Index", anchor=tk.W)
        self.tree.heading("id", text="Value ID", anchor=tk.W)
        self.tree.heading("value", text="Value", anchor=tk.W)

        self.elements_have_indices = None
        self.update_memory_model()

        get_workbench().bind("ShowView", self.update_memory_model, True)
        get_workbench().bind("HideView", self.update_memory_model, True)

    def update_memory_model(self, event=None):
        self._update_columns()

    def _update_columns(self):
        if get_workbench().in_heap_mode():
            if self.elements_have_indices:
                self.tree.configure(displaycolumns=("index", "id"))
            else:
                self.tree.configure(displaycolumns=("id",))
        else:
            if self.elements_have_indices:
                self.tree.configure(displaycolumns=("index", "value"))
            else:
                self.tree.configure(displaycolumns=("value"))

    def applies_to(self, object_info):
        return "elements" in object_info

    def on_select(self, event):
        pass

    def on_double_click(self, event):
        self.show_selected_object_info()

    def set_object_info(self, object_info):
        assert "elements" in object_info

        self.elements_have_indices = object_info["type"] in (repr(tuple), repr(list))
        self._update_columns()

        self._clear_tree()
        index = 0
        # TODO: don't show too big number of elements
        for element in object_info["elements"]:
            node_id = self.tree.insert("", "end")
            if self.elements_have_indices:
                self.tree.set(node_id, "index", index)
            else:
                self.tree.set(node_id, "index", "")

            self.tree.set(node_id, "id", thonny.memory.format_object_id(element.id))
            self.tree.set(
                node_id,
                "value",
                shorten_repr(element.repr, thonny.memory.MAX_REPR_LENGTH_IN_GRID),
            )
            index += 1

        count = len(object_info["elements"])
        self.tree.config(height=min(count, 10))

        """ TODO:
        label.configure (
            text=("%d element" if count == 1 else "%d elements") % count
        ) 
        """


class DictInspector(thonny.memory.MemoryFrame, ContentInspector):
    def __init__(self, master):
        ContentInspector.__init__(self, master)
        thonny.memory.MemoryFrame.__init__(
            self, master, ("key_id", "id", "key", "value")
        )
        self.configure(border=1)
        # self.vert_scrollbar.grid_remove()
        self.tree.column("key_id", width=100, anchor=tk.W, stretch=False)
        self.tree.column("key", width=100, anchor=tk.W, stretch=False)
        self.tree.column("id", width=750, anchor=tk.W, stretch=True)
        self.tree.column("value", width=750, anchor=tk.W, stretch=True)

        self.tree.heading("key_id", text="Key ID", anchor=tk.W)
        self.tree.heading("key", text="Key", anchor=tk.W)
        self.tree.heading("id", text="Value ID", anchor=tk.W)
        self.tree.heading("value", text="Value", anchor=tk.W)

        self.update_memory_model()

    def update_memory_model(self, event=None):
        if get_workbench().in_heap_mode():
            self.tree.configure(displaycolumns=("key_id", "id"))
        else:
            self.tree.configure(displaycolumns=("key", "value"))

    def applies_to(self, object_info):
        return "entries" in object_info

    def on_select(self, event):
        pass

    def on_double_click(self, event):
        # NB! this selects value
        self.show_selected_object_info()

    def set_object_info(self, object_info):
        assert "entries" in object_info

        self._clear_tree()
        # TODO: don't show too big number of elements
        for key, value in object_info["entries"]:
            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "key_id", thonny.memory.format_object_id(key.id))
            self.tree.set(
                node_id,
                "key",
                shorten_repr(key.repr, thonny.memory.MAX_REPR_LENGTH_IN_GRID),
            )
            self.tree.set(node_id, "id", thonny.memory.format_object_id(value.id))
            self.tree.set(
                node_id,
                "value",
                shorten_repr(value.repr, thonny.memory.MAX_REPR_LENGTH_IN_GRID),
            )

        count = len(object_info["entries"])
        self.tree.config(height=min(count, 10))

        """ TODO:
        label.configure (
            text=("%d entry" if count == 1 else "%d entries") % count
        ) 
        """

        self.update_memory_model()


class ImageInspector(ContentInspector, tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        ContentInspector.__init__(self, master)
        self.label = tk.Label(self, anchor="nw")
        self.label.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def set_object_info(self, object_info):
        # print(object_info["image_data"])
        if isinstance(object_info["image_data"], bytes):
            data = base64.b64encode(object_info["image_data"])
        elif isinstance(object_info["image_data"], str):
            data = object_info["image_data"]
        else:
            self.label.configure(
                image=None,
                text="Unsupported image data (%s)" % type(object_info["image_data"]),
            )
            return

        try:
            self.image = tk.PhotoImage(data=data)
            self.label.configure(image=self.image)
        except Exception as e:
            self.label.configure(image=None, text="Unsupported image data (%s)" % e)

    def applies_to(self, object_info):
        return "image_data" in object_info


class AttributesFrame(thonny.memory.VariablesFrame):
    def __init__(self, master):
        thonny.memory.VariablesFrame.__init__(self, master)
        self.configure(border=0)

    def on_select(self, event):
        pass

    def on_double_click(self, event):
        self.show_selected_object_info()


def load_plugin() -> None:
    get_workbench().add_view(ObjectInspector, "Object inspector", "se")
