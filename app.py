# streamlit_app.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Task & Expense App", layout="wide")

# ========================= CUSTOM PURPLE THEME CSS =========================
st.markdown("""
<style>

/* Global Background */
body {
    background-color: #f3e8ff;
}

/* Headings */
h1, h2, h3 {
    color: #5a189a !important;
    font-weight: 800 !important;
}

/* Card Container */
.card {
    background: #ffffff;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0px 6px 18px rgba(90, 24, 154, 0.15);
    margin-bottom: 22px;
    border-left: 6px solid #7b2cbf;
}

/* Input boxes */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    border-radius: 12px !important;
    border: 1px solid #c8a4ff !important;
    padding: 10px !important;
}

/* Text Areas */
textarea {
    border-radius: 12px !important;
    border: 1px solid #c8a4ff !important;
}

/* Selectbox */
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 1px solid #c8a4ff !important;
}

/* Checkboxes */
.stCheckbox > label > div:first-child {
    accent-color: #7b2cbf !important;
}

/* Button */
.stButton>button {
    background-color: #7b2cbf !important;
    color: white !important;
    padding: 10px 24px !important;
    border-radius: 10px !important;
    border: none !important;
    font-size: 17px !important;
}
.stButton>button:hover {
    background-color: #5a189a !important;
}

/* Metric Styling */
[data-testid="stMetricLabel"] {
    color: #7b2cbf !important;
    font-size: 18px !important;
}
[data-testid="stMetricValue"] {
    color: #5a189a !important;
    font-size: 30px !important;
    font-weight: bold !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================================

USERS_FILE = "users.xlsx"
TASKS_FILE = "tasks.xlsx"

# ---------------- File Initialization ----------------
def init_files():
    if not os.path.exists(USERS_FILE):
        df_users = pd.DataFrame(columns=["username", "email", "contact_no", "password"])
        df_users.to_excel(USERS_FILE, index=False)

    if not os.path.exists(TASKS_FILE):
        df_tasks = pd.DataFrame(columns=[
            "username", "date", "task_assigned_by", "work_assignment", "assigned_to_person",
            "task_description", "work_done_today", "task_status", "work_plan_next_day",
            "expense_purpose", "other_purpose", "amount"
        ])
        df_tasks.to_excel(TASKS_FILE, index=False)

init_files()

# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "expense" not in st.session_state:
    st.session_state.expense = {
        "travelling": False, "travelling_amt": 0.0,
        "mobile": False, "mobile_amt": 0.0,
        "food": False, "food_amt": 0.0,
        "other": False, "other_amt": 0.0, "other_purpose": "",
        "none": False
    }

# ---------------- Utility Functions ----------------
def register_user(username, email, contact_no, password):
    try:
        df = pd.read_excel(USERS_FILE)
    except:
        df = pd.DataFrame(columns=["username", "email", "contact_no", "password"])

    if username in df["username"].values:
        return False, "Username already exists!"

    df = pd.concat([df, pd.DataFrame([{
        "username": username,
        "email": email,
        "contact_no": contact_no,
        "password": password
    }])], ignore_index=True)

    df.to_excel(USERS_FILE, index=False)
    return True, "Registration successful!"

def login_user(username, password):
    try:
        df = pd.read_excel(USERS_FILE)
    except:
        return False

    user = df[(df["username"] == username) & (df["password"] == password)]
    return not user.empty

def load_tasks(username):
    try:
        df = pd.read_excel(TASKS_FILE)
        df["date"] = pd.to_datetime(df["date"], errors='coerce')
        return df[df["username"] == username]
    except:
        return pd.DataFrame()

def append_task(row):
    try:
        df = pd.read_excel(TASKS_FILE)
    except:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_excel(TASKS_FILE, index=False)

# ---------------- Sidebar ----------------
st.sidebar.title("Welcome")

if st.session_state.logged_in:
    st.sidebar.write(f"Logged in as **{st.session_state.username}**")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    page = st.sidebar.radio("Menu", ["Dashboard", "Add Task"])
else:
    page = st.sidebar.radio("Menu", ["Login", "Register"])

# ---------------- Register Page ----------------
if page == "Register":

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title("Register")

    with st.form("reg_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        contact = st.text_input("Contact Number")
        password = st.text_input("Password", type="password")

        submit = st.form_submit_button("Register")

        if submit:
            ok, msg = register_user(username, email, contact, password)
            st.success(msg) if ok else st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Login Page ----------------
elif page == "Login":

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submit = st.form_submit_button("Login")

        if submit:
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid login details.")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Dashboard ----------------
elif page == "Dashboard":

    st.title(f"Welcome, {st.session_state.username}!")

    df = load_tasks(st.session_state.username)

    col1, col2 = st.columns(2)
    col1.metric("Total Tasks", len(df))
    col2.metric("Total Expense", f"₹{df['amount'].sum():.2f}" if not df.empty else "₹0.00")

    st.markdown("<h2>Recent Tasks (Last 30 Days)</h2>", unsafe_allow_html=True)

    last_30 = datetime.now() - timedelta(days=30)
    recent = df[df["date"] >= last_30]

    if recent.empty:
        st.info("No recent tasks found.")
    else:
        for _, t in recent.sort_values("date", ascending=False).iterrows():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write(f"### {t['date'].strftime('%Y-%m-%d')}")
            st.write(f"**Assigned By:** {t['task_assigned_by']}")
            st.write(f"**Description:** {t['task_description']}")
            st.write(f"**Work Done:** {t['work_done_today']}")
            st.write(f"**Status:** {t['task_status']}")
            st.write(f"**Next Day Plan:** {t['work_plan_next_day']}")
            if t["expense_purpose"] == "none":
                st.write("**Expense:** No Expense")
            else:
                st.write(f"**Expense:** ₹{t['amount']} ({t['expense_purpose']})")
            st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Add Task Page ----------------
elif page == "Add Task":

    st.title("Add Task & Expense")

    # ============ EXPENSE SECTION ============
    st.markdown("<div class='card'><h2>Expense Section</h2>", unsafe_allow_html=True)

    e = st.session_state.expense

    colA, colB, colC, colD = st.columns(4)
    with colA: e["travelling"] = st.checkbox("Travelling", e["travelling"])
    with colB: e["mobile"] = st.checkbox("Mobile Recharge", e["mobile"])
    with colC: e["food"] = st.checkbox("Food", e["food"])
    with colD: e["other"] = st.checkbox("Other", e["other"])

    e["none"] = st.checkbox("None (No Expense)", e["none"])

    if e["none"]:
        for k in e: e[k] = False
        e["none"] = True
        e["travelling_amt"] = e["mobile_amt"] = e["food_amt"] = e["other_amt"] = 0

    if e["travelling"]:
        e["travelling_amt"] = st.number_input("Travelling Amount ₹", min_value=0.0, step=0.1,
                                             value=e["travelling_amt"])

    if e["mobile"]:
        e["mobile_amt"] = st.number_input("Mobile Recharge Amount ₹", min_value=0.0, step=0.1,
                                          value=e["mobile_amt"])

    if e["food"]:
        e["food_amt"] = st.number_input("Food Amount ₹", min_value=0.0, step=0.1,
                                        value=e["food_amt"])

    if e["other"]:
        e["other_amt"] = st.number_input("Other Amount ₹", min_value=0.0, step=0.1,
                                         value=e["other_amt"])
        e["other_purpose"] = st.text_input("Enter Other Purpose", value=e["other_purpose"])

    total = e["travelling_amt"] + e["mobile_amt"] + e["food_amt"] + e["other_amt"]
    st.text_input("Total Expense Amount ₹", value=f"{total:.2f}", disabled=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ============ TASK ASSIGNED BY ============
    #st.markdown("<div class='card'><h2>Task Assigned By</h2>", unsafe_allow_html=True)
    assigned_by = st.text_input("Task Assigned By")
    st.markdown("</div>", unsafe_allow_html=True)

    # ============ WORK ASSIGNMENT ============
    #st.markdown("<div class='card'><h2>Work Assignment</h2>", unsafe_allow_html=True)

    work_assign = st.selectbox("Work Assignment", ["", "self", "other"])

    if work_assign == "other":
        assigned_to = st.text_input("Enter Name (Assigned To)")
    else:
        assigned_to = ""

    st.markdown("</div>", unsafe_allow_html=True)

    # ============ TASK DETAILS FORM ============
    st.markdown("<div class='card'><h2>Task Details</h2>", unsafe_allow_html=True)

    with st.form("task_form"):

        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())

        with col2:
            task_desc = st.text_area("Task Description")
            work_done = st.text_area("Work Done Today")
            status = st.selectbox("Task Status", ["", "pending", "in_progress", "completed"])
            next_day = st.text_area("Work Plan for Next Day")

        submit = st.form_submit_button("Submit")

        if submit:
            if e["none"]:
                exp_purpose = "none"
                amount = 0
                other_purpose = ""
            else:
                p = []
                if e["travelling"]: p.append("travelling")
                if e["mobile"]: p.append("mobile_recharge")
                if e["food"]: p.append("food")
                if e["other"]: p.append("other")

                exp_purpose = ", ".join(p)
                amount = total
                other_purpose = e["other_purpose"]

            row = {
                "username": st.session_state.username,
                "date": date.strftime("%Y-%m-%d"),
                "task_assigned_by": assigned_by,
                "work_assignment": work_assign,
                "assigned_to_person": assigned_to,
                "task_description": task_desc,
                "work_done_today": work_done,
                "task_status": status,
                "work_plan_next_day": next_day,
                "expense_purpose": exp_purpose,
                "other_purpose": other_purpose,
                "amount": amount
            }

            append_task(row)
            st.success("Task saved successfully!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
