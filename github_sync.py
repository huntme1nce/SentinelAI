import tkinter as tk
from tkinter import messagebox
import subprocess
import datetime
import os
import sys

def run_git():
    try:
        # Detect the project folder
        if getattr(sys, "frozen", False):
            project_path = os.path.dirname(sys.executable)
        else:
            project_path = os.path.dirname(os.path.abspath(__file__))

        os.chdir(project_path)

        commit_msg = "Auto Update - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add files
        result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(result.stderr)

        # Commit (ignore if nothing changed)
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )

        # Push
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(result.stderr)

        messagebox.showinfo("Success", "Project pushed successfully!")

    except Exception as e:
        messagebox.showerror("Git Error", str(e))


root = tk.Tk()
root.title("GitHub Sync")
root.geometry("320x150")
root.resizable(False, False)

label = tk.Label(
    root,
    text="SentinelAI GitHub Sync",
    font=("Arial", 14, "bold")
)
label.pack(pady=15)

push_btn = tk.Button(
    root,
    text="Push to GitHub",
    font=("Arial", 12),
    width=20,
    height=2,
    command=run_git
)
push_btn.pack()

root.mainloop()