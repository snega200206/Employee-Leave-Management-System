
import os
import sys
import hashlib
import secrets
import hmac
import sqlite3
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from io import BytesIO
import pandas as pd

from flask import send_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from database.database import connect_db

from database.database import create_tables

create_tables()

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    secrets.token_hex(32)
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)


# PASSWORD HASHING
def hash_password(password):

    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        100000
    )

    return salt + "$" + hashed.hex()


# PASSWORD VERIFICATION
def verify_password(password, stored_hash):

    try:
        salt, old_hash = stored_hash.split("$")

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt),
            100000
        )

        return hmac.compare_digest(
            new_hash.hex(),
            old_hash
        )

    except (ValueError, AttributeError):
        return False


# CREATE ADMIN ACCOUNT IF NOT EXISTS
def create_admin():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE username = ?",
        ("admin",)
    )

    existing = cursor.fetchone()

    if existing is None:

        cursor.execute("""
            INSERT INTO users
            (username, password_hash, role, employee_id)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            hash_password("Admin@123"),
            "Admin",
            None
        ))

    conn.commit()
    conn.close()


# LOGIN VALIDATION
def login_user(username, password, selected_role):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, password_hash, role, employee_id
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    if user is None:
        conn.close()
        return None

    db_username, password_hash, role, employee_id = user

    if role.lower() != selected_role.lower():
        conn.close()
        return None

    if not verify_password(password, password_hash):
        conn.close()
        return None

    full_name = db_username

    if role.lower() == "employee":

        if not employee_id:
            conn.close()
            return None

        cursor.execute("""
            SELECT full_name
            FROM employees
            WHERE employee_id = ?
            AND is_active = 1
        """, (employee_id,))

        employee = cursor.fetchone()

        if employee is None:
            conn.close()
            return None

        full_name = employee[0]

    conn.close()

    return {
        "username": db_username,
        "role": role,
        "employee_id": employee_id,
        "full_name": full_name
    }


# HOME / LOGIN PAGE
@app.route("/")
def home():

    if "username" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# LOGIN ROUTE
@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    selected_role = request.form.get("role", "")

    if not username or not password:
        flash("Please enter username and password.")
        return redirect(url_for("home"))

    if selected_role not in ["Admin", "Employee"]:
        flash("Please select a valid login role.")
        return redirect(url_for("home"))

    user = login_user(
        username,
        password,
        selected_role
    )

    if user is None:
        flash("Invalid username, password or role.")
        return redirect(url_for("home"))

    session.clear()

    session["username"] = user["username"]
    session["role"] = user["role"]
    session["employee_id"] = user["employee_id"]
    session["full_name"] = user["full_name"]

    return redirect(url_for("dashboard"))


# DASHBOARD ROUTE
@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("home"))

    role = session.get("role", "")
    employee_id = session.get("employee_id")
    full_name = session.get("full_name", session["username"])

    conn = connect_db()
    cursor = conn.cursor()

    # ADMIN DASHBOARD
    if role.lower() == "admin":

        cursor.execute("""
            SELECT COUNT(*)
            FROM employees
            WHERE is_active = 1
        """)
        employees = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM leave_applications
            WHERE status = 'Pending'
        """)
        pending = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM leave_applications
            WHERE status = 'Approved'
        """)
        approved = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM leave_applications
            WHERE status = 'Rejected'
        """)
        rejected = cursor.fetchone()[0]

        conn.close()

        return render_template(
            "dashboard.html",
            username=session["username"],
            full_name=full_name,
            role="Admin",

            # Existing template variable names
            employees=employees,
            pending=pending,
            approved=approved,
            rejected=rejected,

            # Dashboard template compatibility
            total_employees=employees,
            pending_leaves=pending,
            approved_leaves=approved,
            rejected_leaves=rejected
        )

    # EMPLOYEE DASHBOARD
    elif role.lower() == "employee":

        if not employee_id:
            conn.close()
            session.clear()
            flash("Employee account not found. Please login again.")
            return redirect(url_for("home"))

        cursor.execute("""
            SELECT employee_id, full_name, department, designation,
                   email, phone, joining_date, is_active
            FROM employees
            WHERE employee_id = ?
            AND is_active = 1
        """, (employee_id,))

        employee = cursor.fetchone()

        if employee is None:
            conn.close()
            session.clear()
            flash("Employee account is inactive or not found.")
            return redirect(url_for("home"))


        employee = {
            "employee_id": employee[0],
            "full_name": employee[1],
            "department": employee[2],
            "designation": employee[3],
            "email": employee[4],
            "phone": employee[5],
            "joining_date": employee[6],
            "is_active": employee[7]
        }

        cursor.execute("""
            SELECT COUNT(*)
            FROM leave_applications
            WHERE employee_id = ?
            AND status = 'Pending'
        """, (employee_id,))
        pending = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM leave_applications
            WHERE employee_id = ?
            AND status = 'Approved'
        """, (employee_id,))
        approved = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM leave_applications
            WHERE employee_id = ?
            AND status = 'Rejected'
        """, (employee_id,))
        rejected = cursor.fetchone()[0]

        conn.close()

        return render_template(
            "dashboard.html",
            username=session["username"],
            full_name=employee["full_name"],
            role="Employee",
            employee=employee,

            pending=pending,
            approved=approved,
            rejected=rejected,

            pending_leaves=pending,
            approved_leaves=approved,
            rejected_leaves=rejected
        )

    else:

        conn.close()
        session.clear()
        flash("Invalid user role.")
        return redirect(url_for("home"))


