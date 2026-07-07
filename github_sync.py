import tkinter as tk
from tkinter import messagebox
import subprocess
import datetime
import os

# Change this to your SentinelAI project folder
PROJECT_PATH = r"D:\projects\sentinelai"


def run_git():
    try:
        import os
        import subprocess
        import datetime
        from tkinter import messagebox

        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        commit_msg = "Auto Update - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subprocess.run(["git", "add", "."], check=True)

        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=False
        )

        subprocess.run(
            ["git", "push", "origin", "main"],
            check=True
        )

        messagebox.showinfo("Success", "Project pushed successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

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