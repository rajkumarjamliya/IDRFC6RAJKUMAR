import pandas as pd
import streamlit as st
from datetime import date

# Page Configuration
st.set_page_config(page_title="DELHIVERY – IDRFC6 Warehouse Tracker", layout="wide")

# App Title
st.title("📦 DELHIVERY – IDRFC6 Warehouse Operations Tracker")

# Session State for Login and Data
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "data" not in st.session_state:
    # Persistent master storage across dates
    st.session_state["data"] = pd.DataFrame(columns=[
        "Date", "Timestamp", "Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Parcel Count", "Status", "Mistake / Error"
    ])

# Sidebar for Admin Login & Date Filtering / Management
st.sidebar.header("🔐 Admin Panel & Filters")
password_input = st.sidebar.text_input("Enter Admin Password", type="password")

if st.sidebar.button("Login"):
    if password_input == "1234":
        st.session_state["authenticated"] = True
        st.sidebar.success("Login Successful!")
    else:
        st.sidebar.error("Incorrect Password")

# Date Selection for Main View (Default is Today)
today_str = str(date.today())
selected_date = st.sidebar.date_input("Select Date for View", date.today())
selected_date_str = str(selected_date)

# Main Content Layout: Two Columns (Form on Left, Dashboard on Right)
col1, col2 = st.columns([1, 1.3])

with col1:
    st.markdown(f"### 📝 Add Entry ({selected_date_str})")
    
    with st.form("entry_form", clear_on_submit=True):
        piklist_no = st.text_input("Piklist No.")
        emp_name = st.selectbox("Employee Name", ["Select Employee", "Kapil", "Sanjiv", "Bmpatel", "Rajkumar", "Other"])
        emp_id = st.text_input("Employee ID")
        task_type = st.selectbox("Task Type", ["Manifest", "Picking", "Scanning", "Packing", "Loading", "Free"])
        courier = st.selectbox("Courier", ["Delhivery", "Xpressbees", "Ecom Express", "Bluedart", "Shadowfax", "Other"])
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
        # Filter data for the selected date
        df_filtered = df[df["Date"] == selected_date_str]
        
        if not df_filtered.empty:
            total_parcels = df_filtered["Parcel Count"].sum()
            st.metric(label="📦 Total Parcels Completed on this Date", value=total_parcels)
            
            # Table 1: Piklist-wise & Courier-wise Counting Table
            st.markdown("#### 1️⃣ Piklist-wise & Courier-wise Breakdown")
            piklist_courier_summary = df_filtered.groupby(["Piklist No.", "Courier"])["Parcel Count"].sum().reset_index()
            piklist_courier_summary.columns = ["Piklist No.", "Courier Name", "Total Parcels"]
            st.dataframe(piklist_courier_summary, use_container_width=True)
            
            # Table 2: Total Courier-wise Counting with Grand Total at Bottom
            st.markdown("#### 2️⃣ Total Courier-wise Summary")
            courier_summary = df_filtered.groupby("Courier")["Parcel Count"].sum().reset_index()
            courier_summary.columns = ["Courier Name", "Total Parcels"]
            
            # Add Grand Total Row
            grand_total = courier_summary["Total Parcels"].sum()
            total_row = pd.DataFrame({"Courier Name": ["GRAND TOTAL"], "Total Parcels": [grand_total]})
            courier_summary = pd.concat([courier_summary, total_row], ignore_index=True)
            
            st.dataframe(courier_summary, use_container_width=True)
            
            # Detailed Records for the day
            st.markdown("#### 📋 Detailed Log for Selected Date")
            st.dataframe(df_filtered, use_container_width=True)
        else:
            st.info(f"No entries found for {selected_date_str}. Add entries using the form.")
    else:
        st.info("No entries yet. Add a new entry to see summaries.")

# Admin Panel Options (Date-to-Date Records & Clear Data)
if st.session_state["authenticated"]:
    st.markdown("---")
    st.subheader("⚙️ Admin Control Panel (All Dates & Reports)")
    
    if not df.empty:
        st.markdown("#### 📅 View Complete Data Across All Dates")
        st.dataframe(df, use_container_width=True)
        
        if st.button("Clear All Data (Reset System)"):
            st.session_state["data"] = pd.DataFrame(columns=[
                "Date", "Timestamp", "Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Parcel Count", "Status", "Mistake / Error"
            ])
            st.success("All historical data cleared successfully!")
