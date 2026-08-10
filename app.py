import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path

st.set_page_config(page_title="Mosaic Warehouse Dispatch Tracker", layout="wide")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
COURIER_FILE = DATA_DIR / "courier_log.csv"
DISPATCH_FILE = DATA_DIR / "dispatch_log.csv"

COURIER_COLS = [
    "ID","Date","Courier","Vehicle No","Driver Name",
    "In Time","Out Time","Waiting Minutes","Remark"
]
DISPATCH_COLS = [
    "ID","Date","Courier","Manifest No","Picklist No",
    "Order Qty","Dispatch Qty","Pending Qty","Cancel Qty",
    "Dispatch Time","Remark"
]

def load_csv(path, cols):
    if path.exists():
        df = pd.read_csv(path)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols]
    return pd.DataFrame(columns=cols)

def save_csv(df, path):
    df.to_csv(path, index=False)

def next_id(df):
    if df.empty:
        return 1
    nums = pd.to_numeric(df["ID"], errors="coerce").dropna()
    return int(nums.max()) + 1 if not nums.empty else 1

courier_df = load_csv(COURIER_FILE, COURIER_COLS)
dispatch_df = load_csv(DISPATCH_FILE, DISPATCH_COLS)

st.title("📦 Mosaic Warehouse – Dispatch & Courier Tracker")
st.caption("Courier In/Out + Dispatch + Pending + Daily MIS")

with st.sidebar:
    st.header("Menu")
    page = st.radio(
        "Select",
        ["Dashboard", "Courier In/Out", "Dispatch Entry", "Reports"]
    )

    st.divider()
    st.info("Data is stored in the local data/ folder.")

