
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, BASE_DIR)

from database.database import connect_db
from modules.app_header import add_app_header


# DARK NEON 2026 THEME
BG_COLOR = "#050B1E"
HEADER_COLOR = "#080F2B"
CARD_COLOR = "#111D3D"
NEON_BLUE = "#00D9FF"
NEON_PURPLE = "#8B5CF6"
WHITE = "#FFFFFF"
TEXT_COLOR = "#DCEBFF"
SUBTITLE_COLOR = "#A5CFFF"
INPUT_COLOR = "#09152E"


def show_leave_application(parent, employee_id=None):

    # employee_id is None for Admin.
    # employee_id has a value for Employee.

    is_employee = employee_id is not None

    window = tk.Toplevel(parent)
    window.title("Employee Leave Application")
    window.geometry("1100x700")
    window.minsize(1000, 650)
    window.configure(bg=BG_COLOR)

    # DIT COMMON HEADER
    add_app_header(window)

    # TREEVIEW STYLE
    style = ttk.Style(window)
    style.theme_use("clam")

    style.configure(
        "Leave.Treeview",
        background=CARD_COLOR,
        foreground=TEXT_COLOR,
        fieldbackground=CARD_COLOR,
        rowheight=32,
        font=("Arial", 10),
        borderwidth=0
    )

    style.configure(
        "Leave.Treeview.Heading",
        background=HEADER_COLOR,
        foreground=NEON_BLUE,
        font=("Arial", 10, "bold"),
        relief="flat",
        padding=8
    )

    style.map(
        "Leave.Treeview",
        background=[("selected", "#263D70")],
        foreground=[("selected", WHITE)]
    )

    style.configure(
        "Leave.TCombobox",
        fieldbackground=INPUT_COLOR,
        background=HEADER_COLOR,
        foreground=WHITE,
        arrowcolor=NEON_BLUE,
        bordercolor=NEON_PURPLE,
        lightcolor=NEON_BLUE,
        darkcolor=NEON_PURPLE
    )

    style.map(
        "Leave.TCombobox",
        fieldbackground=[("readonly", INPUT_COLOR)],
        foreground=[("readonly", WHITE)],
        selectbackground=[("readonly", INPUT_COLOR)],
        selectforeground=[("readonly", WHITE)]
    )

    # PAGE HEADING
    tk.Label(
        window,
        text="EMPLOYEE LEAVE APPLICATION",
        font=("Arial", 19, "bold"),
        bg=BG_COLOR,
        fg=NEON_BLUE,
        pady=2
    ).pack(fill="x")

    # FORM
    form = tk.Frame(
        window,
        bg=CARD_COLOR,
        padx=15,
        pady=2,
        highlightbackground=NEON_PURPLE,
        highlightthickness=1
    )
    form.pack(fill="x", padx=20, pady=3)

    # EMPLOYEE ID LABEL
    tk.Label(
        form,
        text="Employee ID",
        bg=CARD_COLOR,
        fg=WHITE,
        font=("Arial", 11, "bold")
    ).grid(row=0, column=0, padx=8, pady=2)

    emp_id = tk.Entry(
        form,
        width=25,
        font=("Arial", 10),
        bg=INPUT_COLOR,
        fg=WHITE,
        insertbackground=NEON_BLUE,
        relief="flat",
        highlightbackground=NEON_PURPLE,
        highlightcolor=NEON_BLUE,
        highlightthickness=1
    )
    emp_id.grid(row=0, column=1, padx=8, pady=2, ipady=2)

    # EMPLOYEE ID RESTRICTION
    if is_employee:

        emp_id.insert(0, employee_id)
        emp_id.config(state="disabled")

    # LEAVE TYPE
    tk.Label(
        form,
        text="Leave Type",
        bg=CARD_COLOR,
        fg=WHITE,
        font=("Arial", 11, "bold")
    ).grid(row=1, column=0, padx=8, pady=2)

    leave_type = ttk.Combobox(
        form,
        values=["Casual", "Sick", "Earned"],
        state="readonly",
        width=22,
        style="Leave.TCombobox"
    )
    leave_type.grid(row=1, column=1, padx=10, pady=5)
    leave_type.set("Casual")

    # FROM DATE
    tk.Label(
        form,
        text="From Date (YYYY-MM-DD)",
        bg=CARD_COLOR,
        fg=WHITE,
        font=("Arial", 10, "bold")
    ).grid(row=2, column=0, padx=10, pady=5)

    from_date = tk.Entry(
        form,
        width=25,
        font=("Arial", 10),
        bg=INPUT_COLOR,
        fg=WHITE,
        insertbackground=NEON_BLUE,
        relief="flat",
        highlightbackground=NEON_PURPLE,
        highlightcolor=NEON_BLUE,
        highlightthickness=1
    )
    from_date.grid(row=2, column=1, padx=10, pady=5, ipady=3)

    # TO DATE
    tk.Label(
        form,
        text="To Date (YYYY-MM-DD)",
        bg=CARD_COLOR,
        fg=WHITE,
        font=("Arial", 10, "bold")
    ).grid(row=3, column=0, padx=10, pady=5)

    to_date = tk.Entry(
        form,
        width=25,
        font=("Arial", 10),
        bg=INPUT_COLOR,
        fg=WHITE,
        insertbackground=NEON_BLUE,
        relief="flat",
        highlightbackground=NEON_PURPLE,
        highlightcolor=NEON_BLUE,
        highlightthickness=1
    )
    to_date.grid(row=3, column=1, padx=10, pady=5, ipady=3)

    # REASON
    tk.Label(
        form,
        text="Leave Reason",
        bg=CARD_COLOR,
        fg=WHITE,
        font=("Arial", 10, "bold")
    ).grid(row=4, column=0, padx=10, pady=5)

    reason = tk.Entry(
        form,
        width=40,
        font=("Arial", 10),
        bg=INPUT_COLOR,
        fg=WHITE,
        insertbackground=NEON_BLUE,
        relief="flat",
        highlightbackground=NEON_PURPLE,
        highlightcolor=NEON_BLUE,
        highlightthickness=1
    )
    reason.grid(row=4, column=1, padx=10, pady=5, ipady=3)

    # LEAVE TABLE
    table_frame = tk.Frame(
        window,
        bg=BG_COLOR,
        highlightbackground=NEON_BLUE,
        highlightthickness=1
    )
    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=3
    )

    columns = (
        "Leave ID",
        "Employee ID",
        "Leave Type",
        "From Date",
        "To Date",
        "Days",
        "Status"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Leave.Treeview",
        height=12
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=125, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # LOAD LEAVE RECORDS
    def load_leaves():

        for item in tree.get_children():
            tree.delete(item)

        conn = connect_db()
        cursor = conn.cursor()

        try:

            if is_employee:

                cursor.execute("""
                    SELECT leave_id, employee_id, leave_type,
                           from_date, to_date, total_days, status
                    FROM leave_applications
                    WHERE employee_id = ?
                    ORDER BY leave_id DESC
                """, (employee_id,))

            else:

                cursor.execute("""
                    SELECT leave_id, employee_id, leave_type,
                           from_date, to_date, total_days, status
                    FROM leave_applications
                    ORDER BY leave_id DESC
                """)

            records = cursor.fetchall()

            for record in records:
                tree.insert("", "end", values=record)

        finally:
            conn.close()

    # SUBMIT LEAVE
    def submit_leave():

        if is_employee:
            # Employee ID is always taken from login session.
            employee = employee_id
        else:
            employee = emp_id.get().strip()

        selected_type = leave_type.get()
        start = from_date.get().strip()
        end = to_date.get().strip()
        leave_reason = reason.get().strip()

        if not all([
            employee,
            selected_type,
            start,
            end,
            leave_reason
        ]):
            messagebox.showwarning(
                "Warning",
                "Please fill all details",
                parent=window
            )
            return

        try:

            start_date = datetime.strptime(
                start, "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end, "%Y-%m-%d"
            ).date()

            if end_date < start_date:
                messagebox.showerror(
                    "Invalid Date",
                    "To Date cannot be earlier than From Date",
                    parent=window
                )
                return

            if start_date < datetime.today().date():
                messagebox.showerror(
                    "Invalid Date",
                    "Past leave dates are not allowed",
                    parent=window
                )
                return

            days = (end_date - start_date).days + 1

        except ValueError:

            messagebox.showerror(
                "Invalid Date",
                "Enter dates in YYYY-MM-DD format",
                parent=window
            )
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:

            # CHECK EMPLOYEE
            cursor.execute("""
                SELECT employee_id
                FROM employees
                WHERE employee_id = ?
                AND is_active = 1
            """, (employee,))

            if cursor.fetchone() is None:

                messagebox.showerror(
                    "Error",
                    "Employee ID not found or inactive",
                    parent=window
                )
                return

            # CHECK LEAVE BALANCE
            cursor.execute("""
                SELECT total_days - used_days
                FROM leave_balance
                WHERE employee_id = ?
                AND leave_type = ?
            """, (employee, selected_type))

            balance = cursor.fetchone()

            if balance is None:

                messagebox.showerror(
                    "Error",
                    "Leave balance record not found",
                    parent=window
                )
                return

            if balance[0] < days:

                messagebox.showerror(
                    "Insufficient Balance",
                    "Available leave balance is not enough",
                    parent=window
                )
                return

            # CHECK OVERLAPPING REQUESTS
            cursor.execute("""
                SELECT COUNT(*)
                FROM leave_applications
                WHERE employee_id = ?
                AND status IN ('Pending', 'Approved')
                AND from_date <= ?
                AND to_date >= ?
            """, (employee, end, start))

            if cursor.fetchone()[0] > 0:

                messagebox.showerror(
                    "Error",
                    "Leave dates overlap with an existing request",
                    parent=window
                )
                return

            # SAVE APPLICATION
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
                employee,
                selected_type,
                start,
                end,
                days,
                leave_reason
            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Leave application submitted successfully!",
                parent=window
            )

            # CLEAR FORM
            if not is_employee:
                emp_id.delete(0, tk.END)

            from_date.delete(0, tk.END)
            to_date.delete(0, tk.END)
            reason.delete(0, tk.END)

            load_leaves()

        except Exception as e:

            conn.rollback()

            messagebox.showerror(
                "Database Error",
                str(e),
                parent=window
            )

        finally:
            conn.close()

    # SUBMIT BUTTON
    tk.Button(
        form,
        text="SUBMIT LEAVE",
        width=20,
        bg="#00B982",
        fg="#050B1E",
        activebackground="#00D68F",
        activeforeground=WHITE,
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
        command=submit_leave
    ).grid(row=5, column=1, pady=3, ipady=3)

    # LOAD RECORDS
    load_leaves()
