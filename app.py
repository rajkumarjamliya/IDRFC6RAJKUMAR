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
        padding: 30px;
        border-radius: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0,0,0,0.35);
        border-bottom: 5px solid #ff3b30;
        margin-bottom: 25px;
    }
    .main-header h1 { margin: 0; font-size: 32px; font-weight: 800; color: #ffffff; }
    .main-header p { margin: 10px 0 0 0; font-size: 16px; color: #ffcc00; font-weight: 600; }
    .card-3d {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.6);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1>🚛 DELHIVERY – IDRFC6 DEWAS WAREHOUSE HUB 📦</h1>
        <p>⚡ Advanced Piklist & Courier Logistics Management System &nbsp;|&nbsp; Managed by: RAJKUMAR</p>
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
    "AJAY PATEL": "W222449",
    "PANKAJ PATEL": "W224500",
    "KAMLESH MANDOI": "W225396",
    "ABHISHEK PATEL": "W225403",
    "SHRI RAM": "W225410",
    "KUNAL PATIL": "W225413",
    "RAJSARGARA": "W225415",
    "ANISH PATEL": "226351",
    "ANKIT MANDLOI": "W226654",
    "SANDEEP PATEL": "W228473",
    "ABHISHEK PATEL (2)": "230777",
    "RAJKUMAR JAMLIYA": "W224483",
    "CHANDAN": "W228474",
    "SHAILESH TIWARI": "SSN079654",
    "SUJATA KUSHWAHA": "W231056",
    "SANDHYA KARANJA": "W231195",
    "HARSHITA SOLANKI": "W231196",
    "BHAVNA MALVIYA": "W231057",
    "REKHA": "W231152",
    "KAVITA": "W231689"
}

default_couriers = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "DTDC", "Bluedart", "Ekart"]

def load_employees():
    if os.path.exists(EMPLOYEE_FILE):
        try:
            df = pd.read_csv(EMPLOYEE_FILE)
            return dict(zip(df["Name"], df["Emp ID"]))
        except:
            pass
    return default_employees

def save_employees(emp_dict):
    df = pd.DataFrame(list(emp_dict.items()), columns=["Name", "Emp ID"])
    df.to_csv(EMPLOYEE_FILE, index=False)

def load_couriers():
    if os.path.exists(COURIER_FILE):
        try:
            df = pd.read_csv(COURIER_FILE)
            return df["Courier"].tolist()
        except:
            pass
    return default_couriers

def save_couriers(courier_list):
    df = pd.DataFrame({"Courier": courier_list})
    df.to_csv(COURIER_FILE, index=False)

def load_admin_password():
    if os.path.exists(CONFIG_FILE):
        try:
            df = pd.read_csv(CONFIG_FILE)
            return str(df["Password"].values[0])
        except:
            pass
    return "123654"

def save_admin_password(new_pass):
    df = pd.DataFrame({"Password": [new_pass]})
    df.to_csv(CONFIG_FILE, index=False)

def sanitize_reports_df(df):
    expected_cols = ["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"]
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(columns=expected_cols)
    for col in expected_cols:
        if col not in df.columns:
            if col in ["Manifest", "Cancel", "Dispatch", "Return"]:
                df[col] = 0
            else:
                df[col] = "--:--"
    return df[expected_cols]

