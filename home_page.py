import tkinter as tk
from tkinter import ttk
from datetime import datetime

class HomePage:
    def __init__(self, parent_frame, department_name):
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.create_page()
    
    def create_page(self):
        # Modern header
        header_frame = tk.Frame(self.parent_frame, bg='#2c3e50', height=120)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"🏠 Welcome to {self.department_name}",
                font=('Segoe UI', 18, 'bold'), bg='#2c3e50', fg='white').pack(pady=20)
        
        # Dashboard cards
        cards_frame = tk.Frame(self.parent_frame, bg='#ecf0f1')
        cards_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Quick stats cards
        stats_row = tk.Frame(cards_frame, bg='#ecf0f1')
        stats_row.pack(fill='x', pady=(0, 20))
        
        # Sample dashboard cards
        self.create_stat_card(stats_row, "📦 Total Items", "150", "#3498db")
        self.create_stat_card(stats_row, "🛒 Pending PRs", "8", "#e74c3c")
        self.create_stat_card(stats_row, "📥 Received Today", "12", "#27ae60")
        self.create_stat_card(stats_row, "🏢 Active Suppliers", "25", "#f39c12")
        
        # Recent activity
        activity_frame = tk.LabelFrame(cards_frame, text="Recent Activity", 
                                     font=('Segoe UI', 12, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        activity_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(activity_frame, text="• Purchase Request PR-001 submitted",
                font=('Segoe UI', 10), bg='#ecf0f1', fg='#34495e').pack(anchor='w', padx=10, pady=5)
        tk.Label(activity_frame, text="• Material received from Supplier ABC",
                font=('Segoe UI', 10), bg='#ecf0f1', fg='#34495e').pack(anchor='w', padx=10, pady=5)
        tk.Label(activity_frame, text="• Inventory updated for 15 items",
                font=('Segoe UI', 10), bg='#ecf0f1', fg='#34495e').pack(anchor='w', padx=10, pady=5)
    
    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg='white', relief='solid', bd=1, width=180, height=100)
        card.pack(side='left', padx=10, pady=10)
        card.pack_propagate(False)
        
        tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'), 
                bg='white', fg=color).pack(pady=(15, 5))
        tk.Label(card, text=value, font=('Segoe UI', 20, 'bold'), 
                bg='white', fg='#2c3e50').pack()