import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

class PendingMaterials:
    def __init__(self, parent_frame, department_name):
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.lpo_items = []
        self.data_file = f"lpo_{department_name.lower().replace(' ', '_')}.json"
        self.auto_refresh_enabled = False
        self.refresh_job = None
        self.receive_auto_refresh_enabled = False
        self.receive_refresh_job = None
        self.create_interface()
        self.load_lpo_data()
    
    def create_interface(self):
        # Header
        header_frame = tk.Frame(self.parent_frame, bg='#e67e22', height=60)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📦 Pending Materials to Receive", 
                font=('Segoe UI', 16, 'bold'), bg='#e67e22', fg='white').pack(pady=15)
        
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
        search_entry.bind('<KeyRelease>', self.filter_lpos)
        
        tk.Button(filter_frame, text="🔄 Refresh", bg='#3498db', fg='white',
                 font=('Segoe UI', 9, 'bold'), command=self.refresh_data).pack(side='right', padx=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=False)
        auto_refresh_check = tk.Checkbutton(filter_frame, text="Auto Refresh (30s)", variable=self.auto_refresh_var,
                                           font=('Segoe UI', 9, 'bold'), bg='#ecf0f1', fg='#2c3e50',
                                           command=self.toggle_auto_refresh)
        auto_refresh_check.pack(side='right', padx=5)
        
        # LPO List with scrollbar
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
    
    def load_lpo_data(self):
        """Load LPO data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.lpo_items = json.load(f)
            else:
                self.lpo_items = []
        except Exception as e:
            print(f"Error loading LPO data: {e}")
            self.lpo_items = []
        
        self.display_lpos()
    
    def save_lpo_data(self):
        """Save LPO data to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.lpo_items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving LPO data: {e}")
    
    def display_lpos(self):
        """Display pending LPO items in card format"""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Filter only pending LPOs (not fully received)
        pending_lpos = []
        for lpo in self.lpo_items:
            delivery_status = self.get_delivery_status(lpo)
            if delivery_status != 'Completed':
                pending_lpos.append(lpo)
        
        if not pending_lpos:
            tk.Label(self.scrollable_frame, text="No pending materials to receive",
                    font=('Segoe UI', 12), bg='white', fg='#7f8c8d').pack(pady=50)
            return
        
        # Filter LPOs based on search
        search_text = self.search_var.get().lower()
        filtered_lpos = [lpo for lpo in pending_lpos 
                        if search_text in lpo.get('lpo_number', '').lower() or
                           search_text in lpo.get('supplier_name', '').lower()]
        
        # Create container for horizontal layout
        self.cards_container = tk.Frame(self.scrollable_frame, bg='white')
        self.cards_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.current_row = None
        self.cards_in_row = 0
        
        for i, lpo in enumerate(filtered_lpos):
            self.create_lpo_card(lpo, i)
    
    def create_lpo_card(self, lpo, index):
        """Create a card for each pending LPO item"""
        # Create new row if needed (3 cards per row)
        if self.cards_in_row == 0 or self.cards_in_row >= 3:
            self.current_row = tk.Frame(self.cards_container, bg='white')
            self.current_row.pack(fill='x', pady=5)
            self.cards_in_row = 0
        
        # Main card frame with fixed width
        card_frame = tk.Frame(self.current_row, bg='white', relief='solid', bd=1, width=450, height=220)
        card_frame.pack(side='left', padx=5, pady=0)
        card_frame.pack_propagate(False)
        
        self.cards_in_row += 1
        
        # Card header with LPO number and status
        header_frame = tk.Frame(card_frame, bg='#e67e22', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Show manually entered LPO details if available, otherwise show generated LPO number
        display_lpo = lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')
        tk.Label(header_frame, text=f"📦 {display_lpo}", 
                font=('Segoe UI', 12, 'bold'), bg='#e67e22', fg='white').pack(side='left', padx=10, pady=8)
        
        # Delivery Status badge
        delivery_status = self.get_delivery_status(lpo)
        status_color = '#f39c12' if delivery_status == 'Pending' else '#27ae60'
        tk.Label(header_frame, text=delivery_status, 
                font=('Segoe UI', 9, 'bold'), bg=status_color, fg='white',
                padx=8, pady=2).pack(side='right', padx=10, pady=8)
        
        # Card body with details
        body_frame = tk.Frame(card_frame, bg='white')
        body_frame.pack(fill='x', padx=15, pady=10)
        
        # Row 1: Dates
        row1 = tk.Frame(body_frame, bg='white')
        row1.pack(fill='x', pady=(0, 5))
        
        tk.Label(row1, text=f"📅 LPO Date: {lpo.get('approval_date', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left')
        
        tk.Label(row1, text=f"⏰ Required: {lpo.get('required_date', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left', padx=(20, 0))
        
        # Row 2: Items and Value
        row2 = tk.Frame(body_frame, bg='white')
        row2.pack(fill='x', pady=(0, 5))
        
        items_count = len(lpo.get('items', []))
        tk.Label(row2, text=f"📦 Items: {items_count}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left')
        
        tk.Label(row2, text=f"💰 Value: {lpo.get('total_value', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left', padx=(20, 0))
        
        # Row 3: Supplier Info
        if lpo.get('supplier_name'):
            row3 = tk.Frame(body_frame, bg='white')
            row3.pack(fill='x', pady=(0, 5))
            
            tk.Label(row3, text=f"🏢 Supplier: {lpo.get('supplier_name')}", 
                    font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left')
        
        # Description
        desc_text = lpo.get('description', 'No description available')
        if len(desc_text) > 60:
            desc_text = desc_text[:60] + "..."
        
        tk.Label(body_frame, text=f"📝 {desc_text}", 
                font=('Segoe UI', 8), bg='white', fg='#7f8c8d', 
                wraplength=400, justify='left').pack(anchor='w', pady=(0, 5))
        
        # Action buttons
        action_frame = tk.Frame(body_frame, bg='white')
        action_frame.pack(fill='x', pady=(5, 0))
        
        tk.Button(action_frame, text="📥 Receive", bg='#27ae60', fg='white',
                 font=('Segoe UI', 8, 'bold'), padx=10, pady=2,
                 command=lambda: self.receive_materials(lpo)).pack(side='left', padx=(0, 5))
        
        tk.Button(action_frame, text="👁️ View", bg='#3498db', fg='white',
                 font=('Segoe UI', 8, 'bold'), padx=10, pady=2,
                 command=lambda: self.view_lpo(lpo)).pack(side='left', padx=(0, 5))
    
    def get_delivery_status(self, lpo):
        """Get delivery status of LPO"""
        deliveries = lpo.get('deliveries', [])
        if not deliveries:
            return 'Pending'
        
        # Check if all items are fully received
        items = lpo.get('items', [])
        for item in items:
            ordered_qty = float(item.get('quantity', 0))
            received_qty = sum([float(d.get('items', {}).get(item.get('resource_code', ''), 0)) 
                               for d in deliveries])
            if received_qty < ordered_qty:
                return 'Partial'
        
        return 'Completed'
    
    def receive_materials(self, lpo):
        """Open material receiving dialog"""
        # Check if LPO is priced
        archive_file = f"archived_lpos_{self.department_name.lower().replace(' ', '_')}.json"
        is_priced = False
        
        if os.path.exists(archive_file):
            try:
                with open(archive_file, 'r', encoding='utf-8') as f:
                    archived_lpos = json.load(f)
                lpo_id = lpo.get('lpo_number')
                is_priced = any(archived_lpo.get('lpo_number') == lpo_id for archived_lpo in archived_lpos)
            except:
                pass
        
        # If not priced, ask for permission
        if not is_priced:
            result = messagebox.askyesno(
                "Pricing Required",
                f"LPO {lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')} has not been priced yet.\n\n"
                "Do you want to receive materials without pricing?",
                icon='warning'
            )
            if not result:
                return
        
        # Create popup window
        receive_window = tk.Toplevel(self.parent_frame)
        receive_window.title(f"Receive Materials - {lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')}")
        receive_window.geometry("900x700")
        receive_window.configure(bg='#ecf0f1')
        
        # Header
        header_frame = tk.Frame(receive_window, bg='#e67e22', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        display_lpo = lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')
        tk.Label(header_frame, text=f"📥 Receive Materials - {display_lpo}",
                font=('Segoe UI', 16, 'bold'), bg='#e67e22', fg='white').pack(pady=15)
        
        # Main content
        main_frame = tk.Frame(receive_window, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top section - Items to receive
        items_frame = tk.LabelFrame(main_frame, text="Items to Receive", font=('Segoe UI', 12, 'bold'),
                                   bg='#ecf0f1', fg='#2c3e50')
        items_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Date and Save button frame
        control_frame = tk.Frame(items_frame, bg='#ecf0f1')
        control_frame.pack(fill='x', padx=10, pady=(5, 0))
        
        # Date picker
        tk.Label(control_frame, text="Delivery Date:", font=('Segoe UI', 10, 'bold'),
                bg='#ecf0f1', fg='#2c3e50').pack(side='left')
        
        self.delivery_date = DateEntry(control_frame, width=12, background='darkblue',
                                      foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.delivery_date.pack(side='left', padx=(5, 20))
        
        # Auto refresh checkbox
        self.receive_auto_refresh_var = tk.BooleanVar(value=False)
        auto_refresh_check = tk.Checkbutton(control_frame, text="Auto Refresh (30s)", variable=self.receive_auto_refresh_var,
                                           font=('Segoe UI', 9, 'bold'), bg='#ecf0f1', fg='#2c3e50',
                                           command=lambda: self.toggle_receive_auto_refresh(lpo, receive_window))
        auto_refresh_check.pack(side='left', padx=10)
        
        # Save button in top right corner
        save_btn = tk.Button(control_frame, text="💾 Save Delivery", bg='#27ae60', fg='white',
                           font=('Segoe UI', 10, 'bold'), padx=15, pady=5,
                           command=lambda: self.record_delivery(lpo, receive_window))
        save_btn.pack(side='right')
        
        # Items table
        items_container = tk.Frame(items_frame, bg='white')
        items_container.pack(fill='both', expand=True, padx=10, pady=(10, 10))
        
        # Canvas for scrolling items
        items_canvas = tk.Canvas(items_container, bg='white', highlightthickness=0)
        items_scrollbar = tk.Scrollbar(items_container, orient='vertical', command=items_canvas.yview)
        items_scrollable = tk.Frame(items_canvas, bg='white')
        
        items_canvas.configure(yscrollcommand=items_scrollbar.set)
        items_scrollbar.pack(side='right', fill='y')
        items_canvas.pack(side='left', fill='both', expand=True)
        items_canvas.create_window((0, 0), window=items_scrollable, anchor='nw')
        
        items_scrollable.bind('<Configure>', 
                             lambda e: items_canvas.configure(scrollregion=items_canvas.bbox('all')))
        
        # Display items with receive quantity inputs
        self.receive_entries = {}
        items = lpo.get('items', [])
        deliveries = lpo.get('deliveries', [])
        
        # Create table with proper grid layout
        table_frame = tk.Frame(items_scrollable, bg='white')
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Store reference for refreshing
        self.items_table_frame = table_frame
        
        # Headers with grid
        headers = ["Resource Code", "Item Description", "Unit", "Ordered", "Received", "Pending", "Receive Now", "Unit Rate", "Total Price"]
        col_widths = [12, 25, 6, 8, 8, 8, 10, 10, 12]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            header_label = tk.Label(table_frame, text=header, font=('Segoe UI', 10, 'bold'),
                                   bg='#34495e', fg='white', relief='solid', bd=1)
            header_label.grid(row=0, column=col, sticky='nsew', padx=0, pady=0)
            table_frame.grid_columnconfigure(col, weight=1 if col == 1 else 0, minsize=width*8)
        
        # Calculate totals
        total_amount = 0
        balance_amount = 0
        
        # Data rows with grid
        for i, item in enumerate(items, 1):
            row_bg = 'white' if i % 2 == 1 else '#f8f9fa'
            
            # Resource Code
            resource_code = item.get('resource_code', '')
            code_label = tk.Label(table_frame, text=resource_code, 
                                 font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', 
                                 relief='solid', bd=1, anchor='center')
            code_label.grid(row=i, column=0, sticky='nsew', padx=0, pady=0)
            
            # Item description
            item_label = tk.Label(table_frame, text=item.get('item_description', 'N/A'), 
                                 font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', 
                                 relief='solid', bd=1, anchor='w', wraplength=220)
            item_label.grid(row=i, column=1, sticky='nsew', padx=0, pady=0)
            
            # Unit
            unit_label = tk.Label(table_frame, text=item.get('unit', 'Nos'), 
                                 font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', 
                                 relief='solid', bd=1, anchor='center')
            unit_label.grid(row=i, column=2, sticky='nsew', padx=0, pady=0)
            
            # Ordered quantity
            ordered_qty = float(item.get('quantity', 0))
            ordered_label = tk.Label(table_frame, text=f"{ordered_qty:.0f}", 
                                   font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', relief='solid', bd=1)
            ordered_label.grid(row=i, column=3, sticky='nsew', padx=0, pady=0)
            
            # Already received quantity
            received_qty = sum([float(d.get('items', {}).get(resource_code, 0)) for d in deliveries])
            received_label = tk.Label(table_frame, text=f"{received_qty:.0f}", 
                                    font=('Segoe UI', 9), bg=row_bg, fg='#27ae60', relief='solid', bd=1)
            received_label.grid(row=i, column=4, sticky='nsew', padx=0, pady=0)
            
            # Pending quantity
            pending_qty = ordered_qty - received_qty
            pending_label = tk.Label(table_frame, text=f"{pending_qty:.0f}", 
                                   font=('Segoe UI', 9), bg=row_bg, fg='#e74c3c', relief='solid', bd=1)
            pending_label.grid(row=i, column=5, sticky='nsew', padx=0, pady=0)
            
            # Receive quantity entry
            entry_frame = tk.Frame(table_frame, bg=row_bg, relief='solid', bd=1)
            entry_frame.grid(row=i, column=6, sticky='nsew', padx=0, pady=0)
            
            receive_entry = tk.Entry(entry_frame, font=('Segoe UI', 9), justify='center', bd=0)
            receive_entry.pack(fill='both', expand=True, padx=2, pady=2)
            receive_entry.insert(0, "0")
            self.receive_entries[resource_code] = receive_entry
            
            # Get unit rate from trends
            unit_rate = self.get_unit_rate(resource_code, item.get('item_description', ''))
            
            # Calculate amounts
            total_amount += received_qty * unit_rate
            balance_amount += pending_qty * unit_rate
            
            # Unit Rate display
            rate_label = tk.Label(table_frame, text=f"{unit_rate:.2f}" if unit_rate else "0.00", 
                                 font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', relief='solid', bd=1)
            rate_label.grid(row=i, column=7, sticky='nsew', padx=0, pady=0)
            
            # Total Price display
            total_label = tk.Label(table_frame, text="0.00", 
                                  font=('Segoe UI', 9, 'bold'), bg=row_bg, fg='#27ae60', relief='solid', bd=1)
            total_label.grid(row=i, column=8, sticky='nsew', padx=0, pady=0)
            
            # Bind entry to update total price
            receive_entry.bind('<KeyRelease>', lambda e, rate=unit_rate, label=total_label, entry=receive_entry: 
                              self.update_total_price(entry, rate, label))
        
        # Add summary rows
        summary_row = len(items) + 1
        
        # Total Amount
        total_label_frame = tk.Frame(table_frame, bg='#2c3e50', relief='solid', bd=1)
        total_label_frame.grid(row=summary_row, column=0, columnspan=7, sticky='nsew', padx=0, pady=0)
        tk.Label(total_label_frame, text="Total Amount (Received):", font=('Segoe UI', 10, 'bold'),
                bg='#2c3e50', fg='white', anchor='e', padx=10).pack(fill='both', expand=True)
        
        total_amount_label = tk.Label(table_frame, text=f"{total_amount:.2f}", 
                                     font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white', relief='solid', bd=1)
        total_amount_label.grid(row=summary_row, column=7, columnspan=2, sticky='nsew', padx=0, pady=0)
        
        # Balance Amount
        balance_label_frame = tk.Frame(table_frame, bg='#2c3e50', relief='solid', bd=1)
        balance_label_frame.grid(row=summary_row+1, column=0, columnspan=7, sticky='nsew', padx=0, pady=0)
        tk.Label(balance_label_frame, text="Balance Amount (Pending):", font=('Segoe UI', 10, 'bold'),
                bg='#2c3e50', fg='white', anchor='e', padx=10).pack(fill='both', expand=True)
        
        balance_amount_label = tk.Label(table_frame, text=f"{balance_amount:.2f}", 
                                       font=('Segoe UI', 10, 'bold'), bg='#e74c3c', fg='white', relief='solid', bd=1)
        balance_amount_label.grid(row=summary_row+1, column=7, columnspan=2, sticky='nsew', padx=0, pady=0)
        
        # Bottom section - Delivery History
        history_frame = tk.LabelFrame(main_frame, text="Delivery History", font=('Segoe UI', 12, 'bold'),
                                     bg='#ecf0f1', fg='#2c3e50')
        history_frame.pack(fill='both', expand=True)
        
        # History table
        history_container = tk.Frame(history_frame, bg='white')
        history_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Canvas for scrolling history
        history_canvas = tk.Canvas(history_container, bg='white', highlightthickness=0)
        history_scrollbar = tk.Scrollbar(history_container, orient='vertical', command=history_canvas.yview)
        history_scrollable = tk.Frame(history_canvas, bg='white')
        
        history_canvas.configure(yscrollcommand=history_scrollbar.set)
        history_scrollbar.pack(side='right', fill='y')
        history_canvas.pack(side='left', fill='both', expand=True)
        history_canvas.create_window((0, 0), window=history_scrollable, anchor='nw')
        
        history_scrollable.bind('<Configure>', 
                               lambda e: history_canvas.configure(scrollregion=history_canvas.bbox('all')))
        
        # Store reference for refreshing
        self.history_scrollable_frame = history_scrollable
        
        # Display delivery history with consistent blue headers
        if deliveries:
            for i, delivery in enumerate(deliveries):
                # Main delivery card
                delivery_card = tk.Frame(history_scrollable, bg='white', relief='solid', bd=2)
                delivery_card.pack(fill='x', pady=5, padx=5)
                
                # Header with blue background - increased height
                header_frame = tk.Frame(delivery_card, bg='#3498db', height=55)
                header_frame.pack(fill='x')
                header_frame.pack_propagate(False)
                
                # Delivery title
                title_frame = tk.Frame(header_frame, bg='#3498db')
                title_frame.pack(fill='both', expand=True, padx=10, pady=8)
                
                tk.Label(title_frame, text=f"📦 Delivery #{i+1}", 
                        font=('Segoe UI', 12, 'bold'), bg='#3498db', fg='white').pack(side='left')
                
                tk.Label(title_frame, text=f"📅 {delivery.get('date', 'N/A')}", 
                        font=('Segoe UI', 11), bg='#3498db', fg='white').pack(side='left', padx=(20, 0))
                
                # Action buttons
                btn_frame = tk.Frame(title_frame, bg='#3498db')
                btn_frame.pack(side='right')
                
                edit_btn = tk.Button(btn_frame, text="✏️ Edit", bg='#f39c12', fg='white',
                                   font=('Segoe UI', 9, 'bold'), padx=10, pady=3, relief='flat',
                                   command=lambda idx=i: self.edit_delivery(lpo, idx, receive_window))
                edit_btn.pack(side='right', padx=2)
                
                del_btn = tk.Button(btn_frame, text="🗑️ Delete", bg='#e74c3c', fg='white',
                                  font=('Segoe UI', 9, 'bold'), padx=10, pady=3, relief='flat',
                                  command=lambda idx=i: self.delete_delivery(lpo, idx, receive_window))
                del_btn.pack(side='right', padx=2)
                
                # Items table
                items_frame = tk.Frame(delivery_card, bg='white')
                items_frame.pack(fill='x', padx=10, pady=8)
                
                # Table headers
                headers_frame = tk.Frame(items_frame, bg='#ecf0f1')
                headers_frame.pack(fill='x', pady=(0, 2))
                
                tk.Label(headers_frame, text="Item Code", font=('Segoe UI', 10, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50', width=18, anchor='w').pack(side='left', padx=5)
                tk.Label(headers_frame, text="Item Description", font=('Segoe UI', 10, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50', width=35, anchor='w').pack(side='left', padx=5)
                tk.Label(headers_frame, text="Unit", font=('Segoe UI', 10, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50', width=8).pack(side='left', padx=5)
                tk.Label(headers_frame, text="Quantity", font=('Segoe UI', 10, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50', width=10).pack(side='left', padx=5)
                
                # Items data
                for j, (item_code, qty) in enumerate(delivery.get('items', {}).items()):
                    # Find item description and unit from LPO items
                    item_desc = 'N/A'
                    item_unit = 'Nos'
                    for lpo_item in items:
                        if lpo_item.get('resource_code') == item_code:
                            item_desc = lpo_item.get('item_description', 'N/A')
                            item_unit = lpo_item.get('unit', 'Nos')
                            break
                    
                    item_row = tk.Frame(items_frame, bg='white' if j % 2 == 0 else '#f8f9fa')
                    item_row.pack(fill='x', pady=1)
                    
                    tk.Label(item_row, text=item_code, font=('Segoe UI', 10),
                            bg=item_row['bg'], fg='#2c3e50', width=18, anchor='w').pack(side='left', padx=5)
                    tk.Label(item_row, text=item_desc, font=('Segoe UI', 10),
                            bg=item_row['bg'], fg='#2c3e50', width=35, anchor='w').pack(side='left', padx=5)
                    tk.Label(item_row, text=item_unit, font=('Segoe UI', 10),
                            bg=item_row['bg'], fg='#2c3e50', width=8).pack(side='left', padx=5)
                    tk.Label(item_row, text=str(qty), font=('Segoe UI', 10, 'bold'),
                            bg=item_row['bg'], fg='#27ae60', width=10).pack(side='left', padx=5)
        else:
            # Empty state with attractive design
            empty_frame = tk.Frame(history_scrollable, bg='white', relief='solid', bd=1)
            empty_frame.pack(fill='x', pady=20, padx=20)
            
            tk.Label(empty_frame, text="📋 No deliveries recorded yet",
                    font=('Segoe UI', 12, 'bold'), bg='white', fg='#7f8c8d').pack(pady=20)
            tk.Label(empty_frame, text="Deliveries will appear here after saving",
                    font=('Segoe UI', 10), bg='white', fg='#95a5a6').pack(pady=(0, 20))
        
        # Bottom buttons
        button_frame = tk.Frame(receive_window, bg='#ecf0f1')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="✖️ Close", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=5,
                 command=receive_window.destroy).pack(side='right')
    
    def record_delivery(self, lpo, window):
        """Record a new delivery"""
        # Collect received quantities
        delivery_items = {}
        has_items = False
        
        for resource_code, entry in self.receive_entries.items():
            try:
                qty = float(entry.get() or 0)
                if qty > 0:
                    delivery_items[resource_code] = qty
                    has_items = True
            except ValueError:
                messagebox.showerror("Error", f"Invalid quantity for {resource_code}")
                return
        
        if not has_items:
            messagebox.showwarning("Warning", "Please enter quantities to receive")
            return
        
        # Create delivery record with selected date
        selected_date = self.delivery_date.get_date().strftime('%Y-%m-%d')
        delivery = {
            'date': selected_date,
            'items': delivery_items
        }
        
        # Add to LPO deliveries
        if 'deliveries' not in lpo:
            lpo['deliveries'] = []
        lpo['deliveries'].append(delivery)
        
        # Update LPO status - mark as completed if all items received
        delivery_status = self.get_delivery_status(lpo)
        if delivery_status == 'Completed':
            lpo['lpo_status'] = 'Completed'
        else:
            lpo['lpo_status'] = 'Partially Received'
        
        # Save data
        self.save_lpo_data()
        
        # Don't show success message - just update silently
        
        # Refresh the delivery history in the same window
        self.refresh_delivery_history(window, lpo)
        
        # Clear the input fields
        for entry in self.receive_entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        
        # Update the received quantities display
        self.refresh_items_table(lpo)
        
        # Don't close the window - keep it open for more deliveries
    
    def edit_delivery(self, lpo, delivery_index, parent_window):
        """Edit an existing delivery"""
        deliveries = lpo.get('deliveries', [])
        if delivery_index >= len(deliveries):
            return
        
        delivery = deliveries[delivery_index]
        
        # Create edit dialog
        edit_window = tk.Toplevel(parent_window)
        edit_window.title(f"Edit Delivery #{delivery_index + 1}")
        edit_window.geometry("400x300")
        edit_window.configure(bg='#ecf0f1')
        
        # Header
        tk.Label(edit_window, text=f"Edit Delivery #{delivery_index + 1}",
                font=('Segoe UI', 14, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(pady=10)
        
        # Date picker
        date_frame = tk.Frame(edit_window, bg='#ecf0f1')
        date_frame.pack(pady=10)
        
        tk.Label(date_frame, text="Delivery Date:", font=('Segoe UI', 10, 'bold'),
                bg='#ecf0f1', fg='#2c3e50').pack(side='left')
        
        edit_date = DateEntry(date_frame, width=12, background='darkblue',
                             foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        edit_date.set_date(datetime.strptime(delivery['date'], '%Y-%m-%d').date())
        edit_date.pack(side='left', padx=(10, 0))
        
        # Items frame
        items_frame = tk.LabelFrame(edit_window, text="Items", font=('Segoe UI', 10, 'bold'),
                                   bg='#ecf0f1', fg='#2c3e50')
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Edit entries for items
        edit_entries = {}
        for item_code, qty in delivery.get('items', {}).items():
            item_frame = tk.Frame(items_frame, bg='white')
            item_frame.pack(fill='x', padx=5, pady=2)
            
            tk.Label(item_frame, text=f"{item_code}:", font=('Segoe UI', 9),
                    bg='white', fg='#2c3e50', width=20, anchor='w').pack(side='left')
            
            entry = tk.Entry(item_frame, font=('Segoe UI', 9), width=10)
            entry.pack(side='left', padx=(10, 0))
            entry.insert(0, str(qty))
            edit_entries[item_code] = entry
        
        # Buttons
        btn_frame = tk.Frame(edit_window, bg='#ecf0f1')
        btn_frame.pack(pady=10)
        
        def save_edit():
            # Update delivery
            delivery['date'] = edit_date.get_date().strftime('%Y-%m-%d')
            for item_code, entry in edit_entries.items():
                try:
                    qty = float(entry.get() or 0)
                    if qty > 0:
                        delivery['items'][item_code] = qty
                    else:
                        del delivery['items'][item_code]
                except ValueError:
                    messagebox.showerror("Error", f"Invalid quantity for {item_code}")
                    return
            
            # Save and refresh
            self.save_lpo_data()
            messagebox.showinfo("Success", "Delivery updated successfully!")
            edit_window.destroy()
            self.refresh_delivery_history(parent_window, lpo)
        
        tk.Button(btn_frame, text="💾 Save", bg='#27ae60', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=15, pady=5,
                 command=save_edit).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="✖️ Cancel", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=15, pady=5,
                 command=edit_window.destroy).pack(side='left', padx=5)
    
    def delete_delivery(self, lpo, delivery_index, parent_window):
        """Delete a delivery"""
        result = messagebox.askyesno("Confirm Delete", 
                                    f"Delete Delivery #{delivery_index + 1}?\nThis action cannot be undone.")
        if result:
            deliveries = lpo.get('deliveries', [])
            if delivery_index < len(deliveries):
                del deliveries[delivery_index]
                
                # Update LPO status
                lpo['lpo_status'] = self.get_delivery_status(lpo)
                
                # Save and refresh
                self.save_lpo_data()
                messagebox.showinfo("Success", "Delivery deleted successfully!")
                self.refresh_delivery_history(parent_window, lpo)
    
    def view_lpo(self, lpo):
        """View LPO details"""
        # Create popup window
        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"LPO Details - {lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')}")
        view_window.geometry("800x600")
        view_window.configure(bg='#ecf0f1')
        
        # Header
        header_frame = tk.Frame(view_window, bg='#e67e22', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        display_lpo = lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')
        tk.Label(header_frame, text=f"📋 {display_lpo} - LPO Details",
                font=('Segoe UI', 16, 'bold'), bg='#e67e22', fg='white').pack(pady=15)
        
        # Main content with scrollbar
        main_frame = tk.Frame(view_window, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # LPO Info section
        info_frame = tk.LabelFrame(main_frame, text="LPO Information", font=('Segoe UI', 12, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50')
        info_frame.pack(fill='x', pady=(0, 10))
        
        info_grid = tk.Frame(info_frame, bg='white')
        info_grid.pack(fill='x', padx=10, pady=10)
        
        # Info details
        info_data = [
            ("LPO Number:", lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')),
            ("Approval Date:", lpo.get('approval_date', 'N/A')),
            ("Required Date:", lpo.get('required_date', 'N/A')),
            ("Status:", lpo.get('lpo_status', 'N/A')),
            ("Supplier:", lpo.get('supplier_name', 'N/A')),
            ("Phone:", lpo.get('phone_number', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(info_data):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(info_grid, text=label, font=('Segoe UI', 10, 'bold'),
                    bg='white', fg='#2c3e50').grid(row=row, column=col, sticky='w', padx=(0, 10), pady=5)
            tk.Label(info_grid, text=value, font=('Segoe UI', 10),
                    bg='white', fg='#34495e').grid(row=row, column=col+1, sticky='w', padx=(0, 30), pady=5)
        
        # Close button
        button_frame = tk.Frame(view_window, bg='#ecf0f1')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="✖️ Close", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=5,
                 command=view_window.destroy).pack(side='right')
    
    def filter_lpos(self, event=None):
        """Filter LPOs based on search text"""
        self.display_lpos()
    
    def refresh_data(self):
        """Refresh LPO data"""
        self.load_lpo_data()
    
    def toggle_auto_refresh(self):
        """Toggle auto refresh on/off"""
        if self.auto_refresh_var.get():
            self.auto_refresh_enabled = True
            self.schedule_refresh()
        else:
            self.auto_refresh_enabled = False
            if self.refresh_job:
                self.parent_frame.after_cancel(self.refresh_job)
                self.refresh_job = None
    
    def schedule_refresh(self):
        """Schedule next auto refresh"""
        if self.auto_refresh_enabled:
            self.refresh_data()
            self.refresh_job = self.parent_frame.after(30000, self.schedule_refresh)
    
    def toggle_receive_auto_refresh(self, lpo, receive_window):
        """Toggle auto refresh in receive materials window"""
        if self.receive_auto_refresh_var.get():
            self.receive_auto_refresh_enabled = True
            self.schedule_receive_refresh(lpo)
        else:
            self.receive_auto_refresh_enabled = False
            if hasattr(self, 'receive_refresh_job') and self.receive_refresh_job:
                receive_window.after_cancel(self.receive_refresh_job)
                self.receive_refresh_job = None
    
    def schedule_receive_refresh(self, lpo):
        """Schedule next auto refresh for receive window"""
        if hasattr(self, 'receive_auto_refresh_enabled') and self.receive_auto_refresh_enabled:
            self.refresh_items_table(lpo)
            if hasattr(self, 'items_table_frame'):
                self.receive_refresh_job = self.items_table_frame.after(30000, lambda: self.schedule_receive_refresh(lpo))
    
    def get_unit_rate(self, resource_code, item_description):
        """Get unit rate from trends file"""
        try:
            trends_file = f"trends_{self.department_name.lower().replace(' ', '_')}.json"
            if os.path.exists(trends_file):
                with open(trends_file, 'r', encoding='utf-8') as f:
                    trends_data = json.load(f)
                
                for item_key, trend in trends_data.items():
                    if (trend.get('resource_code', '').lower() == resource_code.lower() and 
                        trend.get('item_description', '').lower() == item_description.lower()):
                        price_history = trend.get('price_history', [])
                        if price_history:
                            return float(price_history[-1].get('price', 0))
            return 0.0
        except:
            return 0.0
    
    def update_total_price(self, entry, unit_rate, label):
        """Update total price when quantity changes"""
        try:
            qty = float(entry.get() or 0)
            total = qty * unit_rate
            label.configure(text=f"{total:.2f}")
        except:
            label.configure(text="0.00")
    
    def refresh_delivery_history(self, receive_window, lpo):
        """Refresh the delivery history section without closing the window"""
        # Store reference to history scrollable frame
        if not hasattr(self, 'history_scrollable_frame'):
            return
        
        # Clear existing history
        for widget in self.history_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Repopulate delivery history with attractive table format
        deliveries = lpo.get('deliveries', [])
        if deliveries:
            for i, delivery in enumerate(deliveries):
                # Main delivery card
                delivery_card = tk.Frame(self.history_scrollable_frame, bg='white', relief='solid', bd=2, width=800)
                delivery_card.pack(fill='both', expand=True, pady=1, padx=1)
                
                # Header with gradient-like effect - increased height
                header_frame = tk.Frame(delivery_card, bg='#3498db', height=45)
                header_frame.pack(fill='x')
                header_frame.pack_propagate(False)
                
                # Delivery title
                title_frame = tk.Frame(header_frame, bg='#3498db')
                title_frame.pack(fill='both', expand=True, padx=8, pady=8)
                
                tk.Label(title_frame, text=f"📦 Delivery #{i+1}", 
                        font=('Segoe UI', 11, 'bold'), bg='#3498db', fg='white', width=20, anchor='w').pack(side='left')
                
                tk.Label(title_frame, text=f"📅 {delivery.get('date', 'N/A')}", 
                        font=('Segoe UI', 10), bg='#3498db', fg='white').pack(side='left', padx=(20, 0))
                
                # Action buttons
                btn_frame = tk.Frame(title_frame, bg='#3498db')
                btn_frame.pack(side='right')
                
                # Create buttons with proper lambda closure
                def make_delete_cmd(index):
                    return lambda: self.delete_delivery(lpo, index, receive_window)
                
                def make_edit_cmd(index):
                    return lambda: self.edit_delivery(lpo, index, receive_window)
                
                del_btn = tk.Button(btn_frame, text="🗑️ Delete", bg='#e74c3c', fg='white',
                                  font=('Segoe UI', 9, 'bold'), padx=12, pady=4, relief='flat',
                                  command=make_delete_cmd(i))
                del_btn.pack(side='right', padx=3)
                
                edit_btn = tk.Button(btn_frame, text="✏️ Edit", bg='#f39c12', fg='white',
                                   font=('Segoe UI', 9, 'bold'), padx=12, pady=4, relief='flat',
                                   command=make_edit_cmd(i))
                edit_btn.pack(side='right', padx=3)
                
                # Items table
                items_frame = tk.Frame(delivery_card, bg='white')
                items_frame.pack(fill='x', padx=10, pady=8)
                
                # Table headers
                headers_frame = tk.Frame(items_frame, bg='#ecf0f1')
                headers_frame.pack(fill='x', pady=(0, 2))
                
                tk.Label(headers_frame, text="Item Code", font=('Segoe UI', 9, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50', width=16, anchor='w').pack(side='left', padx=5)
                tk.Label(headers_frame, text="Item Description", font=('Segoe UI', 9, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50', width=30, anchor='w').pack(side='left', padx=5)
                tk.Label(headers_frame, text="Unit", font=('Segoe UI', 9, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50', width=8).pack(side='left', padx=5)
                tk.Label(headers_frame, text="Quantity", font=('Segoe UI', 9, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50', width=10).pack(side='left', padx=5)
                
                # Items data
                items = lpo.get('items', [])
                for j, (item_code, qty) in enumerate(delivery.get('items', {}).items()):
                    # Find item description and unit
                    item_desc = 'N/A'
                    item_unit = 'Nos'
                    for lpo_item in items:
                        if lpo_item.get('resource_code') == item_code:
                            item_desc = lpo_item.get('item_description', 'N/A')
                            item_unit = lpo_item.get('unit', 'Nos')
                            break
                    
                    item_row = tk.Frame(items_frame, bg='white' if j % 2 == 0 else '#f8f9fa')
                    item_row.pack(fill='x', pady=1)
                    
                    tk.Label(item_row, text=item_code, font=('Segoe UI', 9),
                            bg=item_row['bg'], fg='#2c3e50', width=16, anchor='w').pack(side='left', padx=5)
                    tk.Label(item_row, text=item_desc, font=('Segoe UI', 9),
                            bg=item_row['bg'], fg='#2c3e50', width=30, anchor='w').pack(side='left', padx=5)
                    tk.Label(item_row, text=item_unit, font=('Segoe UI', 9),
                            bg=item_row['bg'], fg='#2c3e50', width=8).pack(side='left', padx=5)
                    tk.Label(item_row, text=str(qty), font=('Segoe UI', 9, 'bold'),
                            bg=item_row['bg'], fg='#27ae60', width=10).pack(side='left', padx=5)
        else:
            # Empty state with attractive design
            empty_frame = tk.Frame(self.history_scrollable_frame, bg='white', relief='solid', bd=1)
            empty_frame.pack(fill='x', pady=20, padx=20)
            
            tk.Label(empty_frame, text="📋 No deliveries recorded yet",
                    font=('Segoe UI', 12, 'bold'), bg='white', fg='#7f8c8d').pack(pady=20)
            tk.Label(empty_frame, text="Deliveries will appear here after saving",
                    font=('Segoe UI', 10), bg='white', fg='#95a5a6').pack(pady=(0, 20))
    
    def refresh_items_table(self, lpo):
        """Refresh the items table to show updated received quantities"""
        if not hasattr(self, 'items_table_frame'):
            return
        
        # Clear existing table
        for widget in self.items_table_frame.winfo_children():
            widget.destroy()
        
        # Recreate table with updated data
        items = lpo.get('items', [])
        deliveries = lpo.get('deliveries', [])
        
        # Headers with grid
        headers = ["Resource Code", "Item Description", "Unit", "Ordered", "Received", "Pending", "Receive Now", "Unit Rate", "Total Price"]
        col_widths = [12, 25, 6, 8, 8, 8, 10, 10, 12]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            header_label = tk.Label(self.items_table_frame, text=header, font=('Segoe UI', 10, 'bold'),
                                   bg='#34495e', fg='white', relief='solid', bd=1)
            header_label.grid(row=0, column=col, sticky='nsew', padx=0, pady=0)
            self.items_table_frame.grid_columnconfigure(col, weight=1 if col == 1 else 0, minsize=width*8)
        
        # Calculate totals
        total_amount = 0
        balance_amount = 0
        
        # Data rows with updated received quantities
        for i, item in enumerate(items, 1):
            row_bg = 'white' if i % 2 == 1 else '#f8f9fa'
            
            # Resource Code
            resource_code = item.get('resource_code', '')
            code_label = tk.Label(self.items_table_frame, text=resource_code, 
                                 font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', 
                                 relief='solid', bd=1, anchor='center')
            code_label.grid(row=i, column=0, sticky='nsew', padx=0, pady=0)
            
            # Item description
            item_label = tk.Label(self.items_table_frame, text=item.get('item_description', 'N/A'), 
                                 font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', 
                                 relief='solid', bd=1, anchor='w', wraplength=220)
            item_label.grid(row=i, column=1, sticky='nsew', padx=0, pady=0)
            
            # Unit
            unit_label = tk.Label(self.items_table_frame, text=item.get('unit', 'Nos'), 
                                 font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', 
                                 relief='solid', bd=1, anchor='center')
            unit_label.grid(row=i, column=2, sticky='nsew', padx=0, pady=0)
            
            # Ordered quantity
            ordered_qty = float(item.get('quantity', 0))
            ordered_label = tk.Label(self.items_table_frame, text=f"{ordered_qty:.0f}", 
                                   font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', relief='solid', bd=1)
            ordered_label.grid(row=i, column=3, sticky='nsew', padx=0, pady=0)
            
            # Already received quantity (updated)
            received_qty = sum([float(d.get('items', {}).get(resource_code, 0)) for d in deliveries])
            received_label = tk.Label(self.items_table_frame, text=f"{received_qty:.0f}", 
                                    font=('Segoe UI', 9), bg=row_bg, fg='#27ae60', relief='solid', bd=1)
            received_label.grid(row=i, column=4, sticky='nsew', padx=0, pady=0)
            
            # Pending quantity (updated)
            pending_qty = ordered_qty - received_qty
            pending_label = tk.Label(self.items_table_frame, text=f"{pending_qty:.0f}", 
                                   font=('Segoe UI', 9), bg=row_bg, fg='#e74c3c', relief='solid', bd=1)
            pending_label.grid(row=i, column=5, sticky='nsew', padx=0, pady=0)
            
            # Receive quantity entry (keep existing entry)
            entry_frame = tk.Frame(self.items_table_frame, bg=row_bg, relief='solid', bd=1)
            entry_frame.grid(row=i, column=6, sticky='nsew', padx=0, pady=0)
            
            if resource_code in self.receive_entries:
                # Keep existing entry
                existing_entry = self.receive_entries[resource_code]
                existing_entry.master.destroy()
                existing_entry = tk.Entry(entry_frame, font=('Segoe UI', 9), justify='center', bd=0)
                existing_entry.pack(fill='both', expand=True, padx=2, pady=2)
                existing_entry.insert(0, "0")
                self.receive_entries[resource_code] = existing_entry
            
            # Get unit rate from trends
            unit_rate = self.get_unit_rate(resource_code, item.get('item_description', ''))
            
            # Calculate amounts
            total_amount += received_qty * unit_rate
            balance_amount += pending_qty * unit_rate
            
            # Unit Rate display
            rate_label = tk.Label(self.items_table_frame, text=f"{unit_rate:.2f}" if unit_rate else "0.00", 
                                 font=('Segoe UI', 9), bg=row_bg, fg='#2c3e50', relief='solid', bd=1)
            rate_label.grid(row=i, column=7, sticky='nsew', padx=0, pady=0)
            
            # Total Price display
            total_label = tk.Label(self.items_table_frame, text="0.00", 
                                  font=('Segoe UI', 9, 'bold'), bg=row_bg, fg='#27ae60', relief='solid', bd=1)
            total_label.grid(row=i, column=8, sticky='nsew', padx=0, pady=0)
            
            # Bind entry to update total price
            if resource_code in self.receive_entries:
                self.receive_entries[resource_code].bind('<KeyRelease>', 
                    lambda e, rate=unit_rate, label=total_label, entry=self.receive_entries[resource_code]: 
                    self.update_total_price(entry, rate, label))
        
        # Add summary rows
        summary_row = len(items) + 1
        
        # Total Amount
        total_label_frame = tk.Frame(self.items_table_frame, bg='#2c3e50', relief='solid', bd=1)
        total_label_frame.grid(row=summary_row, column=0, columnspan=7, sticky='nsew', padx=0, pady=0)
        tk.Label(total_label_frame, text="Total Amount (Received):", font=('Segoe UI', 10, 'bold'),
                bg='#2c3e50', fg='white', anchor='e', padx=10).pack(fill='both', expand=True)
        
        total_amount_label = tk.Label(self.items_table_frame, text=f"{total_amount:.2f}", 
                                     font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white', relief='solid', bd=1)
        total_amount_label.grid(row=summary_row, column=7, columnspan=2, sticky='nsew', padx=0, pady=0)
        
        # Balance Amount
        balance_label_frame = tk.Frame(self.items_table_frame, bg='#2c3e50', relief='solid', bd=1)
        balance_label_frame.grid(row=summary_row+1, column=0, columnspan=7, sticky='nsew', padx=0, pady=0)
        tk.Label(balance_label_frame, text="Balance Amount (Pending):", font=('Segoe UI', 10, 'bold'),
                bg='#2c3e50', fg='white', anchor='e', padx=10).pack(fill='both', expand=True)
        
        balance_amount_label = tk.Label(self.items_table_frame, text=f"{balance_amount:.2f}", 
                                       font=('Segoe UI', 10, 'bold'), bg='#e74c3c', fg='white', relief='solid', bd=1)
        balance_amount_label.grid(row=summary_row+1, column=7, columnspan=2, sticky='nsew', padx=0, pady=0)