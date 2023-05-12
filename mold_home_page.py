from tkinter import *
from methods import get_designer_plan, get_designer_working_plan, get_birthday, update_status, plan_by_mold
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
# import leave_page
import new_mold_entry
# import mold_replanning
import mold_planning
import manage_account_page
# import mold_short_plan
# import mold_plan
from shared_var import shared_variable
from datetime import datetime
# import subprocess


class MoldDesignHome(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)

        self.title("Mold Design Home")
        self.state('zoomed')
        self.protocol("WM_DELETE_WINDOW", self.disable_event)

        # Set window at center
        self.minsize(self.winfo_width(), self.winfo_height())

        self.path = shared_variable.path
        self.MDShdb = f"{self.path}database/MDShdb.db"
        self.initial = shared_variable.initial
        self.leave_path = f"{self.path}database/leaveDb.db"

        # Variables
        self.designer_name = StringVar()
        self.designer_mail = StringVar()
        self.work_hours = StringVar()
        self.changed_status = StringVar()
        self.start_delay = StringVar()
        self.quality_remark = StringVar()
        self.request_id_for_data_update = StringVar()
        self.nos_for_approval = IntVar()
        self.nos_for_checking = IntVar()
        self.nos_for_designing = IntVar()
        self.logged_user_name = StringVar()
        self.logged_user_name.set(self.get_user())
        self.welcome_lab = StringVar()
        self.welcome_lab.set("Welcome " + str(shared_variable.user_name))
        self.activity = StringVar()
        self.designer_ini = StringVar()
        self.designer_ini.set(shared_variable.initial)
        self.int_status = IntVar()

        def get_plan_mold(event):
            try:
                self.new_entry_details.pack_forget()
            except AttributeError:
                pass

            try:
                selected_item = self.working_projects_tree.selection()[0]
                mold_no = self.working_projects_tree.item(selected_item)['values'][1]
            except IndexError:
                try:
                    selected_item = self.designer_projects_tree.selection()[0]
                    mold_no = self.designer_projects_tree.item(selected_item)['values'][1]
                except IndexError:
                    return

            try:
                df_project_mold = plan_by_mold(self.MDShdb, mold_no)

                # Frame New Entry Details

                self.new_entry_details = ttk.LabelFrame(self.center_frame, text="Mold Plan Details", width=750, height=250)
                self.new_entry_details.pack(side='top', padx=5, anchor="nw")

                columns1 = [('Request_ID', 80), ('Mold_No', 100), ('Start_Date', 100), ('Designer', 75), ('Activity', 100), ('Days', 75), ('Status', 175)]
                self.mold_plan_tree = ttk.Treeview(self.new_entry_details, columns=[col[0] for col in columns1], show='headings')

                for col in columns1:
                    self.mold_plan_tree.column(col[0], width=col[1], anchor=CENTER)
                    self.mold_plan_tree.heading(col[0], text=col[0])

                self.mold_plan_tree.place(x=10, y=10, width=715, height=210)

                self.scrollbar_v = ttk.Scrollbar(self.new_entry_details, orient='vertical', command=self.mold_plan_tree.yview)
                self.scrollbar_v.place(x=725, y=10, width=20, height=210)

                self.mold_plan_tree.configure(yscrollcommand=self.scrollbar_v.set)

                # Insert the data into the TreeView
                for i, row in df_project_mold.iterrows():
                    values = tuple(row.values)
                    self.mold_plan_tree.insert("", "end", text=i, values=values)
            except ValueError:
                pass

        def refresh():
            self.clear_all_tree()
            self.get_designer_project_list()
            self.get_designer_working_project_list()
            try:
                self.new_entry_details.pack_forget()
            except AttributeError:
                pass

# Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

