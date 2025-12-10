import tkinter as tk
from tkinter import ttk
from inventory_overview import InventoryOverview

class ViewDetails:
    def __init__(self, parent_frame, department_name, include_inventory=False):
        """
        include_inventory: when True (default) the view builds a two-column layout
        with an InventoryOverview on the left and details on the right. When False,
        it only builds the details panel inside the provided parent_frame. This
        allows other views (like `view_products.py`) to reuse the details UI
        without creating a second InventoryOverview.
        """
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.detail_labels = {}
        self.inventory_overview = None
        self.include_inventory = include_inventory
        # Optional callable to retrieve the currently selected row data from an
        # external InventoryOverview instance: should return a list of cell values
        # or None if nothing is selected.
        self.inventory_source = None
        self.create_page()
    
    def create_page(self):
        # If include_inventory is True, create a two-column layout with the
        # InventoryOverview on the left. Otherwise the provided parent_frame is
        # assumed to be the right-side container for details only.
        if self.include_inventory:
            main_container = tk.Frame(self.parent_frame, bg='#ecf0f1')
            main_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Left side - Inventory table (reduced height)
            left_frame = tk.Frame(main_container, bg='#ecf0f1')
            left_frame.pack(side='left', fill='both', padx=(0, 5))
            # Halve the previous height to make the table much smaller
            left_frame.configure(width=800, height=150)
            left_frame.pack_propagate(False)
            
            self.inventory_overview = InventoryOverview(left_frame, self.department_name)
            self.inventory_overview.set_details_callback(self.update_details)
            
            # Right side - Additional content area
            right_frame = tk.Frame(main_container, bg='#ecf0f1')
            right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        else:
            # Parent frame is already the right-side container
            right_frame = self.parent_frame
        
        # Modern header with gradient-like effect (compact)
        header_frame = tk.Frame(right_frame, bg='#2c3e50', height=48)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="📋 Product Details", font=('Segoe UI', 13, 'bold'),
                bg='#2c3e50', fg='white').pack(side='left', padx=(5, 0))

        # Update button intentionally removed per user request

        # Modern card-style details container (compact)
        details_container = tk.Frame(right_frame, bg='#ffffff', relief='flat')
        # Fixed small height to make the details panel slightly taller
        details_container.configure(height=200)
        details_container.pack(fill='x', expand=False, padx=2, pady=5)
        details_container.pack_propagate(False)

        # Add subtle shadow effect with multiple frames
        shadow_frame = tk.Frame(right_frame, bg='#bdc3c7', height=2)
        shadow_frame.pack(fill='x', padx=7, pady=(0, 3))

        # Details content with minimal styling (short table)
        content_frame = tk.Frame(details_container, bg='#ffffff', padx=6, pady=6)
        content_frame.pack(fill='both', expand=True)

        # Modern field-value pairs in a compact 2-column grid so all fields fit
        fields = [
            ('🏷️ Resource Code', ''),
            ('📝 Item Description', ''),
            ('📏 Unit', ''),
            ('📦 Available Order', ''),
            ('📊 Total Quantity', '')
        ]

        # Column 0: field label, Column 1: value (fills remaining width)
        content_frame.grid_columnconfigure(0, weight=0)
        content_frame.grid_columnconfigure(1, weight=1)

        for i, (field, _) in enumerate(fields):
            field_name = field.split(' ', 1)[1] if ' ' in field else field

            # Slightly larger field label for readability
            lbl = tk.Label(content_frame, text=field, font=('Segoe UI', 10, 'bold'),
                           bg='#ffffff', fg='#34495e', anchor='w')
            lbl.grid(row=i, column=0, sticky='w', padx=(6, 8), pady=2)

            # Slightly larger value font, reduced padding so rows fit
            # For long descriptions, enable wrapping so text moves to next line
            if field_name == 'Item Description':
                val = tk.Label(content_frame, text='Select a row to view details',
                               font=('Segoe UI', 10), bg='#f8f9fa', fg='#6c757d',
                               anchor='nw', justify='left', wraplength=380,
                               padx=6, pady=4, relief='flat', bd=1)
            else:
                val = tk.Label(content_frame, text='Select a row to view details',
                               font=('Segoe UI', 10), bg='#f8f9fa', fg='#6c757d',
                               anchor='w', padx=6, pady=4, relief='flat', bd=1)
            val.grid(row=i, column=1, sticky='ew', padx=(0, 6), pady=2)

            # Ensure rows share available vertical space so content doesn't overflow
            content_frame.grid_rowconfigure(i, weight=1)

            self.detail_labels[field_name] = val

    def set_inventory_source(self, func):
        """Register a callable that returns the currently selected row data.

        The callable should return a list of cell values (same shape as the
        row_data passed to update_details), or None if nothing is selected.
        """
        self.inventory_source = func

    def refresh_details(self):
        """Pull the latest selected-row data from an available inventory source
        and update the details panel."""
        row_data = None

        # Prefer explicit inventory_source if provided
        if callable(self.inventory_source):
            try:
                row_data = self.inventory_source()
            except Exception:
                row_data = None

        # Fallback to internal InventoryOverview (if this instance created it)
        if row_data is None and self.inventory_overview is not None:
            try:
                idx = self.inventory_overview.highlighted_row
                if idx is not None and 0 <= idx < len(self.inventory_overview.cells):
                    row_data = [cell.get() for cell in self.inventory_overview.cells[idx]]
            except Exception:
                row_data = None

        if row_data:
            self.update_details(row_data)
    
    def update_details(self, row_data):
        """Update the details panel with selected row data"""
        field_mapping = {
            'Resource Code': 1,
            'Item Description': 2, 
            'Unit': 3,
            'Available Order': 4,
            'Total Quantity': 5
        }
        
        for field, col_idx in field_mapping.items():
            if field in self.detail_labels and col_idx < len(row_data):
                value = row_data[col_idx].strip() if row_data[col_idx] else 'Not specified'
                self.detail_labels[field].config(text=value, fg='#2c3e50' if value != 'Not specified' else '#95a5a6')