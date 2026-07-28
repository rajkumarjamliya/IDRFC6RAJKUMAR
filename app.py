import pandas as pd
import streamlit as st
from datetime import date, timedelta
import os

# Page Config
st.set_page_config(page_title="DELHIVERY – IDRFC6 Tracker", layout="wide")

st.markdown("""
    <div style="background: #1f77b4; padding: 15px; border-radius: 8px; color: white; text-align: center; margin-bottom: 15px;">
        <h2 style="margin:0; font-size: 22px;">📦 DELHIVERY – IDRFC6 Warehouse Tracker</h2>
        <p style="margin:5px 0 0 0; font-size: 14px;">Managed by: RAJKUMAR</p>
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
    return pd.DataFrame(columns=["Date", "Courier", "Manifest", "Cancel", "Dispatch", "Remark"])

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

# Sidebar
st.sidebar.header("⚙️ Settings & Login")
selected_date = st.sidebar.date_input("Working Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

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

# Main Layout
col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown(f"### 📝 New Entry ({selected_date_str})")
    
    piklist_no = st.text_input("Piklist No.")
    emp_name = st.selectbox("Employee Name", ["Select"] + list(employees.keys()))
    
    auto_id = employees.get(emp_name, "") if emp_name != "Select" else ""
    if emp_name != "Select":
        st.write(f"🆔 ID: **{auto_id}**")
        
    task_type = st.selectbox("Task Type", ["Manifest", "Picking", "Scanning", "Packing", "Loading", "Free"])
    
    courier = "N/A"
    parcel_count = 1
    if task_type == "Manifest":
        courier = st.selectbox("Courier", couriers_list)
        parcel_count = st.number_input("Box Count", min_value=1, value=1)
    else:
        parcel_count = st.number_input("Item Count", min_value=1, value=1)
        
    status = st.selectbox("Status", ["Completed", "Pending", "In Progress", "Error"])
    mistake = st.selectbox("Mistake", ["None", "Wrong Item", "Missing Item", "Tag Damage", "Wrong Scanning"])
    
    if st.button("💾 Submit Entry", use_container_width=True):
        if piklist_no and emp_name != "Select":
            new_id = str(pd.Timestamp.now().timestamp())
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
            
            # Update Reports
            if task_type == "Manifest" and courier != "N/A":
                rep_df = st.session_state["dispatch_reports"]
                ex = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == courier)]
                if not ex.empty:
                    idx = ex.index[0]
                    rep_df.loc[idx, "Manifest"] += int(parcel_count)
                else:
                    new_rep = pd.DataFrame({"Date": [selected_date_str], "Courier": [courier], "Manifest": [int(parcel_count)], "Cancel": [0], "Dispatch": [0], "Remark": [""]})
                    st.session_state["dispatch_reports"] = pd.concat([rep_df, new_rep], ignore_index=True)
                save_reports(st.session_state["dispatch_reports"])
                
            st.success("Saved Successfully!")
            st.rerun()
        else:
            st.error("Piklist No. aur Employee Name bharein!")

with col2:
    st.markdown(f"### 📊 Dashboard ({selected_date_str})")
    
    df = st.session_state["data"]
    df_f = df[df["Date"] == selected_date_str].copy() if not df.empty else pd.DataFrame()
    
    # Table 1
    st.markdown("#### 📋 1. Piklist & Courier Record")
    if not df_f.empty:
        st.dataframe(df_f[["Piklist No.", "Courier", "Parcel Count", "Task Type", "Timestamp"]], use_container_width=True)
        
        # Simple Home Edit
        with st.form("quick_edit"):
            st.markdown("##### ✏️ Quick Edit Record")
            ids = list(df_f["ID"].astype(str))
            sel_id = st.selectbox("Select Record", ids, format_func=lambda x: f"Piklist: {df_f[df_f['ID'].astype(str) == x]['Piklist No.'].values[0]}")
            r_dat = df_f[df_f["ID"].astype(str) == sel_id].iloc[0]
            
            up_pik = st.text_input("New Piklist No.", value=str(r_dat["Piklist No."]))
            up_cou = st.selectbox("New Courier", couriers_list, index=couriers_list.index(r_dat["Courier"]) if r_dat["Courier"] in couriers_list else 0)
            up_cnt = st.number_input("New Count", min_value=1, value=int(r_dat["Parcel Count"]))
            
            if st.form_submit_button("Update"):
                m_i = st.session_state["data"][st.session_state["data"]["ID"].astype(str) == sel_id].index[0]
                st.session_state["data"].loc[m_i, "Piklist No."] = str(up_pik)
                st.session_state["data"].loc[m_i, "Courier"] = up_cou
                st.session_state["data"].loc[m_i, "Parcel Count"] = int(up_cnt)
                save_data(st.session_state["data"])
                st.success("Updated!")
                st.rerun()
    else:
        st.info("No records today.")

    # Table 2: Box Count
    st.markdown("---")
    st.markdown("#### 📦 2. Courier Box Summary")
    if not df_f.empty:
        man_df = df_f[df_f["Courier"].isin(couriers_list)]
        if not man_df.empty:
            summary = man_df.groupby("Courier")["Parcel Count"].sum().reset_index()
            st.dataframe(summary, use_container_width=True)
        else:
            st.info("No box data.")
            
    # Table 3: Work Records
    st.markdown("---")
    st.markdown("#### 🕒 3. Employee Work Records")
    if not df_f.empty:
        st.dataframe(df_f[["Timestamp", "Employee Name", "Task Type", "Piklist No.", "Courier", "Parcel Count"]], use_container_width=True)
    else:
        st.info("No records.")

# Admin Panel
st.markdown("---")
st.markdown("### 🔒 Admin Panel (Delete & Restore)")
if st.session_state["authenticated"]:
    t1, t2 = st.tabs(["🗑️ Date-wise Delete", "♻️ Recycle Bin"])
    
    with t1:
        del_date = st.date_input("Select Date to Delete", date.today())
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
            
    with t2:
        trash_df = st.session_state["trash"]
        if not trash_df.empty:
            st.dataframe(trash_df[["Piklist No.", "Employee Name", "Courier"]], use_container_width=True)
            res_id = st.selectbox("Select to Restore", ["Select"] + list(trash_df["ID"].astype(str)))
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
    st.warning("⚠️ Sidebar me Admin Password (`122436`) daalkar login karein.")
