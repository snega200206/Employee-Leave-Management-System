
import tkinter as tk
from tkinter import messagebox
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from database.database import connect_db
from modules.app_header import add_app_header

# DARK NEON THEME COLORS
BG_COLOR = "#070B18"
CARD_COLOR = "#111A30"
HEADER_COLOR = "#080F2B"
NEON_BLUE = "#00D9FF"
NEON_PURPLE = "#8B5CF6"
WHITE = "#FFFFFF"
TEXT_COLOR = "#A5B4D4"
GREEN = "#00D68F"
RED = "#FF4D6D"


# ADMIN DASHBOARD DATA
def get_dashboard_data():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM employees WHERE is_active = 1"
    )
    employees = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM leave_applications WHERE status='Pending'"
    )
    pending = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM leave_applications WHERE status='Approved'"
    )
    approved = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM leave_applications WHERE status='Rejected'"
    )
    rejected = cursor.fetchone()[0]

    conn.close()

    return employees, pending, approved, rejected


# EMPLOYEE DASHBOARD DATA
def get_employee_dashboard_data(employee_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_id, full_name, department, designation,
               email, phone, joining_date, is_active
        FROM employees
        WHERE employee_id = ? AND is_active = 1
    """, (employee_id,))

    employee = cursor.fetchone()

    if employee is None:
        conn.close()
        return None, 0, 0, 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM leave_applications
        WHERE employee_id = ? AND status = 'Pending'
    """, (employee_id,))
    pending = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM leave_applications
        WHERE employee_id = ? AND status = 'Approved'
    """, (employee_id,))
    approved = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM leave_applications
        WHERE employee_id = ? AND status = 'Rejected'
    """, (employee_id,))
    rejected = cursor.fetchone()[0]

    conn.close()

    return employee, pending, approved, rejected


