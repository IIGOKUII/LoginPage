import sqlite3
import pandas as pd
from datetime import datetime, date, time, timedelta
from shared_var import shared_variable


def get_designer_plan(path, initial):
    """
    :param path:
    :param initial:
    :return dataframe of planned designers work:
    """
    conn = sqlite3.connect(path)

    # define query
    query = f'SELECT REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,STATUS_REMARK FROM {initial} WHERE STATUS = ?'

    # Define the query parameters
    params = '0'

    # Execute a SELECT statement with a WHERE clause
    df_project = pd.read_sql(query, conn, params=params)

    # Close the connection
    conn.close()

    # Convert date column to '%d-%m-%Y' format
    df_project['END_DATE'] = pd.to_datetime(df_project['END_DATE']).dt.strftime('%d-%m-%Y')

    # Convert date column to '%d-%m-%Y' format
    df_project['START_DATE'] = pd.to_datetime(df_project['START_DATE']).dt.strftime('%d-%m-%Y')

    return df_project


def get_designer_working_plan(path, initial):
    """
    :param path:
    :param initial:
    :return dataframe of working designers work:
    """
    conn = sqlite3.connect(path)

    # define query
    query = f'SELECT REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,STATUS_REMARK FROM {initial} WHERE STATUS = ?'

    # Define the query parameters
    params = '1'

    # Execute a SELECT statement with a WHERE clause
    df_project = pd.read_sql(query, conn, params=params)

    # Close the connection
    conn.close()

    # Convert date column to '%d-%m-%Y' format
    df_project['END_DATE'] = pd.to_datetime(df_project['END_DATE']).dt.strftime('%d-%m-%Y')

    # Convert date column to '%d-%m-%Y' format
    df_project['START_DATE'] = pd.to_datetime(df_project['START_DATE']).dt.strftime('%d-%m-%Y')

    return df_project


def plan_by_mold(path, mold_no):
    """
    :param path:
    :param mold_no:
    :return: dataframe of mold plan status by mold number
    """
    try:
        conn = sqlite3.connect(path)

        # define query
        query = 'SELECT * FROM HEATMAP WHERE MOLD_NO=? AND STATUS<?'

        # Define the query parameters
        params = (mold_no.upper(), '5')

        # Execute a SELECT statement with a WHERE clause
        df_project_mold = pd.read_sql(query, conn, params=params)

        # Close the connection
        conn.close()

        # group by and aggregate the 'DAYS' column
        df_project_mold = df_project_mold.groupby(['REQ_ID', 'MOLD_NO', 'DESIGNER', 'ACTIVITY', 'STATUS_REMARK'], as_index=False).agg({'DAYS': 'sum', 'DATE': 'first'})
        df_project_mold = df_project_mold[['REQ_ID', 'MOLD_NO', 'DATE', 'DESIGNER', 'ACTIVITY', 'DAYS', 'STATUS_REMARK']]

        # convert 'DATE' column to datetime format
        df_project_mold['DATE'] = pd.to_datetime(df_project_mold['DATE'], dayfirst=True)

        # Convert date column to '%d-%m-%Y' format
        df_project_mold['DATE'] = pd.to_datetime(df_project_mold['DATE']).dt.strftime('%d-%m-%Y')

        return df_project_mold
    except ValueError:
        pass


def get_birthday(path):
    """
    :param path:
    :return: return list of todays birthday
    """
    today_date = date.today()

    conn = sqlite3.connect(f"{path}database/AIdesigner.db")
    cur = conn.cursor()
    cur.execute("SELECT EMP_NAME FROM ADMIN WHERE strftime('%m-%d', DOB) = ?", (today_date.strftime('%m-%d'),))  # execute a simple SQL select query
    names = cur.fetchall()
    conn.close()
    return names


def update_status(path, leave_path, initial, enp_id, status_remark, status, req_id, activity):
    start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA JOURNAL_MODE='wal' ")

    # Execute a SELECT statement with a WHERE clause
    cursor.execute(f'SELECT START_DATE_ACT,PAUSE,ACT_HOURS FROM {initial} WHERE STATUS = ?', (1,))
    data = cursor.fetchall()

    if data:
        if data[0][1]:
            _start = data[0][1]
        else:
            _start = data[0][0]
        work_hours = working_hour(leave_path, _start, data[0][2], enp_id)
        cursor.execute(f"update {initial} set STATUS_REMARK=?,ACT_HOURS=?,PAUSE=? where STATUS=? AND STATUS_REMARK!=?", ("Pause", work_hours, start_date, 1, "Pause"))
        cursor.execute(f"update HEATMAP set STATUS_REMARK=? where DESIGNER=? AND STATUS=? AND STATUS_REMARK!=?", ("Pause", work_hours, 1, "Pause"))

    cursor.execute(f"update {initial} set STATUS_REMARK=?,STATUS=?,START_DATE_ACT=? where REQ_ID=? AND ACTIVITY=? AND STATUS!=?",
                   (status_remark, status, start_date, req_id, activity, 5))
    cursor.execute(f"update HEATMAP set STATUS_REMARK=?,STATUS=? where REQ_ID=? AND ACTIVITY=? AND DESIGNER=? AND STATUS!=?",
                   (status_remark, status, req_id, activity, initial, 5))
    conn.commit()
    conn.close()


