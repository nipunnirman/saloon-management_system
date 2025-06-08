import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from datetime import datetime

DATA_FILE = "data.json"
BARBERS = ["Barber1", "Barber2", "Barber3", "Barber4"]

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"barbers": {name: [] for name in BARBERS}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

def add_entry(barber, amount, color_packets):
    entry = {
        "amount": amount,
        "color_packets": color_packets,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    data["barbers"][barber].append(entry)
    save_data()

def calculate_summary():
    today = datetime.now().strftime("%Y-%m-%d")
    summary = {
        "barbers": {},
        "total_haircuts": 0,
        "total_color_packets": 0,
        "total_shop_income": 0,
        "total_owner_income": 0
    }
    for barber, entries in data["barbers"].items():
        total = 0
        cuts = 0
        packets = 0
        for e in entries:
            if e["date"] == today:
                cuts += 1
                total += e["amount"]
                packets += e["color_packets"]
        barber_income = total * 0.6
        owner_income = total * 0.4 + packets * 250
        summary["barbers"][barber] = {
            "haircuts": cuts,
            "barber_income": barber_income,
            "packets": packets
        }
        summary["total_haircuts"] += cuts
        summary["total_color_packets"] += packets
        summary["total_shop_income"] += total
        summary["total_owner_income"] += owner_income
    return summary

def export_report():
    today = datetime.now().strftime("%Y-%m-%d")
    # Gather today's entries for all barbers
    rows = []
    for barber, entries in data["barbers"].items():
        for e in entries:
            if e["date"] == today:
                rows.append([
                    barber,
                    e["date"],
                    e["amount"],
                    e["color_packets"],
                    e["amount"] * 0.6,  # Barber income (60%)
                    e["amount"] * 0.4 + e["color_packets"] * 250  # Owner income (40% + Rs.250 per packet)
                ])
    if not rows:
        messagebox.showinfo("No Data", "No data for today to export.")
        return

    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save report as..."
    )
    if not file_path:
        return

   
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
       
        writer.writerow(["Barber", "Date", "Haircut Amount (Rs)", "Color Packets", "Barber Income (Rs)", "Owner Income (Rs)"])
        writer.writerows(rows)

    messagebox.showinfo("Export Successful", f"Report exported successfully:\n{file_path}")

root = tk.Tk()
root.title("Salon Management System")
root.state('zoomed')

main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

barber_entries = {}

barber_row = ttk.Frame(main_frame)
barber_row.pack(side="top", fill="x")

def make_submit(barber):
    def submit(event=None):
        try:
            amount = float(barber_entries[barber]["amount"].get())
            packets = int(barber_entries[barber]["packets"].get())
            add_entry(barber, amount, packets)
            barber_entries[barber]["amount"].delete(0, tk.END)
            barber_entries[barber]["packets"].delete(0, tk.END)
            update_summary()
            barber_entries[barber]["amount"].focus()
        except Exception:
            messagebox.showerror("Invalid Input", "Please enter valid numbers")
    return submit

def on_amount_enter(barber):
    def handler(event):
        barber_entries[barber]["packets"].focus()
    return handler

def on_packets_enter(barber):
    def handler(event):
        make_submit(barber)()
    return handler

for barber in BARBERS:
    frame = ttk.Frame(barber_row, padding=10, relief="ridge")
    frame.pack(side="left", expand=True, fill="both", padx=5)

    ttk.Label(frame, text=barber, font=("Arial", 16, "bold")).pack(pady=10)

    amount_entry = ttk.Entry(frame, font=("Arial", 16))
    amount_entry.pack(pady=5)
    amount_entry.insert(0, "Enter haircut amount")
    amount_entry.bind("<FocusIn>", lambda e, entry=amount_entry: entry.delete(0, tk.END))
    amount_entry.bind("<Return>", on_amount_enter(barber))

    ttk.Label(frame, text="Color Packets").pack()

    packet_entry = ttk.Entry(frame, font=("Arial", 16))
    packet_entry.pack(pady=5)
    packet_entry.insert(0, "Enter color packets")
    packet_entry.bind("<FocusIn>", lambda e, entry=packet_entry: entry.delete(0, tk.END))
    packet_entry.bind("<Return>", on_packets_enter(barber))

    submit_btn = ttk.Button(frame, text="Submit", command=make_submit(barber))
    submit_btn.pack(pady=5)

    barber_entries[barber] = {"amount": amount_entry, "packets": packet_entry}

summary_frame = ttk.Frame(root)
summary_frame.pack(side="bottom", fill="both", expand=True)

summary_text = tk.Text(summary_frame, height=18, font=("Arial", 14))
summary_text.pack(fill="both", expand=True)

def update_summary():
    summary = calculate_summary()
    summary_text.delete(1.0, tk.END)
    for barber, s in summary["barbers"].items():
        summary_text.insert(tk.END, f"{barber} - Haircuts: {s['haircuts']}, Packets: {s['packets']}, Barber Income: Rs. {s['barber_income']:.2f}\n")
    summary_text.insert(tk.END, "\n──── SHOP TOTAL ────\n")
    summary_text.insert(tk.END, f"Total Haircuts: {summary['total_haircuts']}\n")
    summary_text.insert(tk.END, f"Total Packets: {summary['total_color_packets']}\n")
    summary_text.insert(tk.END, f"Shop Income: Rs. {summary['total_shop_income']:.2f}\n")
    summary_text.insert(tk.END, f"Owner Income: Rs. {summary['total_owner_income']:.2f}\n")

def reset_today():
    if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset today's data?"):
        today = datetime.now().strftime("%Y-%m-%d")
        for barber in BARBERS:
            data["barbers"][barber] = [e for e in data["barbers"][barber] if e["date"] != today]
        save_data()
        update_summary()

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

export_btn = ttk.Button(button_frame, text="Export Today's Report", command=export_report)
export_btn.pack(side="left", padx=10)

reset_btn = ttk.Button(button_frame, text="Reset Today", command=reset_today)
reset_btn.pack(side="left", padx=10)

update_summary()
root.mainloop()
