import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="DELHIVERY IDRFC6 Mini Tracker", layout="wide")
st.title("📦 DELHIVERY - IDRFC6 Mini Warehouse Tracker")
FILE="mini_tracker.csv"
if os.path.exists(FILE):
    df=pd.read_csv(FILE)
else:
    df=pd.DataFrame(columns=["Date","Time","Piklist","Employee","Employee ID","Courier","Boxes"])
employees={
"AJAY PATEL":"W222449","PANKAJ PATEL":"W224500","KAMLESH MANDOI":"W225396","ABHISHEK PATEL":"W225403",
"SHRI RAM":"W225410","KUNAL PATIL":"W225413","RAJSARGARA":"W225415","ANISH PATEL":"226351",
"ANKIT MANDLOI":"W226654","SANDEEP PATEL":"W228473","ABHISHEK PATEL (2)":"230777",
"RAJKUMAR JAMLIYA":"W224483","CHANDAN":"W228474","SHAILESH TIWARI":"SSN079654",
"SUJATA KUSHWAHA":"W231056","SANDHYA KARANJA":"W231195","HARSHITA SOLANKI":"W231196",
"BHAVNA MALVIYA":"W231057","REKHA":"W231152","KAVITA":"W231689"}
couriers=["Delhivery","Shadowfax","ATS","Xpressbees","DTDC","Bluedart","Ekart"]
with st.form("f"):
 p=st.text_input("Piklist No.")
 e=st.selectbox("Employee",list(employees.keys()))
 st.text_input("Employee ID",employees[e],disabled=True)
 c=st.selectbox("Courier",couriers)
 b=st.number_input("Boxes",1,99999,1)
 ok=st.form_submit_button("Save")
if ok:
 n=datetime.now()
 df.loc[len(df)]=[n.strftime("%Y-%m-%d"),n.strftime("%H:%M:%S"),p,e,employees[e],c,b]
 df.to_csv(FILE,index=False)
 st.success("Saved")
t=datetime.now().strftime("%Y-%m-%d")
td=df[df["Date"]==t]
st.subheader("Today's Entries")
st.dataframe(td,use_container_width=True)
if not td.empty:
 st.subheader("Courier Summary")
 st.dataframe(td.groupby("Courier",as_index=False)["Boxes"].sum(),use_container_width=True)
 st.metric("Total Boxes",int(td["Boxes"].sum()))
