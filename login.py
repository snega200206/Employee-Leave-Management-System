
import tkinter as tk
from tkinter import messagebox
import hashlib
import secrets
import hmac
import os
import sys

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, BASE_DIR)

from PIL import Image, ImageTk
from database.database import connect_db


# DARK NEON 2026 THEME
BG_COLOR = "#050B1E"
HEADER_COLOR = "#080F2B"
CARD_COLOR = "#111D3D"
NEON_BLUE = "#00D9FF"
NEON_PURPLE = "#8B5CF6"
WHITE = "#FFFFFF"
SUBTITLE_COLOR = "#A5CFFF"
INPUT_COLOR = "#09152E"
TEXT_COLOR = "#DCEBFF"


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


def verify_password(password, stored_hash):

    try:
        salt, original_hash = stored_hash.split("$")

        new_hash = hash_password(password, salt)

        return hmac.compare_digest(
            new_hash,
            stored_hash
        )

    except (ValueError, AttributeError):
        return False


# CREATE DEFAULT ADMIN
def create_admin():

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "SELECT user_id FROM users WHERE username = ?",
            ("admin",)
        )

        if cursor.fetchone() is None:

            password_hash = hash_password("Admin@123")

            cursor.execute("""
                INSERT INTO users
                (username, password_hash, role, employee_id)
                VALUES (?, ?, ?, ?)
            """, (
                "admin",
                password_hash,
                "Admin",
                None
            ))

        conn.commit()

    finally:
        conn.close()


# LOGIN VALIDATION
def login_user(username, password, selected_role):

    conn = connect_db()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT username, password_hash, role, employee_id
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        if user is None:
            return None

        stored_username, stored_hash, role, employee_id = user

        if role.lower() != selected_role.lower():
            return None

        if not verify_password(password, stored_hash):
            return None

        if role.lower() == "employee":

            if not employee_id:
                return None

            cursor.execute("""
                SELECT employee_id
                FROM employees
                WHERE employee_id = ?
                AND is_active = 1
            """, (employee_id,))

            if cursor.fetchone() is None:
                return None

        return role, employee_id

    finally:
        conn.close()


