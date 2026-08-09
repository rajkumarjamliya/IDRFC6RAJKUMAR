from datetime import date, datetime, timedelta
import os
import urllib.parse
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="DELHIVERY – IDRFC6 DEWAS Manual Logistics Portal", layout="wide"
)

# File Paths
DATA_FILE = "warehouse_entries.csv"
REPORT_FILE = "dispatch_reports.csv"
TRASH_FILE = "recycle_bin.csv"
EMP_FILE = "employees_master.csv"
COURIER_FILE = "couriers_master.csv"
BACKUP_DIR = "backups"

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# ================= CSS STYLING =================
st.markdown(
    """
 <style>
 .stApp {
     background: linear-gradient(135deg, #eef2f3 0%, #8e9eab 100%);
     font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
 }
 .main-header {
     background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
     padding: 20px;
     border-radius: 12px;
     color: white;
     text-align: center;
     box-shadow: 0 6px 15px rgba(0,0,0,0.2);
     border-bottom: 4px solid #ff3b30;
     margin-bottom: 20px;
 }
 .main-header h1 { margin: 0; font-size: 26px; font-weight: 800; color: #ffffff; }
 .main-header p { margin: 5px 0 0 0; font-size: 14px; color: #ffcc00; font-weight: 600; }
 .card-3d {
     background: rgba(255, 255, 255, 0.95);
     padding: 18px;
     border-radius: 12px;
     box-shadow: 0 6px 15px rgba(0,0,0,0.08);
     border: 1px solid rgba(255,255,255,0.8);
     margin-bottom: 15px;
 }
 </style>
 """,
    unsafe_allow_html=True,
)


# ================= DATA LOADERS & AUTO-BACKUP =================
def auto_backup():
    today_str = str(date.today())
    if os.path.exists(DATA_FILE):
        df_d = pd.read_csv(DATA_FILE)
        df_d.to_csv(
            os.path.join(BACKUP_DIR, f"backup_entries_{today_str}.csv"),
            index=False,
        )
    if os.path.exists(REPORT_FILE):
        df_r = pd.read_csv(REPORT_FILE)
        df_r.to_csv(
            os.path.join(BACKUP_DIR, f"backup_reports_{today_str}.csv"),
            index=False,
        )


def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(
        columns=[
            "ID",
            "Date",
            "Timestamp",
            "Piklist No.",
            "Employee ID",
            "Employee Name",
            "Task Type",
            "Courier",
            "Parcel Count",
        ]
    )


def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    auto_backup()