def working_hour(leave_path, a_start, old_work_hours, user):
    shift = shared_variable.shift
    if shift == "F":
        shift_in = time(7, 0)
        shift_out = time(15, 15)
        tea_break_1_start_time = time(8, 0)
        tea_break_1_end_time = time(9, 10)
        lunch_break_start_time = time(11, 0)
        lunch_break_end_time = time(11, 30)
        tea_break_2_start_time = time(14, 0)
        tea_break_2_end_time = time(14, 10)
    elif shift == "G":
        shift_in = time(9, 0)
        shift_out = time(17, 30)
        tea_break_1_start_time = time(11, 0)
        tea_break_1_end_time = time(11, 10)
        lunch_break_start_time = time(13, 20)
        lunch_break_end_time = time(13, 50)
        tea_break_2_start_time = time(16, 10)
        tea_break_2_end_time = time(16, 20)
    elif shift == "S":
        shift_in = time(15, 15)
        shift_out = time(23, 15)
        tea_break_1_start_time = time(17, 0)
        tea_break_1_end_time = time(17, 10)
        lunch_break_start_time = time(20, 0)
        lunch_break_end_time = time(20, 30)
        tea_break_2_start_time = time(22, 10)
        tea_break_2_end_time = time(22, 20)
    else:
        shift_in = time(9, 0)
        shift_out = time(17, 30)
        tea_break_1_start_time = time(11, 0)
        tea_break_1_end_time = time(11, 10)
        lunch_break_start_time = time(13, 20)
        lunch_break_end_time = time(13, 50)
        tea_break_2_start_time = time(16, 10)
        tea_break_2_end_time = time(16, 20)

    holidays = [_date for _date in shared_variable.holidays[1:] if _date is not None]
    weekly_off_day = 6  # Sunday is the 7th day of the week, so its index is 6
    holiday_list = []
    for holiday in holidays:
        year, month,  day = holiday.split('-')
        day = int(day)
        month = int(month)
        year = int(year)
        holiday_date = date(year, month, day)
        holiday_list.append(holiday_date)

    conn = sqlite3.connect(leave_path)
    cursor = conn.cursor()
    cursor.execute(f'SELECT Leave_days from leavedatabase WHERE User_ID=? AND Leave_Status=?', (user, "Approved",))
    fetch = cursor.fetchall()
    conn.close()

    # using list comprehension
    if len(fetch) == 0:
        leave_list = ['01/01/2023']
    else:
        out = [item for t in fetch for item in t]
        leave_list = ['01/01/2023']
        for stringA in out:
            li = list(stringA.split(" "))
            for i in li:
                leave_list.append(i)

    final_leave_list = []
    for leave in leave_list:
        day, month, year = leave.split('/')
        day = int(day)
        month = int(month)
        year = int(year)
        leave_date = date(year, month, day)
        final_leave_list.append(leave_date)

    aa_start, aa_time = a_start.split(' ')
    syear, smonth, sday = aa_start.split('-')
    shh, smm, sss = aa_time.split(':')
    start_date = date(int(syear), int(smonth), int(sday))
    start_time = time(int(shh), int(smm), int(sss))

    aa_end, aa_end_time = (datetime.now().strftime("%d/%m/%Y %H:%M:%S")).split(' ')
    eday, emonth, eyear = aa_end.split('/')
    ehh, emm, ess = aa_end_time.split(':')
    end_date = date(int(eyear), int(emonth), int(eday))
    end_time = time(int(ehh), int(emm), int(ess))

    # Define a function to calculate actual working hours
    total_working_hours = old_work_hours

    # Iterate over each day in the work period
    current_date = start_date
    while current_date <= end_date:

        # Check if the current day is a weekly off
        if current_date.weekday() == weekly_off_day:
            current_date += timedelta(days=1)
            continue

        # Check if the current day is a holiday
        if current_date in holiday_list:
            current_date += timedelta(days=1)
            continue

        # Check if the current day is a holiday
        if current_date in leave_list:
            current_date += timedelta(days=1)
            continue

        # Calculate the total working hours on the current day
        if current_date == start_date:
            start_time = max(start_time, shift_in)
        if current_date == end_date:
            end_time = min(end_time, end_time)
        total_working_hours_on_current_day = (datetime.combine(date(1, 1, 1), end_time) - datetime.combine(date(1, 1, 1), start_time)).total_seconds() / 3600
        total_working_hours += total_working_hours_on_current_day

        # Subtract the tea and lunch breaks from the total working hours on the current day
        if tea_break_1_start_time >= start_time and tea_break_1_end_time <= end_time:
            total_working_hours -= 0.17
        if lunch_break_start_time >= start_time and lunch_break_end_time <= end_time:
            total_working_hours -= 0.5
        if tea_break_2_start_time >= start_time and tea_break_2_end_time <= end_time:
            total_working_hours -= 0.17

        current_date += timedelta(days=1)
    return total_working_hours