# EMPLOYEE MANAGEMENT PAGE + SEARCH
@app.route("/employees")
def employee_management():

    if "username" not in session:
        return redirect(url_for("home"))

    if session.get("role", "").lower() != "admin":
        flash("Access denied. Admin login required.")
        return redirect(url_for("dashboard"))

    search = request.args.get("search", "").strip()

    conn = connect_db()
    cursor = conn.cursor()

    if search:

        search_value = "%" + search + "%"

        cursor.execute("""
            SELECT employee_id, full_name, department, designation,
                   email, phone, joining_date
            FROM employees
            WHERE is_active = 1
            AND (
                employee_id LIKE ?
                OR full_name LIKE ?
                OR department LIKE ?
            )
            ORDER BY employee_id
        """, (
            search_value,
            search_value,
            search_value
        ))

    else:

        cursor.execute("""
            SELECT employee_id, full_name, department, designation,
                   email, phone, joining_date
            FROM employees
            WHERE is_active = 1
            ORDER BY employee_id
        """)

    employees_list = cursor.fetchall()

    conn.close()

    return render_template(
        "employee.html",
        employees=employees_list,
        search=search,
        full_name=session.get("full_name", "Admin"),
        role="Admin"
    )


# ADD EMPLOYEE
@app.route("/employees/add", methods=["POST"])
def add_employee():

    if "username" not in session:
        return redirect(url_for("home"))

    if session.get("role", "").lower() != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    employee_id = request.form.get("employee_id", "").strip().upper()
    full_name = request.form.get("full_name", "").strip()
    department = request.form.get("department", "").strip()
    designation = request.form.get("designation", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    joining_date = request.form.get("joining_date", "").strip()

    if not all([
        employee_id,
        full_name,
        department,
        designation,
        email,
        phone,
        joining_date
    ]):
        flash("Please fill in all employee details.")
        return redirect(url_for("employee_management"))

    if not employee_id.startswith("EMP") or len(employee_id) <= 3:
        flash("Employee ID must start with EMP. Example: EMP013.")
        return redirect(url_for("employee_management"))

    if "@" not in email or "." not in email:
        flash("Please enter a valid email address.")
        return redirect(url_for("employee_management"))

    try:
        datetime.strptime(joining_date, "%Y-%m-%d")
    except ValueError:
        flash("Joining date must use YYYY-MM-DD format.")
        return redirect(url_for("employee_management"))

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO employees
            (
                employee_id, full_name, department,
                designation, email, phone, joining_date,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            employee_id,
            full_name,
            department,
            designation,
            email,
            phone,
            joining_date
        ))
        # CREATE DEFAULT LEAVE BALANCE
        leave_allocations = [
            ("Casual", 12),
            ("Sick", 12),
            ("Earned", 15)
        ]

        for leave_type, total_days in leave_allocations:
            cursor.execute("""
                INSERT INTO leave_balance
                (employee_id, leave_type, total_days, used_days)
                VALUES (?, ?, ?, 0)
            """, (
                employee_id,
                leave_type,
                total_days
            ))

        # Default employee login account
        initial_password = "EMP@" + employee_id[3:]

        cursor.execute("""
            INSERT INTO users
            (username, password_hash, role, employee_id)
            VALUES (?, ?, ?, ?)
        """, (
            employee_id,
            hash_password(initial_password),
            "Employee",
            employee_id
        ))

        conn.commit()

        flash(
            "Employee added successfully. "
            "Username: " + employee_id +
            " | Initial Password: " + initial_password
        )

    except sqlite3.IntegrityError:

        conn.rollback()
        flash("Employee ID, email or username already exists.")

    except Exception as error:

        conn.rollback()
        flash("Unable to add employee: " + str(error))

    finally:
        conn.close()

    return redirect(url_for("employee_management"))


