import tkinter as tk
from tkinter import messagebox
import subprocess
import datetime
import os
import sys

# Full path to Git (change this only if Git is installed somewhere else)
GIT = r"C:\Program Files\Git\cmd\git.exe"

def run_git():
    try:
        # Detect project folder
        if getattr(sys, "frozen", False):
            project_path = os.path.dirname(sys.executable)
        else:
            project_path = os.path.dirname(os.path.abspath(__file__))

        os.chdir(project_path)

        # Verify we're inside a Git repository
        if not os.path.exists(".git"):
            raise Exception(
                f"No .git folder found.\n\n"
                f"Current folder:\n{project_path}\n\n"
                f"Place github_sync.exe inside your SentinelAI project folder."
            )

        commit_msg = "Auto Update - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add
        result = subprocess.run(
            [GIT, "add", "."],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(result.stderr)

        # Commit (ignore "nothing to commit")
        subprocess.run(
            [GIT, "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )

        # Push
        result = subprocess.run(
            [GIT, "push", "origin", "main"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(result.stderr)

        messagebox.showinfo("Success", "✅ Successfully pushed to GitHub!")

    except Exception as e:
        messagebox.showerror("Git Error", str(e))


root = tk.Tk()
root.title("SentinelAI GitHub Sync")
root.geometry("350x170")
root.resizable(False, False)

tk.Label(
    root,
    text="SentinelAI GitHub Sync",
    font=("Arial", 14, "bold")
).pack(pady=15)

tk.Button(
    root,
    text="⬆ Push to GitHub",
    width=22,
    height=2,
    command=run_git
).pack()

root.mainloop()