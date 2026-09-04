import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_NAME = "smartattend.db"


def get_connection():
    """Create database connection."""
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def hash_password(password):
    """Hash password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_database():
    """Create all required database tables."""

    conn = get_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Employee',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ATTENDANCE TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            check_in TEXT,
            check_out TEXT,
            working_hours REAL DEFAULT 0,
            status TEXT DEFAULT 'Absent',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # LEAVES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            leave_date TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

    create_default_hr()
    create_demo_attendance_data()


def create_default_hr():
    """Create default HR account for testing."""

    conn = get_connection()
    cursor = conn.cursor()

    email = "hr@smartattend.com"

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))

    if cursor.fetchone() is None:

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """,
            ("HR Admin", email, hash_password("admin123"), "HR"),
        )

        conn.commit()

    conn.close()


def create_demo_attendance_data():
    """
    Create realistic historical attendance data.
    This runs safely without duplicating existing records.
    """

    conn = get_connection()
    cursor = conn.cursor()

    demo_employees = ["hitsaksham23@gmail.com", "rahul@test.com", "priya@test.com"]

    # Get employee IDs
    employees = []

    for email in demo_employees:

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))

        employee = cursor.fetchone()

        if employee:
            employees.append(employee[0])

    if not employees:

        conn.close()
        return

    today = datetime.now().date()

    # Historical attendance patterns
    demo_patterns = [
        ("09:05:00", "17:35:00", 8.5, "Present"),
        ("09:12:00", "17:45:00", 8.55, "Present"),
        ("09:48:00", "18:10:00", 8.37, "Late"),
        ("09:18:00", "17:40:00", 8.37, "Present"),
        ("09:55:00", "18:25:00", 8.5, "Late"),
        ("09:10:00", "17:50:00", 8.67, "Present"),
        ("09:25:00", "18:00:00", 8.58, "Present"),
    ]

    # Add data for previous 7 days
    for employee_index, user_id in enumerate(employees):

        for day_index in range(1, 8):

            attendance_date = today - timedelta(days=day_index)

            date_string = attendance_date.strftime("%Y-%m-%d")

            # Rotate patterns so every employee
            # has slightly different attendance
            pattern_index = (day_index + employee_index) % len(demo_patterns)

            check_in_time, check_out_time, working_hours, status = demo_patterns[
                pattern_index
            ]

            # Prevent duplicate records
            cursor.execute(
                """
                SELECT id
                FROM attendance
                WHERE user_id = ?
                AND date = ?
            """,
                (user_id, date_string),
            )

            existing = cursor.fetchone()

            if existing is None:

                cursor.execute(
                    """
                    INSERT INTO attendance
                    (
                        user_id,
                        date,
                        check_in,
                        check_out,
                        working_hours,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        date_string,
                        check_in_time,
                        check_out_time,
                        working_hours,
                        status,
                    ),
                )

    conn.commit()
    conn.close()


def register_user(name, email, password):
    """Register a new employee."""

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """,
            (name, email.lower(), hash_password(password), "Employee"),
        )

        conn.commit()

        return True, "Registration successful!"

    except sqlite3.IntegrityError:

        return False, "Email already registered."

    finally:

        conn.close()


def login_user(email, password):
    """Authenticate user."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, role
        FROM users
        WHERE email = ?
        AND password = ?
    """,
        (email.lower(), hash_password(password)),
    )

    user = cursor.fetchone()

    conn.close()

    return user


def check_in(user_id):
    """Employee check-in."""

    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    current_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        """
        SELECT id
        FROM attendance
        WHERE user_id = ?
        AND date = ?
    """,
        (user_id, today),
    )

    existing = cursor.fetchone()

    if existing:

        conn.close()

        return False, "You have already checked in today."

    current_dt = datetime.now()

    # Late after 9:30 AM
    if current_dt.hour > 9 or (current_dt.hour == 9 and current_dt.minute > 30):

        status = "Late"

    else:

        status = "Present"

    cursor.execute(
        """
        INSERT INTO attendance
        (user_id, date, check_in, status)
        VALUES (?, ?, ?, ?)
    """,
        (user_id, today, current_time, status),
    )

    conn.commit()
    conn.close()

    return (True, f"Checked in successfully at {current_time}")


def check_out(user_id):
    """Employee check-out and working hours calculation."""

    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    current_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        """
        SELECT id, check_in, check_out
        FROM attendance
        WHERE user_id = ?
        AND date = ?
    """,
        (user_id, today),
    )

    record = cursor.fetchone()

    if not record:

        conn.close()

        return False, "Please check in first."

    attendance_id, check_in_time, check_out_time = record

    if check_out_time:

        conn.close()

        return False, "You have already checked out today."

    check_in_dt = datetime.strptime(f"{today} {check_in_time}", "%Y-%m-%d %H:%M:%S")

    check_out_dt = datetime.strptime(f"{today} {current_time}", "%Y-%m-%d %H:%M:%S")

    working_hours = round((check_out_dt - check_in_dt).total_seconds() / 3600, 2)

    cursor.execute(
        """
        UPDATE attendance
        SET check_out = ?,
            working_hours = ?
        WHERE id = ?
    """,
        (current_time, working_hours, attendance_id),
    )

    conn.commit()
    conn.close()

    return (True, f"Checked out successfully. Working hours: {working_hours}")


def get_today_attendance(user_id):
    """Get today's attendance."""

    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        """
        SELECT
            date,
            check_in,
            check_out,
            working_hours,
            status
        FROM attendance
        WHERE user_id = ?
        AND date = ?
    """,
        (user_id, today),
    )

    data = cursor.fetchone()

    conn.close()

    return data


def get_employee_attendance(user_id):
    """Get all attendance records of employee."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            date,
            check_in,
            check_out,
            working_hours,
            status
        FROM attendance
        WHERE user_id = ?
        ORDER BY date DESC
    """,
        (user_id,),
    )

    records = cursor.fetchall()

    conn.close()

    return records


def get_all_employees():
    """Get all registered employees."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            role
        FROM users
        ORDER BY id DESC
    """)

    employees = cursor.fetchall()

    conn.close()

    return employees


def get_all_attendance():
    """Get complete attendance report."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            users.name,
            users.email,
            attendance.date,
            attendance.check_in,
            attendance.check_out,
            attendance.working_hours,
            attendance.status
        FROM attendance
        JOIN users
        ON attendance.user_id = users.id
        ORDER BY attendance.date DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def apply_leave(user_id, leave_date, leave_type, reason):
    """Apply for leave."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO leaves
        (
            user_id,
            leave_date,
            leave_type,
            reason
        )
        VALUES (?, ?, ?, ?)
    """,
        (user_id, str(leave_date), leave_type, reason),
    )

    conn.commit()
    conn.close()


def get_user_leaves(user_id):
    """Get employee leave requests."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            leave_date,
            leave_type,
            reason,
            status
        FROM leaves
        WHERE user_id = ?
        ORDER BY leave_date DESC
    """,
        (user_id,),
    )

    records = cursor.fetchall()

    conn.close()

    return records


def get_all_leaves():
    """Get all leave requests for HR."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            leaves.id,
            users.name,
            users.email,
            leaves.leave_date,
            leaves.leave_type,
            leaves.reason,
            leaves.status
        FROM leaves
        JOIN users
        ON leaves.user_id = users.id
        ORDER BY leaves.leave_date DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def update_leave_status(leave_id, status):
    """Approve or reject leave."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE leaves
        SET status = ?
        WHERE id = ?
    """,
        (status, leave_id),
    )

    conn.commit()
    conn.close()
