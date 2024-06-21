import os
import time
import psutil
import ctypes
import threading
import tkinter as tk
from pyinjector import inject
from tkinter import filedialog, messagebox


class ProcessInjectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DLL Injector")
        self.root.configure(bg='black')
        self.dll_path = None  # Variable to store DLL path
        self.dll_path_label = tk.Label(root, text="DLL Path:", fg='white', bg='black')
        self.dll_path_label.pack()
        self.dll_path_frame = tk.Frame(root, bg='black')
        self.dll_path_frame.pack()
        self.dll_path_entry = tk.Entry(self.dll_path_frame, width=30, bg='black', fg='white')
        self.dll_path_entry.pack(side=tk.LEFT)
        tk.Button(self.dll_path_frame, text="Browse", command=self.select_dll_file, bg='black', fg='white').pack(side=tk.LEFT)

        tk.Label(root, text="Search Process:", fg='white', bg='black').pack()
        self.search_entry = tk.Entry(root, width=35, bg='black', fg='white')
        self.search_entry.pack()
        self.process_listbox = tk.Listbox(root, selectmode=tk.SINGLE, bg='black', fg='white', selectbackground='blue', width=50)
        self.process_listbox.pack()
        self.search_entry.bind('<KeyRelease>', self.delayed_search_processes)
        self.mutex = threading.Lock()
        self.search_delay = 0.5
        self.last_search_time = 0
        self.refresh_process_list()

        tk.Button(root, text="Inject DLL", command=self.inject_button_click, bg='black', fg='white').pack(pady=20)

    def select_dll_file(self):
        dll_file = filedialog.askopenfilename(filetypes=[("DLL files", "*.dll")])
        if dll_file:
            self.dll_path = dll_file  # Store the DLL path for when you reopen
            dll_name = os.path.basename(dll_file)
            self.dll_path_entry.delete(0, tk.END)
            self.dll_path_entry.insert(tk.END, dll_name)

    def inject_button_click(self):
        if self.dll_path:
            self.inject_dll(self.dll_path)
        else:
            messagebox.showerror("Error", "Please select DLL file.")

    def inject_dll(self, dll_path):
        process_index = self.process_listbox.curselection()
        if process_index:
            process_info = self.process_listbox.get(process_index[0])
            process_name = process_info.split(" - ")[1]

            try:
                pid = self.find_process_id(process_name)
                if pid:
                    inject(pid, dll_path)
                    messagebox.showinfo("Success", f"DLL injected successfully into {process_name}.")
                else:
                    messagebox.showerror("Error", f"Could not find process: {process_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to inject DLL: {e}")
        else:
            messagebox.showerror("Error", "Please select a process to inject into")

    def find_process_id(self, process_name):
        for process in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in process.info['name'].lower():
                return process.info['pid']
        return None

    def delayed_search_processes(self, event):
        current_time = time.time()
        if current_time - self.last_search_time > self.search_delay:
            self.last_search_time = current_time
            threading.Thread(target=self.search_processes).start()

    def search_processes(self):
        search_text = self.search_entry.get().lower()
        self.mutex.acquire()
        self.process_listbox.delete(0, tk.END)
        for process in psutil.process_iter(['pid', 'name']):
            if search_text in process.info['name'].lower():
                self.process_listbox.insert(tk.END, f"{process.info['pid']} - {process.info['name']}")
        self.mutex.release()

    def refresh_process_list(self):
        self.process_listbox.delete(0, tk.END)
        for process in psutil.process_iter(['pid', 'name']):
            self.process_listbox.insert(tk.END, f"{process.info['pid']} - {process.info['name']}")

root = tk.Tk()
app = ProcessInjectorGUI(root)
root.mainloop()
