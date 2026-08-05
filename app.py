import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import os

# Page Config
st.set_page_config(page_title="DELHIVERY – IDRFC6 DEWAS Portal", layout="wide")

# Custom CSS Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 25px;
        border-radius: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0,0,0,0.35);
        border-bottom: 5px solid #ff3b30;
        margin-bottom: 20px;
    }
    .main-header h1 { margin: 0; font-size: 28px; font-weight: 800; color: #ffffff; }
    .main-header p { margin: 8px 0 0 0; font-size: 15px; color: #ffcc00; font-weight: 600; }
    .card-3d {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.6);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1>🚛 DELHIVERY – IDRFC6 DEWAS WAREHOUSE HUB 📦</h1>
        <p>⚡ Advanced Piklist, Employee Work & Courier Dispatch Management System | Rajkumar Jamliya</p>
    </div>
""", unsafe_allow_html=True)

DATA_FILE = "warehouse_entries.csv"
REPORT_FILE = "dispatch_reports.csv"
TRASH_FILE = "recycle_bin.csv"
EMPLOYEE_FILE = "employees_list.csv"
COURIER_FILE = "couriers_list.csv"
CONFIG_FILE = "admin_config.csv"

# Default Employee List
default_employees = {
    "AJAY PATEL": "W222449", "PANKAJ PATEL": "W224500", "KAMLESH MANDOI": "W225396",
    "ABHISHEK PATEL": "W225403", "SHRI RAM": "W225410", "KUNAL PATIL": "W225413",
    "RAJSARGARA": "W225415", "ANISH PATEL": "226351", "ANKIT MANDLOI": "W226654",
    "SANDEEP PATEL": "W228473", "ABHISHEK PATEL (2)": "230777", "RAJKUMAR JAMLIYA": "W224483",
    "CHANDAN": "W228474", "SHAILESH TIWARI": "SSN079654", "SUJATA KUSHWAHA": "W231056",
    "SANDHYA KARANJA": "W231195", "HARSHITA SOLANKI": "W231196", "BHAVNA MALVIYA": "W231057",
    "REKHA": "W231152", "KAVITA": "W231689"
}

default_couriers = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "DTDC", "Bluedart", "Ekart"]

def load_employees():
    if os.path.exists(EMPLOYEE_FILE):
        try:
            df = pd.read_csv(EMPLOYEE_FILE)
            return dict(zip(df["Name"], df["Emp ID"]))
        except: pass
    return default_employees

def save_employees(emp_dict):
    pd.DataFrame(list(emp_dict.items()), columns=["Name", "Emp ID"]).to_csv(EMPLOYEE_FILE, index=False)

def load_couriers():
    if os.path.exists(COURIER_FILE):
        try: return pd.read_csv(COURIER_FILE)["Courier"].tolist()
        except: pass
    return default_couriers

def save_couriers(courier_list):
    pd.DataFrame({"Courier": courier_list}).to_csv(COURIER_FILE, index=False)

def load_admin_password():
    if os.path.exists(CONFIG_FILE):
        try: return str(pd.read_csv(CONFIG_FILE)["Password"].values[0])
        except: pass
    return "123654"

def save_admin_password(new_pass):
    pd.DataFrame({"Password": [new_pass]}).to_csv(CONFIG_FILE, index=False)

def sanitize_reports_df(df):
    expected_cols = ["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"]
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(columns=expected_cols)
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0 if col in ["Manifest", "Cancel", "Dispatch", "Return"] else "--:--"
    return df[expected_cols]

def load_data():
    if os.path.exists(DATA_FILE):
        try: return pd.read_csv(DATA_FILE)
        except: pass
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Emp ID", "Task Type", "Courier", "Parcel Count", "Time"])

def save_data(df): df.to_csv(DATA_FILE, index=False)

def load_reports():
    if os.path.exists(REPORT_FILE):
        try: return sanitize_reports_df(pd.read_csv(REPORT_FILE))
        except: pass
    return sanitize_reports_df(pd.DataFrame())

def save_reports(df): sanitize_reports_df(df).to_csv(REPORT_FILE, index=False)

def load_trash():
    if os.path.exists(TRASH_FILE):
        try: return pd.read_csv(TRASH_FILE)
        except: pass
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Emp ID", "Task Type", "Courier", "Parcel Count", "Time", "Deleted Time"])

def save_trash(df): df.to_csv(TRASH_FILE, index=False)

# Initialize Session States
if "data" not in st.session_state: st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state: st.session_state["dispatch_reports"] = load_reports()
else: st.session_state["dispatch_reports"] = sanitize_reports_df(st.session_state["dispatch_reports"])
if "trash_data" not in st.session_state: st.session_state["trash_data"] = load_trash()
if "admin_logged" not in st.session_state: st.session_state["admin_logged"] = False
if "employees" not in st.session_state: st.session_state["employees"] = load_employees()
if "couriers" not in st.session_state: st.session_state["couriers"] = load_couriers()
if "admin_password" not in st.session_state: st.session_state["admin_password"] = load_admin_password()

couriers_list = st.session_state["couriers"]

# Sidebar Controls
st.sidebar.markdown("### ⚙️ Control Center")
# Default date is automatically set to server's today date
selected_date = st.sidebar.date_input("Select Working / Report Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

nav_page = st.sidebar.radio("Navigation Menu", ["🏠 Home & Main Work Data", "📊 Courier & Dispatch Report", "👥 Employee & Courier Management", "♻️ Admin & Recycle Bin"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 Admin Security")
if not st.session_state["admin_logged"]:
    entered_pass = st.sidebar.text_input("Admin Password", type="password")
    if st.sidebar.button("Unlock Admin"):
        if entered_pass == st.session_state["admin_password"]:
            st.session_state["admin_logged"] = True
            st.sidebar.success("Unlocked!")
            st.rerun()
        else: st.sidebar.error("Wrong Password!")
else:
    st.sidebar.success("🔓 Admin Active")
    if st.sidebar.button("Lock Admin"):
        st.session_state["admin_logged"] = False
        st.rerun()

# ================= 1. HOME & MAIN WORK DATA (HOME PAGE) =================
if nav_page == "🏠 Home & Main Work Data":
    st.markdown(f"<div class='card-3d'><h3>🏠 Home Page - Live Work & Piklist Data ({selected_date_str})</h3></div>", unsafe_allow_html=True)

    df = st.session_state["data"]
    df_f = df[df["Date"] == selected_date_str] if not df.empty and "Date" in df.columns else pd.DataFrame()
    
    if not df_f.empty:
        st.markdown("#### 📋 Today's Recorded Entries")
        display_cols = ["Piklist No.", "Employee Name", "Emp ID", "Task Type", "Courier", "Parcel Count", "Time"]
        st.dataframe(df_f[display_cols], use_container_width=True)
        
        csv_data = df_f.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Work Report (CSV)", csv_data, f"work_report_{selected_date_str}.csv", "text/csv")
        
        st.markdown("#### ✏️ Edit / Delete Entry")
        edit_id = st.selectbox("Select Entry ID", df_f["ID"].astype(str).tolist())
        selected_row = df_f[df_f["ID"].astype(str) == edit_id]
        if not selected_row.empty:
            with st.form("edit_entry_form"):
                new_pikl = st.text_input("Edit Piklist No.", value=str(selected_row["Piklist No."].values[0]))
                new_task = st.selectbox("Edit Task Type", ["Picking", "Packing", "Scanning", "Manifest", "Cancel", "Return"], index=["Picking", "Packing", "Scanning", "Manifest", "Cancel", "Return"].index(selected_row["Task Type"].values[0]) if selected_row["Task Type"].values[0] in ["Picking", "Packing", "Scanning", "Manifest", "Cancel", "Return"] else 0)
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    if st.form_submit_button("Update Entry"):
                        idx = df[df["ID"].astype(str) == edit_id].index[0]
                        st.session_state["data"].loc[idx, "Piklist No."] = new_pikl
                        st.session_state["data"].loc[idx, "Task Type"] = new_task
                        save_data(st.session_state["data"])
                        st.success("Updated!")
                        st.rerun()
                with col_e2:
                    if st.form_submit_button("🗑️ Delete Entry"):
                        target = df[df["ID"].astype(str) == edit_id]
                        trash_row = target.copy()
                        trash_row["Deleted Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state["trash_data"] = pd.concat([st.session_state["trash_data"], trash_row], ignore_index=True)
                        save_trash(st.session_state["trash_data"])
                        
                        st.session_state["data"] = df[df["ID"].astype(str) != edit_id]
                        save_data(st.session_state["data"])
                        st.success("Deleted!")
                        st.rerun()
    else:
        st.info("No work entries found for this date yet.")

    st.markdown("---")
    st.markdown("#### ➕ Add New Piklist / Employee Task Entry")
    with st.form("entry_form"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            piklist_no = st.text_input("Piklist No.")
            emp_list = list(st.session_state["employees"].keys())
            selected_emp = st.selectbox("Select Employee Name", emp_list)
            auto_emp_id = st.session_state["employees"].get(selected_emp, "N/A")
            st.markdown(f"🆔 **Employee ID:** `{auto_emp_id}`")
        with col_f2:
            task_type = st.selectbox("Task Type", ["Picking", "Packing", "Scanning", "Manifest", "Cancel", "Return"])
            courier = "N/A"
            parcel_count = 1
            if task_type in ["Manifest", "Cancel", "Return"]:
                courier = st.selectbox("Select Courier Company", couriers_list)
                parcel_count = st.number_input("Box / Parcel Count", min_value=1, value=1)

        # Automatically capture system current time when saving
        current_time_str = datetime.now().strftime("%I:%M:%S %p")
        st.info(f"🕒 Server / System Time (Automatic): **{current_time_str}**")

        submitted = st.form_submit_button("💾 Save Entry", use_container_width=True)
        if submitted:
            if piklist_no and selected_emp:
                if courier != "N/A":
                    rep_df = sanitize_reports_df(st.session_state["dispatch_reports"])
                    ex = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == courier)]
                    
                    col_target = "Manifest"
                    if task_type == "Cancel": col_target = "Cancel"
                    elif task_type == "Return": col_target = "Return"

                    if not ex.empty:
                        idx = ex.index[0]
                        rep_df.loc[idx, col_target] += int(parcel_count)
                    else:
                        new_row_rep = {
                            "Date": selected_date_str, "Courier": courier, 
                            "In Time": datetime.now().strftime("%I:%M:%S %p"), # Automatic Server In-Time
                            "Out Time": "07:00 PM",
                            "Manifest": int(parcel_count) if task_type == "Manifest" else 0,
                            "Cancel": int(parcel_count) if task_type == "Cancel" else 0,
                            "Dispatch": 0,
                            "Return": int(parcel_count) if task_type == "Return" else 0,
                            "Remark": ""
                        }
                        rep_df = pd.concat([rep_df, pd.DataFrame([new_row_rep])], ignore_index=True)
                    st.session_state["dispatch_reports"] = sanitize_reports_df(rep_df)
                    save_reports(st.session_state["dispatch_reports"])

                new_entry = pd.DataFrame({
                    "ID": [str(pd.Timestamp.now().timestamp())],
                    "Date": [selected_date_str],
                    "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Piklist No.": [str(piklist_no)],
                    "Employee Name": [selected_emp],
                    "Emp ID": [auto_emp_id],
                    "Task Type": [task_type],
                    "Courier": [courier],
                    "Parcel Count": [int(parcel_count)],
                    "Time": [current_time_str] # Saved automatically
                })
                st.session_state["data"] = pd.concat([st.session_state["data"], new_entry], ignore_index=True)
                save_data(st.session_state["data"])
                st.success("Entry Saved Successfully with Automatic Time!")
                st.rerun()
            else:
                st.warning("Please enter Piklist No. and Employee Name.")

# ================= 2. COURIER & DISPATCH REPORT =================
elif nav_page == "📊 Courier & Dispatch Report":
    st.markdown(f"<div class='card-3d'><h3>📊 Courier Dispatch & Timing Report ({selected_date_str})</h3></div>", unsafe_allow_html=True)
    
    rep_df = sanitize_reports_df(st.session_state["dispatch_reports"])
    
    with st.form("courier_report_form"):
        st.markdown("#### Update Courier Timings, Dispatch & Return Counts")
        sel_c = st.selectbox("Select Courier Company", couriers_list)
        curr_row = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == sel_c)]
        
        # Automatic system time default for In Time if not already set
        default_in_time = datetime.now().strftime("%I:%M:%S %p")
        if not curr_row.empty and curr_row["In Time"].values[0] != "--:--":
            default_in_time = str(curr_row["In Time"].values[0])

        c_in = st.text_input("In Time (Auto / Server Time)", value=default_in_time)
        c_out = st.text_input("Out Time", value=str(curr_row["Out Time"].values[0]) if not curr_row.empty else "07:00 PM")
        
        man_v = st.number_input("Manifest Boxes", min_value=0, value=int(curr_row["Manifest"].values[0]) if not curr_row.empty else 0)
        can_v = st.number_input("Cancel Boxes", min_value=0, value=int(curr_row["Cancel"].values[0]) if not curr_row.empty else 0)
        dis_v = st.number_input("Dispatch Boxes", min_value=0, value=int(curr_row["Dispatch"].values[0]) if not curr_row.empty else 0)
        ret_v = st.number_input("Return Boxes", min_value=0, value=int(curr_row["Return"].values[0]) if not curr_row.empty else 0)
        rem_v = st.text_input("Remark", value=str(curr_row["Remark"].values[0]) if not curr_row.empty and pd.notna(curr_row["Remark"].values[0]) else "")

        if st.form_submit_button("Save Courier Report"):
            if not curr_row.empty:
                idx = curr_row.index[0]
                rep_df.loc[idx, ["In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"]] = [c_in, c_out, man_v, can_v, dis_v, ret_v, rem_v]
            else:
                new_r = {"Date": selected_date_str, "Courier": sel_c, "In Time": c_in, "Out Time": c_out, "Manifest": man_v, "Cancel": can_v, "Dispatch": dis_v, "Return": ret_v, "Remark": rem_v}
                rep_df = pd.concat([rep_df, pd.DataFrame([new_r])], ignore_index=True)
            st.session_state["dispatch_reports"] = sanitize_reports_df(rep_df)
            save_reports(st.session_state["dispatch_reports"])
            st.success("Report Saved!")
            st.rerun()

    current_day_rep = rep_df[rep_df["Date"] == selected_date_str]
    yest_rep_view = rep_df[rep_df["Date"] == yesterday_str]
    
    yest_pend = {}
    for c in couriers_list:
        yc = yest_rep_view[yest_rep_view["Courier"] == c]
        if not yc.empty:
            m = int(yc["Manifest"].values[0])
            ca = int(yc["Cancel"].values[0])
            d = int(yc["Dispatch"].values[0])
            r = int(yc["Return"].values[0])
            yest_pend[c] = max(0, m - ca - d + r)
        else:
            yest_pend[c] = 0

    table_rows = []
    tot_man, tot_can, tot_dis, tot_ret, tot_pend = 0, 0, 0, 0, 0
    for c in couriers_list:
        cr = current_day_rep[current_day_rep["Courier"] == c]
        m = int(cr["Manifest"].values[0]) if not cr.empty else 0
        ca = int(cr["Cancel"].values[0]) if not cr.empty else 0
        d = int(cr["Dispatch"].values[0]) if not cr.empty else 0
        r = int(cr["Return"].values[0]) if not cr.empty else 0
        yp = yest_pend.Fget if hasattr(yest_pend, 'Fget') else yest_pend.get(c, 0)
        pend = max(0, (m + yp) - ca - d + r)
        rem = str(cr["Remark"].values[0]) if not cr.empty and pd.notna(cr["Remark"].values[0]) else ""
        
        tot_man += m
        tot_can += ca
        tot_dis += d
        tot_ret += r
        tot_pend += pend

        table_rows.append({
            "Courier": c,
            "In Time": cr["In Time"].values[0] if not cr.empty else "--:--",
            "Out Time": cr["Out Time"].values[0] if not cr.empty else "--:--",
            "Manifest": m,
            "Cancel": ca,
            "Dispatch": d,
            "Return": r,
            "Pending": pend,
            "Remark": rem
        })

    final_report_df = pd.DataFrame(table_rows)
    st.markdown(f"#### 📋 Courier Status Table for Date: `{selected_date_str}`")
    st.dataframe(final_report_df, use_container_width=True)

    csv_rep = final_report_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Courier Report (CSV/Excel)", csv_rep, f"courier_report_{selected_date_str}.csv", "text/csv")

# ================= 3. EMPLOYEE & COURIER MANAGEMENT =================
elif nav_page == "👥 Employee & Courier Management":
    st.markdown("<div class='card-3d'><h3>👥 Employee & Courier Management</h3></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("#### Employees")
        with st.form("add_emp"):
            en = st.text_input("Name")
            ei = st.text_input("Emp ID")
            if st.form_submit_button("Add"):
                if en and ei:
                    st.session_state["employees"][en] = ei
                    save_employees(st.session_state["employees"])
                    st.success("Added!")
                    st.rerun()
        st.dataframe(pd.DataFrame(list(st.session_state["employees"].items()), columns=["Name", "Emp ID"]), use_container_width=True)
    with c2:
        st.markdown("#### Couriers")
        with st.form("add_cour"):
            cn = st.text_input("Courier Name")
            if st.form_submit_button("Add Courier"):
                if cn and cn not in st.session_state["couriers"]:
                    st.session_state["couriers"].append(cn)
                    save_couriers(st.session_state["couriers"])
                    st.success("Added!")
                    st.rerun()
        st.dataframe(pd.DataFrame({"Courier": st.session_state["couriers"]}), use_container_width=True)

# ================= 4. ADMIN & RECYCLE BIN =================
elif nav_page == "♻️ Admin & Recycle Bin":
    st.markdown("<div class='card-3d'><h3>♻️ Admin Panel & Trash</h3></div>", unsafe_allow_html=True)
    if not st.session_state["admin_logged"]:
        st.warning("Please unlock admin from sidebar.")
    else:
        st.success("Admin Access Granted.")
        with st.form("pass_change"):
            np = st.text_input("New Admin Password", type="password")
            if st.form_submit_button("Update Password"):
                if np:
                    st.session_state["admin_password"] = np
                    save_admin_password(np)
                    st.success("Password Updated!")
        
        st.markdown("#### Trash / Deleted Entries")
        trash_df = st.session_state["trash_data"]
        if not trash_df.empty:
            st.dataframe(trash_df, use_container_width=True)
            if st.button("Empty Trash"):
                st.session_state["trash_data"] = pd.DataFrame(columns=trash_df.columns)
                save_trash(st.session_state["trash_data"])
                st.rerun()
        else:
            st.info("Trash is empty.")
