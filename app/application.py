"""
============================================================
MODULE ID   : APP-001
MODULE NAME : Application Bootstrap
VERSION     : 1.0.0
============================================================
"""

import tkinter as tk

from core.constants import (
    APP_NAME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WELCOME_TITLE,
    WELCOME_VERSE,
)

from core.version_manager import APP_VERSION


class SentinelApplication:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title(f"{APP_NAME} {APP_VERSION.full}")

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.root.minsize(1200, 700)

    def start(self):

        self.show_welcome()

        self.root.mainloop()

    def show_welcome(self):

        popup = tk.Toplevel(self.root)

        popup.title(WELCOME_TITLE)

        popup.geometry("700x400")

        popup.grab_set()

        label = tk.Label(
            popup,
            text=WELCOME_VERSE,
            font=("Segoe UI", 13),
            justify="center",
            wraplength=600,
        )

        label.pack(expand=True, padx=20, pady=20)

        button = tk.Button(
            popup,
            text="Enter Sentinel AI",
            command=popup.destroy,
            width=20,
            height=2,
        )

        button.pack(pady=20)