# UPDATE EMPLOYEE
@app.route("/employees/update", methods=["POST"])
def update_employee():

    if "username" not in session:
        return redirect(url_for("home"))

    if session.get("role", "").lower() != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    employee_id = request.form.get("employee_id", "").strip().upper()
    full_name = request.form.get("full_name", "").strip()
    department = request.form.get("department", "").strip()
    designation = request.form.get("designation", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    joining_date = request.form.get("joining_date", "").strip()

    if not all([
        employee_id,
        full_name,
        department,
        designation,
        email,
        phone,
        joining_date
    ]):
        flash("Please fill in all employee details.")
        return redirect(url_for("employee_management"))

    if "@" not in email or "." not in email:
        flash("Please enter a valid email address.")
        return redirect(url_for("employee_management"))

    try:
        datetime.strptime(joining_date, "%Y-%m-%d")
    except ValueError:
        flash("Joining date must use YYYY-MM-DD format.")
        return redirect(url_for("employee_management"))

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE employees
            SET
                full_name = ?,
                department = ?,
                designation = ?,
                email = ?,
                phone = ?,
                joining_date = ?
            WHERE employee_id = ?
            AND is_active = 1
        """, (
            full_name,
            department,
            designation,
            email,
            phone,
            joining_date,
            employee_id
        ))

        if cursor.rowcount == 0:
            conn.rollback()
            flash("Employee not found or already inactive.")
        else:
            conn.commit()
            flash("Employee details updated successfully.")

    except sqlite3.IntegrityError:

        conn.rollback()
        flash("This email address is already used by another employee.")

    except Exception as error:

        conn.rollback()
        flash("Unable to update employee: " + str(error))

    finally:
        conn.close()

    return redirect(url_for("employee_management"))


# DELETE EMPLOYEE - SOFT DELETE
@app.route("/employees/delete", methods=["POST"])
def delete_employee():

    if "username" not in session:
        return redirect(url_for("home"))

    if session.get("role", "").lower() != "admin":
        flash("Access denied.")
        return redirect(url_for("dashboard"))

    employee_id = request.form.get("employee_id", "").strip().upper()

    if not employee_id:
        flash("Please select an employee to delete.")
        return redirect(url_for("employee_management"))

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE employees
            SET is_active = 0
            WHERE employee_id = ?
            AND is_active = 1
        """, (employee_id,))

        if cursor.rowcount == 0:
            conn.rollback()
            flash("Employee not found or already deleted.")
        else:
            conn.commit()
            flash("Employee deleted successfully.")

    except Exception as error:

        conn.rollback()
        flash("Unable to delete employee: " + str(error))

    finally:
        conn.close()

    return redirect(url_for("employee_management"))


