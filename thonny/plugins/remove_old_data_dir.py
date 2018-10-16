import os.path
from tkinter.messagebox import askyesno, showinfo
from thonny import get_workbench, THONNY_USER_DIR
import shutil


def load_plugin():
    old_data_dir = os.path.join(os.path.expanduser("~"), ".thonny")
    if os.path.exists(old_data_dir):

        def doit():
            if not os.path.exists(old_data_dir):
                showinfo("Already deleted", 
                         "Looks like it's already deleted",
                         parent=get_workbench())
                return

            answer = askyesno(
                "Delete old data directory?",
                "Thonny versions before 3.0 (and first 3.0 betas) used to keep "
                + "configuration, logs and such in '%s'" % old_data_dir
                + ". "
                + "Since 3.0 this data is kept in a new location: '%s'.\n\n"
                % THONNY_USER_DIR
                + "If you don't intend to use older Thonny versions anymore, "
                + "you probably want to delete the old directory and reclaim disk space.\n\n"
                + "Do you want me to delete this directory now?",
                parent=get_workbench()
            )
            if answer:
                shutil.rmtree(old_data_dir, True)
                shutil.rmtree(old_data_dir, True)  # first one may keep empty directory
                showinfo("Done!", "Done!", parent=get_workbench())

        get_workbench().add_command(
            "delolddatadir", "tools", "Clean up Thonny 2.1 data folder ...", doit, group=110
        )
