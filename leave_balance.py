
import tkinter as tk
from tkinter import ttk, messagebox
from database.database import connect_db
from modules.app_header import add_app_header


def show_leave_balance(parent, employee_id=None):

    is_employee = employee_id is not None

    window = tk.Toplevel(parent)
    window.title("Leave Balance Management")
    window.geometry("1100x700")
    window.configure(bg="#050B1E")

    # DIT Common Header
    add_app_header(window)

    # Page Title
    title = (
        "My Leave Balance"
        if is_employee
        else "Employee Leave Balance"
    )

    tk.Label(
        window,
        text=title,
        font=("Arial", 20, "bold"),
        bg="#050B1E",
        fg="#00D9FF"
    ).pack(pady=7)

    # Table Frame
    table_frame = tk.Frame(
        window,
        bg="#111D3D",
        bd=1,
        relief="solid",
        highlightbackground="#00D9FF",
        highlightthickness=1
    )
    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=5
    )

    columns = (
        "Employee ID",
        "Employee Name",
        "Leave Type",
        "Total Days",
        "Used Days",
        "Remaining Days"
    )

    style = ttk.Style(window)
    style.theme_use("clam")

    style.configure(
        "Balance.Treeview",
        background="#111D3D",
        foreground="#DCEBFF",
        fieldbackground="#111D3D",
        rowheight=32,
        font=("Arial", 10)
    )

    style.configure(
        "Balance.Treeview.Heading",
        background="#172B50",
        foreground="#00D9FF",
        font=("Arial", 10, "bold"),
        relief="flat",
        padding=10
    )

    style.map(
        "Balance.Treeview",
        background=[("selected", "#2457A6")],
        foreground=[("selected", "#FFFFFF")]
    )

    style.map(
        "Balance.Treeview.Heading",
        background=[("active", "#243B68")]
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Balance.Treeview"
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=160, anchor="center")

    tree.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=5
    )

    # Load Leave Balance
    def load_balance():

        for item in tree.get_children():
            tree.delete(item)

        conn = connect_db()
        cursor = conn.cursor()

        try:

            if is_employee:

                cursor.execute("""
                    SELECT
                        e.employee_id,
                        e.full_name,
                        b.leave_type,
                        b.total_days,
                        b.used_days,
                        (b.total_days - b.used_days)
                    FROM leave_balance b
                    JOIN employees e
                    ON b.employee_id = e.employee_id
                    WHERE b.employee_id = ?
                    AND e.is_active = 1
                    ORDER BY b.leave_type
                """, (employee_id,))

            else:

                cursor.execute("""
                    SELECT
                        e.employee_id,
                        e.full_name,
                        b.leave_type,
                        b.total_days,
                        b.used_days,
                        (b.total_days - b.used_days)
                    FROM leave_balance b
                    JOIN employees e
                    ON b.employee_id = e.employee_id
                    ORDER BY e.employee_id
                """)

            records = cursor.fetchall()

            for record in records:
                tree.insert("", "end", values=record)

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e),
                parent=window
            )

        finally:
            conn.close()

    # Refresh Button
    tk.Button(
        window,
        text="↻  Refresh",
        command=load_balance,
        font=("Arial", 11, "bold"),
        bg="#172B50",
        fg="#00D9FF",
        activebackground="#2457A6",
        activeforeground="white",
        relief="flat",
        width=16,
        cursor="hand2",
        bd=0,
        pady=8
    ).pack(pady=7)

    load_balance()
