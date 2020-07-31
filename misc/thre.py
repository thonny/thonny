from _thread import interrupt_main
from threading import Thread
from time import sleep


def inter():
    print("interwait")
    sleep(1)
    print("interrupting")
    interrupt_main()
    print("interrupted")


Thread(target=inter).start()

import tkinter
root = tkinter.Tk()
root.mainloop()

print("done")
