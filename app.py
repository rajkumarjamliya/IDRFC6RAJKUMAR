import streamlit as st
import pandas as pd
import sqlite3
import io
import os
import hashlib
from datetime import datetime, date, timedelta
import urllib.parse

# ============================================================
# IDRFC6 DEWAS – FULL WAREHOUSE MANAGEMENT SYSTEM
# Modules:
# Dashboard, GRN/Receiving, Putaway, Inventory, Picking,
# Packing, Courier In/Out, Dispatch, Returns, Damage/Hold,
# Stock Transfer, Cycle Count, Employee Productivity, Masters,
# Reports, Excel Export, Audit Log, Backup.
# ============================================================

st.set_page_config(
    page_title="IDRFC6 DEWAS – Warehouse Management System",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = "idfrc6_warehouse.db"
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

# ----------------------------- THEME -----------------------------
st.markdown(
    """
<style>
.stApp{background:#f4f7f6;font-family:'Segoe UI',Roboto,Arial,sans-serif}
.main-header{background:linear-gradient(135deg,#2e363c,#15181b);padding:22px;border-radius:12px;color:white;text-align:center;border-bottom:5px solid #e31d2b;margin-bottom:20px}
.main-header h1{margin:0;font-size:30px;font-weight:800}
.main-header p{margin:6px 0 0;color:#e1e8ed}
.card{background:#fff;padding:18px;border-radius:12px;border:1px solid #e1e8ed;box-shadow:0 3px 12px rgba(0,0,0,.05);margin-bottom:16px}
h3,h4{color:#2e363c}
div.stButton>button{border-radius:7px;font-weight:600}
.small{font-size:12px;color:#667}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------- DATABASE -----------------------------
@st.cache_resource
def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

conn = get_conn()

def q(sql, params=(), fetch=False):
    cur = conn.cursor()
    cur.execute(sql, params)
    if fetch:
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return pd.DataFrame(rows, columns=cols)
    conn.commit()
    return cur.lastrowid

def init_db():
    tables = [
        """CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE, password_hash TEXT, role TEXT,
            employee_name TEXT, active INTEGER DEFAULT 1)""",

        """CREATE TABLE IF NOT EXISTS employees(
            employee_id TEXT PRIMARY KEY, employee_name TEXT,
            department TEXT, role TEXT, active INTEGER DEFAULT 1)""",

        """CREATE TABLE IF NOT EXISTS couriers(
            courier TEXT PRIMARY KEY, vehicle_no TEXT, contact TEXT, active INTEGER DEFAULT 1)""",

        """CREATE TABLE IF NOT EXISTS locations(
            location TEXT PRIMARY KEY, zone TEXT, capacity REAL DEFAULT 0,
            active INTEGER DEFAULT 1)""",

        """CREATE TABLE IF NOT EXISTS items(
            sku TEXT PRIMARY KEY, item_name TEXT, ean TEXT,
            uom TEXT DEFAULT 'PCS', category TEXT, client TEXT,
            active INTEGER DEFAULT 1)""",

        """CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT, batch TEXT, location TEXT,
            qty REAL DEFAULT 0, hold_qty REAL DEFAULT 0,
            updated_at TEXT,
            UNIQUE(sku,batch,location))""",

        """CREATE TABLE IF NOT EXISTS grn(
            grn_no TEXT PRIMARY KEY, grn_date TEXT, vehicle_no TEXT,
            supplier TEXT, po_no TEXT, status TEXT,
            created_by TEXT, created_at TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS grn_lines(
            id INTEGER PRIMARY KEY AUTOINCREMENT, grn_no TEXT,
            sku TEXT, batch TEXT, expected_qty REAL,
            received_qty REAL, short_qty REAL, excess_qty REAL,
            damage_qty REAL, qc_status TEXT, location TEXT,
            remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS picklists(
            picklist_no TEXT PRIMARY KEY, pick_date TEXT,
            client TEXT, status TEXT, assigned_to TEXT,
            created_by TEXT, created_at TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS pick_lines(
            id INTEGER PRIMARY KEY AUTOINCREMENT, picklist_no TEXT,
            sku TEXT, batch TEXT, requested_qty REAL,
            picked_qty REAL DEFAULT 0, location TEXT,
            picker TEXT, status TEXT DEFAULT 'Pending',
            remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS packing(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pack_date TEXT, picklist_no TEXT, packer TEXT,
            parcel_qty REAL, box_type TEXT, start_time TEXT,
            end_time TEXT, status TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS courier_visits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_date TEXT, courier TEXT, vehicle_no TEXT,
            driver_name TEXT, in_time TEXT, out_time TEXT,
            waiting_minutes INTEGER, manifest_no TEXT,
            parcel_qty REAL DEFAULT 0, status TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS dispatch(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dispatch_date TEXT, courier TEXT, manifest_no TEXT,
            picklist_no TEXT, order_qty REAL DEFAULT 0,
            dispatch_qty REAL DEFAULT 0, pending_qty REAL DEFAULT 0,
            cancel_qty REAL DEFAULT 0, return_qty REAL DEFAULT 0,
            dispatch_time TEXT, status TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS returns(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            return_date TEXT, courier TEXT, awb TEXT, sku TEXT,
            batch TEXT, qty REAL, reason TEXT, condition TEXT,
            location TEXT, status TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS stock_movements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movement_date TEXT, movement_type TEXT, sku TEXT,
            batch TEXT, from_location TEXT, to_location TEXT,
            qty REAL, reference_no TEXT, employee TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS cycle_counts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count_date TEXT, location TEXT, sku TEXT, batch TEXT,
            system_qty REAL, physical_qty REAL, variance REAL,
            counted_by TEXT, status TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS issues(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_date TEXT, issue_type TEXT, reference_no TEXT,
            sku TEXT, batch TEXT, qty REAL, severity TEXT,
            status TEXT, owner TEXT, resolution TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS work_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_date TEXT, timestamp TEXT, picklist_no TEXT,
            employee_id TEXT, employee_name TEXT, task_type TEXT,
            courier TEXT, parcel_count REAL, status TEXT, remark TEXT)""",

        """CREATE TABLE IF NOT EXISTS audit_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, username TEXT, action TEXT,
            module TEXT, reference_no TEXT, details TEXT)"""
    ]
    for sql in tables:
        conn.execute(sql)
    conn.commit()

    # Default admin and sample masters
    if q("SELECT COUNT(*) n FROM users", fetch=True).iloc[0,0] == 0:
        q("INSERT INTO users(username,password_hash,role,employee_name) VALUES(?,?,?,?)",
          ("admin", hashlib.sha256("123".encode()).hexdigest(), "Admin", "Rajkumar"))

    if q("SELECT COUNT(*) n FROM couriers", fetch=True).iloc[0,0] == 0:
        for c,v in [
            ("Delhivery","MP09-AB-1234"),("Shadowfax","MP09-CD-5678"),
            ("ATS","MP09-EF-9012"),("Xpressbees","MP09-GH-3456"),
            ("Ekart","MP09-IJ-7890"),("Bluedart","MP09-KL-1234"),
            ("DTDC","MP09-MN-5678")
        ]:
            q("INSERT OR IGNORE INTO couriers(courier,vehicle_no) VALUES(?,?)",(c,v))

    if q("SELECT COUNT(*) n FROM locations", fetch=True).iloc[0,0] == 0:
        for loc,zone,cap in [
            ("RECV-01","Receiving",1000),("QC-01","QC/Hold",500),
            ("A-01-01","Storage",500),("A-01-02","Storage",500),
            ("A-01-03","Storage",500),("PACK-01","Packing",500),
            ("DISP-01","Dispatch",1000),("RTN-01","Returns",500),
            ("DMG-01","Damage",300)
        ]:
            q("INSERT OR IGNORE INTO locations(location,zone,capacity) VALUES(?,?,?)",(loc,zone,cap))

init_db()

# ----------------------------- HELPERS -----------------------------
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def today():
    return date.today().strftime("%Y-%m-%d")

def df(sql, params=()):
    return q(sql, params, fetch=True)

def audit(action, module, ref="", details=""):
    user = st.session_state.get("username","unknown")
    q("""INSERT INTO audit_log(timestamp,username,action,module,reference_no,details)
         VALUES(?,?,?,?,?,?)""",(now(),user,action,module,ref,details))

def backup_db():
    target = os.path.join(BACKUP_DIR, f"warehouse_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    with open(DB_FILE,"rb") as src, open(target,"wb") as dst:
        dst.write(src.read())
    return target

def excel_bytes(sheets):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        for name,data in sheets.items():
            data.to_excel(writer,index=False,sheet_name=name[:31])
    return out.getvalue()

def time_minutes(t1,t2):
    try:
        a=datetime.strptime(t1,"%I:%M %p")
        b=datetime.strptime(t2,"%I:%M %p")
        if b<a: b += timedelta(days=1)
        return int((b-a).total_seconds()/60)
    except:
        return None

def inventory_change(sku,batch,location,delta):
    r=df("""SELECT id,qty FROM inventory
            WHERE sku=? AND batch=? AND location=?""",(sku,batch,location))
    if r.empty:
        if delta < 0:
            return False
        q("""INSERT INTO inventory(sku,batch,location,qty,updated_at)
             VALUES(?,?,?,?,?)""",(sku,batch,location,delta,now()))
    else:
        new_qty=float(r.iloc[0]["qty"])+float(delta)
        if new_qty < -0.0001:
            return False
        q("UPDATE inventory SET qty=?,updated_at=? WHERE id=?",
          (max(0,new_qty),now(),int(r.iloc[0]["id"])))
    return True

def move_stock(sku,batch,from_loc,to_loc,qty,ref,employee,remark=""):
    qty=float(qty)
    if qty<=0:
        return False,"Qty must be > 0"
    if from_loc:
        if not inventory_change(sku,batch,from_loc,-qty):
            return False,"Source location par sufficient stock nahi hai."
    if to_loc:
        inventory_change(sku,batch,to_loc,qty)
    q("""INSERT INTO stock_movements
         (movement_date,movement_type,sku,batch,from_location,to_location,qty,reference_no,employee,remark)
         VALUES(?,?,?,?,?,?,?,?,?,?)""",
      (today(),"TRANSFER" if from_loc else "RECEIPT",sku,batch,from_loc,to_loc,qty,ref,employee,remark))
    return True,"OK"

def select_options(sql, col):
    x=df(sql)
    return x[col].dropna().astype(str).tolist() if not x.empty else []

# ----------------------------- LOGIN -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
if "username" not in st.session_state:
    st.session_state.username=""

if not st.session_state.logged_in:
    st.markdown('<div class="main-header"><h1>IDRFC6 DEWAS WAREHOUSE MANAGEMENT SYSTEM</h1><p>Secure Login</p></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1.2,1])
    with c2:
        st.markdown("### 🔐 Login")
        u=st.text_input("Username",value="admin")
        p=st.text_input("Password",type="password")
        if st.button("Login",type="primary",use_container_width=True):
            r=df("SELECT * FROM users WHERE username=? AND active=1",(u,))
            if not r.empty and hashlib.sha256(p.encode()).hexdigest()==r.iloc[0]["password_hash"]:
                st.session_state.logged_in=True
                st.session_state.username=u
                st.session_state.role=r.iloc[0]["role"]
                audit("LOGIN","AUTH","","Successful login")
                st.rerun()
            else:
                st.error("Invalid username/password")
    st.info("Default first login: admin / 123. Login ke baad password change karna recommended hai.")
    st.stop()

# ----------------------------- HEADER / SIDEBAR -----------------------------
st.markdown(
    f'<div class="main-header"><h1>IDRFC6 DEWAS – FULL WAREHOUSE MANAGEMENT SYSTEM</h1>'
    f'<p>Lead Operator: RAJKUMAR | User: {st.session_state.username}</p></div>',
    unsafe_allow_html=True
)

employees=select_options("SELECT employee_name FROM employees WHERE active=1","employee_name")
couriers=select_options("SELECT courier FROM couriers WHERE active=1","courier")
locations=select_options("SELECT location FROM locations WHERE active=1","location")
skus=select_options("SELECT sku FROM items WHERE active=1","sku")

with st.sidebar:
    st.markdown("## ⚙️ CONTROL PANEL")
    work_date=st.date_input("Working Date",date.today())
    work_date_str=str(work_date)

    pages=[
        "🏠 Dashboard",
        "📥 GRN / Receiving",
        "📍 Putaway",
        "📦 Inventory",
        "📋 Picklist",
        "🎯 Picking",
        "📦 Packing",
        "🚚 Courier In/Out",
        "🚛 Dispatch",
        "↩️ Returns",
        "🔄 Stock Transfer",
        "🔎 Cycle Count",
        "⚠️ Issues / Damage",
        "👷 Productivity",
        "📊 Reports / MIS",
        "⚙️ Masters",
        "🔐 Admin / Backup"
    ]
    page=st.radio("Navigation",pages)

    st.divider()
    if st.button("🔒 Logout"):
        audit("LOGOUT","AUTH","","User logout")
        st.session_state.logged_in=False
        st.rerun()

# ----------------------------- DASHBOARD -----------------------------
if page=="🏠 Dashboard":
    st.subheader(f"📊 Warehouse Dashboard – {work_date_str}")

    grn_count=int(df("SELECT COUNT(*) n FROM grn WHERE grn_date=?",(work_date_str,)).iloc[0,0])
    pick_count=int(df("SELECT COUNT(*) n FROM picklists WHERE pick_date=?",(work_date_str,)).iloc[0,0])
    dispatch_qty=float(df("SELECT COALESCE(SUM(dispatch_qty),0) n FROM dispatch WHERE dispatch_date=?",(work_date_str,)).iloc[0,0])
    pending_qty=float(df("SELECT COALESCE(SUM(pending_qty),0) n FROM dispatch WHERE dispatch_date=?",(work_date_str,)).iloc[0,0])
    courier_visits=int(df("SELECT COUNT(*) n FROM courier_visits WHERE visit_date=?",(work_date_str,)).iloc[0,0])
    issues=int(df("SELECT COUNT(*) n FROM issues WHERE issue_date=? AND status!='Closed'",(work_date_str,)).iloc[0,0])

    a,b,c,d,e,f=st.columns(6)
    a.metric("GRN",grn_count)
    b.metric("Picklists",pick_count)
    c.metric("Dispatch Qty",int(dispatch_qty))
    d.metric("Pending Qty",int(pending_qty))
    e.metric("Courier Visits",courier_visits)
    f.metric("Open Issues",issues)

    st.markdown("### 📦 Stock by Location")
    stock=df("""SELECT location,ROUND(SUM(qty),2) qty,COUNT(DISTINCT sku) skus
                FROM inventory GROUP BY location ORDER BY qty DESC""")
    st.dataframe(stock,use_container_width=True,hide_index=True)

    st.markdown("### 🚚 Today's Courier Status")
    cv=df("""SELECT courier,vehicle_no,driver_name,in_time,out_time,
             waiting_minutes,parcel_qty,status
             FROM courier_visits WHERE visit_date=? ORDER BY id DESC""",(work_date_str,))
    st.dataframe(cv,use_container_width=True,hide_index=True)

# ----------------------------- GRN / RECEIVING -----------------------------
elif page=="📥 GRN / Receiving":
    st.subheader("📥 GRN / Inward Receiving")

    with st.form("grn_form"):
        c1,c2,c3,c4=st.columns(4)
        grn_no=c1.text_input("GRN No *")
        supplier=c2.text_input("Supplier")
        po_no=c3.text_input("PO No")
        vehicle=c4.text_input("Vehicle No")
        status=st.selectbox("GRN Status",["Received","QC Hold","Completed","Short/Excess Review"])
        remark=st.text_input("Remark")
        save=st.form_submit_button("Create GRN",type="primary")
        if save:
            if not grn_no:
                st.error("GRN No required.")
            else:
                try:
                    q("""INSERT INTO grn(grn_no,grn_date,vehicle_no,supplier,po_no,status,created_by,created_at,remark)
                         VALUES(?,?,?,?,?,?,?,?,?)""",
                      (grn_no,work_date_str,vehicle,supplier,po_no,status,st.session_state.username,now(),remark))
                    audit("CREATE","GRN",grn_no,"GRN created")
                    st.success("GRN created.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("GRN No already exists.")

    st.markdown("### ➕ Add GRN Line")
    grns=select_options("SELECT grn_no FROM grn ORDER BY grn_date DESC","grn_no")
    if grns:
        with st.form("grn_line"):
            c1,c2,c3,c4=st.columns(4)
            g=c1.selectbox("GRN",grns)
            sku=c2.text_input("SKU / Material Code")
            batch=c3.text_input("Batch")
            expected=c4.number_input("Expected Qty",min_value=0.0,step=1.0)
            c5,c6,c7,c8=st.columns(4)
            received=c5.number_input("Received Qty",min_value=0.0,step=1.0)
            damage=c6.number_input("Damage Qty",min_value=0.0,step=1.0)
            qc=c7.selectbox("QC Status",["Passed","Hold","Rejected"])
            loc=c8.selectbox("Initial Location",locations if locations else ["RECV-01"])
            line_remark=st.text_input("Line Remark")
            save_line=st.form_submit_button("Save GRN Line",type="primary")
            if save_line:
                if not sku or not batch:
                    st.error("SKU and Batch required.")
                else:
                    short=max(0,float(expected)-float(received))
                    excess=max(0,float(received)-float(expected))
                    q("""INSERT INTO grn_lines
                         (grn_no,sku,batch,expected_qty,received_qty,short_qty,excess_qty,damage_qty,qc_status,location,remark)
                         VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                      (g,sku,batch,expected,received,short,excess,damage,qc,loc,line_remark))
                    # Receipt into inventory only for non-damage, QC passed
                    good=max(0,float(received)-float(damage))
                    if good>0 and qc=="Passed":
                        inventory_change(sku,batch,loc,good)
                        q("""INSERT INTO stock_movements
                             (movement_date,movement_type,sku,batch,from_location,to_location,qty,reference_no,employee,remark)
                             VALUES(?,?,?,?,?,?,?,?,?,?)""",
                          (work_date_str,"RECEIPT",sku,batch,"",loc,good,g,st.session_state.username,"GRN receipt"))
                    audit("CREATE","GRN_LINE",g,f"{sku}/{batch} received {received}")
                    st.success("GRN line saved and stock updated where applicable.")
                    st.rerun()

    st.markdown("### 📋 GRN Register")
    gdf=df("""SELECT g.grn_no,g.grn_date,g.supplier,g.po_no,g.vehicle_no,g.status,
              COUNT(l.id) lines,COALESCE(SUM(l.received_qty),0) received,
              COALESCE(SUM(l.short_qty),0) short,COALESCE(SUM(l.excess_qty),0) excess,
              COALESCE(SUM(l.damage_qty),0) damage
              FROM grn g LEFT JOIN grn_lines l ON g.grn_no=l.grn_no
              GROUP BY g.grn_no ORDER BY g.grn_date DESC""")
    st.dataframe(gdf,use_container_width=True,hide_index=True)

# ----------------------------- PUTAWAY -----------------------------
elif page=="📍 Putaway":
    st.subheader("📍 Putaway / Location Movement")
    inv=df("""SELECT sku,batch,location,qty FROM inventory WHERE qty>0 ORDER BY sku,batch,location""")
    st.dataframe(inv,use_container_width=True,hide_index=True)

    with st.form("putaway"):
        c1,c2,c3=st.columns(3)
        sku= c1.selectbox("SKU",skus if skus else [""])
        batch=c2.text_input("Batch")
        from_loc=c3.selectbox("From Location",locations if locations else ["RECV-01"])
        c4,c5,c6=st.columns(3)
        to_loc=c4.selectbox("To Location",locations if locations else ["A-01-01"])
        qty=c5.number_input("Qty",min_value=0.0,step=1.0)
        emp=c6.selectbox("Operator",employees if employees else [st.session_state.username])
        ref=st.text_input("GRN / Reference No")
        save=st.form_submit_button("Confirm Putaway",type="primary")
        if save:
            ok,msg=move_stock(sku,batch,from_loc,to_loc,qty,ref,emp,"Putaway")
            if ok:
                audit("PUTAWAY","INVENTORY",ref,f"{sku}/{batch} {qty} {from_loc}->{to_loc}")
                st.success("Putaway completed.")
                st.rerun()
            else:
                st.error(msg)

# ----------------------------- INVENTORY -----------------------------
elif page=="📦 Inventory":
    st.subheader("📦 Live Inventory")
    c1,c2,c3=st.columns(3)
    search=c1.text_input("Search SKU / Batch")
    loc_filter=c2.selectbox("Location",["All"]+locations)
    show_hold=c3.checkbox("Show Hold Qty")

    sql="SELECT sku,batch,location,qty,hold_qty,updated_at FROM inventory WHERE 1=1"
    params=[]
    if search:
        sql+=" AND (sku LIKE ? OR batch LIKE ?)"
        params += [f"%{search}%",f"%{search}%"]
    if loc_filter!="All":
        sql+=" AND location=?"
        params.append(loc_filter)
    inv=df(sql,params)
    st.dataframe(inv,use_container_width=True,hide_index=True)

    st.markdown("### 📈 SKU Stock Summary")
    summary=df("""SELECT sku,ROUND(SUM(qty),2) total_qty,
                  ROUND(SUM(hold_qty),2) hold_qty,
                  COUNT(DISTINCT location) locations
                  FROM inventory GROUP BY sku ORDER BY total_qty DESC""")
    st.dataframe(summary,use_container_width=True,hide_index=True)

# ----------------------------- PICKLIST -----------------------------
elif page=="📋 Picklist":
    st.subheader("📋 Picklist Management")
    with st.form("picklist"):
        c1,c2,c3,c4=st.columns(4)
        pl=c1.text_input("Picklist No *")
        client=c2.text_input("Client")
        assigned=c3.selectbox("Assigned Picker",employees if employees else [""])
        status= c4.selectbox("Status",["Open","In Picking","Picked","Packed","Dispatched","Cancelled"])
        remark=st.text_input("Remark")
        save=st.form_submit_button("Create Picklist",type="primary")
        if save:
            if not pl:
                st.error("Picklist No required.")
            else:
                try:
                    q("""INSERT INTO picklists(picklist_no,pick_date,client,status,assigned_to,created_by,created_at,remark)
                         VALUES(?,?,?,?,?,?,?,?)""",
                      (pl,work_date_str,client,status,assigned,st.session_state.username,now(),remark))
                    audit("CREATE","PICKLIST",pl,"Picklist created")
                    st.success("Picklist created.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Picklist already exists.")

    pls=select_options("SELECT picklist_no FROM picklists WHERE status NOT IN ('Dispatched','Cancelled') ORDER BY pick_date DESC","picklist_no")
    if pls:
        st.markdown("### ➕ Add Picklist Line")
        with st.form("pickline"):
            c1,c2,c3,c4=st.columns(4)
            pl=c1.selectbox("Picklist",pls)
            sku=c2.selectbox("SKU",skus if skus else [""])
            batch=c3.text_input("Batch")
            req=c4.number_input("Requested Qty",min_value=0.0,step=1.0)
            loc=c1.selectbox("Pick Location",locations if locations else ["A-01-01"],key="pick_loc")
            remark=c2.text_input("Remark",key="pick_rem")
            save=st.form_submit_button("Add Pick Line",type="primary")
            if save:
                q("""INSERT INTO pick_lines(picklist_no,sku,batch,requested_qty,location,status,remark)
                     VALUES(?,?,?,?,?,'Pending',?)""",(pl,sku,batch,req,loc,remark))
                audit("CREATE","PICK_LINE",pl,f"{sku}/{batch} qty {req}")
                st.success("Pick line added.")
                st.rerun()

    pdf=df("""SELECT p.picklist_no,p.pick_date,p.client,p.status,p.assigned_to,
              COALESCE(SUM(l.requested_qty),0) requested,
              COALESCE(SUM(l.picked_qty),0) picked
              FROM picklists p LEFT JOIN pick_lines l ON p.picklist_no=l.picklist_no
              GROUP BY p.picklist_no ORDER BY p.pick_date DESC""")
    st.dataframe(pdf,use_container_width=True,hide_index=True)

# ----------------------------- PICKING -----------------------------
elif page=="🎯 Picking":
    st.subheader("🎯 Picking Execution")
    lines=df("""SELECT id,picklist_no,sku,batch,requested_qty,picked_qty,location,picker,status,remark
                FROM pick_lines WHERE status!='Picked' ORDER BY id DESC""")
    st.dataframe(lines,use_container_width=True,hide_index=True)

    if not lines.empty:
        line_id=st.number_input("Pick Line ID",min_value=int(lines["id"].min()),step=1)
        selected=lines[lines["id"]==line_id]
        if not selected.empty:
            r=selected.iloc[0]
            st.write(f"**{r['picklist_no']} | {r['sku']} | Batch {r['batch']} | Required {r['requested_qty']} | Location {r['location']}**")
            with st.form("execute_pick"):
                qty=st.number_input("Picked Qty",min_value=0.0,max_value=float(r["requested_qty"]),value=float(r["requested_qty"]),step=1.0)
                picker=st.selectbox("Picker",employees if employees else [st.session_state.username])
                remark=st.text_input("Remark")
                save=st.form_submit_button("Confirm Pick",type="primary")
                if save:
                    ok,msg=move_stock(r["sku"],r["batch"],r["location"],"",qty,r["picklist_no"],picker,"Pick")
                    if ok:
                        q("""UPDATE pick_lines SET picked_qty=?,picker=?,status=?,remark=? WHERE id=?""",
                          (qty,picker,"Picked" if qty>=float(r["requested_qty"]) else "Partial",remark,int(line_id)))
                        q("UPDATE picklists SET status='Picked' WHERE picklist_no=?",(r["picklist_no"],))
                        q("""INSERT INTO work_entries(work_date,timestamp,picklist_no,employee_name,task_type,parcel_count,status,remark)
                             VALUES(?,?,?,?,?,?,?,?)""",
                          (work_date_str,now(),r["picklist_no"],picker,"Picking",qty,"Completed",remark))
                        audit("PICK","PICKING",r["picklist_no"],f"{r['sku']} qty {qty}")
                        st.success("Picking completed.")
                        st.rerun()
                    else:
                        st.error(msg)

# ----------------------------- PACKING -----------------------------
elif page=="📦 Packing":
    st.subheader("📦 Packing")
    with st.form("packing_form"):
        c1,c2,c3,c4=st.columns(4)
        pl=c1.text_input("Picklist No")
        packer=c2.selectbox("Packer",employees if employees else [st.session_state.username])
        parcel=c3.number_input("Parcel / Box Count",min_value=1.0,step=1.0)
        box=c4.text_input("Box Type",value="Standard")
        c5,c6=st.columns(2)
        start=c5.text_input("Start Time (HH:MM)",value=datetime.now().strftime("%H:%M"))
        end=c6.text_input("End Time (HH:MM)",value=datetime.now().strftime("%H:%M"))
        status=st.selectbox("Packing Status",["Completed","Partial","Hold"])
        remark=st.text_input("Remark")
        save=st.form_submit_button("Save Packing",type="primary")
        if save:
            q("""INSERT INTO packing(pack_date,picklist_no,packer,parcel_qty,box_type,start_time,end_time,status,remark)
                 VALUES(?,?,?,?,?,?,?,?,?)""",
              (work_date_str,pl,packer,parcel,box,start,end,status,remark))
            q("""INSERT INTO work_entries(work_date,timestamp,picklist_no,employee_name,task_type,parcel_count,status,remark)
                 VALUES(?,?,?,?,?,?,?,?)""",
              (work_date_str,now(),pl,packer,"Packing",parcel,status,remark))
            audit("PACK","PACKING",pl,f"{parcel} parcels")
            st.success("Packing saved.")
            st.rerun()

    st.dataframe(df("SELECT * FROM packing WHERE pack_date=? ORDER BY id DESC",(work_date_str,)),use_container_width=True,hide_index=True)

# ----------------------------- COURIER IN/OUT -----------------------------
elif page=="🚚 Courier In/Out":
    st.subheader("🚚 Courier In / Out Tracking")
    st.info("Courier arrival se exit tak exact waiting time track hoga.")

    with st.form("courier_in"):
        c1,c2,c3,c4=st.columns(4)
        courier=c1.selectbox("Courier",couriers if couriers else [""])
        vehicle=c2.text_input("Vehicle No")
        driver=c3.text_input("Driver Name")
        manifest=c4.text_input("Manifest No")
        parcel=c1.number_input("Expected Parcel Qty",min_value=0.0,step=1.0)
        remark=c2.text_input("Remark")
        save=st.form_submit_button("📌 Mark Courier IN",type="primary")
        if save:
            q("""INSERT INTO courier_visits(visit_date,courier,vehicle_no,driver_name,in_time,out_time,
                 waiting_minutes,manifest_no,parcel_qty,status,remark)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
              (work_date_str,courier,vehicle,driver,datetime.now().strftime("%I:%M %p"),
               "--:--",0,manifest,parcel,"IN","Courier arrived"))
            audit("COURIER_IN","COURIER",manifest,f"{courier} {vehicle}")
            st.success("Courier IN time saved.")
            st.rerun()

    active=df("""SELECT * FROM courier_visits WHERE visit_date=? AND status='IN' ORDER BY id DESC""",(work_date_str,))
    if not active.empty:
        st.markdown("### 🏁 Mark OUT")
        visit_id=st.selectbox("Select active visit",active["id"].astype(int).tolist())
        if st.button("🏁 Auto OUT Time",type="primary"):
            r=active[active["id"]==visit_id].iloc[0]
            out=datetime.now().strftime("%I:%M %p")
            wait=time_minutes(r["in_time"],out)
            q("""UPDATE courier_visits SET out_time=?,waiting_minutes=?,status='OUT'
                 WHERE id=?""",(out,wait,visit_id))
            audit("COURIER_OUT","COURIER",str(visit_id),f"{r['courier']} waiting {wait} min")
            st.success(f"OUT saved. Waiting time: {wait} minutes")
            st.rerun()

    st.dataframe(df("""SELECT visit_date,courier,vehicle_no,driver_name,in_time,out_time,
                       waiting_minutes,manifest_no,parcel_qty,status,remark
                       FROM courier_visits WHERE visit_date=? ORDER BY id DESC""",(work_date_str,)),
                 use_container_width=True,hide_index=True)

# ----------------------------- DISPATCH -----------------------------
elif page=="🚛 Dispatch":
    st.subheader("🚛 Dispatch & Manifest")
    with st.form("dispatch"):
        c1,c2,c3,c4=st.columns(4)
        courier=c1.selectbox("Courier",couriers if couriers else [""])
        manifest=c2.text_input("Manifest No")
        pl=c3.text_input("Picklist No")
        order_qty=c4.number_input("Order Qty",min_value=0.0,step=1.0)
        c5,c6,c7,c8=st.columns(4)
        disp=c5.number_input("Dispatch Qty",min_value=0.0,step=1.0)
        cancel=c6.number_input("Cancel Qty",min_value=0.0,step=1.0)
        ret=c7.number_input("Return Qty",min_value=0.0,step=1.0)
        status=c8.selectbox("Status",["Dispatched","Partial","Pending","Cancelled"])
        pending=max(0,order_qty-disp-cancel)
        st.metric("Calculated Pending",pending)
        remark=st.text_input("Remark")
        save=st.form_submit_button("Save Dispatch",type="primary")
        if save:
            q("""INSERT INTO dispatch(dispatch_date,courier,manifest_no,picklist_no,order_qty,
                 dispatch_qty,pending_qty,cancel_qty,return_qty,dispatch_time,status,remark)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
              (work_date_str,courier,manifest,pl,order_qty,disp,pending,cancel,ret,
               datetime.now().strftime("%I:%M %p"),status,remark))
            audit("DISPATCH","DISPATCH",manifest,f"{courier} dispatch {disp}")
            st.success("Dispatch saved.")
            st.rerun()

    dday=df("""SELECT * FROM dispatch WHERE dispatch_date=? ORDER BY id DESC""",(work_date_str,))
    st.dataframe(dday,use_container_width=True,hide_index=True)

    st.markdown("### 📊 Courier-wise Dispatch Summary")
    summ=df("""SELECT courier,
               SUM(order_qty) order_qty,SUM(dispatch_qty) dispatch_qty,
               SUM(pending_qty) pending_qty,SUM(cancel_qty) cancel_qty,
               SUM(return_qty) return_qty
               FROM dispatch WHERE dispatch_date=? GROUP BY courier""",(work_date_str,))
    st.dataframe(summ,use_container_width=True,hide_index=True)

# ----------------------------- RETURNS -----------------------------
elif page=="↩️ Returns":
    st.subheader("↩️ Return / RTO / Customer Return")
    with st.form("return_form"):
        c1,c2,c3,c4=st.columns(4)
        courier=c1.selectbox("Courier",couriers if couriers else [""])
        awb=c2.text_input("AWB / Shipment No")
        sku=c3.selectbox("SKU",skus if skus else [""])
        batch=c4.text_input("Batch")
        qty=c1.number_input("Qty",min_value=0.0,step=1.0)
        reason=c2.selectbox("Reason",["RTO","Customer Return","Damaged","Wrong Item","Other"])
        condition=c3.selectbox("Condition",["Good","Damaged","Open Box","Hold"])
        loc=c4.selectbox("Return Location",locations if locations else ["RTN-01"])
        status=st.selectbox("Status",["Received","QC Pending","Restocked","Rejected"])
        remark=st.text_input("Remark")
        save=st.form_submit_button("Save Return",type="primary")
        if save:
            q("""INSERT INTO returns(return_date,courier,awb,sku,batch,qty,reason,condition,location,status,remark)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
              (work_date_str,courier,awb,sku,batch,qty,reason,condition,loc,status,remark))
            if condition=="Good" and status=="Restocked":
                inventory_change(sku,batch,loc,qty)
            audit("RETURN","RETURNS",awb,f"{sku} qty {qty}")
            st.success("Return saved.")
            st.rerun()
    st.dataframe(df("SELECT * FROM returns WHERE return_date=? ORDER BY id DESC",(work_date_str,)),use_container_width=True,hide_index=True)

# ----------------------------- STOCK TRANSFER -----------------------------
elif page=="🔄 Stock Transfer":
    st.subheader("🔄 Stock Transfer / Location Change")
    with st.form("transfer"):
        c1,c2,c3=st.columns(3)
        sku=c1.selectbox("SKU",skus if skus else [""])
        batch=c2.text_input("Batch")
        qty=c3.number_input("Qty",min_value=0.0,step=1.0)
        c4,c5,c6=st.columns(3)
        fr=c4.selectbox("From Location",locations if locations else [""])
        to=c5.selectbox("To Location",locations if locations else [""])
        emp=c6.selectbox("Employee",employees if employees else [st.session_state.username])
        ref=st.text_input("Reference / Transfer No")
        remark=st.text_input("Remark")
        save=st.form_submit_button("Transfer Stock",type="primary")
        if save:
            ok,msg=move_stock(sku,batch,fr,to,qty,ref,emp,remark)
            if ok:
                audit("TRANSFER","INVENTORY",ref,f"{sku} {qty} {fr}->{to}")
                st.success("Stock transferred.")
                st.rerun()
            else:
                st.error(msg)

    st.dataframe(df("""SELECT movement_date,movement_type,sku,batch,from_location,to_location,
                       qty,reference_no,employee,remark
                       FROM stock_movements ORDER BY id DESC LIMIT 200"""),
                 use_container_width=True,hide_index=True)

# ----------------------------- CYCLE COUNT -----------------------------
elif page=="🔎 Cycle Count":
    st.subheader("🔎 Cycle Count / Physical Stock Verification")
    with st.form("cycle"):
        c1,c2,c3,c4=st.columns(4)
        loc= c1.selectbox("Location",locations if locations else [""])
        sku= c2.selectbox("SKU",skus if skus else [""])
        batch=c3.text_input("Batch")
        physical=c4.number_input("Physical Qty",min_value=0.0,step=1.0)
        system=float(df("SELECT COALESCE(SUM(qty),0) q FROM inventory WHERE sku=? AND batch=? AND location=?",(sku,batch,loc)).iloc[0,0])
        st.metric("System Qty",system)
        counted=st.selectbox("Counted By",employees if employees else [st.session_state.username])
        remark=st.text_input("Remark")
        save=st.form_submit_button("Save Count",type="primary")
        if save:
            variance=physical-system
            status="Match" if abs(variance)<0.0001 else "Variance"
            q("""INSERT INTO cycle_counts(count_date,location,sku,batch,system_qty,physical_qty,variance,counted_by,status,remark)
                 VALUES(?,?,?,?,?,?,?,?,?,?)""",
              (work_date_str,loc,sku,batch,system,physical,variance,counted,status,remark))
            if abs(variance)>=0.0001:
                q("""INSERT INTO issues(issue_date,issue_type,reference_no,sku,batch,qty,severity,status,owner,resolution,remark)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                  (work_date_str,"Stock Variance","CYCLE",sku,batch,abs(variance),"Medium","Open",counted,"",remark))
            audit("CYCLE_COUNT","INVENTORY",f"{sku}/{batch}/{loc}",f"Variance {variance}")
            st.success(f"Count saved. Variance: {variance}")
            st.rerun()
    st.dataframe(df("SELECT * FROM cycle_counts ORDER BY id DESC LIMIT 200"),use_container_width=True,hide_index=True)

# ----------------------------- ISSUES / DAMAGE -----------------------------
elif page=="⚠️ Issues / Damage":
    st.subheader("⚠️ Short / Excess / Damage / Mismatch / Operational Issues")
    with st.form("issue"):
        c1,c2,c3,c4=st.columns(4)
        typ=c1.selectbox("Issue Type",["Short","Excess","Damage","Batch Mismatch","EAN Mismatch","Location Mismatch","Process Error","Other"])
        ref=c2.text_input("Reference No")
        sku=c3.selectbox("SKU",skus if skus else [""])
        batch=c4.text_input("Batch")
        qty=c1.number_input("Qty",min_value=0.0,step=1.0)
        sev=c2.selectbox("Severity",["Low","Medium","High","Critical"])
        owner=c3.selectbox("Owner",employees if employees else [st.session_state.username])
        status=c4.selectbox("Status",["Open","Under Review","Closed"])
        resolution=st.text_input("Resolution")
        remark=st.text_input("Remark")
        save=st.form_submit_button("Save Issue",type="primary")
        if save:
            q("""INSERT INTO issues(issue_date,issue_type,reference_no,sku,batch,qty,severity,status,owner,resolution,remark)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
              (work_date_str,typ,ref,sku,batch,qty,sev,status,owner,resolution,remark))
            audit("ISSUE","QUALITY",ref,f"{typ} {sku} qty {qty}")
            st.success("Issue logged.")
            st.rerun()
    st.dataframe(df("SELECT * FROM issues ORDER BY id DESC LIMIT 300"),use_container_width=True,hide_index=True)

# ----------------------------- PRODUCTIVITY -----------------------------
elif page=="👷 Productivity":
    st.subheader("👷 Employee Productivity")
    p=df("""SELECT employee_id,employee_name,task_type,
            SUM(parcel_count) qty,COUNT(*) entries
            FROM work_entries WHERE work_date=?
            GROUP BY employee_id,employee_name,task_type
            ORDER BY qty DESC""",(work_date_str,))
    st.dataframe(p,use_container_width=True,hide_index=True)
    if not p.empty:
        st.bar_chart(p.groupby("employee_name")["qty"].sum())

# ----------------------------- REPORTS / MIS -----------------------------
elif page=="📊 Reports / MIS":
    st.subheader("📊 Mosaic Daily / Date-wise MIS")
    c1,c2=st.columns(2)
    from_d=c1.date_input("From Date",date.today()-timedelta(days=7))
    to_d=c2.date_input("To Date",date.today())

    if from_d>to_d:
        st.error("From Date cannot be greater than To Date.")
    else:
        f=str(from_d); t=str(to_d)
        gr=df("SELECT * FROM grn WHERE grn_date BETWEEN ? AND ?",(f,t))
        gl=df("SELECT * FROM grn_lines WHERE grn_no IN (SELECT grn_no FROM grn WHERE grn_date BETWEEN ? AND ?)",(f,t))
        inv=df("SELECT * FROM inventory")
        picks=df("SELECT * FROM picklists WHERE pick_date BETWEEN ? AND ?",(f,t))
        pickl=df("SELECT * FROM pick_lines WHERE picklist_no IN (SELECT picklist_no FROM picklists WHERE pick_date BETWEEN ? AND ?)",(f,t))
        pack=df("SELECT * FROM packing WHERE pack_date BETWEEN ? AND ?",(f,t))
        cour=df("SELECT * FROM courier_visits WHERE visit_date BETWEEN ? AND ?",(f,t))
        disp=df("SELECT * FROM dispatch WHERE dispatch_date BETWEEN ? AND ?",(f,t))
        ret=df("SELECT * FROM returns WHERE return_date BETWEEN ? AND ?",(f,t))
        issues=df("SELECT * FROM issues WHERE issue_date BETWEEN ? AND ?",(f,t))
        moves=df("SELECT * FROM stock_movements WHERE movement_date BETWEEN ? AND ?",(f,t))

        k1,k2,k3,k4,k5=st.columns(5)
        k1.metric("GRN",len(gr))
        k2.metric("Received Qty",int(gl["received_qty"].sum()) if not gl.empty else 0)
        k3.metric("Picked Qty",int(pickl["picked_qty"].sum()) if not pickl.empty else 0)
        k4.metric("Dispatch Qty",int(disp["dispatch_qty"].sum()) if not disp.empty else 0)
        k5.metric("Returns Qty",int(ret["qty"].sum()) if not ret.empty else 0)

        tab1,tab2,tab3,tab4=st.tabs(["🚚 Dispatch MIS","📥 Inward MIS","📦 Inventory","⚠️ Exceptions"])
        with tab1:
            st.dataframe(disp,use_container_width=True,hide_index=True)
            st.dataframe(cour,use_container_width=True,hide_index=True)
        with tab2:
            st.dataframe(gr,use_container_width=True,hide_index=True)
            st.dataframe(gl,use_container_width=True,hide_index=True)
        with tab3:
            st.dataframe(inv,use_container_width=True,hide_index=True)
            st.dataframe(moves,use_container_width=True,hide_index=True)
        with tab4:
            st.dataframe(issues,use_container_width=True,hide_index=True)
            st.dataframe(ret,use_container_width=True,hide_index=True)

        sheets={
            "GRN":gr,"GRN_Lines":gl,"Inventory":inv,"Picklists":picks,
            "Pick_Lines":pickl,"Packing":pack,"Courier_InOut":cour,
            "Dispatch":disp,"Returns":ret,"Issues":issues,"Movements":moves
        }
        st.download_button(
            "📥 Download Complete Mosaic MIS Excel",
            excel_bytes(sheets),
            f"Mosaic_MIS_{from_d}_to_{to_d}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        # WhatsApp summary
        total_disp=int(disp["dispatch_qty"].sum()) if not disp.empty else 0
        total_pending=int(disp["pending_qty"].sum()) if not disp.empty else 0
        text=f"*IDRFC6 DEWAS – MOSAIC MIS*\n📅 {from_d} to {to_d}\n"
        text+=f"📥 GRN: {len(gr)}\n📦 Received: {int(gl['received_qty'].sum()) if not gl.empty else 0}\n"
        text+=f"🎯 Picked: {int(pickl['picked_qty'].sum()) if not pickl.empty else 0}\n"
        text+=f"🚛 Dispatch: {total_disp}\n⏳ Pending: {total_pending}\n"
        text+=f"↩️ Returns: {int(ret['qty'].sum()) if not ret.empty else 0}\n"
        st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(text)}" target="_blank">📲 Share MIS on WhatsApp</a>',unsafe_allow_html=True)

# ----------------------------- MASTERS -----------------------------
elif page=="⚙️ Masters":
    st.subheader("⚙️ Master Data")
    t1,t2,t3,t4=st.tabs(["👤 Employees","🚚 Couriers","📦 Items","📍 Locations"])

    with t1:
        with st.form("emp_master"):
            eid=st.text_input("Employee ID")
            ename=st.text_input("Employee Name")
            dept=st.text_input("Department",value="Warehouse")
            role=st.text_input("Role",value="Operator")
            save=st.form_submit_button("Add Employee")
            if save and eid and ename:
                q("INSERT OR REPLACE INTO employees(employee_id,employee_name,department,role,active) VALUES(?,?,?,?,1)",(eid,ename,dept,role))
                audit("MASTER","EMPLOYEE",eid,"Employee added")
                st.rerun()
        st.dataframe(df("SELECT * FROM employees"),use_container_width=True,hide_index=True)

    with t2:
        with st.form("cour_master"):
            c=st.text_input("Courier Name")
            v=st.text_input("Vehicle No")
            contact=st.text_input("Contact")
            save=st.form_submit_button("Add/Update Courier")
            if save and c:
                q("INSERT OR REPLACE INTO couriers(courier,vehicle_no,contact,active) VALUES(?,?,?,1)",(c,v,contact))
                audit("MASTER","COURIER",c,"Courier master updated")
                st.rerun()
        st.dataframe(df("SELECT * FROM couriers"),use_container_width=True,hide_index=True)

    with t3:
        with st.form("item_master"):
            sku=st.text_input("SKU")
            name=st.text_input("Item Name")
            ean=st.text_input("EAN / Barcode")
            uom=st.selectbox("UOM",["PCS","BOX","KG","SET","BAG"])
            cat=st.text_input("Category")
            client=st.text_input("Client")
            save=st.form_submit_button("Add/Update Item")
            if save and sku:
                q("""INSERT OR REPLACE INTO items(sku,item_name,ean,uom,category,client,active)
                     VALUES(?,?,?,?,?,?,1)""",(sku,name,ean,uom,cat,client))
                audit("MASTER","ITEM",sku,"Item master updated")
                st.rerun()
        st.dataframe(df("SELECT * FROM items"),use_container_width=True,hide_index=True)

    with t4:
        with st.form("loc_master"):
            loc=st.text_input("Location Code")
            zone=st.selectbox("Zone",["Receiving","QC/Hold","Storage","Picking","Packing","Dispatch","Returns","Damage"])
            cap=st.number_input("Capacity",min_value=0.0,step=1.0)
            save=st.form_submit_button("Add/Update Location")
            if save and loc:
                q("INSERT OR REPLACE INTO locations(location,zone,capacity,active) VALUES(?,?,?,1)",(loc,zone,cap))
                audit("MASTER","LOCATION",loc,"Location master updated")
                st.rerun()
        st.dataframe(df("SELECT * FROM locations"),use_container_width=True,hide_index=True)

# ----------------------------- ADMIN / BACKUP -----------------------------
elif page=="🔐 Admin / Backup":
    if st.session_state.get("role")!="Admin":
        st.warning("Admin access required.")
        st.stop()

    st.subheader("🔐 Admin / Backup / Audit")
    t1,t2,t3=st.tabs(["👤 Users","💾 Backup","🧾 Audit Log"])

    with t1:
        with st.form("user_add"):
            u=st.text_input("Username")
            p=st.text_input("Password",type="password")
            role=st.selectbox("Role",["Admin","Supervisor","Operator","Viewer"])
            name=st.text_input("Employee Name")
            save=st.form_submit_button("Create User")
            if save and u and p:
                try:
                    q("INSERT INTO users(username,password_hash,role,employee_name) VALUES(?,?,?,?)",
                      (u,hashlib.sha256(p.encode()).hexdigest(),role,name))
                    audit("CREATE","USER",u,"User created")
                    st.success("User created.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Username already exists.")
        st.dataframe(df("SELECT id,username,role,employee_name,active FROM users"),use_container_width=True,hide_index=True)

    with t2:
        st.write("Database backup se complete warehouse data safe rahega.")
        if st.button("💾 Create Backup Now",type="primary"):
            path=backup_db()
            audit("BACKUP","SYSTEM","",path)
            st.success(f"Backup created: {path}")
        st.download_button(
            "📥 Download Current Database",
            data=open(DB_FILE,"rb").read(),
            file_name=f"IDRFC6_Warehouse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            mime="application/octet-stream",
            use_container_width=True
        )

    with t3:
        st.dataframe(df("SELECT * FROM audit_log ORDER BY id DESC LIMIT 500"),
                     use_container_width=True,hide_index=True)

st.caption("IDRFC6 DEWAS Warehouse Management System | SQLite backend | Designed for operational tracking and MIS")