# Create 3 Frame's for UI
        self.left_frame = ttk.LabelFrame(self, text='Logged User', width=200, padding=(5, 5))
        self.left_frame.pack(side='left', fill='y')

        self.right_frame = ttk.LabelFrame(self, text='Notice Board', padding=(5, 5))
        self.right_frame.pack(side='right', fill='both', padx=5)

        self.center_frame = ttk.LabelFrame(self, text='Dashboard', padding=(5, 5))
        self.center_frame.pack(side='left', fill='both', padx=5, expand=1)

        def work_hrs_in(event):
            if self.work_hours_entry.get() == 'Work hrs *':
                self.work_hours_entry.delete(0, END)

        def work_hrs_out(event):
            if self.work_hours_entry.get() == '':
                self.work_hours_entry.insert(0, 'Work hrs *')

# Create a CENTER INSIDE UP Frame
        self.center_in_up_frame = Frame(self.center_frame, height=40)
        self.center_in_up_frame.pack(side='top', fill='both', padx=5)

        self.wlcom_lebal = Label(self.center_in_up_frame, text=self.welcome_lab.get(), font=("Comic Sans MS", 12, "bold"), fg="ivory")
        self.wlcom_lebal.place(x=10, y=10)

        # Create a button with the refresh symbol as text
        self.refresh_btn = ttk.Button(self.center_in_up_frame, text="\u27F3", command=refresh)
        self.refresh_btn.place(x=1000, y=5, width=50)

# Create a CENTER INSIDE Frame

        self.center_in_frame = Frame(self.center_frame, width=1200, height=250)
        self.center_in_frame.pack(side='top', fill='both', padx=5)

# Create Label frame for designers work tree view
        self.working_projects_frame = ttk.LabelFrame(self.center_in_frame, text="Working project")
        self.working_projects_frame.place(x=5, y=10, width=520, height=240)

        # Tree view for designer's projects
        self.scrollbar_working_projects_frame = ttk.Scrollbar(self.working_projects_frame)
        self.scrollbar_working_projects_frame.place(x=505, y=10, width=10, height=205)

        columns = [('Request_ID', 60), ('Mold_No', 85), ('Activity', 70), ('Start_Date', 70), ('End_Date', 70), ('Status', 70)]
        self.working_projects_tree = ttk.Treeview(self.working_projects_frame, columns=[col[0] for col in columns], show='headings')
        for col in columns:
            self.working_projects_tree.column(col[0], width=col[1], anchor=CENTER)
            self.working_projects_tree.heading(col[0], text=col[0])
        self.working_projects_tree.place(x=5, y=10, width=495, height=205)
        self.working_projects_tree.config(yscrollcommand=self.scrollbar_working_projects_frame.set)
        self.scrollbar_working_projects_frame.config(command=self.working_projects_tree.yview)
        self.working_projects_tree.bind("<Double-1>", get_plan_mold)
        self.get_designer_working_project_list()

# Create Label frame for designers work tree view
        self.projects_frame = ttk.LabelFrame(self.center_in_frame, text="Planned work for you")
        self.projects_frame.place(x=535, y=10, width=520, height=240)

        # Tree view for designer's projects
        self.scrollbar_projects_frame = ttk.Scrollbar(self.projects_frame)
        self.scrollbar_projects_frame.place(x=505, y=10, width=10, height=205)

        self.designer_projects_tree = ttk.Treeview(self.projects_frame, columns=[col[0] for col in columns], show='headings')
        for col in columns:
            self.designer_projects_tree.column(col[0], width=col[1], anchor=CENTER)
            self.designer_projects_tree.heading(col[0], text=col[0])
        self.get_designer_project_list()
        self.designer_projects_tree.place(x=5, y=10, width=495, height=205)
        self.designer_projects_tree.config(yscrollcommand=self.scrollbar_projects_frame.set)
        self.scrollbar_projects_frame.config(command=self.designer_projects_tree.yview)
        self.designer_projects_tree.bind("<Double-1>", get_plan_mold)

