import tkinter as tk
from tkinter import ttk
from gui.config_window import ConfigWindow
from gui.monitor_window import MonitorWindow
from src.trade_engine import TradeEngine


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Trading Monitor")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.engine = None
        self.monitor_window = None
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(
            main_frame, 
            text="Stock Trading Monitor", 
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 30))
        
        desc_label = ttk.Label(
            main_frame,
            text="Real-time stock price monitoring and portfolio management application",
            font=("Arial", 11),
            wraplength=600
        )
        desc_label.grid(row=1, column=0, pady=(0, 40))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=20)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Configuration",
            command=self.open_config,
            width=25
        )
        self.start_button.pack(pady=10)
        
        exit_button = ttk.Button(
            button_frame,
            text="Exit",
            command=self.on_closing,
            width=25
        )
        exit_button.pack(pady=10)
        
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, pady=20, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready to start",
            font=("Arial", 10)
        )
        self.status_label.grid(row=0, column=0)
        
    def open_config(self):
        self.start_button.config(state="disabled")
        self.status_label.config(text="Opening configuration window...")
        config_window = ConfigWindow(self.root, self.on_config_complete)
        
    def on_config_complete(self, portfolio, alerts, symbols):
        if portfolio or alerts:
            self.status_label.config(text="Configuration complete, starting engine...")
            self.root.update()
            
            self.engine = TradeEngine(portfolio, alerts, symbols)
            self.engine.start()
            
            self.monitor_window = MonitorWindow(self.root, self.engine)
            self.status_label.config(text="Engine running - monitoring active")
            self.root.withdraw()
        else:
            self.status_label.config(text="Configuration cancelled")
            self.start_button.config(state="normal")
    
    def on_closing(self):
        if self.engine:
            self.engine.stop_event.set()
        if self.monitor_window:
            self.monitor_window.destroy()
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def start_gui():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    start_gui()
