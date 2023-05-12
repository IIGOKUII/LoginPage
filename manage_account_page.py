from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from tkinter import filedialog
from PIL import Image                                              
import os, sys 
import shutil
from PIL import ImageTk
import re
from shared_var import shared_variable


class EditProfile(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.update()
        self.title("Manage your account")
        self.focus_force()
        self.grab_set()
        self.resizable(FALSE,FALSE)
        self.protocol("WM_DELETE_WINDOW",self.disable_event)
        
        self.minsize(self.winfo_width(), self.winfo_height())
        x_cordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

        self.uname = StringVar()
        self.answer = StringVar()
        self.newpass = StringVar()
        self.secrert_quetion = StringVar()
        self.confpass = StringVar()
        self.newemail = StringVar()

        self.username = str(self.get_user())

        self.path = shared_variable.path

        self.forgotframe = ttk.LabelFrame(self, text="Edit your profile here")
        self.forgotframe.pack(side='left', padx=5, pady=5)

        self.change_profile_pic_btn = ttk.Button(self.forgotframe, text='Change Profile Picture',cursor='hand2', style="Accent.TButton",command=self.get_side_frame_profile)
        self.change_profile_pic_btn.pack(padx=5, pady=5)

        self.change_secrete_question_btn = ttk.Button(self.forgotframe, text='Change Secrete Question',cursor='hand2', style="Accent.TButton",command=self.get_side_frame_question)
        self.change_secrete_question_btn.pack(padx=5, pady=5)

        self.change_pass_btn = ttk.Button(self.forgotframe, text='Change Password',cursor='hand2', style="Accent.TButton",command=self.get_side_frame_pass)
        self.change_pass_btn.pack(padx=5, pady=5)

        self.change_email_btn = ttk.Button(self.forgotframe, text='Change Email ID',cursor='hand2', style="Accent.TButton",command=self.get_side_frame_email)
        self.change_email_btn.pack(padx=5, pady=5)

        self.side_frame_profile = ttk.Frame(self)
        self.side_frame_question = ttk.Frame(self)
        self.side_frame_pass = ttk.Frame(self)
        self.side_frame_email = ttk.Frame(self)


        self.sfprofile = ttk.LabelFrame(self.side_frame_profile, text="Select your new profile picture")
        self.sfprofile.pack(padx=5, pady=5)
        button_explore = ttk.Button(self.sfprofile,
                        text = "Browse Files", style="Accent.TButton",
                        command = self.browseFiles)
        button_explore.pack(padx=5, pady=5)

        self.successfullchangeprofile = ttk.Label(self.side_frame_profile)
        self.successfullchangeprofile.pack(padx=5, pady=5) 

        self.change_profile_btn = ttk.Button(self.side_frame_profile, text='Change profile pic',cursor='hand2', style="Accent.TButton", command=self.add_details)
       
        self.sfquestion = ttk.LabelFrame(self.side_frame_question, text="Select your new secrete question")
        self.sfquestion.pack(padx=5, pady=5)

        self.secrert_q_combo = ttk.Combobox(self.sfquestion, textvariable= self.secrert_quetion, width=30, value=['Select your secrert question here', '''What's your pet name?''',
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
      
        self.answerEntry = ttk.Entry(self.sfquestion, textvariable=self.answer, width=30)
        self.answerEntry.pack(padx=5, pady=5)
        self.answerEntry.insert(0, 'Your Answer *')
        self.answerEntry.bind('<FocusIn>',ans_enter)
        self.answerEntry.bind('<FocusOut>',ans_out)

        self.change_answer_btn = ttk.Button(self.sfquestion, text='Proceed',cursor='hand2', style="Accent.TButton", command=self.change_ans)
        self.change_answer_btn.pack(padx=5, pady=5)

        self.sfpass = ttk.LabelFrame(self.side_frame_pass, text="Set your new password")
        self.sfpass.pack(padx=5, pady=5)

        def newpass_enter(event):
            if self.newpassEntry.get() == 'Enter New Password *':
                self.newpassEntry.delete(0, END)
                self.newpassEntry.config(show='*')
        def newpass_out(event):
            if self.newpassEntry.get() == '':
                self.newpassEntry.insert(0, 'Enter New Password *')
                self.newpassEntry.config(show='')

        self.newpassEntry = ttk.Entry(self.sfpass, textvariable=self.newpass, width=30)
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
      
        self.confpassEntry = ttk.Entry(self.sfpass, textvariable=self.confpass, width=30)
        self.confpassEntry.pack(padx=5, pady=5)
        self.confpassEntry.insert(0, 'Confirm New Password *')
        self.confpassEntry.bind('<FocusIn>',conf_pass_enter)
        self.confpassEntry.bind('<FocusOut>',conf_pass_out)

        self.retrive_pass_btn = ttk.Button(self.sfpass, text='Change',cursor='hand2', style="Accent.TButton", command=self.change_pass)
        self.retrive_pass_btn.pack(padx=5, pady=5)

        self.sfemail = ttk.LabelFrame(self.side_frame_email, text="Set your new email id")
        self.sfemail.pack(padx=5, pady=5)

        def newemail_enter(event):
            if self.newemailEntry.get() == 'Enter New Email ID *':
                self.newemailEntry.delete(0, END)

        def newemail_out(event):
            if self.newemailEntry.get() == '':
                self.newemailEntry.insert(0, 'Enter New Email ID *')


        self.newemailEntry = ttk.Entry(self.sfemail, textvariable=self.newemail, width=30)
        self.newemailEntry.pack(padx=5, pady=5)
        self.newemailEntry.insert(0, 'Enter New Email ID *')
        self.newemailEntry.bind('<FocusIn>',newemail_enter)
        self.newemailEntry.bind('<FocusOut>',newemail_out)

        self.retrive_email_btn = ttk.Button(self.sfemail, text='Change',cursor='hand2', style="Accent.TButton", command=self.change_email)
        self.retrive_email_btn.pack(padx=5, pady=5)

    def get_side_frame_profile(self):
        self.side_frame_profile.pack(side='right', padx=5, pady=5)
        self.side_frame_question.pack_forget()
        self.side_frame_pass.pack_forget()
        self.side_frame_email.pack_forget()

    def get_side_frame_question(self):
        self.side_frame_question.pack(side='right', padx=5, pady=5)
        self.side_frame_profile.pack_forget()
        self.side_frame_pass.pack_forget()
        self.side_frame_email.pack_forget()

    def get_side_frame_pass(self):
        self.side_frame_pass.pack(side='right', padx=5, pady=5)
        self.side_frame_profile.pack_forget()
        self.side_frame_question.pack_forget()
        self.side_frame_email.pack_forget()

    def get_side_frame_email(self):
        self.side_frame_email.pack(side='right', padx=5, pady=5)
        self.side_frame_pass.pack_forget()
        self.side_frame_profile.pack_forget()
        self.side_frame_question.pack_forget()

    def add_details(self):
            source  = f"{self.path}images/temp/'+str(self.username)+'.png"
            target =f"{self.path}images/profile/'+str(self.username)+'.png"
            shutil.copy(source, target)
            messagebox.showinfo("Successful", "Your profile picture changed successfully.\nRe-start application to see changes.", parent=self)
            try:
                Path = f"{self.path}images/temp/"
                list=os.listdir(Path)
                for tempfile in list:
                    os.remove(Path+tempfile)
            except:
                pass

            self.destroy()


    def browseFiles(self):
        try:
            filename = filedialog.askopenfilename(initialdir = "/",
                                                title = "Select a File",
                                                filetypes = (("PNG",
                                                                "*.png*"),
                                                            ("all files",
                                                                "*.*")))
                
            source = filename
            target = f"{self.path}images/temp/'+str(self.username)+'.png"
            if source == None:
                pass
            else:
                shutil.copy(source, target)

            def resize():
                    if os.path.isfile(target):
                        im = Image.open(target)
                        f, e = os.path.splitext(target)
                        imResize = im.resize((150,150), Image.ANTIALIAS)
                        imResize.save(f+'.png', 'png', quality=80)
            resize()
            self.profile_img = ImageTk.PhotoImage(file=target)
            self.successfullchangeprofile.config(image=self.profile_img)
            self.change_profile_btn.pack(padx=5, pady=5)

        except:
            pass          

    def change_pass(self):
        if self.newpass.get() == self.confpass.get():
            try:
                conn = sqlite3.connect(f"{self.path}database/aicdgusers.db")
                cur = conn.cursor()                
                cur.execute("update ADMIN set PASSWORD=? where USERNAME=?", (self.newpass.get(),self.username))
                conn.commit()
                messagebox.showinfo("Successful", "Password has changed successfully.\nYou can use this new password for next login.", parent=self)
                conn.close()
                # self.redirect_login_window()
                self.destroy()

            except Exception as er:
                messagebox.showerror("Error!", f"{er}")
        else:
            messagebox.showerror("Error!", "Please fill the all entry field correctly.",parent=self)

    def change_email(self):
        def validate_email(email):
            """
            Validate an email address using a regular expression.
            Returns True if the email is valid, False otherwise.
            """
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(email_regex, email) is not None

        email = self.newemail.get()

        if self.newemail.get() == '' or self.newemail.get() == 'Enter New Email ID *':
            messagebox.showerror("Error!", "Please fill the email ID entry field.",parent=self)
        elif not validate_email(email):
                messagebox.showerror("Error!", "Invalid email address.",parent=self)
        else:
            try:
                conn = sqlite3.connect(f"{self.path}database/aicdgusers.db")
                cur = conn.cursor()                
                cur.execute("update ADMIN set EMAIL=? where USERNAME=?", (self.newemail.get(),self.username))
                conn.commit()
                messagebox.showinfo("Successful", "Email ID has changed successfully.", parent=self)
                conn.close()
                # self.redirect_login_window()
                self.destroy()

            except Exception as er:
                messagebox.showerror("Error!", f"{er}")


    def change_ans(self):
        if self.answer.get() == "" or self.answer.get() == "Your Answer *":
            messagebox.showerror("Error!", "Please fill the all entry field.",parent=self)
        elif self.secrert_quetion.get() =="" or self.secrert_quetion.get() =="Select your secrert question here" :
            messagebox.showerror("Error!", "Please fill the all entry field.",parent=self)
        else:
            try:
                conn = sqlite3.connect(f"{self.path}database/aicdgusers.db")
                cur = conn.cursor()                
                cur.execute("update ADMIN set answer=? where USERNAME=?", (self.answer.get(),self.username))
                conn.commit()
                messagebox.showinfo("Successful", "Your secrert question & anwser has been changed successfully.\nPlease remember it & use to retrive your password in case you forgot.", parent=self)
                conn.close()
                # self.redirect_login_window()
                self.destroy()

            except Exception as er:
                messagebox.showerror("Error!", f"{er}")


    def get_user(self):
        try:
            Path = 'D:/logedusers/'
            list=os.listdir(Path)
            unamefile = list[0]
            splituname=unamefile.split('.')
            uname=splituname[0]
        except:
            uname = 'Guest'
        return uname
    
    def disable_event(self):
        file_location = f"{self.path}images/temp/'+str(self.username)+'.png"
        # check if the file exists
        if os.path.exists(file_location):
            # delete the file
            os.remove(file_location)
        else:
            pass
        self.destroy()


