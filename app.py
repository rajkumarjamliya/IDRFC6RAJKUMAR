import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Warehouse Tracker & Management", layout="wide")

# App Title
st.title("📦 Warehouse Tracker & Management System")

# Session State for Login
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Sidebar for Admin Login
st.sidebar.header("🔐 Admin Login")
password_input = st.sidebar.text_input("Enter Admin Password", type="password")

if st.sidebar.button("Login"):
    if password_input == "1234":
        st.session_state["authenticated"] = True
        st.sidebar.success("Login Successful!")
    else:
        st.sidebar.error("Incorrect Password")

# Main Content Area
if not st.session_state["authenticated"]:
    st.warning("⚠️ Please enter the Admin password from the sidebar to make changes.")
else:
    st.success("🔓 Admin Access Granted. You can now manage and edit data.")

# Sample Data Storage for Tracking (Employee & Piklist Operations)
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=["AWB/Order ID", "Employee Name", "Task Type", "Status", "Time"])

# Section: Live Employee Status & New Entry
st.subheader("📋 Live Employee & Piklist Operations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Add New Entry")
    with st.form("entry_form"):
        awb = st.text_input("AWB / Order ID")
        emp_name = st.text_input("Employee Name")
        task_type = st.selectbox("Task Type", ["Picking", "Packing", "Loading", "Free"])
        status = st.selectbox("Status", ["In Progress", "Completed", "Pending"])
        submit = st.form_submit_button("Submit Entry")
        
        if submit:
            if awb and emp_name:
                new_row = pd.DataFrame({
                    "AWB/Order ID": [awb],
                    "Employee Name": [emp_name],
                    "Task Type": [task_type],
                    "Status": [status],
                    "Time": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")]
                })
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                st.success("Entry Added Successfully!")
            else:
                st.error("Please fill in all fields.")

with col2:
    st.markdown("### 📊 Live Status Dashboard")
    if not st.session_state["data"].empty:
        st.dataframe(st.session_state["data"], use_container_width=True)
    else:
        st.info("No entries yet. Add a new entry from the form.")

# Admin Only Delete Section
if st.session_state["authenticated"]:
    st.markdown("---")
    st.subheader("⚙️ Admin Control Panel (Delete / Reset Data)")
    if st.button("Clear All Data"):
        st.session_state["data"] = pd.DataFrame(columns=["AWB/Order ID", "Employee Name", "Task Type", "Status", "Time"])
        st.success("All data cleared successfully!")
        