# LEAVE APPLICATION PAGE + SUBMISSION
@app.route("/leave-application", methods=["GET", "POST"])
def leave_application():

    if "username" not in session:
        return redirect(url_for("home"))

    role = session.get("role", "").lower()
    employee_id = session.get("employee_id")

    if role not in ["admin", "employee"]:
        session.clear()
        flash("Invalid user role.")
        return redirect(url_for("home"))

    conn = connect_db()
    cursor = conn.cursor()

    # SUBMIT LEAVE APPLICATION
    if request.method == "POST":

        form_employee_id = request.form.get(
            "employee_id", ""
        ).strip().upper()

        leave_type = request.form.get(
            "leave_type", ""
        ).strip()

        from_date = request.form.get(
            "from_date", ""
        ).strip()

        to_date = request.form.get(
            "to_date", ""
        ).strip()

        reason = request.form.get(
            "reason", ""
        ).strip()

        # Employee can apply only for their own ID
        if role == "employee":
            form_employee_id = employee_id

        if not all([
            form_employee_id,
            leave_type,
            from_date,
            to_date,
            reason
        ]):
            conn.close()
            flash("Please fill in all leave application details.")
            return redirect(url_for("leave_application"))

        if leave_type not in ["Casual", "Sick", "Earned"]:
            conn.close()
            flash("Please select a valid leave type.")
            return redirect(url_for("leave_application"))

        # DATE VALIDATION
        try:
            start = datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.strptime(to_date, "%Y-%m-%d").date()

        except ValueError:
            conn.close()
            flash("Please enter valid leave dates.")
            return redirect(url_for("leave_application"))

        if start < datetime.today().date():
            conn.close()
            flash("Past dates are not allowed.")
            return redirect(url_for("leave_application"))

        if end < start:
            conn.close()
            flash("To Date cannot be earlier than From Date.")
            return redirect(url_for("leave_application"))

        # Inclusive calendar days, matching the original application
        total_days = (end - start).days + 1

        try:

            # CHECK ACTIVE EMPLOYEE
            cursor.execute("""
                SELECT employee_id
                FROM employees
                WHERE employee_id = ?
                AND is_active = 1
            """, (form_employee_id,))

            employee = cursor.fetchone()

            if employee is None:
                conn.close()
                flash("Employee not found or inactive.")
                return redirect(url_for("leave_application"))

            # CHECK LEAVE BALANCE
            cursor.execute("""
                SELECT total_days, used_days
                FROM leave_balance
                WHERE employee_id = ?
                AND leave_type = ?
            """, (form_employee_id, leave_type))

            balance = cursor.fetchone()

            if balance is None:
                conn.close()
                flash("Leave balance record not found.")
                return redirect(url_for("leave_application"))

            remaining_days = balance[0] - balance[1]

            if total_days > remaining_days:
                conn.close()
                flash("Insufficient leave balance.")
                return redirect(url_for("leave_application"))

            # CHECK OVERLAPPING PENDING / APPROVED LEAVES
            cursor.execute("""
                SELECT leave_id
                FROM leave_applications
                WHERE employee_id = ?
                AND status IN ('Pending', 'Approved')
                AND from_date <= ?
                AND to_date >= ?
            """, (
                form_employee_id,
                to_date,
                from_date
            ))

            overlap = cursor.fetchone()

            if overlap:
                conn.close()
                flash("Leave dates overlap with an existing request.")
                return redirect(url_for("leave_application"))

            # INSERT LEAVE APPLICATION
            cursor.execute("""
                INSERT INTO leave_applications
                (
                    employee_id,
                    leave_type,
                    from_date,
                    to_date,
                    total_days,
                    reason,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, 'Pending')
            """, (
                form_employee_id,
                leave_type,
                from_date,
                to_date,
                total_days,
                reason
            ))

            conn.commit()

            flash("Leave application submitted successfully.")

        except Exception as error:

            conn.rollback()
            flash("Unable to submit leave application: " + str(error))

        finally:
            conn.close()

        return redirect(url_for("leave_application"))

    # GET: LOAD EMPLOYEES FOR ADMIN
    if role == "admin":

        cursor.execute("""
            SELECT employee_id, full_name
            FROM employees
            WHERE is_active = 1
            ORDER BY employee_id
        """)

        employees = cursor.fetchall()

    else:
        employees = []

    # LOAD LEAVE APPLICATIONS
    if role == "admin":

        cursor.execute("""
            SELECT
                leave_id,
                employee_id,
                leave_type,
                from_date,
                to_date,
                total_days,
                status
            FROM leave_applications
            ORDER BY leave_id DESC
        """)

    else:

        if not employee_id:
            conn.close()
            session.clear()
            flash("Employee account not found. Please login again.")
            return redirect(url_for("home"))

        cursor.execute("""
            SELECT
                leave_id,
                employee_id,
                leave_type,
                from_date,
                to_date,
                total_days,
                status
            FROM leave_applications
            WHERE employee_id = ?
            ORDER BY leave_id DESC
        """, (employee_id,))

    applications = cursor.fetchall()
    conn.close()

    return render_template(
        "leave_application.html",
        employees=employees,
        applications=applications,
        employee_id=employee_id,
        role=session.get("role"),
        full_name=session.get("full_name", session["username"])
    )


# ==========================================
# LEAVE APPROVAL PAGE
# ==========================================

