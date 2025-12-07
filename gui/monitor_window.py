import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time


class MonitorWindow:
    def __init__(self, parent, engine):
        self.engine = engine
        self.window = tk.Toplevel(parent)
        self.window.title("Stock Monitor - Real-time")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        self.window.update_idletasks()
        width = 900
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.running = True
        self.setup_ui()
        
        self.add_log("Monitor started")
        self.add_log(f"Portfolio: {list(engine.shared_state.portfolio.keys())}")
        self.add_log(f"Alerts set for: {list(engine.shared_state.alerts.keys())}")
        
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        title_label = ttk.Label(
            main_frame,
            text="Stock Monitor - Real-time",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 15), sticky=tk.W)
        
        value_frame = ttk.LabelFrame(main_frame, text="Portfolio Value", padding="15")
        value_frame.grid(row=1, column=0, pady=(0, 15), sticky=(tk.W, tk.E))
        value_frame.columnconfigure(0, weight=1)
        
        self.portfolio_value_label = ttk.Label(
            value_frame,
            text="$0.00",
            font=("Arial", 24, "bold"),
            foreground="#2E7D32"
        )
        self.portfolio_value_label.grid(row=0, column=0)
        
        prices_frame = ttk.LabelFrame(main_frame, text="Current Prices", padding="10")
        prices_frame.grid(row=2, column=0, pady=(0, 15), sticky=(tk.W, tk.E, tk.N, tk.S))
        prices_frame.columnconfigure(0, weight=1)
        prices_frame.rowconfigure(0, weight=1)
        
        tree_frame = ttk.Frame(prices_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.prices_tree = ttk.Treeview(
            tree_frame,
            columns=("ticker", "price", "shares", "value", "alert"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=8
        )
        scrollbar.config(command=self.prices_tree.yview)
        
        self.prices_tree.heading("ticker", text="Ticker")
        self.prices_tree.heading("price", text="Price")
        self.prices_tree.heading("shares", text="Shares")
        self.prices_tree.heading("value", text="Value")
        self.prices_tree.heading("alert", text="Alert limit")
        
        self.prices_tree.column("ticker", width=120)
        self.prices_tree.column("price", width=120)
        self.prices_tree.column("shares", width=120)
        self.prices_tree.column("value", width=120)
        self.prices_tree.column("alert", width=120)
        
        self.prices_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame = ttk.LabelFrame(main_frame, text="Logs and Alerts", padding="10")
        log_frame.grid(row=3, column=0, pady=(0, 15), sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=10,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop monitoring",
            command=self.on_closing,
            width=20
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
    def update_loop(self):
        """Background thread that updates the GUI"""
        while self.running:
            try:
                self.window.after(0, self.update_display)
                time.sleep(2)
            except:
                break
    
    def update_display(self):
        """Update GUI with current data from engine"""
        if not self.running:
            return
        
        try:
            with self.engine.shared_state.lock:
                value = self.engine.shared_state.portfolio_value
                self.portfolio_value_label.config(text=f"${value:,.2f}")
                
                for item in self.prices_tree.get_children():
                    self.prices_tree.delete(item)
                
                prices = self.engine.shared_state.prices
                portfolio = self.engine.shared_state.portfolio
                alerts = self.engine.shared_state.alerts
                
                for symbol in self.engine.shared_state.symbols:
                    price = prices.get(symbol, 0.0)
                    shares = portfolio.get(symbol, 0)
                    stock_value = price * shares if shares > 0 else 0
                    alert_limit = alerts.get(symbol, None)
                    
                    alert_str = f"${alert_limit:.2f}" if alert_limit else "-"
                    
                    tag = ""
                    if alert_limit and price > alert_limit:
                        tag = "alert"
                    
                    self.prices_tree.insert(
                        "", 
                        tk.END, 
                        values=(
                            symbol, 
                            f"${price:.2f}", 
                            shares if shares > 0 else "-",
                            f"${stock_value:.2f}" if stock_value > 0 else "-",
                            alert_str
                        ),
                        tags=(tag,)
                    )
                
                self.prices_tree.tag_configure("alert", background="#FFCDD2")
            
            while not self.engine.log_queue.empty():
                try:
                    msg = self.engine.log_queue.get_nowait()
                    self.add_log(msg)
                except:
                    break
                    
        except Exception as e:
            self.add_log(f"Error updating display: {e}")
    
    def add_log(self, message):
        """Add a log message to the log text widget"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        
        if "ALERT" in message.upper():
            last_line = self.log_text.index("end-1c linestart")
            self.log_text.tag_add("alert", last_line, "end-1c")
            self.log_text.tag_config("alert", foreground="#D32F2F", font=("Consolas", 9, "bold"))
        
        self.log_text.see(tk.END)
        
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 1000:
            self.log_text.delete('1.0', '2.0')
    
    def on_closing(self):
        self.running = False
        self.engine.stop_event.set()
        
        time.sleep(0.5)
        
        self.window.destroy()
        
        try:
            parent = self.window.master
            if parent:
                parent.quit()
                parent.destroy()
        except:
            pass
    
    def destroy(self):
        self.on_closing()
