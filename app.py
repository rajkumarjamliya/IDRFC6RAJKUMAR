from datetime import date, datetime, timedelta
import os
import urllib.parse
import pandas as pd
import streamlit as st

# ================= PAGE CONF & WEB THEME (Delhivery Style) =================
st.set_page_config(
    page_title="IDRFC6 – DEWAS Logistics Portal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Delhivery Red & Dark Grey Theme CSS
st.markdown(
    """
 <style>
 /* Global Background */
 .stApp {
     background-color: #f4f7f6;
     font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
 }
 
 /* Top Banner/Header */
 .main-header {
     background-color: #2e363c; /* Delhivery Dark Grey */
     padding: 20px;
     border-radius: 10px;
     color: white;
     text-align: center;
     box-shadow: 0 4px 15px rgba(0,0,0,0.2);
     border-bottom: 5px solid #e31d2b; /* Delhivery Red */
     margin-bottom: 25px;
 }
 .main-header h1 { margin: 0; font-size: 32px; font-weight: 800; letter-spacing: 1px; color: #ffffff; }
 .main-header p { margin: 5px 0 0 0; font-size: 16px; color: #fdfdfd; font-weight: 400; opacity: 0.9; }
 
 /* Cards & Containers Look */
 .css-1r6slb0, .css-1x84a4a, .stDataFrame, div[data-testid="stBlock"] {
     border-radius: 10px;
 }
 
 /* Web Page Block/Card Style */
 .wab-card {
     background-color: #ffffff;
     padding: 25px;
     border-radius: 12px;
     box-shadow: 0 5px 15px rgba(0,0,0,0.05);
     border: 1px solid #e1e8ed;
     margin-bottom: 20px;
 }
 .wab-card h4, .wab-card h3 {
     color: #2e363c;
     border-bottom: 2px solid #e31d2b;
     padding-bottom: 10px;
     margin-top: 0;
 }

 /* Custom Buttons (Delhivery Red) */
 div.stButton > button:first-child {
     background-color: #e31d2b !important;
     color: white !important;
     border: none !important;
     border-radius: 6px !important;
     padding: 10px 24px !important;
     font-weight: 600 !important;
     transition: all 0.3s ease;
     width: 100%;
 }
 div.stButton > button:first-child:hover {
     background-color: #b51722 !important;
     box-shadow: 0 4px 10px rgba(227, 29, 43, 0.3) !important;
 }
 
 /* Sidebar Styling */
 .css-1cpx64u { background-color: #ffffff; } /* Sidebar color */
 .css-10trblm { color: #e31d2b; } /* Sidebar Headers */
 
 /* WhatsApp Green Button */
 .wa-btn-container a {
     background-color: #25D366;
     color: white;
     padding: 12px 20px;
     text-decoration: none;
     border-radius: 8px;
     font-weight: bold;
     display: inline-flex;
     align-items: center;
     justify-content: center;
     width: 100%;
     box-shadow: 0 4px 10px rgba(37, 211, 102, 0.2);
     transition: background 0.3s;
 }
 .wa-btn-container a:hover { background-color: #1ebe57; color: white; }
 
 /* Success/Error Messages */
 .stAlert { border-radius: 8px; }
 </style>
 """,
    unsafe_allow_html=True,
)

# ================= DATA FILE PATHS =================
DATA_FILE = "warehouse_entries.csv"
REPORT_FILE = "dispatch_reports.csv"
TRASH_FILE = "recycle_bin.csv"
EMP_FILE = "employees_master.csv"
COURIER_FILE = "couriers_master.csv"
BACKUP_DIR = "backups"

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# ================= HELPERS & DATA LOADERS =================
def auto_backup():
    """Create a daily backup"""
    today_str = str(date.today())
    if os.path.exists(DATA_FILE):
        pd.read_csv(DATA_FILE).to_csv(os.path.join(BACKUP_DIR, f"backup_entries_{today_str}.csv"), index=False)
    if os.path.exists(REPORT_FILE):
        pd.read_csv(REPORT_FILE).to_csv(os.path.join(BACKUP_DIR, f"backup_reports_{today_str}.csv"), index=False)

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee ID", "Employee Name", "Task Type", "Courier", "Parcel Count"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    auto_backup()

def load_reports():
    if os.path.exists(REPORT_FILE):
        df = pd.read_csv(REPORT_FILE)
        cols = ["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"]
        for col in cols: 
            if col not in df.columns: df[col] = (0 if col in ["Manifest", "Cancel", "Dispatch", "Return"] else "--:--")
        return df
    return pd.DataFrame(columns=["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"])

def save_reports(df):
    df.to_csv(REPORT_FILE, index=False)
    auto_backup()

def load_trash():
    if os.path.exists(TRASH_FILE): return pd.read_csv(TRASH_FILE)
    return pd.DataFrame()

def load_employees():
    if os.path.exists(EMP_FILE): return pd.read_csv(EMP_FILE)
    default_emp = pd.DataFrame({"Employee ID": ["EMP001", "EMP002"], "Employee Name": ["Rajkumar", "Operator"]})
    default_emp.to_csv(EMP_FILE, index=False)
    return default_emp

def save_employees(df): df.to_csv(EMP_FILE, index=False)

def load_couriers():
    if os.path.exists(COURIER_FILE): return pd.read_csv(COURIER_FILE)["Courier Name"].tolist()
    default_cour = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "Ekart"]
    pd.DataFrame({"Courier Name": default_cour}).to_csv(COURIER_FILE, index=False)
    return default_cour

