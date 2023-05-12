from tkinter import *
from tkinter import messagebox, ttk
from PIL import ImageTk
import sqlite3
from datetime import datetime, time
from shared_var import shared_variable
# import forgotpass_page
import mold_home_page
import container_design_home_page
from ttkbootstrap import Style


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create control variables
        self.logged_user_name = StringVar()
        self.password = StringVar()
        self.designer_name = StringVar()
        self.emp_name = StringVar()
        self.path = shared_variable.path

        # ASB Logo
        self.logo_img = ImageTk.PhotoImage(file=f'{self.path}images/logo.png')
        self.asbLabel = ttk.Label(self, image=self.logo_img)
        self.asbLabel.pack(side='top', pady=5)

        # Create a Frame for the Entry & buttons
        self.login_frame = ttk.LabelFrame(self, text="Login Here", width=346, height=600, padding=(20, 10))
        self.login_frame.pack(padx=20, pady=10)

        def enter_login(event):
            self.login_func()

        def user_enter(event):
            if self.usernameEntry.get() == 'User Name *':
                self.usernameEntry.delete(0, END)

        def user_out(event):
            if self.usernameEntry.get() == '':
                self.usernameEntry.insert(0, 'User Name *')

        self.usernameEntry = ttk.Entry(self.login_frame, textvariable=self.logged_user_name, width=30)
        self.usernameEntry.pack(padx=5, pady=5)
        self.usernameEntry.insert(0, 'User Name *')
        self.usernameEntry.bind('<FocusIn>', user_enter)
        self.usernameEntry.bind('<FocusOut>', user_out)
        self.usernameEntry.bind('<Return>', enter_login)

        def pass_enter(event):
            if self.passwordEntry.get() == 'Password *':
                self.passwordEntry.delete(0, END)
                self.passwordEntry.config(show='*')

        def pass_out(event):
            if self.passwordEntry.get() == '':
                self.passwordEntry.insert(0, 'Password *')
                self.passwordEntry.config(show='')

        self.passwordEntry = ttk.Entry(self.login_frame, textvariable=self.password, width=30)
        self.passwordEntry.pack(padx=5, pady=5)
        self.passwordEntry.insert(0, 'Password *')
        self.passwordEntry.bind('<FocusIn>', pass_enter)
        self.passwordEntry.bind('<FocusOut>', pass_out)
        self.passwordEntry.bind('<Return>', enter_login)

        self.forgotten_pass = Button(self.login_frame, text='Forgot your password?', command=self.forgot_func, bg='red')
        self.forgotten_pass.pack(padx=5, pady=5)

        # Set the background of the button to transparent
        self.forgotten_pass.configure(background=style.lookup('TLabelframe', 'background'), fg=style.lookup('TButton', 'foreground'), activebackground=style.lookup('TLabelframe', 'background'))

        self.login_button = ttk.Button(self.login_frame, text='LOG IN', cursor='hand2', style="Accent.TButton", width=20, command=self.login_func)
        self.login_button.pack(padx=5, pady=5, fill='x')

        self.quitButton = ttk.Button(self.login_frame, text='QUIT', cursor='hand2', style="Accent.TButton", command=self.close_win)
        self.quitButton.pack(padx=5, pady=5, fill='x')

    def forgot_func(self):
        self.redirect_forgot_window()

    def login_func(self):
        # getting form data
        uname = self.logged_user_name.get()
        pwd = self.password.get()

        if uname == '' or uname == "User Name *" or pwd == '' or pwd == 'Password *':
            messagebox.showinfo("Warning", "All fields are required!!!")

        else:
            try:
                # open database
                conn = sqlite3.connect(f"{self.path}database/AI_Designer.db")
                # select query
                cursor = conn.execute('SELECT EMP_NAME, DEPARTMENT, ROLE, CODE, THEME from ADMIN where USERNAME=? and PASSWORD=?', (uname, pwd))
                row = cursor.fetchone()
                cursor = conn.execute('SELECT * from holiday_list where YEAR=?', (2023,))
                shared_variable.holidays = cursor.fetchall()[0]
                conn.close()

                # fetch data
                if not row:
                    messagebox.showinfo("Warning", "Wrong username or password!!!")

                else:
                    un_input = self.logged_user_name.get()
                    name = row[0]
                    # Access and modify the shared variables
                    shared_variable.user_name = row[0]
                    shared_variable.user_emp_id = self.logged_user_name.get()
                    shared_variable.department = row[1]
                    shared_variable.role = row[2]
                    shared_variable.initial = row[3]
                    shared_variable.theme = row[4]

                    try:
                        today_date = datetime.now().strftime('%d/%m/%Y')
                        start_time = datetime.now().time()

                        if start_time < time(7, 5):
                            shift = 'F'
                            shift_in = time(7, 0)
                            shift_out = time(15, 15)
                            lc = None
                            remark = None
                        elif time(7, 5) < start_time < time(8, 0):
                            shift = 'F'
                            shift_in = time(7, 0)
                            shift_out = time(15, 15)
                            lc = 'YES'
                            remark = None
                        elif time(8, 0) < start_time < time(9, 5):
                            shift = 'G'
                            shift_in = time(9, 0)
                            shift_out = time(17, 30)
                            lc = None
                            remark = None
                        elif time(9, 5) < start_time < time(14, 5):
                            shift = 'G'
                            shift_in = time(9, 0)
                            shift_out = time(17, 30)
                            lc = 'YES'
                            remark = None
                        elif time(14, 5) < start_time < time(15, 20):
                            shift = 'S'
                            shift_in = time(15, 15)
                            shift_out = time(23, 15)
                            lc = None
                            remark = None
                        elif time(15, 20) < start_time < time(16, 0):
                            shift = 'S'
                            shift_in = time(15, 15)
                            shift_out = time(23, 15)
                            lc = 'YES'
                            remark = None
                        else:
                            shift = None
                            shift_in = None
                            shift_out = None
                            lc = None
                            remark = 'Night shift is not in design department,'

                        conn_log = sqlite3.connect(f"{self.path}database/applicationlogDb.db")
                        cursor_log = conn_log.cursor()
                        cursor_log.execute(f'''CREATE TABLE IF NOT EXISTS "{un_input}" (
                                    "Date"	TEXT,
                                    "Designer_Code"	TEXT,
                                    "Designer_Name"	TEXT,
                                    "Application_Start_Time"	TEXT,
                                    "Application_Close_Time"	TEXT,
                                    "Shift"	TEXT,
                                    "Shift_In_Time"	TEXT,
                                    "Shift_Out_Time"	TEXT,
                                    "Late_Coming"	TEXT,
                                    "Early_Going"	TEXT,
                                    "Remark"	TEXT
                                )''')

                        cursor_log.execute(f'''SELECT Application_Start_Time, Remark FROM "{un_input}" WHERE Date=?''', (today_date,))
                        result = cursor_log.fetchone()

                        if result:
                            old_login = result[0]
                            old_login_time = datetime.strptime(old_login, "%H:%M:%S.%f").strftime("%H:%M:%S.%f")
                            old_remark = result[1]

                            if old_remark:
                                new_remark = f'{old_remark}\nPrevious login time is {old_login_time}.'
                            else:
                                new_remark = f'Previous login time is {old_login_time}.'

                            messagebox.showinfo("Already Login!",
                                                f"You have record of previous login time at {old_login_time}.\n"
                                                f"Please avoid frequent login & logout in this application.\n"
                                                f"Keep application open till your shift end for smother functioning.\n"
                                                f"You can Minimize application if you want to do other activities.")
                            cursor_log.execute(f'''UPDATE "{un_input}" set Application_Start_Time=?, Remark=? where Date=?''', (str(start_time), new_remark, today_date))
                        else:
                            cursor_log.execute(f'''INSERT INTO "{un_input}" (Date, Designer_Code, Designer_Name, 
                                                                Application_Start_Time, Shift, Shift_In_Time, Shift_Out_Time,
                                                                Late_Coming, Remark) VALUES (?,?,?,?,?,?,?,?,?)''',
                                               (today_date, un_input, name, str(start_time), shift, str(shift_in), str(shift_out), lc, remark,))
                        conn_log.commit()
                        conn_log.close()
                        shared_variable.shift = shift
                    except Exception as e:
                        messagebox.showerror("Error!", f"Error due to {str(e)}")

                    style = Style(theme=shared_variable.theme)
                    self.redirect_home_window()

            except Exception as e:
                messagebox.showerror("Error!", f"Error due to {str(e)}")

    @staticmethod
    def redirect_home_window():
        department = shared_variable.department
        if department == "Container Design":
            messagebox.showinfo("Successful!", "Login successful to Container Design.")
            new_win = container_design_home_page.ContainerDesignHome()
            root.withdraw()  # hide the login window
            new_win.wait_window()  # wait for the new window to be closed
            root.destroy()  # destroy the login window
        elif department == "Mold Design":
            messagebox.showinfo("Successful!", "Login successful to Mold Design.")
            new_win = mold_home_page.MoldDesignHome()
            root.withdraw()  # hide the login window
            new_win.wait_window()  # wait for the new window to be closed
            root.destroy()  # destroy the login window
        else:
            messagebox.showerror("Error!", "If difficulty in login then please contact admin.")

    @staticmethod
    def redirect_forgot_window():
        forgotpass_page.ForgotPass()

    @staticmethod
    def close_win():
        root.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title("Login Window")
    x_coordinate = int((root.winfo_screenwidth() / 2) - (286 / 2))
    y_coordinate = int((root.winfo_screenheight() / 2) - (372 / 2))
    root.geometry("+{}+{}".format(x_coordinate, y_coordinate))

    style = Style(theme='flatly')

    app = App(root)
    app.pack(expand=True)

    root.mainloop()
