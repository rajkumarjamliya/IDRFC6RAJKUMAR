import pandas as pd
import streamlit as st
from datetime import date, timedelta
import urllib.parse
import os

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

# ----------------- PERMANENT DATA STORAGE FILES -----------------
DATA_FILE = "warehouse_entries.csv"
REPORT_FILE = "dispatch_reports.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Parcel Count", "Status", "Mistake / Error"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_reports():
    if os.path.exists(REPORT_FILE):
        return pd.read_csv(REPORT_FILE)
    else:
        return pd.DataFrame(columns=[
            "Date", "Courier", "Manifest", "Cancel", "Dispatch", "Remark"
        ])

def save_reports(df):
    df.to_csv(REPORT_FILE, index=False)

# ----------------- SESSION STATES -----------------
if "data" not in st.session_state:
    st.session_state["data"] = load_data()

if "dispatch_reports" not in st.session_state:
    st.session_state["dispatch_reports"] = load_reports()

if "trash" not in st.session_state:
    st.session_state["trash"] = pd.DataFrame(columns=st.session_state["data"].columns)

# Permanent Employee List
if "employees" not in st.session_state:
    st.session_state["employees"] = {
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

if "couriers" not in st.session_state:
    st.session_state["couriers"] = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "DTDC", "Bluedart", "Ekart"]

# ----------------- SIDEBAR: DATE & MASTER MANAGEMENT -----------------
st.sidebar.header("⚙️ Controls & Management")

# Date Selection for Working View
selected_date = st.sidebar.date_input("Select Working Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add New Employee / Courier")

new_emp_name = st.sidebar.text_input("Extra Employee Name", key="new_emp_name_input")
new_emp_id = st.sidebar.text_input("Extra Employee ID", key="new_emp_id_input")
if st.sidebar.button("Add Employee"):
    if new_emp_name and new_emp_id:
        st.session_state["employees"][new_emp_name] = new_emp_id
        st.sidebar.success(f"Employee {new_emp_name} added!")
        
st.sidebar.markdown("---")
new_courier = st.sidebar.text_input("New Courier Name", key="new_courier_input")
if st.sidebar.button("Add Courier"):
    if new_courier and new_courier not in st.session_state["couriers"]:
        st.session_state["couriers"].append(new_courier)
        st.sidebar.success(f"Courier {new_courier} added!")

# ----------------- MAIN LAYOUT: FORM & DASHBOARD -----------------
col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown(f"### 📝 Entry Form ({selected_date_str})")
    
    piklist_no = st.text_input("Piklist No. (Sankhiya)")
    
    emp_names_list = ["Select Employee"] + list(st.session_state["employees"].keys())
    emp_name = st.selectbox("Employee Name", emp_names_list)
    
    auto_emp_id = st.session_state["employees"].get(emp_name, "") if emp_name != "Select Employee" else ""
    if emp_name != "Select Employee":
        st.info(f"🆔 Employee ID: **{auto_emp_id}**")
    
    task_type = st.selectbox("Task Type", ["Picking", "Scanning", "Packing", "Manifest", "Loading", "Free"])
    
    courier = "N/A"
    parcel_count = 1
    if task_type == "Manifest":
        courier = st.selectbox("Courier", st.session_state["couriers"])
        parcel_count = st.number_input("Parcel Count (Quantity)", min_value=1, step=1, value=1, key="parcels_man")
    else:
        parcel_count = st.number_input("Parcel Count / Item Count", min_value=1, step=1, value=1, key="parcels_other")
        
    status = st.selectbox("Status", ["Completed", "Pending", "In Progress", "Error"])
    mistake = st.selectbox("Mistake / Error", ["None", "Wrong Item", "Missing Item", "Tag Damage", "Wrong Scanning"])
    
    submit = st.button("Submit Entry")
    
    if submit:
        if piklist_no and emp_name != "Select Employee":
            entry_id = str(pd.Timestamp.now().timestamp())
            new_row = pd.DataFrame({
                "ID": [entry_id],
                "Date": [selected_date_str],
                "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
                "Piklist No.": [str(piklist_no)],
                "Employee Name": [emp_name],
                "Employee ID": [auto_emp_id],
                "Task Type": [task_type],
                "Courier": [courier],
                "Parcel Count": [int(parcel_count)],
                "Status": [status],
                "Mistake / Error": [mistake]
            })
            st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
            save_data(st.session_state["data"])
            
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
                save_reports(st.session_state["dispatch_reports"])
                    
            st.success("Entry Saved Successfully!")
            st.rerun()
        else:
            st.error("Please fill Piklist No. and select Employee Name.")

