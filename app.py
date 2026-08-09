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
EMP_FILE = "employees_master.csv"
COURIER_FILE = "couriers_master.csv"
BACKUP_DIR = "backups"

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# ================= CSS STYLING (Web Design Look) =================
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
 /* WhatsApp Button Custom Styling */
 .wa-btn {
     display: flex;
     justify-content: center;
     align-items: center;
     background-color: #25D366;
     color: white;
     padding: 14px 28px;
     font-size: 18px;
     font-weight: bold;
     border-radius: 8px;
     text-decoration: none;
     margin-top: 20px;
     box-shadow: 0 4px 10px rgba(0,0,0,0.1);
     width: 100%;
 }
 .wa-btn:hover {
     background-color: #1ebe57;
     color: white;
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


def load_employees():
    # Fixed List ke anusar employees hardcoded hain
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
    # Hamesha file overwrite karein taaki names update rahein
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
    <p>⚡ Automated Warehouse, Task & Courier Management System | Admin: RAJKUMAR</p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar Navigation & Dates
st.sidebar.markdown("### ⚙️ Navigation & Date")
selected_date = st.sidebar.date_input("Working Date", date.today())
selected_date_str = str(selected_date)
display_date_str = selected_date.strftime("%d/%m/%Y")
yesterday_str = str(selected_date - timedelta(days=1))

nav_page = st.sidebar.radio(
    "Navigation Menu",
    [
        "🏠 Home Manual Entry",
        "📊 Employee Work Report",
        "🔐 Admin Setup",
    ],
)

# Admin Security Panel
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
    # UPDATE 1: NEW CARD DESIGN & Heading Name Change
    st.markdown(
        """
    <div class="card-3d" style="border-left: 5px solid #ff3b30; border-top: 1px solid #ff3b30;">
        <h3 style="margin:0; color: #ff3b30; font-weight: 800;">📝 DEWAS OPERATION TEAM - RAJKUMAR</h3>
        <p style="color:#555; margin:0; font-weight: 600;">Daily Task aur Manifest details type karke enter karein.</p>
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
            "Piklist No.", placeholder="Scan or Type Piklist No."
        )

        emp_df = st.session_state["employees"]
        emp_options = [
            f"{row['Employee Name']} ({row['Employee ID']})"
            for _, row in emp_df.iterrows()
        ]
        selected_emp_str = st.selectbox(
            "Select Employee Name", ["-- Select Employee --"] + emp_options
        )

        emp_id_val = ""
        emp_name_val = ""
        if selected_emp_str != "-- Select Employee --":
            emp_name_val = selected_emp_str.split(" (")[0]
            emp_id_val = selected_emp_str.split("(")[1].replace(")", "")
            st.info(f"👤 **ID:** `{emp_id_val}` | **Name:** `{emp_name_val}`")

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

        # Sirf Manifest select karne par hi Courier aur Box options dikhenge
        courier_val = "N/A"
        box_count_val = 0

        if task_type == "Manifest":
            st.markdown("---")
            st.subheader("🚚 Manifest Details")
            courier_val = st.selectbox(
                "Select Courier Company", st.session_state["couriers"]
            )
            box_count_val = st.number_input(
                "Manifest Box Count", min_value=1, value=10, step=1
            )

        if st.button("💾 Submit Work Entry", use_container_width=True):
            if (
                piklist_no
                and selected_emp_str != "-- Select Employee --"
                and emp_id_val
            ):
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Main Data Table me Save karein
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

                # Manifest hai toh Dispatch Report Table automatically update karein
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
                st.error("Piklist No. aur Employee select karna zaroori hai!")

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
            st.info("Aaj abhi tak koi entry logged nahi hai.")

        st.markdown("</div>", unsafe_allow_html=True)

    # DIRECT EDITABLE SUMMARY TABLE
    st.markdown("---")
    st.markdown(
        f"<div class='card-3d'><h3>📊 Interactive Dispatch Summary Table ({display_date_str})</h3><p style='margin:0; color:#666; font-weight:600;'>Table me cells par click karke details (Time, Gadi, Box Count) direct edit karein:</p></div>",
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
        # Yesterday Pending calculation
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

        # Dropdown options load karein agar exist karte hain
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

        # Pending Formula: Yesterday Pend + Today Manifest - Today Cancel - Today Dispatch
        pend = max(0, (man + y_pend) - can - dis)

        # Totals add karein WhatsApp aur Summary Display ke liye
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

    # UPDATE: Interactive Data Editor (Sirf Pending aur Courier lock hai)
    edited_df = st.data_editor(
        summary_df,
        disabled=["Courier", "Pending"],  # Calculated columns lock rakhein
        column_config={
            "Courier": st.column_config.TextColumn(width="medium"),
            "In Time": st.column_config.TextColumn(width="small"),
            "Out Time": st.column_config.TextColumn(width="small"),
            "Manifest": st.column_config.NumberColumn(
                min_value=0, step=1, format="%d"
            ),
            "Cancel": st.column_config.NumberColumn(
                min_value=0, step=1, format="%d"
            ),
            "Dispatch": st.column_config.NumberColumn(
                min_value=0, step=1, format="%d"
            ),
            "Pending": st.column_config.NumberColumn(format="%d"),
            "Vehicle No": st.column_config.TextColumn(width="medium"),
            "Remark": st.column_config.TextColumn(width="medium"),
        },
        use_container_width=True,
        num_rows="fixed",
    )

    # SAVE BUTTON: edited data ko main REPORT_FILE me save karein
    if st.button("💾 Save Table Changes", use_container_width=True):
        # Report table load karein taaki update kar sakein
        report_df = st.session_state["dispatch_reports"]

        # Har edited row ko report file me date-wise safe karein
        for _, row in edited_df.iterrows():
            c_name = row["Courier"]
            curr_rep_row = report_df[
                (report_df["Date"] == selected_date_str)
                & (report_df["Courier"] == c_name)
            ]

            if not curr_rep_row.empty:
                # Row exist karti hai toh modify karein
                idx = curr_rep_row.index[0]
                report_df.loc[idx, "In Time"] = row["In Time"]
                report_df.loc[idx, "Out Time"] = row["Out Time"]
                # Convert numbers (Cancel may be blank string initially)
                report_df.loc[idx, "Manifest"] = int(row["Manifest"])
                report_df.loc[idx, "Dispatch"] = int(row["Dispatch"])
                # Handle possible empty string from Cancel editor
                try:
                    report_df.loc[idx, "Cancel"] = int(row["Cancel"])
                except Exception:
                    report_df.loc[idx, "Cancel"] = 0
                report_df.loc[idx, "Vehicle No"] = row["Vehicle No"]
                report_df.loc[idx, "Remark"] = row["Remark"]
            else:
                # Naya record banayein date-wise
                try:
                    c_val = int(row["Cancel"])
                except Exception:
                    c_val = 0

                new_r = pd.DataFrame(
                    {
                        "Date": [selected_date_str],
                        "Courier": [c_name],
                        "In Time": [row["In Time"]],
                        "Out Time": [row["Out Time"]],
                        "Manifest": [int(row["Manifest"])],
                        "Cancel": [c_val],
                        "Dispatch": [int(row["Dispatch"])],
                        "Return": [0],
                        "Vehicle No": [row["Vehicle No"]],
                        "Remark": [row["Remark"]],
                    }
                )
                report_df = pd.concat([report_df, new_r], ignore_index=True)

        st.session_state["dispatch_reports"] = report_df
        save_reports(report_df)
        st.success("Summary Table changes saved successfully!")
        st.rerun()

    # Totals Recalculate based on current edited state for WhatsApp
    whatsapp_tot_man = edited_df["Manifest"].sum()
    # Cancel might be objects if blank strings used, handle during sum
    try:
        whatsapp_tot_can = edited_df["Cancel"].astype(int).sum()
    except Exception:
        whatsapp_tot_can = 0
    whatsapp_tot_dis = edited_df["Dispatch"].sum()
    whatsapp_tot_pend = edited_df["Pending"].sum()

    # UPDATE 2: professional Bada-Chadaker WhatsApp Report Formatting (image format)
    wa_text = f"*DEWAS OPERATION - DISPATCH REPORT*\n"
    wa_text += f"📅 *Date:* {display_date_str}\n\n"
    wa_text += (
        f"{'👤 Courier':<12} | {'Man':<5} | {'Can':<4} | {'Dis':<5} | {'Pend':<4} |"
        f" {'🚛 Gadi/In/Out'}\n"
    )
    wa_text += (
        "--------------------------------------------------------------------\n"
    )

    for _, row in edited_df.iterrows():
        c_name = row["Courier"]
        # Numbers ko format karein (skip zeros for man/dis, show zeros for can)
        m_val = str(row["Manifest"]) if row["Manifest"] != 0 else ""
        try:
            can_raw = int(row["Cancel"])
            c_val = str(can_raw) if can_raw != 0 else ""
        except Exception:
            c_val = ""
        d_val = str(row["Dispatch"]) if row["Dispatch"] != 0 else ""
        p_val = str(row["Pending"])

        # Vehicle & Time format karein image ke anusar (Truck emoji included)
        v_val = str(row["Vehicle No"]) if row["Vehicle No"] != "--" else ""
        t_val = ""
        if row["In Time"] != "--" and row["Out Time"] != "--":
            t_val = f" ({row['In Time']}-{row['Out Time']})"
        elif row["In Time"] != "--":
            t_val = f" (In {row['In Time']})"

        v_t_combined = f"{v_val}{t_val}"

        # Left padding (f-string alignment logic)
        wa_text += (
            f"{c_name:<12} | {m_val:<5} | {c_val:<4} | {d_val:<5} |"
            f" {p_val:<4} | {v_t_combined}\n"
        )

    wa_text += (
        "--------------------------------------------------------------------\n"
    )
    # Total row ko format karein
    wa_text += (
        f"✅ *TOTAL*        | *{whatsapp_tot_man}*   | *{whatsapp_tot_can}*  |"
        f" *{whatsapp_tot_dis}*   | *{whatsapp_tot_pend}*\n"
    )
    wa_text += (
        "--------------------------------------------------------------------\n"
    )
    wa_text += f"_Remark:_ _Daily summary shared via Dashboard_\n"

    # Encoded URL for Button
    encoded_wa_msg = urllib.parse.quote(wa_text)
    wa_url = f"https://wa.me/?text={encoded_wa_msg}"

    st.markdown("---")
    # WhatsApp Share Button with professional bada format
    st.markdown(
        f"""
        <a href="{wa_url}" target="_blank" class="wa-btn">
            📲 Share Table Report on WhatsApp Group (Professional Format)
        </a>
    """,
        unsafe_allow_html=True,
    )


# ================= PAGE 2: EMPLOYEE WORK REPORT =================
elif nav_page == "📊 Employee Work Report":
    st.markdown(
        "<div class='card-3d'><h3>📊 Employee Productivity Dashboard</h3></div>",
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

        st.markdown("---")
        st.markdown("#### 📈 Task Wise Parcel Count Breakdown")
        task_summary = (
            df_date.groupby("Task Type")["Parcel Count"].sum().reset_index()
        )
        st.bar_chart(task_summary.set_index("Task Type"))
    else:
        st.info("Selected date ke liye koi employee work record nahi hai.")


# ================= PAGE 3: ADMIN SETUP =================
elif nav_page == "🔐 Admin Setup":
    st.markdown(
        "<div class='card-3d'><h3>🔐 Master Database & Excel Downloads</h3></div>",
        unsafe_allow_html=True,
    )

    if not st.session_state["admin_logged"]:
        st.warning(
            "🔒 Locked Section. Kripya Sidebar me Password dalkar access unlock"
            " karein."
        )
    else:
        tab_emp, tab_cour, tab_excel = st.tabs(
            ["👥 Employees List", "🚚 Couriers List", "📥 Excel Reports"]
        )

        with tab_emp:
            st.markdown("#### Registered Employees Database")
            st.dataframe(st.session_state["employees"], use_container_width=True)

        with tab_cour:
            st.markdown("#### Manifest Courier Options")
            col_c1, col_c2 = st.columns([1, 1.2])
            with col_c1:
                new_c_name = st.text_input("Add New Courier Company")
                if st.button("➕ Add Courier"):
                    if (
                        new_c_name
                        and new_c_name not in st.session_state["couriers"]
                    ):
                        st.session_state["couriers"].append(new_c_name)
                        pd.DataFrame(
                            {"Courier Name": st.session_state["couriers"]}
                        ).to_csv(COURIER_FILE, index=False)
                        st.success("Courier Added!")
                        st.rerun()

            with col_c2:
                st.write("**Current Courier List:**")
                st.write(st.session_state["couriers"])

        with tab_excel:
            st.markdown("#### 📥 Date Wise Excel Export")
            export_date = st.date_input(
                "Export Date", date.today(), key="admin_export_date"
            )
            export_date_str = str(export_date)

            df_all = st.session_state["data"]
            rep_all = st.session_state["dispatch_reports"]

            # Filter data date-wise
            df_exp = (
                df_all[df_all["Date"] == export_date_str]
                if not df_all.empty
                else pd.DataFrame()
            )
            rep_exp = (
                rep_all[rep_all["Date"] == export_date_str]
                if not rep_all.empty
                else pd.DataFrame()
            )

            # Generate and download Excel
            excel_name = f"Dewas_Warehouse_Report_{export_date_str}.xlsx"
            if st.button("Generate Excel Report", use_container_width=True):
                with pd.ExcelWriter(excel_name, engine="openpyxl") as writer:
                    df_exp.to_excel(writer, sheet_name="Entries Log", index=False)
                    rep_exp.to_excel(writer, sheet_name="Dispatch Summary", index=False)
                    st.session_state["employees"].to_excel(writer, sheet_name="Employees", index=False)
                    st.success(f"Report '{excel_name}' ready!")

                with open(excel_name, "rb") as f:
                    st.download_button(
                        label="📥 Click Here to Download Excel",
                        data=f,
                        file_name=excel_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
