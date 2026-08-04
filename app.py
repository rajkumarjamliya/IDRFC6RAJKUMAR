import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import os

# Page Config
st.set_page_config(page_title="DELHIVERY – IDRFC6 DEWAS 3D Tracker", layout="wide")

# Custom 3D & Modern Glassmorphism CSS Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
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
    .main-header h1 { margin: 0; font-size: 28px; font-weight: 700; }
    .main-header p { margin: 8px 0 0 0; font-size: 15px; color: #00d2ff; }
    
    .card-3d {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1), inset 0 1px 2px rgba(255,255,255,0.8);
        border: 1px solid rgba(255,255,255,0.5);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Banner with IDRFC6 DEWAS
st.markdown("""
    <div class="main-header">
        <h1>📦 DELHIVERY – IDRFC6 DEWAS Tracker</h1>
        <p>Station: IDRFC6 DEWAS &nbsp;|&nbsp; Managed by: RAJKUMAR &nbsp;|&nbsp; Auto Time & 3D Dashboard</p>
    </div>
""", unsafe_allow_html=True)

DATA_FILE = "warehouse_entries.csv"
REPORT_FILE = "dispatch_reports.csv"

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Task Type", "Courier", "Parcel Count"])

def save_data(df): df.to_csv(DATA_FILE, index=False)

def load_reports():
    if os.path.exists(REPORT_FILE): return pd.read_csv(REPORT_FILE)
    return pd.DataFrame(columns=["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Remark"])

def save_reports(df): df.to_csv(REPORT_FILE, index=False)

if "data" not in st.session_state: st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state: st.session_state["dispatch_reports"] = load_reports()

couriers_list = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "DTDC", "Bluedart", "Ekart"]

st.sidebar.markdown("### ⚙️ Control Center")
selected_date = st.sidebar.date_input("Working Date", date.today())
selected_date_str = str(selected_date)

nav_page = st.sidebar.radio("Navigation Menu", ["🏠 Home Entry Portal", "📊 Analytics & Automatic Time Reports"])

if nav_page == "🏠 Home Entry Portal":
    col1, col2 = st.columns([1, 1.3])
    with col1:
        st.markdown("<div class='card-3d'><h3>📝 New Warehouse Entry</h3></div>", unsafe_allow_html=True)
        piklist_no = st.text_input("Piklist No.")
        emp_name = st.text_input("Employee Name")
        task_type = st.selectbox("Task Type", ["Manifest", "Picking", "Packing", "Scanning"])
        
        courier = "N/A"
        parcel_count = 1
        if task_type == "Manifest":
            courier = st.selectbox("Courier", couriers_list)
            parcel_count = st.number_input("Box Count", min_value=1, value=1)

        if st.button("💾 Submit Entry", use_container_width=True):
            if piklist_no and emp_name:
                auto_in_time = datetime.now().strftime("%I:%M %p")
                
                if task_type == "Manifest" and courier != "N/A":
                    rep_df = st.session_state["dispatch_reports"]
                    ex = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == courier)]
                    
                    parsed_in = datetime.strptime(auto_in_time, "%I:%M %p")
                    auto_out_time = (parsed_in + timedelta(minutes=5)).strftime("%I:%M %p")

                    if not ex.empty:
                        idx = ex.index[0]
                        rep_df.loc[idx, "Manifest"] += int(parcel_count)
                        if pd.isna(rep_df.loc[idx, "In Time"]) or rep_df.loc[idx, "In Time"] == "--:--":
                            rep_df.loc[idx, "In Time"] = auto_in_time
                            rep_df.loc[idx, "Out Time"] = auto_out_time
                    else:
                        new_rep = pd.DataFrame({
                            "Date": [selected_date_str], "Courier": [courier], 
                            "In Time": [auto_in_time], "Out Time": [auto_out_time], 
                            "Manifest": [int(parcel_count)], "Cancel": [0], "Dispatch": [0], "Remark": ["Auto System Logged"]
                        })
                        st.session_state["dispatch_reports"] = pd.concat([rep_df, new_rep], ignore_index=True)
                    save_reports(st.session_state["dispatch_reports"])
                
                st.success(f"Entry Saved Successfully!\n\n🕒 In-Time: **{auto_in_time}**")
                st.rerun()

elif nav_page == "📊 Analytics & Automatic Time Reports":
    st.markdown("<div class='card-3d'><h3>🚚 Automatic Time In/Out Report (+5 Mins)</h3></div>", unsafe_allow_html=True)
    rep_df = st.session_state["dispatch_reports"]
    
    with st.form("auto_time_form"):
        sel_courier = st.selectbox("Select Courier", couriers_list)
        curr_row = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == sel_courier)]
        
        default_in = datetime.now().strftime("%I:%M %p")
        if not curr_row.empty and pd.notna(curr_row["In Time"].values[0]) and curr_row["In Time"].values[0] != "--:--":
            default_in = curr_row["In Time"].values[0]
            
        c_dispatch = st.number_input("Enter Dispatch Boxes", min_value=0, value=int(curr_row["Dispatch"].values[0]) if not curr_row.empty else 0)
        c_cancel = st.number_input("Enter Cancel Boxes", min_value=0, value=int(curr_row["Cancel"].values[0]) if not curr_row.empty else 0)
        
        try:
            p_in = datetime.strptime(default_in.strip(), "%I:%M %p")
            calc_out = (p_in + timedelta(minutes=5)).strftime("%I:%M %p")
        except:
            calc_out = (datetime.now() + timedelta(minutes=5)).strftime("%I:%M %p")
            
        st.info(f"⚡ System Auto Time -> In-Time: **{default_in}** | Out-Time (In + 5 Mins): **{calc_out}**")

        if st.form_submit_button("Confirm & Save Dispatch"):
            if not curr_row.empty:
                idx = curr_row.index[0]
                rep_df.loc[idx, "In Time"] = default_in
                rep_df.loc[idx, "Out Time"] = calc_out
                rep_df.loc[idx, "Dispatch"] = c_dispatch
                rep_df.loc[idx, "Cancel"] = c_cancel
            else:
                new_rep = pd.DataFrame({
                    "Date": [selected_date_str], "Courier": [sel_courier], 
                    "In Time": [default_in], "Out Time": [calc_out], 
                    "Manifest": [0], "Cancel": [c_cancel], "Dispatch": [c_dispatch], "Remark": ["Auto Timing"]
                })
                st.session_state["dispatch_reports"] = pd.concat([rep_df, new_rep], ignore_index=True)
            save_reports(st.session_state["dispatch_reports"])
            st.success("Dispatch & Timing Saved Successfully!")
            st.rerun()

    st.dataframe(st.session_state["dispatch_reports"], use_container_width=True)
