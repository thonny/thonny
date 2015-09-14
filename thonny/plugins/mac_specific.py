# -*- coding: utf-8 -*-
from thonny.misc_utils import running_on_mac_os
from thonny.globals import get_workbench

def _set_up_mac_specific_stuff():
    # TODO: see idlelib.macosxSupports
    # https://www.tcl.tk/man/tcl8.6/TkCmd/tk_mac.htm
    
    def mac_open_document(*args):
        # TODO:
        #showinfo("open doc", str(args))
        pass
    
    def mac_open_application(*args):
        #showinfo("open app", str(args))
        pass
    
    def mac_reopen_application(*args):
        #showinfo("reopen app", str(args))
        pass
    
    def _cmd_mac_add_download_assessment():
        # TODO:
        """
        Normally Mac doesn't allow opening py files from web directly
        See:
        http://keith.chaos-realm.net/plugin/tag/downloadassessment
        https://developer.apple.com/library/mac/#documentation/Miscellaneous/Reference/UTIRef/Articles/System-DeclaredUniformTypeIdentifiers.html
        
        create file ~/Library/Preferences/com.apple.DownloadAssessment.plist
        with following content:
        
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>LSRiskCategorySafe</key> 
            <dict>
                <key>LSRiskCategoryContentTypes</key>
                <array>
                    <string>public.xml</string>
                </array>
            
                <key>LSRiskCategoryExtensions</key>
                <array>
                    <string>py</string>
                    <string>pyw</string>
                </array>
            </dict>
        </dict>
        </plist>
        """
    
    get_workbench().createcommand("::tk::mac::OpenDocument", mac_open_document)
    get_workbench().createcommand("::tk::mac::OpenApplication", mac_open_application)
    get_workbench().createcommand("::tk::mac::ReopenApplication", mac_reopen_application)
    # TODO: get_workbench().createcommand("tkAboutDialog", self._cmd_about)
    get_workbench().createcommand("::tk::mac::ShowPreferences", lambda: print("Prefs"))
    
    """ TODO:
    self._add_command("mac_add_download_assessment", "Misc", 'Allow opening py files from browser ...',
                      ...)
    """
    
def load_plugin():
    if running_on_mac_os():
        _set_up_mac_specific_stuff()