# Update project work widgets
        self.running_designer_project_edit_frame = Frame(self.center_frame, height=50)
        self.running_designer_project_edit_frame.pack(padx=5, pady=5, fill='both')

        self.running_designer_project_edit_button = ttk.Button(self.running_designer_project_edit_frame, text='Change Status', cursor='hand2', style="Accent.TButton", command=self.update_running_project_status)
        self.running_designer_project_edit_button.place(x=10, y=10)

        self.start_status_button = ttk.Button(self.running_designer_project_edit_frame, text='Start Activity', style="Accent.TButton", cursor='hand2', command=self.start_status)
        self.start_status_button.place(x=540, y=10)

        self.update_status_button = ttk.Button(self.running_designer_project_edit_frame, text='Update Status', style="Accent.TButton", cursor='hand2')

        self.delay_start_update_status_button = ttk.Button(self.running_designer_project_edit_frame, text='Start', cursor='hand2', style="Accent.TButton")

        self.cancel_status_button = ttk.Button(self.running_designer_project_edit_frame, text='Cancel Update', style="Accent.TButton", cursor='hand2')

        self.work_hours_entry = ttk.Entry(self.running_designer_project_edit_frame, textvariable=self.work_hours, width=10)
        self.work_hours_entry.insert(0, 'Work hrs *')
        self.work_hours_entry.bind('<FocusIn>', work_hrs_in)
        self.work_hours_entry.bind('<FocusOut>', work_hrs_out)

        self.start_delay_combo = ttk.Combobox(self.running_designer_project_edit_frame, textvariable=self.start_delay, width=17)

        self.quality_remark_combo = ttk.Combobox(self.running_designer_project_edit_frame, textvariable=self.quality_remark, width=25, value=['ALL OK', 'MINOR', 'MODERATE', 'MAJOR'])

# Sub frame of right frame
        self.ba_frame1 = ttk.Frame(self.right_frame, height=250)
        self.ba_frame1.grid(sticky='n', column=1, row=1, padx=5, pady=5)

        self.ba_frame2 = ttk.Frame(self.right_frame, height=250)
        self.ba_frame2.grid(sticky='n', column=1, row=2, padx=5, pady=5)

# Birthday on notice board
        self.happy_birthday_frame = ttk.Frame(self.ba_frame1)
        self.happy_birthday_frame.pack(side='top', padx=5, pady=5)

        self.img_cake = ImageTk.PhotoImage(Image.open(f"{self.path}images/cake.png"))
        self.img_birthday = ImageTk.PhotoImage(Image.open(f"{self.path}images/birthday.png"))

        # Create a Label Widget to display the img_cake
        self.label_cake = Label(self.happy_birthday_frame, image=self.img_cake)
        self.label_cake.grid(column=0, row=0)

        # Create a Label Widget to display the img_birthday
        self.label_birthday = Label(self.happy_birthday_frame, image=self.img_birthday)
        self.label_birthday.grid(column=1, row=0)

# Profile widgets
        self.profile_frame = ttk.LabelFrame(self.left_frame, width=220, padding=(5, 5))
        self.profile_frame.pack()

        self.menu_frame = ttk.LabelFrame(self.left_frame, text="Menu", width=220, padding=(5, 5))
        self.menu_frame.pack(fill='y')

        # Profile photo
        self.profile_img = ImageTk.PhotoImage(file=f'{self.path}images/profile/' + str(self.logged_user_name.get()) + '.png')
        self.profile_pic_lab = ttk.Label(self.profile_frame, image=self.profile_img)
        self.profile_pic_lab.pack(padx=5, pady=5)

        self.edit_profile_button = ttk.Button(self.profile_frame, text='Manage account', cursor='hand2', style="Accent.TButton", command=manage_account_page.EditProfile)
        self.edit_profile_button.pack(pady=5)