@app.route("/leave-approval")
def leave_approval():

    if "username" not in session:
        return redirect(url_for("home"))

    if session.get("role", "").lower() != "admin":
        flash("Access denied. Admin only.")
        return redirect(url_for("dashboard"))

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            la.leave_id,
            la.employee_id,
            e.full_name,
            la.leave_type,
            la.from_date,
            la.to_date,
            la.total_days,
            la.reason,
            la.status
        FROM leave_applications la
        JOIN employees e
            ON la.employee_id = e.employee_id
        ORDER BY la.leave_id DESC
    """)

    applications = cursor.fetchall()
    conn.close()

    return render_template(
        "leave_approval.html",
        applications=applications,
        full_name=session.get("full_name", session["username"]),
        role=session.get("role")
    )


# ==========================================
# APPROVE LEAVE
# ==========================================

@app.route("/leave-approval/approve/<int:leave_id>", methods=["POST"])
def approve_leave(leave_id):

    if "username" not in session:
        return redirect(url_for("home"))

    if session.get("role", "").lower() != "admin":
        flash("Access denied. Admin only.")
        return redirect(url_for("dashboard"))

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT employee_id, leave_type, total_days, status
            FROM leave_applications
            WHERE leave_id = ?
        """, (leave_id,))

        leave = cursor.fetchone()

        if leave is None:
            raise Exception("Leave application not found.")

        employee_id, leave_type, total_days, status = leave

        if status != "Pending":
            raise Exception("This leave request has already been processed.")

        cursor.execute("""
            UPDATE leave_balance
            SET used_days = used_days + ?
            WHERE employee_id = ?
              AND leave_type = ?
              AND total_days - used_days >= ?
        """, (total_days, employee_id, leave_type, total_days))

        if cursor.rowcount == 0:
            raise Exception("Insufficient leave balance or balance record not found.")

        cursor.execute("""
            UPDATE leave_applications
            SET status = 'Approved',
                reviewed_by = 'admin',
                reviewed_at = CURRENT_TIMESTAMP
            WHERE leave_id = ?
              AND status = 'Pending'
        """, (leave_id,))

        if cursor.rowcount == 0:
            raise Exception("Unable to approve this leave request.")

        conn.commit()
        flash("Leave application approved successfully.")

    except Exception as error:
        conn.rollback()
        flash(str(error))

    finally:
        conn.close()

    return redirect(url_for("leave_approval"))


# ==========================================
# REJECT LEAVE
# ==========================================

@app.route("/leave-approval/reject/<int:leave_id>", methods=["POST"])
def reject_leave(leave_id):

    if "username" not in session:
        return redirect(url_for("home"))

    if session.get("role", "").lower() != "admin":
        flash("Access denied. Admin only.")
        return redirect(url_for("dashboard"))

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE leave_applications
            SET status = 'Rejected',
                reviewed_by = 'admin',
                reviewed_at = CURRENT_TIMESTAMP
            WHERE leave_id = ?
              AND status = 'Pending'
        """, (leave_id,))

        if cursor.rowcount == 0:
            raise Exception("Leave request not found or already processed.")

        conn.commit()
        flash("Leave application rejected successfully.")

    except Exception as error:
        conn.rollback()
        flash(str(error))

    finally:
        conn.close()

    return redirect(url_for("leave_approval"))

# ==========================================
# MY LEAVE HISTORY
# ==========================================

@app.route("/my-leave-history")
def my_leave_history():

    if "username" not in session:
        return redirect(url_for("home"))

    if session.get("role", "").lower() != "employee":
        flash("Access denied. Employee only.")
        return redirect(url_for("dashboard"))

    employee_id = session.get("employee_id")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            leave_id,
            leave_type,
            from_date,
            to_date,
            total_days,
            reason,
            status
        FROM leave_applications
        WHERE employee_id = ?
        ORDER BY leave_id DESC
    """, (employee_id,))

    applications = cursor.fetchall()
    conn.close()

    return render_template(
        "my_leave_history.html",
        applications=applications,
        full_name=session.get("full_name", session["username"]),
        role=session.get("role")
    )

# LEAVE BALANCE PAGE
@app.route("/leave-balance")
def leave_balance():

    if "username" not in session:
        return redirect(url_for("home"))

    role = session.get("role", "").lower()
    employee_id = session.get("employee_id")

    conn = connect_db()
    cursor = conn.cursor()

    if role == "admin":

        cursor.execute("""
            SELECT
                e.employee_id,
                e.full_name,
                lb.leave_type,
                lb.total_days,
                lb.used_days,
                (lb.total_days - lb.used_days) AS remaining_days
            FROM leave_balance lb
            JOIN employees e
                ON lb.employee_id = e.employee_id
            WHERE e.is_active = 1
            ORDER BY e.employee_id, lb.leave_type
        """)

        balances = cursor.fetchall()

        page_title = "EMPLOYEE LEAVE BALANCE"

    elif role == "employee":

        if not employee_id:
            conn.close()
            session.clear()
            flash("Employee account not found. Please login again.")
            return redirect(url_for("home"))

        cursor.execute("""
            SELECT
                e.employee_id,
                e.full_name,
                lb.leave_type,
                lb.total_days,
                lb.used_days,
                (lb.total_days - lb.used_days) AS remaining_days
            FROM leave_balance lb
            JOIN employees e
                ON lb.employee_id = e.employee_id
            WHERE e.employee_id = ?
            AND e.is_active = 1
            ORDER BY lb.leave_type
        """, (employee_id,))

        balances = cursor.fetchall()

        page_title = "MY LEAVE BALANCE"

    else:
        conn.close()
        session.clear()
        flash("Invalid user role.")
        return redirect(url_for("home"))

    conn.close()

    return render_template(
        "leave_balance.html",
        balances=balances,
        page_title=page_title,
        full_name=session.get("full_name", session["username"]),
        role=session.get("role")
    )


