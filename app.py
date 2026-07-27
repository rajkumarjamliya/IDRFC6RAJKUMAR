import pandas as pd
import streamlit as st
import cv2
import numpy as np

# Page Configuration
st.set_page_config(page_title="DELHIVERY – IDRFC6 Warehouse Tracker", layout="wide")

# App Title
st.title("📦 DELHIVERY – IDRFC6 Warehouse Operations Tracker")

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

if not st.session_state["authenticated"]:
    st.warning("⚠️ Please enter the Admin password from the sidebar to make changes.")
else:
    st.success("🔓 Admin Access Granted.")

# Data Storage Initialization
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=[
        "Timestamp", "AWB / Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Status", "Mistake / Error"
    ])

# Layout: Two Columns (Form on Left, Dashboard/Summary on Right)
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("### 📝 Add New Entry")
    
    # Camera Scanning Section
    st.markdown("#### 📷 Mobile Camera Scanner")
    camera_image = st.camera_input("Scan Barcode / QR Code")
    scanned_code = ""

    if camera_image is not None:
        bytes_data = camera_image.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Detect QR Code
        qr_detector = cv2.QRCodeDetector()
        qr_data, _, _ = qr_detector.detectAndDecode(cv2_img)
        
        if qr_data:
            scanned_code = qr_data
            st.success(f"✅ Scanned Code: {scanned_code}")
        else:
            try:
                barcode_detector = cv2.barcode.BarcodeDetector()
                ok, barcode_data, _, _ = barcode_detector.detectAndDecode(cv2_img)
                if ok and barcode_data and barcode_data[0]:
                    scanned_code = barcode_data[0]
                    st.success(f"✅ Scanned Barcode: {scanned_code}")
                else:
                    st.info("💡 Code detect nahi hua. Niche manual type karein.")
            except Exception:
                st.info("💡 Code detect nahi hua. Niche manual enter karein.")

    st.markdown("---")
    
    with st.form("entry_form"):
        awb = st.text_input("AWB / Piklist No.", value=scanned_code)
        emp_name = st.text_input("Employee Name")
        emp_id = st.text_input("Employee ID")
        task_type = st.selectbox("Task Type", ["Picking", "Scanning", "Packing", "Manifest", "Loading", "Free"])
        courier = st.selectbox("Courier", ["Delhivery", "Xpressbees", "Ecom Express", "Bluedart", "Shadowfax", "Other"])
        status = st.selectbox("Status", ["Completed", "Pending", "In Progress", "Error"])
        mistake = st.selectbox("Mistake / Error", ["None", "Wrong Item", "Missing Item", "Tag Damage", "Wrong Scanning"])
        
        submit = st.form_submit_button("Submit Entry")
        
        if submit:
            if awb and emp_name and emp_id:
                new_row = pd.DataFrame({
                    "Timestamp": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "AWB / Piklist No.": [awb],
                    "Employee Name": [emp_name],
                    "Employee ID": [emp_id],
                    "Task Type": [task_type],
                    "Courier": [courier],
                    "Status": [status],
                    "Mistake / Error": [mistake]
                })
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                st.success("Entry Saved Successfully!")
            else:
                st.error("Please fill in AWB, Employee Name, and Employee ID.")

with col2:
    st.markdown("### 📊 Live Summary & Dashboard")
    
    df = st.session_state["data"]
    
    if not df.empty:
        # Total counts metrics
        total_parcels = len(df)
        st.metric(label="📦 Total Entries / Parcels", value=total_parcels)
        
        # Courier-wise Counting Table
        st.markdown("#### 🚚 Courier-wise Counting")
        courier_counts = df["Courier"].value_counts().reset_index()
        courier_counts.columns = ["Courier Name", "Total Count"]
        st.dataframe(courier_counts, use_container_width=True)
        
        # Employee-wise Performance Table
        st.markdown("#### 👨‍💻 Employee-wise Performance")
        emp_counts = df[["Employee Name", "Employee ID"]].value_counts().reset_index()
        emp_counts.columns = ["Employee Name", "Employee ID", "Total Tasks Done"]
        st.dataframe(emp_counts, use_container_width=True)
        
        # Full Live Data Table
        st.markdown("#### 📋 Detailed Records")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No entries yet. Add a new entry to see live counting and summaries.")

# Admin Control Panel
if st.session_state["authenticated"]:
    st.markdown("---")
    st.subheader("⚙️ Admin Control Panel")
    if st.button("Clear All Data"):
        st.session_state["data"] = pd.DataFrame(columns=[
            "Timestamp", "AWB / Piklist No.", "Employee Name", "Employee ID", "Task Type", "Courier", "Status", "Mistake / Error"
        ])
        st.success("All data cleared successfully!")