def load_reports():
    if os.path.exists(REPORT_FILE):
        df = pd.read_csv(REPORT_FILE)
        expected_cols = [
            "Date",
            "Courier",
            "In Time",
            "Out Time",
            "Manifest",
            "Cancel",
            "Dispatch",
            "Return",
            "Vehicle No",
            "Remark",
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = (
                    0
                    if col in ["Manifest", "Cancel", "Dispatch", "Return"]
                    else "--"
                )
        return df
    return pd.DataFrame(
        columns=[
            "Date",
            "Courier",
            "In Time",
            "Out Time",
            "Manifest",
            "Cancel",
            "Dispatch",
            "Return",
            "Vehicle No",
            "Remark",
        ]
    )


def save_reports(df):
    df.to_csv(REPORT_FILE, index=False)
    auto_backup()


def load_trash():
    if os.path.exists(TRASH_FILE):
        return pd.read_csv(TRASH_FILE)
    return pd.DataFrame()


def save_trash(df):
    df.to_csv(TRASH_FILE, index=False)


def load_employees():
    # Naye employees ki default list (Purane naam hata diye gaye hain)
    default_emp = pd.DataFrame(
        {
            "Employee ID": ["W222449", "W224500", "W225396", "W225403"],
            "Employee Name": [
                "AJAY PATEL",
                "PANKAJ PATEL",
                "KAMLESH MANDOI",
                "ABHISHEK PATEL",
            ],
        }
    )
    if not os.path.exists(EMP_FILE):
        default_emp.to_csv(EMP_FILE, index=False)
        return default_emp
    return pd.read_csv(EMP_FILE)


def save_employees(df):
    df.to_csv(EMP_FILE, index=False)


def load_couriers():
    if os.path.exists(COURIER_FILE):
        return pd.read_csv(COURIER_FILE)["Courier Name"].tolist()
    default_couriers = [
        "Delhivery",
        "Shadowfax",
        "ATS",
        "Xpressbees",
        "DTDC",
        "Bluedart",
        "Ekart",
    ]
    pd.DataFrame({"Courier Name": default_couriers}).to_csv(
        COURIER_FILE, index=False
    )
    return default_couriers


def save_couriers(courier_list):
    pd.DataFrame({"Courier Name": courier_list}).to_csv(
        COURIER_FILE, index=False
    )


# Session States
if "data" not in st.session_state:
    st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state:
    st.session_state["dispatch_reports"] = load_reports()
if "trash_data" not in st.session_state:
    st.session_state["trash_data"] = load_trash()
if "admin_logged" not in st.session_state:
    st.session_state["admin_logged"] = False
if "employees" not in st.session_state:
    st.session_state["employees"] = load_employees()
if "couriers" not in st.session_state:
    st.session_state["couriers"] = load_couriers()

# Main Header Banner
st.markdown(
    """
<div class="main-header">
    <h1>🚛 DELHIVERY – IDRFC6 DEWAS LOGISTICS PORTAL 📦</h1>
    <p>⚡ Manual Box Counting, Task & Courier Management System | Admin: RAJKUMAR</p>
</div>
""",
    unsafe_allow_html=True,
)

# ================= SIDEBAR NAVIGATION =================
st.sidebar.markdown("### ⚙️ Control Menu")
selected_date = st.sidebar.date_input("Working Date", date.today())
selected_date_str = str(selected_date)
display_date_str = selected_date.strftime("%d/%m/%Y")
yesterday_str = str(selected_date - timedelta(days=1))

nav_page = st.sidebar.radio(
    "Navigation Menu",
    [
        "🏠 Home Manual Entry",
        "📊 Employee Work Report",
        "🔐 Admin & Master Setup",
    ],
)

# Sidebar Admin Authentication
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 Admin Authentication")
ADMIN_PASSWORD = "123654"

if not st.session_state["admin_logged"]:
    entered_pass = st.sidebar.text_input("Enter Password", type="password")
    if st.sidebar.button("Unlock Admin", use_container_width=True):
        if entered_pass == ADMIN_PASSWORD:
            st.session_state["admin_logged"] = True
            st.sidebar.success("Admin Active!")
            st.rerun()
        else:
            st.sidebar.error("Galat Password!")
else:
    st.sidebar.success("🔓 Admin Mode Active")
    if st.sidebar.button("Lock Admin", use_container_width=True):
        st.session_state["admin_logged"] = False
        st.rerun()


# ================= PAGE 1: HOME MANUAL ENTRY =================
if nav_page == "🏠 Home Manual Entry":
    st.markdown(
        """
    <div class="card-3d" style="border-left: 5px solid #ff3b30;">
        <h3 style="margin:0;">📝 Task & Manifest Entry Form</h3>
        <p style="color:#555; margin:0;">Piklist & Employee select karein. Manifest chunne par hi Courier aur Box Count open hoga.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.1, 1.4], gap="large")

    with col1:
        st.markdown(
            "<div class='card-3d'><h4>📌 Enter Details</h4>",
            unsafe_allow_html=True,
        )

        piklist_no = st.text_input(
            "Piklist Number", placeholder="e.g. PKL-8890"
        )

        emp_df = st.session_state["employees"]
        emp_names = emp_df["Employee Name"].tolist()
        selected_emp = st.selectbox(
            "Select Employee Name", ["-- Select Employee --"] + emp_names
        )

        emp_id_val = ""
        if selected_emp != "-- Select Employee --":
            emp_id_val = emp_df[emp_df["Employee Name"] == selected_emp][
                "Employee ID"
            ].values[0]
            st.info(f"👤 **ID:** `{emp_id_val}` | **Name:** `{selected_emp}`")

        task_type = st.selectbox(
            "Select Task / Work Type",
            [
                "Picking",
                "Packing",
                "Scanning",
                "Gadi Loading",
                "Gadi Unloading",
                "Inventory Work",
                "Manifest",
            ],
        )

        # SIRF MANIFEST CHUNNE PAR HI COURIER AUR BOX COUNT OPTION KHULEGA
        courier_val = "N/A"
        box_count_val = 0

        if task_type == "Manifest":
            st.markdown("---")
            st.subheader("🚚 Courier & Manifest Details")
            courier_val = st.selectbox(
                "Courier Name", st.session_state["couriers"]
            )
            box_count_val = st.number_input(
                "Manifest Box Count (सँख्या)", min_value=1, value=1, step=1
            )

        if st.button("💾 Save Entry", use_container_width=True):
            if (
                piklist_no
                and selected_emp != "-- Select Employee --"
                and emp_id_val
            ):
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                new_entry = pd.DataFrame(
                    {
                        "ID": [str(pd.Timestamp.now().timestamp())],
                        "Date": [selected_date_str],
                        "Timestamp": [current_timestamp],
                        "Piklist No.": [str(piklist_no)],
                        "Employee ID": [emp_id_val],
                        "Employee Name": [selected_emp],
                        "Task Type": [task_type],
                        "Courier": [courier_val],
                        "Parcel Count": [int(box_count_val)],
                    }
                )

                st.session_state["data"] = pd.concat(
                    [st.session_state["data"], new_entry], ignore_index=True
                )
                save_data(st.session_state["data"])

                # Manifest Box Auto Update in Dispatch Report
                if task_type == "Manifest" and courier_val != "N/A":
                    rep_df = st.session_state["dispatch_reports"]
                    ex = rep_df[
                        (rep_df["Date"] == selected_date_str)
                        & (rep_df["Courier"] == courier_val)
                    ]

                    if not ex.empty:
                        idx = ex.index[0]
                        rep_df.loc[idx, "Manifest"] += int(box_count_val)
                    else:
                        new_rep = pd.DataFrame(
                            {
                                "Date": [selected_date_str],
                                "Courier": [courier_val],
                                "In Time": ["--"],
                                "Out Time": ["--"],
                                "Manifest": [int(box_count_val)],
                                "Cancel": [0],
                                "Dispatch": [0],
                                "Return": [0],
                                "Vehicle No": ["--"],
                                "Remark": [""],
                            }
                        )
                        rep_df = pd.concat([rep_df, new_rep], ignore_index=True)

                    st.session_state["dispatch_reports"] = rep_df
                    save_reports(rep_df)

                st.success("Entry Saved Successfully!")
                st.rerun()
            else:
                st.error("Piklist No. aur Employee Name chunna zaroori hai!")

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"<div class='card-3d'><h4>📋 Live Task Table ({selected_date_str})</h4>",
            unsafe_allow_html=True,
        )

        df = st.session_state["data"]
        df_today = (
            df[df["Date"] == selected_date_str] if not df.empty else pd.DataFrame()
        )

        if not df_today.empty:
            st.dataframe(
                df_today[
                    [
                        "Timestamp",
                        "Piklist No.",
                        "Employee ID",
                        "Employee Name",
                        "Task Type",
                        "Courier",
                        "Parcel Count",
                    ]
                ],
                use_container_width=True,
                height=260,
            )
        else:
            st.info("Aaj abhi tak koi task entry darj nahi hui hai.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ================= SUMMARY TABLE & COURIER TIMING HUB =================
    st.markdown("---")
    st.markdown(
        f"<div class='card-3d'><h3>📊 Dispatch Summary Table ({display_date_str})</h3></div>",
        unsafe_allow_html=True,
    )

    rep_df = st.session_state["dispatch_reports"]

    current_day_rep = (
        rep_df[rep_df["Date"] == selected_date_str]
        if not rep_df.empty
        else pd.DataFrame()
    )
    yest_rep_view = (
        rep_df[rep_df["Date"] == yesterday_str]
        if not rep_df.empty
        else pd.DataFrame()
    )

    summary_rows = []
    tot_man = tot_can = tot_dis = tot_pend = 0

    for c in st.session_state["couriers"]:
        c_yest = (
            yest_rep_view[yest_rep_view["Courier"] == c]
            if not yest_rep_view.empty
            else pd.DataFrame()
        )
        y_pend = (
            max(
                0,
                int(c_yest["Manifest"].values[0])
                - int(c_yest["Cancel"].values[0])
                - int(c_yest["Dispatch"].values[0]),
            )
            if not c_yest.empty
            else 0
        )

        c_curr = (
            current_day_rep[current_day_rep["Courier"] == c]
            if not current_day_rep.empty
            else pd.DataFrame()
        )

        in_t = (
            str(c_curr["In Time"].values[0])
            if not c_curr.empty and pd.notna(c_curr["In Time"].values[0])
            else "--"
        )
        out_t = (
            str(c_curr["Out Time"].values[0])
            if not c_curr.empty and pd.notna(c_curr["Out Time"].values[0])
            else "--"
        )
        man = int(c_curr["Manifest"].values[0]) if not c_curr.empty else 0
        can = int(c_curr["Cancel"].values[0]) if not c_curr.empty else 0
        dis = int(c_curr["Dispatch"].values[0]) if not c_curr.empty else 0
        veh = (
            str(c_curr["Vehicle No"].values[0])
            if not c_curr.empty and "Vehicle No" in c_curr.columns
            else "--"
        )
        rem = (
            str(c_curr["Remark"].values[0])
            if not c_curr.empty and "Remark" in c_curr.columns
            else ""
        )

        pend = max(0, (man + y_pend) - can - dis)

        tot_man += man
        tot_can += can
        tot_dis += dis
        tot_pend += pend

        summary_rows.append(
            {
                "Courier": c,
                "In Time": in_t,
                "Out Time": out_t,
                "Manifest": man,
                "Cancel": can if can > 0 else "",
                "Dispatch": dis,
                "Pending": pend if pend > 0 else "",
                "Vehicle No": veh,
                "Remark": rem,
            }
        )

    summary_df = pd.DataFrame(summary_rows)

    st.dataframe(summary_df, use_container_width=True)

    # SUMMARY TABLE EDIT OPTION
    st.markdown("#### ✏️ Direct Edit Summary Details")
    col_ed1, col_ed2, col_ed3, col_ed4 = st.columns(4)

    with col_ed1:
        edit_cour = st.selectbox(
            "Select Courier to Edit",
            st.session_state["couriers"],
            key="edit_summary_cour",
        )
    with col_ed2:
        in_t_input = st.text_input("In Time (e.g. 10:30 AM)", placeholder="--")
        out_t_input = st.text_input("Out Time (e.g. 06:00 PM)", placeholder="--")
    with col_ed3:
        veh_input = st.text_input("Gadi No.", placeholder="e.g. MP-09-1234")
        rem_input = st.text_input("Remark", placeholder="Optional remark")
    with col_ed4:
        man_input = st.number_input("Manifest Count", min_value=0, value=0)
        dis_input = st.number_input("Dispatch Count", min_value=0, value=0)
        can_input = st.number_input("Cancel Count", min_value=0, value=0)

    if st.button("🔄 Update Summary Record", use_container_width=True):
        curr_row = rep_df[
            (rep_df["Date"] == selected_date_str)
            & (rep_df["Courier"] == edit_cour)
        ]
        if not curr_row.empty:
            idx = curr_row.index[0]
            if in_t_input:
                rep_df.loc[idx, "In Time"] = in_t_input
            if out_t_input:
                rep_df.loc[idx, "Out Time"] = out_t_input
            if veh_input:
                rep_df.loc[idx, "Vehicle No"] = veh_input
            if rem_input:
                rep_df.loc[idx, "Remark"] = rem_input
            if man_input > 0:
                rep_df.loc[idx, "Manifest"] = int(man_input)
            if dis_input > 0:
                rep_df.loc[idx, "Dispatch"] = int(dis_input)
            if can_input > 0:
                rep_df.loc[idx, "Cancel"] = int(can_input)
        else:
            new_r = pd.DataFrame(
                {
                    "Date": [selected_date_str],
                    "Courier": [edit_cour],
                    "In Time": [in_t_input if in_t_input else "--"],
                    "Out Time": [out_t_input if out_t_input else "--"],
                    "Manifest": [int(man_input)],
                    "Cancel": [int(can_input)],
                    "Dispatch": [int(dis_input)],
                    "Return": [0],
                    "Vehicle No": [veh_input if veh_input else "--"],
                    "Remark": [rem_input],
                }
            )
            rep_df = pd.concat([rep_df, new_r], ignore_index=True)

        st.session_state["dispatch_reports"] = rep_df
        save_reports(rep_df)
        st.success(f"{edit_cour} Record Updated Successfully!")
        st.rerun()

    # WHATSAPP REPORT FORMAT
    wa_text = f"🟨 *{display_date_str}*\n\n"
    wa_text += f"{'Courier':<12} | {'Man':<5} | {'Can':<4} | {'Dis':<5} | {'Pend':<4} | {'Gadi/Time'}\n"
    wa_text += "--------------------------------------------------------\n"

    for row in summary_rows:
        c_name = row["Courier"]
        m_val = str(row["Manifest"]) if row["Manifest"] != 0 else ""
        c_val = str(row["Cancel"])
        d_val = str(row["Dispatch"]) if row["Dispatch"] != 0 else ""
        p_val = str(row["Pending"])
        v_val = row["Vehicle No"] if row["Vehicle No"] != "--" else ""
        t_val = (
            f"({row['In Time']}-{row['Out Time']})"
            if row["In Time"] != "--"
            else ""
        )

        wa_text += f"{c_name:<12} | {m_val:<5} | {c_val:<4} | {d_val:<5} | {p_val:<4} | {v_val} {t_val}\n"

    wa_text += "--------------------------------------------------------\n"
    wa_text += f"*Total*        | *{tot_man}*   | *{tot_can}*  | *{tot_dis}*   | *{tot_pend}*\n"

    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"

    st.markdown("---")
    st.markdown(
        f"""
        <a href="{wa_url}" target="_blank">
            <button style="background-color: #25D366; color: white; border: none; padding: 14px 28px; font-size: 18px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%;">
                📲 1-Click Share Table Report on WhatsApp Group
            </button>
        </a>
    """,
        unsafe_allow_html=True,
    )


# ================= PAGE 2: EMPLOYEE WORK REPORT =================
elif nav_page == "📊 Employee Work Report":
    st.markdown(
        "<div class='card-3d'><h3>📊 Employee Work & Box Count Report</h3></div>",
        unsafe_allow_html=True,
    )

    df_all = st.session_state["data"]
    df_date = (
        df_all[df_all["Date"] == selected_date_str]
        if not df_all.empty
        else pd.DataFrame()
    )

    if not df_date.empty:
        st.markdown(
            f"#### 👥 Today's Work Report by Employee ({selected_date_str})"
        )

        emp_summary = (
            df_date.groupby(["Employee ID", "Employee Name", "Task Type"])
            .agg({"Parcel Count": "sum", "Piklist No.": "count"})
            .reset_index()
            .rename(columns={"Piklist No.": "Total Piklists Entries"})
        )

        st.dataframe(emp_summary, use_container_width=True)
    else:
        st.info("Selected date ke liye koi work entry nahi mili.")


# ================= PAGE 3: ADMIN & MASTER SETUP =================
elif nav_page == "🔐 Admin & Master Setup":
    st.markdown(
        "<div class='card-3d'><h3>🔐 Admin Security & Master Setup</h3></div>",
        unsafe_allow_html=True,
    )

    if not st.session_state["admin_logged"]:
        st.warning("🔒 Sidebar me Password `123654` dalkar Admin unlock karein.")
    else:
        tab_emp, tab_cour, tab_excel, tab_trash = st.tabs(
            [
                "👥 Employee Master",
                "🚚 Courier Master",
                "📥 Excel Download",
                "♻️ Recycle Bin",
            ]
        )

        with tab_emp:
            st.markdown("#### Add / Delete Employee")
            emp_df = st.session_state["employees"]
            col1, col2 = st.columns(2)
            with col1:
                e_id = st.text_input("Employee ID (e.g. W222449)")
                e_name = st.text_input("Employee Name")
                if st.button("➕ Add Employee"):
                    if e_id and e_name:
                        emp_df = pd.concat(
                            [
                                emp_df,
                                pd.DataFrame(
                                    {
                                        "Employee ID": [e_id],
                                        "Employee Name": [e_name],
                                    }
                                ),
                            ],
                            ignore_index=True,
                        )
                        st.session_state["employees"] = emp_df
                        save_employees(emp_df)
                        st.success("Employee Added!")
                        st.rerun()

            with col2:
                st.dataframe(emp_df, use_container_width=True)

        with tab_cour:
            st.markdown("#### Add / Delete Courier")
            c_name = st.text_input("New Courier Name")
            if st.button("➕ Add Courier"):
                if c_name and c_name not in st.session_state["couriers"]:
                    st.session_state["couriers"].append(c_name)
                    save_couriers(st.session_state["couriers"])
                    st.success("Courier Added!")
                    st.rerun()

        with tab_excel:
            st.markdown("#### 📥 Export Full Excel Sheet")
            exp_d = st.date_input("Select Date", date.today())
            exp_d_str = str(exp_d)

            if st.button("📊 Download Excel File"):
                fname = f"Logistics_Report_{exp_d_str}.xlsx"
                with pd.ExcelWriter(fname, engine="openpyxl") as writer:
                    st.session_state["data"][
                        st.session_state["data"]["Date"] == exp_d_str
                    ].to_excel(writer, sheet_name="Entries", index=False)
                    st.session_state["dispatch_reports"][
                        st.session_state["dispatch_reports"]["Date"] == exp_d_str
                    ].to_excel(
                        writer, sheet_name="Dispatch_Summary", index=False
                    )
                    st.session_state["employees"].to_excel(
                        writer, sheet_name="Employee_Master", index=False
                    )

                with open(fname, "rb") as f:
                    st.download_button(
                        "📥 Click Here to Download Excel",
                        data=f,
                        file_name=fname,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

        with tab_trash:
            st.dataframe(
                st.session_state["trash_data"], use_container_width=True
            )