# LOGOUT ROUTE
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


@app.route("/reports")
def reports():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        flash("Access denied. Admin only.")
        return redirect(url_for("dashboard"))

    selected = request.args.get("report_type", "All Leaves")

    conn = connect_db()
    cursor = conn.cursor()

    if selected == "All Leaves":
        cursor.execute("""
            SELECT l.leave_id, l.employee_id,
                   e.full_name, l.leave_type,
                   l.from_date, l.to_date,
                   l.total_days, l.status
            FROM leave_applications l
            JOIN employees e
            ON l.employee_id = e.employee_id
            ORDER BY l.leave_id DESC
        """)
    else:
        status = selected.replace(" Leaves", "")

        if status not in ("Pending", "Approved", "Rejected"):
            status = "All"

        if status == "All":
            cursor.execute("""
                SELECT l.leave_id, l.employee_id,
                       e.full_name, l.leave_type,
                       l.from_date, l.to_date,
                       l.total_days, l.status
                FROM leave_applications l
                JOIN employees e
                ON l.employee_id = e.employee_id
                ORDER BY l.leave_id DESC
            """)
        else:
            cursor.execute("""
                SELECT l.leave_id, l.employee_id,
                       e.full_name, l.leave_type,
                       l.from_date, l.to_date,
                       l.total_days, l.status
                FROM leave_applications l
                JOIN employees e
                ON l.employee_id = e.employee_id
                WHERE l.status = ?
                ORDER BY l.leave_id DESC
            """, (status,))

    report_data = cursor.fetchall()
    conn.close()

    return render_template(
        "reports.html",
        report_data=report_data,
        selected=selected
    )


@app.route("/reports/export")
def export_reports():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        flash("Access denied. Admin only.")
        return redirect(url_for("dashboard"))

    selected = request.args.get("report_type", "All Leaves")

    conn = connect_db()
    cursor = conn.cursor()

    if selected == "All Leaves":
        cursor.execute("""
            SELECT l.leave_id, l.employee_id,
                   e.full_name, l.leave_type,
                   l.from_date, l.to_date,
                   l.total_days, l.status
            FROM leave_applications l
            JOIN employees e
            ON l.employee_id = e.employee_id
            ORDER BY l.leave_id DESC
        """)
    else:
        status = selected.replace(" Leaves", "")

        if status not in ("Pending", "Approved", "Rejected"):
            status = "All"

        if status == "All":
            cursor.execute("""
                SELECT l.leave_id, l.employee_id,
                       e.full_name, l.leave_type,
                       l.from_date, l.to_date,
                       l.total_days, l.status
                FROM leave_applications l
                JOIN employees e
                ON l.employee_id = e.employee_id
                ORDER BY l.leave_id DESC
            """)
        else:
            cursor.execute("""
                SELECT l.leave_id, l.employee_id,
                       e.full_name, l.leave_type,
                       l.from_date, l.to_date,
                       l.total_days, l.status
                FROM leave_applications l
                JOIN employees e
                ON l.employee_id = e.employee_id
                WHERE l.status = ?
                ORDER BY l.leave_id DESC
            """, (status,))

    report_data = cursor.fetchall()
    conn.close()

    columns = [
        "Leave ID",
        "Employee ID",
        "Employee Name",
        "Leave Type",
        "From Date",
        "To Date",
        "Days",
        "Status"
    ]

    df = pd.DataFrame(report_data, columns=columns)

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Leave_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )



# RUN WEBSITE

create_admin()

if __name__ == "__main__":
    print("Employee Leave Management Website Started")
    print("Open Chrome: http://127.0.0.1:5000")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
