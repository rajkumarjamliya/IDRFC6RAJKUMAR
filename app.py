from datetime import date, datetime, timedelta
import io
import os
import urllib.parse
import pandas as pd
import streamlit as st

# ================= PAGE CONF & WEB THEME =================
st.set_page_config(
    page_title="IDRFC6 – DEWAS Logistics Portal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown(
    """
 <style>
 .stApp {
     background-color: #f4f7f6;
     font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
 }
 .main-header {
     background: linear-gradient(135deg, #2e363c 0%, #1a1e21 100%);
     padding: 24px;
     border-radius: 12px;
     color: white;
     text-align: center;
     box-shadow: 0 6px 20px rgba(0,0,0,0.15);
     border-bottom: 5px solid #e31d2b;
     margin-bottom: 25px;
 }
 .main-header h1 { margin: 0; font-size: 30px; font-weight: 800; letter-spacing: 1px; color: #ffffff; }
 .main-header p { margin: 6px 0 0 0; font-size: 14px; color: #e1e8ed; font-weight: 400; }
 
 .wab-card {
     background-color: #ffffff;
     padding: 20px;
     border-radius: 12px;
     box-shadow: 0 4px 12px rgba(0,0,0,0.05);
     border: 1px solid #e1e8ed;
     margin-bottom: 22px;
 }
 .wab-card h4, .wab-card h3 {
     color: #2e363c;
     border-bottom: 2px solid #e31d2b;
     padding-bottom: 8px;
     margin-top: 0;
     font-weight: 700;
 }

 div.stButton > button:first-child {
     background-color: #e31d2b !important;
     color: white !important;
     border: none !important;
     border-radius: 6px !important;
     padding: 10px 20px !important;
     font-weight: 600 !important;
     width: 100%;
     transition: all 0.2s ease-in-out;
 }
 div.stButton > button:first-child:hover {
     background-color: #b51722 !important;
     box-shadow: 0 4px 10px rgba(227, 29, 43, 0.3) !important;
 }
 
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
 }
 .wa-btn-container a:hover { background-color: #1ebe57; color: white; }
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
    today_str = str(date.today())
    if os.path.exists(DATA_FILE):
        pd.read_csv(DATA_FILE).to_csv(os.path.join(BACKUP_DIR, f"backup_entries_{today_str}.csv"), index=False)
    if os.path.exists(REPORT_FILE):
        pd.read_csv(REPORT_FILE).to_csv(os.path.join(BACKUP_DIR, f"backup_reports_{today_str}.csv"), index=False)

def load_data():
    if os.path.exists(DATA_FILE): 
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee ID", "Employee Name", "Task Type", "Courier", "Parcel Count"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    auto_backup()

def load_reports():
    if os.path.exists(REPORT_FILE):
        df = pd.read_csv(REPORT_FILE)
        cols = ["Date", "Courier", "Vehicle No", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"]
        for col in cols: 
            if col not in df.columns: 
                df[col] = (0 if col in ["Manifest", "Cancel", "Dispatch", "Return"] else ("--" if col == "Vehicle No" else "--:--"))
        return df
    return pd.DataFrame(columns=["Date", "Courier", "Vehicle No", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"])

def save_reports(df):
    df.to_csv(REPORT_FILE, index=False)
    auto_backup()

def load_employees():
    if os.path.exists(EMP_FILE): return pd.read_csv(EMP_FILE)
    default_emp = pd.DataFrame({"Employee ID": ["EMP001", "EMP002"], "Employee Name": ["Rajkumar", "Operator"]})
    default_emp.to_csv(EMP_FILE, index=False)
    return default_emp

def save_employees(df): df.to_csv(EMP_FILE, index=False)

def load_couriers():
    if os.path.exists(COURIER_FILE): 
        df = pd.read_csv(COURIER_FILE)
        if "Vehicle No" not in df.columns:
            df["Vehicle No"] = "MP09-XX-0000"
        return df
    
    default_cour = pd.DataFrame({
        "Courier Name": ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "Ekart"],
        "Vehicle No": ["MP09-AB-1234", "MP09-CD-5678", "MP09-EF-9012", "MP09-GH-3456", "MP09-IJ-7890"]
    })
    default_cour.to_csv(COURIER_FILE, index=False)
    return default_cour

def save_couriers(df): 
    df.to_csv(COURIER_FILE, index=False)

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ================= SESSION INITIALIZATION =================
if "data" not in st.session_state: st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state: st.session_state["dispatch_reports"] = load_reports()
if "employees" not in st.session_state: st.session_state["employees"] = load_employees()
if "couriers_df" not in st.session_state: st.session_state["couriers_df"] = load_couriers()
if "admin_logged" not in st.session_state: st.session_state["admin_logged"] = False

# ================= WEB HEADER =================
st.markdown(
    """
<div class="main-header">
    <h1>IDRFC6 DEWAS OPERATION PORTAL</h1>
    <p>⚡ Fast Warehouse Dispatch & Employee Management | Lead: RAJKUMAR</p>
</div>
""",
    unsafe_allow_html=True,
)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ CONTROL PANEL")
    selected_date = st.date_input("📅 Working Date", date.today())
    selected_date_str = str(selected_date)
    yesterday_str = str(selected_date - timedelta(days=1))

    nav_page = st.radio(
        "🌐 Navigation Menu",
        ["🏠 Home Operations", "📊 Employee Productivity", "🔐 Admin & Data Export"]
    )

    st.markdown("---")
    st.markdown("### 🔐 SECURITY LOCK")
    ADMIN_PASS = "123"
    if not st.session_state["admin_logged"]:
        entered_pass = st.text_input("Enter Admin Password", type="password")
        if st.button("Unlock Admin"):
            if entered_pass == ADMIN_PASS:
                st.session_state["admin_logged"] = True
                st.rerun()
            else: 
                st.error("Invalid Admin Password!")
    else:
        st.success("🔓 Admin Access Active")
        if st.button("Lock Admin"):
            st.session_state["admin_logged"] = False
            st.rerun()

# ================= PAGE 1: HOME OPERATIONS =================
if nav_page == "🏠 Home Operations":
    
    df = st.session_state["data"]
    df_today = df[df["Date"] == selected_date_str] if not df.empty else pd.DataFrame()
    
    total_parcels = df_today["Parcel Count"].sum() if not df_today.empty else 0
    total_entries = len(df_today) if not df_today.empty else 0
    active_emps = df_today["Employee Name"].nunique() if not df_today.empty else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("📦 Total Parcels Today", total_parcels)
    m2.metric("📝 Entries Logged", total_entries)
    m3.metric("👷 Active Staff Today", active_emps)

    couriers_df = st.session_state["couriers_df"]
    courier_list = couriers_df["Courier Name"].tolist()

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

        with col2:
            task_type = st.selectbox("🛠️ Task Type", ["Picking", "Packing", "Scanning", "Load", "Unload", "Manifest"])
            parcel_count = st.number_input("📦 Parcel/Box Count", min_value=1, value=1)

        with col3:
            courier = "N/A"
            if task_type == "Manifest":
                courier = st.selectbox("🚚 Select Courier Company", courier_list)
            
            st.write("")
            st.write("")
            if st.button("💾 Submit Work Entry"):
                if piklist_no and selected_emp_name != "-- Select --":
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    new_entry = pd.DataFrame({
                        "ID": [str(pd.Timestamp.now().timestamp())], 
                        "Date": [selected_date_str],
                        "Timestamp": [now_str], 
                        "Piklist No.": [str(piklist_no)],
                        "Employee ID": [emp_id], 
                        "Employee Name": [selected_emp_name],
                        "Task Type": [task_type], 
                        "Courier": [courier], 
                        "Parcel Count": [int(parcel_count)]
                    })
                    
                    st.session_state["data"] = pd.concat([st.session_state["data"], new_entry], ignore_index=True)
                    save_data(st.session_state["data"])

                    if task_type == "Manifest":
                        rep_df = st.session_state["dispatch_reports"]
                        curr_cour = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == courier)]
                        v_no = couriers_df[couriers_df["Courier Name"] == courier]["Vehicle No"].values[0] if courier in couriers_df["Courier Name"].values else "--"

                        if not curr_cour.empty:
                            idx = curr_cour.index[0]
                            rep_df.loc[idx, "Manifest"] += int(parcel_count)
                        else:
                            new_rep = pd.DataFrame({
                                "Date": [selected_date_str], 
                                "Courier": [courier],
                                "Vehicle No": [v_no],
                                "In Time": ["--:--"], 
                                "Out Time": ["--:--"],
                                "Manifest": [int(parcel_count)], 
                                "Cancel": [0], 
                                "Dispatch": [0], 
                                "Return": [0],
                                "Remark": ["Auto Logged"]
                            })
                            rep_df = pd.concat([rep_df, new_rep], ignore_index=True)
                        st.session_state["dispatch_reports"] = rep_df
                        save_reports(rep_df)

                    st.success("Entry Saved Successfully!")
                    st.rerun()
                else: 
                    st.error("Piklist No. & Employee Selection are mandatory!")

    # LIVE LOG TABLE (EDITABLE)
    st.markdown(f'<div class="wab-card"><h4>📋 Live Task Log ({selected_date_str}) - [Click Cell to Edit / Select Row to Delete]</h4></div>', unsafe_allow_html=True)
    if not df_today.empty:
        edited_today = st.data_editor(
            df_today,
            key="home_live_editor",
            num_rows="dynamic",
            use_container_width=True
        )
        if st.button("💾 Save Changes to Task Log"):
            all_df = st.session_state["data"]
            all_df = all_df[all_df["Date"] != selected_date_str]
            updated_df = pd.concat([all_df, edited_today], ignore_index=True)
            st.session_state["data"] = updated_df
            save_data(updated_df)
            st.success("Live Log Updated Successfully!")
            st.rerun()
    else: 
        st.info("No records logged for today yet.")

    st.markdown("---")
    
    # DISPATCH HUB
    st.markdown(f'<div class="wab-card"><h3>🚚 Courier Dispatch Live Hub ({selected_date_str})</h3></div>', unsafe_allow_html=True)
    
    rep_df = st.session_state["dispatch_reports"]
    col_in, col_box, col_out = st.columns([1, 1.2, 1], gap="medium")

    # 1. IN-TIME MODULE
    with col_in:
        st.markdown("#### 1. 📌 Courier In-Time")
        c_in_sel = st.selectbox("Select Courier (IN)", courier_list, key="c_in_key")
        default_v = couriers_df[couriers_df["Courier Name"] == c_in_sel]["Vehicle No"].values[0] if c_in_sel in couriers_df["Courier Name"].values else ""
        c_in_veh = st.text_input("🚚 Vehicle No.", value=default_v, key="c_in_veh_key")

        if st.button("📌 Auto IN-Time"):
            now_in = datetime.now().strftime("%I:%M %p")
            curr_r = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == c_in_sel)]
            if not curr_r.empty:
                idx = curr_r.index[0]
                rep_df.loc[idx, "In Time"] = now_in
                rep_df.loc[idx, "Vehicle No"] = c_in_veh
            else:
                new_r = pd.DataFrame({
                    "Date": [selected_date_str], "Courier": [c_in_sel],
                    "Vehicle No": [c_in_veh],
                    "In Time": [now_in], "Out Time": ["--:--"],
                    "Manifest": [0], "Cancel": [0], "Dispatch": [0], "Return": [0], "Remark": ["In-Time Marked"]
                })
                rep_df = pd.concat([rep_df, new_r], ignore_index=True)
            st.session_state["dispatch_reports"] = rep_df
            save_reports(rep_df)
            st.success(f"In-Time {now_in} saved!")
            st.rerun()

    # 2. DISPATCH BOX ENTRY
    with col_box:
        st.markdown("#### 2. 📦 Dispatch Box Entry")
        c_box_sel = st.selectbox("Select Courier (Dispatch)", courier_list, key="c_box_key")
        box_qty = st.number_input("Dispatch Boxes Count", min_value=1, value=10, step=1)
        if st.button("📦 Add Dispatch Boxes"):
            curr_r = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == c_box_sel)]
            v_no = couriers_df[couriers_df["Courier Name"] == c_box_sel]["Vehicle No"].values[0] if c_box_sel in couriers_df["Courier Name"].values else "--"

            if not curr_r.empty:
                idx = curr_r.index[0]
                rep_df.loc[idx, "Dispatch"] += int(box_qty)
            else:
                new_r = pd.DataFrame({
                    "Date": [selected_date_str], "Courier": [c_box_sel],
                    "Vehicle No": [v_no],
                    "In Time": ["--:--"], "Out Time": ["--:--"],
                    "Manifest": [0], "Cancel": [0], "Dispatch": [int(box_qty)], "Return": [0], "Remark": ["Box Entry Added"]
                })
                rep_df = pd.concat([rep_df, new_r], ignore_index=True)
            st.session_state["dispatch_reports"] = rep_df
            save_reports(rep_df)
            st.success(f"{box_qty} Boxes Added!")
            st.rerun()

    # 3. OUT-TIME MODULE
    with col_out:
        st.markdown("#### 3. 🏁 Courier Out-Time")
        c_out_sel = st.selectbox("Select Courier (OUT)", courier_list, key="c_out_key")
        if st.button("🏁 Auto OUT-Time"):
            now_out = datetime.now().strftime("%I:%M %p")
            curr_r = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == c_out_sel)]
            v_no = couriers_df[couriers_df["Courier Name"] == c_out_sel]["Vehicle No"].values[0] if c_out_sel in couriers_df["Courier Name"].values else "--"

            if not curr_r.empty:
                idx = curr_r.index[0]
                rep_df.loc[idx, "Out Time"] = now_out
            else:
                new_r = pd.DataFrame({
                    "Date": [selected_date_str], "Courier": [c_out_sel],
                    "Vehicle No": [v_no],
                    "In Time": ["--:--"], "Out Time": [now_out],
                    "Manifest": [0], "Cancel": [0], "Dispatch": [0], "Return": [0], "Remark": ["Out-Time Marked"]
                })
                rep_df = pd.concat([rep_df, new_r], ignore_index=True)
            st.session_state["dispatch_reports"] = rep_df
            save_reports(rep_df)
            st.success(f"Out-Time {now_out} saved!")
            st.rerun()

    st.markdown("---")
    st.markdown("#### 📊 Live Dispatch Table (Direct Edit Option)")
    st.caption("👉 Aap kisi bhi cell par click karke In Time, Out Time, Dispatch, Cancel, Vehicle No direct badal sakte hain!")

    today_ops = df_today[df_today["Task Type"] == "Manifest"] if not df_today.empty else pd.DataFrame()
    today_disp_rep = rep_df[rep_df["Date"] == selected_date_str] if not rep_df.empty else pd.DataFrame()
    yesterday_disp_rep = rep_df[rep_df["Date"] == yesterday_str] if not rep_df.empty else pd.DataFrame()
    
    final_rows = []
    whatsapp_text = f"*IDRFC6 DEWAS - DISPATCH REPORT*\n📅 Date: {selected_date_str}\n-----------------------------------\n"
    total_pend = 0

    for c_name in courier_list:
        man_ops = today_ops[today_ops["Courier"] == c_name]["Parcel Count"].sum() if not today_ops.empty else 0
        c_rep = today_disp_rep[today_disp_rep["Courier"] == c_name]
        man_rep = int(c_rep["Manifest"].values[0]) if not c_rep.empty else 0
        man_final = max(man_ops, man_rep)
        
        default_v = couriers_df[couriers_df["Courier Name"] == c_name]["Vehicle No"].values[0] if c_name in couriers_df["Courier Name"].values else "--"
        veh_no = c_rep["Vehicle No"].values[0] if (not c_rep.empty and str(c_rep["Vehicle No"].values[0]) != "--") else default_v

        in_t = c_rep["In Time"].values[0] if not c_rep.empty else "--:--"
        out_t = c_rep["Out Time"].values[0] if not c_rep.empty else "--:--"
        can = int(c_rep["Cancel"].values[0]) if not c_rep.empty else 0
        disp = int(c_rep["Dispatch"].values[0]) if not c_rep.empty else 0
        ret = int(c_rep["Return"].values[0]) if not c_rep.empty else 0
        remark = c_rep["Remark"].values[0] if not c_rep.empty else ""

        c_yes = yesterday_disp_rep[yesterday_disp_rep["Courier"] == c_name]
        y_pend = max(0, int(c_yes["Manifest"].values[0]) - int(c_yes["Cancel"].values[0]) - int(c_yes["Dispatch"].values[0])) if not c_yes.empty else 0
        
        pend = max(0, (y_pend + man_final) - can - disp)
        total_pend += pend
        
        final_rows.append({
            "Courier": c_name, 
            "Vehicle No": veh_no,
            "In Time": in_t, 
            "Out Time": out_t,
            "Yes. Pend": y_pend, 
            "Today Manif.": man_final, 
            "Cancel": can, 
            "Dispatch": disp, 
            "Return": ret,
            "PENDING": pend, 
            "Remark": remark
        })
        
        whatsapp_text += f"🚚 *{c_name}* ({veh_no}): In:{in_t} | Out:{out_t} | Man:{man_final} | Disp:{disp} | *Pend:{pend}*\n"

    disp_table_df = pd.DataFrame(final_rows)
    edited_disp_table = st.data_editor(disp_table_df, key="dispatch_live_editor", use_container_width=True)

    if st.button("💾 Save Direct Edits to Dispatch Table"):
        for _, row in edited_disp_table.iterrows():
            c_name = row["Courier"]
            curr_r = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == c_name)]
            if not curr_r.empty:
                idx = curr_r.index[0]
                rep_df.loc[idx, "Vehicle No"] = row["Vehicle No"]
                rep_df.loc[idx, "In Time"] = row["In Time"]
                rep_df.loc[idx, "Out Time"] = row["Out Time"]
                rep_df.loc[idx, "Manifest"] = int(row["Today Manif."])
                rep_df.loc[idx, "Cancel"] = int(row["Cancel"])
                rep_df.loc[idx, "Dispatch"] = int(row["Dispatch"])
                rep_df.loc[idx, "Return"] = int(row["Return"])
                rep_df.loc[idx, "Remark"] = row["Remark"]
            else:
                new_r = pd.DataFrame({
                    "Date": [selected_date_str], "Courier": [c_name],
                    "Vehicle No": [row["Vehicle No"]],
                    "In Time": [row["In Time"]], "Out Time": [row["Out Time"]],
                    "Manifest": [int(row["Today Manif."])], "Cancel": [int(row["Cancel"])], 
                    "Dispatch": [int(row["Dispatch"])], "Return": [int(row["Return"])], 
                    "Remark": [row["Remark"]]
                })
                rep_df = pd.concat([rep_df, new_r], ignore_index=True)
        
        st.session_state["dispatch_reports"] = rep_df
        save_reports(rep_df)
        st.success("Dispatch Data Changes Saved!")
        st.rerun()

    col_w1, col_w2 = st.columns([2, 1])
    with col_w1:
        st.caption("Formula: PENDING = (Yesterday Pending + Today Manifest) - Cancel - Dispatch")
    with col_w2:
        whatsapp_text += f"-----------------------------------\n*Total Pending: {total_pend}*"
        encoded_text = urllib.parse.quote(whatsapp_text)
        wa_link = f"https://wa.me/?text={encoded_text}"
        st.markdown(f'<div class="wa-btn-container"><a href="{wa_link}" target="_blank">📲 Share Report on WhatsApp</a></div>', unsafe_allow_html=True)

# ================= PAGE 2: EMPLOYEE PRODUCTIVITY =================
elif nav_page == "📊 Employee Productivity":
    st.markdown(f'<div class="wab-card"><h3>📊 Staff Performance & Work Summary ({selected_date_str})</h3></div>', unsafe_allow_html=True)
    df = st.session_state["data"]
    df_today = df[df["Date"] == selected_date_str] if not df.empty else pd.DataFrame()
    
    if not df_today.empty:
        emp_summary = df_today.groupby(["Employee ID", "Employee Name"])["Parcel Count"].sum().reset_index()
        total_team_parcels = emp_summary["Parcel Count"].sum()
        
        emp_summary["Contribution %"] = ((emp_summary["Parcel Count"] / total_team_parcels) * 100).round(2) if total_team_parcels > 0 else 0.0
        emp_summary = emp_summary.sort_values(by="Parcel Count", ascending=False)

        col_p1, col_p2 = st.columns([1.2, 1])
        
        with col_p1:
            st.markdown("#### 🏆 Staff Contribution Breakdown")
            for _, row in emp_summary.iterrows():
                st.write(f"**{row['Employee Name']}** ({row['Employee ID']})")
                st.progress(float(row['Contribution %']) / 100.0)
                st.caption(f"Total Parcels: {int(row['Parcel Count'])} | Share: {row['Contribution %']}%")
                st.write("---")

        with col_p2:
            st.markdown("#### 📊 Task Breakdown Table")
            pivot_prod = df_today.pivot_table(index=["Employee ID", "Employee Name"], columns="Task Type", values="Parcel Count", aggfunc="sum", fill_value=0).reset_index()
            st.dataframe(pivot_prod, use_container_width=True)

            # LADKON KE KAAM KI REPORT CSV DOWNLOAD
            csv_data = convert_df_to_csv(pivot_prod)
            st.download_button(
                label="📥 Download Staff Report CSV",
                data=csv_data,
                file_name=f"Staff_Performance_{selected_date_str}.csv",
                mime="text/csv"
            )

        st.markdown("---")
        st.markdown("#### 📈 Staff Wise Task Chart")
        emp_prod = df_today.groupby(["Employee Name", "Task Type"])["Parcel Count"].sum().reset_index()
        st.bar_chart(emp_prod, x="Employee Name", y="Parcel Count", color="Task Type", stack=False)
    else: 
        st.info("No records logged for this selected date.")

# ================= PAGE 3: ADMIN & EXCEL EXPORT =================
elif nav_page == "🔐 Admin & Data Export":
    st.markdown('<div class="wab-card"><h3>🔐 Admin Control & Old Data Report Generator</h3></div>', unsafe_allow_html=True)
    
    if not st.session_state["admin_logged"]:
        st.warning("⚠️ Access Locked! Enter password (123) in sidebar.")
    else:
        tab_export, tab_master, tab_reset = st.tabs(["📊 Purana Data Search & Export", "⚙️ Master Tables (Courier & Staff)", "🗑️ Reset / Clear Data"])
        
        # TAB 1: DATE RANGE PURANA DATA EXPORT
        with tab_export:
            st.markdown("#### 📅 Select Date Range for Old Data Report")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                from_d = st.date_input("From Date", date.today() - timedelta(days=7))
            with col_d2:
                to_d = st.date_input("To Date", date.today())

            all_df = st.session_state["data"]
            if not all_df.empty:
                all_df["Date_dt"] = pd.to_datetime(all_df["Date"])
                mask = (all_df["Date_dt"] >= pd.to_datetime(from_d)) & (all_df["Date_dt"] <= pd.to_datetime(to_d))
                filtered_df = all_df.loc[mask].drop(columns=["Date_dt"])
            else:
                filtered_df = pd.DataFrame()

            st.write(f"**Total Records found between {from_d} and {to_d}:** {len(filtered_df)}")
            
            if not filtered_df.empty:
                edited_admin_data = st.data_editor(filtered_df, key="admin_data_editor", num_rows="dynamic", use_container_width=True)
                
                col_save, col_dl = st.columns(2)
                with col_save:
                    if st.button("💾 Save Admin Table Modifications"):
                        st.session_state["data"] = edited_admin_data
                        save_data(edited_admin_data)
                        st.success("Admin Modifications Saved Successfully!")
                        st.rerun()

                with col_dl:
                    csv_export = convert_df_to_csv(edited_admin_data)
                    st.download_button(
                        label="📄 Download Selected Data Report (CSV)",
                        data=csv_export,
                        file_name=f"Warehouse_Report_{from_d}_to_{to_d}.csv",
                        mime="text/csv"
                    )

        # TAB 2: MASTER TABLES
        with tab_master:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown("#### 👤 Employee Master")
                emp_df = st.session_state["employees"]
                
                edited_emp = st.data_editor(emp_df, key="emp_editor", num_rows="dynamic", use_container_width=True)
                if st.button("💾 Save Employee Changes"):
                    save_employees(edited_emp)
                    st.session_state["employees"] = edited_emp
                    st.success("Employee List Saved!")
                    st.rerun()
            
            with col_m2:
                st.markdown("#### 🚚 Courier & Gadi (Vehicle) Master")
                couriers_df = st.session_state["couriers_df"]
                
                edited_cour = st.data_editor(couriers_df, key="cour_editor", num_rows="dynamic", use_container_width=True)
                if st.button("💾 Save Courier & Gadi Changes"):
                    save_couriers(edited_cour)
                    st.session_state["couriers_df"] = edited_cour
                    st.success("Courier & Vehicle Master Saved!")
                    st.rerun()

        # TAB 3: DATA RESET
        with tab_reset:
            st.markdown("#### ⚠️ Permanent System Reset")
            warn_confirm = st.checkbox("YES, I want to delete data.")
            
            if st.button("🔥 CLEAR ALL SYSTEM DATA PERMANENTLY"):
                if warn_confirm:
                    empty_df = pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee ID", "Employee Name", "Task Type", "Courier", "Parcel Count"])
                    empty_rep = pd.DataFrame(columns=["Date", "Courier", "Vehicle No", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"])
                    
                    st.session_state["data"] = empty_df
                    st.session_state["dispatch_reports"] = empty_rep
                    
                    save_data(empty_df)
                    save_reports(empty_rep)
                    
                    st.success("System Reset Completed! All records cleared.")
                    st.rerun()
                else:
                    st.warning("Please tick the confirmation checkbox first.")
