import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import warnings
import sys
import os


class ConfigWindow:
    def __init__(self, parent, callback):
        self.callback = callback
        self.window = tk.Toplevel(parent)
        self.window.title("Portfolio and Alerts Configuration")
        self.window.geometry("700x600")
        self.window.resizable(True, True)
        
        self.window.update_idletasks()
        width = 700
        height = 600
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.portfolio = {}
        self.alerts = {}
        
        self.setup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        title_label = ttk.Label(
            main_frame,
            text="Portfolio Configuration",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 15), sticky=tk.W)
        
        input_frame = ttk.LabelFrame(main_frame, text="Add Stock", padding="10")
        input_frame.grid(row=1, column=0, pady=(0, 15), sticky=(tk.W, tk.E))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Ticker:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.ticker_entry = ttk.Entry(input_frame, width=15)
        self.ticker_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(input_frame, text="Number of shares:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.shares_entry = ttk.Entry(input_frame, width=10)
        self.shares_entry.grid(row=0, column=3, sticky=tk.W)
        
        self.alert_var = tk.BooleanVar()
        self.alert_check = ttk.Checkbutton(
            input_frame,
            text="Set alert at price:",
            variable=self.alert_var,
            command=self.toggle_alert_entry
        )
        self.alert_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.alert_entry = ttk.Entry(input_frame, width=15, state="disabled")
        self.alert_entry.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        add_button = ttk.Button(
            input_frame,
            text="Add",
            command=self.add_stock
        )
        add_button.grid(row=2, column=0, columnspan=4, pady=(15, 0))
        
        display_frame = ttk.LabelFrame(main_frame, text="Your Portfolio", padding="10")
        display_frame.grid(row=2, column=0, pady=(0, 15), sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        tree_frame = ttk.Frame(display_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ticker", "shares", "alert"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=10
        )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("shares", text="Number of shares")
        self.tree.heading("alert", text="Alert price")
        
        self.tree.column("ticker", width=150)
        self.tree.column("shares", width=150)
        self.tree.column("alert", width=150)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        remove_button = ttk.Button(
            display_frame,
            text="Remove selected stock",
            command=self.remove_stock
        )
        remove_button.grid(row=1, column=0, pady=(10, 0))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 0))
        
        finish_button = ttk.Button(
            button_frame,
            text="Finish and start",
            command=self.on_finish,
            width=20
        )
        finish_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            width=20
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.ticker_entry.bind("<Return>", lambda e: self.add_stock())
        self.shares_entry.bind("<Return>", lambda e: self.add_stock())
        
    def toggle_alert_entry(self):
        if self.alert_var.get():
            self.alert_entry.config(state="normal")
        else:
            self.alert_entry.config(state="disabled")
            
    def ticker_exists(self, ticker):
        warnings.filterwarnings("ignore")
        stderr_backup = sys.stderr
        sys.stderr = open(os.devnull, "w")
        
        try:
            data = yf.download(ticker, period="1d", interval="1d", progress=False)
            return not data.empty
        except:
            return False
        finally:
            sys.stderr.close()
            sys.stderr = stderr_backup
    
    def add_stock(self):
        ticker = self.ticker_entry.get().strip().upper()
        shares_str = self.shares_entry.get().strip()
        
        if not ticker:
            messagebox.showwarning("Error", "Please enter a ticker!")
            return
        
        if not shares_str:
            messagebox.showwarning("Error", "Please enter number of shares!")
            return
        
        if not self.ticker_exists(ticker):
            messagebox.showerror("Error", f"Ticker '{ticker}' does not exist!")
            return
        
        try:
            shares = int(shares_str)
            if shares <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Error", "Number of shares must be a positive integer!")
            return
        
        self.portfolio[ticker] = shares
        
        alert_price = None
        if self.alert_var.get():
            alert_str = self.alert_entry.get().strip()
            if alert_str:
                try:
                    alert_price = float(alert_str)
                    if alert_price <= 0:
                        raise ValueError()
                    self.alerts[ticker] = alert_price
                except ValueError:
                    messagebox.showwarning("Error", "Invalid alert price!")
                    return
        
        self.update_tree()
        
        self.ticker_entry.delete(0, tk.END)
        self.shares_entry.delete(0, tk.END)
        self.alert_entry.delete(0, tk.END)
        self.alert_var.set(False)
        self.toggle_alert_entry()
        self.ticker_entry.focus()
        
    def remove_stock(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Error", "Select a stock to remove!")
            return
        
        item = self.tree.item(selection[0])
        ticker = item['values'][0]
        
        if ticker in self.portfolio:
            del self.portfolio[ticker]
        if ticker in self.alerts:
            del self.alerts[ticker]
        
        self.update_tree()
        
    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for ticker in self.portfolio:
            shares = self.portfolio[ticker]
            alert = self.alerts.get(ticker, "-")
            self.tree.insert("", tk.END, values=(ticker, shares, alert))
    
    def on_finish(self):
        if not self.portfolio and not self.alerts:
            messagebox.showwarning("Error", "Add at least one stock or alert!")
            return
        
        symbols = list(set(self.portfolio.keys()) | set(self.alerts.keys()))
        self.callback(self.portfolio, self.alerts, symbols)
        self.window.destroy()
        
    def on_cancel(self):
        self.callback({}, {}, [])
        self.window.destroy()