def calc_wait(in_time, out_time):
    if not in_time or not out_time:
        return ""
    try:
        t1 = datetime.strptime(str(in_time), "%H:%M")
        t2 = datetime.strptime(str(out_time), "%H:%M")
        if t2 < t1:
            # Handles a shift crossing midnight
            from datetime import timedelta
            t2 += timedelta(days=1)
        return int((t2 - t1).total_seconds() // 60)
    except Exception:
        return ""

if page == "Dashboard":
    st.subheader("📊 Daily Dashboard")

    selected_date = st.date_input("Report Date", value=date.today())
    dstr = selected_date.strftime("%Y-%m-%d")

    cday = courier_df[courier_df["Date"].astype(str) == dstr].copy()
    pday = dispatch_df[dispatch_df["Date"].astype(str) == dstr].copy()

    for col in ["Order Qty","Dispatch Qty","Pending Qty","Cancel Qty"]:
        if col in pday:
            pday[col] = pd.to_numeric(pday[col], errors="coerce").fillna(0)

    total_couriers = len(cday)
    total_order = int(pday["Order Qty"].sum()) if not pday.empty else 0
    total_dispatch = int(pday["Dispatch Qty"].sum()) if not pday.empty else 0
    total_pending = int(pday["Pending Qty"].sum()) if not pday.empty else 0
    total_cancel = int(pday["Cancel Qty"].sum()) if not pday.empty else 0

    a,b,c,d,e = st.columns(5)
    a.metric("Courier Visits", total_couriers)
    b.metric("Order Qty", total_order)
    c.metric("Dispatch Qty", total_dispatch)
    d.metric("Pending Qty", total_pending)
    e.metric("Cancel Qty", total_cancel)

    st.divider()
    st.subheader("Courier-wise Dispatch")

    if not pday.empty:
        summary = (
            pday.groupby("Courier", dropna=False)
            [["Order Qty","Dispatch Qty","Pending Qty","Cancel Qty"]]
            .sum()
            .reset_index()
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        st.info("Selected date ke liye dispatch data nahi hai.")

elif page == "Courier In/Out":
    st.subheader("🚚 Courier In / Out Entry")

    with st.form("courier_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        entry_date = col1.date_input("Date", date.today())
        courier = col2.selectbox(
            "Courier",
            ["Delhivery","Bluedart","Xpressbees","Ecom Express","DTDC","Ekart","Shadowfax","ATS","Other"]
        )
        vehicle = col3.text_input("Vehicle No")

        col4, col5, col6 = st.columns(3)
        driver = col4.text_input("Driver Name")
        in_time = col5.time_input("In Time", datetime.now().time())
        out_time = col6.time_input("Out Time", datetime.now().time())

        remark = st.text_input("Remark")
        submitted = st.form_submit_button("Save Courier Entry", type="primary")

        if submitted:
            in_str = in_time.strftime("%H:%M")
            out_str = out_time.strftime("%H:%M")
            wait = calc_wait(in_str, out_str)

            new = pd.DataFrame([{
                "ID": next_id(courier_df),
                "Date": entry_date.strftime("%Y-%m-%d"),
                "Courier": courier,
                "Vehicle No": vehicle,
                "Driver Name": driver,
                "In Time": in_str,
                "Out Time": out_str,
                "Waiting Minutes": wait,
                "Remark": remark
            }])
            courier_df = pd.concat([courier_df, new], ignore_index=True)
            save_csv(courier_df, COURIER_FILE)
            st.success("Courier In/Out entry saved successfully.")
            st.rerun()

    st.divider()
    st.subheader("Courier Log")
    if not courier_df.empty:
        view = courier_df.copy()
        view["Waiting Time"] = pd.to_numeric(
            view["Waiting Minutes"], errors="coerce"
        ).fillna(0).astype(int).astype(str) + " min"
        st.dataframe(view, use_container_width=True, hide_index=True)

elif page == "Dispatch Entry":
    st.subheader("📦 Dispatch Entry")

    with st.form("dispatch_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        entry_date = col1.date_input("Date", date.today())
        courier = col2.selectbox(
            "Courier",
            ["Delhivery","Bluedart","Xpressbees","Ecom Express","DTDC","Ekart","Shadowfax","ATS","Other"]
        )
        manifest = col3.text_input("Manifest No")

        col4, col5 = st.columns(2)
        picklist = col4.text_input("Picklist No")
        dispatch_time = col5.time_input("Dispatch Time", datetime.now().time())

        col6, col7, col8, col9 = st.columns(4)
        order_qty = col6.number_input("Order Qty", min_value=0, step=1)
        dispatch_qty = col7.number_input("Dispatch Qty", min_value=0, step=1)
        cancel_qty = col8.number_input("Cancel Qty", min_value=0, step=1)
        pending_qty = max(int(order_qty) - int(dispatch_qty) - int(cancel_qty), 0)
        col9.metric("Pending Qty", pending_qty)

        remark = st.text_input("Remark")
        submitted = st.form_submit_button("Save Dispatch", type="primary")

        if submitted:
            new = pd.DataFrame([{
                "ID": next_id(dispatch_df),
                "Date": entry_date.strftime("%Y-%m-%d"),
                "Courier": courier,
                "Manifest No": manifest,
                "Picklist No": picklist,
                "Order Qty": int(order_qty),
                "Dispatch Qty": int(dispatch_qty),
                "Pending Qty": pending_qty,
                "Cancel Qty": int(cancel_qty),
                "Dispatch Time": dispatch_time.strftime("%H:%M"),
                "Remark": remark
            }])
            dispatch_df = pd.concat([dispatch_df, new], ignore_index=True)
            save_csv(dispatch_df, DISPATCH_FILE)
            st.success("Dispatch entry saved successfully.")
            st.rerun()

    st.divider()
    st.subheader("Dispatch Log")
    st.dataframe(dispatch_df, use_container_width=True, hide_index=True)

elif page == "Reports":
    st.subheader("📋 Mosaic MIS Reports")

    if courier_df.empty and dispatch_df.empty:
        st.info("Report ke liye data available nahi hai.")
    else:
        min_date = date.today()
        max_date = date.today()

        all_dates = []
        if not courier_df.empty:
            all_dates += courier_df["Date"].dropna().astype(str).tolist()
        if not dispatch_df.empty:
            all_dates += dispatch_df["Date"].dropna().astype(str).tolist()

        if all_dates:
            parsed = pd.to_datetime(all_dates, errors="coerce").dropna()
            if not parsed.empty:
                min_date = parsed.min().date()
                max_date = parsed.max().date()

        col1, col2 = st.columns(2)
        from_date = col1.date_input("From Date", min_date)
        to_date = col2.date_input("To Date", max_date)

        if from_date > to_date:
            st.error("From Date, To Date se badi nahi honi chahiye.")
        else:
            c = courier_df.copy()
            p = dispatch_df.copy()

            if not c.empty:
                c["DateParsed"] = pd.to_datetime(c["Date"], errors="coerce").dt.date
                c = c[(c["DateParsed"] >= from_date) & (c["DateParsed"] <= to_date)]

            if not p.empty:
                p["DateParsed"] = pd.to_datetime(p["Date"], errors="coerce").dt.date
                p = p[(p["DateParsed"] >= from_date) & (p["DateParsed"] <= to_date)]

            st.subheader("Courier In/Out Report")
            st.dataframe(c.drop(columns=["DateParsed"], errors="ignore"),
                         use_container_width=True, hide_index=True)

            st.subheader("Dispatch Report")
            st.dataframe(p.drop(columns=["DateParsed"], errors="ignore"),
                         use_container_width=True, hide_index=True)

            if not p.empty:
                for col in ["Order Qty","Dispatch Qty","Pending Qty","Cancel Qty"]:
                    p[col] = pd.to_numeric(p[col], errors="coerce").fillna(0)

                summary = (
                    p.groupby("Courier")
                    [["Order Qty","Dispatch Qty","Pending Qty","Cancel Qty"]]
                    .sum().reset_index()
                )

                st.subheader("Courier-wise Summary")
                st.dataframe(summary, use_container_width=True, hide_index=True)

                csv = p.drop(columns=["DateParsed"], errors="ignore").to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Dispatch CSV",
                    csv,
                    "Mosaic_Dispatch_Report.csv",
                    "text/csv"
                )

            if not c.empty:
                csv2 = c.drop(columns=["DateParsed"], errors="ignore").to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Courier In-Out CSV",
                    csv2,
                    "Mosaic_Courier_In_Out_Report.csv",
                    "text/csv"
                )