def save_couriers(cour_list): pd.DataFrame({"Courier Name": cour_list}).to_csv(COURIER_FILE, index=False)

# ================= INITIALIZE SESSION STATES =================
if "data" not in st.session_state: st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state: st.session_state["dispatch_reports"] = load_reports()
if "trash_data" not in st.session_state: st.session_state["trash_data"] = load_trash()
if "employees" not in st.session_state: st.session_state["employees"] = load_employees()
if "couriers" not in st.session_state: st.session_state["couriers"] = load_couriers()
if "admin_logged" not in st.session_state: st.session_state["admin_logged"] = False

# ================= WEB PAGE HEADER (दिल्लीवरी Look) =================
st.markdown(
    """
<div class="main-header">
    <h1>IDRFC6 DEWAS OPERATION TEAM</h1>
    <p>⚡ Automated Logistics, Manifest, and Dispatch Management System | Operator: RAJKUMAR</p>
</div>
""",
    unsafe_allow_html=True,
)

# ================= SIDEBAR (NAVIGATION) =================
with st.sidebar:
    st.image("https://www.delhivery.com/wp-content/uploads/2018/10/Delhivery_Logo_Red_Black-1.png", width=200) # Placeholder or actual logo
    st.markdown("---")
    st.markdown("### ⚙️ CONTROL PANEL")
    selected_date = st.date_input("📅 Select Working Date", date.today())
    selected_date_str = str(selected_date)
    yesterday_str = str(selected_date - timedelta(days=1))

    nav_page = st.radio(
        "🌐 Navigation Menu",
        ["🏠 Home Operations", "📊 Employee Productivity", "♻️ Admin & Recycle Bin"]
    )

    # Admin Security
    st.markdown("---")
    st.markdown("### 🔐 SECURITY")
    ADMIN_PASS = "123" # Changable
    if not st.session_state["admin_logged"]:
        entered_pass = st.text_input("Enter Admin Password", type="password")
        if st.button("Unlock Admin"):
            if entered_pass == ADMIN_PASS:
                st.session_state["admin_logged"] = True
                st.rerun()
            else: st.error("Wrong password!")
    else:
        st.success("🔓 Admin Unlocked")
        if st.button("Lock Admin"):
            st.session_state["admin_logged"] = False
            st.rerun()

