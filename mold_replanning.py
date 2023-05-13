from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from tkcalendar import Calendar
from datetime import datetime, timedelta
import pandas as pd
from shared_var import shared_variable


class RePlanning(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title("Mold Re-Planning")
        self.focus_force()
        self.grab_set()
        # self.resizable(FALSE, FALSE)

# Set Window size and Ser at center
        window_height = 780
        window_width = 1280
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cor = int((screen_width / 2) - (window_width / 2)) - 10
        y_cor = int((screen_height / 2.3) - (window_height / 2))

        self.geometry(f'{window_width}x{window_height}+{x_cor}+{y_cor}')
        self.minsize(int((screen_width / 2)), window_height)

        self.path = shared_variable.path

        # Entry Variable
        self.mold_no = StringVar()
        self.designer = StringVar()
        self.start_data = StringVar()
        self.end_data = StringVar()
        self.no_day = StringVar()
        self.new_designer = StringVar()
        self.old_designer = StringVar()
        self.tree_mold_no = StringVar()
        self.req_id = IntVar()
        self.activity = StringVar()

        self.DegnModel = StringVar()
        self.end_day = StringVar()

        uname = shared_variable.user_name

        def submit():

            selected_item = self.data_tree.selection()[0]

            blank_check = (self.req_id, self.tree_mold_no, self.start_data, self.new_designer, self.activity, self.no_day)

            blank_item = []
            for v in blank_check:
                if v.get() == "":
                    v.set("Input Required")
                    blank_item.append(v.get())

            if blank_item:
                return

            # Convert string to datetime object
            start_date = datetime.strptime(self.start_data.get(), "%d-%m-%Y")

            # Connect to the SQLite database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
            c = conn.cursor()

            c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.new_designer.get()}'")
            designer_tbl = c.fetchone()

            if not designer_tbl:
                messagebox.showinfo("Scheduler", "Please select the proper designer")
                return

            result = c.execute("SELECT YEAR2023 FROM holidaylist")
            holiday_list = tuple(date[0] for date in result.fetchall())

            cursor = conn.execute(f"SELECT * FROM {self.new_designer.get()} WHERE REQ_ID=? AND MOLD_NO=? AND ACTIVITY=? AND START_DATE=? AND DAYS_COUNT=? AND STATUS!=?",
                                  (self.req_id.get(), self.tree_mold_no.get(), self.activity.get(), datetime.strftime(start_date, "%Y-%m-%d"), self.no_day.get(), 5))

            row = cursor.fetchone()

            if row:
                conn.close()
                messagebox.showerror("Planning", "Same Plan already available")
                return

            c.execute(f"UPDATE {self.data_tree.item(selected_item)['values'][3]} SET STATUS=? WHERE REQ_ID=? AND ACTIVITY=?",
                      (5, self.req_id.get(), self.activity.get()))

            c.execute("UPDATE HEATMAP SET STATUS=? WHERE REQ_ID=? AND DESIGNER=? AND ACTIVITY=?",
                      (5, self.req_id.get(), self.data_tree.item(selected_item)['values'][3], self.activity.get()))

            # Define the input values
            if '.' in self.no_day.get():
                no_of_days = float(self.no_day.get())
            else:
                no_of_days = int(self.no_day.get())

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
                          (self.req_id.get(), self.tree_mold_no.get(), date_str, self.new_designer.get(), self.activity.get(), 1, 0, 'Planned', uname))
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
                          (self.req_id.get(), self.tree_mold_no.get(), date_str, self.new_designer.get(), self.activity.get(), no_of_days % 1, 0, 'Planned', uname))

            # reset the start date
            ob_date = datetime.strptime(self.start_data.get(), "%d-%m-%Y")
            start_date = datetime.strftime(ob_date, "%Y-%m-%d")

            c.execute(f"INSERT INTO {self.new_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)",
                      (self.req_id.get(), self.tree_mold_no.get(), self.activity.get(), start_date, self.end_day.get(), self.no_day.get(), 0, 'Planned'))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

            # Clear all label in planning_details
            for child in self.planning_details.winfo_children():
                child.destroy()

            get_plan_mold(self.tree_mold_no.get())

        def add_plan():
            selected_item = self.data_tree.selection()[0]

            blank_check = (self.req_id, self.tree_mold_no, self.start_data, self.new_designer, self.activity, self.no_day)

            blank_item = []
            for v in blank_check:
                if v.get() == "":
                    v.set("Input Required")
                    blank_item.append(v.get())

            if blank_item:
                return

            # Connect to the SQLite database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
            c = conn.cursor()

            c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.new_designer.get()}'")
            designer_tbl = c.fetchone()

            if not designer_tbl:
                messagebox.showinfo("Scheduler", "Please select the proper designer")
                return

            result = c.execute("SELECT YEAR2023 FROM holidaylist")
            holiday_list = tuple(date[0] for date in result.fetchall())

            cursor = conn.execute(f"SELECT * FROM {self.new_designer.get()} WHERE REQ_ID=? AND MOLD_NO=? AND ACTIVITY=? AND STATUS!=?",
                                  (self.req_id.get(), self.tree_mold_no.get(), self.activity.get(), 5))

            row = cursor.fetchone()

            if row:
                conn.close()
                messagebox.showerror("Planning", "Same Plan already available")
                return

            # Define the input values
            if '.' in self.no_day.get():
                no_of_days = float(self.no_day.get())
            else:
                no_of_days = int(self.no_day.get())

            # Convert string to datetime object
            start_date = datetime.strptime(self.start_data.get(), "%d-%m-%Y")

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
                          (self.req_id.get(), self.tree_mold_no.get(), date_str, self.new_designer.get(), self.activity.get(), 1, 0, 'Planned', uname))
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
                          (self.req_id.get(), self.tree_mold_no.get(), date_str, self.new_designer.get(), self.activity.get(), no_of_days % 1, 0, 'Planned', uname))

            # reset the start date
            ob_date = datetime.strptime(self.start_data.get(), "%d-%m-%Y")
            start_date = datetime.strftime(ob_date, "%Y-%m-%d")

            c.execute(f"INSERT INTO {self.new_designer.get()} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)",
                      (self.req_id.get(), self.tree_mold_no.get(), self.activity.get(), start_date, self.end_day.get(), self.no_day.get(), 0, 'Planned'))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

            # Clear all label in planning_details
            for child in self.planning_details.winfo_children():
                child.destroy()

            get_plan_mold(self.tree_mold_no.get())

        def sel_dsgn(event, arg):

            # Update variables from tree view
            try:
                selected_item = self.tree.selection()[0]
                arg.set(self.tree.item(selected_item)['values'][0])
            except IndexError:
                if arg.get() == '':
                    arg.set('Select Designer')

        def get_designers(m_date):

            McModelCon = {"ASB-70DPH": 'DPH', "ASB-70DPW": 'DPH', "ASB-50MB": 'FMB', "ASB-12M": 'FMB', "PF": 'PF', "Preform": 'PFM', "Modification": 'MOD', "Parts Order": 'PART'}

            selection = ''

            # get the selected value from the combobox
            if selection == '':
                selection = self.DegnModel.get()

            # get the required dict
            r_dict = McModelCon[selection]

            designers_list = {
                'DPH': ("AKS", "AGM", "AMR", "ASJ", "DNU", "DPS", "DIV", "KKR", "MSD", "MDP", "PRT", "RAN", "RPA", "SGR", "SRM", "SSP", "SSN", "SWL", "VIR"),
                'FMB': ("ANS", "ASP", "ARG", "CSD", "GGP", "KSB", "ADS", "RSB", "RPS", "SSY", "SKV", "SHC", "KVS", "VKD", "VIN", "VSP", "YDS", "ADK"),
                'MOD': ("ASR", "GCG", "RKG", "RVI", "STP"),
                'PART': ("HKN", "YSM"),
                'PF': ("ATL", "BJS", "GRV", "GAN", "KIR", "LAK", "NDS", "PKL", "SGA", "SKP"),
                'PFM': ("RAK", "ANK", "PKS", "PTK", "PNM", "RAD", "SAB")
            }

            # Define the column headings for the dates
            date_columns = [(m_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]

            names = designers_list[r_dict]

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
            result = result.reindex(designers_list[r_dict])
            result.reset_index(inplace=True)

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

        # Date Entry widget function
        def open_cal(event, arg, pos):
            if self.DegnModel.get() != '':
                my_w_child = Toplevel(pos)
                x = arg.winfo_rootx() + 110
                y = arg.winfo_rooty() - 225
                my_w_child.geometry(f"250x230+{x}+{y}")
                my_w_child.grab_set()
                my_w_child.title("Calender")

                def grab_date():
                    # Convert string to datetime object
                    date_object = datetime.strptime(cal.get_date(), "%Y-%m-%d")
                    arg.delete(0, END)
                    arg.insert(0, datetime.strftime(date_object, '%d-%m-%Y'))
                    my_w_child.destroy()
                    get_designers(datetime.strptime(cal.get_date(), '%Y-%m-%d'))

                def close_function():
                    arg.delete(0, END)
                    my_w_child.destroy()

                cal = Calendar(my_w_child, selectmode='day', date_pattern="yyyy-mm-dd")
                cal.grid(row=0, column=0, columnspan=2)

                submit_btn = ttk.Button(my_w_child, text="Submit", command=grab_date, width=12)
                submit_btn.grid(row=1, column=0, pady=5)

                close_btn = ttk.Button(my_w_child, text="Clear", command=close_function, width=12)
                close_btn.grid(row=1, column=1, pady=5)
            else:
                arg.delete(0, END)
                arg.insert(0, 'Missing Input')

        def re_plan_data(event):

            designers_list = {
                'ASB-70DP': ("AKS", "AGM", "AMR", "ASJ", "DNU", "DPS", "DIV", "KKR", "MSD", "MDP", "PRT", "RAN", "RPA", "SGR", "SRM", "SSP", "SSN", "SWL", "VIR"),
                'ASB-12M': ("ANS", "ASP", "ARG", "CSD", "GGP", "KSB", "ADS", "RSB", "RPS", "SSY", "SKV", "SHC", "KVS", "VKD", "VIN", "VSP", "YDS", "ADK"),
                'Modification': ("ASR", "GCG", "RKG", "RVI", "STP"),
                'Parts Order': ("HKN", "YSM"),
                'PF': ("ATL", "BJS", "GRV", "GAN", "KIR", "LAK", "NDS", "PKL", "SGA", "SKP"),
                'Preform': ("RAK", "ANK", "PKS", "PTK", "PNM", "RAD", "SAB")
            }

            # Get key for value 2
            for key, value in designers_list.items():
                if self.new_designer.get() in value:
                    selected = key

            try:
                selected_item = self.data_tree.selection()[0]
            except IndexError:
                return

            self.old_designer.set(self.data_tree.item(selected_item)['values'][3])

            self.req_id.set(self.data_tree.item(selected_item)['values'][0])
            self.tree_mold_no.set(self.data_tree.item(selected_item)['values'][1])
            self.start_data.set(self.data_tree.item(selected_item)['values'][2])
            self.new_designer.set(self.data_tree.item(selected_item)['values'][3])
            self.activity.set(self.data_tree.item(selected_item)['values'][4])
            self.no_day.set(self.data_tree.item(selected_item)['values'][5])

            widgets_show()

            for p_widgets in self.planning_details.winfo_children():
                p_widgets.grid_configure(padx=5, pady=4)

        def get_plan_tree(event):
            # Clear all label in planning_details
            for child in self.planning_details.winfo_children():
                child.destroy()

            # Update variables from tree view
            try:
                selected_item = self.project_tree.selection()[0]
                get_plan_mold(self.project_tree.item(selected_item)['values'][1])
            except IndexError:
                return

        def get_plan_mold(mold_no):
            try:
                conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

                # define query
                query = 'SELECT * FROM HEATMAP WHERE MOLD_NO=? AND STATUS=?'

                # Define the query parameters
                params = (mold_no.upper(), '0')

                # Execute a SELECT statement with a WHERE clause
                df_project_mold = pd.read_sql(query, conn, params=params)

                # group by and aggregate the 'DAYS' olumn
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

        def get_plan():

            # Clear all label in planning_details
            for child in self.planning_details.winfo_children():
                child.destroy()

            if self.mold_no.get() == '' and self.designer.get() == '':
                pass

            elif self.mold_no.get() == '' and self.designer.get() != '':
                conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

                # define query
                query = f'SELECT * FROM {self.designer.get()} WHERE STATUS = ?'

                # Define the query parameters
                params = '0'

                # Execute a SELECT statement with a WHERE clause
                df_project_dsgn = pd.read_sql(query, conn, params=params)

                conn.close()

                df_project_dsgn['DESIGNER'] = self.designer.get().upper()

                df_project_dsgn = df_project_dsgn[['REQ_ID', 'MOLD_NO', 'START_DATE', 'DESIGNER', 'ACTIVITY', 'DAYS_COUNT', 'STATUS']]

                # convert 'DATE' column to datetime format
                df_project_dsgn['START_DATE'] = pd.to_datetime(df_project_dsgn['START_DATE'], dayfirst=True)

                # Convert date column to '%d-%m-%Y' format
                df_project_dsgn['START_DATE'] = pd.to_datetime(df_project_dsgn['START_DATE']).dt.strftime('%d-%m-%Y')

                # Delete all data from the TreeView
                self.data_tree.delete(*self.data_tree.get_children())

                # Insert the data into the TreeView
                for i, row in df_project_dsgn.iterrows():
                    values = tuple(row.values)
                    self.data_tree.insert("", "end", text=i, values=values)

            else:
                get_plan_mold(self.mold_no.get())

        def get_projects():

            # Connect to the SQLite database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

            # define query
            query = "SELECT * FROM HEATMAP WHERE STATUS = ?"

            # Define the query parameters
            params = '0'

            # Execute a SELECT statement with a WHERE clause
            df_project = pd.read_sql(query, conn, params=params)

            # Close the connection
            conn.close()

            # group by and aggregate the 'DAYS' column
            df_project = df_project.groupby(['REQ_ID', 'STATUS'], as_index=False).agg({'DAYS': 'sum', 'DATE': 'first', 'MOLD_NO': 'first', 'ACTIVITY': 'first'})

            # convert date to integer value
            df_project['DAYS'] = df_project['DAYS'].astype(int)

            # convert 'DATE' column to datetime format
            df_project['DATE'] = pd.to_datetime(df_project['DATE'], dayfirst=True)

            # add new column that is the sum of 'DATE' and 'DAYS'
            df_project['END_DATE'] = df_project['DATE'] + pd.to_timedelta(df_project['DAYS'], unit='d')

            # Sort date as close date will be shown first
            df_project = df_project.sort_values('END_DATE')   # .reset_index()

            # Convert date column to '%d-%m-%Y' format
            df_project['END_DATE'] = pd.to_datetime(df_project['END_DATE']).dt.strftime('%d-%m-%Y')

            # create new dataframe from df_project with required column
            new_df = df_project[['REQ_ID', 'MOLD_NO', 'END_DATE']]

            # Insert the data into the TreeView
            for i, row in new_df.iterrows():
                values = tuple(row.values)
                self.project_tree.insert("", "end", text=i, values=values)

        def clear_designer(event):
            self.designer.set('')

        def clear_mold_no(event):
            self.mold_no.set('')

        def widgets_show():
            # Labels Heading

            mc_model_values2 = ('ASB-70DPH', 'ASB-12M', 'PF', 'Preform', 'Modification', 'Parts Order', 'ECM')

            activities = ("Preform", "Assembly", "Assembly Check", "Detailing", "Checking", "Second Check", "Issue")

            self.req_id_label = ttk.Label(self.planning_details, text='Request ID:').grid(column=1, row=1, sticky="W")
            self.mold_no_label = ttk.Label(self.planning_details, text='Mold No:').grid(column=1, row=2, sticky="W")
            self.Designer_label = ttk.Label(self.planning_details, text='Designers Group:').grid(column=1, row=3, sticky="W")
            self.start_label = ttk.Label(self.planning_details, text='Start Date:').grid(column=1, row=4, sticky="W")
            self.design_label = ttk.Label(self.planning_details, text='Designer:').grid(column=1, row=5, sticky="W")
            self.activity_label = ttk.Label(self.planning_details, text='Activity:').grid(column=1, row=6, sticky="W")
            self.end_label = ttk.Label(self.planning_details, text='No of Days:').grid(column=1, row=7, sticky="W")

            # Request ID
            self.req_id_entry = ttk.Entry(self.planning_details, textvariable=self.req_id, width=15).grid(column=2, row=1, padx=20, pady=4)

            # Mold No
            self.mold_no_entry = ttk.Entry(self.planning_details, textvariable=self.tree_mold_no, width=15).grid(column=2, row=2, padx=20, pady=4)

            # Design Model
            self.Designer_Comb = ttk.Combobox(self.planning_details, textvariable=self.DegnModel, width=15, values=mc_model_values2).grid(column=2, row=3, padx=20, pady=4)

            # Start date
            self.P_start_date = ttk.Entry(self.planning_details, textvariable=self.start_data, width=15)
            self.P_start_date.grid(column=2, row=4, padx=20, pady=4)
            self.P_start_date.bind('<1>', lambda event, arg=self.P_start_date, pos=self.planning_details: open_cal(event, arg, pos))

            # Designers data
            self.P_designer = ttk.Entry(self.planning_details, textvariable=self.new_designer, width=15)
            self.P_designer.grid(column=2, row=5)
            self.P_designer.bind('<1>', lambda event, arg=self.new_designer: sel_dsgn(event, arg))

            # activity
            self.activity_entry = ttk.Combobox(self.planning_details, textvariable=self.activity, width=15, values=activities).grid(column=2, row=6, padx=20, pady=4)

            # End date
            self.P_end_date = ttk.Entry(self.planning_details, textvariable=self.no_day, width=15).grid(column=2, row=7, padx=20, pady=4)

            self.submit_btn = ttk.Button(self.planning_details, text="Update Plan", command=submit, width=10).grid(column=2, row=8, padx=20, pady=44)

            self.add_btn = ttk.Button(self.planning_details, text="Add Plan", command=add_plan, width=10).grid(column=1, row=8, padx=20, pady=44)

# Input data

        self.mold_details = ttk.LabelFrame(self, text="Input data:")
        self.mold_details.place(x=680, y=300, width=200, height=270)
        self.mold_details.columnconfigure((0, 1), weight=1)

        self.Mold_No_label = ttk.Label(self.mold_details, text='Mold No:').pack(side='top', pady=5)
        self.Mold_No_entry = ttk.Entry(self.mold_details, textvariable=self.mold_no, width=15)
        self.Mold_No_entry.pack(side='top', pady=5)
        self.Mold_No_entry.bind('<FocusIn>', clear_designer)

        self.designer_label = ttk.Label(self.mold_details, text='Designer:').pack(side='top', pady=5)
        self.designer_entry = ttk.Entry(self.mold_details, textvariable=self.designer, width=15)
        self.designer_entry.pack(side='top', pady=5)
        self.designer_entry.bind('<FocusIn>', clear_mold_no)

        self.get_btn = ttk.Button(self.mold_details, text="Get Plan", command=get_plan, width=12).pack(side='top', pady=5)

# Running Molds

        self.mold_details = ttk.LabelFrame(self, text="Working Projects")
        self.mold_details.place(x=955, y=300, width=295, height=420)
        self.mold_details.columnconfigure((0, 1), weight=1)

        columns = ('reqid', 'md_no', 'date')
        self.project_tree = ttk.Treeview(self.mold_details, columns=columns, show='headings')
        self.project_tree.place(x=10, y=10, width=260, height=380)

        self.scrollbar_v = ttk.Scrollbar(self.mold_details, orient='vertical', command=self.project_tree.yview)
        self.scrollbar_v.place(x=270, y=10, width=20, height=380)

        self.project_tree.heading('reqid', text='Request ID')
        self.project_tree.column('reqid', anchor=CENTER, stretch=NO, minwidth=75, width=75)
        self.project_tree.heading('md_no', text='Mold No')
        self.project_tree.column('md_no', anchor=CENTER, stretch=NO, minwidth=100, width=100)
        self.project_tree.heading('date', text='End Date')
        self.project_tree.column('date', anchor=CENTER, stretch=NO, minwidth=75, width=75)

        get_projects()

        self.project_tree.bind("<Double-1>", get_plan_tree)
        self.project_tree.configure(yscrollcommand=self.scrollbar_v.set)

# Planning Info

        self.planning_details = ttk.LabelFrame(self, text="Planning Information")
        self.planning_details.place(x=20, y=300, width=300, height=420)
        self.planning_details.columnconfigure((0, 1, 2, 3), weight=1)

# Frame New Entry Details

        self.new_entry_details = ttk.LabelFrame(self, text="Plan Data")
        self.new_entry_details.place(x=20, y=20, width=650, height=260)

        columns = ('reqid', 'md_no', 'date', 'designer', 'activity', 'days', 'status')
        self.data_tree = ttk.Treeview(self.new_entry_details, columns=columns, show='headings')
        self.data_tree.place(x=10, y=10, width=615, height=210)

        self.scrollbar_v = ttk.Scrollbar(self.new_entry_details, orient='vertical', command=self.data_tree.yview)
        self.scrollbar_v.place(x=625, y=10, width=20, height=210)

        self.scrollbar_h = ttk.Scrollbar(self.new_entry_details, orient='horizontal', command=self.data_tree.xview)
        self.scrollbar_h.place(x=10, y=220, width=615, height=20)

        self.data_tree.heading('reqid', text='Request ID')
        self.data_tree.column('reqid', anchor=CENTER, stretch=NO, minwidth=60, width=80)
        self.data_tree.heading('md_no', text='Mold No')
        self.data_tree.column('md_no', anchor=CENTER, stretch=NO, minwidth=60, width=100)
        self.data_tree.heading('date', text='Start Date')
        self.data_tree.column('date', anchor=CENTER, stretch=NO, minwidth=60, width=100)
        self.data_tree.heading('designer', text='Designer')
        self.data_tree.column('designer', anchor=CENTER, stretch=NO, minwidth=60, width=75)
        self.data_tree.heading('activity', text='Activity')
        self.data_tree.column('activity', anchor=CENTER, stretch=NO, minwidth=60, width=100)
        self.data_tree.heading('days', text='Days')
        self.data_tree.column('days', anchor=CENTER, stretch=NO, minwidth=60, width=75)
        self.data_tree.heading('status', text='Status')
        self.data_tree.column('status', anchor=CENTER, stretch=NO, minwidth=60, width=75)

        self.data_tree.bind("<Double-1>", re_plan_data)
        self.data_tree.configure(yscrollcommand=self.scrollbar_v.set)
        self.data_tree.configure(xscrollcommand=self.scrollbar_h.set)

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
