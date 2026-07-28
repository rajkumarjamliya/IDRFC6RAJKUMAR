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
    </style>
    <div class="main-header">
        <h1>📦 DELHIVERY – IDRFC6 Warehouse Operations Tracker</h1>
        <p>Station: IDRFC6 | Managed by: RAJKUMAR</p>
    </div>
""", unsafe_allow_html=True)

# ----------------- DATA STORAGE FILES -----------------
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

# ----------------- SIDEBAR: LOGIN & DATE -----------------
st.sidebar.header("🔐 Admin Panel & Date")
selected_date = st.sidebar.date_input("Select Working Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

if not st.session_state["authenticated"]:
    password_input = st.sidebar.text_input("Enter Admin Password", type="password", key="login_pass")
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

# ----------------- MAIN LAYOUT: FORM & REPORTS -----------------
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown(f"### 📝 Entry Form ({selected_date_str})")
    
    piklist_no = st.text_input("Piklist No. (Sankhiya)")
    
    emp_names_list = ["Select Employee"] + list(st.session_state["employees"].keys())
    emp_name = st.selectbox("Employee Name", emp_names_list)
    
    auto_emp_id = st.session_state["employees"].get(emp_name, "") if emp_name != "Select Employee" else ""
    if emp_name != "Select Employee":
        st.info(f"🆔 Employee ID: **{auto_emp_id}**")
    
    task_type = st.selectbox("Task Type", ["Manifest", "Picking", "Scanning", "Packing", "Loading", "Free"])
    
    courier = "N/A"
    parcel_count = 1
    if task_type == "Manifest":
        courier = st.selectbox("Courier Name", st.session_state["couriers"])
        parcel_count = st.number_input("Courier Box Count / Quantity", min_value=1, step=1, value=1, key="parcels_man")
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
            
            # Automatically update Courier Manifest Report if Task Type is Manifest
            if task_type == "Manifest" and courier != "N/A":
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
    st.markdown(f"### 📊 Warehouse Dashboard & Reports ({selected_date_str})")
    
    df = st.session_state["data"]
    df_filtered = df[df["Date"] == selected_date_str].copy() if not df.empty else pd.DataFrame()
    
    # ----------------- TABLE 1: PIKLIST & COURIER WISE RECORD (UPPER) -----------------
    st.markdown("#### 📋 1. Piklist & Courier Wise Record (Kis Piklist me kitna item/box)")
    if not df_filtered.empty:
        # Filter only Manifest or entries with courier info
        pik_courier_df = df_filtered[["Piklist No.", "Courier", "Parcel Count", "Task Type", "Timestamp"]].copy()
        st.dataframe(pik_courier_df, use_container_width=True)
    else:
        st.info("No records for this date yet.")
        
    # ----------------- TABLE 2: COURIER WISE TOTAL BOX COUNT -----------------
    st.markdown("---")
    st.markdown("#### 📦 2. Courier Wise Total Box Count")
    if not df_filtered.empty:
        # Group by Courier and sum Parcel Count where task is Manifest or courier is valid
        manifest_entries = df_filtered[df_filtered["Courier"].isin(st.session_state["couriers"])]
        if not manifest_entries.empty:
            courier_summary = manifest_entries.groupby("Courier")["Parcel Count"].sum().reset_index()
            courier_summary.columns = ["Courier Name", "Total Boxes / Count"]
            st.dataframe(courier_summary, use_container_width=True)
        else:
            st.info("No courier box data recorded yet.")
    else:
        st.info("No data available.")

    # ----------------- TABLE 3: DISPATCH REPORT -----------------
    st.markdown("---")
    st.markdown(f"#### 📊 3. Dispatch Report (Courier Wise)")
    
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

    # ----------------- TABLE 4: LADKO KA TIME & DATE HISAB (WORK RECORDS) -----------------
    st.markdown("---")
    st.markdown(f"#### 🕒 4. Ladko Ka Kaam & Time Hisab (Employee Work Records)")
    if not df_filtered.empty:
        emp_work_df = df_filtered[["Timestamp", "Employee Name", "Task Type", "Piklist No.", "Courier", "Parcel Count", "Status"]].copy()
        st.dataframe(emp_work_df, use_container_width=True)
    else:
        st.info("No work records for today.")

# ----------------- ADMIN CORRECTION & EDIT SECTION (LADKO KA GALAT ENTRY SUDRANE KE LIYE) -----------------
st.markdown("---")
st.markdown("### ⚙️ Admin Correction Panel (Galat Entry ya Naam Sudharne Ke Liye)")
if st.session_state["authenticated"]:
    if not df.empty and not df[df["Date"] == selected_date_str].empty:
        df_fil = df[df["Date"] == selected_date_str]
        
        with st.form("admin_correction_form"):
            entry_ids_list = list(df_fil["ID"].astype(str))
            selected_edit_id = st.selectbox(
                "Select Entry to Correct", 
                entry_ids_list, 
                format_func=lambda x: f"Piklist: {df_fil[df_fil['ID'].astype(str) == x]['Piklist No.'].values[0]} | Emp: {df_fil[df_fil['ID'].astype(str) == x]['Employee Name'].values[0]} | Time: {df_fil[df_fil['ID'].astype(str) == x]['Timestamp'].values[0]}"
            )
            
            row_data = df_fil[df_fil["ID"].astype(str) == selected_edit_id].iloc[0]
            
            new_pik_val = st.text_input("Corrected Piklist No.", value=str(row_data["Piklist No."]))
            
            curr_emp = row_data["Employee Name"]
            emp_list_keys = list(st.session_state["employees"].keys())
            new_emp_val = st.selectbox("Corrected Employee Name", emp_list_keys, index=emp_list_keys.index(curr_emp) if curr_emp in emp_list_keys else 0)
            
            curr_cour = row_data["Courier"] if row_data["Courier"] in st.session_state["couriers"] else "Delhivery"
            new_cour_val = st.selectbox("Corrected Courier Name", st.session_state["couriers"], index=st.session_state["couriers"].index(curr_cour) if curr_cour in st.session_state["couriers"] else 0)
            
            new_count_val = st.number_input("Corrected Box / Parcel Count", min_value=1, step=1, value=int(row_data["Parcel Count"]))
            
            if st.form_submit_button("Update / Correct Entry"):
                main_idx = st.session_state["data"][st.session_state["data"]["ID"].astype(str) == selected_edit_id].index[0]
                st.session_state["data"].loc[main_idx, "Piklist No."] = str(new_pik_val)
                st.session_state["data"].loc[main_idx, "Employee Name"] = new_emp_val
                st.session_state["data"].loc[main_idx, "Employee ID"] = st.session_state["employees"].get(new_emp_val, "")
                st.session_state["data"].loc[main_idx, "Courier"] = new_cour_val
                st.session_state["data"].loc[main_idx, "Parcel Count"] = int(new_count_val)
                
                save_data(st.session_state["data"])
                st.success("Entry corrected successfully!")
                st.rerun()
    else:
        st.info("No entries to correct for selected date.")
else:
    st.warning("⚠️ Admin Password (`122436`) dalkar sidebar se login karein agar koi galat entry ya naam sudharna hai.")