# ================= PAGE 1: HOME OPERATIONS =================
if nav_page == "🏠 Home Operations":
    
    # 📝 ENTRY FORM CARD
    st.markdown('<div class="wab-card"><h3>📝 New Work Entry</h3></div>', unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1.2])
        
        with col1:
            piklist_no = st.text_input("📋 Piklist No.")
            
            emp_df = st.session_state["employees"]
            selected_emp_name = st.selectbox("👤 Select Employee", ["-- Select --"] + emp_df["Employee Name"].tolist())
            emp_id = ""
            if selected_emp_name != "-- Select --":
                emp_id = emp_df[emp_df["Employee Name"] == selected_emp_name]["Employee ID"].values[0]
                st.caption(f"Employee ID: {emp_id}")

        with col2:
            task_type = st.selectbox("🛠️ Task Type", ["Picking", "Packing", "Scanning", "Load", "Unload", "Manifest"])
            parcel_count = st.number_input("📦 Parcel/Box Count", min_value=1, value=1)

        with col3:
            courier = "N/A"
            if task_type == "Manifest":
                courier = st.selectbox("🚚 Select Courier Company", st.session_state["couriers"])
                st.warning(f"Manifesting: {parcel_count} boxes for {courier}")
            
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("💾 Submit Entry"):
                if piklist_no andselected_emp_name != "-- Select --":
                    now = datetime.now()
                    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    in_time_auto = now.strftime("%I:%M %p")
                    out_time_auto = (now + timedelta(minutes=5)).strftime("%I:%M %p") # Placeholder auto out time

                    new_entry = pd.DataFrame({
                        "ID": [str(pd.Timestamp.now().timestamp())], "Date": [selected_date_str],
                        "Timestamp": [current_time], "Piklist No.": [str(piklist_no)],
                        "Employee ID": [emp_id], "Employee Name": [selected_emp_name],
                        "Task Type": [task_type], "Courier": [courier], "Parcel Count": [int(parcel_count)]
                    })
                    
                    st.session_state["data"] = pd.concat([st.session_state["data"], new_entry], ignore_index=True)
                    save_data(st.session_state["data"])

                    # If Manifest, update dispatch report auto
                    if task_type == "Manifest":
                        rep_df = st.session_state["dispatch_reports"]
                        curr_cour = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == courier)]
                        
                        if not curr_cour.empty:
                            idx = curr_cour.index[0]
                            rep_df.loc[idx, "Manifest"] += int(parcel_count)
                        else:
                            new_rep = pd.DataFrame({
                                "Date": [selected_date_str], "Courier": [courier],
                                "In Time": [in_time_auto], "Out Time": ["--:--"],
                                "Manifest": [int(parcel_count)], "Cancel": [0], "Dispatch": [0], "Return": [0],
                                "Remark": ["Auto"]
                            })
                            rep_df = pd.concat([rep_df, new_rep], ignore_index=True)
                        st.session_state["dispatch_reports"] = rep_df
                        save_reports(rep_df)

                    st.success("Entry Saved!")
                    st.rerun()
                else: st.error("Piklist No. and Employee are mandatory!")

    # 📊 LIVE RECORDS TABLE
    st.markdown(f'<div class="wab-card"><h4>📋 Live Records ({selected_date_str})</h4></div>', unsafe_allow_html=True)
    df = st.session_state["data"]
    df_today = df[df["Date"] == selected_date_str] if not df.empty else pd.DataFrame()
    
    if not df_today.empty:
        #Delhivery Style Dataframe
        st.dataframe(
            df_today[["Timestamp", "Piklist No.", "Employee Name", "Task Type", "Courier", "Parcel Count"]].sort_values(by="Timestamp", ascending=False),
            use_container_width=True
        )
    else: st.info("No records for today yet.")

    st.markdown("---")
    
    # 🚚 DISPATCH SUMMARY CARD
    st.markdown(f'<div class="wab-card WabRed"><h3>🚛 Dispatch & Courier Summary ({selected_date_str})</h3></div>', unsafe_allow_html=True)
    
    rep_df = st.session_state["dispatch_reports"]
    
    # Data sync with operator entries and yesterdays pending
    today_ops = df_today[df_today["Task Type"] == "Manifest"] if not df_today.empty else pd.DataFrame()
    today_disp_rep = rep_df[rep_df["Date"] == selected_date_str] if not rep_df.empty else pd.DataFrame()
    yesterday_disp_rep = rep_df[rep_df["Date"] == yesterday_str] if not rep_df.empty else pd.DataFrame()
    
    final_rows = []
    whatsapp_text = f"*DEWAS OPERATIONS - DISPATCH REPORT*\n📅 Date: {selected_date_str}\n---\n"
    total_pend = 0

    for c_name in st.session_state["couriers"]:
        # Operator entries sum
        man_ops = today_ops[today_ops["Courier"] == c_name]["Parcel Count"].sum() if not today_ops.empty else 0
        
        # Report table data (In/Out/Disp)
        c_rep = today_disp_rep[today_disp_rep["Courier"] == c_name]
        man_rep = int(c_rep["Manifest"].values[0]) if not c_rep.empty else 0
        # Sync ops data with rep data
        man_final = max(man_ops, man_rep)
        
        in_t = c_rep["In Time"].values[0] if not c_rep.empty else "--:--"
        out_t = c_rep["Out Time"].values[0] if not c_rep.empty else "--:--"
        can = int(c_rep["Cancel"].values[0]) if not c_rep.empty else 0
        disp = int(c_rep["Dispatch"].values[0]) if not c_rep.empty else 0
        ret = int(c_rep["Return"].values[0]) if not c_rep.empty else 0
        remark = c_rep["Remark"].values[0] if not c_rep.empty else ""
        
        # Update Report if mismatch found
        if not c_rep.empty and man_final > man_rep:
             idx = today_disp_rep[today_disp_rep["Courier"] == c_name].index[0]
             rep_df.loc[idx, "Manifest"] = man_final
             save_reports(rep_df)

        # Yesterday Pending
        c_yes = yesterday_disp_rep[yesterday_disp_rep["Courier"] == c_name]
        y_pend = max(0, int(c_yes["Manifest"].values[0]) - int(c_yes["Cancel"].values[0]) - int(c_yes["Dispatch"].values[0])) if not c_yes.empty else 0
        
        # Final Pending
        pend = max(0, (y_pend + man_final) - can - disp)
        total_pend += pend
        
        final_rows.append({
            "Courier": c_name, "Yes. Pend": y_pend, "In Time": in_t, "Out Time": out_t,
            "Today Manif.": man_final, "Cancel": can, "Dispatch": disp, "Return": ret,
            "PENDING": pend, "Remark": remark
        })
        
        whatsapp_text += f"*{c_name}*:\n   T: {man_final} | D: {disp} | C: {can} | *P: {pend}*\n"

    # Delhivery styled Summary Table
    st.dataframe(pd.DataFrame(final_rows), use_container_width=True)
    
    col_w1, col_w2 = st.columns([2,1])
    with col_w1:
        st.caption(f"Yesterday Pending based on {yesterday_str} records. PENDING = (Yes.Pend + Manif) - Cancel - Dispatch.")
    with col_w2:
        # WhatsApp Share
        whatsapp_text += f"---\n*Total Pending: {total_pend}*"
        encoded_text = urllib.parse.quote(whatsapp_text)
        wa_link = f"https://wa.me/?text={encoded_text}"
        st.markdown(f'<div class="wa-btn-container"><a href="{wa_url}" target="_blank">📲 Share on WhatsApp</a></div>', unsafe_allow_html=True)

    # ✏️ ADMIN REPORT EDIT (Below Table)
    if st.session_state["admin_logged"]:
        with st.expander("✏️ Admin: Edit Dispatch Report/Remark", expanded=False):
            with st.form("edit_report_form"):
                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    e_cour = st.selectbox("Courier", st.session_state["couriers"])
                    e_in = st.text_input("In Time (e.g. 10:30 AM)")
                with col_e2:
                    e_out = st.text_input("Out Time (e.g. 05:00 PM)")
                    e_disp = st.number_input("Set Dispatch Count", min_value=0, value=0)
                with col_e3:
                    e_can = st.number_input("Set Cancel Count", min_value=0, value=0)
                    e_remark = st.text_input("Remark")
                
                if st.form_submit_button("Update Report"):
                    rep_df = st.session_state["dispatch_reports"]
                    curr_rep_cour = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == e_cour)]
                    
                    if not curr_rep_cour.empty:
                        idx = curr_rep_cour.index[0]
                        if e_in: rep_df.loc[idx, "In Time"] = e_in
                        if e_out: rep_df.loc[idx, "Out Time"] = e_out
                        if e_disp > 0: rep_df.loc[idx, "Dispatch"] = e_disp
                        if e_can > 0: rep_df.loc[idx, "Cancel"] = e_can
                        rep_df.loc[idx, "Remark"] = e_remark
                        save_reports(rep_df)
                        st.success("Updated!")
                        st.rerun()
                    else: st.error("No manifest entry by operator for this courier today.")

