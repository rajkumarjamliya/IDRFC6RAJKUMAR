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
        <p>Station: IDRFC6 DEWAS &nbsp;|&nbsp; Managed by: RAJKUMAR &nbsp;|&nbsp; Auto Time & Return Boxes Enabled</p>
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
    # Added 'Return' column to tracking reports
    return pd.DataFrame(columns=["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"])

def save_reports(df): df.to_csv(REPORT_FILE, index=False)

if "data" not in st.session_state: st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state: st.session_state["dispatch_reports"] = load_reports()

couriers_list = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "DTDC", "Bluedart", "Ekart"]

st.sidebar.markdown("### ⚙️ Control Center")
selected_date = st.sidebar.date_input("Working Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

nav_page = st.sidebar.radio("Navigation Menu", ["🏠 Home Entry Portal", "📊 Analytics & Return/Dispatch Reports"])

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
                            "Manifest": [int(parcel_count)], "Cancel": [0], "Dispatch": [0], "Return": [0], "Remark": ["Auto System Logged"]
                        })
                        st.session_state["dispatch_reports"] = pd.concat([rep_df, new_rep], ignore_index=True)
                    save_reports(st.session_state["dispatch_reports"])
                
                st.success(f"Entry Saved Successfully!\n\n🕒 In-Time: **{auto_in_time}**")
                st.rerun()

elif nav_page == "📊 Analytics & Return/Dispatch Reports":
    st.markdown("<div class='card-3d'><h3>🚚 Dispatch, Cancel & Return Parcel Report</h3></div>", unsafe_allow_html=True)
    rep_df = st.session_state["dispatch_reports"]
    
    with st.form("auto_time_form"):
        sel_courier = st.selectbox("Select Courier", couriers_list)
        curr_row = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == sel_courier)]
        
        default_in = datetime.now().strftime("%I:%M %p")
        if not curr_row.empty and pd.notna(curr_row["In Time"].values[0]) and curr_row["In Time"].values[0] != "--:--":
            default_in = curr_row["In Time"].values[0]
            
        c_dispatch = st.number_input("Dispatch Boxes (Bheje Gaye)", min_value=0, value=int(curr_row["Dispatch"].values[0]) if not curr_row.empty and "Dispatch" in curr_row.columns else 0)
        c_cancel = st.number_input("Cancel Boxes (Radd Kiye Gaye)", min_value=0, value=int(curr_row["Cancel"].values[0]) if not curr_row.empty and "Cancel" in curr_row.columns else 0)
        c_return = st.number_input("Return Boxes (Kitne Box Wapas Aaye)", min_value=0, value=int(curr_row["Return"].values[0]) if not curr_row.empty and "Return" in curr_row.columns else 0)
        c_remark = st.text_input("Remark", value=str(curr_row["Remark"].values[0]) if not curr_row.empty and pd.notna(curr_row["Remark"].values[0]) else "")
        
        try:
            p_in = datetime.strptime(default_in.strip(), "%I:%M %p")
            calc_out = (p_in + timedelta(minutes=5)).strftime("%I:%M %p")
        except:
            calc_out = (datetime.now() + timedelta(minutes=5)).strftime("%I:%M %p")
            
        st.info(f"⚡ System Auto Time -> In-Time: **{default_in}** | Out-Time (In + 5 Mins): **{calc_out}**")

        if st.form_submit_button("Confirm & Save Report"):
            if not curr_row.empty:
                idx = curr_row.index[0]
                rep_df.loc[idx, "In Time"] = default_in
                rep_df.loc[idx, "Out Time"] = calc_out
                rep_df.loc[idx, "Dispatch"] = c_dispatch
                rep_df.loc[idx, "Cancel"] = c_cancel
                rep_df.loc[idx, "Return"] = c_return
                rep_df.loc[idx, "Remark"] = c_remark
            else:
                new_rep = pd.DataFrame({
                    "Date": [selected_date_str], "Courier": [sel_courier], 
                    "In Time": [default_in], "Out Time": [calc_out], 
                    "Manifest": [0], "Cancel": [c_cancel], "Dispatch": [c_dispatch], "Return": [c_return], "Remark": [c_remark]
                })
                st.session_state["dispatch_reports"] = pd.concat([rep_df, new_rep], ignore_index=True)
            save_reports(st.session_state["dispatch_reports"])
            st.success("Dispatch, Cancel & Return Report Saved Successfully!")
            st.rerun()

    # Calculate Summary with Returns Included
    current_day_rep = rep_df[rep_df["Date"] == selected_date_str] if not rep_df.empty else pd.DataFrame()
    
    # Yesterday pending map
    yest_pend_map = {}
    yest_rep_view = rep_df[rep_df["Date"] == yesterday_str] if not rep_df.empty else pd.DataFrame()
    for c in couriers_list:
        c_yest = yest_rep_view[yest_rep_view["Courier"] == c]
        if not c_yest.empty:
            man_y = int(c_yest["Manifest"].values[0])
            can_y = int(c_yest["Cancel"].values[0])
            dis_y = int(c_yest["Dispatch"].values[0])
            ret_y = int(c_yest["Return"].values[0]) if "Return" in c_yest.columns else 0
            yest_pend_map[c] = max(0, man_y - can_y - dis_y + ret_y)
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
        ret = int(c_curr["Return"].values[0]) if not c_curr.empty and "Return" in c_curr.columns else 0
        rem = str(c_curr["Remark"].values[0]) if not c_curr.empty and pd.notna(c_curr["Remark"].values[0]) else ""
        y_pend = yest_pend_map.get(c, 0)
        
        # Formula including Returns
        final_pend = max(0, (man + y_pend) - can - dis + ret)
        
        display_summary_rows.append({
            "Courier": c,
            "Yesterday Pending": y_pend,
            "In Time": in_t,
            "Out Time": out_t,
            "Manifest": man,
            "Cancel": can,
            "Dispatch": dis,
            "Return": ret,
            "Pending": final_pend,
            "Remark": rem
        })
        
    st.markdown("#### 📋 Final Courier Status & Return Summary Table")
    st.dataframe(pd.DataFrame(display_summary_rows), use_container_width=True)