with col2:
    st.markdown(f"### 📊 Live Dashboard & Reports ({selected_date_str})")
    
    df = st.session_state["data"]
    
    if not df.empty:
        df_filtered = df[df["Date"] == selected_date_str]
        
        if not df_filtered.empty:
            total_parcels = int(df_filtered["Parcel Count"].sum())
            st.metric(label="📦 Total Parcel Count on Selected Date", value=total_parcels)
            
            # ----------------- COURIER DISPATCH REPORT TABLE -----------------
            st.markdown(f"#### 📋 Courier Dispatch Report — {selected_date_str}")
            
            all_couriers = st.session_state["couriers"]
            rep_data = st.session_state["dispatch_reports"]
            
            yesterday_pending_map = {}
            if not rep_data.empty:
                yest_df = rep_data[rep_data["Date"] == yesterday_str]
                for c in all_couriers:
                    c_row = yest_df[yest_df["Courier"] == c]
                    if not c_row.empty:
                        man = c_row["Manifest"].values[0]
                        can = c_row["Cancel"].values[0]
                        dis = c_row["Dispatch"].values[0]
                        yesterday_pending_map[c] = max(0, man - can - dis)
                    else:
                        yesterday_pending_map[c] = 0
            else:
                for c in all_couriers:
                    yesterday_pending_map[c] = 0

            current_rep = rep_data[rep_data["Date"] == selected_date_str] if not rep_data.empty else pd.DataFrame()
            
            display_rows = []
            for c in all_couriers:
                c_data = current_rep[current_rep["Courier"] == c] if not current_rep.empty else pd.DataFrame()
                man = int(c_data["Manifest"].values[0]) if not c_data.empty else 0
                can = int(c_data["Cancel"].values[0]) if not c_data.empty else 0
                dis = int(c_data["Dispatch"].values[0]) if not c_data.empty else 0
                rem = str(c_data["Remark"].values[0]) if not c_data.empty and pd.notna(c_data["Remark"].values[0]) else ""
                yest_pend = yesterday_pending_map.get(c, 0)
                
                pending = max(0, (man + yest_pend) - can - dis)
                
                display_rows.append({
                    "Courier": c,
                    "Yesterday Pending": yest_pend,
                    "Manifest": man,
                    "Cancel": can,
                    "Dispatch": dis,
                    "Pending": pending,
                    "Remark": rem
                })
                
            report_table_df = pd.DataFrame(display_rows)
            
            tot_yest = report_table_df["Yesterday Pending"].sum()
            tot_man = report_table_df["Manifest"].sum()
            tot_can = report_table_df["Cancel"].sum()
            tot_dis = report_table_df["Dispatch"].sum()
            tot_pend = report_table_df["Pending"].sum()
            
            total_summary_row = pd.DataFrame({
                "Courier": ["Total"],
                "Yesterday Pending": [tot_yest],
                "Manifest": [tot_man],
                "Cancel": [tot_can],
                "Dispatch": [tot_dis],
                "Pending": [tot_pend],
                "Remark": [""]
            })
            report_table_df = pd.concat([report_table_df, total_summary_row], ignore_index=True)
            
            st.dataframe(report_table_df, use_container_width=True)
            
            # ----------------- EDIT COURIER COUNTING DIRECTLY -----------------
            with st.form("edit_courier_report_form"):
                st.markdown("##### ✏️ Edit Courier Counting / Report (No Lock)")
                edit_courier_sel = st.selectbox("Select Courier to Correct", st.session_state["couriers"])
                
                cur_man_val, cur_can_val, cur_dis_val, cur_rem_val = 0, 0, 0, ""
                if not rep_data.empty:
                    match_row = rep_data[(rep_data["Date"] == selected_date_str) & (rep_data["Courier"] == edit_courier_sel)]
                    if not match_row.empty:
                        cur_man_val = int(match_row["Manifest"].values[0])
                        cur_can_val = int(match_row["Cancel"].values[0])
                        cur_dis_val = int(match_row["Dispatch"].values[0])
                        cur_rem_val = str(match_row["Remark"].values[0]) if pd.notna(match_row["Remark"].values[0]) else ""
                
                new_man_input = st.number_input("Corrected Manifest (Courier Counting)", min_value=0, step=1, value=cur_man_val)
                new_can_input = st.number_input("Corrected Cancel Count", min_value=0, step=1, value=cur_can_val)
                new_dis_input = st.number_input("Corrected Dispatch Count", min_value=0, step=1, value=cur_dis_val)
                new_rem_input = st.text_input("Corrected Remark", value=cur_rem_val)
                
                if st.form_submit_button("Update Courier Report"):
                    rep_df = st.session_state["dispatch_reports"]
                    existing_row = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == edit_courier_sel)]
                    if not existing_row.empty:
                        idx = existing_row.index[0]
                        st.session_state["dispatch_reports"].loc[idx, "Manifest"] = int(new_man_input)
                        st.session_state["dispatch_reports"].loc[idx, "Cancel"] = int(new_can_input)
                        st.session_state["dispatch_reports"].loc[idx, "Dispatch"] = int(new_dis_input)
                        st.session_state["dispatch_reports"].loc[idx, "Remark"] = new_rem_input
                    else:
                        new_rep = pd.DataFrame({
                            "Date": [selected_date_str],
                            "Courier": [edit_courier_sel],
                            "Manifest": [int(new_man_input)],
                            "Cancel": [int(new_can_input)],
                            "Dispatch": [int(new_dis_input)],
                            "Remark": [new_rem_input]
                        })
                        st.session_state["dispatch_reports"] = pd.concat([st.session_state["dispatch_reports"], new_rep], ignore_index=True)
                    
                    save_reports(st.session_state["dispatch_reports"])
                    st.success(f"Courier {edit_courier_sel} updated successfully!")
                    st.rerun()

            # Export & WhatsApp Sharing Options
            st.markdown("#### 📥 Export & Share Options")
            col_csv, col_wa = st.columns(2)
            
            with col_csv:
                csv_data = report_table_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Excel / CSV",
                    data=csv_data,
                    file_name=f"Dispatch_Report_{selected_date_str}.csv",
                    mime="text/csv",
                )
                
            with col_wa:
                wa_text = f"*📦 DELHIVERY - IDRFC6 Dispatch Report* \n*Date:* {selected_date_str}\n\n"
                for _, r in report_table_df.iterrows():
                    wa_text += f"_{r['Courier']}_ -> Man:{r['Manifest']} | Dis:{r['Dispatch']} | Pend:{r['Pending']}\n"
                encoded_wa = urllib.parse.quote(wa_text)
                st.markdown(f'<a href="https://wa.me/?text={encoded_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; font-weight:bold;">💬 Share on WhatsApp</button></a>', unsafe_allow_html=True)

            # ----------------- DETAILED RECORDS & UNLOCKED EDIT/DELETE -----------------
            st.markdown("#### 📋 Detailed Records & Quick Corrections (Selected Date)")
            st.dataframe(df_filtered.drop(columns=["ID"]), use_container_width=True)
            
            st.markdown("---")
            st.markdown("### ⚙️ Unlocked Quick Edit, Delete & Recycle Bin")
            
            sub_tab1, sub_tab2 = st.tabs(["✏️ Edit / Delete Entry", "🗑️ Recycle Bin"])
            
            with sub_tab1:
                edit_id = st.selectbox("Select Entry to Edit/Delete (by Piklist & Time)", ["Select"] + list(df_filtered["ID"].astype(str)), key="direct_edit_sel")
                if edit_id != "Select":
                    row_data = df[df["ID"] == edit_id].iloc[0]
                    
                    with st.form("direct_edit_form"):
                        new_pik = st.text_input("Piklist No. (Sankhiya)", value=str(row_data["Piklist No."]))
                        
                        # Courier list for editing
                        current_courier_val = row_data["Courier"] if row_data["Courier"] in st.session_state["couriers"] else "Delhivery"
                        new_cour = st.selectbox("Courier Name", st.session_state["couriers"], index=st.session_state["couriers"].index(current_courier_val) if current_courier_val in st.session_state["couriers"] else 0)
                        
                        new_status = st.selectbox("Status", ["Completed", "Pending", "In Progress", "Error"], index=["Completed", "Pending", "In Progress", "Error"].index(row_data["Status"]) if row_data["Status"] in ["Completed", "Pending", "In Progress", "Error"] else 0)
                        
                        new_count = st.number_input("Parcel / Counting", min_value=1, step=1, value=int(row_data["Parcel Count"]))
                        
                        col_e1, col_e2 = st.columns(2)
                        update_btn = col_e1.form_submit_button("Save Changes")
                        delete_btn = col_e2.form_submit_button("Delete Entry")
                        
                        if update_btn:
                            idx = df[df["ID"] == edit_id].index[0]
                            st.session_state["data"].loc[idx, "Piklist No."] = str(new_pik)
                            st.session_state["data"].loc[idx, "Courier"] = new_cour
                            st.session_state["data"].loc[idx, "Status"] = new_status
                            st.session_state["data"].loc[idx, "Parcel Count"] = int(new_count)
                            save_data(st.session_state["data"])
                            st.success("Entry updated successfully!")
                            st.rerun()
                            
                        if delete_btn:
                            row_to_trash = df[df["ID"] == edit_id]
                            st.session_state["trash"] = pd.concat([st.session_state["trash"], row_to_trash], ignore_index=True)
                            st.session_state["data"] = df[df["ID"] != edit_id]
                            save_data(st.session_state["data"])
                            st.success("Entry deleted and moved to Recycle Bin successfully!")
                            st.rerun()
                    
            with sub_tab2:
                trash_df = st.session_state["trash"]
                if not trash_df.empty:
                    st.dataframe(trash_df.drop(columns=["ID"]), use_container_width=True)
                    
                    restore_id = st.selectbox("Select Entry ID to Restore", ["Select"] + list(trash_df["ID"].astype(str)), key="direct_restore_sel")
                    if restore_id != "Select":
                        if st.button("Restore Entry"):
                            row_to_restore = trash_df[trash_df["ID"] == restore_id]
                            st.session_state["data"] = pd.concat([st.session_state["data"], row_to_restore], ignore_index=True)
                            st.session_state["trash"] = trash_df[trash_df["ID"] != restore_id]
                            save_data(st.session_state["data"])
                            st.success("Entry restored successfully!")
                            st.rerun()
                else:
                    st.info("Recycle Bin is empty.")
        else:
            st.info(f"No entries found for {selected_date_str}.")
    else:
        st.info("No entries yet. Add entries using the form.")
