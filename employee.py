
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime
import sqlite3
import hashlib
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from database.database import connect_db


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


# PASSWORD HASHING
def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        100000
    )

    return salt + "$" + hashed.hex()


def show_employee_window(parent):

    window = tk.Toplevel(parent)
    window.title("Employee Management")
    window.geometry("1100x700")
    window.configure(bg=BG_COLOR)
    window.minsize(900, 550)

    selected_employee = tk.StringVar()

    # TREEVIEW STYLE
    style = ttk.Style(window)
    style.theme_use("clam")

    style.configure(
        "Neon.Treeview",
        background=CARD_COLOR,
        foreground=TEXT_COLOR,
        fieldbackground=CARD_COLOR,
        rowheight=32,
        font=("Arial", 10),
        borderwidth=0
    )

    style.configure(
        "Neon.Treeview.Heading",
        background=HEADER_COLOR,
        foreground=NEON_BLUE,
        font=("Arial", 10, "bold"),
        relief="flat",
        padding=8
    )

    style.map(
        "Neon.Treeview",
        background=[("selected", "#263D70")],
        foreground=[("selected", WHITE)]
    )

    style.configure(
        "Neon.Vertical.TScrollbar",
        background=HEADER_COLOR,
        troughcolor=BG_COLOR,
        arrowcolor=NEON_BLUE,
        bordercolor=BG_COLOR
    )

    # HEADING
    tk.Label(
        window,
        text="EMPLOYEE MANAGEMENT",
        font=("Arial", 22, "bold"),
        bg=HEADER_COLOR,
        fg=NEON_BLUE,
        pady=15,
        highlightbackground=NEON_BLUE,
        highlightthickness=1
    ).pack(fill="x")

    # FORM
    form = tk.Frame(
        window,
        bg=CARD_COLOR,
        padx=20,
        pady=15,
        highlightbackground=NEON_PURPLE,
        highlightthickness=1
    )
    form.pack(fill="x", padx=20, pady=15)

    fields = [
        "Employee ID",
        "Full Name",
        "Department",
        "Designation",
        "Email",
        "Phone",
        "Joining Date"
    ]

    entries = {}

    for i, field in enumerate(fields):

        row = i // 4
        col = (i % 4) * 2

        tk.Label(
            form,
            text=field,
            bg=CARD_COLOR,
            fg=WHITE,
            font=("Arial", 10, "bold")
        ).grid(row=row, column=col, padx=5, pady=10)

        entry = tk.Entry(
            form,
            width=22,
            font=("Arial", 10),
            bg=INPUT_COLOR,
            fg=WHITE,
            insertbackground=NEON_BLUE,
            relief="flat",
            highlightbackground=NEON_PURPLE,
            highlightcolor=NEON_BLUE,
            highlightthickness=1
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=5,
            pady=10,
            ipady=5
        )

        entries[field] = entry

    # EMPLOYEE TABLE
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
        "ID", "Name", "Department",
        "Designation", "Email", "Phone", "Joining Date"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=7,
        style="Neon.Treeview"
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview,
        style="Neon.Vertical.TScrollbar"
    )

    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # LOAD EMPLOYEES
    def load_employees(search=""):

        try:
            for item in tree.get_children():
                tree.delete(item)

            conn = connect_db()
            cursor = conn.cursor()

            keyword = f"%{search}%"

            cursor.execute("""
                SELECT employee_id, full_name, department,
                       designation, email, phone, joining_date
                FROM employees
                WHERE is_active = 1
                AND (
                    employee_id LIKE ?
                    OR full_name LIKE ?
                    OR department LIKE ?
                )
                ORDER BY employee_id
            """, (keyword, keyword, keyword))

            records = cursor.fetchall()

            for record in records:
                tree.insert("", "end", values=record)

            conn.close()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e),
                parent=window
            )

    # CLEAR FORM
    def clear_form():

        for entry in entries.values():
            entry.config(state="normal")
            entry.delete(0, tk.END)

        selected_employee.set("")

        for item in tree.selection():
            tree.selection_remove(item)

        entries["Employee ID"].focus_set()

    # VALIDATE FORM
    def get_form_values():

        values = [
            entries[field].get().strip()
            for field in fields
        ]

        if not all(values):
            messagebox.showwarning(
                "Missing Details",
                "Please fill all employee details.",
                parent=window
            )
            return None

        values[0] = values[0].upper()

        try:
            datetime.strptime(values[6], "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Joining Date must be in YYYY-MM-DD format.",
                parent=window
            )
            return None

        if "@" not in values[4] or "." not in values[4]:
            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address.",
                parent=window
            )
            return None

        if not values[0].startswith("EMP") or len(values[0]) <= 3:
            messagebox.showwarning(
                "Invalid Employee ID",
                "Employee ID must be like EMP001.",
                parent=window
            )
            return None

        return values

    # ADD EMPLOYEE + CREATE LOGIN ACCOUNT
    def add_employee():

        if selected_employee.get():
            messagebox.showwarning(
                "Warning",
                "Click Clear before adding a new employee.",
                parent=window
            )
            return

        values = get_form_values()

        if values is None:
            return

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            employee_id = values[0]
            username = employee_id
            initial_password = "EMP@" + employee_id[3:]

            password_hash = hash_password(initial_password)

            # CHECK EXISTING USER ACCOUNT
            cursor.execute("""
                SELECT user_id
                FROM users
                WHERE username = ?
            """, (username,))

            if cursor.fetchone():
                messagebox.showerror(
                    "Account Exists",
                    "A login account already exists for this Employee ID.",
                    parent=window
                )
                return

            # INSERT EMPLOYEE
            cursor.execute("""
                INSERT INTO employees (
                    employee_id,
                    full_name,
                    department,
                    designation,
                    email,
                    phone,
                    joining_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, values)

            # CREATE EMPLOYEE LOGIN
            cursor.execute("""
                INSERT INTO users (
                    username,
                    password_hash,
                    role,
                    employee_id
                )
                VALUES (?, ?, ?, ?)
            """, (
                username,
                password_hash,
                "Employee",
                employee_id
            ))

            conn.commit()

            messagebox.showinfo(
                "Employee Created Successfully",
                f"Employee added successfully!\n\n"
                f"Employee ID: {employee_id}\n"
                f"Username: {username}\n"
                f"Initial Password: {initial_password}\n\n"
                f"Share these login details securely.",
                parent=window
            )

            load_employees()
            clear_form()

        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Duplicate Details",
                "Employee ID or Email already exists.\n"
                "Please check the details.",
                parent=window
            )

        except sqlite3.Error as e:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error",
                str(e),
                parent=window
            )

        finally:
            if conn:
                conn.close()

    # SELECT EMPLOYEE
    def select_employee(event=None):

        selected = tree.selection()

        if not selected:
            return

        values = tree.item(selected[0], "values")

        if not values:
            return

        selected_employee.set(values[0])

        for field, value in zip(fields, values):

            entries[field].config(state="normal")
            entries[field].delete(0, tk.END)
            entries[field].insert(0, value)

        entries["Employee ID"].config(state="readonly")

    tree.bind("<<TreeviewSelect>>", select_employee)

    # UPDATE EMPLOYEE
    def update_employee():

        emp_id = selected_employee.get()

        if not emp_id:
            messagebox.showwarning(
                "Select Employee",
                "Please select an employee from the table first.",
                parent=window
            )
            return

        values = get_form_values()

        if values is None:
            return

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE employees
                SET full_name = ?,
                    department = ?,
                    designation = ?,
                    email = ?,
                    phone = ?,
                    joining_date = ?
                WHERE employee_id = ?
                AND is_active = 1
            """, (
                values[1],
                values[2],
                values[3],
                values[4],
                values[5],
                values[6],
                emp_id
            ))

            if cursor.rowcount == 0:
                conn.rollback()

                messagebox.showwarning(
                    "Not Updated",
                    "Employee record was not found or is inactive.",
                    parent=window
                )
                return

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Employee details updated successfully!",
                parent=window
            )

            load_employees()
            clear_form()

        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Duplicate Email",
                "This email address is already used by another employee.",
                parent=window
            )

        except sqlite3.Error as e:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error",
                str(e),
                parent=window
            )

        finally:
            if conn:
                conn.close()

    # DELETE EMPLOYEE
    def delete_employee():

        emp_id = selected_employee.get()

        if not emp_id:
            messagebox.showwarning(
                "Warning",
                "Please select an employee.",
                parent=window
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to deactivate this employee?",
            parent=window
        )

        if not confirm:
            return

        conn = None

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE employees
                SET is_active = 0
                WHERE employee_id = ?
            """, (emp_id,))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Employee deactivated successfully!",
                parent=window
            )

            load_employees()
            clear_form()

        except sqlite3.Error as e:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Database Error",
                str(e),
                parent=window
            )

        finally:
            if conn:
                conn.close()

    # SEARCH AND CLEAR BUTTONS - TOP
    search_frame = tk.Frame(
        window,
        bg=BG_COLOR
    )
    search_frame.pack(pady=3)

    search_entry = tk.Entry(
        search_frame,
        width=35,
        font=("Arial", 10),
        bg=INPUT_COLOR,
        fg=WHITE,
        insertbackground=NEON_BLUE,
        relief="flat",
        highlightbackground=NEON_PURPLE,
        highlightcolor=NEON_BLUE,
        highlightthickness=1
    )

    search_entry.pack(
        side="left",
        padx=5,
        ipady=6
    )

    def search_employee():
        load_employees(search_entry.get().strip())

    tk.Button(
        search_frame,
        text="Search",
        command=search_employee,
        bg=NEON_BLUE,
        fg="#050B1E",
        activebackground=NEON_PURPLE,
        activeforeground=WHITE,
        width=12,
        font=("Arial", 9, "bold"),
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=5, ipady=4)

    tk.Button(
        search_frame,
        text="Clear",
        command=lambda: (
            search_entry.delete(0, tk.END),
            clear_form()
        ),
        bg="#263D70",
        fg=WHITE,
        activebackground=NEON_PURPLE,
        activeforeground=WHITE,
        width=12,
        font=("Arial", 9, "bold"),
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=5, ipady=4)

    # ACTION BUTTONS - BOTTOM
    button_frame = tk.Frame(
        window,
        bg=BG_COLOR
    )
    button_frame.pack(pady=5)

    tk.Button(
        button_frame,
        text="Add Employee",
        width=16,
        bg="#00B982",
        fg="#050B1E",
        activebackground="#00D68F",
        font=("Arial", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=add_employee
    ).pack(side="left", padx=5, ipady=7)

    tk.Button(
        button_frame,
        text="Update Employee",
        width=16,
        bg=NEON_BLUE,
        fg="#050B1E",
        activebackground="#62E8FF",
        font=("Arial", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=update_employee
    ).pack(side="left", padx=5, ipady=7)

    tk.Button(
        button_frame,
        text="Delete Employee",
        width=16,
        bg="#FF4D6D",
        fg=WHITE,
        activebackground="#D9365A",
        font=("Arial", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=delete_employee
    ).pack(side="left", padx=5, ipady=7)

    tk.Button(
        button_frame,
        text="Refresh",
        width=12,
        bg="#263D70",
        fg=WHITE,
        activebackground=NEON_PURPLE,
        font=("Arial", 9, "bold"),
        relief="flat",
        cursor="hand2",
        command=lambda: (
            search_entry.delete(0, tk.END),
            load_employees()
        )
    ).pack(side="left", padx=5, ipady=7)

    # INITIAL LOAD
    load_employees()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    show_employee_window(root)
    root.mainloop()
