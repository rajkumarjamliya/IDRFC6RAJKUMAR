import pandas as pd
import streamlit as st
from datetime import date
import base64

# Page Configuration
st.set_page_config(page_title="DELHIVERY – IDRFC6 Warehouse Tracker", layout="wide")

# Custom Professional Styling & Header Branding
st.markdown("""
    <style>
    .main-title {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding-bottom: 10px;
    }
    .sub-banner {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        color: #333;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📦 DELHIVERY – IDRFC6 Warehouse Operations Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-banner">Managed by: RAJKUMAR | Station: IDRFC6</div>', unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=[
        "Date", "Timestamp", "Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Parcel Count", "Status", "Mistake / Error"
    ])

if "employees" not in st.session_state:
    st.session_state["employees"] = ["Kapil", "Sanjiv", "Bmpatel", "Rajkumar"]

if "couriers" not in st.session_state:
    st.session_state["couriers"] = ["Delhivery", "Xpressbees", "Ecom Express", "Bluedart", "Shadowfax"]

# Sidebar for Admin Login & Settings
st.sidebar.header("🔐 Admin Panel & Management")
password_input = st.sidebar.text_input("Enter Admin Password", type="password")

if st.sidebar.button("Login"):
    if password_input == "1234":
        st.session_state["authenticated"] = True
        st.sidebar.success("Admin Login Successful!")
    else:
        st.sidebar.error("Incorrect Password")

# Date Selection for View
selected_date = st.sidebar.date_input("Select Date for View", date.today())
selected_date_str = str(selected_date)

# Admin Master Management (Add Employee / Courier)
if st.session_state["authenticated"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Master Settings")
    new_emp = st.sidebar.text_input("Add New Employee")
    if st.sidebar.button("Save Employee"):
        if new_emp and new_emp not in st.session_state["employees"]:
            st.session_state["employees"].append(new_emp)
            st.sidebar.success(f"Employee {new_emp} added!")
            
    new_courier = st.sidebar.text_input("Add New Courier")
    if st.sidebar.button("Save Courier"):
        if new_courier and new_courier not in st.session_state["couriers"]:
            st.session_state["couriers"].append(new_courier)
            st.sidebar.success(f"Courier {new_courier} added!")

# Main Layout: Two Columns (Form on Left, Dashboard on Right)
col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown(f"### 📝 Operation Entry Form ({selected_date_str})")
    
    with st.form("entry_form", clear_on_submit=True):
        piklist_no = st.text_input("Piklist No.")
        emp_name = st.selectbox("Employee Name", ["Select Employee"] + st.session_state["employees"])
        emp_id = st.text_input("Employee ID")
        task_type = st.selectbox("Task Type", ["Manifest", "Picking", "Scanning", "Packing", "Loading", "Free"])
        courier = st.selectbox("Courier", st.session_state["couriers"])
        parcel_count = st.number_input("Parcel Count (Quantity)", min_value=1, step=1, value=1)
        status = st.selectbox("Status", ["Completed", "Pending", "In Progress", "Error"])
        mistake = st.selectbox("Mistake / Error", ["None", "Wrong Item", "Missing Item", "Tag Damage", "Wrong Scanning"])
        
        submit = st.form_submit_button("Submit Entry")
        
        if submit:
            if piklist_no and emp_name != "Select Employee" and emp_id:
                new_row = pd.DataFrame({
                    "Date": [selected_date_str],
                    "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Piklist No.": [piklist_no],
                    "Employee Name": [emp_name],
                    "Employee ID": [emp_id],
                    "Task Type": [task_type],
                    "Courier": [courier],
                    "Parcel Count": [int(parcel_count)],
                    "Status": [status],
                    "Mistake / Error": [mistake]
                })
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                st.success("Entry Saved Successfully!")
            else:
                st.error("Please fill Piklist No., Employee Name, and Employee ID.")

with col2:
    st.markdown(f"### 📊 Live Dashboard & Reports ({selected_date_str})")
    
    df = st.session_state["data"]
    
    if not df.empty:
        df_filtered = df[df["Date"] == selected_date_str]
        
        if not df_filtered.empty:
            total_parcels = df_filtered["Parcel Count"].sum()
            st.metric(label="📦 Total Parcels Completed on this Date", value=total_parcels)
            
            # Table 1: Piklist-wise & Courier-wise Counting Table
            st.markdown("#### 1️⃣ Piklist-wise & Courier-wise Breakdown")
            piklist_courier_summary = df_filtered.groupby(["Piklist No.", "Courier"])["Parcel Count"].sum().reset_index()
            piklist_courier_summary.columns = ["Piklist No.", "Courier Name", "Total Parcels"]
            st.dataframe(piklist_courier_summary, use_container_width=True)
            
            # Table 2: Total Courier-wise Counting with Grand Total
            st.markdown("#### 2️⃣ Total Courier-wise Summary")
            courier_summary = df_filtered.groupby("Courier")["Parcel Count"].sum().reset_index()
            courier_summary.columns = ["Courier Name", "Total Parcels"]
            
            grand_total = courier_summary["Total Parcels"].sum()
            total_row = pd.DataFrame({"Courier Name": ["GRAND TOTAL"], "Total Parcels": [grand_total]})
            courier_summary = pd.concat([courier_summary, total_row], ignore_index=True)
            
            st.dataframe(courier_summary, use_container_width=True)
            
            # Export to CSV (Excel format) and Print Option buttons
            st.markdown("#### 📥 Export & Print Options")
            col_csv, col_print = st.columns(2)
            
            with col_csv:
                csv_data = df_filtered.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Excel / CSV",
                    data=csv_data,
                    file_name=f"Warehouse_Report_{selected_date_str}.csv",
                    mime="text/csv",
                )
                
            with col_print:
                if st.button("🖨️ Print Report View"):
                    st.toast("Use browser shortcut Ctrl+P to print this page cleanly.")

            # Detailed Records for the day
            st.markdown("#### 📋 Detailed Log for Selected Date")
            st.dataframe(df_filtered, use_container_width=True)
        else:
            st.info(f"No entries found for {selected_date_str}.")
    else:
        st.info("No entries yet. Add entries using the form.")

# Admin Control Panel (Secured Data Deletion with Warning)
if st.session_state["authenticated"]:
    st.markdown("---")
    st.subheader("⚙️ Admin Danger Zone & Complete History")
    
    if not df.empty:
        st.markdown("#### 📅 Complete Data Across All Dates")
        st.dataframe(df, use_container_width=True)
        
        st.warning("⚠️ Data deletion requires confirmation check below to avoid accidental data loss.")
        confirm_delete = st.checkbox("I want to permanently delete all historical data")
        
        if st.button("Clear All Data (Reset System)") and confirm_delete:
            st.session_state["data"] = pd.DataFrame(columns=[
                "Date", "Timestamp", "Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Parcel Count", "Status", "Mistake / Error"
            ])
            st.success("All historical data cleared successfully!")
        elif st.button("Clear All Data (Reset System)") and not confirm_delete:
            st.error("Please check the confirmation box above before clearing data.")
