from tkinter import *
from tkinter import ttk
from tkinter import messagebox
# from methods import *
import sqlite3
from shared_var import shared_variable


class ForgotPass(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.update()
        self.title("Forgot Your Password")
        self.focus_force()
        self.grab_set()
        self.resizable(FALSE,FALSE)
 
        self.minsize(self.winfo_width(), self.winfo_height())
        x_cordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

        self.uname = StringVar()
        self.answer = StringVar()
        self.newpass = StringVar()
        self.secrert_quetion = StringVar()
        self.confpass = StringVar()
        self.path = shared_variable.path

        self.heading = ttk.Label(self, text='''That's OK; we're here to help.''')
        self.heading.pack()

        self.forgotframe = ttk.LabelFrame(self, text="Fill below details")
        self.forgotframe.pack(side='top', padx=5, pady=5)

        self.change_pass_frame = ttk.LabelFrame(self, text="Set new password here")

        def newpass_enter(event):
            if self.newpassEntry.get() == 'Enter New Password *':
                self.newpassEntry.delete(0, END)
                self.newpassEntry.config(show='*')
        def newpass_out(event):
            if self.newpassEntry.get() == '':
                self.newpassEntry.insert(0, 'Enter New Password *')
                self.newpassEntry.config(show='')
      
        self.newpassEntry = ttk.Entry(self.change_pass_frame, textvariable=self.newpass, width=30)
        self.newpassEntry.pack(padx=5, pady=5)
        self.newpassEntry.insert(0, 'Enter New Password *')
        self.newpassEntry.bind('<FocusIn>',newpass_enter)
        self.newpassEntry.bind('<FocusOut>',newpass_out)

        def conf_pass_enter(event):
            if self.confpassEntry.get() == 'Confirm New Password *':
                self.confpassEntry.delete(0, END)
                
        def conf_pass_out(event):
            if self.confpassEntry.get() == '':
                self.confpassEntry.insert(0, 'Confirm New Password *')
      
        self.confpassEntry = ttk.Entry(self.change_pass_frame, textvariable=self.confpass, width=30)
        self.confpassEntry.pack(padx=5, pady=5)
        self.confpassEntry.insert(0, 'Confirm New Password *')
        self.confpassEntry.bind('<FocusIn>',conf_pass_enter)
        self.confpassEntry.bind('<FocusOut>',conf_pass_out)

        self.change_pass_btn = ttk.Button(self.change_pass_frame, text='Change Password',cursor='hand2', command=self.change_pass)
        self.change_pass_btn.pack(padx=5, pady=5)

        def user_enter(event):
            if self.usernameEntry.get() == 'User Name *':
                self.usernameEntry.delete(0, END)
        def user_out(event):
            if self.usernameEntry.get() == '':
                self.usernameEntry.insert(0, 'User Name *')
      
        self.usernameEntry = ttk.Entry(self.forgotframe, textvariable=self.uname, width=30)
        self.usernameEntry.pack(padx=5, pady=5)
        self.usernameEntry.insert(0, 'User Name *')
        self.usernameEntry.bind('<FocusIn>',user_enter)
        self.usernameEntry.bind('<FocusOut>',user_out)

        self.secrert_q_combo = ttk.Combobox(self.forgotframe, textvariable= self.secrert_quetion, width=30, value=['Select your secrert question here', '''What's your pet name?''',
                    'Your first teacher name',
                    'Your birthplace',
                    'Your favorite movie'])
        self.secrert_q_combo.current(0)
        self.secrert_q_combo.pack(padx=5, pady=5)

        def ans_enter(event):
            if self.answerEntry.get() == 'Your Answer *':
                self.answerEntry.delete(0, END)
        def ans_out(event):
            if self.answerEntry.get() == '':
                self.answerEntry.insert(0, 'Your Answer *')
      
        self.answerEntry = ttk.Entry(self.forgotframe, textvariable=self.answer, width=30)
        self.answerEntry.pack(padx=5, pady=5)
        self.answerEntry.insert(0, 'Your Answer *')
        self.answerEntry.bind('<FocusIn>',ans_enter)
        self.answerEntry.bind('<FocusOut>',ans_out)

        self.retrive_pass_btn = ttk.Button(self.forgotframe, text='Proceed',cursor='hand2', command=self.check_details)
        self.retrive_pass_btn.pack(padx=5, pady=5)

    def check_details(self):

        if self.uname.get() == "" or self.uname.get() == "User Name *" or self.answer.get() == "" or self.answer.get() == "Your Answer *"  or self.secrert_quetion.get() =="":
            messagebox.showerror("Error!", "Please fill the all entry field.",parent=self)
        else:
            try:
                conn = sqlite3.connect(f"{self.path}database/AIdesigner.db")
                cur = conn.cursor()
                cur.execute("select * from ADMIN where USERNAME=? and question=? and answer=?", (self.uname.get(),self.secrert_quetion.get(),self.answer.get()))
                row=cur.fetchone()
                conn.close()

                if row == None:
                    messagebox.showerror("Error!", "Please fill the all entry field correctly.", parent=self)
                else:
                    self.change_pass_frame.pack()

            except Exception as er:
                        messagebox.showerror("Error!", f"{er}")

    def change_pass(self):
        if self.newpass.get() == self.confpass.get():
            try:
                conn = sqlite3.connect(f"{self.path}database/AIdesigner.db")
                cur = conn.cursor()                
                cur.execute("update ADMIN set PASSWORD=? where USERNAME=?", (self.newpass.get(),self.uname.get()))
                conn.commit()
                messagebox.showinfo("Successful", "Password has changed successfully", parent=self)
                conn.close()
                self.destroy()

            except Exception as er:
                messagebox.showerror("Error!", f"{er}")