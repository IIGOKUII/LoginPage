from tkinter import *
from tkinter import ttk, filedialog
from tkinter import messagebox
from ttkbootstrap import DateEntry
import sqlite3
from datetime import datetime
from openpyxl import *
import warnings
from shared_var import shared_variable


class NewEntry(Toplevel):
    def __init__(self):
        Toplevel.__init__(self)
        self.title("New Mold Entry")
        self.focus_force()
        self.grab_set()
        self.resizable(FALSE, FALSE)

        warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# Set Window size and at center

        window_width = 1180
        window_height = 620
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cor = int((screen_width / 2) - (window_width / 2))
        y_cor = int((screen_height / 2.5) - (window_height / 2))
        self.geometry(f'{window_width}x{window_height}+{x_cor}+{y_cor}')
        self.minsize(int((screen_width / 2)), window_height)

# Var
        self.path = shared_variable.path

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
        self.request_id = IntVar()
        self.malt = StringVar()
        self.hrtype = StringVar()
        self.difficulty = StringVar()

# next_request_id #

        def next_request_id():
            current_date_time = datetime.now()
            current_month = current_date_time.month
            current_year = int(str(current_date_time.year)[2:])
            conn = sqlite3.connect(f"{self.path}database/MDShdb.db")

            cur = conn.cursor()
            cur.execute("Select Max(REQ_ID) from MOLD_TABLE")
            result = cur.fetchone()
            conn.close()
            # print(result)
            self.Id = result[0]

            if self.Id:
                last_entry_year = int(str(self.Id)[:2])

                if current_year > last_entry_year and current_month > 3:
                    self.request_id = int(str(current_year) + '00001')
                else:
                    self.request_id = self.Id + 1
            else:
                self.request_id = int(str(current_year) + '00001')

# Check blank widget function

        def check_blank_widgets(frame):
            blank_widgets = []
            for widget in frame.winfo_children():
                if isinstance(widget, Entry):
                    if widget.get().strip() == "":
                        blank_widgets.append(widget)
                elif isinstance(widget, Text):
                    if widget.get('1.0', 'end-1c').strip() == "":
                        blank_widgets.append(widget)
                elif isinstance(widget, Frame):
                    blank_widgets.extend(check_blank_widgets(widget))
            return blank_widgets

# Check blank widget function

        def clear_widgets():
            self.info_date.set("")
            self.mold_no.set("")
            self.machine_type.set("")
            self.cav_no.set("")
            self.ord_scp.set("")
            self.ord_typ.set("")
            self.iss_to.set("")
            self.zc_var.set("")
            self.qmc_var.set("")
            self.air_ejt_var.set("")
            self.pos_ver.set("")
            self.country.set("")
            self.bottle_no.set("")
            self.customer.set("")
            self.malt.set("")
            self.hrtype.set("")
            self.difficulty.set("")
            self.remark_text.delete("1.0", END)

# Import data from excel function

        def open_excel():
            # Open Excel and insert data into tree view
            book_path = filedialog.askopenfilename()
            if book_path != "":
                book = load_workbook(book_path)
                sheet = book.worksheets[0]
                cells = sheet['A2': f"S{sheet.max_row}"]
                list1 = []

                for c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19 in cells:
                    list1.append((c4.value, c5.value, c7.value, c16.value, c15.value, c9.value, c11.value, c17.value, c12.value, c1.value, c8.value, c14.value, c10.value, c18.value, c19.value))

                # Delete old data from tree view
                for item in self.tree.get_children():
                    self.tree.delete(item)

                for record in list1:
                    self.tree.insert('', END, values=record)
            else:
                pass

