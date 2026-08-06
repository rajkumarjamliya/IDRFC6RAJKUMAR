import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import os

# Page Config
st.set_page_config(page_title="DELHIVERY – IDRFC6 DEWAS Portal", layout="wide")

# Custom 3D & Modern Glassmorphism CSS Styling with Truck/Logistics Vibe
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 30px;
        border-radius: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0,0,0,0.35);
        border-bottom: 5px solid #ff3b30;
        margin-bottom: 25px;
    }
    .main-header h1 { 
        margin: 0; 
        font-size: 32px; 
        font-weight: 800; 
        letter-spacing: 1px;
        color: #ffffff;
    }
    .main-header p { 
        margin: 10px 0 0 0; 
        font-size: 16px; 
        color: #ffcc00; 
        font-weight: 600; 
    }

    .card-3d {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1), inset 0 1px 3px rgba(255,255,255,0.9);
        border: 1px solid rgba(255,255,255,0.6);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1>🚛 DELHIVERY – IDRFC6 DEWAS WAREHOUSE HUB 📦</h1>
        <p>⚡ Advanced Automated Logistics & Dispatch Management System &nbsp;|&nbsp; Managed by: RAJKUMAR</p>
    </div>
""", unsafe_allow_html=True)

DATA_FILE = "warehouse_entries.csv"
REPORT_FILE = "dispatch_reports.csv"
TRASH_FILE = "recycle_bin.csv"

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Task Type", "Courier", "Parcel Count"])

def save_data(df): df.to_csv(DATA_FILE, index=False)

def load_reports():
    if os.path.exists(REPORT_FILE):
        df = pd.read_csv(REPORT_FILE)
        expected_cols = ["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0 if col in ["Manifest", "Cancel", "Dispatch", "Return"] else "--:--"
        return df
    return pd.DataFrame(columns=["Date", "Courier", "In Time", "Out Time", "Manifest", "Cancel", "Dispatch", "Return", "Remark"])

def save_reports(df): df.to_csv(REPORT_FILE, index=False)

def load_trash():
    if os.path.exists(TRASH_FILE): return pd.read_csv(TRASH_FILE)
    return pd.DataFrame(columns=["ID", "Date", "Timestamp", "Piklist No.", "Employee Name", "Task Type", "Courier", "Parcel Count", "Deleted Time"])

def save_trash(df): df.to_csv(TRASH_FILE, index=False)

if "data" not in st.session_state: st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state: st.session_state["dispatch_reports"] = load_reports()
if "trash_data" not in st.session_state: st.session_state["trash_data"] = load_trash()
if "admin_logged" not in st.session_state: st.session_state["admin_logged"] = False

couriers_list = ["Delhivery", "Shadowfax", "ATS", "Xpressbees", "DTDC", "Bluedart", "Ekart"]

# ================= SIDEBAR CONTROL CENTER =================
st.sidebar.markdown("### ⚙️ Control Center")
selected_date = st.sidebar.date_input("Working Date", date.today())
selected_date_str = str(selected_date)
yesterday_str = str(selected_date - timedelta(days=1))

nav_page = st.sidebar.radio("Navigation Menu", ["🏠 Home Entry Portal", "📊 Analytics & Return/Dispatch Reports", "♻️ Admin & Recycle Bin"])

# Admin Authentication Section in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 Admin Security Panel")
ADMIN_PASSWORD = "123"  # Aap yahan apna password badal sakte hain

if not st.session_state["admin_logged"]:
    entered_pass = st.sidebar.text_input("Enter Admin Password", type="password")
    if st.sidebar.button("Unlock Admin Mode"):
        if entered_pass == ADMIN_PASSWORD:
            st.session_state["admin_logged"] = True
            st.sidebar.success("Admin Mode Unlocked!")
            st.rerun()
        else:
            st.sidebar.error("Wrong Password!")
else:
    st.sidebar.success("🔓 Admin Mode Active")
    if st.sidebar.button("Lock Admin Mode"):
        st.session_state["admin_logged"] = False
        st.rerun()

# ================= HOME PAGE PORTAL =================
if nav_page == "🏠 Home Entry Portal":
    st.markdown("""
        <div class="card-3d" style="background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 100%); border-left: 6px solid #ff3b30;">
            <h3>👋 Welcome to IDRFC6 Dewas Dashboard</h3>
            <p style="color: #555; margin-bottom: 0;">Yahan se aap naye piklist entries aur manifest boxes darj kar sakte hain.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.4], gap="large")
    
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

        if st.button("💾 Submit Entry Now", use_container_width=True):
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
                            "Manifest": [int(parcel_count)], "Cancel": [0], "Dispatch": [0], "Return": [0], "Remark": ["Auto Logged"]
                        })
                        st.session_state["dispatch_reports"] = pd.concat([rep_df, new_rep], ignore_index=True)
                    save_reports(st.session_state["dispatch_reports"])
                
                new_row = pd.DataFrame({
                    "ID": [str(pd.Timestamp.now().timestamp())],
                    "Date": [selected_date_str],
                    "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Piklist No.": [str(piklist_no)],
                    "Employee Name": [emp_name],
                    "Task Type": [task_type],
                    "Courier": [courier],
                    "Parcel Count": [int(parcel_count)]
                })
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                save_data(st.session_state["data"])

                st.success(f"Entry Saved Successfully!\n\n🕒 Mobile In-Time: **{auto_in_time}**")
                st.rerun()

    with col2:
        st.markdown("<div class='card-3d'><h3>📊 Today's Live Records (" + selected_date_str + ")</h3></div>", unsafe_allow_html=True)
        df = st.session_state["data"]
        df_f = df[df["Date"] == selected_date_str] if not df.empty else pd.DataFrame()
        
        if not df_f.empty:
            st.dataframe(df_f[["ID", "Piklist No.", "Employee Name", "Task Type", "Courier", "Parcel Count"]], use_container_width=True)
            
            # Admin Delete Option for Today's Entries
            if st.session_state["admin_logged"]:
                st.markdown("#### 🗑️ Admin Action: Delete Specific Entry")
                del_id = st.selectbox("Select Entry ID to Delete", df_f["ID"].astype(str).tolist())
                if st.button("Delete Selected Entry"):
                    target_row = df[df["ID"].astype(str) == del_id]
                    if not target_row.empty:
                        # Move to trash
                        trash_row = target_row.copy()
                        trash_row["Deleted Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state["trash_data"] = pd.concat([st.session_state["trash_data"], trash_row], ignore_index=True)
                        save_trash(st.session_state["trash_data"])
                        
                        # Remove from main data
                        st.session_state["data"] = df[df["ID"].astype(str) != del_id]
                        save_data(st.session_state["data"])
                        st.success("Entry deleted and moved to Recycle Bin successfully!")
                        st.rerun()
        else:
            st.info("📦 Aaj ke din abhi tak koi entry darj nahi ki gayi hai.")

# ================= REPORTS & ANALYTICS PAGE =================
elif nav_page == "📊 Analytics & Return/Dispatch Reports":
    st.markdown("<div class='card-3d'><h3>🚚 Dispatch, Cancel & Return Parcel Report Hub</h3></div>", unsafe_allow_html=True)
    rep_df = st.session_state["dispatch_reports"]
    
    with st.form("auto_time_form"):
        sel_courier = st.selectbox("Select Courier", couriers_list)
        curr_row = rep_df[(rep_df["Date"] == selected_date_str) & (rep_df["Courier"] == sel_courier)]
        
        default_in = datetime.now().strftime("%I:%M %p")
        if not curr_row.empty and pd.notna(curr_row["In Time"].values[0]) and curr_row["In Time"].values[0] != "--:--":
            default_in = curr_row["In Time"].values[0]
            
        c_dispatch = st.number_input("Dispatch Boxes (Bheje Gaye)", min_value=0, value=int(curr_row["Dispatch"].values[0]) if not curr_row.empty and "Dispatch" in curr_row.columns else 0)
        c_cancel = st.number_input("Cancel Boxes (Radd Kiye Gaye)", min_value=0, value=int(curr_row["Cancel"].values[0]) if not curr_row.empty and "Cancel" in curr_row.columns else 0)
        c_return = st.number_input("Return Boxes (Wapas Aaye Hue)", min_value=0, value=int(curr_row["Return"].values[0]) if not curr_row.empty and "Return" in curr_row.columns else 0)
        c_remark = st.text_input("Remark / Notes", value=str(curr_row["Remark"].values[0]) if not curr_row.empty and pd.notna(curr_row["Remark"].values[0]) else "")
        
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
            st.success("Report Saved Successfully!")
            st.rerun()

    current_day_rep = rep_df[rep_df["Date"] == selected_date_str] if not rep_df.empty else pd.DataFrame()
    
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
        
    st.markdown("#### 📋 Final Status Summary Table")
    st.dataframe(pd.DataFrame(display_summary_rows), use_container_width=True)

# ================= ADMIN & RECYCLE BIN PAGE =================
elif nav_page == "♻️ Admin & Recycle Bin":
    st.markdown("<div class='card-3d'><h3>♻️ Admin Recycle Bin & Data Management</h3></div>", unsafe_app_html=True)
    
    if not st.session_state["admin_logged"]:
        st.warning("🔒 Yeh section sirf Admin ke liye locked hai. Kripya sidebar mein password dalkar Admin Mode unlock karein (Default Password: `123`).")
    else:
        st.success("✅ Admin Access Granted. Aap yahan deleted entries dekh sakte hain aur unhe wapas restore kar sakte hain.")
        
        trash_df = st.session_state["trash_data"]
        if not trash_df.empty:
            st.markdown("#### 🗑️ Deleted Entries (Recycle Bin)")
            st.dataframe(trash_df, use_container_width=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("♻️ Restore All Deleted Data"):
                    st.session_state["data"] = pd.concat([st.session_state["data"], trash_df.drop(columns=["Deleted Time"])], ignore_index=True)
                    save_data(st.session_state["data"])
                    st.session_state["trash_data"] = pd.DataFrame(columns=trash_df.columns)
                    save_trash(st.session_state["trash_data"])
                    st.success("Saari entries successfully restore ho gayi hain!")
                    st.rerun()
            with col_b2:
                if st.button("🔥 Empty Recycle Bin Permanently"):
                    st.session_state["trash_data"] = pd.DataFrame(columns=trash_df.columns)
                    save_trash(st.session_state["trash_data"])
                    st.warning("Recycle bin khali kar di gayi hai!")
                    st.rerun()
        else:
            st.info("♻️ Recycle Bin bilkul khali hai. Koi bhi deleted entry nahi hai.")
