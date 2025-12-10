import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import json
import os
from datetime import datetime
import tkinter.simpledialog

class PRRise:
    def __init__(self, parent_frame, department_name):
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.selected_items = []
        self.supplier_history = self.load_supplier_history()
        self.create_interface()
    
    def load_supplier_history(self):
        """Load supplier history from file"""
        try:
            if os.path.exists('supplier_history.json'):
                with open('supplier_history.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_supplier_history(self):
        """Save supplier history to file"""
        try:
            with open('supplier_history.json', 'w') as f:
                json.dump(self.supplier_history, f)
        except:
            pass
    
    def create_interface(self):
        # Header
        header_frame = tk.Frame(self.parent_frame, bg='#34495e', height=50)
        header_frame.pack(fill='x', padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Purchase Request Details", 
                font=('Arial', 14, 'bold'), bg='#34495e', fg='white').pack(pady=12)
        
        # Main content with scrollbar
        main_canvas = tk.Canvas(self.parent_frame, bg='white')
        main_scrollbar = tk.Scrollbar(self.parent_frame, orient='vertical', command=main_canvas.yview)
        self.main_content = tk.Frame(main_canvas, bg='white')
        
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_scrollbar.pack(side='right', fill='y')
        main_canvas.pack(side='left', fill='both', expand=True, padx=5, pady=(0, 5))
        main_canvas.create_window((0, 0), window=self.main_content, anchor='nw')
        
        # Configure scroll region
        self.main_content.bind('<Configure>', 
                              lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all')))
        
        # PR Details Form
        self.create_pr_form()
        
        # Selected items section
        self.create_selected_items_section()
        
        # Action buttons
        self.create_action_buttons()
    
    def create_pr_form(self):
        """Create modern PR form"""
        # Modern container
        main_container = tk.Frame(self.main_content, bg='#0f172a', relief='flat')
        main_container.pack(fill='x', padx=15, pady=15)
        
        # Header
        header_container = tk.Frame(main_container, bg='#1e293b', relief='flat')
        header_container.pack(fill='x', padx=3, pady=3)
        
        header_inner = tk.Frame(header_container, bg='#0ea5e9', height=50)
        header_inner.pack(fill='x', padx=2, pady=2)
        header_inner.pack_propagate(False)
        
        header_content = tk.Frame(header_inner, bg='#0ea5e9')
        header_content.pack(expand=True, fill='both')
        
        tk.Label(header_content, text="✨ PURCHASE REQUEST", 
                font=('Inter', 16, 'bold'), bg='#0ea5e9', fg='white').pack(pady=10)
        
        # Form body
        form_body = tk.Frame(main_container, bg='#1e293b')
        form_body.pack(fill='x', padx=3, pady=(0, 3))
        
        content_area = tk.Frame(form_body, bg='#1e293b')
        content_area.pack(fill='x', padx=25, pady=25)
        

        
        # PR Number section
        pr_section = tk.Frame(content_area, bg='#1e293b')
        pr_section.pack(fill='x', pady=(0, 20))
        
        tk.Label(pr_section, text="📋 PR NUMBER", 
                font=('Inter', 11, 'bold'), bg='#1e293b', fg='#06b6d4').pack(anchor='w', pady=(0, 8))
        
        pr_input_frame = tk.Frame(pr_section, bg='#334155', relief='flat')
        pr_input_frame.pack(fill='x', ipady=2)
        
        self.pr_var = tk.StringVar()
        self.pr_entry = tk.Entry(pr_input_frame, textvariable=self.pr_var,
                                font=('Inter', 11), bg='#475569', fg='white',
                                relief='flat', bd=0, insertbackground='white')
        self.pr_entry.pack(fill='x', padx=15, pady=12)
        
        # Dates section
        dates_section = tk.Frame(content_area, bg='#1e293b')
        dates_section.pack(fill='x', pady=(0, 20))
        
        tk.Label(dates_section, text="📅 TIMELINE MANAGEMENT", 
                font=('Inter', 11, 'bold'), bg='#1e293b', fg='#06b6d4').pack(anchor='w', pady=(0, 10))
        
        dates_row = tk.Frame(dates_section, bg='#1e293b')
        dates_row.pack(fill='x')
        
        # Request Date
        req_date_col = tk.Frame(dates_row, bg='#1e293b')
        req_date_col.pack(side='left', fill='x', expand=True, padx=(0, 15))
        
        tk.Label(req_date_col, text="Request Date", font=('Inter', 9), 
                bg='#1e293b', fg='#94a3b8').pack(anchor='w', pady=(0, 3))
        
        self.request_date = DateEntry(req_date_col, width=18, background='#0ea5e9',
                                     foreground='white', borderwidth=0, date_pattern='dd/mm/yyyy',
                                     font=('Inter', 10, 'bold'))
        self.request_date.pack(anchor='w')
        
        # Required Date
        req_by_col = tk.Frame(dates_row, bg='#1e293b')
        req_by_col.pack(side='right', fill='x', expand=True, padx=(15, 0))
        
        tk.Label(req_by_col, text="Required By", font=('Inter', 9), 
                bg='#1e293b', fg='#94a3b8').pack(anchor='w', pady=(0, 3))
        
        self.required_date = DateEntry(req_by_col, width=18, background='#0ea5e9',
                                      foreground='white', borderwidth=0, date_pattern='dd/mm/yyyy',
                                      font=('Inter', 10, 'bold'))
        self.required_date.pack(anchor='w')
        
        # Description section
        desc_section = tk.Frame(content_area, bg='#1e293b')
        desc_section.pack(fill='x')
        
        tk.Label(desc_section, text="📝 DESCRIPTION & NOTES", 
                font=('Inter', 11, 'bold'), bg='#1e293b', fg='#06b6d4').pack(anchor='w', pady=(0, 8))
        
        desc_container = tk.Frame(desc_section, bg='#334155', relief='flat')
        desc_container.pack(fill='x', ipady=3)
        
        self.description_text = tk.Text(desc_container, height=4, font=('Inter', 10),
                                       bg='#475569', fg='white', relief='flat', bd=0,
                                       wrap='word', insertbackground='white')
        self.description_text.pack(fill='x', padx=15, pady=12)
    
    def create_selected_items_section(self):
        """Create selected items section"""
        items_frame = tk.LabelFrame(self.main_content, text="Selected Items", 
                                   font=('Arial', 11, 'bold'), bg='white', fg='#2c3e50')
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Items count header
        self.items_header_label = tk.Label(items_frame, text="Selected Items (0)", 
                                          font=('Arial', 10, 'bold'), bg='white', fg='#34495e')
        self.items_header_label.pack(pady=5)
        
        # Scrollable items list
        list_frame = tk.Frame(items_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(list_frame, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # Configure scroll region
        self.scrollable_frame.bind('<Configure>', 
                                  lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        # Initial empty message
        self.show_empty_message()
    
    def create_action_buttons(self):
        """Create modern action buttons"""
        # Modern action buttons
        modern_btn_frame = tk.Frame(self.main_content, bg='#0f172a')
        modern_btn_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        btn_container = tk.Frame(modern_btn_frame, bg='#1e293b')
        btn_container.pack(fill='x', padx=3, pady=3)
        
        btn_inner = tk.Frame(btn_container, bg='#1e293b')
        btn_inner.pack(fill='x', padx=20, pady=15)
        
        tk.Button(btn_inner, text="🗑️ CLEAR ALL", bg='#ef4444', fg='white',
                 font=('Inter', 10, 'bold'), relief='flat', bd=0, cursor='hand2',
                 command=self.clear_all).pack(side='left', padx=5, ipady=8, ipadx=15)
        
        tk.Button(btn_inner, text="➡️ SUBMIT PR", bg='#10b981', fg='white',
                 font=('Inter', 10, 'bold'), relief='flat', bd=0, cursor='hand2',
                 command=self.submit_pr).pack(side='right', padx=5, ipady=8, ipadx=15)
    
    def show_supplier_dropdown(self):
        """Show supplier dropdown"""
        pass
    
    def show_empty_message(self):
        """Show empty message when no items selected"""
        tk.Label(self.scrollable_frame, text="No items selected", 
                font=('Arial', 11), bg='white', fg='#7f8c8d').pack(pady=30)
    
    def update_selected_items(self, items):
        """Update the selected items list - keep section empty until Next is clicked"""
        self.selected_items = items
        
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Always show empty message - no item display until Next is clicked
        self.show_empty_message()
    
    def remove_item(self, index):
        """Remove item from selected list"""
        if 0 <= index < len(self.selected_items):
            self.selected_items.pop(index)
            self.update_selected_items(self.selected_items)
    
    def clear_all(self):
        """Clear all selected items and form"""
        self.selected_items = []
        self.update_selected_items(self.selected_items)

        self.pr_var.set("")
        self.description_text.delete('1.0', 'end')
        self.request_date.set_date(datetime.now().date())
        self.required_date.set_date(datetime.now().date())
    
    def validate_form(self):
        """Validate form data"""
        if not self.selected_items:
            return "Please select at least one item."
        
        if not self.pr_var.get().strip():
            return "Please enter PR number."
        
        return None
    
    def submit_pr(self):
        """Submit PR and create card in pending PRs"""
        print("DEBUG: submit_pr called")
        
        # Validate form
        error = self.validate_form()
        if error:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Validation Error", error)
            return
        
        # Create PR data
        pr_data = {
            'pr_number': self.pr_var.get().strip(),
            'department': self.department_name,
            'request_date': self.request_date.get(),
            'required_date': self.required_date.get(),

            'description': self.description_text.get('1.0', 'end-1c').strip(),
            'status': 'Pending Approval',
            'priority': 'Medium',
            'items_count': len(self.selected_items),
            'total_value': 'To be calculated',
            'items': []
        }
        
        # Add items with quantities
        for i, item in enumerate(self.selected_items):
            quantity = 1
            if hasattr(self, 'quantity_vars') and i < len(self.quantity_vars):
                try:
                    quantity = int(self.quantity_vars[i].get())
                except:
                    quantity = 1
            
            pr_data['items'].append({
                'resource_code': item.get('resource_code', ''),
                'item_description': item.get('item_description', ''),
                'unit': item.get('unit', ''),
                'quantity': quantity,
                'unit_price': 0,
                'total_price': 0
            })
        
        print(f"DEBUG: PR data created: {pr_data}")
        
        # Save to pending PRs JSON file directly
        try:
            data_file = f"pending_prs_{self.department_name.lower().replace(' ', '_')}.json"
            
            # Load existing PRs
            existing_prs = []
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    existing_prs = json.load(f)
            
            # Add new PR
            existing_prs.append(pr_data)
            
            # Save back to file
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_prs, f, indent=2, ensure_ascii=False)
            
            print(f"DEBUG: PR saved to {data_file}")
            
            # Show success message
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Success", f"PR {pr_data['pr_number']} created successfully!\n\nStatus: Pending Approval\n\nGo to Purchase → Pending PR'S tab to view your PR card.")
            
            # Clear form
            self.clear_all()
            
        except Exception as e:
            print(f"ERROR saving PR: {e}")
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Failed to save PR: {str(e)}")
    
    def add_items_to_table(self, items):
        """Add selected items to the table format in selected items section"""
        print(f"DEBUG: add_items_to_table called with {len(items)} items")
        
        self.selected_items = items
        
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create table frame
        table_frame = tk.Frame(self.scrollable_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create headers
        headers = ['S.No', 'Resource Code', 'Description', 'Unit', 'Quantity']
        header_frame = tk.Frame(table_frame, bg='#3498db')
        header_frame.pack(fill='x')
        
        for col, header in enumerate(headers):
            tk.Label(header_frame, text=header, font=('Arial', 10, 'bold'),
                    bg='#3498db', fg='white', relief='solid', bd=1).grid(
                    row=0, column=col, sticky='nsew', padx=0, pady=0)
        
        # Configure column weights
        header_frame.grid_columnconfigure(0, weight=0, minsize=50)
        header_frame.grid_columnconfigure(1, weight=1, minsize=120)
        header_frame.grid_columnconfigure(2, weight=3, minsize=250)
        header_frame.grid_columnconfigure(3, weight=0, minsize=80)
        header_frame.grid_columnconfigure(4, weight=0, minsize=80)
        
        # Store quantity variables
        self.quantity_vars = []
        
        # Create rows with editable quantity WITH VALIDATION
        for i, item in enumerate(items, 1):
            row_frame = tk.Frame(table_frame, bg='white')
            row_frame.pack(fill='x')
            
            # S.No
            tk.Label(row_frame, text=str(i), font=('Arial', 9),
                    bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                    row=0, column=0, sticky='nsew', padx=0, pady=0)
            
            # Resource Code
            tk.Label(row_frame, text=item.get('resource_code', 'N/A'), font=('Arial', 9),
                    bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                    row=0, column=1, sticky='nsew', padx=0, pady=0)
            
            # Description
            tk.Label(row_frame, text=item.get('item_description', 'N/A'), font=('Arial', 9),
                    bg='white', fg='#2c3e50', relief='solid', bd=1, wraplength=250).grid(
                    row=0, column=2, sticky='nsew', padx=0, pady=0)
            
            # Unit
            tk.Label(row_frame, text=item.get('unit', 'N/A'), font=('Arial', 9),
                    bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                    row=0, column=3, sticky='nsew', padx=0, pady=0)
            
            # Quantity (Editable Entry WITH VALIDATION)
            qty_var = tk.StringVar(value='0')
            self.quantity_vars.append(qty_var)
            
            qty_entry = tk.Entry(row_frame, textvariable=qty_var, font=('Arial', 9),
                               justify='center', width=8)
            qty_entry.grid(row=0, column=4, sticky='nsew', padx=1, pady=1)
            
            # Add validation with available quantity
            available_qty = item.get('available', 0)
            if available_qty > 0:
                qty_var.trace('w', lambda *args, var=qty_var, aq=available_qty: self.validate_quantity(var, aq))
                qty_entry.bind('<FocusOut>', lambda e, var=qty_var, aq=available_qty: self.validate_quantity(var, aq))
                
                # Add tooltip on hover (positioned below)
                def show_tooltip(event, aq=available_qty):
                    tooltip = tk.Toplevel()
                    tooltip.wm_overrideredirect(True)
                    tooltip.configure(bg='#ffffcc', relief='solid', bd=1)
                    tk.Label(tooltip, text=f"Max Available: {aq}", bg='#ffffcc', font=('Arial', 8)).pack(padx=3, pady=1)
                    x = event.widget.winfo_rootx()
                    y = event.widget.winfo_rooty() + event.widget.winfo_height() + 5
                    tooltip.geometry(f"+{x}+{y}")
                    event.widget.tooltip = tooltip
                
                def hide_tooltip(event):
                    if hasattr(event.widget, 'tooltip'):
                        event.widget.tooltip.destroy()
                        delattr(event.widget, 'tooltip')
                
                qty_entry.bind('<Enter>', show_tooltip)
                qty_entry.bind('<Leave>', hide_tooltip)
            
            # Configure column weights for each row
            row_frame.grid_columnconfigure(0, weight=0, minsize=50)
            row_frame.grid_columnconfigure(1, weight=1, minsize=120)
            row_frame.grid_columnconfigure(2, weight=3, minsize=250)
            row_frame.grid_columnconfigure(3, weight=0, minsize=80)
            row_frame.grid_columnconfigure(4, weight=0, minsize=80)
        
        # Update header count
        self.items_header_label.configure(text=f"Selected Items ({len(items)})")
        
        # Update canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
        print(f"DEBUG: Items table created successfully with {len(items)} items")
    
    def validate_quantity(self, qty_var, available_qty):
        """Validate quantity against available stock"""
        try:
            value = qty_var.get().strip()
            if not value:
                return
            
            requested_qty = float(value)
            
            # Check if quantity exceeds available
            if requested_qty > available_qty:
                # Show warning and auto-correct
                qty_var.set(str(int(available_qty)))
                self.show_warning(f"⚠️ Quantity corrected to maximum available: {int(available_qty)}")
            elif requested_qty < 0:
                # Correct to minimum value
                qty_var.set('0')
                self.show_warning("⚠️ Quantity cannot be negative. Set to 0.")
                
        except ValueError:
            # Invalid input, reset to 0
            qty_var.set('0')
            self.show_warning("⚠️ Invalid quantity. Set to 0.")
    
    def show_warning(self, message):
        """Show warning message briefly"""
        try:
            if hasattr(self, 'warning_label'):
                self.warning_label.destroy()
            
            self.warning_label = tk.Label(self.scrollable_frame, text=message, 
                                        bg='#ffcccc', fg='#cc0000', font=('Arial', 9, 'bold'))
            self.warning_label.pack(pady=2)
            
            # Auto-hide after 3 seconds
            self.scrollable_frame.after(3000, lambda: self.warning_label.destroy() if hasattr(self, 'warning_label') else None)
        except:
            pass