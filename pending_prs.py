import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from rejected_prs import RejectedPRs

class PendingPRs:
    def __init__(self, parent_frame, department_name):
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.pending_prs = []
        self.data_file = f"pending_prs_{department_name.lower().replace(' ', '_')}.json"
        self.rejected_prs_handler = RejectedPRs(parent_frame, department_name, self.restore_pr_from_rejected)
        self.create_interface()
        self.load_pending_prs()
        self.start_auto_highlight()
    
    def create_interface(self):
        # Header
        header_frame = tk.Frame(self.parent_frame, bg='#f39c12', height=60)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📋 Pending Purchase Requests", 
                font=('Segoe UI', 16, 'bold'), bg='#f39c12', fg='white').pack(pady=15)
        
        # Main content area
        content_frame = tk.Frame(self.parent_frame, bg='#ecf0f1')
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Filter and search section
        filter_frame = tk.Frame(content_frame, bg='#ecf0f1')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="🔍 Search:", font=('Segoe UI', 10, 'bold'),
                bg='#ecf0f1', fg='#2c3e50').pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, width=30,
                               font=('Segoe UI', 10))
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_prs)
        
        # Date filter
        tk.Label(filter_frame, text="📅 Date:", font=('Segoe UI', 10, 'bold'),
                bg='#ecf0f1', fg='#2c3e50').pack(side='left', padx=(20, 5))
        
        self.date_filter_var = tk.StringVar()
        date_entry = tk.Entry(filter_frame, textvariable=self.date_filter_var, width=12,
                             font=('Segoe UI', 10))
        date_entry.pack(side='left', padx=(0, 5))
        date_entry.bind('<KeyRelease>', self.filter_prs)
        
        tk.Label(filter_frame, text="(DD/MM/YYYY)", font=('Segoe UI', 8),
                bg='#ecf0f1', fg='#7f8c8d').pack(side='left', padx=(0, 10))
        
        tk.Button(filter_frame, text="Clear", bg='#95a5a6', fg='white',
                 font=('Segoe UI', 8, 'bold'), command=self.clear_date_filter).pack(side='left', padx=(0, 10))
        
        tk.Button(filter_frame, text="🔄 Refresh", bg='#3498db', fg='white',
                 font=('Segoe UI', 9, 'bold'), command=self.refresh_data).pack(side='right', padx=5)
        tk.Button(filter_frame, text="🔄 Rejected", bg="#db3434", fg='white',
                 font=('Segoe UI', 9, 'bold'), command=self.rejected_prs_handler.show_rejected_prs).pack(side='left', padx=5)
        
        # PR List with scrollbar
        list_container = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        list_container.pack(fill='both', expand=True)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(list_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # Configure scroll region
        self.scrollable_frame.bind('<Configure>', 
                                  lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
    
    def load_pending_prs(self):
        """Load pending PRs from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.pending_prs = json.load(f)
            else:
                # Create sample data if file doesn't exist
                self.create_sample_data()
        except Exception as e:
            print(f"Error loading pending PRs: {e}")
            self.create_sample_data()
        
        # Display PRs immediately
        self.display_prs()
        
        # Defer highlighting to prevent blocking UI
        self.parent_frame.after_idle(self.highlight_all_pending_items)
    
    def save_pending_prs(self):
        """Save pending PRs to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.pending_prs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving pending PRs: {e}")
    
    def create_sample_data(self):
        """Create sample pending PRs"""
        self.pending_prs = [
            {
                "pr_number": "PR-001",
                "request_date": "15/12/2024",
                "required_date": "20/12/2024",
                "status": "Pending Approval",
                "priority": "High",
                "items_count": 5,
                "total_value": "₹25,000",
                "description": "Electrical cables and switches for office renovation"
            },
            {
                "pr_number": "PR-002", 
                "request_date": "14/12/2024",
                "required_date": "18/12/2024",
                "status": "Pending Approval",
                "priority": "Medium",
                "items_count": 3,
                "total_value": "₹15,500",
                "description": "LED lights and fixtures for conference room"
            },
            {
                "pr_number": "PR-003",
                "request_date": "13/12/2024", 
                "required_date": "25/12/2024",
                "status": "Pending Approval",
                "priority": "Low",
                "items_count": 8,
                "total_value": "₹42,300",
                "description": "Circuit breakers and electrical panels"
            }
        ]
        self.save_pending_prs()
    
    def display_prs(self):
        """Display pending PRs in the scrollable frame"""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.pending_prs:
            tk.Label(self.scrollable_frame, text="No pending purchase requests found",
                    font=('Segoe UI', 12), bg='white', fg='#7f8c8d').pack(pady=50)
            return
        
        # Filter PRs based on search and date
        search_text = self.search_var.get().lower()
        date_filter = self.date_filter_var.get().strip()
        
        filtered_prs = []
        for pr in self.pending_prs:
            # Search filter
            search_match = (search_text in pr.get('pr_number', '').lower() or
                           search_text in pr.get('description', '').lower())
            
            # Date filter
            date_match = True
            if date_filter:
                pr_date = pr.get('request_date', '')
                date_match = date_filter in pr_date
            
            if search_match and date_match:
                filtered_prs.append(pr)
        
        # Create container for horizontal layout
        self.cards_container = tk.Frame(self.scrollable_frame, bg='white')
        self.cards_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.current_row = None
        self.cards_in_row = 0
        
        # Create cards in batches to prevent UI blocking
        self.create_cards_batch(filtered_prs, 0)
    
    def create_pr_card(self, pr, index):
        """Create a card for each pending PR"""
        # Create new row if needed (3 cards per row)
        if self.cards_in_row == 0 or self.cards_in_row >= 3:
            self.current_row = tk.Frame(self.cards_container, bg='white')
            self.current_row.pack(fill='x', pady=5)
            self.cards_in_row = 0
        
        # Main card frame with fixed width
        card_frame = tk.Frame(self.current_row, bg='white', relief='solid', bd=1, width=450, height=200)
        card_frame.pack(side='left', padx=5, pady=0)
        card_frame.pack_propagate(False)
        
        self.cards_in_row += 1
        
        # Card header with PR number and status
        header_frame = tk.Frame(card_frame, bg='#34495e', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"📋 {pr.get('pr_number', 'N/A')}", 
                font=('Segoe UI', 12, 'bold'), bg='#34495e', fg='white').pack(side='left', padx=10, pady=8)
        
        # Status badge - only show if Pending Approval
        status = pr.get('status', '')
        if status == 'Pending Approval':
            status_color = self.get_status_color(status)
            tk.Label(header_frame, text=status, 
                    font=('Segoe UI', 9, 'bold'), bg=status_color, fg='white',
                    padx=8, pady=2).pack(side='right', padx=10, pady=8)
        
        # Card body with details
        body_frame = tk.Frame(card_frame, bg='white')
        body_frame.pack(fill='x', padx=15, pady=10)
        
        # Row 1: Dates
        row1 = tk.Frame(body_frame, bg='white')
        row1.pack(fill='x', pady=(0, 5))
        
        tk.Label(row1, text=f"📅 Request: {pr.get('request_date', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left')
        
        tk.Label(row1, text=f"⏰ Required: {pr.get('required_date', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left', padx=(20, 0))
        
        # Row 2: Items
        row2 = tk.Frame(body_frame, bg='white')
        row2.pack(fill='x', pady=(0, 5))
        
        tk.Label(row2, text=f"📦 Items: {pr.get('items_count', 0)}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left')
        
        # Row 3: Additional Info (if available)
        if pr.get('lpo_number') or pr.get('supplier_name'):
            row3 = tk.Frame(body_frame, bg='white')
            row3.pack(fill='x', pady=(0, 5))
            
            if pr.get('lpo_number'):
                tk.Label(row3, text=f"📄 LPO: {pr.get('lpo_number')}", 
                        font=('Segoe UI', 8), bg='white', fg='#2c3e50').pack(side='left')
            
            if pr.get('supplier_name'):
                tk.Label(row3, text=f"🏢 {pr.get('supplier_name')}", 
                        font=('Segoe UI', 13), bg='white', fg='#2c3e50').pack(side='right')
        
        # Description
        desc_text = pr.get('description', 'No description available')
        if len(desc_text) > 60:
            desc_text = desc_text[:60] + "..."
        
        tk.Label(body_frame, text=f"📝 {desc_text}", 
                font=('Segoe UI', 8), bg='white', fg='#7f8c8d', 
                wraplength=400, justify='left').pack(anchor='w', pady=(0, 5))
        
        # Action buttons
        action_frame = tk.Frame(body_frame, bg='white')
        action_frame.pack(fill='x', pady=(5, 0))
        
        tk.Button(action_frame, text="👁️ View", bg='#3498db', fg='white',
                 font=('Segoe UI', 8, 'bold'), padx=10, pady=2,
                 command=lambda: self.view_pr(pr)).pack(side='left', padx=(0, 5))
        
        tk.Button(action_frame, text="✅ Approve", bg='#27ae60', fg='white',
                 font=('Segoe UI', 8, 'bold'), padx=10, pady=2,
                 command=lambda: self.approve_pr(pr)).pack(side='left', padx=(0, 5))
        
        tk.Button(action_frame, text="❌ Reject", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 8, 'bold'), padx=10, pady=2,
                 command=lambda: self.reject_pr(pr)).pack(side='right', padx=(5, 0))
        
        tk.Button(action_frame, text="🗑️ Delete", bg='#95a5a6', fg='white',
                 font=('Segoe UI', 8, 'bold'), padx=10, pady=2,
                 command=lambda: self.delete_pr(pr)).pack(side='right')
    
    def get_status_color(self, status):
        """Get color based on status"""
        colors = {
            'Pending Approval': '#f39c12',
           
        }
        return colors.get(status, '#95a5a6')
    
    def clear_date_filter(self):
        """Clear date filter"""
        self.date_filter_var.set("")
        self.display_prs()
    
    def filter_prs(self, event=None):
        """Filter PRs based on search text"""
        self.display_prs()
    
    def refresh_data(self):
        """Refresh PR data"""
        self.load_pending_prs()
        # Trigger immediate highlight after refresh
        self.highlight_all_pending_items()
    
    def view_pr(self, pr):
        """View PR details with selected items"""
        # Store items for highlighting after window is created
        pr_items = pr.get('items', [])
        print(f"DEBUG: PR has {len(pr_items)} items to highlight")
        for item in pr_items:
            print(f"DEBUG: PR Item - {item.get('resource_code')} : {item.get('item_description')}")
        
        # Create popup window
        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"PR Details - {pr.get('pr_number', 'N/A')}")
        view_window.geometry("800x600")
        view_window.configure(bg='#ecf0f1')
        
        # Clear highlights when window is closed
        def on_close():
            self.clear_inventory_highlights()
            view_window.destroy()
        view_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Header
        header_frame = tk.Frame(view_window, bg='#3498db', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"📋 {pr.get('pr_number', 'N/A')} - Purchase Request Details",
                font=('Segoe UI', 16, 'bold'), bg='#3498db', fg='white').pack(pady=15)
        
        # Main content with scrollbar
        main_frame = tk.Frame(view_window, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # PR Info section
        info_frame = tk.LabelFrame(main_frame, text="PR Information", font=('Segoe UI', 12, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50')
        info_frame.pack(fill='x', pady=(0, 10))
        
        info_grid = tk.Frame(info_frame, bg='white')
        info_grid.pack(fill='x', padx=10, pady=10)
        
        # Info details
        info_data = [
            ("PR Number:", pr.get('pr_number', 'N/A')),
            ("Request Date:", pr.get('request_date', 'N/A')),
            ("Required Date:", pr.get('required_date', 'N/A')),
            ("Status:", pr.get('status', 'N/A')),
            ("Total Value:", pr.get('total_value', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(info_data):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(info_grid, text=label, font=('Segoe UI', 10, 'bold'),
                    bg='white', fg='#2c3e50').grid(row=row, column=col, sticky='w', padx=(0, 10), pady=5)
            tk.Label(info_grid, text=value, font=('Segoe UI', 10),
                    bg='white', fg='#34495e').grid(row=row, column=col+1, sticky='w', padx=(0, 30), pady=5)
        
        # Additional fields section
        additional_frame = tk.LabelFrame(main_frame, text="Additional Information", font=('Segoe UI', 12, 'bold'),
                                        bg='#ecf0f1', fg='#2c3e50')
        additional_frame.pack(fill='x', pady=(0, 10))
        
        additional_grid = tk.Frame(additional_frame, bg='white')
        additional_grid.pack(fill='x', padx=10, pady=10)
        
        # LPO Number
        tk.Label(additional_grid, text="LPO Number:", font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.lpo_entry = tk.Entry(additional_grid, font=('Segoe UI', 10), width=20)
        self.lpo_entry.grid(row=0, column=1, sticky='w', padx=(0, 30), pady=5)
        self.lpo_entry.insert(0, pr.get('lpo_number', ''))
        
        # Supplier Name
        tk.Label(additional_grid, text="Supplier Name:", font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=0, column=2, sticky='w', padx=(0, 10), pady=5)
        self.supplier_entry = tk.Entry(additional_grid, font=('Segoe UI', 10), width=20)
        self.supplier_entry.grid(row=0, column=3, sticky='w', padx=(0, 30), pady=5)
        self.supplier_entry.insert(0, pr.get('supplier_name', ''))
        
        # Phone Number
        tk.Label(additional_grid, text="Phone Number:", font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        self.phone_entry = tk.Entry(additional_grid, font=('Segoe UI', 10), width=20)
        self.phone_entry.grid(row=1, column=1, sticky='w', padx=(0, 30), pady=5)
        self.phone_entry.insert(0, pr.get('phone_number', '+971'))
        
        # Description
        desc_frame = tk.LabelFrame(main_frame, text="Description", font=('Segoe UI', 12, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50')
        desc_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(desc_frame, text=pr.get('description', 'No description available'),
                font=('Segoe UI', 10), bg='white', fg='#34495e', wraplength=750,
                justify='left').pack(padx=10, pady=10, anchor='w')
        
        # Selected Items section
        items_frame = tk.LabelFrame(main_frame, text="Selected Items", font=('Segoe UI', 12, 'bold'),
                                   bg='#ecf0f1', fg='#2c3e50')
        items_frame.pack(fill='both', expand=True)
        
        # Items table with scrollbar
        table_container = tk.Frame(items_frame, bg='white')
        table_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Canvas for scrolling
        canvas = tk.Canvas(table_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(table_container, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        
        # Configure scroll region
        scrollable_frame.bind('<Configure>', 
                             lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Display items
        items = pr.get('items', [])
        if items:
            # Headers
            headers = ['S.No', 'Resource Code', 'Item Description', 'Unit', 'Quantity']
            header_frame = tk.Frame(scrollable_frame, bg='#3498db')
            header_frame.pack(fill='x')
            
            for col, header in enumerate(headers):
                tk.Label(header_frame, text=header, font=('Segoe UI', 10, 'bold'),
                        bg='#3498db', fg='white', relief='solid', bd=1).grid(
                        row=0, column=col, sticky='nsew', padx=0, pady=0)
            
            # Configure column weights
            header_frame.grid_columnconfigure(0, weight=0, minsize=50)
            header_frame.grid_columnconfigure(1, weight=1, minsize=120)
            header_frame.grid_columnconfigure(2, weight=3, minsize=300)
            header_frame.grid_columnconfigure(3, weight=0, minsize=80)
            header_frame.grid_columnconfigure(4, weight=0, minsize=80)
            
            # Items rows
            for i, item in enumerate(items, 1):
                row_frame = tk.Frame(scrollable_frame, bg='white')
                row_frame.pack(fill='x')
                
                # S.No
                tk.Label(row_frame, text=str(i), font=('Segoe UI', 9),
                        bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                        row=0, column=0, sticky='nsew', padx=0, pady=0)
                
                # Resource Code
                tk.Label(row_frame, text=item.get('resource_code', 'N/A'), font=('Segoe UI', 9),
                        bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                        row=0, column=1, sticky='nsew', padx=0, pady=0)
                
                # Description
                tk.Label(row_frame, text=item.get('item_description', 'N/A'), font=('Segoe UI', 9),
                        bg='white', fg='#2c3e50', relief='solid', bd=1, wraplength=300).grid(
                        row=0, column=2, sticky='nsew', padx=0, pady=0)
                
                # Unit
                tk.Label(row_frame, text=item.get('unit', 'N/A'), font=('Segoe UI', 9),
                        bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                        row=0, column=3, sticky='nsew', padx=0, pady=0)
                
                # Quantity (default to 1 if not specified)
                quantity = item.get('quantity', '1')
                tk.Label(row_frame, text=quantity, font=('Segoe UI', 9),
                        bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                        row=0, column=4, sticky='nsew', padx=0, pady=0)
                
                # Configure column weights for each row
                row_frame.grid_columnconfigure(0, weight=0, minsize=50)
                row_frame.grid_columnconfigure(1, weight=1, minsize=120)
                row_frame.grid_columnconfigure(2, weight=3, minsize=300)
                row_frame.grid_columnconfigure(3, weight=0, minsize=80)
                row_frame.grid_columnconfigure(4, weight=0, minsize=80)
        else:
            tk.Label(scrollable_frame, text="No items found for this PR",
                    font=('Segoe UI', 12), bg='white', fg='#7f8c8d').pack(pady=50)
        
        # Buttons
        button_frame = tk.Frame(view_window, bg='#ecf0f1')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="💾 Save", bg='#27ae60', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=5,
                 command=lambda: self.save_additional_info(pr, view_window)).pack(side='left')
        
        tk.Button(button_frame, text="✖️ Close", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=5,
                 command=on_close).pack(side='right')
        
        # Store PR items globally for highlighting when inventory is accessed
        self.store_pr_items_for_highlighting(pr_items)
        
        # Try immediate highlighting
        view_window.after(100, lambda: self.highlight_inventory_items(pr_items))
    
    def edit_pr(self, pr):
        """Edit PR"""
        print(f"Editing PR: {pr.get('pr_number')}")
        # TODO: Implement PR editing
    
    def approve_pr(self, pr):
        """Approve PR and move to LPO system"""
        # Check if required fields are filled
        if not pr.get('lpo_number', '').strip():
            messagebox.showerror("Validation Error", "LPO Number is required before approval.\n\nPlease view the PR details and fill in the LPO Number.")
            return
        
        if not pr.get('supplier_name', '').strip():
            messagebox.showerror("Validation Error", "Supplier Name is required before approval.\n\nPlease view the PR details and fill in the Supplier Name.")
            return
        
        if not pr.get('phone_number', '').strip() or pr.get('phone_number', '').strip() == '+971':
            messagebox.showerror("Validation Error", "Phone Number is required before approval.\n\nPlease view the PR details and fill in the Phone Number.")
            return
        
        try:
            # Import LPO system
            from lpo_s import LPOSystem
            
            # Create a temporary LPO instance to add the approved PR
            temp_frame = tk.Frame()
            lpo_system = LPOSystem(temp_frame, self.department_name)
            
            # Add approved PR to LPO system
            if lpo_system.add_approved_pr(pr.copy()):
                # Remove from pending PRs
                self.pending_prs = [p for p in self.pending_prs if p.get('pr_number') != pr.get('pr_number')]
                self.save_pending_prs()
                self.display_prs()
                
                # Show success message
                messagebox.showinfo("Success", 
                                   f"PR {pr.get('pr_number')} has been approved and moved to LPO system!\n\n"
                                   f"Status: Invoice Prepared - Awaiting Delivery")
            
            # Clean up temporary frame
            temp_frame.destroy()
            
        except Exception as e:
            print(f"Error approving PR: {e}")
            messagebox.showerror("Error", f"Failed to approve PR: {str(e)}")
    
    def reject_pr(self, pr):
        """Reject PR with reason"""
        # Create reason dialog
        reason_window = tk.Toplevel(self.parent_frame)
        reason_window.title("Reject PR - Reason Required")
        reason_window.geometry("400x300")
        reason_window.configure(bg='#ecf0f1')
        reason_window.transient(self.parent_frame.winfo_toplevel())
        reason_window.grab_set()
        
        # Header
        header_frame = tk.Frame(reason_window, bg='#e74c3c', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"Reject PR: {pr.get('pr_number', 'N/A')}", 
                font=('Segoe UI', 14, 'bold'), bg='#e74c3c', fg='white').pack(pady=12)
        
        # Content
        content_frame = tk.Frame(reason_window, bg='#ecf0f1')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="Please provide a reason for rejection:", 
                font=('Segoe UI', 12, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(anchor='w', pady=(0, 10))
        
        # Reason text area
        reason_text = tk.Text(content_frame, height=8, font=('Segoe UI', 10),
                             wrap='word', relief='solid', bd=1)
        reason_text.pack(fill='both', expand=True, pady=(0, 15))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#ecf0f1')
        button_frame.pack(fill='x')
        
        def confirm_reject():
            reason = reason_text.get('1.0', 'end-1c').strip()
            if not reason:
                messagebox.showwarning("Warning", "Please provide a reason for rejection.")
                return
            
            # Save to rejected PRs
            self.rejected_prs_handler.save_rejected_pr(pr, reason)
            
            # Remove from pending PRs
            self.pending_prs = [p for p in self.pending_prs if p.get('pr_number') != pr.get('pr_number')]
            self.save_pending_prs()
            self.display_prs()
            
            reason_window.destroy()
            messagebox.showinfo("Success", f"PR {pr.get('pr_number')} has been rejected.")
        
        tk.Button(button_frame, text="❌ Reject", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=5,
                 command=confirm_reject).pack(side='right', padx=(5, 0))
        
        tk.Button(button_frame, text="Cancel", bg='#95a5a6', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=5,
                 command=reason_window.destroy).pack(side='right')
    

    
    def save_additional_info(self, pr, window):
        """Save additional information (LPO, supplier, phone)"""
        # Validate required fields
        lpo_number = self.lpo_entry.get().strip()
        supplier_name = self.supplier_entry.get().strip()
        phone_number = self.phone_entry.get().strip()
        
        if not lpo_number:
            tk.messagebox.showerror("Validation Error", "LPO Number is required.")
            return
        
        if not supplier_name:
            tk.messagebox.showerror("Validation Error", "Supplier Name is required.")
            return
        
        if not phone_number or phone_number == '+971':
            tk.messagebox.showerror("Validation Error", "Phone Number is required.")
            return
        
        # Update PR with additional info
        pr['lpo_number'] = lpo_number
        pr['supplier_name'] = supplier_name
        pr['phone_number'] = phone_number
        
        # Save to file
        self.save_pending_prs()
        
        # Refresh display to show updated cards
        self.display_prs()
        
        # Show confirmation
        tk.messagebox.showinfo("Success", "Additional information saved successfully!")
        window.destroy()
    
    def add_new_pr(self, pr_data):
        """Add new PR from PR_rise"""
        # Generate PR number
        pr_number = f"PR-{len(self.pending_prs) + 1:03d}"
        
        # Create new PR entry
        new_pr = {
            "pr_number": pr_number,
            "request_date": pr_data.get('request_date', ''),
            "required_date": pr_data.get('required_date', ''),
            "status": "Pending Approval",
            "priority": "Medium",
            "items_count": len(pr_data.get('items', [])),
            "total_value": pr_data.get('total_value', '₹0'),
            "description": pr_data.get('description', ''),
            "items": pr_data.get('items', [])
        }
        
        # Add to pending PRs
        self.pending_prs.append(new_pr)
        self.save_pending_prs()
        self.display_prs()
        
        return pr_number
    
    def delete_pr(self, pr):
        """Delete PR permanently"""
        import tkinter.messagebox as messagebox
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to permanently delete PR {pr.get('pr_number', 'N/A')}?\n\nThis action cannot be undone."
        )
        
        if result:
            # Remove from pending PRs list
            self.pending_prs = [p for p in self.pending_prs if p.get('pr_number') != pr.get('pr_number')]
            
            # Save updated list
            self.save_pending_prs()
            
            # Refresh display
            self.display_prs()
            
            # Show success message
            messagebox.showinfo("Success", f"PR {pr.get('pr_number')} has been deleted permanently.")
    
    def restore_pr_from_rejected(self, pr):
        """Restore a PR from rejected back to pending"""
        # Add the PR back to pending list
        self.pending_prs.append(pr)
        
        # Save updated pending PRs
        self.save_pending_prs()
        
        # Refresh display
        self.display_prs()
    
    def store_pr_items_for_highlighting(self, pr_items):
        """Store PR items globally for highlighting when inventory is accessed"""
        try:
            # Store in a global variable that can be accessed by inventory widgets
            import __main__
            __main__.pending_pr_items_to_highlight = pr_items
            print(f"DEBUG: Stored {len(pr_items)} PR items globally for highlighting")
        except Exception as e:
            print(f"Error storing PR items: {e}")
    
    def highlight_inventory_items(self, pr_items):
        """Highlight matching items in inventory overview with orange color for pending approval"""
        try:
            print(f"\n=== ORANGE HIGHLIGHTING DEBUG ===")
            print(f"DEBUG: Highlighting {len(pr_items)} items")
            for item in pr_items:
                print(f"DEBUG: PR Item - Resource: '{item.get('resource_code')}', Description: '{item.get('item_description')}'")
            
            # Find inventory overview widget in the application
            inventory_widget = self.find_inventory_widget()
            print(f"DEBUG: Found inventory widget: {inventory_widget is not None}")
            if inventory_widget:
                print(f"DEBUG: Calling highlight_pending_items on widget: {type(inventory_widget)}")
                inventory_widget.highlight_pending_items(pr_items)
                print(f"DEBUG: highlight_pending_items called successfully")
            else:
                print("DEBUG: No inventory widget found - checking registry...")
                from inventory_overview import get_all_inventory_instances
                all_instances = get_all_inventory_instances()
                print(f"DEBUG: All available inventory instances: {list(all_instances.keys())}")
        except Exception as e:
            print(f"ERROR highlighting inventory items: {e}")
            import traceback
            traceback.print_exc()
    
    def clear_inventory_highlights(self):
        """Clear highlights from inventory overview"""
        try:
            inventory_widget = self.find_inventory_widget()
            if inventory_widget:
                inventory_widget.clear_pending_highlights()
        except Exception as e:
            print(f"Error clearing inventory highlights: {e}")
    
    def create_cards_batch(self, filtered_prs, start_index, batch_size=5):
        """Create PR cards in batches to prevent UI blocking"""
        end_index = min(start_index + batch_size, len(filtered_prs))
        
        for i in range(start_index, end_index):
            self.create_pr_card(filtered_prs[i], i)
        
        # If more cards to create, schedule next batch
        if end_index < len(filtered_prs):
            self.parent_frame.after(10, lambda: self.create_cards_batch(filtered_prs, end_index, batch_size))
    
    def start_auto_highlight(self):
        """Start automatic highlighting cycle"""
        self.highlight_all_pending_items()
        # Schedule next highlight in 15 seconds (reduced frequency)
        self.parent_frame.after(15000, self.start_auto_highlight)
    
    def highlight_all_pending_items(self):
        """Automatically highlight all items from pending PRs in inventory"""
        try:
            all_pending_items = []
            for pr in self.pending_prs:
                if pr.get('status') == 'Pending Approval':
                    pr_items = pr.get('items', [])
                    all_pending_items.extend(pr_items)
            
            if all_pending_items:
                print(f"AUTO-HIGHLIGHT: Found {len(all_pending_items)} pending items to highlight")
                self.highlight_inventory_items(all_pending_items)
        except Exception as e:
            print(f"Error in auto-highlight: {e}")
    
    def find_inventory_widget(self):
        """Find the inventory overview widget in the application"""
        try:
            # Import the function to get inventory instance
            from inventory_overview import get_inventory_instance, get_all_inventory_instances
            
            all_instances = get_all_inventory_instances()
            
            # Find the most recently created inventory instance for this department
            best_match = None
            for key, instance in all_instances.items():
                # Check if it's for the same department
                if self.department_name.lower().replace(' ', '_') in key.lower():
                    # Test if the widget is still valid by trying to access a property
                    try:
                        # Try to access the cells to see if widget is still alive
                        if hasattr(instance, 'cells') and len(instance.cells) > 0:
                            # Try to access the first cell to test if it's valid
                            test_cell = instance.cells[0][1]
                            test_cell.winfo_exists()  # This will raise an error if widget is destroyed
                            best_match = instance
                            break
                    except Exception as e:
                        continue
            
            return best_match
            
        except Exception as e:
            print(f"Error finding inventory widget: {e}")
            return None
    
