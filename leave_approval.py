
import tkinter as tk
from tkinter import ttk, messagebox
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


def show_leave_approval(parent):

    window = tk.Toplevel(parent)
    window.title("Leave Approval")
    window.geometry("1150x700")
    window.configure(bg=BG_COLOR)

    # DIT COMMON HEADER
    add_app_header(window)

    # TREEVIEW STYLE
    style = ttk.Style(window)
    style.theme_use("clam")

    style.configure(
        "Approval.Treeview",
        background=CARD_COLOR,
        foreground=TEXT_COLOR,
        fieldbackground=CARD_COLOR,
        rowheight=35,
        font=("Arial", 10),
        borderwidth=0
    )

    style.configure(
        "Approval.Treeview.Heading",
        background=HEADER_COLOR,
        foreground=NEON_BLUE,
        font=("Arial", 10, "bold"),
        relief="flat",
        padding=9
    )

    style.map(
        "Approval.Treeview",
        background=[("selected", "#263D70")],
        foreground=[("selected", WHITE)]
    )

    style.configure(
        "Approval.Vertical.TScrollbar",
        background=HEADER_COLOR,
        troughcolor=BG_COLOR,
        arrowcolor=NEON_BLUE,
        bordercolor=BG_COLOR
    )

    # PAGE HEADING
    tk.Label(
        window,
        text="LEAVE APPROVAL MANAGEMENT",
        font=("Arial", 19, "bold"),
        bg=BG_COLOR,
        fg=NEON_BLUE
    ).pack(pady=15)

    # TABLE FRAME
    table_frame = tk.Frame(
        window,
        bg=CARD_COLOR,
        highlightbackground=NEON_PURPLE,
        highlightthickness=1
    )
    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    columns = (
        "Leave ID", "Employee ID", "Name",
        "Leave Type", "From Date", "To Date",
        "Days", "Reason", "Status"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Approval.Treeview"
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=115, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview,
        style="Approval.Vertical.TScrollbar"
    )

    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(
        side="left",
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    scrollbar.pack(side="right", fill="y", pady=10)

    # LOAD LEAVE REQUESTS
    def load_requests():

        for item in tree.get_children():
            tree.delete(item)

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT l.leave_id, l.employee_id,
                       e.full_name, l.leave_type,
                       l.from_date, l.to_date,
                       l.total_days, l.reason, l.status
                FROM leave_applications l
                JOIN employees e
                ON l.employee_id = e.employee_id
                ORDER BY l.leave_id DESC
            """)

            records = cursor.fetchall()

            for record in records:
                tree.insert("", "end", values=record)

        finally:
            conn.close()

    # APPROVE LEAVE
    def approve_leave():

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a leave request",
                parent=window
            )
            return

        values = tree.item(selected[0], "values")
        leave_id = values[0]

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN IMMEDIATE")

            cursor.execute("""
                SELECT employee_id, leave_type,
                       total_days, status
                FROM leave_applications
                WHERE leave_id = ?
            """, (leave_id,))

            request = cursor.fetchone()

            if not request or request[3] != "Pending":
                raise Exception(
                    "This request is not Pending."
                )

            emp_id, leave_type, days, status = request

            cursor.execute("""
                UPDATE leave_balance
                SET used_days = used_days + ?
                WHERE employee_id = ?
                AND leave_type = ?
                AND total_days - used_days >= ?
            """, (days, emp_id, leave_type, days))

            if cursor.rowcount == 0:
                raise Exception(
                    "Insufficient leave balance."
                )

            cursor.execute("""
                UPDATE leave_applications
                SET status = 'Approved',
                    reviewed_by = 'admin',
                    reviewed_at = CURRENT_TIMESTAMP
                WHERE leave_id = ?
                AND status = 'Pending'
            """, (leave_id,))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Leave Approved Successfully!",
                parent=window
            )

        except Exception as error:
            conn.rollback()
            messagebox.showerror(
                "Error",
                str(error),
                parent=window
            )

        finally:
            conn.close()

        load_requests()

    # REJECT LEAVE
    def reject_leave():

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a leave request",
                parent=window
            )
            return

        values = tree.item(selected[0], "values")
        leave_id = values[0]

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

            if cursor.rowcount == 1:
                conn.commit()
                messagebox.showinfo(
                    "Success",
                    "Leave Rejected Successfully!",
                    parent=window
                )
            else:
                conn.rollback()
                messagebox.showwarning(
                    "Warning",
                    "This request is not Pending.",
                    parent=window
                )

        finally:
            conn.close()

        load_requests()

    # BUTTON FRAME
    button_frame = tk.Frame(
        window,
        bg=BG_COLOR
    )
    button_frame.pack(pady=15)

    # APPROVE BUTTON
    tk.Button(
        button_frame,
        text="APPROVE",
        command=approve_leave,
        bg="#00B982",
        fg="#050B1E",
        activebackground="#00D68F",
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        width=15,
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=10, ipady=7)

    # REJECT BUTTON
    tk.Button(
        button_frame,
        text="REJECT",
        command=reject_leave,
        bg="#FF4D6D",
        fg=WHITE,
        activebackground="#D9365A",
        font=("Arial", 10, "bold"),
        width=15,
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=10, ipady=7)

    # REFRESH BUTTON
    tk.Button(
        button_frame,
        text="REFRESH",
        command=load_requests,
        bg="#263D70",
        fg=WHITE,
        activebackground=NEON_PURPLE,
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        width=15,
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=10, ipady=7)

    load_requests()
