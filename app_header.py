
import tkinter as tk
import os
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LOGO_PATH = os.path.join(
    BASE_DIR, "assets", "logo.png"
)

# DARK NEON THEME COLORS
BG_COLOR = "#050B1E"
HEADER_COLOR = "#080F2B"
NEON_BLUE = "#00D9FF"
NEON_PURPLE = "#8B5CF6"
WHITE = "#FFFFFF"
SUBTITLE_COLOR = "#A5CFFF"
BOX_COLOR = "#111D3D"


def add_app_header(parent, username=None):

    header = tk.Frame(
        parent,
        bg=HEADER_COLOR,
        highlightbackground=NEON_BLUE,
        highlightthickness=1
    )
    header.pack(fill="x")

    # MAIN HEADER
    top_frame = tk.Frame(
        header,
        bg=HEADER_COLOR,
        height=82
    )
    top_frame.pack(fill="x")
    top_frame.pack_propagate(False)

    # ORIGINAL DIT LOGO
    try:
        image = Image.open(LOGO_PATH).convert("RGBA")
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
            padx=(18, 12),
            pady=5
        )

    except Exception as e:
        print("Logo loading error:", e)

        tk.Label(
            top_frame,
            text="DIT",
            font=("Arial", 18, "bold"),
            bg=HEADER_COLOR,
            fg=NEON_BLUE
        ).pack(side="left", padx=20)

    # APP NAME
    title_frame = tk.Frame(
        top_frame,
        bg=HEADER_COLOR
    )
    title_frame.pack(
        side="left",
        pady=15
    )

    tk.Label(
        title_frame,
        text="EMPLOYEE LEAVE MANAGEMENT SYSTEM",
        font=("Arial", 16, "bold"),
        bg=HEADER_COLOR,
        fg=WHITE
    ).pack(anchor="w")

    tk.Label(
        title_frame,
        text="Employee Management | Leave Administration",
        font=("Arial", 9),
        bg=HEADER_COLOR,
        fg=SUBTITLE_COLOR
    ).pack(anchor="w")

    # WELCOME NAME
    if username:
        tk.Label(
            top_frame,
            text=f"WELCOME, {username}",
            font=("Arial", 15, "bold"),
            bg=HEADER_COLOR,
            fg=NEON_BLUE
        ).pack(side="right", padx=25)

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

        border_color = NEON_BLUE if index % 2 == 0 else NEON_PURPLE

        box = tk.Label(
            info_frame,
            text=item,
            font=("Arial", 8, "bold"),
            bg=BOX_COLOR,
            fg=WHITE,
            padx=8,
            pady=5,
            bd=1,
            relief="solid",
            highlightbackground=border_color,
            highlightcolor=border_color,
            highlightthickness=1
        )

        box.pack(
            side="left",
            padx=(0, 6),
            pady=2
        )

    return header
