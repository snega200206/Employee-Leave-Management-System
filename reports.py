
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database.database import connect_db
from modules.app_header import add_app_header
import pandas as pd


def show_reports(parent):

    window = tk.Toplevel(parent)
    window.title("Leave Reports Management")
    window.geometry("1200x750")
    window.configure(bg="#050B1E")

    # DIT HEADER
    add_app_header(window)

    # PAGE TITLE
    tk.Label(
        window,
        text="LEAVE REPORTS MANAGEMENT",
        font=("Arial", 20, "bold"),
        bg="#050B1E",
        fg="#00D9FF"
    ).pack(pady=12)

    # FILTER FRAME
    filter_frame = tk.Frame(
        window,
        bg="#111D3D",
        bd=1,
        relief="solid",
        highlightbackground="#00D9FF",
        highlightthickness=1
    )
    filter_frame.pack(
        fill="x",
        padx=25,
        pady=8
    )

    tk.Label(
        filter_frame,
        text="Select Report:",
        font=("Arial", 11, "bold"),
        bg="#111D3D",
        fg="#DCEBFF"
    ).pack(side="left", padx=15, pady=12)

    report_type = tk.StringVar(value="All Leaves")

    # DROPDOWN STYLE
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Reports.TCombobox",
        fieldbackground="#172B50",
        background="#172B50",
        foreground="#FFFFFF",
        arrowcolor="#00D9FF",
        bordercolor="#00D9FF",
        padding=7
    )

    style.map(
        "Reports.TCombobox",
        fieldbackground=[("readonly", "#172B50")],
        foreground=[("readonly", "#FFFFFF")]
    )

    report_dropdown = ttk.Combobox(
        filter_frame,
        textvariable=report_type,
        values=[
            "All Leaves",
            "Pending Leaves",
            "Approved Leaves",
            "Rejected Leaves"
        ],
        state="readonly",
        width=22,
        font=("Arial", 10),
        style="Reports.TCombobox"
    )
    report_dropdown.pack(side="left", padx=10, pady=12)

    # TABLE FRAME
    table_frame = tk.Frame(
        window,
        bg="#111D3D",
        bd=1,
        relief="solid",
        highlightbackground="#00D9FF",
        highlightthickness=1
    )

    columns = (
        "Leave ID",
        "Employee ID",
        "Employee Name",
        "Leave Type",
        "From Date",
        "To Date",
        "Days",
        "Status"
    )

    # TREEVIEW STYLE
    style.configure(
        "Reports.Treeview",
        background="#111D3D",
        foreground="#DCEBFF",
        fieldbackground="#111D3D",
        rowheight=35,
        font=("Arial", 10)
    )

    style.configure(
        "Reports.Treeview.Heading",
        background="#172B50",
        foreground="#00D9FF",
        font=("Arial", 10, "bold"),
        relief="flat",
        padding=10
    )

    style.map(
        "Reports.Treeview",
        background=[("selected", "#2457A6")],
        foreground=[("selected", "#FFFFFF")]
    )

    style.map(
        "Reports.Treeview.Heading",
        background=[("active", "#243B68")]
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Reports.Treeview"
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(
            col,
            width=135,
            anchor="center"
        )

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    report_data = []

    # LOAD REPORT
    def load_report():

        for item in tree.get_children():
            tree.delete(item)

        conn = connect_db()
        cursor = conn.cursor()

        selected = report_type.get()

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

        nonlocal report_data
        report_data = cursor.fetchall()
        conn.close()

        for record in report_data:
            tree.insert("", "end", values=record)

    # EXPORT TO EXCEL
    def export_excel():

        if not report_data:
            messagebox.showwarning(
                "Warning",
                "Please generate the report first!"
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile="Leave_Report.xlsx"
        )

        if file_path:

            try:
                df = pd.DataFrame(
                    report_data,
                    columns=columns
                )

                df.to_excel(file_path, index=False)

                messagebox.showinfo(
                    "Success",
                    "Excel Report Exported Successfully!"
                )

            except Exception as error:
                messagebox.showerror(
                    "Export Error",
                    str(error)
                )

    # GENERATE REPORT BUTTON
    tk.Button(
        filter_frame,
        text="Generate Report",
        command=load_report,
        font=("Arial", 10, "bold"),
        bg="#172B50",
        fg="#00D9FF",
        activebackground="#2457A6",
        activeforeground="white",
        relief="flat",
        width=16,
        cursor="hand2",
        bd=0,
        pady=5
    ).pack(side="left", padx=15, pady=12)

    # EXPORT BUTTON - BOTTOM CENTER
    export_frame = tk.Frame(
        window,
        bg="#050B1E"
    )

    export_button = tk.Button(
        export_frame,
        text="EXPORT TO EXCEL",
        command=export_excel,
        font=("Arial", 13, "bold"),
        bg="#087F5B",
        fg="white",
        activebackground="#0A9B70",
        activeforeground="white",
        relief="flat",
        width=25,
        height=2,
        padx=20,
        pady=8,
        cursor="hand2",
        bd=0
    )

    export_button.pack(pady=10)

    # PACK EXPORT FIRST, TABLE AFTER
    export_frame.pack(
        side="bottom",
        fill="x",
        pady=8
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=8
    )

    # INITIAL REPORT
    load_report()
