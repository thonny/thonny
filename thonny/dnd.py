"""Drag-and-drop support for Tkinter.

This is very preliminary.  I currently only support dnd *within* one
application, between different windows (or within the same window).

I am trying to make this as generic as possible -- not dependent on
the use of a particular widget or icon type, etc.  I also hope that
this will work with Pmw.

To enable an object to be dragged, you must create an event binding
for it that starts the drag-and-drop process. Typically, you should
bind <ButtonPress> to a callback function that you write. The function
should call Tkdnd.dnd_start(source, event), where 'source' is the
object to be dragged, and 'event' is the event that invoked the call
(the argument to your callback function).  Even though this is a class
instantiation, the returned instance should not be stored -- it will
be kept alive automatically for the duration of the drag-and-drop.

When a drag-and-drop is already in process for the Tk interpreter, the
call is *ignored*; this normally averts starting multiple simultaneous
dnd processes, e.g. because different button callbacks all
dnd_start().

The object is *not* necessarily a widget -- it can be any
application-specific object that is meaningful to potential
drag-and-drop targets.

Potential drag-and-drop targets are discovered as follows.  Whenever
the mouse moves, and at the start and end of a drag-and-drop move, the
Tk widget directly under the mouse is inspected.  This is the target
widget (not to be confused with the target object, yet to be
determined).  If there is no target widget, there is no dnd target
object.  If there is a target widget, and it has an attribute
dnd_accept, this should be a function (or any callable object).  The
function is called as dnd_accept(source, event), where 'source' is the
object being dragged (the object passed to dnd_start() above), and
'event' is the most recent event object (generally a <Motion> event;
it can also be <ButtonPress> or <ButtonRelease>).  If the dnd_accept()
function returns something other than None, this is the new dnd target
object.  If dnd_accept() returns None, or if the target widget has no
dnd_accept attribute, the target widget's parent is considered as the
target widget, and the search for a target object is repeated from
there.  If necessary, the search is repeated all the way up to the
root widget.  If none of the target widgets can produce a target
object, there is no target object (the target object is None).

The target object thus produced, if any, is called the new target
object.  It is compared with the old target object (or None, if there
was no old target widget).  There are several cases ('source' is the
source object, and 'event' is the most recent event object):

- Both the old and new target objects are None.  Nothing happens.

- The old and new target objects are the same object.  Its method
dnd_motion(source, event) is called.

- The old target object was None, and the new target object is not
None.  The new target object's method dnd_enter(source, event) is
called.

- The new target object is None, and the old target object is not
None.  The old target object's method dnd_leave(source, event) is
called.

- The old and new target objects differ and neither is None.  The old
target object's method dnd_leave(source, event), and then the new
target object's method dnd_enter(source, event) is called.

Once this is done, the new target object replaces the old one, and the
Tk mainloop proceeds.  The return value of the methods mentioned above
is ignored; if they raise an exception, the normal exception handling
mechanisms take over.

The drag-and-drop processes can end in two ways: a final target object
is selected, or no final target object is selected.  When a final
target object is selected, it will always have been notified of the
potential drop by a call to its dnd_enter() method, as described
above, and possibly one or more calls to its dnd_motion() method; its
dnd_leave() method has not been called since the last call to
dnd_enter().  The target is notified of the drop by a call to its
method dnd_commit(source, event).

If no final target object is selected, and there was an old target
object, its dnd_leave(source, event) method is called to complete the
dnd sequence.

Finally, the source object is notified that the drag-and-drop process
is over, by a call to source.dnd_end(target, event), specifying either
the selected target object, or None if no target object was selected.
The source object can use this to implement the commit action; this is
sometimes simpler than to do it in the target's dnd_commit().  The
target's dnd_commit() method could then simply be aliased to
dnd_leave().

At any time during a dnd sequence, the application can cancel the
sequence by calling the cancel() method on the object returned by
dnd_start().  This will call dnd_leave() if a target is currently
active; it will never call dnd_commit().

"""

import tkinter

__all__ = ["dnd_start", "DndHandler"]


# The factory function


def dnd_start(source, event):
    h = DndHandler(source, event)
    if h.root is not None:
        return h
    else:
        return None


# The class that does the work


class DndHandler:
    root = None

    def __init__(self, source, event):
        if event.num > 5:
            return
        root = event.widget._root()
        try:
            root.__dnd
            return  # Don't start recursive dnd
        except AttributeError:
            root.__dnd = self
            self.root = root
        self.source = source
        self.target = None
        self.initial_button = button = event.num
        self.initial_widget = widget = event.widget
        self.release_pattern = "<B%d-ButtonRelease-%d>" % (button, button)
        self.save_cursor = widget["cursor"] or ""
        widget.bind(self.release_pattern, self.on_release)
        widget.bind("<Motion>", self.on_motion)
        widget["cursor"] = "hand2"

    def __del__(self):
        root = self.root
        self.root = None
        if root is not None:
            try:
                del root.__dnd
            except AttributeError:
                pass

    def on_motion(self, event):
        x, y = event.x_root, event.y_root
        target_widget = self.initial_widget.winfo_containing(x, y)
        source = self.source
        motion_anywhere = getattr(source, "dnd_motion_anywhere", None)
        if motion_anywhere:
            motion_anywhere(source, event)
        new_target = None
        while target_widget is not None:
            try:
                attr = target_widget.dnd_accept
            except AttributeError:
                pass
            else:
                new_target = attr(source, event)
                if new_target is not None:
                    break
            target_widget = target_widget.master
        old_target = self.target
        if old_target is new_target:
            if old_target is not None:
                old_target.dnd_motion(source, event)
        else:
            if old_target is not None:
                self.target = None
                old_target.dnd_leave(source, event)
            if new_target is not None:
                new_target.dnd_enter(source, event)
                self.target = new_target

    def on_release(self, event):
        self.finish(event, 1)

    def cancel(self, event=None):
        self.finish(event, 0)

    def finish(self, event, commit=0):
        target = self.target
        source = self.source
        widget = self.initial_widget
        root = self.root
        try:
            del root.__dnd
            self.initial_widget.unbind(self.release_pattern)
            self.initial_widget.unbind("<Motion>")
            widget["cursor"] = self.save_cursor
            self.target = self.source = self.initial_widget = self.root = None
            if target is not None:
                if commit:
                    target.dnd_commit(source, event)
                else:
                    target.dnd_leave(source, event)
        finally:
            source.dnd_end(target, event)
