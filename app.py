import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from database import (
    initialize_database,
    register_user,
    login_user,
    check_in,
    check_out,
    get_today_attendance,
    get_employee_attendance,
    get_all_employees,
    get_all_attendance,
    apply_leave,
    get_user_leaves,
    get_all_leaves,
    update_leave_status,
)

# =================================================
# PAGE CONFIGURATION
# =================================================

st.set_page_config(
    page_title="SmartAttend",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =================================================
# DATABASE INITIALIZATION
# =================================================

initialize_database()


# =================================================
# PREMIUM CUSTOM CSS
# =================================================

st.markdown(
    """
    <style>

    /* ============================================
       GLOBAL BACKGROUND
    ============================================ */

    .stApp {
        background:
            radial-gradient(
                circle at 15% 20%,
                rgba(59, 130, 246, 0.18),
                transparent 30%
            ),
            radial-gradient(
                circle at 85% 80%,
                rgba(16, 185, 129, 0.12),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #080d18 0%,
                #101827 50%,
                #080d18 100%
            );
    }


    /* ============================================
       MAIN CONTAINER
    ============================================ */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }


    /* ============================================
       LOGIN BRANDING
    ============================================ */

    .main-title {
        font-size: 58px;
        font-weight: 850;
        text-align: center;
        letter-spacing: -2px;
        margin-top: 15px;
        margin-bottom: 5px;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #7dd3fc,
                #a7f3d0
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }


    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 18px;
        margin-bottom: 30px;
        letter-spacing: 0.5px;
    }


    /* ============================================
       INPUT BOXES
    ============================================ */

    div[data-baseweb="input"] > div {
        background-color: rgba(30, 41, 59, 0.85);
        border: 1px solid #334155;
        border-radius: 12px;
    }


    div[data-baseweb="input"] > div:focus-within {
        border-color: #38bdf8;
        box-shadow:
            0 0 0 2px
            rgba(56, 189, 248, 0.15);
    }


    /* ============================================
       BUTTONS
    ============================================ */

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 48px;
        border: 1px solid #334155;
        transition: all 0.2s ease;
    }


    .stButton > button:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }


    .stButton > button[kind="primary"] {
        background:
            linear-gradient(
                90deg,
                #2563eb,
                #0ea5e9
            );

        border: none;
    }


    /* ============================================
       TABS
    ============================================ */

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }


    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 10px;
        padding-left: 25px;
        padding-right: 25px;
    }


    /* ============================================
       SIDEBAR
    ============================================ */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0b1220,
                #111827
            );
    }


    /* ============================================
       METRICS
    ============================================ */

    [data-testid="stMetric"] {
        background:
            rgba(30, 41, 59, 0.65);

        border: 1px solid #26364d;

        padding: 18px;

        border-radius: 14px;
    }


    /* ============================================
       INSIGHT CARDS
    ============================================ */

    .insight-card {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =================================================
# SESSION STATE
# =================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if "user" not in st.session_state:
    st.session_state.user = None


# =================================================
# LOGIN PAGE
# =================================================


def login_page():

    st.markdown("<br>", unsafe_allow_html=True)

    # BRANDING

    st.markdown(
        """
        <div class='main-title'>
            ⏱️ SmartAttend
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='sub-title'>
            Smart Employee Attendance & Workforce Analytics System
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CENTER LOGIN SECTION

    left_space, main_content, right_space = st.columns([1, 1.25, 1])

    with main_content:

        tab1, tab2 = st.tabs(
            [
                "🔐 Login",
                "📝 Register",
            ]
        )

        # ==========================================
        # LOGIN
        # ==========================================

        with tab1:

            st.markdown("### 👋 Welcome Back")

            st.caption("Sign in to access your SmartAttend workspace.")

            st.markdown("<br>", unsafe_allow_html=True)

            email = st.text_input(
                "Email Address",
                placeholder="Enter your email",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(
                "🚀 Login to SmartAttend",
                use_container_width=True,
                type="primary",
            ):

                if not email or not password:

                    st.warning("Please enter your email and password.")

                else:

                    user = login_user(
                        email,
                        password,
                    )

                    if user:

                        st.session_state.logged_in = True

                        st.session_state.user = user

                        st.success(f"Welcome back, {user[1]}! 🎉")

                        st.rerun()

                    else:

                        st.error("Invalid email or password.")

            st.markdown("<br>", unsafe_allow_html=True)

            st.caption("🔒 Your credentials are securely protected.")

        # ==========================================
        # REGISTER
        # ==========================================

        with tab2:

            st.markdown("### ✨ Create Your Account")

            st.caption("Register as an employee and start managing your attendance.")

            st.markdown("<br>", unsafe_allow_html=True)

            name = st.text_input(
                "Full Name",
                placeholder="Enter your full name",
                key="register_name",
            )

            register_email = st.text_input(
                "Email Address",
                placeholder="Enter your email address",
                key="register_email",
            )

            register_password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password",
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Confirm your password",
                key="confirm_password",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(
                "✨ Create My Account",
                use_container_width=True,
                type="primary",
            ):

                if not all(
                    [
                        name,
                        register_email,
                        register_password,
                        confirm_password,
                    ]
                ):

                    st.warning("Please fill all fields.")

                elif register_password != confirm_password:

                    st.error("Passwords do not match.")

                elif len(register_password) < 4:

                    st.warning("Password must be at least 4 characters.")

                else:

                    success, message = register_user(
                        name,
                        register_email,
                        register_password,
                    )

                    if success:

                        st.success(message)

                        st.balloons()

                    else:

                        st.error(message)

    # ==========================================
    # BOTTOM FEATURE STRIP
    # ==========================================

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.caption("⚡ Fast & Simple Attendance")

    with col2:

        st.caption("📊 Smart Workforce Analytics")

    with col3:

        st.caption("🔒 Secure Employee Access")


# =================================================
# EMPLOYEE DASHBOARD
# =================================================


def employee_dashboard(user):

    # USER DETAILS

    user_id = user[0]

    user_name = user[1]

    # SIDEBAR

    st.sidebar.title("⏱️ SmartAttend")

    st.sidebar.success(f"👤 {user_name}")

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📋 Attendance History",
            "🏖️ Leave Management",
        ],
    )

    # LOGOUT

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        st.session_state.logged_in = False

        st.session_state.user = None

        st.rerun()

    # =============================================
    # EMPLOYEE HOME DASHBOARD
    # =============================================

    if menu == "🏠 Dashboard":

        st.title(f"Welcome back, {user_name} 👋")

        st.caption(f"📅 {date.today().strftime('%A, %d %B %Y')}")

        today_data = get_today_attendance(user_id)

        if today_data:

            status = today_data[4]

            check_in_time = today_data[1] or "--"

            check_out_time = today_data[2] or "--"

            working_hours = today_data[3] or 0

        else:

            status = "Not Checked In"

            check_in_time = "--"

            check_out_time = "--"

            working_hours = 0

        # METRICS

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Today's Status",
                status,
            )

        with col2:

            st.metric(
                "Check-In",
                check_in_time,
            )

        with col3:

            st.metric(
                "Check-Out",
                check_out_time,
            )

        with col4:

            st.metric(
                "Working Hours",
                f"{working_hours} hrs",
            )

        st.divider()

        # =========================================
        # CHECK-IN / CHECK-OUT
        # =========================================

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🟢 CHECK IN",
                use_container_width=True,
            ):

                success, message = check_in(user_id)

                if success:

                    st.success(message)

                    st.balloons()

                    st.rerun()

                else:

                    st.warning(message)

        with col2:

            if st.button(
                "🔴 CHECK OUT",
                use_container_width=True,
            ):

                success, message = check_out(user_id)

                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.warning(message)

        st.divider()

        # =========================================
        # ATTENDANCE ANALYTICS
        # =========================================

        records = get_employee_attendance(user_id)

        if records:

            df = pd.DataFrame(
                records,
                columns=[
                    "Date",
                    "Check In",
                    "Check Out",
                    "Working Hours",
                    "Status",
                ],
            )

            total_days = len(df)

            present_days = len(
                df[
                    df["Status"].isin(
                        [
                            "Present",
                            "Late",
                        ]
                    )
                ]
            )

            attendance_percentage = round(
                (present_days / total_days) * 100,
                1,
            )

            late_days = len(df[df["Status"] == "Late"])

            avg_hours = round(
                df["Working Hours"].mean(),
                2,
            )

            attendance_score = max(
                0,
                attendance_percentage - (late_days * 2),
            )

            st.subheader("📊 My Attendance Analytics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Attendance %",
                    f"{attendance_percentage}%",
                )

            with col2:

                st.metric(
                    "Attendance Score",
                    f"{attendance_score}%",
                )

            with col3:

                st.metric(
                    "Late Arrivals",
                    late_days,
                )

            with col4:

                st.metric(
                    "Average Working Hours",
                    f"{avg_hours} hrs",
                )

            # PERFORMANCE MESSAGE

            if attendance_score >= 90:

                st.success("🏆 Excellent! You have an outstanding attendance record.")

            elif attendance_score >= 75:

                st.info("👍 Good attendance! Keep maintaining your consistency.")

            else:

                st.warning("⚠️ Your attendance needs improvement.")

            chart = px.pie(
                df,
                names="Status",
                title="My Attendance Distribution",
            )

            st.plotly_chart(
                chart,
                use_container_width=True,
            )

    # =============================================
    # ATTENDANCE HISTORY
    # =============================================

    elif menu == "📋 Attendance History":

        st.title("📋 Attendance History")

        records = get_employee_attendance(user_id)

        if records:

            df = pd.DataFrame(
                records,
                columns=[
                    "Date",
                    "Check In",
                    "Check Out",
                    "Working Hours",
                    "Status",
                ],
            )

            st.dataframe(
                df,
                use_container_width=True,
            )

            # DOWNLOAD REPORT

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download My Attendance Report",
                data=csv,
                file_name="my_attendance_report.csv",
                mime="text/csv",
                use_container_width=True,
            )

        else:

            st.info("No attendance records available.")

    # =============================================
    # LEAVE MANAGEMENT
    # =============================================

    elif menu == "🏖️ Leave Management":

        st.title("🏖️ Leave Management")

        tab1, tab2 = st.tabs(
            [
                "Apply Leave",
                "My Leave Requests",
            ]
        )

        # APPLY LEAVE

        with tab1:

            leave_date = st.date_input("Select Leave Date")

            leave_type = st.selectbox(
                "Leave Type",
                [
                    "Casual Leave",
                    "Sick Leave",
                    "Unpaid Leave",
                ],
            )

            reason = st.text_area("Reason")

            if st.button(
                "Submit Leave Request",
                use_container_width=True,
            ):

                if not reason:

                    st.warning("Please enter a reason.")

                else:

                    apply_leave(
                        user_id,
                        leave_date,
                        leave_type,
                        reason,
                    )

                    st.success("Leave request submitted successfully!")

        # LEAVE HISTORY

        with tab2:

            leaves = get_user_leaves(user_id)

            if leaves:

                df = pd.DataFrame(
                    leaves,
                    columns=[
                        "Leave Date",
                        "Leave Type",
                        "Reason",
                        "Status",
                    ],
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                )

            else:

                st.info("No leave requests yet.")


