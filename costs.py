import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class Costs:
    def __init__(self, parent_frame, department_name):
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.create_page()
    
    def create_page(self):
        # Header
        header_frame = tk.Frame(self.parent_frame, bg='#9b59b6', height=60)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="💰 Cost Management",
                font=('Segoe UI', 16, 'bold'), bg='#9b59b6', fg='white').pack(pady=15)
        
        # Main container - increased size
        main_container = tk.Frame(self.parent_frame, bg='#ecf0f1')
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Search section
        search_frame = tk.Frame(main_container, bg='#ecf0f1', height=50)
        search_frame.pack(fill='x', pady=(0, 10))
        search_frame.pack_propagate(False)
        
        tk.Label(search_frame, text="🔍 Search LPO:", font=('Segoe UI', 12, 'bold'),
                bg='#ecf0f1', fg='#2c3e50').pack(side='left', padx=10, pady=12)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 11),
                               width=30, relief='solid', bd=1)
        search_entry.pack(side='left', padx=5, pady=12)
        search_entry.bind('<KeyRelease>', self.filter_lpos)
        
        tk.Button(search_frame, text="Clear", command=self.clear_search,
                 bg='#95a5a6', fg='white', font=('Segoe UI', 9, 'bold')).pack(side='left', padx=5, pady=12)
        
        tk.Button(search_frame, text="🔄 Refresh", command=self.refresh_data,
                 bg='#3498db', fg='white', font=('Segoe UI', 9, 'bold')).pack(side='left', padx=5, pady=12)
        
        tk.Button(search_frame, text="🔄 Revert", command=self.show_archived_lpos,
                 bg='#e67e22', fg='white', font=('Segoe UI', 9, 'bold')).pack(side='left', padx=5, pady=12)
                
        # LPO list container - increased size
        lpo_container = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        lpo_container.pack(fill='both', expand=True)
        
        # Canvas for scrolling - vertical only
        canvas = tk.Canvas(lpo_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(lpo_container, orient='vertical', command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # Configure scroll region
        self.scrollable_frame.bind('<Configure>', 
                                  lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Store all LPOs for filtering
        self.all_lpos = []
        
        # Load and display LPOs
        self.load_lpos_for_costing()
    
    def load_lpos_for_costing(self):
        """Load real LPO data for cost management - separate copy"""
        try:
            # Use separate file for costs but copy real LPO data
            archive_file = f"archived_lpos_{self.department_name.lower().replace(' ', '_')}.json"
            main_lpo_file = f"lpo_{self.department_name.lower().replace(' ', '_')}.json"
            
            # Always refresh from main LPO file to get latest data
            if os.path.exists(main_lpo_file):
                with open(main_lpo_file, 'r', encoding='utf-8') as f:
                    main_lpos = json.load(f)
                
                # Load archived LPOs to exclude them
                archived_lpos = []
                if os.path.exists(archive_file):
                    try:
                        with open(archive_file, 'r', encoding='utf-8') as f:
                            archived_lpos = json.load(f)
                    except:
                        archived_lpos = []
                
                # Get archived LPO IDs
                archived_ids = [lpo.get('lpo_number') for lpo in archived_lpos]
                
                # Filter to show only non-archived LPOs
                lpos = [lpo for lpo in main_lpos if lpo.get('lpo_number') not in archived_ids]
            else:
                # No main LPO file exists
                lpos = []
            
            # Update all_lpos
            self.all_lpos = lpos
            
            # Clear existing display
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Display LPOs or show empty message
            if not lpos:
                tk.Label(self.scrollable_frame, text="No cost items available",
                        font=('Segoe UI', 14), bg='white', fg='#7f8c8d').pack(pady=50)
            else:
                for lpo in lpos:
                    self.create_lpo_cost_card(lpo)
                
        except Exception as e:
            tk.Label(self.scrollable_frame, text=f"Error loading LPOs: {str(e)}",
                    font=('Segoe UI', 12), bg='white', fg='#e74c3c').pack(pady=20)
    
    def create_lpo_cost_card(self, lpo):
        """Create a card for each LPO with items for cost entry"""
        # Main card frame - vertical layout
        card_frame = tk.Frame(self.scrollable_frame, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', padx=10, pady=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg='#16a085', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        lpo_number = lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')
        tk.Label(header_frame, text=f"📋 {lpo_number} - Unit Price Entry",
                font=('Segoe UI', 12, 'bold'), bg='#16a085', fg='white').pack(side='left', padx=10, pady=8)
        
        # Items table with proper layout
        table_frame = tk.Frame(card_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create table with fixed column widths
        columns = ['Resource Code', 'Item Description', 'Unit', 'Unit Price']
        col_widths = [20, 50, 12, 15]  # Character widths for each column
        
        # Headers with consistent layout
        header_row = tk.Frame(table_frame, bg='#34495e')
        header_row.pack(fill='x', pady=(0, 2))
        
        # Resource Code header
        tk.Label(header_row, text='Resource Code', font=('Segoe UI', 10, 'bold'),
                bg='#34495e', fg='white', width=col_widths[0], anchor='center').pack(side='left', padx=1, pady=2)
        
        # Item Description header - expandable
        tk.Label(header_row, text='Item Description', font=('Segoe UI', 10, 'bold'),
                bg='#34495e', fg='white', anchor='center').pack(side='left', fill='x', expand=True, padx=1, pady=2)
        
        # Unit header
        tk.Label(header_row, text='Unit', font=('Segoe UI', 10, 'bold'),
                bg='#34495e', fg='white', width=col_widths[2], anchor='center').pack(side='left', padx=1, pady=2)
        
        # Unit Price header
        tk.Label(header_row, text='Unit Price', font=('Segoe UI', 10, 'bold'),
                bg='#34495e', fg='white', width=col_widths[3], anchor='center').pack(side='left', padx=1, pady=2)
        
        # Items rows with consistent layout
        items = lpo.get('items', [])
        if not hasattr(self, 'price_entries'):
            self.price_entries = {}
        
        for i, item in enumerate(items):
            row_frame = tk.Frame(table_frame, bg='white' if i % 2 == 0 else '#f8f9fa')
            row_frame.pack(fill='x', pady=1)
            
            # Resource Code
            tk.Label(row_frame, text=item.get('resource_code', ''), font=('Segoe UI', 9),
                    bg=row_frame['bg'], fg='#2c3e50', width=col_widths[0], anchor='center').pack(side='left', padx=1)
            
            # Item Description - with proper width
            desc_text = item.get('item_description', '')
            desc_label = tk.Label(row_frame, text=desc_text, font=('Segoe UI', 9),
                                bg=row_frame['bg'], fg='#2c3e50', anchor='w', width=60)
            desc_label.pack(side='left', padx=1)
            
            # Unit - Editable dropdown
            unit_var = tk.StringVar(value=item.get('unit', 'Nos'))
            unit_combo = ttk.Combobox(row_frame, textvariable=unit_var, font=('Segoe UI', 9),
                                    width=col_widths[2]-2, justify='center', state='readonly')
            unit_combo['values'] = ('Nos', 'Mtr', 'Gln', 'Ctn', 'Roll', 'Box', 'Kg', 'Ltr', 'Pcs', 'Set')
            unit_combo.pack(side='left', padx=1, pady=1)
            
            # Unit Price Entry
            price_var = tk.StringVar()
            price_entry = tk.Entry(row_frame, textvariable=price_var, font=('Segoe UI', 9),
                                  justify='center', width=col_widths[3], relief='solid', bd=1)
            price_entry.pack(side='left', padx=1, pady=1)
            
            # Store references with unique key
            item_key = f"{lpo_number}_{i}"
            self.price_entries[item_key] = {
                'price_var': price_var,
                'unit_var': unit_var,
                'item': item
            }
            print(f"DEBUG: Stored price entry for {item_key}")
        
        # Action buttons
        action_frame = tk.Frame(card_frame, bg='white')
        action_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Button(action_frame, text="💾 Save Prices", bg='#27ae60', fg='white',
                 font=('Segoe UI', 9, 'bold'), padx=15, pady=5,
                 command=lambda: self.save_lpo_prices(lpo)).pack(side='right', padx=5)
    

    
    def save_lpo_prices(self, lpo):
        """Save unit prices for LPO items"""
        try:
            lpo_number = lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')
            
            # Update items with prices and units
            updated_items = []
            for i, item in enumerate(lpo.get('items', [])):
                item_key = f"{lpo_number}_{i}"
                print(f"DEBUG: Looking for price entry {item_key}")
                if item_key in self.price_entries:
                    price = self.price_entries[item_key]['price_var'].get().strip()
                    unit = self.price_entries[item_key]['unit_var'].get()
                    print(f"DEBUG: Found price '{price}' for {item_key}")
                    item['unit_price'] = price if price else None
                    item['unit'] = unit
                else:
                    print(f"DEBUG: No price entry found for {item_key}")
                    item['unit_price'] = None
                updated_items.append(item)
            
            # Update LPO with prices
            lpo['items'] = updated_items
            lpo['pricing_updated'] = True
            
            # Archive LPO
            self.archive_lpo(lpo)
            
            # Refresh display to remove archived LPO
            self.load_lpos_for_costing()
            
            # Update trends data
            from trends import Trends
            trends_updated = 0
            for i, item in enumerate(updated_items):
                price = item.get('unit_price', '').strip()
                if price and price != '':
                    print(f"DEBUG: Updating trend for {item.get('resource_code')} with price {price}")
                    success = Trends.update_price_trend(
                        self.department_name,
                        item.get('resource_code', ''),
                        item.get('item_description', ''),
                        item.get('unit', ''),
                        price
                    )
                    if success:
                        trends_updated += 1
                else:
                    print(f"DEBUG: Skipping trend update for {item.get('resource_code')} - no price entered")
            
            print(f"DEBUG: Updated {trends_updated} items in trends")
            
            # Show revert section immediately after saving (no blocking messagebox)
            self.show_archived_lpos()
            
            # Show success message after revert window is displayed
            if trends_updated > 0:
                print(f"Success: Prices saved for {lpo_number}, {trends_updated} items added to price trends")
            else:
                print(f"Success: Prices saved for {lpo_number}, no prices entered for trend tracking")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save prices: {str(e)}")
    
    def filter_lpos(self, event=None):
        """Filter LPOs based on search text"""
        search_text = self.search_var.get().lower().strip()
        
        # Clear current display
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Show filtered LPOs
        if not search_text:
            # Show all LPOs if no search text
            for lpo in self.all_lpos:
                self.create_lpo_cost_card(lpo)
        else:
            # Filter LPOs by LPO number
            found_lpos = []
            for lpo in self.all_lpos:
                lpo_number = lpo.get('manual_lpo_number') or lpo.get('lpo_number', '')
                if search_text in lpo_number.lower():
                    found_lpos.append(lpo)
            
            if found_lpos:
                for lpo in found_lpos:
                    self.create_lpo_cost_card(lpo)
            else:
                tk.Label(self.scrollable_frame, text=f"No LPOs found matching '{self.search_var.get()}'",
                        font=('Segoe UI', 12), bg='white', fg='#e74c3c').pack(pady=30)
    
    def clear_search(self):
        """Clear search and show all LPOs"""
        self.search_var.set('')
        self.filter_lpos()
    
    def refresh_data(self):
        """Refresh LPO data from main file"""
        self.load_lpos_for_costing()
    
    def navigate_to_trends(self):
        """Navigate to trends tab after saving prices"""
        try:
            result = messagebox.askquestion("Navigate to Trends", 
                                          "Prices saved successfully!\n\nWould you like to view price trends now?",
                                          icon='question')
            if result == 'yes':
                print("Navigating to trends tab...")
                
        except Exception as e:
            print(f"Navigation error: {e}")
    
    def archive_lpo(self, lpo):
        """Move LPO to archived file after pricing"""
        try:
            archive_file = f"archived_lpos_{self.department_name.lower().replace(' ', '_')}.json"
            
            # Load existing archived LPOs
            if os.path.exists(archive_file):
                with open(archive_file, 'r', encoding='utf-8') as f:
                    archived_lpos = json.load(f)
            else:
                archived_lpos = []
            
            # Add current LPO to archive
            archived_lpos.append(lpo)
            
            # Save archived LPOs
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archived_lpos, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error archiving LPO: {e}")
    
    def show_archived_lpos(self):
        """Show archived LPOs with revert option"""
        try:
            archive_file = f"archived_lpos_{self.department_name.lower().replace(' ', '_')}.json"
            
            if not os.path.exists(archive_file):
                messagebox.showinfo("No Archived LPOs", "No archived LPOs found.")
                return
            
            with open(archive_file, 'r', encoding='utf-8') as f:
                archived_lpos = json.load(f)
            
            if not archived_lpos:
                messagebox.showinfo("No Archived LPOs", "No archived LPOs found.")
                return
            
            # Create revert window
            revert_window = tk.Toplevel(self.parent_frame)
            revert_window.title("Archived LPOs - Revert Options")
            revert_window.geometry("600x400")
            revert_window.configure(bg='#ecf0f1')
            
            # Header
            header_frame = tk.Frame(revert_window, bg='#e67e22', height=50)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text="🔄 Archived LPOs (Priced Items)",
                    font=('Segoe UI', 14, 'bold'), bg='#e67e22', fg='white').pack(pady=12)
            
            # List frame
            list_frame = tk.Frame(revert_window, bg='white')
            list_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Canvas for scrolling
            canvas = tk.Canvas(list_frame, bg='white')
            scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')
            canvas.pack(side='left', fill='both', expand=True)
            canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            
            scrollable_frame.bind('<Configure>', 
                                 lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            
            # Display archived LPOs
            for i, lpo in enumerate(archived_lpos):
                lpo_frame = tk.Frame(scrollable_frame, bg='#f8f9fa', relief='solid', bd=1)
                lpo_frame.pack(fill='x', padx=5, pady=2)
                
                lpo_number = lpo.get('manual_lpo_number') or lpo.get('lpo_number', 'N/A')
                items_count = len(lpo.get('items', []))
                
                tk.Label(lpo_frame, text=f"📋 {lpo_number} ({items_count} items)",
                        font=('Segoe UI', 11, 'bold'), bg='#f8f9fa', fg='#2c3e50').pack(side='left', padx=10, pady=8)
                
                tk.Button(lpo_frame, text="↩️ Revert", bg='#27ae60', fg='white',
                         font=('Segoe UI', 9, 'bold'), padx=10, pady=2,
                         command=lambda idx=i: self.revert_lpo(idx, revert_window)).pack(side='right', padx=10, pady=5)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load archived LPOs: {str(e)}")
    
    def revert_lpo(self, lpo_index, revert_window):
        """Revert an archived LPO back to active list"""
        try:
            archive_file = f"archived_lpos_{self.department_name.lower().replace(' ', '_')}.json"
            
            # Load archived LPOs
            with open(archive_file, 'r', encoding='utf-8') as f:
                archived_lpos = json.load(f)
            
            # Get the LPO to revert
            lpo_to_revert = archived_lpos[lpo_index]
            
            # Remove pricing data to make it available for re-pricing
            for item in lpo_to_revert.get('items', []):
                item.pop('unit_price', None)
            lpo_to_revert['pricing_updated'] = False
            
            # Remove from archived list
            archived_lpos.pop(lpo_index)
            
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archived_lpos, f, indent=2, ensure_ascii=False)
            
            # Refresh display
            self.load_lpos_for_costing()
            
            messagebox.showinfo("Success", f"LPO {lpo_to_revert.get('manual_lpo_number') or lpo_to_revert.get('lpo_number', 'N/A')} reverted successfully!")
            
            # Close revert window
            revert_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to revert LPO: {str(e)}")
