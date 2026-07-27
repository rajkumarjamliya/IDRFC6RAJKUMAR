from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import streamlit as st

# Database Setup with persistent connection
conn = sqlite3.connect("warehouse_management.db", check_same_thread=False)
cursor = conn.cursor()

# Tables Creation
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        role TEXT
    )
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS couriers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS work_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT,
        piklist_number TEXT,
        work_type TEXT,
        start_time TEXT,
        end_time TEXT,
        status TEXT,
        courier_name TEXT,
        awb_number TEXT,
        date TEXT
    )
"""
)
conn.commit()

# Seed default couriers and employees if empty
cursor.execute("SELECT COUNT(*) FROM couriers")
if cursor.fetchone()[0] == 0:
  default_couriers = ["Delhivery", "Amazon", "Xpressbees", "Blue Dart", "DTDC"]
  for c in default_couriers:
    cursor.execute("INSERT OR IGNORE INTO couriers (name) VALUES (?)", (c,))
  conn.commit()

cursor.execute("SELECT COUNT(*) FROM users")
if cursor.fetchone()[0] == 0:
  default_users = [
      ("Rajkumar", "Admin"),
      ("Kapil", "Employee"),
      ("Sanjiv", "Employee"),
  ]
  for u, r in default_users:
    cursor.execute(
        "INSERT OR IGNORE INTO users (name, role) VALUES (?, ?)", (u, r)
    )
  conn.commit()

# Page Configuration
st.set_page_config(
    page_title="RAJKUMAR IDRFC 6 - Warehouse Tracker", layout="wide"
)

st.title("📦 RAJKUMAR IDRFC 6 - Warehouse & OT Report Tracker")
st.markdown("---")

# Sidebar - Navigation & User Control
st.sidebar.header("🔐 IDRFC6 User Control")

cursor.execute("SELECT name FROM users")
all_users = [row[0] for row in cursor.fetchall()]
current_user = st.sidebar.selectbox(
    "Select Your Profile (Name)", all_users if all_users else ["Rajkumar"]
)

cursor.execute("SELECT role FROM users WHERE name = ?", (current_user,))
res_role = cursor.fetchone()
user_role = res_role[0] if res_role else "Employee"
st.sidebar.markdown(f"**Role:** `{user_role}` | **ID:** `IDRFC6`")

menu = st.sidebar.selectbox(
    "Navigation Menu",
    [
        "Live Work Status",
        "Piklist Operations (Work Entry)",
        "Courier & Box Summary",
        "Manage Master Data (Employees & Couriers)",
        "Admin Report & Editing",
    ],
)

# ----------------- 1. LIVE WORK STATUS -----------------
if menu == "Live Work Status":
  st.header("🟢 Live Employee Work Status")
  st.write("Yahan live pata chalega ki is waqt kaun sa employee kya kaam kar raha hai.")

  cursor.execute(
      "SELECT employee_name, piklist_number, work_type, start_time, courier_name"
      " FROM work_status WHERE status='Running'"
  )
  running_data = cursor.fetchall()

  if running_data:
    df_running = pd.DataFrame(
        running_data,
        columns=[
            "Employee Name",
            "Piklist Number",
            "Work Type",
            "Start Time",
            "Courier",
        ],
    )
    st.dataframe(df_running, use_container_width=True)
  else:
    st.info("Filhal koi bhi employee active nahi hai (Running status zero hai).")

  st.subheader("👥 Total Employees Working per Piklist")
  cursor.execute(
      "SELECT piklist_number, COUNT(DISTINCT employee_name) as Total_Employees"
      " FROM work_status WHERE status='Running' GROUP BY piklist_number"
  )
  summary_data = cursor.fetchall()
  if summary_data:
    df_summary = pd.DataFrame(
        summary_data, columns=["Piklist Number", "Active Employees Count"]
    )
    st.table(df_summary)

# ----------------- 2. PIKLIST OPERATIONS (WORK ENTRY) -----------------
elif menu == "Piklist Operations (Work Entry)":
  st.header("⚡ Piklist Work & Timing Entry (Picking, Packing, Scanning)")

  cursor.execute("SELECT name FROM couriers")
  courier_list = [row[0] for row in cursor.fetchall()]

  with st.form("work_entry_form"):
    col1, col2 = st.columns(2)
    with col1:
      piklist_no = st.text_input("Enter Piklist Number")
      work_type = st.selectbox(
          "Select Work Type", ["Picking", "Packing", "Scanning"]
      )
    with col2:
      courier_name = st.selectbox(
          "Select Courier Name",
          courier_list if courier_list else ["Delhivery", "Amazon"],
      )
      awb_no = st.text_input("Enter AWB Number (Optional)")

    action = st.radio("Choose Action", ["Start Work", "Minimize / Complete Work"])
    submit_btn = st.form_submit_button("Submit Work Entry")

    if submit_btn:
      current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      today_date = datetime.now().strftime("%Y-%m-%d")

      if action == "Start Work":
        if awb_no:
          cursor.execute(
              "SELECT * FROM work_status WHERE awb_number = ?", (awb_no,)
          )
          is_duplicate = cursor.fetchone()
          if is_duplicate:
            st.error(
                "⚠️ **ALERT! Duplicate AWB Number Found!** Yeh AWB pehle hi save"
                " ho chuka hai."
            )
            st.markdown(
                '<audio autoplay><source src="https://www.myinstants.com/media/sounds/error.mp3" type="audio/mpeg"></audio>',
                unsafe_allow_html=True,
            )

        cursor.execute(
            """
            INSERT INTO work_status (employee_name, piklist_number, work_type, start_time, status, courier_name, awb_number, date)
            VALUES (?, ?, ?, ?, 'Running', ?, ?, ?)
        """,
            (
                current_user,
                piklist_no,
                work_type,
                current_time,
                courier_name,
                awb_no,
                today_date,
            ),
        )
        conn.commit()
        st.success(
            f"✅ {work_type} started for Piklist: {piklist_no} by {current_user}"
        )

      elif action == "Minimize / Complete Work":
        cursor.execute(
            """
            UPDATE work_status 
            SET end_time = ?, status = 'Completed' 
            WHERE employee_name = ? AND piklist_number = ? AND status = 'Running'
        """,
            (current_time, current_user, piklist_no),
        )
        conn.commit()
        st.success(
            f"🏁 Work completed and minimized for Piklist: {piklist_no}!"
        )

# ----------------- 3. COURIER & BOX SUMMARY -----------------
elif menu == "Courier & Box Summary":
  st.header("📊 Courier-wise & Box Entry Summary")

  selected_date = st.date_input("Select Date for Report", datetime.now())
  date_str = selected_date.strftime("%Y-%m-%d")

  st.subheader(f"Summary for Date: {date_str}")

  cursor.execute(
      """
      SELECT courier_name, COUNT(DISTINCT piklist_number) as Total_Piklists, COUNT(awb_number) as Total_AWBs 
      FROM work_status WHERE date = ? GROUP BY courier_name
  """,
      (date_str,),
  )
  courier_summary = cursor.fetchall()

  if courier_summary:
    df_courier = pd.DataFrame(
        courier_summary,
        columns=["Courier Name", "Total Piklists", "Total AWB / Boxes"],
    )
    st.dataframe(df_courier, use_container_width=True)
  else:
    st.warning("Is date par koi data available nahi hai.")

  if st.checkbox("Show Detailed AWB & Piklist Records"):
    cursor.execute(
        "SELECT employee_name, piklist_number, work_type, courier_name,"
        " awb_number, start_time, end_time FROM work_status WHERE date = ?",
        (date_str,),
    )
    all_logs = cursor.fetchall()
    df_logs = pd.DataFrame(
        all_logs,
        columns=[
            "Employee",
            "Piklist",
            "Work",
            "Courier",
            "AWB",
            "Start Time",
            "End Time",
        ],
    )
    st.dataframe(df_logs)

# ----------------- 4. MANAGE MASTER DATA (EMPLOYEES & COURIERS) -----------------
elif menu == "Manage Master Data (Employees & Couriers)":
  st.header("⚙️ Add New Employees and Couriers")

  col1, col2 = st.columns(2)

  with col1:
    st.subheader("➕ Add New Employee")
    new_emp_name = st.text_input("Employee Name")
    new_emp_role = st.selectbox(
        "Employee Role", ["Employee", "Admin"], key="emp_role"
    )
    if st.button("Add Employee"):
      if new_emp_name:
        try:
          cursor.execute(
              "INSERT INTO users (name, role) VALUES (?, ?)",
              (new_emp_name, new_emp_role),
          )
          conn.commit()
          st.success(f"✅ Employee '{new_emp_name}' successfully added!")
          st.rerun()
        except sqlite3.IntegrityError:
          st.error("⚠️ Yeh employee name pehle se exist karta hai.")
      else:
        st.warning("Kripya name enter karein.")

    st.markdown("### Existing Employees List")
    cursor.execute("SELECT name, role FROM users")
    st.table(pd.DataFrame(cursor.fetchall(), columns=["Name", "Role"]))

  with col2:
    st.subheader("➕ Add New Courier")
    new_courier_name = st.text_input(
        "Courier Company Name (e.g., Ecom Express, Shadowfax)"
    )
    if st.button("Add Courier"):
      if new_courier_name:
        try:
          cursor.execute(
              "INSERT INTO couriers (name) VALUES (?)", (new_courier_name,)
          )
          conn.commit()
          st.success(f"✅ Courier '{new_courier_name}' successfully added!")
          st.rerun()
        except sqlite3.IntegrityError:
          st.error("⚠️ Yeh courier pehle se list mein hai.")
      else:
        st.warning("Kripya courier name enter karein.")

    st.markdown("### Existing Couriers List")
    cursor.execute("SELECT name FROM couriers")
    st.table(pd.DataFrame(cursor.fetchall(), columns=["Courier Name"]))

# ----------------- 5. ADMIN REPORT & EDITING -----------------
elif menu == "Admin Report & Editing":
  st.header("🛠️ Admin Panel & Data Editing")

  if user_role != "Admin":
    st.error("⚠️ Access Denied! Yeh section sirf Admin ke liye hai.")
  else:
    st.success(
        "Welcome Admin! Aap yahan data edit aur date-wise report nikal sakte"
        " hain."
    )

    cursor.execute(
        "SELECT id, employee_name, piklist_number, work_type, start_time,"
        " courier_name, awb_number FROM work_status ORDER BY id DESC LIMIT 50"
    )
    records = cursor.fetchall()

    if records:
      df_edit = pd.DataFrame(
          records,
          columns=[
              "ID",
              "Employee",
              "Piklist",
              "Work",
              "Start Time",
              "Courier",
              "AWB",
          ],
      )
      st.dataframe(df_edit)

      st.markdown("### ✏️ Edit Specific Record")
      edit_id = st.number_input("Enter Record ID to Edit", min_value=1, step=1)

      cursor.execute("SELECT start_time FROM work_status WHERE id = ?", (edit_id,))
      res = cursor.fetchone()

      if res:
        start_t_str = res[0]
        start_t = datetime.strptime(start_t_str, "%Y-%m-%d %H:%M:%S")
        time_diff = datetime.now() - start_t
        is_within_3_hours = time_diff <= timedelta(hours=3)

        if is_within_3_hours:
          st.info(
              "ℹ️ Yeh entry 3 ghante ke andar ki hai, ise koi bhi ya"
              " employee bhi edit kar sakta hai."
          )
        else:
          st.warning(
              "🔒 Yeh entry 3 ghante se purani hai. Isme changes karne ka right"
              " sirf **Admin** ke pas hai."
          )

        new_piklist = st.text_input("New Piklist Number")

        cursor.execute("SELECT name FROM couriers")
        c_list = [row[0] for row in cursor.fetchall()]
        new_courier = st.selectbox(
            "New Courier", c_list if c_list else ["Delhivery", "Amazon"]
        )
        new_awb = st.text_input("New AWB Number")

        if st.button("Update Record"):
          cursor.execute(
              """
              UPDATE work_status 
              SET piklist_number = ?, courier_name = ?, awb_number = ? 
              WHERE id = ?
          """,
              (new_piklist, new_courier, new_awb, edit_id),
          )
          conn.commit()
          st.success(f"✅ Record ID {edit_id} successfully updated!")
streamlit==1.32.0
pandas==2.2.0
