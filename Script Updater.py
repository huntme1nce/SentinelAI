import tkinter as tk
from tkinter import filedialog
import zipfile
import json
import os

import os
import json

# Change: Save config in the user's home directory instead of the script folder
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "quick_transfer_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {"source": "", "dest": ""}

def save_config(source, dest):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"source": source, "dest": dest}, f)
    except Exception as e:
        print(f"Warning: Could not save config: {e}")

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip")])
    if filename:
        entry_source.delete(0, tk.END)
        entry_source.insert(0, filename)

def browse_folder():
    foldername = filedialog.askdirectory()
    if foldername:
        entry_dest.delete(0, tk.END)
        entry_dest.insert(0, foldername)

def transfer():
    source_path = entry_source.get()
    dest_path = entry_dest.get()
    
    if not os.path.exists(source_path):
        label_status.config(text="Error: ZIP file not found", fg="red")
        return
    
    try:
        label_status.config(text="Transferring...", fg="blue")
        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            namelist = zip_ref.namelist()
            # Find the first folder name (e.g., "Version1.0/")
            # The first item in the list is usually the root folder
            root_folder = namelist[0]
            
            for member in namelist:
                # We skip the root folder itself and only process contents inside it
                if member.startswith(root_folder) and member != root_folder:
                    # Remove the dynamic folder name part from the path
                    target_path = member[len(root_folder):]
                    
                    full_dest_path = os.path.join(dest_path, target_path)
                    
                    if member.endswith('/'): # It's a folder
                        os.makedirs(full_dest_path, exist_ok=True)
                    else: # It's a file
                        os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)
                        with open(full_dest_path, 'wb') as f:
                            f.write(zip_ref.read(member))
        
        label_status.config(text="Successful", fg="green")
        save_config(source_path, dest_path)
    except Exception as e:
        label_status.config(text=f"Error: {str(e)}", fg="red")

# UI Setup
root = tk.Tk()
root.title("Quick File Transfer")
root.geometry("500x250")
config = load_config()

# Source
tk.Label(root, text="Source ZIP File:").pack(pady=(10, 0))
frame_source = tk.Frame(root)
frame_source.pack(fill='x', padx=20)
entry_source = tk.Entry(frame_source)
entry_source.insert(0, config.get("source", ""))
entry_source.pack(side='left', expand=True, fill='x')
tk.Button(frame_source, text="Browse", command=browse_file).pack(side='right', padx=5)

# Destination
tk.Label(root, text="Destination Folder:").pack(pady=(10, 0))
frame_dest = tk.Frame(root)
frame_dest.pack(fill='x', padx=20)
entry_dest = tk.Entry(frame_dest)
entry_dest.insert(0, config.get("dest", ""))
entry_dest.pack(side='left', expand=True, fill='x')
tk.Button(frame_dest, text="Browse", command=browse_folder).pack(side='right', padx=5)

# Transfer
tk.Button(root, text="Transfer Files", command=transfer, height=2, bg="#d1e7dd").pack(pady=20)
label_status = tk.Label(root, text="Ready", font=('Arial', 10, 'bold'))
label_status.pack()

root.mainloop()