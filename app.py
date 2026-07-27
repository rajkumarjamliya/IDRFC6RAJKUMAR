import pandas as pd
import streamlit as st
from datetime import date, timedelta
import urllib.parse

# Page Configuration & Professional Theme
st.set_page_config(page_title="DELHIVERY – IDRFC6 Warehouse Tracker", layout="wide")

st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #002b36);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 26px;
    }
    .main-header p {
        margin: 5px 0 0 0;
        font-size: 16px;
        color: #d3d3d3;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
    <div class="main-header">
        <h1>📦 DELHIVERY – IDRFC6 Warehouse Operations Tracker</h1>
        <p>Station: IDRFC6 | Managed by: RAJKUMAR</p>
    </div>
""", unsafe_allow_html=True)

# ----------------- SESSION STATES -----------------
if "admin_password" not in st.session_state:
    st.session_state["admin_password"] = "122436"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=[
        "ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Parcel Count", "Status", "Mistake / Error"
    ])

if "dispatch_reports" not in st.session_state:
    # Stores daily summary for Courier Report Table: Date, Courier, Manifest, Cancel, Dispatch, Pending, Remark
    st.session_state["dispatch_reports"] = pd.DataFrame(columns=[
        "Date", "Courier", "Manifest", "Cancel", "Dispatch", "Remark"
    ])

if "trash" not in st.session_state:
    st.session_state["trash"] = pd.DataFrame(columns=[
        "ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Parcel Count", "Status", "Mistake / Error"
    ])

if "employees" not in st.session_state:
    st.session_state["employees"] = {
        "Kapil": "EMP001",
        "Sanjiv": "EMP002",
        "Bmpatel": "EMP003",
        "Rajkumar": "EMP004"
    }

if "couriers" not in st.session_state:
    st.session_state["couriers"] = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "DTDC", "Bluedart", "Ekart"]

# ----------------- SIDEBAR: LOGIN & ADMIN CONTROLS -----------------
st.sidebar.header("🔐 Admin Panel & Security")

if not st.session_state["authenticated"]:
    password_input = st.sidebar.text_input("Enter Admin Password", type="password")
    if st.sidebar.button("Login"):
        if password_input == st.session_state["admin_password"]:
            st.session_state["authenticated"] = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.sidebar.error("Incorrect Password")
else:
    st.sidebar.success("Logged in as Admin 🟢")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 Change Password")
    old_p = st.sidebar.text_input("Current Password", type="password")
    new_p = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Update Password"):
        if old_p == st.session_state["admin_password"]:
            if new_p:
                st.session_state["admin_password"] = new_p
                st.sidebar.success("Password updated successfully!")
            else:
                st.sidebar.error("New password cannot be empty.")
        else:
            st.sidebar.error("Current password is incorrect.")

# Date Selection for Working View
selected_date = st.sidebar.date_input("Select Working Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

# Admin Master Management (Add/Delete Employee & Courier)
if st.session_state["authenticated"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Master Management")
    
    new_emp_name = st.sidebar.text_input("New Employee Name")
    new_emp_id = st.sidebar.text_input("New Employee ID")
    if st.sidebar.button("Add Employee"):
        if new_emp_name and new_emp_id:
            st.session_state["employees"][new_emp_name] = new_emp_id
            st.sidebar.success(f"Employee {new_emp_name} added!")
            
    del_emp = st.sidebar.selectbox("Delete Employee", ["Select"] + list(st.session_state["employees"].keys()))
    if st.sidebar.button("Remove Employee") and del_emp != "Select":
        del st.session_state["employees"][del_emp]
        st.sidebar.success(f"Employee {del_emp} removed!")
        
    st.sidebar.markdown("---")
    new_courier = st.sidebar.text_input("New Courier Name")
    if st.sidebar.button("Add Courier"):
        if new_courier and new_courier not in st.session_state["couriers"]:
            st.session_state["couriers"].append(new_courier)
            st.sidebar.success(f"Courier {new_courier} added!")
            
    del_courier = st.sidebar.selectbox("Delete Courier", ["Select"] + st.session_state["couriers"])
    if st.sidebar.button("Remove Courier") and del_courier != "Select":
        st.session_state["couriers"].remove(del_courier)
        st.sidebar.success(f"Courier {del_courier} removed!")

# ----------------- MAIN LAYOUT: FORM & DASHBOARD -----------------
col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown(f"### 📝 Entry Form ({selected_date_str})")
    
    with st.form("entry_form", clear_on_submit=True):
        piklist_no = st.text_input("Piklist No.")
        
        emp_names_list = ["Select Employee"] + list(st.session_state["employees"].keys())
        emp_name = st.selectbox("Employee Name", emp_names_list)
        
        auto_emp_id = st.session_state["employees"].get(emp_name, "") if emp_name != "Select Employee" else ""
        emp_id = st.text_input("Employee ID (Auto-filled)", value=auto_emp_id, disabled=True)
        
        task_type = st.selectbox("Task Type", ["Manifest", "Picking", "Scanning", "Packing", "Loading", "Free"])
        courier = st.selectbox("Courier", st.session_state["couriers"])
        parcel_count = st.number_input("Parcel Count (Quantity)", min_value=1, step=1, value=1)
        status = st.selectbox("Status", ["Completed", "Pending", "In Progress", "Error"])
        mistake = st.selectbox("Mistake / Error", ["None", "Wrong Item", "Missing Item", "Tag Damage", "Wrong Scanning"])
        
        submit = st.form_submit_button("Submit Entry")
        
        if submit:
            if piklist_no and emp_name != "Select Employee":
                entry_id = str(pd.Timestamp.now().timestamp())
                new_row = pd.DataFrame({
                    "ID": [entry_id],
                    "Date": [selected_date_str],
                    "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Piklist No.": [piklist_no],
                    "Employee Name": [emp_name],
                    "Employee ID": [auto_emp_id],
                    "Task Type": [task_type],
                    "Courier": [courier],
                    "Parcel Count": [int(parcel_count)],
                    "Status": [status],
                    "Mistake / Error": [mistake]
                })
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                
                # Automatically update or insert into Dispatch Report (Manifest counting from task)
                if task_type == "Manifest":
                    rep_df = st.session_state["dispatch_reports"]
                    existing_row = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == courier)]
                    if not existing_row.empty:
                        idx = existing_row.index[0]
                        st.session_state["dispatch_reports"].loc[idx, "Manifest"] += int(parcel_count)
                    else:
                        new_rep = pd.DataFrame({
                            "Date": [selected_date_str],
                            "Courier": [courier],
                            "Manifest": [int(parcel_count)],
                            "Cancel": [0],
                            "Dispatch": [0],
                            "Remark": [""]
                        })
                        st.session_state["dispatch_reports"] = pd.concat([st.session_state["dispatch_reports"], new_rep], ignore_index=True)
                        
                st.success("Entry Saved Successfully!")
            else:
                st.error("Please fill Piklist No. and select Employee Name.")

with col2:
    st.markdown(f"### 📊 Live Dashboard & Reports ({selected_date_str})")
    
    df = st.session_state["data"]
    
    if not df.empty:
        df_filtered = df[df["Date"] == selected_date_str]
        
        if not df_filtered.empty:
            total_parcels = df_filtered["Parcel Count"].sum()
            st.metric(label="📦 Total Parcels Logged on Selected Date", value=total_parcels)
            
            # ----------------- COURIER DISPATCH REPORT TABLE (IMAGE FORMAT) -----------------
            st.markdown(f"#### 📋 Courier Dispatch Report — {selected_date_str}")
            
            # Calculate Yesterday's Pending for each courier
            all_couriers = st.session_state["couriers"]
            rep_data = st.session_state["dispatch_reports"]
            
            # Get yesterday pending map
            yesterday_pending_map = {}
            if not rep_data.empty:
                yest_df = rep_data[rep_data["Date"] == yesterday_str]
                for c in all_couriers:
                    # Calculate yesterday's pending = Manifest + Yesterday Pending - Cancel - Dispatch
                    c_row = yest_df[yest_df["Courier"] == c]
                    if not c_row.empty:
                        man = c_row["Manifest"].values[0]
                        can = c_row["Cancel"].values[0]
                        dis = c_row["Dispatch"].values[0]
                        # check if there was older pending too
                        yesterday_pending_map[c] = max(0, man - can - dis)
                    else:
                        yesterday_pending_map[c] = 0
            else:
                for c in all_couriers:
                    yesterday_pending_map[c] = 0

            # Build current date report presentation table
            current_rep = rep_data[rep_data["Date"] == selected_date_str] if not rep_data.empty else pd.DataFrame()
            
            display_rows = []
            for c in all_couriers:
                c_data = current_rep[current_rep["Courier"] == c] if not current_rep.empty else pd.DataFrame()
                man = int(c_data["Manifest"].values[0]) if not c_data.empty else 0
                can = int(c_data["Cancel"].values[0]) if not c_data.empty else 0
                dis = int(c_data["Dispatch"].values[0]) if not c_data.empty else 0
                rem = str(c_data["Remark"].values[0]) if not c_data.empty and pd.notna(c_data["Remark"].values[0]) else ""
                yest_pend = yesterday_pending_map.get(c, 0)
                
                # Pending = (Manifest + Yesterday Pending) - Cancel - Dispatch
                pending = max(0, (man + yest_pend) - can - dis)
                
                display_rows.append({
                    "Mosaic": c,
                    "Yesterday Pending": yest_pend,
                    "Manifest": man,
                    "Cancel": can,
                    "Dispatch": dis,
                    "Pending": pending,
                    "Remark": rem
                })
                
            report_table_df = pd.DataFrame(display_rows)
            
            # Add Total Row
            tot_yest = report_table_df["Yesterday Pending"].sum()
            tot_man = report_table_df["Manifest"].sum()
            tot_can = report_table_df["Cancel"].sum()
            tot_dis = report_table_df["Dispatch"].sum()
            tot_pend = report_table_df["Pending"].sum()
            
            total_summary_row = pd.DataFrame({
                "Mosaic": ["Total"],
                "Yesterday Pending": [tot_yest],
                "Manifest": [tot_man],
                "Cancel": [tot_can],
                "Dispatch": [tot_dis],
                "Pending": [tot_pend],
                "Remark": [""]
            })
            report_table_df = pd.concat([report_table_df, total_summary_row], ignore_index=True)
            
            st.dataframe(report_table_df, use_container_width=True)
            
            # Manual Update Form for Dispatch, Cancel, & Remarks
            with st.form("update_dispatch_form"):
                st.markdown("##### ✍️ Update Dispatch / Cancel / Remarks")
                up_courier = st.selectbox("Select Courier to Update", st.session_state["couriers"])
                up_cancel = st.number_input("Cancel Count", min_value=0, step=1, value=0)
                up_dispatch = st.number_input("Dispatch Count (Manual)", min_value=0, step=1, value=0)
                up_remark = st.text_input("Remark")
                
                if st.form_submit_button("Save Report Update"):
                    rep_df = st.session_state["dispatch_reports"]
                    existing_row = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == up_courier)]
                    if not existing_row.empty:
                        idx = existing_row.index[0]
                        st.session_state["dispatch_reports"].loc[idx, "Cancel"] = int(up_cancel)
                        st.session_state["dispatch_reports"].loc[idx, "Dispatch"] = int(up_dispatch)
                        st.session_state["dispatch_reports"].loc[idx, "Remark"] = up_remark
                    else:
                        new_rep = pd.DataFrame({
                            "Date": [selected_date_str],
                            "Courier": [up_courier],
                            "Manifest": [0],
                            "Cancel": [int(up_cancel)],
                            "Dispatch": [int(up_dispatch)],
                            "Remark": [up_remark]
                        })
                        st.session_state["dispatch_reports"] = pd.concat([st.session_state["dispatch_reports"], new_rep], ignore_index=True)
                    st.success("Dispatch report updated successfully!")
                    st.rerun()

            # Export, Print & WhatsApp Sharing Options
            st.markdown("#### 📥 Export, Print & Share Options")
            col_csv, col_print, col_wa = st.columns(3)
            
            with col_csv:
                csv_data = report_table_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Excel / CSV",
                    data=csv_data,
                    file_name=f"Dispatch_Report_{selected_date_str}.csv",
                    mime="text/csv",
                )
                
            with col_print:
                if st.button("🖨️ Print Report View"):
                    st.toast("Press Ctrl + P in your browser to print cleanly.")
                    
            with col_wa:
                wa_text = f"*📦 DELHIVERY - IDRFC6 Dispatch Report* \n*Date:* {selected_date_str}\n\n"
                for _, r in report_table_df.iterrows():
                    wa_text += f"_{r['Mosaic']}_ -> Man:{r['Manifest']} | Dis:{r['Dispatch']} | Pend:{r['Pending']}\n"
                encoded_wa = urllib.parse.quote(wa_text)
                st.markdown(f'<a href="https://wa.me/?text={encoded_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; font-weight:bold;">💬 Share on WhatsApp</button></a>', unsafe_allow_html=True)

            # Detailed Logs with Safe Editing Option
            st.markdown("#### 📋 Detailed Records & Quick Edit (Selected Date)")
            edit_entry_id = st.selectbox("Select Entry ID to Edit Status/Count", ["Select"] + list(df_filtered["ID"].astype(str)))
            if edit_entry_id != "Select":
                row_idx = df[df["ID"] == edit_entry_id].index[0]
                with st.form("edit_form"):
                    st.write(f"Editing Entry: Piklist **{df.loc[row_idx, 'Piklist No.']}** | Employee **{df.loc[row_idx, 'Employee Name']}**")
                    new_count = st.number_input("Update Parcel Count", value=int(df.loc[row_idx, 'Parcel Count']))
                    new_status = st.selectbox("Update Status", ["Completed", "Pending", "In Progress", "Error"], index=["Completed", "Pending", "In Progress", "Error"].index(df.loc[row_idx, 'Status']))
                    
                    if st.form_submit_button("Save Changes"):
                        st.session_state["data"].loc[row_idx, 'Parcel Count'] = new_count
                        st.session_state["data"].loc[row_idx, 'Status'] = new_status
                        st.success("Entry Updated Successfully!")
                        st.rerun()

            st.dataframe(df_filtered.drop(columns=["ID"]), use_container_width=True)
        else:
            st.info(f"No entries found for {selected_date_str}.")
    else:
        st.info("No entries yet. Add entries using the form.")

# ----------------- ADMIN PANEL: HISTORY & RECYCLE BIN -----------------
if st.session_state["authenticated"]:
    st.markdown("---")
    st.subheader("⚙️ Admin Control Panel & Recycle Bin")
    
    admin_tab1, admin_tab2 = st.tabs(["📅 Date-to-Date Master Log", "🗑️ Recycle Bin (Restore Deleted)"])
    
    with admin_tab1:
        st.markdown("#### Complete History Across All Dates")
        if not df.empty:
            st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
            
            del_id = st.selectbox("Select Entry ID to Delete to Recycle Bin", ["Select"] + list(df["ID"].astype(str)), key="admin_del")
            if del_id != "Select":
                if st.button("Move Selected Entry to Recycle Bin"):
                    row_to_trash = df[df["ID"] == del_id]
                    st.session_state["trash"] = pd.concat([st.session_state["trash"], row_to_trash], ignore_index=True)
                    st.session_state["data"] = df[df["ID"] != del_id]
                    st.success("Entry moved to Recycle Bin safely!")
                    st.rerun()
        else:
            st.info("No history available.")
            
    with admin_tab2:
        st.markdown("#### Deleted Entries (Recycle Bin)")
        trash_df = st.session_state["trash"]
        if not trash_df.empty:
            st.dataframe(trash_df.drop(columns=["ID"]), use_container_width=True)
            
            restore_id = st.selectbox("Select Entry ID to Restore", ["Select"] + list(trash_df["ID"].astype(str)), key="restore_sel")
            if restore_id != "Select":
                if st.button("Restore Entry"):
                    row_to_restore = trash_df[trash_df["ID"] == restore_id]
                    st.session_state["data"] = pd.concat([st.session_state["data"], row_to_restore], ignore_index=True)
                    st.session_state["trash"] = trash_df[trash_df["ID"] != restore_id]
                    st.success("Entry restored successfully!")
                    st.rerun()
        else:
            st.info("Recycle Bin is empty.")
