import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime

class CompletedPRs:
    def __init__(self, parent_frame, department_name):
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.data_file = f"completed_prs_{department_name.lower().replace(' ', '_')}.json"
        self.create_page()
        self.load_completed_prs()
    
    def create_page(self):
        # Main container
        main_container = tk.Frame(self.parent_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with dropdown
        header_frame = tk.Frame(main_container, bg='#ecf0f1')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Completed Purchase Requests", 
                font=('Helvetica', 16, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(side='left', padx=10, pady=10)
        
        # Filter dropdown
        filter_frame = tk.Frame(header_frame, bg='#ecf0f1')
        filter_frame.pack(side='right', padx=10, pady=10)
        
        tk.Label(filter_frame, text="Filter by Status:", font=('Arial', 10), 
                bg='#ecf0f1', fg='#34495e').pack(side='left', padx=(0, 5))
        
        self.status_var = tk.StringVar(value="All")
        status_dropdown = ttk.Combobox(filter_frame, textvariable=self.status_var, 
                                      values=["All", "Completed", "Approved", "Delivered"], 
                                      state="readonly", width=12)
        status_dropdown.pack(side='left')
        status_dropdown.bind('<<ComboboxSelected>>', self.filter_prs)
        
        # Table container
        table_container = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        table_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(table_container, bg='white')
        v_scrollbar = ttk.Scrollbar(table_container, orient='vertical', command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient='horizontal', command=canvas.xview)
        
        self.table_frame = tk.Frame(canvas, bg='white')
        canvas.create_window((0, 0), window=self.table_frame, anchor='nw')
        
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        self.table_frame.bind('<Configure>', configure_scroll_region)
        
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        canvas.pack(side='left', fill='both', expand=True)
        
        self.canvas = canvas
        
        # Create table headers
        self.create_table_headers()
    
    def create_table_headers(self):
        headers = ['PR ID', 'Date Submitted', 'Items Count', 'Status', 'Approved By', 'Actions']
        
        # Header row
        header_frame = tk.Frame(self.table_frame, bg='#3498db')
        header_frame.pack(fill='x', padx=1, pady=1)
        
        for col, header in enumerate(headers):
            tk.Label(header_frame, text=header, font=('Arial', 10, 'bold'), 
                    bg='#3498db', fg='white', relief='solid', bd=1, 
                    width=15 if col != 4 else 20).grid(row=0, column=col, sticky='nsew', padx=0, pady=0)
        
        # Configure column weights
        for col in range(len(headers)):
            header_frame.grid_columnconfigure(col, weight=1)
    
    def load_completed_prs(self):
        """Load completed PRs from file"""
        self.completed_prs = []
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.completed_prs = json.load(f)
            except Exception as e:
                print(f"Error loading completed PRs: {e}")
        else:
            # Create sample data for demonstration
            self.create_sample_data()
        
        self.display_prs()
    
    def create_sample_data(self):
        """Create sample completed PRs data"""
        sample_data = [
            {
                "pr_id": "PR001",
                "date_submitted": "2024-01-15",
                "items": [
                    {"resource_code": "RC001", "item_description": "Office Chair"},
                    {"resource_code": "RC002", "item_description": "Desk Lamp"}
                ],
                "status": "Completed",
                "approved_by": "John Manager"
            },
            {
                "pr_id": "PR002", 
                "date_submitted": "2024-01-10",
                "items": [
                    {"resource_code": "RC003", "item_description": "Laptop Stand"},
                    {"resource_code": "RC004", "item_description": "Wireless Mouse"},
                    {"resource_code": "RC005", "item_description": "Keyboard"}
                ],
                "status": "Approved",
                "approved_by": "Sarah Director"
            },
            {
                "pr_id": "PR003",
                "date_submitted": "2024-01-08", 
                "items": [
                    {"resource_code": "RC006", "item_description": "Monitor Stand"}
                ],
                "status": "Delivered",
                "approved_by": "Mike Supervisor"
            }
        ]
        
        self.completed_prs = sample_data
        self.save_completed_prs()
    
    def save_completed_prs(self):
        """Save completed PRs to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.completed_prs, f, indent=2)
        except Exception as e:
            print(f"Error saving completed PRs: {e}")
    
    def display_prs(self):
        """Display PRs in table format"""
        # Clear existing rows
        for widget in self.table_frame.winfo_children()[1:]:
            widget.destroy()
        
        # Filter PRs based on status
        filtered_prs = self.get_filtered_prs()
        
        # Display each PR
        for pr in filtered_prs:
            self.create_pr_row(pr)
        
        # Update scroll region
        self.table_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def get_filtered_prs(self):
        """Get PRs filtered by selected status"""
        status_filter = self.status_var.get()
        if status_filter == "All":
            return self.completed_prs
        else:
            return [pr for pr in self.completed_prs if pr['status'] == status_filter]
    
    def create_pr_row(self, pr):
        """Create a row for a PR"""
        row_frame = tk.Frame(self.table_frame, bg='white')
        row_frame.pack(fill='x', padx=1, pady=1)
        
        # PR ID
        tk.Label(row_frame, text=pr['pr_id'], font=('Arial', 9), 
                bg='white', fg='#2c3e50', relief='solid', bd=1, 
                width=15).grid(row=0, column=0, sticky='nsew')
        
        # Date Submitted
        tk.Label(row_frame, text=pr['date_submitted'], font=('Arial', 9), 
                bg='white', fg='#2c3e50', relief='solid', bd=1, 
                width=15).grid(row=0, column=1, sticky='nsew')
        
        # Items Count
        tk.Label(row_frame, text=str(len(pr['items'])), font=('Arial', 9), 
                bg='white', fg='#2c3e50', relief='solid', bd=1, 
                width=15).grid(row=0, column=2, sticky='nsew')
        
        # Status with color coding
        status_color = self.get_status_color(pr['status'])
        tk.Label(row_frame, text=pr['status'], font=('Arial', 9, 'bold'), 
                bg=status_color, fg='white', relief='solid', bd=1, 
                width=15).grid(row=0, column=3, sticky='nsew')
        
        # Approved By
        tk.Label(row_frame, text=pr['approved_by'], font=('Arial', 9), 
                bg='white', fg='#2c3e50', relief='solid', bd=1, 
                width=20).grid(row=0, column=4, sticky='nsew')
        
        # Actions
        action_frame = tk.Frame(row_frame, bg='white', relief='solid', bd=1)
        action_frame.grid(row=0, column=5, sticky='nsew')
        
        view_btn = tk.Button(action_frame, text="View", bg='#3498db', fg='white', 
                            font=('Arial', 8), command=lambda: self.view_pr_details(pr))
        view_btn.pack(side='left', padx=2, pady=2)
        
        # Configure column weights
        for col in range(6):
            row_frame.grid_columnconfigure(col, weight=1)
    
    def get_status_color(self, status):
        """Get color for status"""
        colors = {
            'Completed': '#27ae60',
            'Approved': '#f39c12', 
            'Delivered': '#8e44ad',
            'Pending': '#e74c3c'
        }
        return colors.get(status, '#95a5a6')
    
    def filter_prs(self, event=None):
        """Filter PRs based on dropdown selection"""
        self.display_prs()
    
    def view_pr_details(self, pr):
        """View detailed PR information"""
        # Create detail window
        detail_window = tk.Toplevel(self.parent_frame)
        detail_window.title(f"PR Details - {pr['pr_id']}")
        detail_window.geometry("600x400")
        detail_window.configure(bg='white')
        
        # Make window modal
        detail_window.transient(self.parent_frame.winfo_toplevel())
        detail_window.grab_set()
        
        # Header
        header_frame = tk.Frame(detail_window, bg='#ecf0f1')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(header_frame, text=f"Purchase Request - {pr['pr_id']}", 
                font=('Helvetica', 16, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(pady=10)
        
        # PR Info
        info_frame = tk.Frame(detail_window, bg='white')
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(info_frame, text=f"Date Submitted: {pr['date_submitted']}", 
                font=('Arial', 11), bg='white', fg='#34495e').pack(anchor='w')
        tk.Label(info_frame, text=f"Status: {pr['status']}", 
                font=('Arial', 11), bg='white', fg='#34495e').pack(anchor='w')
        tk.Label(info_frame, text=f"Approved By: {pr['approved_by']}", 
                font=('Arial', 11), bg='white', fg='#34495e').pack(anchor='w')
        
        # Items table
        items_frame = tk.Frame(detail_window, bg='white')
        items_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(items_frame, text="Items:", font=('Arial', 12, 'bold'), 
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        
        # Items table headers
        items_header = tk.Frame(items_frame, bg='#3498db')
        items_header.pack(fill='x')
        
        tk.Label(items_header, text="S.No", font=('Arial', 10, 'bold'), 
                bg='#3498db', fg='white', relief='solid', bd=1).grid(row=0, column=0, sticky='nsew')
        tk.Label(items_header, text="Resource Code", font=('Arial', 10, 'bold'), 
                bg='#3498db', fg='white', relief='solid', bd=1).grid(row=0, column=1, sticky='nsew')
        tk.Label(items_header, text="Item Description", font=('Arial', 10, 'bold'), 
                bg='#3498db', fg='white', relief='solid', bd=1).grid(row=0, column=2, sticky='nsew')
        
        items_header.grid_columnconfigure(0, weight=0, minsize=60)
        items_header.grid_columnconfigure(1, weight=1, minsize=150)
        items_header.grid_columnconfigure(2, weight=2, minsize=300)
        
        # Items rows
        for i, item in enumerate(pr['items'], 1):
            item_row = tk.Frame(items_frame, bg='white')
            item_row.pack(fill='x')
            
            tk.Label(item_row, text=str(i), font=('Arial', 9), 
                    bg='white', fg='#2c3e50', relief='solid', bd=1).grid(row=0, column=0, sticky='nsew')
            tk.Label(item_row, text=item['resource_code'], font=('Arial', 9), 
                    bg='white', fg='#2c3e50', relief='solid', bd=1).grid(row=0, column=1, sticky='nsew')
            tk.Label(item_row, text=item['item_description'], font=('Arial', 9), 
                    bg='white', fg='#2c3e50', relief='solid', bd=1, 
                    wraplength=280, justify='left').grid(row=0, column=2, sticky='nsew')
            
            item_row.grid_columnconfigure(0, weight=0, minsize=60)
            item_row.grid_columnconfigure(1, weight=1, minsize=150)
            item_row.grid_columnconfigure(2, weight=2, minsize=300)
        
        # Close button
        tk.Button(detail_window, text="Close", bg='#95a5a6', fg='white', 
                 font=('Arial', 10, 'bold'), command=detail_window.destroy).pack(pady=20)
        
        # Center the window
        detail_window.update_idletasks()
        x = (detail_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (detail_window.winfo_screenheight() // 2) - (400 // 2)
        detail_window.geometry(f"600x400+{x}+{y}")
    
    def add_completed_pr(self, pr_data):
        """Add a new completed PR (called when PR is submitted)"""
        new_pr = {
            "pr_id": f"PR{len(self.completed_prs) + 1:03d}",
            "date_submitted": datetime.now().strftime("%Y-%m-%d"),
            "items": pr_data,
            "status": "Completed",
            "approved_by": "System Auto"
        }
        
        self.completed_prs.append(new_pr)
        self.save_completed_prs()
        self.display_prs()