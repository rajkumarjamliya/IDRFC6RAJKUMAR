import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import os
import io

# Page Config
st.set_page_config(page_title="DELHIVERY – IDRFC6 3D Tracker", layout="wide")

# Custom 3D & Modern Glassmorphism CSS Styling
st.markdown("""
    <style>
    /* Main Background & Font */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 3D Header Banner */
    .main-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 25px;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        border-bottom: 4px solid #00d2ff;
        margin-bottom: 25px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 1px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    .main-header p {
        margin: 8px 0 0 0;
        font-size: 15px;
        color: #00d2ff;
        font-weight: 500;
    }

    /* 3D Container Cards */
    .card-3d {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1), inset 0 1px 2px rgba(255,255,255,0.8);
        border: 1px solid rgba(255,255,255,0.5);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card-3d:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }

    /* Custom Metric 3D Box */
    .metric-box {
        background: linear-gradient(135deg, #1fa2ff 0%, #12d8fa 50%, #a6ffcb 100%);
        padding: 15px;
        border-radius: 12px;
        color: #0f2027;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 6px 15px rgba(31, 162, 255, 0.3);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Banner
st.markdown("""
    <div class="main-header">
        <h1>📦 DELHIVERY – IDRFC6 3D Warehouse Tracker</h1>
        <p>Station: IDRFC6 &nbsp;|&nbsp; Managed by: RAJKUMAR &nbsp;|&nbsp; Advanced 3D Management Hub</p>
    </div>
""", unsafe_allow_html=True)

# Files
DATA_FILE = "warehouse_entries.csv"
REPORT_FILE = "dispatch_reports.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Parcel Count", "Status", "Mistake / Error"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_reports():
    if os.path.exists(REPORT_FILE):
        return pd.read_csv(REPORT_FILE)
    return pd.DataFrame(columns=["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Remark"])

def save_reports(df):
    df.to_csv(REPORT_FILE, index=False)

# Session States
if "admin_password" not in st.session_state:
    st.session_state["admin_password"] = "122436"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "data" not in st.session_state:
    st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state:
    st.session_state["dispatch_reports"] = load_reports()
if "trash" not in st.session_state:
    st.session_state["trash"] = pd.DataFrame(columns=st.session_state["data"].columns)

# Employees List
employees = {
    "AJAY PATEL": "W222449", "PANKAJ PATEL": "W224500", "KAMLESH MANDOI": "W225396",
    "ABHISHEK PATEL": "W225403", "SHRI RAM": "W225410", "KUNAL PATIL": "W225413",
    "RAJSARGARA": "W225415", "ANISH PATEL": "226351", "ANKIT MANDLOI": "W226654",
    "SANDEEP PATEL": "W228473", "ABHISHEK PATEL (2)": "230777", "RAJKUMAR JAMLIYA": "W224483",
    "CHANDAN": "W228474", "SHAILESH TIWARI": "SSN079654", "SUJATA KUSHWAHA": "W231056",
    "SANDHYA KARANJA": "W231195", "HARSHITA SOLANKI": "W231196", "BHAVNA MALVIYA": "W231057",
    "REKHA": "W231152", "KAVITA": "W231689"
}
couriers_list = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "DTDC", "Bluedart", "Ekart"]

# Sidebar Control Center
st.sidebar.markdown("### ⚙️ 3D Control Center")
selected_date = st.sidebar.date_input("Working Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

st.sidebar.markdown("---")
nav_page = st.sidebar.radio("Navigation Menu", ["🏠 Home Entry Portal", "📊 3D Analytics & Reports", "🔒 Admin Security Panel"])

st.sidebar.markdown("---")
if not st.session_state["authenticated"]:
    pwd = st.sidebar.text_input("Admin Password", type="password")
    if st.sidebar.button("Login"):
        if pwd == st.session_state["admin_password"]:
            st.session_state["authenticated"] = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.sidebar.error("Wrong Password")
else:
    st.sidebar.success("Admin Logged In 🟢")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

# ================= PAGE 1: HOME ENTRY PORTAL =================
if nav_page == "🏠 Home Entry Portal":
    col1, col2 = st.columns([1, 1.3], gap="medium")
    
    with col1:
        st.markdown(f"""
            <div class="card-3d">
                <h3>📝 New Warehouse Entry</h3>
                <p style="color: gray; font-size: 13px;">Date: {selected_date_str}</p>
            </div>
        """, unsafe_allow_html=True)
        
        piklist_no = st.text_input("Piklist No.")
        emp_name = st.selectbox("Employee Name", ["Select"] + list(employees.keys()))
        
        auto_id = employees.get(emp_name, "") if emp_name != "Select" else ""
        if emp_name != "Select":
            st.markdown(f"<span style='color: #007bff; font-weight: bold;'>🆔 Employee ID: {auto_id}</span>", unsafe_allow_html=True)
            
        task_type = st.selectbox("Task Type", ["Manifest", "Picking", "Packing", "Scanning", "Loading", "Free"])
        
        courier = "N/A"
        parcel_count = 1
        if task_type == "Manifest":
            courier = st.selectbox("Courier", couriers_list)
            parcel_count = st.number_input("Box Count", min_value=1, value=1)
        else:
            parcel_count = st.number_input("Item Count", min_value=1, value=1)
            
        status = st.selectbox("Status", ["Completed", "Pending", "In Progress", "Error"])
        mistake = st.selectbox("Mistake", ["None", "Wrong Item", "Missing Item", "Tag Damage", "Wrong Scanning"])
        
        if st.button("💾 Submit Entry Now", use_container_width=True):
            if piklist_no and emp_name != "Select":
                new_id = str(pd.Timestamp.now().timestamp())
                current_time_str = datetime.now().strftime("%I:%M %p")
                
                new_row = pd.DataFrame({
                    "ID": [new_id], "Date": [selected_date_str],
                    "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Piklist No.": [str(piklist_no)], "Employee Name": [emp_name],
                    "Employee ID": [auto_id], "Task Type": [task_type],
                    "Courier": [courier], "Parcel Count": [int(parcel_count)],
                    "Status": [status], "Mistake / Error": [mistake]
                })
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                save_data(st.session_state["data"])
                
                if task_type == "Manifest" and courier != "N/A":
                    rep_df = st.session_state["dispatch_reports"]
                    ex = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == courier)]
                    if not ex.empty:
                        idx = ex.index[0]
                        rep_df.loc[idx, "Manifest"] += int(parcel_count)
                    else:
                        new_rep = pd.DataFrame({
                            "Date": [selected_date_str], "Courier": [courier], 
                            "In Time": [current_time_str], "Out Time": ["--:--"], 
                            "Manifest": [int(parcel_count)], "Cancel": [0], "Dispatch": [0], "Remark": [""]
                        })
                        st.session_state["dispatch_reports"] = pd.concat([rep_df, new_rep], ignore_index=True)
                    save_reports(st.session_state["dispatch_reports"])
                    
                st.success("Entry Saved Successfully!")
                st.rerun()
            else:
                st.error("Piklist No. aur Employee Name zaroor bharein!")

    with col2:
        st.markdown(f"""
            <div class="card-3d">
                <h3>📊 Live Activity Dashboard</h3>
                <p style="color: gray; font-size: 13px;">Today's Live Records ({selected_date_str})</p>
            </div>
        """, unsafe_allow_html=True)
        
        df = st.session_state["data"]
        df_f = df[df["Date"] == selected_date_str].copy() if not df.empty else pd.DataFrame()
        
        if not df_f.empty:
            st.dataframe(df_f[["Piklist No.", "Employee Name", "Courier", "Parcel Count", "Task Type", "Timestamp"]], use_container_width=True)
            
            # Quick Edit Form inside Card
            with st.form("quick_edit"):
                st.markdown("##### ✏️ Quick Edit Record")
                ids = list(df_f["ID"].astype(str))
                sel_id = st.selectbox("Select Record ID", ids, format_func=lambda x: f"Piklist: {df_f[df_f['ID'].astype(str) == x]['Piklist No.'].values[0]} | {df_f[df_f['ID'].astype(str) == x]['Employee Name'].values[0]}")
                r_dat = df_f[df_f["ID"].astype(str) == sel_id].iloc[0]
                
                up_pik = st.text_input("New Piklist No.", value=str(r_dat["Piklist No."]))
                old_courier_val = r_dat["Courier"]
                up_cou = st.selectbox("New Courier", couriers_list, index=couriers_list.index(old_courier_val) if old_courier_val in couriers_list else 0)
                old_cnt_val = int(r_dat["Parcel Count"])
                up_cnt = st.number_input("New Count", min_value=1, value=old_cnt_val)
                
                if st.form_submit_button("Update Record"):
                    m_i = st.session_state["data"][st.session_state["data"]["ID"].astype(str) == sel_id].index[0]
                    task_t = st.session_state["data"].loc[m_i, "Task Type"]
                    
                    if task_t == "Manifest":
                        rep_df = st.session_state["dispatch_reports"]
                        if old_courier_val != "N/A":
                            ex_old = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == old_courier_val)]
                            if not ex_old.empty:
                                idx_o = ex_old.index[0]
                                rep_df.loc[idx_o, "Manifest"] = max(0, int(rep_df.loc[idx_o, "Manifest"]) - old_cnt_val)
                        
                        if up_cou != "N/A":
                            ex_new = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == up_cou)]
                            if not ex_new.empty:
                                idx_n = ex_new.index[0]
                                rep_df.loc[idx_n, "Manifest"] = int(rep_df.loc[idx_n, "Manifest"]) + up_cnt
                            else:
                                new_rep = pd.DataFrame({
                                    "Date": [selected_date_str], "Courier": [up_cou], 
                                    "In Time": [datetime.now().strftime("%I:%M %p")], "Out Time": ["--:--"], 
                                    "Manifest": [up_cnt], "Cancel": [0], "Dispatch": [0], "Remark": [""]
                                })
                                st.session_state["dispatch_reports"] = pd.concat([rep_df, new_rep], ignore_index=True)
                        save_reports(st.session_state["dispatch_reports"])

                    st.session_state["data"].loc[m_i, "Piklist No."] = str(up_pik)
                    st.session_state["data"].loc[m_i, "Courier"] = up_cou
                    st.session_state["data"].loc[m_i, "Parcel Count"] = int(up_cnt)
                    save_data(st.session_state["data"])
                    st.success("Updated successfully!")
                    st.rerun()
        else:
            st.info("Aaj ke din koi entry abhi tak darj nahi ki gayi hai.")

# ================= PAGE 2: ANALYTICS & REPORTS =================
elif nav_page == "📊 3D Analytics & Reports":
    st.markdown(f"""
        <div class="card-3d">
            <h3>🚚 Courier In/Out, Dispatch & Pending Report</h3>
            <p style="color: gray;">Real-time tracking of manifest, dispatch, cancel, and pending packages.</p>
        </div>
    """, unsafe_allow_html=True)
    
    rep_df = st.session_state["dispatch_reports"]
    
    with st.form("courier_dispatch_form"):
        st.markdown("##### ⏱️ Update Courier In/Out & Dispatch/Cancel Boxes")
        sel_c_rep = st.selectbox("Select Courier", couriers_list)
        
        curr_row_check = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == sel_c_rep)]
        default_in = curr_row_check["In Time"].values[0] if not curr_row_check.empty and pd.notna(curr_row_check["In Time"].values[0]) else datetime.now().strftime("%I:%M %p")
        default_out = curr_row_check["Out Time"].values[0] if not curr_row_check.empty and pd.notna(curr_row_check["Out Time"].values[0]) else "--:--"
        default_disp = int(curr_row_check["Dispatch"].values[0]) if not curr_row_check.empty else 0
        default_canc = int(curr_row_check["Cancel"].values[0]) if not curr_row_check.empty else 0
        default_rem = str(curr_row_check["Remark"].values[0]) if not curr_row_check.empty and pd.notna(curr_row_check["Remark"].values[0]) else ""

        col_a, col_b = st.columns(2)
        with col_a:
            c_in_time = st.text_input("In Time", value=default_in)
            c_dispatch = st.number_input("Dispatch Boxes", min_value=0, value=default_disp)
        with col_b:
            c_cancel = st.number_input("Cancel Boxes", min_value=0, value=default_canc)
            c_remark = st.text_input("Remark", value=default_rem)
        
        calc_out_time = default_out
        if c_dispatch > 0 and c_in_time and c_in_time != "--:--":
            try:
                parsed_in = datetime.strptime(c_in_time.strip(), "%I:%M %p")
                calc_out_time = (parsed_in + timedelta(minutes=5)).strftime("%I:%M %p")
            except:
                calc_out_time = (datetime.now() + timedelta(minutes=5)).strftime("%I:%M %p")
        
        c_out_time = st.text_input("Out Time (Auto +5 mins after Dispatch)", value=calc_out_time)
        
        if st.form_submit_button("Save Courier Timing & Dispatch"):
            ex_r = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == sel_c_rep)]
            if not ex_r.empty:
                idx = ex_r.index[0]
                rep_df.loc[idx, "In Time"] = c_in_time
                rep_df.loc[idx, "Out Time"] = c_out_time
                rep_df.loc[idx, "Dispatch"] = c_dispatch
                rep_df.loc[idx, "Cancel"] = c_cancel
                rep_df.loc[idx, "Remark"] = c_remark
            else:
                new_row_rep = pd.DataFrame({
                    "Date": [selected_date_str], "Courier": [sel_c_rep],
                    "In Time": [c_in_time], "Out Time": [c_out_time],
                    "Manifest": [0], "Cancel": [c_cancel], "Dispatch": [c_dispatch], "Remark": [c_remark]
                })
                st.session_state["dispatch_reports"] = pd.concat([rep_df, new_row_rep], ignore_index=True)
            save_reports(st.session_state["dispatch_reports"])
            st.success("Updated successfully!")
            st.rerun()

    cur_rep_view = st.session_state["dispatch_reports"]
    current_day_rep = cur_rep_view[cur_rep_view["Date"] == selected_date_str] if not cur_rep_view.empty else pd.DataFrame()
    
    yest_pend_map = {}
    yest_rep_view = cur_rep_view[cur_rep_view["Date"] == yesterday_str] if not cur_rep_view.empty else pd.DataFrame()
    for c in couriers_list:
        c_yest = yest_rep_view[yest_rep_view["Courier"] == c]
        if not c_yest.empty:
            man_y = c_yest["Manifest"].values[0]
            can_y = c_yest["Cancel"].values[0]
            dis_y = c_yest["Dispatch"].values[0]
            yest_pend_map[c] = max(0, man_y - can_y - dis_y)
        else:
            yest_pend_map[c] = 0

    display_summary_rows = []
    for c in couriers_list:
        c_curr = current_day_rep[current_day_rep["Courier"] == c] if not current_day_rep.empty else pd.DataFrame()
        in_t = c_curr["In Time"].values[0] if not c_curr.empty and pd.notna(c_curr["In Time"].values[0]) else "--:--"
        out_t = c_curr["Out Time"].values[0] if not c_curr.empty and pd.notna(c_curr["Out Time"].values[0]) else "--:--"
        man = int(c_curr["Manifest"].values[0]) if not c_curr.empty else 0
        can = int(c_curr["Cancel"].values[0]) if not c_curr.empty else 0
        dis = int(c_curr["Dispatch"].values[0]) if not c_curr.empty else 0
        rem = str(c_curr["Remark"].values[0]) if not c_curr.empty and pd.notna(c_curr["Remark"].values[0]) else ""
        y_pend = yest_pend_map.get(c, 0)
        
        final_pend = max(0, (man + y_pend) - can - dis)
        
        display_summary_rows.append({
            "Courier": c,
            "Yesterday Pending": y_pend,
            "In Time": in_t,
            "Out Time": out_t,
            "Manifest": man,
            "Cancel": can,
            "Dispatch": dis,
            "Pending": final_pend,
            "Remark": rem
        })
        
    summary_table_df = pd.DataFrame(display_summary_rows)
    st.markdown("#### 📋 Final Status Summary Table")
    st.dataframe(summary_table_df, use_container_width=True)

# ================= PAGE 3: ADMIN SECURITY PANEL =================
elif nav_page == "🔒 Admin Security Panel":
    if st.session_state["authenticated"]:
        st.markdown("""
            <div class="card-3d">
                <h3>🔒 Admin Security & Management Hub</h3>
                <p style="color: gray;">Download Excel reports, edit past dispatch entries, and manage trash records securely.</p>
            </div>
        """, unsafe_allow_html=True)
        
        adm_t1, adm_t2, adm_t3, adm_t4 = st.tabs([
            "📥 Date-to-Date Excel Report", 
            "✏️ Edit Final Dispatch Report", 
            "🗑️ Date-wise Delete", 
            "♻️ Recycle Bin"
        ])
        
        with adm_t1:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_d = st.date_input("Start Date", date.today(), key="exc_start")
            with col_d2:
                end_d = st.date_input("End Date", date.today(), key="exc_end")
                
            start_str = str(start_d)
            end_str = str(end_d)
            
            all_entries = st.session_state["data"]
            if not all_entries.empty:
                filtered_excel_df = all_entries[(all_entries["Date"] >= start_str) & (all_entries["Date"] <= end_str)]
                if not filtered_excel_df.empty:
                    st.write(f"Total Entries Found: **{len(filtered_excel_df)}**")
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        filtered_excel_df.to_excel(writer, sheet_name='Warehouse Data', index=False)
                    processed_data = output.getvalue()
                    
                    st.download_button(
                        label="📥 Download Excel Report (.xlsx)",
                        data=processed_data,
                        file_name=f"Warehouse_Report_{start_str}_to_{end_str}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                else:
                    st.info("Is date range me koi data available nahi hai.")
            else:
                st.info("No data recorded yet.")

        with adm_t2:
            edit_rep_date = st.date_input("Select Report Date", date.today(), key="edit_rep_dt")
            edit_rep_date_str = str(edit_rep_date)
            rep_current_df = st.session_state["dispatch_reports"]
            date_rep_filtered = rep_current_df[rep_current_df["Date"] == edit_rep_date_str] if not rep_current_df.empty else pd.DataFrame()
            
            if not date_rep_filtered.empty:
                st.dataframe(date_rep_filtered, use_container_width=True)
                with st.form("admin_edit_final_report_form"):
                    sel_edit_courier = st.selectbox("Select Courier to Edit", list(date_rep_filtered["Courier"].unique()))
                    row_to_edit = date_rep_filtered[date_rep_filtered["Courier"] == sel_edit_courier].iloc[0]
                    
                    e_in = st.text_input("Edit In Time", value=str(row_to_edit["In Time"]))
                    e_out = st.text_input("Edit Out Time", value=str(row_to_edit["Out Time"]))
                    e_man = st.number_input("Edit Manifest Boxes", min_value=0, value=int(row_to_edit["Manifest"]))
                    e_can = st.number_input("Edit Cancel Boxes", min_value=0, value=int(row_to_edit["Cancel"]))
                    e_dis = st.number_input("Edit Dispatch Boxes", min_value=0, value=int(row_to_edit["Dispatch"]))
                    e_rem = st.text_input("Edit Remark", value=str(row_to_edit["Remark"]) if pd.notna(row_to_edit["Remark"]) else "")
                    
                    if st.form_submit_button("Update Dispatch Report"):
                        idx_match = rep_current_df[(rep_current_df["Date"] == edit_rep_date_str) & (rep_current_df["Courier"] == sel_edit_courier)].index[0]
                        rep_current_df.loc[idx_match, "In Time"] = e_in
                        rep_current_df.loc[idx_match, "Out Time"] = e_out
                        rep_current_df.loc[idx_match, "Manifest"] = e_man
                        rep_current_df.loc[idx_match, "Cancel"] = e_can
                        rep_current_df.loc[idx_match, "Dispatch"] = e_dis
                        rep_current_df.loc[idx_match, "Remark"] = e_rem
                        
                        save_reports(rep_current_df)
                        st.success("Final Dispatch Report Updated Successfully!")
                        st.rerun()
            else:
                st.info(f"Date {edit_rep_date_str} ke liye koi report data nahi hai.")

        with adm_t3:
            del_date = st.date_input("Select Date to Delete Entry", date.today(), key="del_dt")
            del_date_str = str(del_date)
            all_d = st.session_state["data"]
            date_df = all_d[all_d["Date"] == del_date_str] if not all_d.empty else pd.DataFrame()
            
            if not date_df.empty:
                st.dataframe(date_df[["Piklist No.", "Employee Name", "Courier", "Parcel Count"]], use_container_width=True)
                del_sel = st.selectbox("Select Entry to Delete", ["Select"] + list(date_df["ID"].astype(str)), format_func=lambda x: "Select" if x=="Select" else f"Piklist: {date_df[date_df['ID'].astype(str) == x]['Piklist No.'].values[0]} | Emp: {date_df[date_df['ID'].astype(str) == x]['Employee Name'].values[0]}")
                
                if del_sel != "Select":
                    if st.button("Move to Trash"):
                        trash_row = all_d[all_d["ID"].astype(str) == del_sel]
                        st.session_state["trash"] = pd.concat([st.session_state["trash"], trash_row], ignore_index=True)
                        st.session_state["data"] = all_d[all_d["ID"].astype(str) != del_sel]
                        save_data(st.session_state["data"])
                        st.success("Deleted successfully!")
                        st.rerun()
            else:
                st.info("No data found for this date.")
                
        with adm_t4:
            trash_df = st.session_state["trash"]
            if not trash_df.empty:
                st.dataframe(trash_df[["Piklist No.", "Employee Name", "Courier"]], use_container_width=True)
                res_id = st.selectbox("Select to Restore", ["Select"] + list(trash_df["ID"].astype(str)), key="res_sel")
                if res_id != "Select":
                    if st.button("Restore"):
                        r_row = trash_df[trash_df["ID"].astype(str) == res_id]
                        st.session_state["data"] = pd.concat([st.session_state["data"], r_row], ignore_index=True)
                        st.session_state["trash"] = trash_df[trash_df["ID"].astype(str) != res_id]
                        save_data(st.session_state["data"])
                        st.success("Restored!")
                        st.rerun()
            else:
                st.info("Recycle Bin is empty.")
    else:
        st.warning("⚠️ Kripya sidebar me Admin Password (`122436`) daalkar login karein taaki Admin panel access kiya ja sake.")