# Menu buttons
        if shared_variable.role not in ["PLANNER", "PROGRAMMER", "HEAD"]:
            messagebox.showwarning("WARNING", "You are not authorised for this module")
        else:

            self.new_project_button = ttk.Button(self.menu_frame, text='New Project Entry', cursor='hand2', style="Accent.TButton", width=20, command=new_mold_entry.NewEntry)
            self.new_project_button.pack(pady=5)

            self.project_planning_button = ttk.Button(self.menu_frame, text='Planning New Project', cursor='hand2', style="Accent.TButton", width=20, command=mold_planning.Planning)
            self.project_planning_button.pack(pady=5)

            # self.short_plan_button = ttk.Button(self.menu_frame, text='Short Plan', cursor='hand2', style="Accent.TButton", width=20, command=mold_short_plan.StPlanning)
            # self.short_plan_button.pack(pady=5)
            #
            # self.re_planing_button = ttk.Button(self.menu_frame, text='Re-planning Project', cursor='hand2', style="Accent.TButton", width=20, command=mold_replanning.RePlanning)
            # self.re_planing_button.pack(pady=5)

        # self.codification_button = ttk.Button(self.menu_frame, text='Codification', cursor='hand2', style="Accent.TButton", width=20, command=self.redirect_codification)
        # self.codification_button.pack(pady=5)

        # self.leave_button = ttk.Button(self.menu_frame, text='Leave Planning',
        #                                cursor='hand2', style="Accent.TButton", width=20, command=leave_page.leavePage)
        # self.leave_button.pack(pady=5)

        # self.Complete_plan_button = ttk.Button(self.menu_frame, text='Mold Plan', cursor='hand2', style="Accent.TButton", width=20, command=mold_plan.MoldPlan)
        # self.Complete_plan_button.pack(pady=5)

        # self.molddata_management_button = ttk.Button(self.menu_frame, text='Data to Mold Design', cursor='hand2', width=20, command=self.cmd)
        # self.molddata_management_button.pack(pady=5)

        self.add_button = ttk.Button(self.menu_frame, text='Notice Board', cursor='hand2', style="Accent.TButton", width=20, command=self.noticeboard)
        self.add_button.pack(pady=5)       

        self.quit_button = ttk.Button(self.menu_frame, text='Log Out', style="Accent.TButton",
                                      cursor='hand2', width=20, command=self.logout)
        self.quit_button.pack(pady=5)

