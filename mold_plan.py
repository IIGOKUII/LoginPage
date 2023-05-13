import sqlite3
import pandas as pd
from shared_var import shared_variable
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename


class MoldPlan(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title("Mold Plan")
        # self.focus_force()
        # self.grab_set()
        self.state('zoomed')
        self.overrideredirect(False)
        self.minsize(int(self.winfo_width()/2), int(self.winfo_height()/2))

        self.path = shared_variable.path

        def get_mold_plan():

            # Connect to database
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

            # define query
            query = f"SELECT * FROM HEATMAP WHERE MOLD_NO NOT IN (SELECT MOLD_NO FROM HEATMAP WHERE ACTIVITY=? AND STATUS>?)"

            # Define the query parameters
            params = ('Issue', 3)

            # Execute a SELECT statement with a WHERE clause
            df1 = pd.read_sql(query, conn, params=params)

            # define query
            query2 = f"SELECT MOLD_NO,DATE FROM HEATMAP WHERE ACTIVITY=? AND MOLD_NO NOT IN (SELECT MOLD_NO FROM HEATMAP WHERE ACTIVITY=? AND STATUS>?)"

            # Define the query parameters
            params2 = ('Issue', 'Issue', 3)

            # Execute a SELECT statement with a WHERE clause
            df2 = pd.read_sql(query2, conn, params=params2)

            # Close the connection
            conn.close()

            df1 = df1.sort_values(by=['DATE', 'STATUS'], ascending=[False, True])

            df1 = df1.groupby(['MOLD_NO', 'ACTIVITY', 'STATUS', 'STATUS_REMARK'], as_index=False).agg({'STATUS_REMARK': 'first'})

            # create the pivot table
            pivot_table = pd.pivot_table(df1, index=['MOLD_NO'], columns='ACTIVITY', values='STATUS_REMARK', aggfunc='first')

            # Reindex the columns to ensure that all desired columns are present
            desired_columns = ['Preform', 'Assembly', 'Assembly Check', 'Detailing', 'Checking', 'Correction', 'Second Check', 'Issue']
            pivot_table = pivot_table.reindex(columns=desired_columns)

            # Convert to DataFrame
            df = pd.DataFrame(pivot_table.to_records()).fillna('Not Planned')

            # merge the dataframes on 'MOLD_NO'
            df = pd.merge(df, df2[['MOLD_NO', 'DATE']], on='MOLD_NO', how='left')

            df = df[['MOLD_NO', 'DATE', 'Preform', 'Assembly', 'Assembly Check', 'Detailing', 'Checking', 'Correction', 'Second Check', 'Issue']]

            self.df = df.sort_values(by='DATE')

            # Insert the data into the TreeView
            for i, row in df.iterrows():
                values = tuple(row.values)
                self.data_tree.insert("", "end", text=i, values=values)

        def save_dataframe_to_excel():
            # Create a Tkinter file dialog to select a file
            file_path = asksaveasfilename(defaultextension='.xlsx')

            # If a file was selected, save the DataFrame to it
            if file_path:
                self.df.to_excel(file_path, index=False)

        def get_plan_mold(event):

            try:
                for item in self.mold_data_tree.get_children():
                    self.mold_data_tree.delete(item)
            except AttributeError:
                pass

            try:
                selected_item = self.data_tree.selection()[0]
                mold_no = self.data_tree.item(selected_item)['values'][0]
            except IndexError:
                try:
                    selected_item = self.data_tree.selection()[0]
                    mold_no = self.data_tree.item(selected_item)['values'][0]
                except IndexError:
                    return

            try:
                conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

                # define query
                query = 'SELECT * FROM HEATMAP WHERE MOLD_NO=? AND STATUS<?'

                # Define the query parameters
                params = (mold_no.upper(), '5')

                # Execute a SELECT statement with a WHERE clause
                df_project_mold = pd.read_sql(query, conn, params=params)

                # group by and aggregate the 'DAYS' column
                df_project_mold = df_project_mold.groupby(['REQ_ID', 'MOLD_NO', 'DESIGNER', 'ACTIVITY', 'STATUS_REMARK'], as_index=False).agg({'DAYS': 'sum', 'DATE': 'first'})
                df_project_mold = df_project_mold[['REQ_ID', 'MOLD_NO', 'DATE', 'DESIGNER', 'ACTIVITY', 'DAYS', 'STATUS_REMARK']]

                # convert 'DATE' column to datetime format
                df_project_mold['DATE'] = pd.to_datetime(df_project_mold['DATE'], dayfirst=True)

                # Convert date column to '%d-%m-%Y' format
                df_project_mold['DATE'] = pd.to_datetime(df_project_mold['DATE']).dt.strftime('%d-%m-%Y')

                # Frame New Entry Details
                self.new_entry_details = Frame(self, width=750, height=300)
                self.new_entry_details.place(x=25, y=710)

                columns = {
                    'reqid': {'text': 'Request ID', 'width': 80},
                    'md_no': {'text': 'Mold No', 'width': 100},
                    'date': {'text': 'Start Date', 'width': 100},
                    'designer': {'text': 'Designer', 'width': 75},
                    'activity': {'text': 'Activity', 'width': 100},
                    'days': {'text': 'Days', 'width': 75},
                    'status': {'text': 'Status', 'width': 175},
                }

                self.mold_data_tree = ttk.Treeview(self.new_entry_details, columns=list(columns.keys()), show='headings', style='Custom.Treeview')
                self.mold_data_tree.place(x=0, y=10, width=715, height=280)

                for col_name, col_data in columns.items():
                    self.mold_data_tree.heading(col_name, text=col_data['text'])
                    self.mold_data_tree.column(col_name, anchor=CENTER, stretch=NO, minwidth=60, width=col_data['width'])

                # Insert the data into the TreeView
                for i, row in df_project_mold.iterrows():
                    values = tuple(row.values)
                    self.mold_data_tree.insert("", "end", text=i, values=values)
            except ValueError:
                pass

        # Create a custom style for the Treeview widget
        style = ttk.Style()
        style.configure('Custom.Treeview', rowheight=25, font=(None, 11))

        columns1 = [('Mold_no', 125), ('Date', 125), ('Preform', 175), ('Assembly', 175), ('Assembly_Check', 235), ('Detailing', 175), ('Checking', 175),
                    ('Correction', 235), ('Second_Check', 235), ('Issue', 175)]
        self.data_tree = ttk.Treeview(self, columns=[col[0] for col in columns1], show="headings", style='Custom.Treeview')

        for col in columns1:
            self.data_tree.column(col[0], width=col[1], anchor=CENTER)
            self.data_tree.heading(col[0], text=col[0])

        self.data_tree.place(x=25, y=10, width=self.winfo_width() - 60, height=700)
        self.data_tree.bind("<<TreeviewSelect>>", get_plan_mold)

        self.scrollbar_v = ttk.Scrollbar(self, orient='vertical', command=self.data_tree.yview)
        self.scrollbar_v.place(x=self.winfo_width()-30, y=10, width=20, height=700)

        self.data_tree.configure(yscrollcommand=self.scrollbar_v.set)

        get_mold_plan()

        self.export_button = ttk.Button(self, text='Export', cursor='hand2', style="Accent.TButton", width=20, command=save_dataframe_to_excel)
        self.export_button.place(x=900, y=800)
