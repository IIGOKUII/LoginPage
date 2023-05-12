from tkinter import *
from methods import get_new_entry, get_short_plan, get_complete_plan, get_mold_info, get_mold_info, plan_by_mold
from tkinter import ttk
from tkinter import messagebox
import sqlite3
# from tkcalendar import Calendar
from tkcalendar import Calendar
from datetime import datetime, timedelta
import pandas as pd
from shared_var import shared_variable
import seaborn as sns
import matplotlib.pyplot as plt
from ttkbootstrap import DateEntry
import json


class Planning(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.Activity_start_date = None
        self.title("Mold Planning")
        self.focus_force()
        self.grab_set()
        # self.resizable(FALSE, FALSE)
        self.P_start_date = None
        self.A_start_date = None
        self.AC_start_date = None
        self.D_start_date = None
        self.C_start_date = None
        self.CR_start_date = None
        self.SC_start_date = None
        self.I_start_date = None

# Set Window size and Ser at center
        window_height = 780
        window_width = 1280
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cor = int((screen_width / 2) - (window_width / 2)) - 10
        y_cor = int((screen_height / 2.3) - (window_height / 2))

        self.geometry(f'{window_width}x{window_height}+{x_cor}+{y_cor}')
        self.minsize(int((screen_width / 2)), window_height)

# Variables
        self.path = shared_variable.path
        self.MDShdb = f"{self.path}database/MDShdb.db"
        self.initial = shared_variable.initial
        self.leave_path = f"{self.path}database/leaveDb.db"

        self.cal_date = StringVar()

        self.Activity_var = StringVar()
        self.Y_var = IntVar()
        self.N_var = IntVar()
        self.Activity_day = StringVar()
        self.Activity_end = StringVar()
        self.Activity_designer = StringVar()

        # Difficulty Variable
        self.difficulty = StringVar()

        # Mold Info Variable
        self.info_date = StringVar()
        self.mold_no = StringVar()
        self.customer = StringVar()
        self.machine_type = StringVar()
        self.cav_no = StringVar()
        self.ord_scp = StringVar()
        self.ord_typ = StringVar()
        self.iss_to = StringVar()
        self.zc_var = StringVar()
        self.qmc_var = StringVar()
        self.air_ejt_var = StringVar()
        self.pos_ver = StringVar()
        self.country = StringVar()
        self.bottle_no = StringVar()
        self.req_id = IntVar()
        self.malt = StringVar()
        self.hrtype = StringVar()

        # Combobox Variable
        self.mcModel = StringVar()
        self.DegnModel = StringVar()
        self.month = StringVar()
        self.month.set(datetime.today().strftime('%B'))
        self.end_day = StringVar()

        # Change Plan Var
        self.ch_start_date = StringVar()
        self.ch_days = StringVar()
        self.ch_designer = StringVar()

        uname = shared_variable.user_name

        queries = []

        # Fill no of days as per difficulty
        def fill_days():
            # create a dictionary of tuples with no of days as per difficulty
            mc_model_values2 = ('ASB-70DPH', 'ASB-70DPW', 'ASB-50MB', 'ASB-12M', 'PF', 'Preform', 'Modification', 'Parts Order', 'ECM')

            with open('O:/Scheduling/Mold Design Application/Final software/database/planning_days.json', 'r') as f:
                # Load the contents of the file as a dictionary
                days_data = json.load(f)

            r_dict = days_data[self.DegnModel.get()]

            # get the data corresponding to the selected value from the dictionary
            p, a, ac, d, c, sc, i = r_dict[self.difficulty.get()]

            # display the data in the entry widgets
            set_difficulty = {
                "Preform": p,
                "Assembly": a,
                "Assembly Check": ac,
                "Detailing": d,
                "Checking": c,
                "Second Check": sc,
                "Issue": i
            }

            self.Designer_label = ttk.Label(self, text='Designers Group:').place(x=250, y=735)
            self.Designer_Comb = ttk.Combobox(self, textvariable=self.DegnModel, width=15, values=mc_model_values2).place(x=360, y=730)
            # Create a button with the refresh symbol as text
            self.refresh_btn = ttk.Button(self, text="\u27F3", command=get_designers)
            self.refresh_btn.place(x=485, y=730, width=40)



        # Select designer
        def sel_dsgn(event, arg):
            # Update variables from tree view
            try:
                selected_item = self.tree.selection()[0]
                arg.set(self.tree.item(selected_item)['values'][0])
            except IndexError:
                arg.set('Select Designer')

        # Date Entry widget function
        def open_cal(event, arg):
            self.cal_date.set(arg.entry.get())

        def query_n_cmd(arg1, arg2, arg3):
            arg2.set(2)

            try:
                queries.remove(arg3)
            except ValueError:
                pass

        def query_y_cmd(arg1, arg2, arg3):
            arg1.set(0)

            if arg2.get() == 1:
                queries.append(arg3)
            elif arg2.get() == 0:
                queries.remove(arg3)
            else:
                pass

        def submit_one(arg1, arg2, arg3):
            # arg1=checkbox var, arg2="query', arg3="D_PLAN_STATUS"

            if arg1.get() != 1:
                messagebox.showerror("Scheduler", "Please plan first")
                return

            blank_check = (self.Activity_var, self.Activity_day, self.Activity_start_date.entry, self.Activity_end, self.Activity_designer)

            blank_item = []
            for v in blank_check:
                if v.get() == "" or v.get() == "***":
                    v.set("***")
                    blank_item.append(v.get())

            if blank_item:
                return

            # Connect to the SQLite3 database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
            c = conn.cursor()

            c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{blank_check[arg2][2].get()}'")
            designer_tbl = c.fetchone()

            if not designer_tbl:
                messagebox.showinfo("Scheduler", "Please select the proper designer")
                return

            result = c.execute("SELECT YEAR2023 FROM holidaylist")
            holiday_list = tuple(date[0] for date in result.fetchall())

            days_insert = {
                "p_query": (self.P_start_date.entry.get(), self.p_day.get(), self.p_designer.get(), "Preform"),
                "a_query": (self.A_start_date.entry.get(), self.a_day.get(), self.a_designer.get(), "Assembly"),
                "ac_query": (self.AC_start_date.entry.get(), self.ac_day.get(), self.ac_designer.get(), "Assembly Check"),
                "d_query": (self.D_start_date.entry.get(), self.d_day.get(), self.d_designer.get(), "Detailing"),
                "c_query": (self.C_start_date.entry.get(), self.c_day.get(), self.c_designer.get(), "Checking"),
                "cr_query": (self.CR_start_date.entry.get(), self.cr_day.get(), self.cr_designer.get(), "Correction"),
                "sc_query": (self.SC_start_date.entry.get(), self.sc_day.get(), self.sc_designer.get(), "Second Check"),
                "i_query": (self.I_start_date.entry.get(), self.i_day.get(), self.i_designer.get(), "Issue"),
            }

            # Define the input values
            if '.' in days_insert[arg2][1]:
                no_of_days = float(days_insert[arg2][1])
            else:
                no_of_days = int(days_insert[arg2][1])

            # user log date
            user_log = uname + " " + datetime.now().strftime('%d/%m/%Y')

            # Convert string to datetime object
            start_date = datetime.strptime(days_insert[arg2][0], "%d-%m-%Y")

            # Loop through the number of days and insert records into the database
            for i in range(int(no_of_days)):
                if start_date.weekday() == 6:
                    start_date = start_date + timedelta(days=1)
                    if start_date.strftime("%Y-%m-%d") in holiday_list:
                        start_date = start_date + timedelta(days=1)
                # Create a date string in the format 'dd-mm-yyyy'
                date_str = start_date.strftime("%Y-%m-%d")
                self.end_day.set(date_str)
                # Insert the record into the database
                c.execute("INSERT INTO HEATMAP (REQ_ID,MOLD_NO,DATE,DESIGNER,ACTIVITY,DAYS,STATUS,STATUS_REMARK,USER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (self.req_id.get(), self.mold_no.get(), date_str, days_insert[arg2][2], days_insert[arg2][3], 1, 0, 'Planned', user_log))
                # Increment the day by 1
                start_date = start_date + timedelta(days=1)

            # If there are remaining days (e.g. 0.5 in this case), insert a record with the remaining days
            if no_of_days % 1 != 0:
                if start_date.weekday() == 6:
                    start_date = start_date + timedelta(days=1)
                    if start_date.strftime("%Y-%m-%d") in holiday_list:
                        start_date = start_date + timedelta(days=1)
                date_str = start_date.strftime("%Y-%m-%d")
                self.end_day.set(date_str)
                c.execute("INSERT INTO HEATMAP (REQ_ID,MOLD_NO,DATE,DESIGNER,ACTIVITY,DAYS,STATUS,STATUS_REMARK,USER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (self.req_id.get(), self.mold_no.get(), date_str, days_insert[arg2][2], days_insert[arg2][3], no_of_days % 1, 0, 'Planned', user_log))

            # Execute the update query
            c.execute(f"UPDATE MOLD_TABLE SET {arg3}={arg3}+?,PRE_PLAN_STATUS=? WHERE REQ_ID=?", (1, 1, self.req_id.get()))

            # reset the start date
            ob_date = datetime.strptime(days_insert[arg2][0], "%d-%m-%Y")
            start_date = datetime.strftime(ob_date, "%Y-%m-%d")

            p_query = f"INSERT INTO {self.p_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)", \
                      (self.req_id.get(), self.mold_no.get(), 'Preform', start_date, self.end_day.get(), self.p_day.get(), 0, 'Planned'),
            a_query = f"INSERT INTO {self.a_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)", \
                      (self.req_id.get(), self.mold_no.get(), "Assembly", start_date, self.end_day.get(), self.a_day.get(), 0, 'Planned'),
            ac_query = f"INSERT INTO {self.ac_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)", \
                       (self.req_id.get(), self.mold_no.get(), "Assembly Check", start_date, self.end_day.get(), self.ac_day.get(), 0, 'Planned'),
            d_query = f"INSERT INTO {self.d_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)", \
                      (self.req_id.get(), self.mold_no.get(), "Detailing", start_date, self.end_day.get(), self.d_day.get(), 0, 'Planned'),
            c_query = f"INSERT INTO {self.c_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)", \
                      (self.req_id.get(), self.mold_no.get(), "Checking", start_date, self.end_day.get(), self.c_day.get(), 0, 'Planned'),
            cr_query = f"INSERT INTO {self.cr_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)", \
                       (self.req_id.get(), self.mold_no.get(), "Checking", start_date, self.end_day.get(), self.cr_day.get(), 0, 'Planned'),
            sc_query = f"INSERT INTO {self.sc_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)", \
                       (self.req_id.get(), self.mold_no.get(), "Second Check", start_date, self.end_day.get(), self.sc_day.get(), 0, 'Planned'),
            i_query = f"INSERT INTO {self.i_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)", \
                      (self.req_id.get(), self.mold_no.get(), "Issue", start_date, self.end_day.get(), self.i_day.get(), 0, 'Planned')

            dsgn_insert = {
                "p_query": p_query,
                "a_query": a_query,
                "ac_query": ac_query,
                "d_query": d_query,
                "c_query": c_query,
                "cr_query": cr_query,
                "sc_query": sc_query,
                "i_query": i_query,
            }

            c.execute(dsgn_insert[arg2][0], dsgn_insert[arg2][1])

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

            blank_check[arg2][0].delete(0, END)
            blank_check[arg2][2].set("")
            arg1.set(0)

            get_mold_plan(self.mold_no.get())

            # Delete all data from the TreeView
            self.tree.delete(*self.tree.get_children())

        def get_first_day_of_month(month_name):
            current_year = datetime.today().year
            month_number = datetime.strptime(month_name, '%B').month
            first_day = datetime(current_year, month_number, 1)
            return first_day.strftime('%d-%m-%Y')

        def heatmap():
            m_date = get_first_day_of_month(self.month.get())
            m_date = datetime.today().strptime(m_date, "%d-%m-%Y")

            # get the selected value from the combobox
            selection = self.DegnModel.get()

            with open('O:/Scheduling/Mold Design Application/Final software/database/list.json', 'r') as f:
                # Load the contents of the file as a dictionary
                data = json.load(f)

            # get the required dict
            try:
                names = data['designers'][selection]
            except KeyError:
                names = data['designers']['ASB-70DPH']

            # Define the column headings for the dates
            date_columns = [(m_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

            # Create a dictionary with the required data
            data_dict = {'DESIGNER': names, **{col: [0] * len(names) for col in date_columns}}

            # Create a DataFrame from the dictionary
            data = pd.DataFrame(data_dict)

            # Rename the columns
            data.columns = ['DESIGNER'] + date_columns

            # Connect to database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

            # define query
            query = f"SELECT DATE, DESIGNER, DAYS FROM HEATMAP WHERE DATE BETWEEN ? AND date(?, '+30 day')"

            # Define the query parameters
            params = (m_date.strftime('%Y-%m-%d'), m_date.strftime('%Y-%m-%d'),)

            # Execute a SELECT statement with a WHERE clause
            df1 = pd.read_sql(query, conn, params=params)

            # Close the connection
            conn.close()

            # create the pivot table
            pivot_table = pd.pivot_table(df1, index='DESIGNER', columns='DATE', values='DAYS', aggfunc=sum)

            # Convert to DataFrame
            df = pd.DataFrame(pivot_table.to_records()).fillna(0)

            # set the "DESIGNER" column as the index for both dataframes
            data.set_index('DESIGNER', inplace=True)
            df.set_index('DESIGNER', inplace=True)

            # add the two dataframes together
            result = data.add(df, fill_value=0)

            # replace any missing values with zeros
            result.fillna(0, inplace=True)

            # reset the index to make "DESIGNER" a column again
            result = result.reindex(names)

            # create a new figure and axis object
            fig, ax = plt.subplots(figsize=(screen_width/100, screen_height/100))

            sns.heatmap(result, annot=True, fmt=".1f", vmin=0, vmax=3, cmap="YlGnBu", center=1.5, ax=ax)
            plt.show()

        def reset_var():


            self.difficulty.set('')


            self.DegnModel.set('')

            queries.clear()

        # def get_new_entry():
        #     # Connect to the SQLite database
        #     conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
        #     cursor = conn.cursor()
        #
        #     # Execute a SELECT statement with a WHERE clause
        #     cursor.execute('SELECT * FROM MOLD_TABLE WHERE PRE_PLAN_STATUS = ?', (0,))
        #     data = cursor.fetchall()
        #
        #     # Close the connection
        #     conn.close()
        #
        #     # Insert the data into the TreeView
        #     for row in data:
        #         self.dtree.insert('', END, values=row)

        def update_info(event, arg):

            # Reset all variable
            reset_var()

            mold_no = arg.item(arg.selection()[0])['values'][1]

            df_project_mold = plan_by_mold(self.MDShdb, mold_no)

            # Delete all data from the TreeView
            self.data_tree.delete(*self.data_tree.get_children())

            # Insert the data into the TreeView
            for i, row_mold in df_project_mold.iterrows():
                values = tuple(row_mold.values)
                self.data_tree.insert("", "end", text=i, values=values)

            df_mold_info = get_mold_info(self.MDShdb, mold_no)

            self.req_id.set(df_mold_info.at[0, 'REQ_ID'])
            self.mold_no.set(df_mold_info.at[0, 'MOLD_NO'])
            self.customer.set(df_mold_info.at[0, 'CUSTOMER'])
            self.machine_type.set(df_mold_info.at[0, 'MACHINE_TYPE'])
            self.cav_no.set(df_mold_info.at[0, 'CAVITY'])
            self.ord_scp.set(df_mold_info.at[0, 'ORDER_SCOPE'])
            self.ord_typ.set(df_mold_info.at[0, 'ORDER_TYPE'])
            self.iss_to.set(df_mold_info.at[0, 'ISSUE_TO'])
            self.zc_var.set(df_mold_info.at[0, 'ZC'])
            self.qmc_var.set(df_mold_info.at[0, 'QMC'])
            self.air_ejt_var.set(df_mold_info.at[0, 'AIR_EJECT'])
            self.pos_ver.set(df_mold_info.at[0, 'POS_VER'])
            self.country.set(df_mold_info.at[0, 'COUNTRY'])
            self.bottle_no.set(df_mold_info.at[0, 'CONTAINER_NO'])
            self.malt.set(df_mold_info.at[0, 'MOLDING_MALT'])
            self.hrtype.set(df_mold_info.at[0, 'HR_TYPE'])
            self.difficulty.set(df_mold_info.at[0, 'DIFFICULTY'])

            # Label of mold information
            self.mold_no_label = ttk.Label(self.mold_details, text=f'Mold No : {self.mold_no.get()}').grid(column=0, row=0)
            self.req_id_label = ttk.Label(self.mold_details, text=f'Request ID : {self.req_id.get()}').grid(column=1, row=0)
            self.cust_label = ttk.Label(self.mold_details, text=f'Customer : {self.customer.get()}').grid(column=0, row=1, columnspan=2)
            self.mc_label = ttk.Label(self.mold_details, text=f'Machine Type : {self.machine_type.get()}').grid(column=0, row=2, columnspan=2)
            self.cav_label = ttk.Label(self.mold_details, text=f'Cavity : {self.cav_no.get()}').grid(column=0, row=3)
            self.scope_label = ttk.Label(self.mold_details, text=f'Order Scope : {self.ord_scp.get()}').grid(column=1, row=3)
            self.type_label = ttk.Label(self.mold_details, text=f'Order Type : {self.ord_typ.get()}').grid(column=0, row=4)
            self.issue_to_label = ttk.Label(self.mold_details, text=f'Issue To : {self.iss_to.get()}').grid(column=1, row=4)
            self.zc_label = ttk.Label(self.mold_details, text=f'ZC : {self.zc_var.get()}').grid(column=0, row=5)
            self.qmc_label = ttk.Label(self.mold_details, text=f'QMC : {self.qmc_var.get()}').grid(column=1, row=5)
            self.air_label = ttk.Label(self.mold_details, text=f'Air Eject : {self.air_ejt_var.get()}').grid(column=0, row=6)
            self.ver_label = ttk.Label(self.mold_details, text=f'POS Ver : {self.pos_ver.get()}').grid(column=1, row=6)
            self.country_label = ttk.Label(self.mold_details, text=f'POS Ver : {self.country.get()}').grid(column=0, row=7)
            self.bottle_label = ttk.Label(self.mold_details, text=f'Bottle No : {self.bottle_no.get()}').grid(column=1, row=7)
            self.malt_label = ttk.Label(self.mold_details, text=f'Molding Material : {self.malt.get()}').grid(column=0, row=8)
            self.hrtype_label = ttk.Label(self.mold_details, text=f'HR Type : {self.hrtype.get()}').grid(column=1, row=8)

            # Configure for all widgets in Project Details frame
            for wid in self.mold_details.winfo_children():
                wid.grid_configure(padx=20, pady=3, sticky=W)

        def get_designers():
            # try:
            #     m_date = datetime.strptime(cal_date, "%d-%m-%Y")
            # except ValueError:
            #     m_date = cal_date
            print(type(self.cal_date.get()))
            m_date = datetime.strptime(self.cal_date.get(), "%d-%m-%Y")

            # get the selected value from the combobox
            selection = self.DegnModel.get()

            with open('O:/Scheduling/Mold Design Application/Final software/database/list.json', 'r') as f:
                # Load the contents of the file as a dictionary
                data = json.load(f)

            # get the required dict
            try:
                names = data['designers'][selection]
            except KeyError:
                names = data['designers']['ASB-70DPH']

            # Define the column headings for the dates
            date_columns = [(m_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]
            #
            # names = designers_list[r_dict]

            # Create a dictionary with the required data
            data_dict = {'DESIGNER': names, **{col: [0] * len(names) for col in date_columns}}

            # Create a DataFrame from the dictionary
            data = pd.DataFrame(data_dict)

            # Rename the columns
            data.columns = ['DESIGNER'] + date_columns

            # Connect to database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

            # define query
            query = f"SELECT DATE, DESIGNER, DAYS FROM HEATMAP WHERE DATE BETWEEN ? AND date(?, '+5 day')"

            # Define the query parameters
            params = (m_date.strftime('%Y-%m-%d'), m_date.strftime('%Y-%m-%d'),)

            # Execute a SELECT statement with a WHERE clause
            df1 = pd.read_sql(query, conn, params=params)

            # Close the connection
            conn.close()

            # create the pivot table
            pivot_table = pd.pivot_table(df1, index='DESIGNER', columns='DATE', values='DAYS', aggfunc=sum)

            # Convert to DataFrame
            df = pd.DataFrame(pivot_table.to_records()).fillna(0)

            # set the "DESIGNER" column as the index for both dataframes
            data.set_index('DESIGNER', inplace=True)
            df.set_index('DESIGNER', inplace=True)

            # add the two dataframes together
            result = data.add(df, fill_value=0)

            # replace any missing values with zeros
            result.fillna(0, inplace=True)

            # reset the index to make "DESIGNER" a column again
            result = result.reindex(names)
            result.reset_index(inplace=True)

            # iterate over the column names
            for col_name in result.columns:
                if col_name != 'DESIGNER':
                    if datetime.strptime(col_name, '%Y-%m-%d').weekday() == 6:
                        result.loc[:, col_name] = ['Sunday'] * len(names)

            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insert the data into the TreeView
            for i, row in result.iterrows():
                values = tuple(row.values)
                for j in range(2, 7):
                    date_str = (m_date + timedelta(days=j-2)).strftime("%d-%m-%Y")
                    self.tree.heading("#" + str(j), text=date_str)
                self.tree.heading("#1", text="Designer")
                self.tree.insert("", "end", text=i, values=values)

        def mold_information():
            activity = ('Preform', 'Assembly', 'Assembly Check', 'Detailing', 'Checking', 'Correction', '2nd Checking', 'Mold Issue')

            # Labels Heading
            self.activity_label = ttk.Label(self.planning_details, text='Activity').grid(column=0, row=1)
            self.yes_label = ttk.Label(self.planning_details, text='YES').grid(column=1, row=1)
            self.no_label = ttk.Label(self.planning_details, text='NO').grid(column=2, row=1)
            self.start_label = ttk.Label(self.planning_details, text='Start Date').grid(column=3, row=1)
            self.day_label = ttk.Label(self.planning_details, text='Days').grid(column=4, row=1)
            self.end_label = ttk.Label(self.planning_details, text='End Date').grid(column=5, row=1)
            self.design_label = ttk.Label(self.planning_details, text='Designer').grid(column=6, row=1)

            # Labels row
            self.Activity_combo = ttk.Combobox(self.planning_details, textvariable=self.Activity_var, values=activity, width=15).grid(column=0, row=2, sticky="W")

            # Activity check buttons
            self.R1 = ttk.Checkbutton(self.planning_details, variable=self.Y_var, command=lambda arg1=self.N_var, arg2=self.Y_var, arg3=self.Activity_var: query_y_cmd(arg1, arg2, arg3))
            self.R1.grid(column=1, row=2)

            # Activity check buttons
            self.R11 = ttk.Checkbutton(self.planning_details, variable=self.N_var, command=lambda arg1=self.N_var, arg2=self.Y_var, arg3=self.Activity_var: query_n_cmd(arg1, arg2, arg3))
            self.R11.grid(column=2, row=2)

            # Start date
            self.Activity_start_date = DateEntry(self.planning_details, width=12)
            self.Activity_start_date.grid(column=3, row=2, padx=20, pady=4)
            self.Activity_start_date.entry.bind('<FocusIn>', lambda event, arg=self.P_start_date: open_cal(event, arg))
            self.Activity_start_date.entry.delete(first=0, last=END)

            # Days
            self.Activity_day = ttk.Entry(self.planning_details, textvariable=self.Activity_day, width=5).grid(column=4, row=2, padx=20, pady=4)

            # End date
            self.Activity_end = ttk.Entry(self.planning_details, textvariable=self.Activity_end, width=10).grid(column=5, row=2)

            # Designers data
            self.Activity_designer = ttk.Entry(self.planning_details, textvariable=self.Activity_designer, width=10)
            self.Activity_designer.grid(column=6, row=2)
            self.Activity_designer.bind('<1>', lambda event, arg=self.Activity_designer: sel_dsgn(event, arg))

            # Add buttons
            self.Activity_Button = ttk.Button(self.planning_details, text="Add", command=lambda arg1=self.Y_var, arg2=self.Activity_var: submit_one(arg1, arg2), width=4)
            self.Activity_Button.grid(column=7, row=2)

            for p_widgets in self.planning_details.winfo_children():
                p_widgets.grid_configure(padx=5, pady=4)

        def get_mold_plan(mold_no):
            try:
                conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

                # define query
                query = 'SELECT * FROM HEATMAP WHERE MOLD_NO=? AND STATUS=?'

                # Define the query parameters
                params = (mold_no, '0')

                # Execute a SELECT statement with a WHERE clause
                df_project_mold = pd.read_sql(query, conn, params=params)
                conn.close()

                # group by and aggregate the 'DAYS' column
                df_project_mold = df_project_mold.groupby(['REQ_ID', 'MOLD_NO', 'DESIGNER', 'ACTIVITY', 'STATUS'], as_index=False).agg({'DAYS': 'sum', 'DATE': 'first'})
                df_project_mold = df_project_mold[['REQ_ID', 'MOLD_NO', 'DATE', 'DESIGNER', 'ACTIVITY', 'DAYS', 'STATUS']]

                # convert 'DATE' column to datetime format
                df_project_mold['DATE'] = pd.to_datetime(df_project_mold['DATE'], dayfirst=True)

                # Convert date column to '%d-%m-%Y' format
                df_project_mold['DATE'] = pd.to_datetime(df_project_mold['DATE']).dt.strftime('%d-%m-%Y')

                # Delete all data from the TreeView
                self.data_tree.delete(*self.data_tree.get_children())

                # Insert the data into the TreeView
                for i, row in df_project_mold.iterrows():
                    values = tuple(row.values)
                    self.data_tree.insert("", "end", text=i, values=values)
            except ValueError:
                pass
            pass

        def switch_func():
            pass
        #     # Check if the Label has been place
        #     if self.mold_plan_details.winfo_manager() == "place":
        #         self.mold_plan_details.place_forget()
        #         self.mold_details.place(x=680, y=300, width=575, height=420)
        #     else:
        #         self.mold_details.place_forget()
        #         self.mold_plan_details.place(x=680, y=300)

        def change_plan(event):
            # Update variables from tree view
            try:
                selected_item = self.data_tree.selection()[0]
            except IndexError:
                # messagebox.showerror("Error", 'Select Proper Row')
                return

            self.ch_start_date.set(self.data_tree.item(selected_item)['values'][2])
            self.ch_days.set(self.data_tree.item(selected_item)['values'][5])
            self.ch_designer.set(self.data_tree.item(selected_item)['values'][3])

            self.ch_start_date_label = ttk.Label(self.mold_plan_details, text='Start Date').place(x=35, y=250)
            self.ch_start_date_entry = ttk.Entry(self.mold_plan_details, textvariable=self.ch_start_date).place(x=20, y=270, width=100)
            self.ch_days_label = ttk.Label(self.mold_plan_details, text='No of Days').place(x=145, y=250)
            self.ch_days_entry = ttk.Entry(self.mold_plan_details, textvariable=self.ch_days).place(x=130, y=270, width=100)
            self.ch_designer_date_label = ttk.Label(self.mold_plan_details, text='Designer').place(x=255, y=250)
            self.ch_designer_date_entry = ttk.Entry(self.mold_plan_details, textvariable=self.ch_designer).place(x=240, y=270, width=100)

            self.update1_btn = ttk.Button(self.mold_plan_details, text="Update", command=update_pre_plan).place(x=350, y=270, width=80)
            self.change1_btn = ttk.Button(self.mold_plan_details, text="Delete", command=delete_pre_plan).place(x=450, y=270, width=80)

        def update_pre_plan():
            # Update variables from tree view
            try:
                selected_item = self.data_tree.selection()[0]
            except IndexError:
                messagebox.showerror("Error", 'Select Proper Row')
                return

            temp_req_id = self.data_tree.item(selected_item)['values'][0]
            temp_designer = self.data_tree.item(selected_item)['values'][3]
            temp_mold_no = self.data_tree.item(selected_item)['values'][1]
            temp_activity = self.data_tree.item(selected_item)['values'][4]
            temp_start = self.data_tree.item(selected_item)['values'][2]

            # Connect to the SQLite3 database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
            c = conn.cursor()
            c.execute("PRAGMA JOURNAL_MODE='wal' ")

            try:
                row = c.execute(f"SELECT REQ_ID FROM {self.ch_designer.get()}")
            except sqlite3.OperationalError:
                return

            c.execute(f"DELETE FROM {temp_designer} WHERE REQ_ID=? AND ACTIVITY=?", (temp_req_id, temp_activity))

            c.execute("DELETE FROM HEATMAP WHERE REQ_ID=? AND DESIGNER=? AND ACTIVITY=?", (temp_req_id, temp_designer, temp_activity))

            result = c.execute("SELECT YEAR2023 FROM holidaylist")
            holiday_list = tuple(date[0] for date in result.fetchall())

            # Define the input values
            if '.' in self.ch_days.get():
                no_of_days = float(self.ch_days.get())
            else:
                no_of_days = int(self.ch_days.get())

            # user log date
            user_log = uname + " " + datetime.now().strftime('%d-%m-%Y')

            # Convert string to datetime object
            try:
                start_date = datetime.strptime(self.ch_start_date.get(), "%d-%m-%Y")
            except ValueError:
                date_string = self.ch_start_date.get()
                datetime_object = datetime.strptime(date_string, "%Y-%m-%d")
                start_date = datetime_object.strftime("%d-%m-%Y")

            # Loop through the number of days and insert records into the database
            for i in range(int(no_of_days)):
                if start_date.weekday() == 6:
                    start_date = start_date + timedelta(days=1)
                    if start_date.strftime("%Y-%m-%d") in holiday_list:
                        start_date = start_date + timedelta(days=1)
                # Create a date string in the format 'dd-mm-yyyy'
                date_str = start_date.strftime("%Y-%m-%d")
                self.end_day.set(date_str)
                # Insert the record into the database
                c.execute("INSERT INTO HEATMAP (REQ_ID,MOLD_NO,DATE,DESIGNER,ACTIVITY,DAYS,STATUS,STATUS_REMARK,USER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (temp_req_id, temp_mold_no, date_str, self.ch_designer.get(), temp_activity, 1, 0, 'Planned', user_log))
                # Increment the day by 1
                start_date = start_date + timedelta(days=1)

            # If there are remaining days (e.g. 0.5 in this case), insert a record with the remaining days
            if no_of_days % 1 != 0:
                if start_date.weekday() == 6:
                    start_date = start_date + timedelta(days=1)
                    if start_date.strftime("%Y-%m-%d") in holiday_list:
                        start_date = start_date + timedelta(days=1)
                date_str = start_date.strftime("%Y-%m-%d")
                self.end_day.set(date_str)
                c.execute("INSERT INTO HEATMAP (REQ_ID,MOLD_NO,DATE,DESIGNER,ACTIVITY,DAYS,STATUS,STATUS_REMARK,USER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (temp_req_id, temp_mold_no, date_str, self.ch_designer.get(), temp_activity, no_of_days % 1, 0, 'Planned', user_log))

            # Convert date string
            temp_start = self.ch_start_date.get()
            datetime_object = datetime.strptime(temp_start, "%d-%m-%Y")
            temp_start = datetime_object.strftime("%Y-%m-%d")

            c.execute(f"INSERT INTO {self.ch_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS_REMARK) VALUES (?,?,?,?,?,?,?)",
                      (temp_req_id, temp_mold_no, temp_activity, temp_start, self.end_day.get(), self.ch_days.get(), 'Planned'))

            conn.commit()
            conn.close()

            get_mold_plan(temp_mold_no)

            self.ch_start_date.set("")
            self.ch_days.set("")
            self.ch_designer.set("")

        def delete_pre_plan():
            # Update variables from tree view
            try:
                selected_item = self.data_tree.selection()[0]
            except IndexError:
                messagebox.showerror("Error", 'Select Proper Row')
                return

            temp_req_id = self.data_tree.item(selected_item)['values'][0]
            temp_designer = self.data_tree.item(selected_item)['values'][3]
            temp_mold_no = self.data_tree.item(selected_item)['values'][1]
            temp_activity = self.data_tree.item(selected_item)['values'][4]

            # Connect to the SQLite3 database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
            c = conn.cursor()

            try:
                row = c.execute(f"SELECT REQ_ID FROM {self.ch_designer.get()}")
            except sqlite3.OperationalError:
                return

            c.execute(f"DELETE FROM {temp_designer} WHERE REQ_ID=? AND ACTIVITY=?", (temp_req_id, temp_activity))

            c.execute("DELETE FROM HEATMAP WHERE REQ_ID=? AND DESIGNER=? AND ACTIVITY=?", (temp_req_id, temp_designer, temp_activity))

            up_plan = {
                "Preform": "P_PLAN_STATUS",
                "Assembly": "A_PLAN_STATUS",
                "Assembly Check": "AC_PLAN_STATUS",
                "Detailing": "D_PLAN_STATUS",
                "Checking": "C_PLAN_STATUS",
                "Correction": "CR_PLAN_STATUS",
                "Second Check": "SC_PLAN_STATUS",
                "Issue": "I_PLAN_STATUS"
            }

            arg3 = up_plan[temp_activity]

            # Execute the update query
            c.execute(f"UPDATE MOLD_TABLE SET {arg3}={arg3}-?,PRE_PLAN_STATUS=? WHERE REQ_ID=?", (1, 1, self.req_id.get()))

            conn.commit()
            conn.close()

            get_mold_plan(temp_mold_no)

            self.ch_start_date.set("")
            self.ch_days.set("")
            self.ch_designer.set("")

        def submit():
            selection = self.dtree.selection()

            if not selection:
                messagebox.showerror("Error", 'Please plan first')
                return

            # try:
            #     remark = self.remark_text.get("1.0", "end")
            # except AttributeError:
            #     pass
            #
            # # Connect to the SQLite3 database
            # conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
            # c = conn.cursor()
            #
            # c.execute("UPDATE MOLD_TABLE SET REMARK=? WHERE REQ_ID=?", (remark, self.req_id.get()))
            # conn.commit()
            # conn.close()

            # Reset all variable
            reset_var()

            # Clear all label in mold details
            for child in self.mold_details.winfo_children():
                child.destroy()

            # Clear all label in mold details
            for child in self.planning_details.winfo_children():
                child.destroy()

            # Delete all data from the TreeView
            self.tree.delete(*self.tree.get_children())
            self.dtree.delete(*self.dtree.get_children())
            self.data_tree.delete(*self.data_tree.get_children())
            get_new_entry()

# Mold Info

        self.mold_details = ttk.LabelFrame(self, text="Mold Information")
        self.mold_details.place(x=20, y=20, width=650, height=260)
        self.mold_details.columnconfigure((0, 1), weight=1)

# Planning Info

        self.planning_details = ttk.LabelFrame(self, text="Planning Information")
        self.planning_details.place(x=20, y=550, width=650, height=150)
        self.planning_details.columnconfigure(0, weight=2)
        self.planning_details.columnconfigure((1, 2), weight=0)
        self.planning_details.columnconfigure((3, 4, 5), weight=3)
        self.planning_details.columnconfigure(6, weight=1)

# Available Designers

        self.designer_details = ttk.LabelFrame(self, text="Available Designers")
        self.designer_details.place(x=680, y=20, width=575, height=260)

        columns = ('design', 'date1', 'date2', 'date3', 'date4', 'initial')
        self.tree = ttk.Treeview(self.designer_details, columns=columns, show='headings')
        self.tree.place(x=10, y=10, width=555, height=220)

        self.scrollbar_v = ttk.Scrollbar(self.designer_details, orient='vertical', command=self.tree.yview)
        self.scrollbar_v.place(x=1135, y=10, width=20, height=210)

        self.tree.heading('design', text='Designer')
        self.tree.column('design', anchor=CENTER, stretch=NO, minwidth=90, width=80)
        self.tree.heading('date1', text='Days')
        self.tree.column('date1', anchor=CENTER, stretch=YES, minwidth=70, width=80)
        self.tree.heading('date2', text='Days')
        self.tree.column('date2', anchor=CENTER, stretch=YES, minwidth=70, width=80)
        self.tree.heading('date3', text='Days')
        self.tree.column('date3', anchor=CENTER, stretch=YES, minwidth=70, width=80)
        self.tree.heading('date4', text='Days')
        self.tree.column('date4', anchor=CENTER, stretch=YES, minwidth=70, width=80)
        self.tree.heading('initial', text='Days')
        self.tree.column('initial', anchor=CENTER, stretch=YES, minwidth=70, width=80)

        # self.tree.bind("<Double-1>", on_double_click)
        self.tree.configure(yscrollcommand=self.scrollbar_v.set)

# new entry
        self.mold_plan_details = Frame(self, bd=2)
        self.mold_plan_details.place(x=680, y=300, width=575, height=410)

        data = get_new_entry(self.MDShdb)

        self.new_entry_label = ttk.LabelFrame(self.mold_plan_details, text=f"New Mold : {len(data)}")
        self.new_entry_label.place(x=0, y=0, width=190, height=395)

        columns = ('info', 'mold')
        self.new_entry_tree = ttk.Treeview(self.new_entry_label, columns=columns, show='headings')
        self.new_entry_tree.place(x=0, y=5, width=175, height=370)

        self.scrollbar_v = ttk.Scrollbar(self.new_entry_label, orient='vertical', command=self.new_entry_tree.yview)
        self.scrollbar_v.place(x=175, y=5, width=10, height=370)

        self.new_entry_tree.heading('info', text='Info Date')
        self.new_entry_tree.column('info', anchor=CENTER, stretch=NO, minwidth=75, width=75)
        self.new_entry_tree.heading('mold', text='Mold No')
        self.new_entry_tree.column('mold', anchor=CENTER, stretch=NO, minwidth=100, width=95)

        self.new_entry_tree.bind('<Double-1>', lambda event, arg=self.new_entry_tree: update_info(event, arg))

        # Insert the data into the TreeView
        for row in data:
            self.new_entry_tree.insert('', END, values=row)

# Short Plan

        short_plan_data = get_short_plan(self.MDShdb)

        self.short_plan_details = ttk.LabelFrame(self.mold_plan_details, text=f"Short Plan : {len(short_plan_data)}")
        self.short_plan_details.place(x=195, y=0, width=190, height=395)

        columns = ('info', 'mold')
        self.short_plan_tree = ttk.Treeview(self.short_plan_details, columns=columns, show='headings')
        self.short_plan_tree.place(x=0, y=5, width=175, height=370)

        self.scrollbar_v = ttk.Scrollbar(self.short_plan_details, orient='vertical', command=self.short_plan_tree.yview)
        self.scrollbar_v.place(x=175, y=5, width=10, height=370)

        self.short_plan_tree.heading('info', text='Info Date')
        self.short_plan_tree.column('info', anchor=CENTER, stretch=NO, minwidth=75, width=75)
        self.short_plan_tree.heading('mold', text='Mold No')
        self.short_plan_tree.column('mold', anchor=CENTER, stretch=NO, minwidth=100, width=95)

        self.short_plan_tree.bind('<Double-1>', lambda event, arg=self.short_plan_tree: update_info(event, arg))

        # Insert the data into the TreeView
        for row in short_plan_data:
            self.short_plan_tree.insert('', END, values=row)

# Complete Plan

        complete_plan = get_complete_plan(self.MDShdb)

        self.complete_plan_details = ttk.LabelFrame(self.mold_plan_details, text=f"Complete Plan : {len(complete_plan)}")
        self.complete_plan_details.place(x=390, y=0, width=180, height=395)

        columns = ('info', 'mold')
        self.complete_plan_tree = ttk.Treeview(self.complete_plan_details, columns=columns, show='headings')
        self.complete_plan_tree.place(x=0, y=5, width=175, height=370)

        self.scrollbar_v = ttk.Scrollbar(self.complete_plan_details, orient='vertical', command=self.complete_plan_tree.yview)
        self.scrollbar_v.place(x=175, y=5, width=10, height=370)

        self.complete_plan_tree.heading('info', text='Info Date')
        self.complete_plan_tree.column('info', anchor=CENTER, stretch=NO, minwidth=75, width=75)
        self.complete_plan_tree.heading('mold', text='Mold No')
        self.complete_plan_tree.column('mold', anchor=CENTER, stretch=NO, minwidth=100, width=95)

        self.complete_plan_tree.bind('<Double-1>', lambda event, arg=self.complete_plan_tree: update_info(event, arg))

        # Insert the data into the TreeView
        for row in complete_plan:
            self.complete_plan_tree.insert('', END, values=row)

# Submit Button

        self.submit_btn = ttk.Button(self, text="Submit", command=submit).place(x=575, y=730)

# Month Combobox

        month_values = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        self.month_Comb = ttk.Combobox(self, textvariable=self.month, width=12, values=month_values).place(x=20, y=730)

# Heatmap Button

        self.heatmap_btn = ttk.Button(self, text="Heatmap", command=heatmap).place(x=130, y=730)

# Switch Mold Information and Mold Info Button

        self.switch_btn = ttk.Button(self, text=">", command=switch_func, width=1).place(x=1225, y=730)

# Mold Planning

        self.mold_plan_details = ttk.Frame(self, width=650, height=250)
        self.mold_plan_details.place(x=20, y=300)

        self.label_plan = ttk.Label(self.mold_plan_details, text="Mold Plan Information:")
        self.label_plan.place(x=0, y=10)

        columns = ('reqid', 'md_no', 'date', 'designer', 'activity', 'days', 'status')
        self.data_tree = ttk.Treeview(self.mold_plan_details, columns=columns, show='headings')
        self.data_tree.place(x=0, y=35, width=625, height=210)

        self.scrollbar_v = ttk.Scrollbar(self.mold_plan_details, orient='vertical', command=self.data_tree.yview)
        self.scrollbar_v.place(x=630, y=35, width=20, height=210)

        self.data_tree.heading('reqid', text='Request ID')
        self.data_tree.column('reqid', anchor=CENTER, stretch=NO, minwidth=60, width=80)
        self.data_tree.heading('md_no', text='Mold No')
        self.data_tree.column('md_no', anchor=CENTER, stretch=NO, minwidth=60, width=80)
        self.data_tree.heading('date', text='Start Date')
        self.data_tree.column('date', anchor=CENTER, stretch=NO, minwidth=60, width=80)
        self.data_tree.heading('designer', text='Designer')
        self.data_tree.column('designer', anchor=CENTER, stretch=NO, minwidth=60, width=75)
        self.data_tree.heading('activity', text='Activity')
        self.data_tree.column('activity', anchor=CENTER, stretch=NO, minwidth=60, width=80)
        self.data_tree.heading('days', text='Days')
        self.data_tree.column('days', anchor=CENTER, stretch=NO, minwidth=60, width=75)
        self.data_tree.heading('status', text='Status')
        self.data_tree.column('status', anchor=CENTER, stretch=NO, minwidth=60, width=75)

        self.data_tree.bind('<<TreeviewSelect>>', change_plan)

        mold_information()


class XYZ(object):
    def __init__(self, master):
        self.master = master
        self.master.title("Mold Design")
        # self.master.geometry("650x500")
        self.master.state('zoomed')
        Planning()


from ttkbootstrap import Style
# The main function
if __name__ == "__main__":
    root = Tk()
    style = Style(theme='flatly')

    obj = XYZ(root)
    root.mainloop()
