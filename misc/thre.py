from _thread import interrupt_main
from threading import Thread
from time import sleep
import os
import signal


def inter():
    print("interwait")
    sleep(1)
    print("interrupting")
    #interrupt_main()
    os.kill(os.getpid(), signal.SIGINT)
    #os.raise_signal(signal.SIGINT)
    print("interrupted")


#Thread(target=inter).start()
#"""
import tkinter
root = tkinter.Tk()
#root.focus_set()
root.mainloop()
#"""

#sleep(5)

print("done")
