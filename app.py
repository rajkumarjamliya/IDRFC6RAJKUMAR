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

# CSS STYLING
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


def auto_backup():
    today_str = str(date.today())
    if os.path.exists(DATA_FILE):
        pd.read_csv(DATA_FILE).to_csv(
            os.path.join(BACKUP_DIR, f"backup_entries_{today_str}.csv"),
            index=False,
        )
    if os.path.exists(REPORT_FILE):
        pd.read_csv(REPORT_FILE).to_csv(
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


def load_employees():
    # Naye 4 Employee ID and Names (Aapki list ke anusar)
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
    # File rewrite karke naye name enforce karein
    default_emp.to_csv(EMP_FILE, index=False)
    return default_emp


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


# Session States Init
if "data" not in st.session_state:
    st.session_state["data"] = load_data()
if "dispatch_reports" not in st.session_state:
    st.session_state["dispatch_reports"] = load_reports()
if "employees" not in st.session_state:
    st.session_state["employees"] = load_employees()
if "couriers" not in st.session_state:
    st.session_state["couriers"] = load_couriers()
if "admin_logged" not in st.session_state:
    st.session_state["admin_logged"] = False

# Main Header Banner
st.markdown(
    """
<div class="main-header">
    <h1>🚛 DELHIVERY – IDRFC6 DEWAS LOGISTICS PORTAL 📦</h1>
    <p>⚡ Manual Box Counting & Live Editable Summary Portal | Admin: RAJKUMAR</p>
</div>
""",
    unsafe_allow_html=True,
)

# Navigation & Dates
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

# Admin Pass
st.sidebar.markdown("---")
ADMIN_PASSWORD = "123654"
if not st.session_state["admin_logged"]:
    entered_pass = st.sidebar.text_input("Admin Password", type="password")
    if st.sidebar.button("Unlock Admin"):
        if entered_pass == ADMIN_PASSWORD:
            st.session_state["admin_logged"] = True
            st.rerun()
        else:
            st.sidebar.error("Wrong Password!")

# PAGE 1: HOME MANUAL ENTRY
if nav_page == "🏠 Home Manual Entry":
    st.markdown(
        """
    <div class="card-3d" style="border-left: 5px solid #ff3b30;">
        <h3 style="margin:0;">📝 Task & Manifest Entry Form</h3>
        <p style="color:#555; margin:0;">Manifest chunne par hi Courier aur Box Count ka option dikhega.</p>
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
        emp_options = [
            f"{row['Employee Name']} ({row['Employee ID']})"
            for _, row in emp_df.iterrows()
        ]
        selected_emp_str = st.selectbox(
            "Select Employee", ["-- Select Employee --"] + emp_options
        )

        emp_id_val = ""
        emp_name_val = ""
        if selected_emp_str != "-- Select Employee --":
            emp_name_val = selected_emp_str.split(" (")[0]
            emp_id_val = selected_emp_str.split("(")[1].replace(")", "")

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

        courier_val = "N/A"
        box_count_val = 0

        # SIRF MANIFEST CHUNNE PAR HI BOX AND COURIER SHOW HOGA
        if task_type == "Manifest":
            st.markdown("---")
            st.subheader("🚚 Courier & Manifest Details")
            courier_val = st.selectbox(
                "Courier Name", st.session_state["couriers"]
            )
            box_count_val = st.number_input(
                "Manifest Box Count", min_value=1, value=1, step=1
            )

        if st.button("💾 Save Entry", use_container_width=True):
            if piklist_no and emp_id_val:
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                new_entry = pd.DataFrame(
                    {
                        "ID": [str(pd.Timestamp.now().timestamp())],
                        "Date": [selected_date_str],
                        "Timestamp": [current_timestamp],
                        "Piklist No.": [str(piklist_no)],
                        "Employee ID": [emp_id_val],
                        "Employee Name": [emp_name_val],
                        "Task Type": [task_type],
                        "Courier": [courier_val],
                        "Parcel Count": [int(box_count_val)],
                    }
                )

                st.session_state["data"] = pd.concat(
                    [st.session_state["data"], new_entry], ignore_index=True
                )
                save_data(st.session_state["data"])

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
                st.error("Piklist No. and Employee select karein!")

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
            st.info("Aaj abhi tak koi entry nahi hui.")
        st.markdown("</div>", unsafe_allow_html=True)

    # DIRECT EDITABLE SUMMARY TABLE (NO SEPARATE INPUTS BELOW)
    st.markdown("---")
    st.markdown(
        f"<div class='card-3d'><h3>📊 Interactive Editable Summary Table ({display_date_str})</h3><p style='margin:0; color:#666;'>Table me hi direct Click karke Time, Vehicle No, Manifest, Cancel, Dispatch edit karein:</p></div>",
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

        summary_rows.append(
            {
                "Courier": c,
                "In Time": in_t,
                "Out Time": out_t,
                "Manifest": man,
                "Cancel": can,
                "Dispatch": dis,
                "Pending": pend,
                "Vehicle No": veh,
                "Remark": rem,
            }
        )

    summary_df = pd.DataFrame(summary_rows)

    # Direct Data Editor in Streamlit
    edited_df = st.data_editor(
        summary_df,
        disabled=["Courier", "Pending"],  # Calculated columns lock rahenge
        column_config={
            "Manifest": st.column_config.NumberColumn(min_value=0, step=1),
            "Cancel": st.column_config.NumberColumn(min_value=0, step=1),
            "Dispatch": st.column_config.NumberColumn(min_value=0, step=1),
        },
        use_container_width=True,
        num_rows="fixed",
    )

    if st.button("💾 Save Table Changes", use_container_width=True):
        for _, row in edited_df.iterrows():
            c_name = row["Courier"]
            curr_row = rep_df[
                (rep_df["Date"] == selected_date_str)
                & (rep_df["Courier"] == c_name)
            ]

            if not curr_row.empty:
                idx = curr_row.index[0]
                rep_df.loc[idx, "In Time"] = row["In Time"]
                rep_df.loc[idx, "Out Time"] = row["Out Time"]
                rep_df.loc[idx, "Manifest"] = int(row["Manifest"])
                rep_df.loc[idx, "Cancel"] = int(row["Cancel"])
                rep_df.loc[idx, "Dispatch"] = int(row["Dispatch"])
                rep_df.loc[idx, "Vehicle No"] = row["Vehicle No"]
                rep_df.loc[idx, "Remark"] = row["Remark"]
            else:
                new_r = pd.DataFrame(
                    {
                        "Date": [selected_date_str],
                        "Courier": [c_name],
                        "In Time": [row["In Time"]],
                        "Out Time": [row["Out Time"]],
                        "Manifest": [int(row["Manifest"])],
                        "Cancel": [int(row["Cancel"])],
                        "Dispatch": [int(row["Dispatch"])],
                        "Return": [0],
                        "Vehicle No": [row["Vehicle No"]],
                        "Remark": [row["Remark"]],
                    }
                )
                rep_df = pd.concat([rep_df, new_r], ignore_index=True)

        st.session_state["dispatch_reports"] = rep_df
        save_reports(rep_df)
        st.success("Summary Table Changes Saved Successfully!")
        st.rerun()

    # WHATSAPP REPORT GENERATION
    tot_man = edited_df["Manifest"].sum()
    tot_can = edited_df["Cancel"].sum()
    tot_dis = edited_df["Dispatch"].sum()
    tot_pend = edited_df["Pending"].sum()

    wa_text = f"🟨 *{display_date_str}*\n\n"
    wa_text += f"{'Courier':<12} | {'Man':<5} | {'Can':<4} | {'Dis':<5} | {'Pend':<4} | {'Gadi/Time'}\n"
    wa_text += "--------------------------------------------------------\n"

    for _, row in edited_df.iterrows():
        c_name = row["Courier"]
        m_val = str(row["Manifest"]) if row["Manifest"] != 0 else ""
        c_val = str(row["Cancel"]) if row["Cancel"] != 0 else ""
        d_val = str(row["Dispatch"]) if row["Dispatch"] != 0 else ""
        p_val = str(row["Pending"]) if row["Pending"] != 0 else ""
        v_val = str(row["Vehicle No"]) if row["Vehicle No"] != "--" else ""
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
                📲 1-Click Share Table Report on WhatsApp
            </button>
        </a>
    """,
        unsafe_allow_html=True,
    )

# PAGE 2: EMPLOYEE WORK REPORT
elif nav_page == "📊 Employee Work Report":
    st.markdown(
        "<div class='card-3d'><h3>📊 Employee Work Report</h3></div>",
        unsafe_allow_html=True,
    )
    df_all = st.session_state["data"]
    df_date = (
        df_all[df_all["Date"] == selected_date_str]
        if not df_all.empty
        else pd.DataFrame()
    )

    if not df_date.empty:
        emp_summary = (
            df_date.groupby(["Employee ID", "Employee Name", "Task Type"])
            .agg({"Parcel Count": "sum", "Piklist No.": "count"})
            .reset_index()
            .rename(columns={"Piklist No.": "Total Piklists Entries"})
        )
        st.dataframe(emp_summary, use_container_width=True)
    else:
        st.info("No work record found for today.")

# PAGE 3: ADMIN SETUP
elif nav_page == "🔐 Admin & Master Setup":
    st.markdown(
        "<div class='card-3d'><h3>🔐 Master Setup</h3></div>",
        unsafe_allow_html=True,
    )
    if st.session_state["admin_logged"]:
        st.dataframe(st.session_state["employees"], use_container_width=True)
    else:
        st.warning("Unlock Admin from sidebar.")
