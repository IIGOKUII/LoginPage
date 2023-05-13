from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import os
from datetime import date, datetime, timedelta
from tkcalendar import DateEntry, Calendar
from dateutil.rrule import rrule, DAILY
from shared_var import shared_variable


class leavePage(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.update()
        self.title("Leave Application")
        self.focus_force()
        self.grab_set()
        self.resizable(FALSE,FALSE)
 
        self.minsize(self.winfo_width(), self.winfo_height())
        x_cordinate = int((self.winfo_screenwidth() / 5) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 5) - (self.winfo_height() / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

        self.leavefrom = StringVar()
        self.leaveto = StringVar()
        self.selectid = StringVar()
        self.totalleaves = StringVar()
        self.leavetype = StringVar()
        self.leavereason = StringVar()
        self.leave = StringVar()

        self.username = str(self.get_user())

        self.path = shared_variable.path

        def select_leave_date(entryfield, arg, pos):
            my_w_child = Toplevel(self)
            my_w_child.grab_set()
            x = arg.winfo_rootx()
            y = arg.winfo_rooty()+40
            my_w_child.geometry(f"250x230+{x}+{y}")
            # my_w_child.geometry("250x220")
            my_w_child.title("Calender")

            def setdate():
                entryfield.delete(0, END)
                entryfield.insert(0, format(cal.selection_get(),"%d/%m/%Y"))
                my_w_child.destroy()
                self.grab_set()
            def closecal():
                entryfield.unbind('<FocusIn>')
                my_w_child.destroy()
                self.grab_set()

            cal = Calendar(my_w_child, selectmode='day')
            cal.grid(row=0, column=0, columnspan=2)

            submit_btn = ttk.Button(my_w_child, text="Submit", style="Accent.TButton", command=setdate)
            submit_btn.grid(row=1, column=0)

            close_btn = ttk.Button(my_w_child, text="Close", style="Accent.TButton", command=closecal)
            close_btn.grid(row=1, column=1)

        # Define a function for switching the frames
        def change_to_apply_leave():
            self.apply_leave_frame.pack(side='left', fill='y', padx=10, pady=10)
            self.viewleaveframe.pack_forget()
            self.cancelleaveframe.pack_forget()
            self.forapprovalleaveframe.pack_forget()

        def change_to_view_leave():
            self.viewleaveframe.pack(side='left',fill='y', padx=10, pady=10)
            self.apply_leave_frame.pack_forget()
            self.cancelleaveframe.pack_forget()
            self.forapprovalleaveframe.pack_forget()
            self.clear_all_from_viewleavetree()
            self.place_tree_data(self.totalleaves_Tree, self.get_all_leave_data())
            

        def change_to_cancel_leave():
            self.cancelleaveframe.pack(side='left',fill='y', padx=10, pady=10)
            self.apply_leave_frame.pack_forget()
            self.viewleaveframe.pack_forget()
            self.forapprovalleaveframe.pack_forget()           
            self.clear_all_from_canceltree()
            self.place_tree_data(self.pendingleaves_Tree, self.get_for_cancel_leave_data())
            self.cancel_leave.config(command=self.cancel_leave_bydesigner)

        def change_to_for_approval_leave():
            self.forapprovalleaveframe.pack(side='left',fill='y', padx=10, pady=10)
            self.apply_leave_frame.pack_forget()
            self.viewleaveframe.pack_forget()
            self.cancelleaveframe.pack_forget()
            self.clear_all_from_approvetree()
            self.place_tree_data(self.approvalleaves_Tree, self.get_pendingforapproval_leave_data())
            self.cancel_leave_from_approve.config(command=self.cancel_leave_byadmin)

        def leavefor(event):
            if self.leave.get() == "Half Day":
                self.leaveto.set(datetime.now().strftime('%d/%m/%Y'))
                self.to_date_lbm.pack_forget()
            else:
                self.to_date_lbm.pack(after=self.from_date_lbm ,padx=5, pady=5)

        def get_leavedays():
            start_date = datetime.strptime(self.leavefrom.get(), '%d/%m/%Y')
            end_date = datetime.strptime(self.leaveto.get(), '%d/%m/%Y')
            year1 = start_date.year
            year2 = end_date.year

            def allsundays(year):
                d = date(year, 1, 1)                    # January 1st
                d += timedelta(days = 6 - d.weekday())  # First Sunday
                while d.year == year:
                    yield d
                    d += timedelta(days = 7)
 
            listofsundays = [] # list of all sundays
            for d in allsundays(2023):
                listofsundays.append(d.strftime('%d/%m/%Y'))
            # print(listofsundays)

            if year1 == year2:
                for d in allsundays(year1):
                    listofsundays.append(d.strftime('%d/%m/%Y'))
            else:
                for d in allsundays(year1):
                    listofsundays.append(d.strftime('%d/%m/%Y'))
                for d1 in allsundays(year2):    
                    listofsundays.append(d1.strftime('%d/%m/%Y'))

            leavedayslist=[]

            def get_holidaylist():
                with open(f'{self.path}database/holidaylist.txt', 'r', encoding="utf8") as inFile:
                    newholidays=[line.strip()for line in inFile] 
                return newholidays 
            holidays=get_holidaylist()


            all_days = (start_date + timedelta(idx + 1)
                    for idx in range((end_date - start_date).days))
            
            # iterating over the dates
            for d in rrule(DAILY, dtstart=start_date, until=end_date):
                leavedayslist.append(d.strftime('%d/%m/%Y'))
   

            nosofleavedaysapplied = len(leavedayslist)
            # print("Total days in between :" + str(nosofleavedaysapplied))

            res = len(set(leavedayslist) & set(holidays))
            res1 = len(set(leavedayslist) & set(listofsundays))

            if self.leave.get() == 'Half Day':
                applieddays = 0.5
                self.leaveto.set(self.leavefrom.get())
                Leave_days_list = start_date.strftime('%d/%m/%Y')
            else:
                applieddays = nosofleavedaysapplied-res-res1
                Leave_days_list = ' '.join([str(elem) for elem in leavedayslist])   

            # print("total applied days :" + str(applieddays))
            self.totalleaves.set("Total days of applied leave :"+str(applieddays))
            currentDateTime = datetime.now()
            Leave_Applied_on = str(currentDateTime.strftime('%d/%m/%Y %I:%M:%S %p'))
            if datetime.strptime(self.leavefrom.get(), '%d/%m/%Y') >= datetime.strptime(Leave_Applied_on, '%d/%m/%Y %I:%M:%S %p'):
                self.leavetype.set('PL')
            else:
                self.leavetype.set('UL')

            if self.leavefrom.get() == "" or self.leavefrom.get() == "From Date *" or self.leaveto.get() == "" or self.leaveto.get() == "To Date *":
                messagebox.showerror("Error!", "Please fill the all entry field correctly")       
            else:
                try:
                    conn = sqlite3.connect(f"{self.path}database/leaveDb.db")
                    cur = conn.cursor()
                    cur.execute('''INSERT INTO leavedatabase (User_ID,From_Date,To_Date,Days,Leave_For,Leave_Status,Leave_Type,Reason,Leave_Applied_on,Leave_Days) VALUES (?,?,?,?,?,?,?,?,?,?)''',
                            (self.username,self.leavefrom.get(),self.leaveto.get(),applieddays,self.leave.get(),'Pending',self.leavetype.get(),self.leavereason.get(),Leave_Applied_on,Leave_days_list))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Successful", "Leave applied successfully", parent=self)

                except Exception as er:
                    messagebox.showerror("Error!", f"{er}", parent=self)
            self.rest_aplly_leave_form()

        self.leavefram = ttk.LabelFrame(self, text="Menu Bar", width=250)
        self.leavefram.pack(side='left', padx=5, pady=5, fill='both')

        # self.treeScroll1 = ttk.Scrollbar(self.leavefram)
        # self.treeScroll1.pack(side='right', fill='y')

        self.apply_leave_btn = ttk.Button(self.leavefram, text='Apply Leave',cursor='hand2', style="Accent.TButton", width=20,command=change_to_apply_leave)
        self.apply_leave_btn.pack(padx=5, pady=5)

        self.view_leave_btn = ttk.Button(self.leavefram, text='View Leave',cursor='hand2', style="Accent.TButton", width=20,command=change_to_view_leave)
        self.view_leave_btn.pack(padx=5, pady=5)

        self.cancel_leave_btn = ttk.Button(self.leavefram, text='Cancel Leave',cursor='hand2', style="Accent.TButton", width=20,command=change_to_cancel_leave)
        self.cancel_leave_btn.pack(padx=5, pady=5)

        if self.username == '1389':
            self.approve_leave_btn = ttk.Button(self.leavefram, text='Pending For Approval',cursor='hand2', style="Accent.TButton", width=20,command=change_to_for_approval_leave)
            self.approve_leave_btn.pack(padx=5, pady=5)
        else:
            pass

        self.exit_btn = ttk.Button(self.leavefram, text='Exit',cursor='hand2', style="Accent.TButton", width=20, command=self.exit_win)
        self.exit_btn.pack(padx=5, pady=5)


        self.apply_leave_frame = ttk.LabelFrame(self, text='Fill below details')
        self.viewleaveframe = ttk.LabelFrame(self, text='Total applied leaves')
        self.cancelleaveframe = ttk.LabelFrame(self, text='Applied Leaves')
        self.forapprovalleaveframe = ttk.LabelFrame(self, text='Pending for approval')

        ### data in apply_leave_frame ######
        self.leave_for_lbm = ttk.LabelFrame(self.apply_leave_frame, text='''Leave for:''')
        self.leave_for_lbm.pack(padx=5, pady=5)

        self.leave_combo = ttk.Combobox(self.leave_for_lbm, state="readonly", textvariable= self.leave, width=25, value=('Full Day', 'Half Day'))
        self.leave_combo.bind('<<ComboboxSelected>>', leavefor)
        self.leave_combo.pack(padx=5, pady=5)

        self.from_date_lbm = ttk.LabelFrame(self.apply_leave_frame, text='''From Date:''')
        self.from_date_lbm.pack(padx=5, pady=5)

        def fromdate_in(event):
            if self.fromdateEntry.get() == 'From Date *':
                self.fromdateEntry.delete(0, END)
                self.fromdateEntry.bind('<1>', select_leave_date(self.fromdateEntry, self.fromdateEntry,self.from_date_lbm))
        def fromdate_out(event):
            if self.fromdateEntry.get() == '':
                self.fromdateEntry.insert(0, 'From Date *')
            self.fromdateEntry.bind('<FocusIn>',fromdate_in)

        
        self.fromdateEntry = ttk.Entry(self.from_date_lbm, textvariable=self.leavefrom, width=20)
        self.fromdateEntry.pack(padx=5, pady=5)
        self.fromdateEntry.insert(0, 'From Date *')
        self.fromdateEntry.bind('<FocusIn>', fromdate_in)
        self.fromdateEntry.bind('<FocusOut>', fromdate_out)



        self.to_date_lbm = ttk.LabelFrame(self.apply_leave_frame, text='''To Date:''')
        self.to_date_lbm.pack(padx=5, pady=5)

        def todate_in(event):
            if self.todateEntry.get() == 'To Date *':
                self.todateEntry.delete(0, END)
                self.todateEntry.bind('<1>', select_leave_date(self.todateEntry, self.todateEntry, self.to_date_lbm))
        def todate_out(event):
            if self.todateEntry.get() == '':
                self.todateEntry.insert(0, 'To Date *')
            self.todateEntry.bind('<FocusIn>',todate_in)

   
        self.todateEntry = ttk.Entry(self.to_date_lbm, textvariable=self.leaveto, width=20)
        self.todateEntry.pack(padx=5, pady=5)
        self.todateEntry.insert(0, 'To Date *')
        self.todateEntry.bind('<FocusIn>', todate_in)
        self.todateEntry.bind('<FocusOut>', todate_out)
        
        def leave_reason_in(event):
            if self.reason_Entry.get() == 'Leave reason *':
                self.reason_Entry.delete(0, END)
        def leave_reason_out(event):
            if self.reason_Entry.get() == '':
                self.reason_Entry.insert(0, 'Leave reason *')

        self.reason_Entry = ttk.Entry(self.apply_leave_frame, textvariable=self.leavereason, width=25)
        self.reason_Entry.pack(padx=5, pady=5)
        self.reason_Entry.insert(0, 'Leave reason *')
        self.reason_Entry.bind('<FocusIn>', leave_reason_in)
        self.reason_Entry.bind('<FocusOut>', leave_reason_out)
        

        self.total_days_lbm = ttk.Label(self.apply_leave_frame, textvariable=self.totalleaves)
        self.total_days_lbm.pack(padx=5, pady=5)

        self.apply_leave = ttk.Button(self.apply_leave_frame, text='Submit', style="Accent.TButton", width=20, cursor='hand2', command=get_leavedays)
        self.apply_leave.pack(padx=5, pady=5)

        ##### data in viewleaveframe ######
        # Scrollbar
        self.scrollbar_y_viewleaveframe = ttk.Scrollbar(self.viewleaveframe)
        self.scrollbar_y_viewleaveframe.pack(side="right", fill="y")

        # Treeview
        self.totalleaves_Tree = ttk.Treeview(self.viewleaveframe, selectmode="extended")
        self.totalleaves_Tree.pack(padx=10, pady=10)
        self.scrollbar_y_viewleaveframe.config(command=self.totalleaves_Tree.yview)

        ##### data in cancelleaveframe ######
        self.frame_for_button_in_cancelframe = ttk.Frame(self.cancelleaveframe)
        self.frame_for_button_in_cancelframe.pack(side='top', fill='x')
        self.cancel_leave = ttk.Button(self.frame_for_button_in_cancelframe, text='Cancel Leave', style="Accent.TButton", width=20, cursor='hand2') #, command=self.cancel_leave_fromlist(self.pendingleaves_Tree))
        self.cancel_leave.pack(side='left', padx=5, pady=5)

        # Scrollbar
        self.scrollbar_cancelleaveframe = ttk.Scrollbar(self.cancelleaveframe)
        self.scrollbar_cancelleaveframe.pack(side="right", fill="y")

        # Treeview
        self.pendingleaves_Tree = ttk.Treeview(self.cancelleaveframe, selectmode="extended")
        self.pendingleaves_Tree.pack(padx=10, pady=10)
        self.scrollbar_cancelleaveframe.config(command=self.pendingleaves_Tree.yview)


        ##### data in approvalleaveframe ######
        self.frame_for_button_in_approveframe = ttk.Frame(self.forapprovalleaveframe)
        self.frame_for_button_in_approveframe.pack(side='top', fill='x')
        self.approve_leave = ttk.Button(self.frame_for_button_in_approveframe, text='Approve Leave', width=20, cursor='hand2', style="Accent.TButton", command=self.approve_leave_fromlist)
        self.approve_leave.pack(side='left', padx=5, pady=5)
        self.cancel_leave_from_approve = ttk.Button(self.frame_for_button_in_approveframe, text='Cancel Leave', width=20, cursor='hand2', style="Accent.TButton") #, command=self.cancel_leave_fromlist(self.approvalleaves_Tree))
        self.cancel_leave_from_approve.pack(side='left',padx=5, pady=5)

        # Scrollbar
        self.scrollbar_approvalleaveframe = ttk.Scrollbar(self.forapprovalleaveframe)
        self.scrollbar_approvalleaveframe.pack(side="right", fill="y")

        # Treeview
        self.approvalleaves_Tree = ttk.Treeview(self.forapprovalleaveframe, selectmode="extended")
        self.approvalleaves_Tree.pack(padx=10, pady=10)
        self.scrollbar_approvalleaveframe.config(command=self.approvalleaves_Tree.yview)

    def exit_win(self):
        self.destroy()

    # Define a function to clear all the items present in Treeview
    def clear_all_from_viewleavetree(self):
        for item in self.totalleaves_Tree.get_children():
            self.totalleaves_Tree.delete(item)

    def clear_all_from_canceltree(self):
        for item in self.pendingleaves_Tree.get_children():
            self.pendingleaves_Tree.delete(item)

    def clear_all_from_approvetree(self):
        for item in self.approvalleaves_Tree.get_children():
            self.approvalleaves_Tree.delete(item)

    def approve_leave_fromlist(self):
        selectedItem = self.approvalleaves_Tree.selection()[0]
        selectedID = self.approvalleaves_Tree.item(selectedItem)['values'][0]
        self.selectid.set(selectedID)
        remark = 'Approved By ' + self.username
        conn = sqlite3.connect(f"{self.path}database/leaveDb.db")
        cursor = conn.cursor()
        cursor.execute("update leavedatabase set Leave_Status=?, Leave_Remark=? where App_ID=?", ('Approved',remark,self.selectid.get()))
        conn.commit()
        messagebox.showinfo("Successful", '''Leave status changed to 'Approved'.''', parent=self)
        conn.close()
        self.clear_all_from_canceltree()
        self.place_tree_data(self.pendingleaves_Tree, self.get_for_cancel_leave_data())
        self.clear_all_from_viewleavetree()
        self.place_tree_data(self.totalleaves_Tree, self.get_all_leave_data())
        self.clear_all_from_approvetree()
        self.place_tree_data(self.approvalleaves_Tree, self.get_pendingforapproval_leave_data())

    def cancel_leave_bydesigner(self):
        selectedItem = self.pendingleaves_Tree.selection()[0]
        selectedID = self.pendingleaves_Tree.item(selectedItem)['values'][0]
        self.selectid.set(selectedID)
        remark = 'Canceled By ' + self.username

        conn = sqlite3.connect(f"{self.path}database/leaveDb.db")
        cursor = conn.cursor()
        cursor.execute("update leavedatabase set Leave_Status=?, Leave_Remark=? where App_ID=?", ('Canceled',remark,self.selectid.get()))
        conn.commit()
        messagebox.showinfo("Successful", '''Leave status changed to 'Canceled'.''', parent=self)
        conn.close()
        self.clear_all_from_canceltree()
        self.place_tree_data(self.pendingleaves_Tree, self.get_for_cancel_leave_data())
        self.clear_all_from_viewleavetree()
        self.place_tree_data(self.totalleaves_Tree, self.get_all_leave_data())
        self.clear_all_from_approvetree()
        self.place_tree_data(self.approvalleaves_Tree, self.get_pendingforapproval_leave_data())

    def cancel_leave_byadmin(self):
        selectedItem = self.approvalleaves_Tree.selection()[0]
        selectedID = self.approvalleaves_Tree.item(selectedItem)['values'][0]
        self.selectid.set(selectedID)
        remark = 'Canceled By ' + self.username

        conn = sqlite3.connect(f"{self.path}database/leaveDb.db")
        cursor = conn.cursor()
        cursor.execute("update leavedatabase set Leave_Status=?, Leave_Remark=? where App_ID=?", ('Canceled',remark,self.selectid.get()))
        conn.commit()
        messagebox.showinfo("Successful", '''Leave status changed to 'Canceled'.''', parent=self)
        conn.close()
        self.clear_all_from_canceltree()
        self.place_tree_data(self.pendingleaves_Tree, self.get_for_cancel_leave_data())
        self.clear_all_from_viewleavetree()
        self.place_tree_data(self.totalleaves_Tree, self.get_all_leave_data())
        self.clear_all_from_approvetree()
        self.place_tree_data(self.approvalleaves_Tree, self.get_pendingforapproval_leave_data())


    def get_all_leave_data(self):
        conn = sqlite3.connect(f"{self.path}database/leaveDb.db")
        cursor = conn.cursor()
        cursor.execute('SELECT App_ID,User_ID,From_Date,To_Date,Days,Leave_For,Leave_Status,Leave_Type,Reason,Leave_Applied_on from leavedatabase where User_ID=? and Leave_Status<>?', (self.username,'Pending'))
        fetch = cursor.fetchall()
        conn.close()
        headersname = [description[0] for description in cursor.description]
        return fetch, headersname
    
    def get_for_cancel_leave_data(self):
        conn = sqlite3.connect(f"{self.path}database/leaveDb.db")
        cursor = conn.cursor()
        cursor.execute('SELECT App_ID,User_ID,From_Date,To_Date,Days,Leave_For,Leave_Status,Leave_Type,Reason,Leave_Applied_on from leavedatabase where User_ID=? and Leave_Status=?', (self.username, 'Pending'))
        fetch = cursor.fetchall()
        conn.close()
        headersname = [description[0] for description in cursor.description]
        return fetch, headersname   
    
    def get_pendingforapproval_leave_data(self):
        conn = sqlite3.connect(f"{self.path}database/leaveDb.db")
        cursor = conn.cursor()
        cursor.execute('SELECT App_ID,User_ID,From_Date,To_Date,Days,Leave_For,Leave_Status,Leave_Type,Reason,Leave_Applied_on from leavedatabase where Leave_Status=?', ('Pending',))
        fetch = cursor.fetchall()
        conn.close()
        headersname = [description[0] for description in cursor.description]
        return fetch, headersname

    def place_tree_data(self, treeview, database):
        fetch, headersname = database
        if fetch == []:
            pass
        else:
            firstlist = fetch[0]
            lengthofdata = []
            for v in firstlist:
                try:
                    l = len(v)
                    lengthofdata.append(l)
                except:
                    lengthofdata.append(1)    

            lenthofheaderlist = []
            for i in headersname:
                l = len(i)
                lenthofheaderlist.append(l)

            # Treeview
            treeview.config(columns=(headersname))
            
            for data in fetch:
                treeview.insert('', 'end', values=(data))
            
            # Create an iterator object using the iter function
            iterator = iter(headersname)
            
            # Use the next function to retrieve the elements of the iterator
            # Using enumerate() 
            for i, val in enumerate(headersname):
                column=('#'+str(i))
                w=len(val)
                treeview.column('#0', stretch=NO, minwidth=0, width=0)
                treeview.column(column, stretch=NO, minwidth=0, width=100)
                # treeview.bind("<<TreeviewSelect>>", getvalue)

                try:
                    while True:
                        element = next(iterator)
                        treeview.heading(element, text=element, anchor=W)
                        
                except StopIteration:
                    pass           

    def get_user(self):
        try:
            uname = shared_variable.user_emp_id
        except:
            uname = 'Guest'
        return uname

    def rest_aplly_leave_form(self):
        self.fromdateEntry.delete(0,END)
        self.fromdateEntry.insert(0, 'From Date *')
        self.todateEntry.delete(0,END)
        self.todateEntry.insert(0, 'To Date *')
        self.reason_Entry.delete(0, END)
        self.reason_Entry.insert(0, 'Leave reason *')
        self.leave.set('')
        self.totalleaves.set('')