# ================= PAGE 2: EMPLOYEE PRODUCTIVITY =================
elif nav_page == "📊 Employee Productivity":
    st.markdown(f'<div class="wab-card"><h3>📊 Employee Work Report ({selected_date_str})</h3></div>', unsafe_allow_html=True)
    df = st.session_state["data"]
    df_today = df[df["Date"] == selected_date_str] if not df.empty else pd.DataFrame()
    
    if not df_today.empty:
        # Employee Summary
        emp_prod = df_today.groupby(["Employee ID", "Employee Name", "Task Type"])["Parcel Count"].sum().reset_index()
        # Pivot for Delhivery web report style
        pivot_prod = emp_prod.pivot(index=["Employee ID", "Employee Name"], columns="Task Type", values="Parcel Count").reset_index().fillna(0)
        
        st.dataframe(pivot_prod, use_container_width=True)
        
        # Chart
        st.markdown("---")
        st.bar_chart(emp_prod, x="Employee Name", y="Parcel Count", color="Task Type", stack=False)

    else: st.info("No records found for this date.")

# ================= PAGE 3: ADMIN & RECYCLE BIN =================
elif nav_page == "♻️ Admin & Recycle Bin":
    st.markdown('<div class="wab-card WabRed"><h3>🔐 Admin Setup & Data Management</h3></div>', unsafe_allow_html=True)
    
    if not st.session_state["admin_logged"]:
        st.warning("Locked Section. Enter password in sidebar to unlock.")
    else:
        # DATA MASTERS
        tab_data, tab_trash = st.tabs(["⚙️ Master Tables", "♻️ Recycle Bin"])
        
        with tab_data:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                # Employees
                st.markdown("#### 👤 Employee Master")
                emp_df = st.session_state["employees"]
                new_e_id = st.text_input("Employee ID")
                new_e_name = st.text_input("Employee Name")
                if st.button("➕ Add Employee"):
                    if new_e_id and new_e_name:
                        new_e = pd.DataFrame({"Employee ID": [new_e_id], "Employee Name": [new_e_name]})
                        emp_df = pd.concat([emp_df, new_e], ignore_index=True)
                        save_employees(emp_df)
                        st.session_state["employees"] = emp_df
                        st.success("Added!")
                        st.rerun()
                st.dataframe(emp_df, use_container_width=True)
            
            with col_d2:
                # Couriers
                st.markdown("#### 🚚 Courier Master")
                couriers_list = st.session_state["couriers"]
                new_c = st.text_input("New Courier Name")
                if st.button("➕ Add Courier"):
                    if new_c and new_c not in couriers_list:
                        couriers_list.append(new_c)
                        save_couriers(couriers_list)
                        st.success("Added!")
                        st.rerun()
                st.write("**Current Couriers:**")
                st.write(couriers_list)

        # RECYCLE BIN
        with tab_trash:
            st.markdown("#### 🗑️ Deleted Records (Entries)")
            trash_df = st.session_state["trash_data"]
            
            if not trash_df.empty:
                st.dataframe(trash_df, use_container_width=True)
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    if st.button("♻️ Restore All Data"):
                        restore_df = trash_df.drop(columns=["Deleted Time"])
                        st.session_state["data"] = pd.concat([st.session_state["data"], restore_df], ignore_index=True)
                        save_data(st.session_state["data"])
                        save_trash(pd.DataFrame(columns=trash_df.columns))
                        st.session_state["trash_data"] = load_trash()
                        st.success("All data restored!")
                        st.rerun()
                with col_t2:
                    if st.button("🔥 Empty Recycle Bin permanently"):
                        save_trash(pd.DataFrame(columns=trash_df.columns))
                        st.session_state["trash_data"] = load_trash()
                        st.warning("Recycle Bin Emptied!")
                        st.rerun()
            else: st.info("Recycle Bin is empty.")