# =================================================
# HR DASHBOARD
# =================================================


def hr_dashboard(user):

    # SIDEBAR

    st.sidebar.title("👔 SmartAttend HR")

    st.sidebar.success(f"👤 {user[1]}")

    menu = st.sidebar.radio(
        "HR Navigation",
        [
            "📊 Dashboard",
            "👥 Employees",
            "📋 Attendance",
            "🏖️ Leave Requests",
        ],
    )

    # LOGOUT

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        st.session_state.logged_in = False

        st.session_state.user = None

        st.rerun()

    # =============================================
    # HR DASHBOARD
    # =============================================

    if menu == "📊 Dashboard":

        st.title("📊 HR Workforce Dashboard")

        st.caption("Real-time workforce overview and attendance insights")

        employees = get_all_employees()

        attendance = get_all_attendance()

        # TOTAL EMPLOYEES

        total_employees = len([emp for emp in employees if emp[3] == "Employee"])

        # TODAY'S DATA

        today = date.today().strftime("%Y-%m-%d")

        today_records = [record for record in attendance if record[2] == today]

        present_today = len(
            [
                record
                for record in today_records
                if record[6]
                in [
                    "Present",
                    "Late",
                ]
            ]
        )

        late_today = len([record for record in today_records if record[6] == "Late"])

        currently_working = len(
            [record for record in today_records if record[4] is None]
        )

        # METRICS

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Employees",
                total_employees,
            )

        with col2:

            st.metric(
                "Present Today",
                present_today,
            )

        with col3:

            st.metric(
                "Late Today",
                late_today,
            )

        with col4:

            st.metric(
                "Currently Working",
                currently_working,
            )

        st.divider()

        # =========================================
        # SMART WORKFORCE INSIGHTS
        # =========================================

        if attendance:

            st.subheader("🧠 Smart Workforce Insights")

            df_insights = pd.DataFrame(
                attendance,
                columns=[
                    "Name",
                    "Email",
                    "Date",
                    "Check In",
                    "Check Out",
                    "Working Hours",
                    "Status",
                ],
            )

            # LATE CHECK-INS

            late_count = len(df_insights[df_insights["Status"] == "Late"])

            # TOP EMPLOYEE

            attendance_score = (
                df_insights.groupby("Name")
                .size()
                .reset_index(name="Attendance Days")
                .sort_values(
                    "Attendance Days",
                    ascending=False,
                )
            )

            best_employee = attendance_score.iloc[0]["Name"]

            best_days = attendance_score.iloc[0]["Attendance Days"]

            # AVERAGE WORKING HOURS

            avg_work_hours = round(
                df_insights["Working Hours"].mean(),
                2,
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.info(f"⏰ Total Late Check-ins: {late_count}")

            with col2:

                st.success(
                    f"🏆 Top Performer: {best_employee} "
                    f"({best_days} attendance days)"
                )

            with col3:

                st.info(f"📊 Average Working Hours: " f"{avg_work_hours} hrs")

            st.divider()

            # =====================================
            # ANALYTICS CHARTS
            # =====================================

            col1, col2 = st.columns(2)

            with col1:

                status_chart = px.pie(
                    df_insights,
                    names="Status",
                    title="Overall Attendance Distribution",
                )

                st.plotly_chart(
                    status_chart,
                    use_container_width=True,
                )

            with col2:

                working_df = (
                    df_insights.groupby("Name")["Working Hours"].sum().reset_index()
                )

                hours_chart = px.bar(
                    working_df,
                    x="Name",
                    y="Working Hours",
                    title="Total Working Hours by Employee",
                )

                st.plotly_chart(
                    hours_chart,
                    use_container_width=True,
                )

        else:

            st.info("No attendance data available yet.")

    # =============================================
    # EMPLOYEE DIRECTORY
    # =============================================

    elif menu == "👥 Employees":

        st.title("👥 Employee Directory")

        employees = get_all_employees()

        df = pd.DataFrame(
            employees,
            columns=[
                "ID",
                "Name",
                "Email",
                "Role",
            ],
        )

        st.dataframe(
            df,
            use_container_width=True,
        )

    # =============================================
    # ATTENDANCE REPORT
    # =============================================

    elif menu == "📋 Attendance":

        st.title("📋 Attendance Report")

        records = get_all_attendance()

        if records:

            df = pd.DataFrame(
                records,
                columns=[
                    "Name",
                    "Email",
                    "Date",
                    "Check In",
                    "Check Out",
                    "Working Hours",
                    "Status",
                ],
            )

            # FILTERS

            col1, col2 = st.columns(2)

            with col1:

                selected_status = st.multiselect(
                    "Filter by Status",
                    options=df["Status"].unique(),
                    default=df["Status"].unique(),
                )

            with col2:

                selected_employee = st.multiselect(
                    "Filter by Employee",
                    options=df["Name"].unique(),
                    default=df["Name"].unique(),
                )

            filtered_df = df[
                (df["Status"].isin(selected_status))
                & (df["Name"].isin(selected_employee))
            ]

            st.dataframe(
                filtered_df,
                use_container_width=True,
            )

            # DOWNLOAD CSV

            csv = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download Attendance Report (CSV)",
                data=csv,
                file_name="smartattend_attendance_report.csv",
                mime="text/csv",
                use_container_width=True,
            )

        else:

            st.info("No attendance records available.")

    # =============================================
    # LEAVE REQUESTS
    # =============================================

    elif menu == "🏖️ Leave Requests":

        st.title("🏖️ Employee Leave Requests")

        leaves = get_all_leaves()

        if leaves:

            for leave in leaves:

                leave_id = leave[0]

                with st.expander(f"{leave[1]} — " f"{leave[3]} — " f"{leave[4]}"):

                    st.write(f"**Employee Email:** {leave[2]}")

                    st.write(f"**Reason:** {leave[5]}")

                    st.write(f"**Current Status:** {leave[6]}")

                    if leave[6] == "Pending":

                        col1, col2 = st.columns(2)

                        with col1:

                            if st.button(
                                "✅ Approve",
                                key=f"approve_{leave_id}",
                                use_container_width=True,
                            ):

                                update_leave_status(
                                    leave_id,
                                    "Approved",
                                )

                                st.success("Leave approved successfully!")

                                st.rerun()

                        with col2:

                            if st.button(
                                "❌ Reject",
                                key=f"reject_{leave_id}",
                                use_container_width=True,
                            ):

                                update_leave_status(
                                    leave_id,
                                    "Rejected",
                                )

                                st.warning("Leave rejected.")

                                st.rerun()

        else:

            st.info("No leave requests available.")


# =================================================
# MAIN APPLICATION
# =================================================

if not st.session_state.logged_in:

    login_page()


else:

    user = st.session_state.user

    if user[3] == "HR":

        hr_dashboard(user)

    else:

        employee_dashboard(user)
