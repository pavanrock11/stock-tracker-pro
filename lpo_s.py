import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class LPOSystem:
    def __init__(self, parent_frame, department_name):
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.lpo_items = []
        self.data_file = f"lpo_{department_name.lower().replace(' ', '_')}.json"
        self.create_interface()
        self.load_lpo_data()
    
    def create_interface(self):
        # Header
        header_frame = tk.Frame(self.parent_frame, bg='#16a085', height=60)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📋 LPO - Procurement & Delivery", 
                font=('Segoe UI', 16, 'bold'), bg='#16a085', fg='white').pack(pady=15)
        
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
    
    def add_approved_pr(self, pr_data):
        """Add approved PR to LPO system"""
        # Update status and add approval date
        pr_data['status'] = 'LPO - Awaiting Delivery'
        pr_data['approval_date'] = datetime.now().strftime('%d/%m/%Y')
        pr_data['lpo_status'] = 'Invoice Prepared'
        
        # Preserve manually entered LPO details from PR Details section
        manual_lpo = pr_data.get('lpo_number', '')
        if manual_lpo and manual_lpo.strip():
            pr_data['manual_lpo_number'] = manual_lpo
        
        # Generate system LPO number based on PR number for internal tracking
        pr_number = pr_data.get('pr_number', 'PR-000')
        pr_data['lpo_number'] = pr_number.replace('PR-', 'LPO-')
        
        # Add to LPO list
        self.lpo_items.append(pr_data)
        self.save_lpo_data()
        self.display_lpos()
        
        return True
    
    def display_lpos(self):
        """Display LPO items in the scrollable frame"""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.lpo_items:
            tk.Label(self.scrollable_frame, text="No LPO items found",
                    font=('Segoe UI', 12), bg='white', fg='#7f8c8d').pack(pady=50)
            return
        
        # Filter LPOs based on search
        search_text = self.search_var.get().lower()
        filtered_lpos = [lpo for lpo in self.lpo_items 
                        if search_text in lpo.get('pr_number', '').lower() or
                           search_text in lpo.get('description', '').lower()]
        
        # Create container for horizontal layout
        self.cards_container = tk.Frame(self.scrollable_frame, bg='white')
        self.cards_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.current_row = None
        self.cards_in_row = 0
        
        for i, lpo in enumerate(filtered_lpos):
            self.create_lpo_card(lpo, i)
    
    def get_receiving_status(self, lpo):
        """Calculate receiving status based on deliveries"""
        deliveries = lpo.get('deliveries', [])
        if not deliveries:
            return 'Yet to Receive'
        
        items = lpo.get('items', [])
        for item in items:
            ordered_qty = float(item.get('quantity', 0))
            received_qty = sum([float(d.get('items', {}).get(item.get('resource_code', ''), 0)) 
                               for d in deliveries])
            if received_qty < ordered_qty:
                return 'Partially Received'
        
        return 'Completely Received'
    
    def create_lpo_card(self, lpo, index):
        """Create a card for each LPO item"""
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
        
        # Card header with PR number and status
        header_frame = tk.Frame(card_frame, bg='#16a085', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Show manually entered LPO details if available, otherwise show generated LPO number
        display_lpo = lpo.get('manual_lpo_number') or lpo.get('lpo_number', lpo.get('pr_number', 'N/A'))
        tk.Label(header_frame, text=f"📋 {display_lpo}", 
                font=('Segoe UI', 12, 'bold'), bg='#16a085', fg='white').pack(side='left', padx=10, pady=8)
        
        # LPO Status badge - calculate from deliveries
        receiving_status = self.get_receiving_status(lpo)
        if receiving_status == 'Yet to Receive':
            status_color = '#f39c12'
        elif receiving_status == 'Partially Received':
            status_color = '#3498db'
        else:
            status_color = '#27ae60'
        
        tk.Label(header_frame, text=receiving_status, 
                font=('Segoe UI', 9, 'bold'), bg=status_color, fg='white',
                padx=8, pady=2).pack(side='right', padx=10, pady=8)
        
        # Card body with details
        body_frame = tk.Frame(card_frame, bg='white')
        body_frame.pack(fill='x', padx=15, pady=10)
        
        # Row 1: Dates
        row1 = tk.Frame(body_frame, bg='white')
        row1.pack(fill='x', pady=(0, 5))
        
        tk.Label(row1, text=f"📅 Approved: {lpo.get('approval_date', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left')
        
        tk.Label(row1, text=f"⏰ Required: {lpo.get('required_date', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left', padx=(20, 0))
        
        # Row 2: Items and Value
        row2 = tk.Frame(body_frame, bg='white')
        row2.pack(fill='x', pady=(0, 5))
        
        tk.Label(row2, text=f"📦 Items: {lpo.get('items_count', 0)}", 
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
        
        tk.Button(action_frame, text="👁️ View", bg='#3498db', fg='white',
                 font=('Segoe UI', 8, 'bold'), padx=10, pady=2,
                 command=lambda: self.view_lpo(lpo)).pack(side='left', padx=(0, 5))
        

        
        tk.Button(action_frame, text="🗑️ Delete", bg='#95a5a6', fg='white',
                 font=('Segoe UI', 8, 'bold'), padx=10, pady=2,
                 command=lambda: self.delete_lpo(lpo)).pack(side='right')
    
    def view_lpo(self, lpo):
        """View LPO details with selected items"""
        # Get LPO items for highlighting
        lpo_items = lpo.get('items', [])
        print(f"DEBUG: LPO has {len(lpo_items)} items to highlight in green")
        for item in lpo_items:
            print(f"DEBUG: LPO Item - {item.get('resource_code')} : {item.get('item_description')}")
        
        # Create popup window
        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"LPO Details - {lpo.get('lpo_number', lpo.get('pr_number', 'N/A'))}")
        view_window.geometry("800x600")
        view_window.configure(bg='#ecf0f1')
        
        # Clear highlights when window is closed
        def on_close():
            self.clear_inventory_highlights()
            view_window.destroy()
        view_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Header
        header_frame = tk.Frame(view_window, bg='#16a085', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Show manually entered LPO details if available, otherwise show generated LPO number
        display_lpo = lpo.get('manual_lpo_number') or lpo.get('lpo_number', lpo.get('pr_number', 'N/A'))
        tk.Label(header_frame, text=f"📋 {display_lpo} - LPO Details",
                font=('Segoe UI', 16, 'bold'), bg='#16a085', fg='white').pack(pady=15)
        
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
            ("LPO Number:", lpo.get('manual_lpo_number') or lpo.get('lpo_number', lpo.get('pr_number', 'N/A'))),
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
        
        # Description
        desc_frame = tk.LabelFrame(main_frame, text="Description", font=('Segoe UI', 12, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50')
        desc_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(desc_frame, text=lpo.get('description', 'No description available'),
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
        items = lpo.get('items', [])
        if items:
            # Headers
            headers = ['S.No', 'Resource Code', 'Item Description', 'Unit', 'Quantity', 'Status']
            header_frame = tk.Frame(scrollable_frame, bg='#16a085')
            header_frame.pack(fill='x')
            
            for col, header in enumerate(headers):
                tk.Label(header_frame, text=header, font=('Segoe UI', 10, 'bold'),
                        bg='#16a085', fg='white', relief='solid', bd=1).grid(
                        row=0, column=col, sticky='nsew', padx=0, pady=0)
            
            # Configure column weights
            header_frame.grid_columnconfigure(0, weight=0, minsize=50)
            header_frame.grid_columnconfigure(1, weight=1, minsize=120)
            header_frame.grid_columnconfigure(2, weight=3, minsize=300)
            header_frame.grid_columnconfigure(3, weight=0, minsize=80)
            header_frame.grid_columnconfigure(4, weight=0, minsize=80)
            header_frame.grid_columnconfigure(5, weight=0, minsize=120)
            
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
                
                # Quantity
                quantity = item.get('quantity', '1')
                tk.Label(row_frame, text=quantity, font=('Segoe UI', 9),
                        bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                        row=0, column=4, sticky='nsew', padx=0, pady=0)
                
                # Status - check receiving status
                status_text, status_color = self.get_item_status(lpo, item)
                tk.Label(row_frame, text=status_text, font=('Segoe UI', 9, 'bold'),
                        bg=status_color, fg='white', relief='solid', bd=1).grid(
                        row=0, column=5, sticky='nsew', padx=0, pady=0)
                
                # Configure column weights for each row
                row_frame.grid_columnconfigure(0, weight=0, minsize=50)
                row_frame.grid_columnconfigure(1, weight=1, minsize=120)
                row_frame.grid_columnconfigure(2, weight=3, minsize=300)
                row_frame.grid_columnconfigure(3, weight=0, minsize=80)
                row_frame.grid_columnconfigure(4, weight=0, minsize=80)
                row_frame.grid_columnconfigure(5, weight=0, minsize=120)
        else:
            tk.Label(scrollable_frame, text="No items found for this LPO",
                    font=('Segoe UI', 12), bg='white', fg='#7f8c8d').pack(pady=50)
        
        # Close button
        button_frame = tk.Frame(view_window, bg='#ecf0f1')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="✖️ Close", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=5,
                 command=on_close).pack(side='right')
        
        # Highlight matching items in inventory with green color
        view_window.after(100, lambda: self.highlight_inventory_items(lpo_items))
    
    def mark_delivered(self, lpo):
        """Mark LPO as delivered"""
        result = messagebox.askyesno("Confirm Delivery", 
                                    f"Mark LPO {lpo.get('lpo_number', lpo.get('pr_number'))} as delivered?")
        if result:
            lpo['lpo_status'] = 'Delivered'
            lpo['delivery_date'] = datetime.now().strftime('%d/%m/%Y')
            self.save_lpo_data()
            self.display_lpos()
            messagebox.showinfo("Success", f"LPO {lpo.get('lpo_number', lpo.get('pr_number'))} marked as delivered!")
    
    def delete_lpo(self, lpo):
        """Delete LPO item"""
        result = messagebox.askyesno("Confirm Delete", 
                                    f"Delete LPO {lpo.get('lpo_number', lpo.get('pr_number'))}?")
        if result:
            self.lpo_items = [item for item in self.lpo_items 
                             if item.get('lpo_number') != lpo.get('lpo_number')]
            self.save_lpo_data()
            self.display_lpos()
            messagebox.showinfo("Success", f"LPO {lpo.get('lpo_number', lpo.get('pr_number'))} deleted!")
    
    def filter_lpos(self, event=None):
        """Filter LPOs based on search text"""
        self.display_lpos()
    
    def refresh_data(self):
        """Refresh LPO data"""
        self.load_lpo_data()
    
    def highlight_inventory_items(self, lpo_items):
        """Highlight matching items in inventory overview with green color for LPO items"""
        try:
            print(f"\n=== GREEN HIGHLIGHTING DEBUG ===")
            print(f"DEBUG: Highlighting {len(lpo_items)} LPO items in green")
            for item in lpo_items:
                print(f"DEBUG: LPO Item - Resource: '{item.get('resource_code')}', Description: '{item.get('item_description')}'")
            
            # Find inventory overview widget in the application
            inventory_widget = self.find_inventory_widget()
            print(f"DEBUG: Found inventory widget: {inventory_widget is not None}")
            if inventory_widget:
                print(f"DEBUG: Calling highlight_lpo_items on widget: {type(inventory_widget)}")
                inventory_widget.highlight_lpo_items(lpo_items)
                print(f"DEBUG: highlight_lpo_items called successfully")
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
        """Clear green highlights from inventory overview"""
        try:
            inventory_widget = self.find_inventory_widget()
            if inventory_widget:
                inventory_widget.clear_lpo_highlights()
        except Exception as e:
            print(f"Error clearing inventory highlights: {e}")
    
    def get_item_status(self, lpo, item):
        """Get receiving status for a specific item"""
        lpo_number = lpo.get('lpo_number', '')
        resource_code = item.get('resource_code', '')
        ordered_qty = float(item.get('quantity', 0))
        
        # Check if LPO exists in pending materials
        pending_file = f"lpo_{self.department_name.lower().replace(' ', '_')}.json"
        if not os.path.exists(pending_file):
            return 'Completely Received', '#27ae60'
        
        try:
            with open(pending_file, 'r', encoding='utf-8') as f:
                pending_lpos = json.load(f)
            
            # Find matching LPO
            matching_lpo = None
            for pending_lpo in pending_lpos:
                if pending_lpo.get('lpo_number') == lpo_number:
                    matching_lpo = pending_lpo
                    break
            
            if not matching_lpo:
                return 'Completely Received', '#27ae60'
            
            # Calculate received quantity for this item
            deliveries = matching_lpo.get('deliveries', [])
            received_qty = sum([float(d.get('items', {}).get(resource_code, 0)) for d in deliveries])
            pending_qty = ordered_qty - received_qty
            
            if pending_qty <= 0:
                return 'Completely Received', '#27ae60'
            else:
                return 'Yet to Receive', '#f39c12'
        
        except Exception as e:
            print(f"Error checking item status: {e}")
            return 'Unknown', '#95a5a6'
    
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