def submit_entry(path, req_id, mold_no, activity, start, days, designer):
    # Connect to the SQLite3 database
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("PRAGMA JOURNAL_MODE='wal' ")

    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{designer}'")
    designer_tbl = c.fetchone()

    if not designer_tbl:
        return

    holiday_list = [_date for _date in shared_variable.holidays[1:] if _date is not None]

    status = {
        "Preform": "P_PLAN_STATUS",
        "Assembly": "A_PLAN_STATUS",
        "Assembly Check": "AC_PLAN_STATUS",
        "Detailing": "D_PLAN_STATUS",
        "Checking": "C_PLAN_STATUS",
        "Correction": "CR_PLAN_STATUS",
        "Second Check": "SC_PLAN_STATUS",
        "Mold Issue": "I_PLAN_STATUS",
    }

    # Define the input values
    if '.' in days:
        no_of_days = float(days)
    else:
        no_of_days = int(days)

    uname = shared_variable.user_name

    # user log date
    user_log = uname + " " + datetime.now().strftime('%d/%m/%Y')

    # Convert string to datetime object
    start_date = datetime.strptime(start, "%d-%m-%Y")

    # Loop through the number of days and insert records into the database
    for i in range(int(no_of_days)):
        if start_date.weekday() == 6:
            start_date = start_date + timedelta(days=1)
            if start_date.strftime("%Y-%m-%d") in holiday_list:
                start_date = start_date + timedelta(days=1)
        # Create a date string in the format 'dd-mm-yyyy'
        date_str = start_date.strftime("%Y-%m-%d")
        end_day = date_str
        # Insert the record into the database
        c.execute("INSERT INTO HEATMAP (REQ_ID,MOLD_NO,DATE,DESIGNER,ACTIVITY,DAYS,STATUS,STATUS_REMARK,USER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (req_id, mold_no, date_str, designer, activity, 1, 0, 'Planned', user_log))
        # Increment the day by 1
        start_date = start_date + timedelta(days=1)

    # If there are remaining days (e.g. 0.5 in this case), insert a record with the remaining days
    if no_of_days % 1 != 0:
        if start_date.weekday() == 6:
            start_date = start_date + timedelta(days=1)
            if start_date.strftime("%Y-%m-%d") in holiday_list:
                start_date = start_date + timedelta(days=1)
        date_str = start_date.strftime("%Y-%m-%d")
        end_day = date_str
        c.execute("INSERT INTO HEATMAP (REQ_ID,MOLD_NO,DATE,DESIGNER,ACTIVITY,DAYS,STATUS,STATUS_REMARK,USER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (req_id, mold_no, date_str, designer, activity, no_of_days % 1, 0, 'Planned', user_log))

    # Execute the update query
    c.execute(f"UPDATE MOLD_TABLE SET {status[activity]}={status[activity]}+?,PRE_PLAN_STATUS=? WHERE REQ_ID=?", (1, 1, req_id))

    # reset the start date
    ob_date = datetime.strptime(start, "%d-%m-%Y")
    start_date = datetime.strftime(ob_date, "%Y-%m-%d")

    c.execute(f"INSERT INTO {designer} (REQ_ID,MOLD_NO,ACTIVITY,START_DATE,END_DATE,DAYS_COUNT,STATUS,STATUS_REMARK) VALUES (?,?,?,?,?,?,?,?)",
              (req_id, mold_no, activity, start_date, end_day, days, 0, 'Planned'))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def get_new_entry(path):
    # Connect to the SQLite database
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Execute a SELECT statement with a WHERE clause
    cursor.execute('SELECT INFO_DATE,MOLD_NO FROM MOLD_TABLE WHERE PRE_PLAN_STATUS = ?', (0,))
    data = cursor.fetchall()

    # Close the connection
    conn.close()
    return data


def get_short_plan(path):
    # Connect to the SQLite database
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Execute a SELECT statement with a WHERE clause
    cursor.execute('SELECT INFO_DATE,MOLD_NO FROM MOLD_TABLE WHERE RE_PLAN_STATUS=? AND PRE_PLAN_STATUS!=?', (0, 0))
    data = cursor.fetchall()

    # Close the connection
    conn.close()
    return data


def get_complete_plan(path):
    # Connect to the SQLite database
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Execute a SELECT statement with a WHERE clause
    cursor.execute('SELECT INFO_DATE,MOLD_NO FROM MOLD_TABLE WHERE RE_PLAN_STATUS=? AND PRE_PLAN_STATUS>?', (1, 0))
    data = cursor.fetchall()

    # Close the connection
    conn.close()
    return data


def get_mold_info(path, mold_no):
    # Connect to the SQLite database
    conn = sqlite3.connect(path)

    # define query
    query = 'SELECT * FROM MOLD_TABLE WHERE MOLD_NO=?'

    # Define the query parameters
    params = (mold_no,)

    # Execute a SELECT statement with a WHERE clause
    df_mold_info = pd.read_sql(query, conn, params=params)

    # Close the connection
    conn.close()

    return df_mold_info