# Birthday wish
        names = get_birthday(self.path)
        for name in names:
            self.label_n = Label(self.happy_birthday_frame, text=name[0], font=("Comic Sans MS", 12, "bold"), fg="ivory")
            self.label_n.grid(column=0, row=1, columnspan=2)

    def disable_event(self):
        # Minimize window when press close button
        self.iconify()

    @staticmethod
    def cmd():
        messagebox.showinfo('Thanks for showing interest!', 'We are working on these add-on modules.\nSoon we will activated all functionality.')

    def logout(self):
        # ask the user a yes/no question
        response = messagebox.askquestion("Confirm", "Do you want to close the window?")
        if response == 'yes':
            # close the tkinter window
            self.destroy()

    def noticeboard(self):
        # Check if the Label has been packed
        if self.right_frame.winfo_manager() == "pack":
            self.right_frame.pack_forget()
            self.center_frame.pack_forget()
            self.center_frame.pack(side='left', fill='both', padx=5, expand=1)
        else:
            self.center_frame.pack_forget()
            self.right_frame.pack(side='right', fill='both', padx=5)
            self.center_frame.pack(side='left', fill='both', padx=5, expand=1)

    def get_designer_project_list(self):
        df_project = get_designer_plan(self.MDShdb, self.initial)

        # Insert the data into the TreeView
        for i, row in df_project.iterrows():
            values = tuple(row.values)
            self.designer_projects_tree.insert("", "end", text=i, values=values)

    def get_designer_working_project_list(self):
        df_project = get_designer_working_plan(self.MDShdb, self.initial)

        # Insert the data into the TreeView
        for i, row in df_project.iterrows():
            values = tuple(row.values)
            self.working_projects_tree.insert("", "end", text=i, values=values)

    def update_running_project_status(self):
        try:
            self.working_projects_tree.selection()[0]
        except IndexError:
            messagebox.showinfo("Warning!", '''Select project from the list of project planned for your.''', parent=self)
            return

        def update_status_with_delay():
            res1 = messagebox.askquestion("Info!", "Do you want to change project status?", parent=self)
            if res1 == 'yes':
                if self.start_delay.get() == "":
                    messagebox.showwarning("Warning!", '''Please select delay code before change status.''', parent=self)
                else:
                    update_status(self.MDShdb, self.leave_path, self.initial, enp_id, status_remark, status, req_id=req_id, activity=activity)
                    messagebox.showinfo("Successful", f'''Project status changed to {self.changed_status.get()}.''', parent=self)
                    self.clear_all_tree()
                    self.get_designer_project_list()
                    self.get_designer_working_project_list()
                    self.start_delay_combo.set('')
                    self.start_delay_combo.place_forget()
                    self.delay_start_update_status_button.place_forget()
                    self.cancel_status_button.place_forget()
            else:
                pass

        with open(f"{self.path}database/delaycode.txt", encoding="utf8") as inFile:
            delay_code = [line for line in inFile]

        selected_item = self.working_projects_tree.selection()[0]
        req_id = self.working_projects_tree.item(selected_item)['values'][0]
        activity = self.working_projects_tree.item(selected_item)['values'][2]
        status_old = self.working_projects_tree.item(selected_item)['values'][5]
        planned_end = self.working_projects_tree.item(selected_item)['values'][4]
        enp_id = shared_variable.user_emp_id

        change_status = {
            'In Preform': (4, 'Preform Completed'),
            'In Assembly': (4, 'Assembly Completed'),
            'In Assembly Check': (4, 'Assembly Check Completed'),
            'In Detailing': (4, 'Checking Completed'),
            'In Checking': (4, 'Checking Completed'),
            'In Correction': (4, 'Correction Completed'),
            'In 2nd Check': (4, '2nd Check Completed'),
            'In Issue': (4, 'Issue Completed')
        }
        today_date = datetime.now().strftime("%d-%m-%Y")

        if status_old == "Pause":
            status_remark = f'In {activity}'
            status = 1
        else:
            status_remark = change_status[status_old][1]
            status = change_status[status_old][0]

        if datetime.strptime(today_date, '%d-%m-%Y') > datetime.strptime(planned_end, '%d-%m-%Y') and status_old != "Pause":
            self.start_delay_combo.place(x=130, y=10)
            self.start_delay_combo['values'] = delay_code
            self.delay_start_update_status_button.config(text='Update', command=update_status_with_delay)
            self.delay_start_update_status_button.place(x=280, y=10)
            self.cancel_status_button.place(x=390, y=10)
            self.cancel_status_button.config(command=self.hideentryfields)

            messagebox.showinfo("Delay", f'''Project was planned to end on {planned_end} \nBut it is ending today on {today_date} \nSo please select delay code for delay end.''', parent=self)
        else:
            res = messagebox.askquestion("Info!", "Do you want to change project status?", parent=self)
            if res == 'yes':
                update_status(self.MDShdb, self.leave_path, self.initial, enp_id, status_remark, status, req_id=req_id, activity=activity)
                messagebox.showinfo("Successful", f'''Project status changed to {self.changed_status.get()}.''', parent=self)
                self.clear_all_tree()
                self.get_designer_project_list()
                self.get_designer_working_project_list()
            else:
                pass

    def start_status(self):
        try:
            self.designer_projects_tree.selection()[0]
        except IndexError:
            messagebox.showinfo("Warning!", '''Select project from the list of project planned for your.''', parent=self)
            return

        def update_status_with_delay():
            res1 = messagebox.askquestion("Info!", "Do you want to change project status?", parent=self)
            if res1 == 'yes':
                if self.start_delay.get() == "":
                    messagebox.showwarning("Warning!", '''Please select delay code before change status.''', parent=self)
                else:
                    update_status(self.MDShdb, self.leave_path, self.initial, enp_id, status_remark, status=1, req_id=req_id, activity=activity)
                    messagebox.showinfo("Successful", f'''Project status changed to {self.changed_status.get()}.''', parent=self)
                    self.clear_all_tree()
                    self.get_designer_project_list()
                    self.get_designer_working_project_list()
                    self.start_delay_combo.set('')
                    self.start_delay_combo.place_forget()
                    self.delay_start_update_status_button.place_forget()
                    self.cancel_status_button.place_forget()
            else:
                pass

        with open(f"{self.path}database/delaycode.txt", encoding="utf8") as inFile:
            delay_code = [line for line in inFile]

        selected_item = self.designer_projects_tree.selection()[0]
        req_id = self.designer_projects_tree.item(selected_item)['values'][0]
        activity = self.designer_projects_tree.item(selected_item)['values'][2]
        planned_start = self.designer_projects_tree.item(selected_item)['values'][3]
        enp_id = shared_variable.user_emp_id
        today_date = datetime.now().strftime("%d-%m-%Y")
        status_remark = f'In {activity}'

        if datetime.strptime(today_date, '%d-%m-%Y') > datetime.strptime(planned_start, '%d-%m-%Y'):
            self.start_delay_combo.place(x=650, y=10)
            self.start_delay_combo['values'] = delay_code
            self.delay_start_update_status_button.config(text='Start', command=update_status_with_delay)
            self.delay_start_update_status_button.place(x=800, y=10)
            self.cancel_status_button.place(x=910, y=10)
            self.cancel_status_button.config(command=self.hideentryfields)

            messagebox.showinfo("Delay", f'''Project was planned to start on {planned_start} \nBut it is started today on {today_date} \nso please select delay code for delay start.''', parent=self)
        else:
            res = messagebox.askquestion("Info!", "Do you want to change project status?", parent=self)
            if res == 'yes':
                update_status(self.MDShdb, self.leave_path, self.initial, enp_id, status_remark, status=1, req_id=req_id, activity=activity)
                messagebox.showinfo("Successful", f'''Project status changed to {self.changed_status.get()}.''', parent=self)
                self.clear_all_tree()
                self.get_designer_project_list()
                self.get_designer_working_project_list()
            else:
                pass

    def clear_all_tree(self):
        self.designer_projects_tree.selection_remove(*self.designer_projects_tree.selection())
        for item in self.designer_projects_tree.get_children():
            self.designer_projects_tree.delete(item)

        self.working_projects_tree.selection_remove(*self.working_projects_tree.selection())
        for item in self.working_projects_tree.get_children():
            self.working_projects_tree.delete(item)

    @staticmethod
    def get_user():
        try:
            uname = shared_variable.user_emp_id
        except ValueError:
            uname = shared_variable.user_emp_id
        return uname
        
    def get_refresh_data(self):
        self.clear_all_tree()
        self.get_designer_project_list()
        self.profile_pic_lab.pack_forget()
        self.edit_profile_button.pack_forget()
        self.profile_img = ImageTk.PhotoImage(file='images/profile/' + str(self.logged_user_name.get()) + '.png')
        self.profile_pic_lab.config(image=self.profile_img)
        self.profile_pic_lab.pack(padx=5, pady=5)
        self.edit_profile_button.pack(pady=5)

    def hideentryfields(self):
        self.clear_all_tree()
        self.get_designer_project_list()
        self.get_designer_working_project_list()
        self.start_delay_combo.set('')
        self.start_delay_combo.place_forget()
        self.delay_start_update_status_button.place_forget()
        self.cancel_status_button.place_forget()

    def hold_running_project(self):
        messagebox.showinfo("Warning!", '''Project hold is available for authorized designer.\nPlease contact subsidiary in-charge.''', parent=self)
