# SmartCab AI – Professional GUI (Tkinter + ttk)
# Now with:
# 1) Live incremental updates per app (Uber → Ola → Rapido)
# 2) Integrated Logs tab inside the results section
# Works with your existing logic (apps/, compareprices.py, agent_runner.py)

import threading
import tkinter as tk
from tkinter import ttk, messagebox

from apps import uber, ola, rapido
from compareprices import compare_and_choose


# -----------------------------
# Styling helpers
# -----------------------------

def setup_styles(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure("TFrame", background="#0b1220")
    style.configure("Header.TLabel", background="#0b1220", foreground="#e5e7eb", font=("Segoe UI", 20, "bold"))
    style.configure("SubHeader.TLabel", background="#0b1220", foreground="#9ca3af", font=("Segoe UI", 10))
    style.configure("Card.TFrame", background="#111827")
    style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
    style.configure("Field.TLabel", background="#111827", foreground="#c7d2fe")
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
    style.configure("Accent.TButton", background="#2563eb", foreground="#ffffff")
    style.map("Accent.TButton", background=[("active", "#1d4ed8")])

    style.configure("Treeview",
                    background="#0f172a",
                    foreground="#e5e7eb",
                    rowheight=26,
                    fieldbackground="#0f172a")
    style.configure("Treeview.Heading",
                    background="#1f2933",
                    foreground="#e5e7eb",
                    font=("Segoe UI", 10, "bold"))

    style.configure("Status.TLabel", background="#0b1220", foreground="#22c55e", font=("Segoe UI", 10, "bold"))
    style.configure("Warn.TLabel", background="#0b1220", foreground="#fbbf24", font=("Segoe UI", 10, "bold"))


class SmartCabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartCab AI – Autonomous Cab Booking")
        self.root.geometry("980x680")
        self.root.minsize(980, 680)

        setup_styles(root)

        self.pickup_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.vehicle_var = tk.StringVar(value="cab")

        self.uber_data = None
        self.ola_data = None
        self.rapido_data = None

        self.build_ui()

    # ---------------- UI -----------------

    def build_ui(self):
        self.root.configure(bg="#0b1220")

        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=20, pady=(16, 8))

        ttk.Label(header, text="🚕 SmartCab AI", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="Multi‑App Autonomous Cab Booking using DroidRun + Gemini", style="SubHeader.TLabel").pack(anchor="w", pady=(4, 0))

        # Main content
        content = ttk.Frame(self.root)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # Left card – Inputs
        left = ttk.Frame(content, style="Card.TFrame")
        left.pack(side="left", fill="y", padx=(0, 12), pady=8)

        ttk.Label(left, text="Trip Details", font=("Segoe UI", 12, "bold"), background="#111827", foreground="#e5e7eb").pack(anchor="w", padx=16, pady=(12, 8))

        form = ttk.Frame(left, style="Card.TFrame")
        form.pack(fill="x", padx=16, pady=8)

        ttk.Label(form, text="Pickup Location", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.pickup_var, width=30).grid(row=1, column=0, pady=(0, 10))

        ttk.Label(form, text="Destination", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.dest_var, width=30).grid(row=3, column=0, pady=(0, 14))

        self.next_btn = ttk.Button(form, text="Fetch Prices →", style="Accent.TButton", command=self.start_fetching)
        self.next_btn.grid(row=4, column=0, sticky="ew")

        # Vehicle selection
        ttk.Label(left, text="Vehicle Type", font=("Segoe UI", 12, "bold"), background="#111827", foreground="#e5e7eb").pack(anchor="w", padx=16, pady=(18, 6))

        vbox = ttk.Frame(left, style="Card.TFrame")
        vbox.pack(anchor="w", padx=16, pady=(0, 12))

        ttk.Radiobutton(vbox, text="Cab", variable=self.vehicle_var, value="cab").pack(anchor="w", pady=2)
        ttk.Radiobutton(vbox, text="Auto", variable=self.vehicle_var, value="auto").pack(anchor="w", pady=2)
        ttk.Radiobutton(vbox, text="Bike", variable=self.vehicle_var, value="bike").pack(anchor="w", pady=2)

        # Status area
        self.status_label = ttk.Label(left, text="Idle", style="Status.TLabel")
        self.status_label.pack(anchor="w", padx=16, pady=(10, 12))

        # Right side – Results
        right = ttk.Frame(content, style="Card.TFrame")
        right.pack(side="right", fill="both", expand=True, pady=8)

        ttk.Label(right, text="Live Results", font=("Segoe UI", 12, "bold"), background="#111827", foreground="#e5e7eb").pack(anchor="w", padx=16, pady=(12, 6))

        # Tabs for apps + logs
        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.uber_tab = self.create_table_tab("Uber")
        self.ola_tab = self.create_table_tab("Ola")
        self.rapido_tab = self.create_table_tab("Rapido")
        self.logs_tab = self.create_logs_tab()

        # Bottom actions
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=20, pady=(0, 16))

        self.progress = ttk.Progressbar(bottom, mode="indeterminate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.book_btn = ttk.Button(bottom, text="Compare & Book", style="Accent.TButton", command=self.compare_and_book, state="disabled")
        self.book_btn.pack(side="right")

    def create_table_tab(self, name):
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text=name)

        cols = ("Service", "Price (₹)", "ETA (min)")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center")

        tree.pack(fill="both", expand=True, padx=8, pady=8)
        setattr(self, f"{name.lower()}_table", tree)
        return frame

    def create_logs_tab(self):
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text="Logs")

        self.log_text = tk.Text(frame, bg="#020617", fg="#e5e7eb", insertbackground="#e5e7eb", wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.log_text.configure(state="disabled")

        return frame

    # ---------------- Helpers -----------------

    def log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def set_status(self, text, warn=False):
        if warn:
            self.status_label.configure(text=text, style="Warn.TLabel")
        else:
            self.status_label.configure(text=text, style="Status.TLabel")

    def clear_table(self, table):
        for i in table.get_children():
            table.delete(i)

    def fill_table(self, table, data, key_service="service"):
        self.clear_table(table)
        if not data:
            return
        for item in data:
            if not isinstance(item, dict):
                continue
            service = item.get(key_service) or item.get("ride_type") or "-"
            price = item.get("price") or item.get("estimated_fare") or "-"
            eta = item.get("eta") or item.get("time") or "-"
            table.insert("", "end", values=(service, price, eta))

    # ---------------- Logic -----------------

    def start_fetching(self):
        pickup = self.pickup_var.get().strip()
        dest = self.dest_var.get().strip()

        if not pickup or not dest:
            messagebox.showerror("Missing data", "Please enter pickup and destination")
            return

        self.next_btn.config(state="disabled")
        self.book_btn.config(state="disabled")
        self.set_status("Fetching prices…")
        self.log("Starting price fetch…")

        self.progress.start(10)

        threading.Thread(target=self.fetch_prices_incremental, daemon=True).start()

    def fetch_prices_incremental(self):
        try:
            # Uber
            self.log("Fetching Uber prices…")
            self.uber_data = uber.get_prices(self.pickup_var.get(), self.dest_var.get())
            self.root.after(0, lambda: self.update_single_table("uber"))

            # Ola
            self.log("Fetching Ola prices…")
            self.ola_data = ola.get_prices(self.pickup_var.get(), self.dest_var.get())
            self.root.after(0, lambda: self.update_single_table("ola"))

            # Rapido
            self.log("Fetching Rapido prices…")
            self.rapido_data = rapido.get_prices(self.pickup_var.get(), self.dest_var.get())
            self.root.after(0, lambda: self.update_single_table("rapido"))

            self.root.after(0, self.finish_fetching)
        except Exception as e:
            self.root.after(0, lambda: self.on_error(str(e)))

    def update_single_table(self, app_name):
        if app_name == "uber":
            self.fill_table(self.uber_table, self.uber_data, "service")
            self.log("Uber prices updated in UI")
        elif app_name == "ola":
            ola_list = self.ola_data.get("json") if isinstance(self.ola_data, dict) else self.ola_data
            self.fill_table(self.ola_table, ola_list, "service")
            self.log("Ola prices updated in UI")
        elif app_name == "rapido":
            rapido_list = self.rapido_data.get("json") if isinstance(self.rapido_data, dict) else self.rapido_data
            self.fill_table(self.rapido_table, rapido_list, "ride_type")
            self.log("Rapido prices updated in UI")

    def finish_fetching(self):
        self.progress.stop()
        self.set_status("Prices fetched successfully")
        self.log("All prices fetched successfully")
        self.book_btn.config(state="normal")
        self.next_btn.config(state="normal")

    def on_error(self, msg):
        self.progress.stop()
        self.set_status("Error occurred", warn=True)
        self.log("ERROR: " + msg)
        messagebox.showerror("Error", msg)
        self.next_btn.config(state="normal")

    def compare_and_book(self):
        type_map = {"cab": "1", "auto": "2", "bike": "3"}
        choice = type_map[self.vehicle_var.get()]

        # UI feedback immediately
        self.set_status("Comparing using Gemini…")
        self.log("Comparing options using Gemini…")
        self.progress.start(10)
        self.book_btn.config(state="disabled")

        def compare_task():
            winner = compare_and_choose(self.uber_data, self.ola_data, self.rapido_data, choice)

            def after_compare():
                if winner == "NoServiceFound":
                    self.progress.stop()
                    self.set_status("No suitable service found", warn=True)
                    self.log("No suitable service found")
                    self.book_btn.config(state="normal")
                    return

                # Show selected app immediately
                self.set_status(f"Selected: {winner}")
                self.log(f"Best option selected: {winner}")

                # Switch to logs tab automatically
                self.tabs.select(self.logs_tab)

                # Start booking in background
                self.set_status(f"Booking on {winner}…")
                self.log(f"Booking ride on {winner}…")

                threading.Thread(target=booking_task, args=(winner,), daemon=True).start()

            self.root.after(0, after_compare)

        def booking_task(winner):
            # Heavy / blocking automation here
            if winner == "Uber":
                res = uber.book_ride(self.pickup_var.get(), self.dest_var.get(), self.vehicle_var.get())
            elif winner == "Ola":
                res = ola.book_ride(self.pickup_var.get(), self.dest_var.get(), self.vehicle_var.get())
            elif winner == "Rapido":
                res = rapido.book_ride(self.pickup_var.get(), self.dest_var.get(), self.vehicle_var.get())
            else:
                res = None

            def after_booking():
                self.progress.stop()
                if res is None:
                    self.set_status("Booking failed", warn=True)
                    self.log("Booking failed")
                else:
                    self.set_status("Booking initiated successfully ✓")
                    self.log("Booking initiated successfully")
                    messagebox.showinfo("Success", f"Ride booking initiated on {winner}.")

                self.book_btn.config(state="normal")

            self.root.after(0, after_booking)

        threading.Thread(target=compare_task, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCabApp(root)
    root.mainloop()