def load_data():
    if os.path.exists(DATA_FILE): 
        try: return pd.read_csv(DATA_FILE)
        except: pass
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Emp ID", "Task Type", "Courier", "Parcel Count", "In Time"])

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
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Emp ID", "Task Type", "Courier", "Parcel Count", "In Time", "Deleted Time"])

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
selected_date = st.sidebar.date_input("Working Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

nav_page = st.sidebar.radio("Navigation Menu", ["🏠 Piklist & Entry Portal", "📊 Courier-wise Total & Pending Report", "👥 Employee & Courier Management", "♻️ Admin & Recycle Bin"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 Admin Security Panel")

if not st.session_state["admin_logged"]:
    entered_pass = st.sidebar.text_input("Enter Admin Password", type="password")
    if st.sidebar.button("Unlock Admin Mode"):
        if entered_pass == st.session_state["admin_password"]:
            st.session_state["admin_logged"] = True
            st.sidebar.success("Admin Unlocked!")
            st.rerun()
        else:
            st.sidebar.error("Wrong Password!")
else:
    st.sidebar.success("🔓 Admin Mode Active")
    if st.sidebar.button("Lock Admin Mode"):
        st.session_state["admin_logged"] = False
        st.rerun()

# ================= 1. HOME ENTRY PORTAL =================
if nav_page == "🏠 Piklist & Entry Portal":
    st.markdown("<div class='card-3d'><h3>📝 Piklist-wise Courier & Box Entry Portal (Live Current Time Status)</h3></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.4], gap="large")
    
    with col1:
        piklist_no = st.text_input("Piklist No.")
        
        emp_list = list(st.session_state["employees"].keys())
        selected_emp = st.selectbox("Select Employee Name", emp_list)
        auto_emp_id = st.session_state["employees"].get(selected_emp, "N/A")
        
        st.markdown(f"🆔 **Automatic Employee ID:** `{auto_emp_id}`")
        
        task_type = st.selectbox("Task Type", ["Manifest", "Picking", "Packing", "Scanning"])
        
        courier = "N/A"
        parcel_count = 1
        if task_type == "Manifest":
            courier = st.selectbox("Courier Company", couriers_list)
            parcel_count = st.number_input("Box / Parcel Count", min_value=1, value=1)

        live_preview_time = datetime.now().strftime("%I:%M:%S %p")
        st.info(f"🕒 Current Live Time (Jis time status update hoga): **{live_preview_time}**")

        if st.button("💾 Submit Piklist Entry", use_container_width=True):
            if piklist_no and selected_emp:
                auto_in_time = datetime.now().strftime("%I:%M:%S %p")
                
                # Agar task Manifest hai, toh courier report mein boxes add ho jayenge
                if task_type == "Manifest" and courier != "N/A":
                    rep_df = sanitize_reports_df(st.session_state["dispatch_reports"])
                    ex = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == courier)]

                    if not ex.empty:
                        idx = ex.index[0]
                        rep_df.loc[idx, "Manifest"] += int(parcel_count)
                    else:
                        new_rep = pd.DataFrame({
                            "Date": [selected_date_str], "Courier": [courier], 
                            "In Time": ["10:00 AM"], "Out Time": ["07:00 PM"], 
                            "Manifest": [int(parcel_count)], "Cancel": [0], "Dispatch": [0], "Return": [0], "Remark": ["Auto Logged"]
                        })
                        rep_df = pd.concat([rep_df, new_rep], ignore_index=True)
                    
                    st.session_state["dispatch_reports"] = sanitize_reports_df(rep_df)
                    save_reports(st.session_state["dispatch_reports"])
                
                new_row = pd.DataFrame({
                    "ID": [str(pd.Timestamp.now().timestamp())],
                    "Date": [selected_date_str],
                    "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Piklist No.": [str(piklist_no)],
                    "Employee Name": [selected_emp],
                    "Emp ID": [auto_emp_id],
                    "Task Type": [task_type],
                    "Courier": [courier],
                    "Parcel Count": [int(parcel_count)],
                    "In Time": [auto_in_time]
                })
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                save_data(st.session_state["data"])

                st.success(f"Entry Saved Successfully!\n\n👤 Employee: **{selected_emp}** | 📋 Piklist: **{piklist_no}**\n🕒 Working In-Time: **{auto_in_time}**")
                st.rerun()

    with col2:
        st.markdown(f"<h3>📦 Employee Live Status & Piklist Records ({selected_date_str})</h3>", unsafe_allow_html=True)
        df = st.session_state["data"]
        df_f = df[df["Date"] == selected_date_str] if not df.empty and "Date" in df.columns else pd.DataFrame()
        
        if not df_f.empty:
            if "In Time" not in df_f.columns: df_f["In Time"] = "--:--"
            
            # Clean table showing only Piklist No, Employee Name, ID Code, Task Type, Courier, Parcel Count, and Time (No Database ID shown)
            display_cols = ["Piklist No.", "Employee Name", "Emp ID", "Task Type", "Courier", "Parcel Count", "In Time"]
            st.dataframe(df_f[display_cols], use_container_width=True)
            
            if st.session_state["admin_logged"]:
                st.markdown("#### 🗑️ Delete Specific Piklist Entry")
                del_id = st.selectbox("Select Entry ID to Delete", df_f["ID"].astype(str).tolist())
                if st.button("Delete Entry"):
                    target_row = df[df["ID"].astype(str) == del_id]
                    if not target_row.empty:
                        trash_row = target_row.copy()
                        trash_row["Deleted Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state["trash_data"] = pd.concat([st.session_state["trash_data"], trash_row], ignore_index=True)
                        save_trash(st.session_state["trash_data"])
                        
                        st.session_state["data"] = df[df["ID"].astype(str) != del_id]
                        save_data(st.session_state["data"])
                        st.success("Moved to Recycle Bin!")
                        st.rerun()
        else:
            st.info("📦 Aaj ke liye koi entry nahi hai.")

# ================= 2. COURIER-WISE REPORT & SUMMARY =================
elif nav_page == "📊 Courier-wise Total & Pending Report":
    st.markdown("<div class='card-3d'><h3>📊 Courier-wise Total Box, Dispatch, Cancel, Return & Dispute Timing Report</h3></div>", unsafe_allow_html=True)
    
    rep_df = sanitize_reports_df(st.session_state["dispatch_reports"])
    st.session_state["dispatch_reports"] = rep_df
    
    with st.form("courier_update_form"):
        st.markdown("#### Update Courier Box Counts & Dispute In/Out Timings")
        sel_courier = st.selectbox("Select Courier Company", couriers_list)
        curr_row = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == sel_courier)]
        
        default_in = "10:00 AM"
        if not curr_row.empty and pd.notna(curr_row["In Time"].values[0]) and curr_row["In Time"].values[0] != "--:--":
            default_in = str(curr_row["In Time"].values[0])

        default_out = "07:00 PM"
        if not curr_row.empty and pd.notna(curr_row["Out Time"].values[0]) and curr_row["Out Time"].values[0] != "--:--":
            default_out = str(curr_row["Out Time"].values[0])
            
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            c_in_time = st.text_input("Courier Dispute In Time", value=default_in)
        with col_t2:
            c_out_time = st.text_input("Courier Dispute Out Time", value=default_out)
            
        c_manifest = st.number_input("Manifest Boxes (Aaye Hue)", min_value=0, value=int(curr_row["Manifest"].values[0]) if not curr_row.empty else 0)
        c_dispatch = st.number_input("Dispatch Boxes (Bheje Gaye)", min_value=0, value=int(curr_row["Dispatch"].values[0]) if not curr_row.empty else 0)
        c_cancel = st.number_input("Cancel Boxes (Radd Kiye Gaye)", min_value=0, value=int(curr_row["Cancel"].values[0]) if not curr_row.empty else 0)
        c_return = st.number_input("Return Boxes (Wapas Aaye Hue)", min_value=0, value=int(curr_row["Return"].values[0]) if not curr_row.empty else 0)
        c_remark = st.text_input("Remark / Notes", value=str(curr_row["Remark"].values[0]) if not curr_row.empty and pd.notna(curr_row["Remark"].values[0]) else "")

        if st.form_submit_button("Save Courier Dispute Report"):
            if not curr_row.empty:
                idx = curr_row.index[0]
                rep_df.loc[idx, "In Time"] = c_in_time
                rep_df.loc[idx, "Out Time"] = c_out_time
                rep_df.loc[idx, "Manifest"] = c_manifest
                rep_df.loc[idx, "Dispatch"] = c_dispatch
                rep_df.loc[idx, "Cancel"] = c_cancel
                rep_df.loc[idx, "Return"] = c_return
                rep_df.loc[idx, "Remark"] = c_remark
            else:
                new_rep = pd.DataFrame({
                    "Date": [selected_date_str], "Courier": [sel_courier], 
                    "In Time": [c_in_time], "Out Time": [c_out_time], 
                    "Manifest": [c_manifest], "Cancel": [c_cancel], "Dispatch": [c_dispatch], "Return": [c_return], "Remark": [c_remark]
                })
                rep_df = pd.concat([rep_df, new_rep], ignore_index=True)
            
            st.session_state["dispatch_reports"] = sanitize_reports_df(rep_df)
            save_reports(st.session_state["dispatch_reports"])
            st.success("Courier Report Saved Successfully!")
            st.rerun()

    current_day_rep = rep_df[rep_df["Date"] == selected_date_str] if not rep_df.empty else pd.DataFrame()
    yest_rep_view = rep_df[rep_df["Date"] == yesterday_str] if not rep_df.empty else pd.DataFrame()
    
    yest_pend_map = {}
    for c in couriers_list:
        if not yest_rep_view.empty and "Courier" in yest_rep_view.columns:
            c_yest = yest_rep_view[yest_rep_view["Courier"] == c]
            if not c_yest.empty:
                man_y = int(c_yest["Manifest"].values[0]) if "Manifest" in c_yest.columns else 0
                can_y = int(c_yest["Cancel"].values[0]) if "Cancel" in c_yest.columns else 0
                dis_y = int(c_yest["Dispatch"].values[0]) if "Dispatch" in c_yest.columns else 0
                ret_y = int(c_yest["Return"].values[0]) if "Return" in c_yest.columns else 0
                yest_pend_map[c] = max(0, man_y - can_y - dis_y + ret_y)
            else:
                yest_pend_map[c] = 0
        else:
            yest_pend_map[c] = 0

    display_summary_rows = []
    for c in couriers_list:
        c_curr = current_day_rep[current_day_rep["Courier"] == c] if not current_day_rep.empty and "Courier" in current_day_rep.columns else pd.DataFrame()
        in_t = c_curr["In Time"].values[0] if not c_curr.empty and pd.notna(c_curr["In Time"].values[0]) else "--:--"
        out_t = c_curr["Out Time"].values[0] if not c_curr.empty and pd.notna(c_curr["Out Time"].values[0]) else "--:--"
        man = int(c_curr["Manifest"].values[0]) if not c_curr.empty and "Manifest" in c_curr.columns else 0
        can = int(c_curr["Cancel"].values[0]) if not c_curr.empty and "Cancel" in c_curr.columns else 0
        dis = int(c_curr["Dispatch"].values[0]) if not c_curr.empty and "Dispatch" in c_curr.columns else 0
        ret = int(c_curr["Return"].values[0]) if not c_curr.empty and "Return" in c_curr.columns else 0
        rem = str(c_curr["Remark"].values[0]) if not c_curr.empty and pd.notna(c_curr["Remark"].values[0]) else ""
        y_pend = yest_pend_map.get(c, 0)
        
        final_pend = max(0, (man + y_pend) - can - dis + ret)
        
        display_summary_rows.append({
            "Courier": c,
            "Yesterday Pending": y_pend,
            "In Time": in_t,
            "Out Time": out_t,
            "Manifest": man,
            "Cancel": can,
            "Dispatch": dis,
            "Return": ret,
            "Final Pending": final_pend,
            "Remark": rem
        })
        
    st.markdown("#### 📋 Complete Courier-wise Final Status Summary")
    st.dataframe(pd.DataFrame(display_summary_rows), use_container_width=True)

# ================= 3. EMPLOYEE & COURIER MANAGEMENT =================
elif nav_page == "👥 Employee & Courier Management":
    st.markdown("<div class='card-3d'><h3>👥 Employee & Courier Management (Add / Delete)</h3></div>", unsafe_allow_html=True)
    
    col_e1, col_e2 = st.columns(2, gap="large")
    
    with col_e1:
        st.markdown("#### 👤 Employee Management")
        
        with st.form("add_emp_form"):
            st.markdown("**Add New Employee**")
            new_emp_name = st.text_input("Employee Full Name")
            new_emp_id = st.text_input("Assign Employee ID (e.g., W231700)")
            if st.form_submit_button("➕ Add Employee"):
                if new_emp_name and new_emp_id:
                    st.session_state["employees"][new_emp_name] = new_emp_id
                    save_employees(st.session_state["employees"])
                    st.success(f"Employee {new_emp_name} added successfully!")
                    st.rerun()
                else:
                    st.warning("Please fill both Name and Employee ID.")

        with st.form("del_emp_form"):
            st.markdown("**Remove Existing Employee**")
            del_emp_name = st.selectbox("Select Employee to Remove", list(st.session_state["employees"].keys()))
            if st.form_submit_button("🗑️ Delete Selected Employee"):
                if del_emp_name in st.session_state["employees"]:
                    del st.session_state["employees"][del_emp_name]
                    save_employees(st.session_state["employees"])
                    st.success(f"Employee {del_emp_name} removed successfully!")
                    st.rerun()

        st.markdown("#### Current Employee List")
        emp_df = pd.DataFrame(list(st.session_state["employees"].items()), columns=["Employee Name", "Employee ID"])
        st.dataframe(emp_df, use_container_width=True)

    with col_e2:
        st.markdown("#### 🚚 Courier Management")
        
        with st.form("add_cour_form"):
            st.markdown("**Add New Courier Company**")
            new_cour_name = st.text_input("Courier Company Name")
            if st.form_submit_button("➕ Add Courier"):
                if new_cour_name and new_cour_name not in st.session_state["couriers"]:
                    st.session_state["couriers"].append(new_cour_name)
                    save_couriers(st.session_state["couriers"])
                    st.success(f"Courier {new_cour_name} added successfully!")
                    st.rerun()
                else:
                    st.warning("Please enter a valid or unique Courier name.")

        with st.form("del_cour_form"):
            st.markdown("**Remove Existing Courier Company**")
            del_cour_name = st.selectbox("Select Courier to Remove", st.session_state["couriers"])
            if st.form_submit_button("🗑️ Delete Selected Courier"):
                if len(st.session_state["couriers"]) > 1:
                    st.session_state["couriers"].remove(del_cour_name)
                    save_couriers(st.session_state["couriers"])
                    st.success(f"Courier {del_cour_name} removed successfully!")
                    st.rerun()
                else:
                    st.warning("At least one courier must remain.")

        st.markdown("#### Current Courier List")
        cour_df = pd.DataFrame({"Courier Company": st.session_state["couriers"]})
        st.dataframe(cour_df, use_container_width=True)

# ================= 4. ADMIN & RECYCLE BIN =================
elif nav_page == "♻️ Admin & Recycle Bin":
    st.markdown("<div class='card-3d'><h3>♻️ Admin Panel & Recycle Bin</h3></div>", unsafe_allow_html=True)
    
    if not st.session_state["admin_logged"]:
        st.warning("🔒 Sidebar mein password dalkar Admin Mode unlock karein.")
    else:
        st.success("✅ Admin Access Granted.")
        
        st.markdown("#### 🔑 Change Admin Password")
        with st.form("change_pass_form"):
            new_admin_pass = st.text_input("Enter New Admin Password", type="password")
            confirm_admin_pass = st.text_input("Confirm New Admin Password", type="password")
            if st.form_submit_button("Update Password"):
                if new_admin_pass and new_admin_pass == confirm_admin_pass:
                    st.session_state["admin_password"] = new_admin_pass
                    save_admin_password(new_admin_pass)
                    st.success("Admin password updated successfully! Please use your new password next time.")
                else:
                    st.error("Passwords do not match or field is empty.")

        st.markdown("---")
        st.markdown("#### ♻️ Recycle Bin Data")
        trash_df = st.session_state["trash_data"]
        if not trash_df.empty:
            st.dataframe(trash_df, use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("♻️ Restore All Data"):
                    restore_data = trash_df.drop(columns=["Deleted Time"]) if "Deleted Time" in trash_df.columns else trash_df
                    st.session_state["data"] = pd.concat([st.session_state["data"], restore_data], ignore_index=True)
                    save_data(st.session_state["data"])
                    st.session_state["trash_data"] = pd.DataFrame(columns=trash_df.columns)
                    save_trash(st.session_state["trash_data"])
                    st.success("Data restored successfully!")
                    st.rerun()
            with col2:
                if st.button("🔥 Empty Recycle Bin"):
                    st.session_state["trash_data"] = pd.DataFrame(columns=trash_df.columns)
                    save_trash(st.session_state["trash_data"])
                    st.warning("Recycle bin emptied!")
                    st.rerun()
        else:
            st.info("♻️ Recycle Bin is empty.")
