from tkinter import *
from tkinter import ttk, messagebox


class ContainerDesignHome(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.update()
        self.title("Container Design Home")
        self.focus_force()
        self.grab_set()
        # self.resizable(FALSE,FALSE)
        self.state('zoomed')
        self.overrideredirect(False)

        self.minsize(self.winfo_width(), self.winfo_height())
        x_cordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