# MAIN DASHBOARD
def show_dashboard(username="admin", role="Admin", employee_id=None):

    root = tk.Tk()
    root.title("Employee Leave Management System")
    root.geometry("1100x700")
    root.configure(bg=BG_COLOR)

    # LOGOUT FUNCTION
    def logout():

        if messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?",
            parent=root
        ):

            root.destroy()

            from modules.login import show_login
            show_login()

    # ADMIN DASHBOARD
    if role.lower() == "admin":

        # ADMIN HEADER
        add_app_header(root, username)

        tk.Label(
            root,
            text="ADMIN DASHBOARD",
            font=("Arial", 23, "bold"),
            bg=BG_COLOR,
            fg=NEON_BLUE
        ).pack(pady=8)

        employees, pending, approved, rejected = get_dashboard_data()

        stats_frame = tk.Frame(root, bg=BG_COLOR)
        stats_frame.pack(pady=5)

        def create_card(title, value, column):

            card = tk.Frame(
                stats_frame,
                bg=CARD_COLOR,
                width=220,
                height=120,
                bd=0,
                relief="flat",
                highlightbackground=NEON_BLUE if column % 2 == 0 else NEON_PURPLE,
                highlightthickness=1
            )

            card.grid(row=0, column=column, padx=10)
            card.pack_propagate(False)

            tk.Label(
                card,
                text=title,
                font=("Arial", 12, "bold"),
                bg=CARD_COLOR,
                fg=TEXT_COLOR
            ).pack(pady=15)

            value_color = [
                NEON_BLUE,
                "#FBBF24",
                GREEN,
                RED
            ][column]

            tk.Label(
                card,
                text=str(value),
                font=("Arial", 27, "bold"),
                bg=CARD_COLOR,
                fg=value_color
            ).pack()

        create_card("Total Employees", employees, 0)
        create_card("Pending Leaves", pending, 1)
        create_card("Approved Leaves", approved, 2)
        create_card("Rejected Leaves", rejected, 3)

        tk.Label(
            root,
            text="MANAGEMENT OPTIONS",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=NEON_PURPLE
        ).pack(pady=8)

        button_frame = tk.Frame(root, bg=BG_COLOR)
        button_frame.pack(pady=3)

        def open_employee_management():

            from modules.employee import show_employee_window
            show_employee_window(root)

        def open_leave_application():

            from modules.leave_application import show_leave_application
            show_leave_application(root)

        from modules.leave_approval import show_leave_approval
        from modules.leave_balance import show_leave_balance
        from modules.reports import show_reports

        buttons = [
            ("Employee Management", open_employee_management),
            ("Leave Applications", open_leave_application),
            ("Leave Balance", lambda: show_leave_balance(root)),
            ("Reports", lambda: show_reports(root)),
            ("Leave Approval", lambda: show_leave_approval(root))
        ]

        for i, (text, action) in enumerate(buttons):

            if i == 4:
                row = 2
                column = 0
                columnspan = 2
            else:
                row = i // 2
                column = i % 2
                columnspan = 1

            tk.Button(
                button_frame,
                text=text,
                width=25,
                height=2,
                font=("Arial", 11, "bold"),
                bg="#17264A",
                fg=NEON_BLUE,
                activebackground=NEON_PURPLE,
                activeforeground=WHITE,
                relief="flat",
                bd=0,
                highlightbackground=NEON_BLUE,
                highlightcolor=NEON_PURPLE,
                highlightthickness=1,
                cursor="hand2",
                command=action
            ).grid(
                row=row,
                column=column,
                columnspan=columnspan,
                padx=20,
                pady=10
            )

    # EMPLOYEE DASHBOARD
    elif role.lower() == "employee":

        if not employee_id:
            messagebox.showerror(
                "Login Error",
                "Employee ID not found. Please login again.",
                parent=root
            )
            root.destroy()
            return

        employee, pending, approved, rejected = (
            get_employee_dashboard_data(employee_id)
        )

        if employee is None:
            messagebox.showerror(
                "Access Denied",
                "Employee account is inactive or not found.",
                parent=root
            )
            root.destroy()
            return

        (
            emp_id,
            full_name,
            department,
            designation,
            email,
            phone,
            joining_date,
            is_active
        ) = employee

        # EMPLOYEE HEADER
        add_app_header(root, full_name)

        # EMPLOYEE LOGOUT
        welcome_frame = tk.Frame(root, bg=BG_COLOR)
        welcome_frame.pack(fill="x", padx=40, pady=(5, 5))

        tk.Button(
            welcome_frame,
            text="Logout",
            width=12,
            height=1,
            font=("Arial", 10, "bold"),
            bg="#401B35",
            fg=RED,
            activebackground=RED,
            activeforeground=WHITE,
            relief="flat",
            highlightbackground=RED,
            highlightthickness=1,
            cursor="hand2",
            command=logout
        ).pack(side="right", padx=5)

        # PROFILE AND STATISTICS MAIN FRAME
        content_frame = tk.Frame(root, bg=BG_COLOR)
        content_frame.pack(
            fill="x",
            padx=35,
            pady=10
        )

        # LEFT SIDE - EMPLOYEE PROFILE
        profile_frame = tk.Frame(
            content_frame,
            bg=CARD_COLOR,
            width=520,
            height=270,
            highlightbackground=NEON_BLUE,
            highlightthickness=1
        )

        profile_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        profile_frame.pack_propagate(False)

        tk.Label(
            profile_frame,
            text="MY PROFILE",
            font=("Arial", 18, "bold"),
            bg=CARD_COLOR,
            fg=NEON_PURPLE
        ).pack(pady=(15, 12))

        # FULL EMPLOYEE DETAILS
        details_frame = tk.Frame(
            profile_frame,
            bg=CARD_COLOR
        )
        details_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=5
        )

        profile_details = [
            ("Employee ID", emp_id),
            ("Full Name", full_name),
            ("Department", department),
            ("Designation", designation or "-"),
            ("Email", email or "-"),
            ("Phone", phone or "-"),
            ("Joining Date", joining_date or "-"),
            ("Account Status", "Active" if is_active else "Inactive")
        ]

        for index, (label_text, value_text) in enumerate(profile_details):

            tk.Label(
                details_frame,
                text=label_text,
                font=("Arial", 10, "bold"),
                bg=CARD_COLOR,
                fg=TEXT_COLOR,
                anchor="w"
            ).grid(
                row=index,
                column=0,
                sticky="w",
                padx=(0, 12),
                pady=4
            )

            tk.Label(
                details_frame,
                text=f":  {value_text}",
                font=("Arial", 10),
                bg=CARD_COLOR,
                fg=WHITE,
                anchor="w",
                justify="left",
                wraplength=280
            ).grid(
                row=index,
                column=1,
                sticky="w",
                pady=4
            )

        details_frame.grid_columnconfigure(1, weight=1)

        # RIGHT SIDE - EMPLOYEE LEAVE STATISTICS
        stats_frame = tk.Frame(
            content_frame,
            bg=BG_COLOR,
            width=420
        )

        stats_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        tk.Label(
            stats_frame,
            text="LEAVE STATISTICS",
            font=("Arial", 17, "bold"),
            bg=BG_COLOR,
            fg=NEON_PURPLE
        ).pack(pady=(5, 12))

        employee_stats = [
            ("Pending Leaves", pending, "#FBBF24"),
            ("Approved Leaves", approved, GREEN),
            ("Rejected Leaves", rejected, RED)
        ]

        for title, value, color in employee_stats:

            card = tk.Frame(
                stats_frame,
                bg=CARD_COLOR,
                height=65,
                highlightbackground=NEON_BLUE,
                highlightthickness=1
            )

            card.pack(
                fill="x",
                padx=12,
                pady=7
            )

            card.pack_propagate(False)

            tk.Label(
                card,
                text=title,
                font=("Arial", 11, "bold"),
                bg=CARD_COLOR,
                fg=TEXT_COLOR
            ).pack(
                side="left",
                padx=18
            )

            tk.Label(
                card,
                text=str(value),
                font=("Arial", 22, "bold"),
                bg=CARD_COLOR,
                fg=color
            ).pack(
                side="right",
                padx=22
            )

        # EMPLOYEE OPTIONS
        tk.Label(
            root,
            text="EMPLOYEE OPTIONS",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=NEON_PURPLE
        ).pack(pady=10)

        button_frame = tk.Frame(root, bg=BG_COLOR)
        button_frame.pack(pady=5)

        def open_employee_leave_application():

            from modules.leave_application import show_leave_application
            show_leave_application(root, employee_id=employee_id)

        def open_my_leave_balance():

            from modules.leave_balance import show_leave_balance
            show_leave_balance(root, employee_id=employee_id)

        
        def open_my_leave_history():

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT leave_type, from_date, to_date,
                       total_days, reason, status
                FROM leave_applications
                WHERE employee_id = ?
                ORDER BY applied_at DESC
            """, (employee_id,))

            records = cursor.fetchall()
            conn.close()

            history_window = tk.Toplevel(root)
            history_window.title("My Leave History")
            history_window.geometry("950x500")
            history_window.configure(bg=BG_COLOR)

            # DARK NEON HISTORY HEADER
            tk.Label(
                history_window,
                text="MY LEAVE HISTORY",
                font=("Arial", 21, "bold"),
                bg=BG_COLOR,
                fg=NEON_BLUE
            ).pack(pady=(20, 15))

            # TABLE CONTAINER
            table_frame = tk.Frame(
                history_window,
                bg=CARD_COLOR,
                highlightbackground=NEON_BLUE,
                highlightthickness=1
            )
            table_frame.pack(
                fill="both",
                expand=True,
                padx=25,
                pady=15
            )

            from tkinter import ttk

            # CUSTOM DARK NEON TREEVIEW THEME
            history_style = ttk.Style(history_window)
            history_style.theme_use("clam")

            history_style.configure(
                "History.Treeview",
                background=CARD_COLOR,
                foreground=WHITE,
                fieldbackground=CARD_COLOR,
                font=("Arial", 10),
                rowheight=35,
                borderwidth=0
            )

            history_style.configure(
                "History.Treeview.Heading",
                background=HEADER_COLOR,
                foreground=NEON_BLUE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padding=10
            )

            history_style.map(
                "History.Treeview",
                background=[
                    ("selected", NEON_PURPLE)
                ],
                foreground=[
                    ("selected", WHITE)
                ]
            )

            history_style.map(
                "History.Treeview.Heading",
                background=[
                    ("active", "#17264A")
                ],
                foreground=[
                    ("active", WHITE)
                ]
            )

            # TABLE COLUMNS
            columns = (
                "Leave Type",
                "From Date",
                "To Date",
                "Days",
                "Reason",
                "Status"
            )

            tree = ttk.Treeview(
                table_frame,
                columns=columns,
                show="headings",
                style="History.Treeview"
            )

            for column in columns:

                tree.heading(
                    column,
                    text=column,
                    anchor="center"
                )

                tree.column(
                    column,
                    width=140,
                    minwidth=100,
                    anchor="center"
                )

            tree.column("Reason", width=220)

            # SCROLLBAR
            scrollbar = ttk.Scrollbar(
                table_frame,
                orient="vertical",
                command=tree.yview
            )

            tree.configure(
                yscrollcommand=scrollbar.set
            )

            tree.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(10, 0),
                pady=10
            )

            scrollbar.pack(
                side="right",
                fill="y",
                padx=(0, 10),
                pady=10
            )

            # STATUS COLORS
            tree.tag_configure(
                "Approved",
                foreground=GREEN
            )

            tree.tag_configure(
                "Pending",
                foreground="#FBBF24"
            )

            tree.tag_configure(
                "Rejected",
                foreground=RED
            )

            # INSERT LEAVE RECORDS
            for record in records:

                status = record[5]

                tree.insert(
                    "",
                    "end",
                    values=record,
                    tags=(status,)
                )

            # EMPTY DATA MESSAGE
            if not records:

                tk.Label(
                    history_window,
                    text="No leave applications found.",
                    font=("Arial", 12, "bold"),
                    bg=BG_COLOR,
                    fg=TEXT_COLOR
                ).pack(pady=5)

            # CLOSE BUTTON
            tk.Button(
                history_window,
                text="Close",
                width=14,
                height=2,
                font=("Arial", 10, "bold"),
                bg="#17264A",
                fg=NEON_BLUE,
                activebackground=NEON_PURPLE,
                activeforeground=WHITE,
                relief="flat",
                highlightbackground=NEON_BLUE,
                highlightthickness=1,
                cursor="hand2",
                command=history_window.destroy
            ).pack(pady=(0, 18))


        # EMPLOYEE BUTTON FUNCTION
        def employee_button(text, action, column):

            tk.Button(
                button_frame,
                text=text,
                width=25,
                height=3,
                font=("Arial", 11, "bold"),
                bg="#17264A",
                fg=NEON_BLUE,
                activebackground=NEON_PURPLE,
                activeforeground=WHITE,
                relief="flat",
                highlightbackground=NEON_BLUE,
                highlightthickness=1,
                cursor="hand2",
                command=action
            ).grid(
                row=0,
                column=column,
                padx=12,
                pady=9
            )

        # THREE BUTTONS IN ONE ROW
        employee_button(
            "Apply for Leave",
            open_employee_leave_application,
            0
        )

        employee_button(
            "My Leave Balance",
            open_my_leave_balance,
            1
        )

        employee_button(
            "My Leave History",
            open_my_leave_history,
            2
        )

    else:

        messagebox.showerror(
            "Access Denied",
            "Invalid user role.",
            parent=root
        )
        root.destroy()
        return

    # BOTTOM BUTTONS
    bottom_frame = tk.Frame(root, bg=BG_COLOR)
    bottom_frame.pack(
        fill="x",
        pady=15
    )

    # REFRESH
    def refresh_dashboard():

        root.destroy()
        show_dashboard(username, role, employee_id)

    refresh_button = tk.Button(
        bottom_frame,
        text="↻  Refresh Dashboard",
        width=20,
        height=2,
        font=("Arial", 10, "bold"),
        bg="#12364A",
        fg=NEON_BLUE,
        activebackground=NEON_BLUE,
        activeforeground=BG_COLOR,
        relief="flat",
        highlightbackground=NEON_BLUE,
        highlightthickness=1,
        cursor="hand2",
        command=refresh_dashboard
    )

    if role.lower() == "employee":

        refresh_button.pack(anchor="center")

    else:

        refresh_button.pack(side="left", padx=10)

    # ADMIN LOGOUT
    if role.lower() == "admin":

        tk.Button(
            bottom_frame,
            text="Logout",
            width=15,
            height=2,
            font=("Arial", 10, "bold"),
            bg="#401B35",
            fg=RED,
            activebackground=RED,
            activeforeground=WHITE,
            relief="flat",
            highlightbackground=RED,
            highlightthickness=1,
            cursor="hand2",
            command=logout
        ).pack(side="left", padx=10)

    root.mainloop()


if __name__ == "__main__":
    show_dashboard()