# Double click event for tree view entries

        def on_double_click(event):
            self.ord_typ.set('Design')
            self.iss_to.set('AI')

            try:
                selected_item = self.tree.selection()[0]
                self.mold_no.set(self.tree.item(selected_item)['values'][1].strip())
                self.info_date.set(self.tree.item(selected_item)['values'][0].replace(".", "/").strip())
                self.machine_type.set(self.tree.item(selected_item)['values'][3].strip())
                self.cav_no.set(str(self.tree.item(selected_item)['values'][4]).strip())
                self.ord_scp.set(dictionary1[self.tree.item(selected_item)['values'][5].upper().strip()])
                self.zc_var.set(dictionary2[self.tree.item(selected_item)['values'][6].upper().strip()])
                self.qmc_var.set(dictionary2[self.tree.item(selected_item)['values'][7].upper().strip()])
                self.air_ejt_var.set(dictionary2[self.tree.item(selected_item)['values'][8].upper().strip()])
                self.pos_ver.set(str(self.tree.item(selected_item)['values'][9]).strip())
                self.customer.set(self.tree.item(selected_item)['values'][2].strip())
                self.country.set(self.tree.item(selected_item)['values'][10].strip())
                self.bottle_no.set(self.tree.item(selected_item)['values'][11].strip())
                self.malt.set(self.tree.item(selected_item)['values'][13].strip())
                self.hrtype.set(self.tree.item(selected_item)['values'][14].strip())
                self.remark_text.delete("1.0", END)
                self.remark_text.insert("1.0", self.tree.item(selected_item)['values'][12].strip())
            except (KeyError, IndexError):
                pass

        # Submit function

        def submit_btn():

            # If statement to check blank widgets in frames if non of the widgets are blank data will be insert to MDShdb.db
            blank_widgets = check_blank_widgets(self.project_details)
            if blank_widgets:
                messagebox.showinfo("", 'Fill all "Mold Order Details"')
            else:
                blank_widgets = check_blank_widgets(self.Remarks_details)
                if blank_widgets:
                    messagebox.showinfo("", 'Fill all "Remark"')
                else:
                    # Next request id function
                    next_request_id()
                    # Get the data from remark text widget
                    remark = self.remark_text.get("1.0", "end")

                    conn = sqlite3.connect(f"{self.path}database/MDShdb.db")
                    cursor = conn.execute('SELECT * from MOLD_TABLE where MOLD_NO=?', (self.mold_no.get(),))
                    row = cursor.fetchone()

                    if row:
                        messagebox.showinfo("", "Mold No already exist")
                        conn.close()
                        clear_widgets()
                        selection = self.tree.selection()
                        self.tree.delete(selection)

                    else:
                        try:
                            cur = conn.cursor()
                            cur.execute('''INSERT INTO MOLD_TABLE 
                            (REQ_ID,INFO_DATE,MOLD_NO,CUSTOMER,MACHINE_TYPE,CAVITY,ORDER_SCOPE,ORDER_TYPE,ISSUE_TO,ZC,QMC,AIR_EJECT,POS_VER,REMARK,COUNTRY,CONTAINER_NO,PRE_PLAN_STATUS,MOLDING_MALT
                            ,HR_TYPE,DIFFICULTY) 
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                                        (self.request_id, self.info_date.get(), self.mold_no.get(), self.customer.get(), self.machine_type.get(), self.cav_no.get(), self.ord_scp.get(),
                                         self.ord_typ.get(), self.iss_to.get(), self.zc_var.get(), self.qmc_var.get(), self.air_ejt_var.get(), self.pos_ver.get(), remark, self.country.get(),
                                         self.bottle_no.get(), 0, self.malt.get(), self.hrtype.get(), self.difficulty.get()))
                            conn.commit()
                            conn.close()
                            messagebox.showinfo("Successful", "Initial Entry Done successfully!")
                            clear_widgets()
                            selection = self.tree.selection()
                            self.tree.delete(selection)

                        except Exception as er:
                            conn.close()
                            messagebox.showerror("Error!", f"{er}")

# Lists
        order_scope_name = ["Complete", "Injection", "Blow", "Parts Order"]

        order_type_name = ["Design", "Translation"]

        issue_to_name = ["AI", "HQ"]

        dictionary1 = {"F": 'Complete', "I": 'Injection', "B": 'Blow', "P": 'Parts Order', "NONE": "NONE"}

        dictionary2 = {"YES": "YES", "NO": "NO", "NA": "NO", "NONE": "NO", '': "NO"}

# Frame Project Details

        self.project_details = ttk.LabelFrame(self, text="Mold Order Details")
        self.project_details.place(x=20, y=20, width=350, height=540)

        # Entry fields in column 1 #

        self.mold_no_label = ttk.Label(self.project_details, text='Mold No:').grid(column=0, row=0)
        self.mold_no_Entry = ttk.Entry(self.project_details, textvariable=self.mold_no, width=20).grid(column=0, row=1)

        self.arrival_date_label = ttk.Label(self.project_details, text='Info Date:')
        self.arrival_date_label.grid(column=0, row=2)
        self.arrival_date_Entry = ttk.Entry(self.project_details, textvariable=self.info_date, width=20)
        # self.arrival_date_Entry = DateEntry(self.project_details, style='CalendarEntry.TEntry')width=20, date_pattern='dd/MM/yyyy', anchor='e'
        self.arrival_date_Entry.grid(column=0, row=3)

        self.machine_type_label = ttk.Label(self.project_details, text='Machine Type:').grid(column=0, row=4)
        self.machine_type_Comb = ttk.Entry(self.project_details, textvariable=self.machine_type, width=20).grid(column=0, row=5)

        self.cavitation_label = ttk.Label(self.project_details, text='No. of Cavity:').grid(column=0, row=6)
        self.cavitation_Comb = ttk.Combobox(self.project_details, textvariable=self.cav_no, width=18).grid(column=0, row=7)

        self.order_scope_label = ttk.Label(self.project_details, text="Order Scope:").grid(column=0, row=8)
        self.order_scope_Comb = ttk.Combobox(self.project_details, textvariable=self.ord_scp, width=18, state="readonly", values=order_scope_name).grid(column=0, row=9)

        self.order_type_label = ttk.Label(self.project_details, text='Order Type:').grid(column=0, row=10)
        self.order_type_Comb = ttk.Combobox(self.project_details, textvariable=self.ord_typ, width=18, state="readonly", values=order_type_name).grid(column=0, row=11)

        self.issue_to_label = ttk.Label(self.project_details, text='Issue To:').grid(column=0, row=12)
        self.issue_to_Comb = ttk.Combobox(self.project_details, textvariable=self.iss_to, width=18, state="readonly", values=issue_to_name).grid(column=0, row=13)

        self.pos_rev_label = ttk.Label(self.project_details, text='POS Revision:').grid(column=1, row=0)
        self.pos_rev_label = ttk.Entry(self.project_details, textvariable=self.pos_ver, width=20).grid(column=1, row=1)

        self.customer_label = ttk.Label(self.project_details, text='Customer:').grid(column=1, row=2)
        self.customer_Entry = ttk.Entry(self.project_details, textvariable=self.customer, width=20).grid(column=1, row=3)

        self.country_label = ttk.Label(self.project_details, text='Country:').grid(column=1, row=4)
        self.country_Entry = ttk.Entry(self.project_details, textvariable=self.country, width=20).grid(column=1, row=5)

        self.bottle_no_label = ttk.Label(self.project_details, text='Bottle No:').grid(column=1, row=6)
        self.bottle_no_Entry = ttk.Entry(self.project_details, textvariable=self.bottle_no, width=20).grid(column=1, row=7)

        self.material_label = ttk.Label(self.project_details, text='Molding Material:').grid(column=1, row=8)
        self.material_Entry = ttk.Entry(self.project_details, textvariable=self.malt, width=20).grid(column=1, row=9)

        self.hr_label = ttk.Label(self.project_details, text='HR Type:').grid(column=1, row=10)
        self.hr_Entry = ttk.Entry(self.project_details, textvariable=self.hrtype, width=20).grid(column=1, row=11)

        self.difficulty_label = ttk.Label(self.project_details, text='Difficulty:').grid(column=1, row=12)
        self.difficulty_entry = ttk.Combobox(self.project_details, textvariable=self.difficulty, width=18, state="readonly", values=('A', 'B', 'C', 'D', 'E')).grid(column=1, row=13)

        # Configure for all widgets in Project Details frame
        for widgets in self.project_details.winfo_children():
            widgets.grid_configure(padx=20, pady=4, sticky=W)

# Frame New Entry Details

        self.new_entry_details = ttk.LabelFrame(self, text="New Entry Details")
        self.new_entry_details.place(x=390, y=20, width=770, height=260)

        # defined columns for tree view
        columns = ('infodate', 'md_no', 'cust', 'mctype', 'cav', 'det', 'zc', 'qmc', 'Airej', 'ver', 'country', 'cdgno', 'remark', 'malt', 'hrtype')

        self.tree = ttk.Treeview(self.new_entry_details, columns=columns, show='headings')
        self.tree.place(x=10, y=10, width=725, height=205)  # .pack(side=LEFT, anchor=NW)

        self.scrollbar_v = ttk.Scrollbar(self.new_entry_details, orient='vertical', command=self.tree.yview)
        self.scrollbar_v.place(x=740, y=10, width=20, height=205)  # .pack(side=RIGHT, fill='y', anchor=NE)

        self.scrollbar_h = ttk.Scrollbar(self.new_entry_details, orient='horizontal', command=self.tree.xview)
        self.scrollbar_h.place(x=10, y=220, width=725, height=20)  # .pack(side=BOTTOM, fill='x')

        self.tree.heading('infodate', text='Info Date')
        self.tree.column('infodate', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('md_no', text='Mold No')
        self.tree.column('md_no', anchor=CENTER, stretch=NO, minwidth=90, width=100)
        self.tree.heading('cust', text='Customer')
        self.tree.column('cust', stretch=YES, minwidth=190, width=200)
        self.tree.heading('mctype', text='Machine')
        self.tree.column('mctype', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('cav', text='Cavitation')
        self.tree.column('cav', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('det', text='Scope')
        self.tree.column('det', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('zc', text='ZC')
        self.tree.column('zc', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('qmc', text='QMC')
        self.tree.column('qmc', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('Airej', text='Air Eject')
        self.tree.column('Airej', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('ver', text='POS-VER')
        self.tree.column('ver', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('country', text='COUNTRY')
        self.tree.column('country', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('cdgno', text='BOTTLE NO')
        self.tree.column('cdgno', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('malt', text='MATERIAL')
        self.tree.column('malt', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('hrtype', text='HR TYPE')
        self.tree.column('hrtype', anchor=CENTER, stretch=NO, minwidth=60, width=76)
        self.tree.heading('remark', text='REMARK')
        self.tree.column('remark', anchor=CENTER, stretch=NO, minwidth=60, width=200)

        self.tree.bind("<Double-1>", on_double_click)
        self.tree.configure(yscrollcommand=self.scrollbar_v.set)
        self.tree.configure(xscrollcommand=self.scrollbar_h.set)

# Frame Remarks

        self.Remarks_details = ttk.LabelFrame(self, text="Other Details")
        self.Remarks_details.place(x=390, y=300, width=770, height=260)

        self.Remarks_details1 = Frame(self.Remarks_details, bd=1, width=700, height=200, bg='yellow')
        self.Remarks_details1.pack(side='left', anchor='nw', pady=20)

        self.zc_label = ttk.Label(self.Remarks_details1, text='Zero Cooling:', justify=LEFT).grid(column=0, row=0, padx=20, sticky=NW)
        self.R1 = ttk.Radiobutton(self.Remarks_details1, text="Yes", variable=self.zc_var, value="YES").grid(column=1, row=0)
        self.R2 = ttk.Radiobutton(self.Remarks_details1, text="No", variable=self.zc_var, value="NO").grid(column=2, row=0)

        self.qmc_label = ttk.Label(self.Remarks_details1, text='Quick Mold Change:', justify=LEFT).grid(column=0, row=1, padx=20, sticky=NW)
        self.R3 = ttk.Radiobutton(self.Remarks_details1, text="Yes", variable=self.qmc_var, value="YES").grid(column=1, row=1, sticky=NW)
        self.R4 = ttk.Radiobutton(self.Remarks_details1, text="No", variable=self.qmc_var, value="NO").grid(column=2, row=1, sticky=NW)

        self.air_ejt_label = ttk.Label(self.Remarks_details1, text='Air Eject:', justify=LEFT).grid(column=0, row=2, padx=20, sticky=NW)
        self.R5 = ttk.Radiobutton(self.Remarks_details1, text="Yes", variable=self.air_ejt_var, value="YES").grid(column=1, row=2, sticky=NW)
        self.R6 = ttk.Radiobutton(self.Remarks_details1, text="No", variable=self.air_ejt_var, value="NO").grid(column=2, row=2, sticky=NW)

        self.Remarks_details2 = Frame(self.Remarks_details, bd=0, width=300, height=200, bg='red')
        self.Remarks_details2.pack(side='left')

        self.remark_label = ttk.Label(self.Remarks_details2, text='Remarks:', justify=LEFT).grid(column=3, row=0, padx=20, sticky=NW)
        self.remark_text = Text(self.Remarks_details2, width=68, height=12, font=('Arial', 10))
        self.remark_text.grid(column=3, row=1, padx=20, pady=5, sticky=NW)

        for widgets in self.Remarks_details1.winfo_children():
            widgets.grid_configure(padx=10, pady=5)

# Submit Button

        self.submit_btn = ttk.Button(self, text="Submit", command=submit_btn, width=10).place(x=1075, y=570)
        self.open_btn = ttk.Button(self, text="Open", command=open_excel, width=10).place(x=970, y=570)