# LOGIN GUI
def show_login():

    create_admin()

    root = tk.Tk()
    root.title("Employee Leave Management System")
    root.state("zoomed")
    root.configure(bg=BG_COLOR)
    root.resizable(True, True)

    # MAIN HEADER
    header = tk.Frame(
        root,
        bg=HEADER_COLOR,
        highlightbackground=NEON_BLUE,
        highlightthickness=1
    )
    header.pack(fill="x")

    top_frame = tk.Frame(
        header,
        bg=HEADER_COLOR,
        height=80
    )
    top_frame.pack(fill="x")
    top_frame.pack_propagate(False)

    # ORIGINAL DIT LOGO
    try:

        logo_path = os.path.join(
            BASE_DIR, "assets", "logo.png"
        )

        image = Image.open(logo_path).convert("RGBA")
        image.thumbnail((65, 65), Image.Resampling.LANCZOS)

        logo = ImageTk.PhotoImage(image)

        logo_label = tk.Label(
            top_frame,
            image=logo,
            bg=HEADER_COLOR
        )
        logo_label.image = logo
        logo_label.pack(
            side="left",
            padx=(20, 12),
            pady=5
        )

    except Exception as e:

        print("Logo loading error:", e)

        tk.Label(
            top_frame,
            text="DIT",
            font=("Arial", 20, "bold"),
            bg=HEADER_COLOR,
            fg=NEON_BLUE
        ).pack(side="left", padx=20)

    # APPLICATION NAME
    title_frame = tk.Frame(
        top_frame,
        bg=HEADER_COLOR
    )
    title_frame.pack(side="left", pady=13)

    tk.Label(
        title_frame,
        text="EMPLOYEE LEAVE MANAGEMENT SYSTEM",
        font=("Arial", 17, "bold"),
        bg=HEADER_COLOR,
        fg=WHITE
    ).pack(anchor="w")

    tk.Label(
        title_frame,
        text="Employee Management | Leave Administration",
        font=("Arial", 10),
        bg=HEADER_COLOR,
        fg=SUBTITLE_COLOR
    ).pack(anchor="w")

    # INFORMATION BOXES
    info_frame = tk.Frame(
        header,
        bg=HEADER_COLOR
    )
    info_frame.pack(
        fill="x",
        padx=18,
        pady=(0, 8)
    )

    info_items = [
        "Project ID: DIT-P13",
        "Team ID: T13",
        "DefineInfoTech Pvt. Ltd (DIT)",
        "Kalaignar Karunanithi Government Arts College for Women (A)"
    ]

    for index, item in enumerate(info_items):

        tk.Label(
            info_frame,
            text=item,
            font=("Arial", 8, "bold"),
            bg=CARD_COLOR,
            fg=NEON_BLUE if index % 2 == 0 else "#C4A7FF",
            padx=9,
            pady=5,
            highlightbackground=(
                NEON_BLUE if index % 2 == 0
                else NEON_PURPLE
            ),
            highlightthickness=1
        ).pack(
            side="left",
            padx=(0, 6),
            pady=2
        )

    # MAIN LOGIN AREA
    login_area = tk.Frame(
        root,
        bg=BG_COLOR
    )
    login_area.pack(
        expand=True,
        fill="both",
        padx=35,
        pady=10
    )

    # LEFT INFORMATION PANEL
    left_panel = tk.Frame(
        login_area,
        bg=CARD_COLOR,
        highlightbackground=NEON_PURPLE,
        highlightthickness=2
    )
    left_panel.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 15)
    )

    tk.Label(
        left_panel,
        text="WELCOME TO",
        font=("Arial", 14, "bold"),
        bg=CARD_COLOR,
        fg=SUBTITLE_COLOR
    ).pack(
        anchor="w",
        padx=30,
        pady=(35, 3)
    )

    tk.Label(
        left_panel,
        text="EMPLOYEE LEAVE\nMANAGEMENT SYSTEM",
        font=("Arial", 23, "bold"),
        bg=CARD_COLOR,
        fg=NEON_BLUE,
        justify="left"
    ).pack(
        anchor="w",
        padx=30,
        pady=7
    )

    tk.Label(
        left_panel,
        text=(
            "A smart and secure platform for managing "
            "employee leave activities."
        ),
        font=("Arial", 11),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        wraplength=430,
        justify="left"
    ).pack(
        anchor="w",
        padx=30,
        pady=7
    )

    tk.Label(
        left_panel,
        text="SYSTEM FEATURES",
        font=("Arial", 12, "bold"),
        bg=CARD_COLOR,
        fg=NEON_PURPLE
    ).pack(
        anchor="w",
        padx=30,
        pady=(15, 8)
    )

    features = [
        "• Employee Profile Management",
        "• Online Leave Application",
        "• Leave Balance Tracking",
        "• Leave Approval and Rejection",
        "• Reports and Excel Export",
        "• Secure Role-Based Login"
    ]

    for feature in features:

        tk.Label(
            left_panel,
            text=feature,
            font=("Arial", 10),
            bg=CARD_COLOR,
            fg=WHITE
        ).pack(
            anchor="w",
            padx=35,
            pady=3
        )

    tk.Label(
        left_panel,
        text="SMART  |  SECURE  |  SIMPLE",
        font=("Arial", 10, "bold"),
        bg=CARD_COLOR,
        fg=NEON_BLUE
    ).pack(
        anchor="w",
        padx=30,
        pady=(18, 10)
    )

    # RIGHT LOGIN PANEL
    right_panel = tk.Frame(
        login_area,
        bg=CARD_COLOR,
        padx=30,
        pady=15,
        highlightbackground=NEON_BLUE,
        highlightthickness=2
    )
    right_panel.pack(
        side="right",
        fill="y",
        padx=(15, 0)
    )

    right_panel.configure(width=420)
    right_panel.pack_propagate(False)

    # LOGIN TITLE
    tk.Label(
        right_panel,
        text="ACCOUNT LOGIN",
        font=("Arial", 21, "bold"),
        bg=CARD_COLOR,
        fg=NEON_BLUE
    ).pack(pady=(12, 4))

    tk.Label(
        right_panel,
        text="Select your account type to continue",
        font=("Arial", 9),
        bg=CARD_COLOR,
        fg=SUBTITLE_COLOR
    ).pack(pady=(0, 12))

    # LOGIN TYPE
    selected_role = tk.StringVar(value="Admin")

    role_frame = tk.Frame(
        right_panel,
        bg=CARD_COLOR
    )
    role_frame.pack(fill="x", pady=(0, 12))

    # USERNAME
    tk.Label(
        right_panel,
        text="USERNAME",
        bg=CARD_COLOR,
        fg=WHITE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    username_entry = tk.Entry(
        right_panel,
        width=35,
        font=("Arial", 11),
        bg=INPUT_COLOR,
        fg=WHITE,
        insertbackground=NEON_BLUE,
        relief="flat",
        highlightbackground=NEON_PURPLE,
        highlightcolor=NEON_BLUE,
        highlightthickness=1
    )
    username_entry.pack(
        fill="x",
        pady=(5, 12),
        ipady=7
    )

    # PASSWORD
    tk.Label(
        right_panel,
        text="PASSWORD",
        bg=CARD_COLOR,
        fg=WHITE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    password_entry = tk.Entry(
        right_panel,
        show="*",
        font=("Arial", 11),
        bg=INPUT_COLOR,
        fg=WHITE,
        insertbackground=NEON_BLUE,
        relief="flat",
        highlightbackground=NEON_PURPLE,
        highlightcolor=NEON_BLUE,
        highlightthickness=1
    )
    password_entry.pack(
        fill="x",
        pady=(5, 5),
        ipady=7
    )

    # SHOW PASSWORD OPTION
    show_password_var = tk.BooleanVar(value=False)

    def toggle_password():

        if show_password_var.get():
            password_entry.config(show="")
        else:
            password_entry.config(show="*")

    show_password_check = tk.Checkbutton(
        right_panel,
        text="Show Password",
        variable=show_password_var,
        command=toggle_password,
        bg=CARD_COLOR,
        fg=SUBTITLE_COLOR,
        activebackground=CARD_COLOR,
        activeforeground=NEON_BLUE,
        selectcolor=INPUT_COLOR,
        font=("Arial", 9),
        cursor="hand2"
    )
    show_password_check.pack(
        anchor="w",
        pady=(0, 8)
    )

    # ROLE BUTTON STYLE
    def select_role(role):

        selected_role.set(role)

        if role == "Admin":

            admin_button.config(
                bg=NEON_BLUE,
                fg=BG_COLOR
            )

            employee_button.config(
                bg="#202D4D",
                fg=WHITE
            )

        else:

            employee_button.config(
                bg=NEON_PURPLE,
                fg=WHITE
            )

            admin_button.config(
                bg="#202D4D",
                fg=WHITE
            )

        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        show_password_var.set(False)
        password_entry.config(show="*")

        username_entry.focus_set()

    # ADMIN BUTTON
    admin_button = tk.Button(
        role_frame,
        text="ADMIN LOGIN",
        font=("Arial", 10, "bold"),
        bg=NEON_BLUE,
        fg=BG_COLOR,
        activebackground=NEON_BLUE,
        activeforeground=BG_COLOR,
        relief="flat",
        cursor="hand2",
        command=lambda: select_role("Admin")
    )
    admin_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(0, 5),
        ipady=9
    )

    # EMPLOYEE BUTTON
    employee_button = tk.Button(
        role_frame,
        text="EMPLOYEE LOGIN",
        font=("Arial", 10, "bold"),
        bg="#202D4D",
        fg=WHITE,
        activebackground=NEON_PURPLE,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=lambda: select_role("Employee")
    )
    employee_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(5, 0),
        ipady=9
    )

    # LOGIN FUNCTION
    def check_login():

        username = username_entry.get().strip()
        password = password_entry.get()
        role_choice = selected_role.get()

        if not username or not password:

            messagebox.showwarning(
                "Warning",
                "Please enter username and password",
                parent=root
            )
            return

        result = login_user(
            username,
            password,
            role_choice
        )

        if result:

            role, employee_id = result

            messagebox.showinfo(
                "Success",
                "Login Successful!",
                parent=root
            )

            root.destroy()

            from modules.dashboard import show_dashboard

            show_dashboard(
                username,
                role,
                employee_id
            )

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username, password or account type.",
                parent=root
            )

    # LOGIN BUTTON
    login_button = tk.Button(
        right_panel,
        text="LOGIN",
        bg=NEON_BLUE,
        fg=BG_COLOR,
        activebackground=NEON_PURPLE,
        activeforeground=WHITE,
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
        command=check_login
    )
    login_button.pack(
        fill="x",
        pady=(8, 7),
        ipady=9
    )

    # CLEAR BUTTON
    def clear_fields():

        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        show_password_var.set(False)
        password_entry.config(show="*")

        username_entry.focus_set()

    clear_button = tk.Button(
        right_panel,
        text="CLEAR",
        bg="#202D4D",
        fg=WHITE,
        activebackground=NEON_PURPLE,
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        command=clear_fields
    )
    clear_button.pack(
        fill="x",
        ipady=8
    )

    # LOGIN INFORMATION

    tk.Label(
        right_panel,
        text="Contact Admin if you need account assistance.",
        font=("Arial", 8),
        bg=CARD_COLOR,
        fg="#7185AA",
        wraplength=330
    ).pack(pady=3)

    # FOOTER
    tk.Label(
        root,
        text="EMPLOYEE LEAVE MANAGEMENT SYSTEM",
        font=("Arial", 8, "bold"),
        bg=BG_COLOR,
        fg="#7185AA"
    ).pack(pady=(0, 7))

    # DEFAULT FOCUS
    username_entry.focus_set()

    root.mainloop()


if __name__ == "__main__":
    show_login()
