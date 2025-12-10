import tkinter as tk
from tkinter import ttk
from view_details import ViewDetails
from purchase_request import PurchaseRequest
from material_received import MaterialReceived
from suppliers import Suppliers
from statistics import Statistics
from costs import Costs
from trends import Trends
from inventory_overview import InventoryOverview
from home_page import HomePage
from pending_prs import PendingPRs
from lpo_s import LPOSystem
from pending import PendingMaterials
from received import History
from loading_widget import LoadingWidget
import threading

class BaseDepartment:
    def __init__(self, parent_frame, back_callback, department_name):
        self.parent_frame = parent_frame
        self.back_callback = back_callback
        self.department_name = department_name
        
        # Pre-create inventory instance to ensure it's available for highlighting
        self.inventory_instance = None
        
        self.create_page()
    
    def create_page(self):
        # Header section
        header_frame = tk.Frame(self.parent_frame, bg='#34495e', relief='raised', bd=2)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Department title and back button
        title_frame = tk.Frame(header_frame, bg='#34495e')
        title_frame.pack(fill='x', padx=10, pady=2)
        
        tk.Label(title_frame, text=f"{self.department_name} Department", 
                font=('Helvetica', 16, 'bold'), bg='#34495e', fg='#ecf0f1').pack(side='left', pady=2)
        
        tk.Button(title_frame, text="← Back to Home", command=self.back_callback,
                 bg='#e74c3c', fg='white', font=('Helvetica', 10, 'bold'),
                 relief='raised', bd=2, cursor='hand2').pack(side='right')
        
        # Tabs section with dropdown - minimized spacing
        tabs_frame = tk.Frame(self.parent_frame, bg='#2c3e50', height=45)
        tabs_frame.pack(fill='x', pady=(0, 5))
        tabs_frame.pack_propagate(False)
        
        # Left side - main tabs
        main_tabs_frame = tk.Frame(tabs_frame, bg='#2c3e50')
        main_tabs_frame.pack(side='left', padx=10, pady=5)
        
        # Define tabs with sub-tabs
        self.tab_config = {
            "🏠 Home": {
                "subtabs": [], 
                "current": "🏠 Home"
            },
            "📦 Products": {
                "subtabs": ["📋 View Details"], 
                "current": "📦 Products"
            },
            "🛒 Purchase": {
                "subtabs": ["📝 New PR", "📋 Pending PR'S", "✅ LPO"], 
                "current": "🛒 Purchase"
            },
            "📥 Received": {
                "subtabs": ["📦 Pending", "✅ Received", "📋 History"], 
                "current": "📥 Received"
            },
            "🏢 Suppliers": {
                "subtabs": ["👥 Active", "📞 Contacts", "📊 Performance"], 
                "current": "🏢 Suppliers"
            },
            "📊 Stats": {
                "subtabs": ["📈 Reports", "📉 Trends", "💰 Costs"], 
                "current": "📊 Stats"
            }
        }
        
        self.tab_buttons = []
        self.tab_dropdown_buttons = []
        self.active_tab = 0
        
        for i, (tab_key, tab_data) in enumerate(self.tab_config.items()):
            # Create tab container with proper spacing
            tab_container = tk.Frame(main_tabs_frame, bg='#2c3e50')
            tab_container.pack(side='left', padx=8)  # More spacing between tabs
            
            # Create unified tab button with splitter icon integrated
            if tab_data["subtabs"]:
                # Tab with dropdown - include splitter in text
                tab_text = f"{tab_data['current']} ▼"
                btn_width = 16
            else:
                # Simple tab without dropdown
                tab_text = tab_data["current"]
                btn_width = 14
            
            # Enhanced button styling
            btn = tk.Button(tab_container, text=tab_text, width=btn_width, height=1,
                          font=('Segoe UI', 9, 'bold'), 
                          bg='#1abc9c' if i == 0 else '#3498db', fg='white',
                          activebackground='#16a085', activeforeground='white',
                          relief='flat', bd=0, cursor='hand2',
                          padx=8, pady=4,
                          command=lambda idx=i, key=tab_key: self.handle_tab_click(idx, key))
            
            # Add hover effects
            def on_enter(e, button=btn, index=i):
                if index == self.active_tab:
                    button.configure(bg='#16a085')
                else:
                    button.configure(bg='#2980b9')
            
            def on_leave(e, button=btn, index=i):
                if index == self.active_tab:
                    button.configure(bg='#1abc9c')
                else:
                    button.configure(bg='#3498db')
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            btn.pack(pady=2)
            self.tab_buttons.append(btn)
            
            # Store dropdown info for later use
            self.tab_dropdown_buttons.append(tab_data["subtabs"] if tab_data["subtabs"] else None)
        
        # Right side - dropdown menu with minimized spacing
        dropdown_frame = tk.Frame(tabs_frame, bg='#2c3e50')
        dropdown_frame.pack(side='right', padx=10, pady=5)
        
        more_btn = tk.Button(dropdown_frame, text="⋮ More", width=8, height=1,
                           font=('Segoe UI', 9, 'bold'), bg='#e74c3c', fg='white',
                           activebackground='#c0392b', activeforeground='white',
                           relief='flat', bd=0, cursor='hand2', padx=8, pady=4,
                           command=self.show_dropdown_menu)
        
        # Add hover effect to More button
        def more_on_enter(e):
            more_btn.configure(bg='#c0392b')
        
        def more_on_leave(e):
            more_btn.configure(bg='#e74c3c')
        
        more_btn.bind("<Enter>", more_on_enter)
        more_btn.bind("<Leave>", more_on_leave)
        more_btn.pack()
        
        # Content area - maximized height
        self.content_frame = tk.Frame(self.parent_frame, bg='#ecf0f1', relief='sunken', bd=2)
        self.content_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        self.show_welcome()
    
    def show_welcome(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text=f"Welcome to {self.department_name} Department",
                font=('Helvetica', 18, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(pady=80)
        
        tk.Label(self.content_frame, text="Select a tab above to manage department operations",
                font=('Helvetica', 14), bg='#ecf0f1', fg='#7f8c8d').pack(pady=20)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def handle_tab_click(self, tab_index, tab_key):
        """Handle tab click - either switch tab or show dropdown"""
        # Check if tab has subtabs
        if self.tab_config[tab_key]["subtabs"]:
            # Show dropdown for subtabs
            self.show_subtab_dropdown(tab_index, tab_key)
        else:
            # Direct tab switch for tabs without subtabs
            self.switch_tab(tab_index, tab_key)
    
    def switch_tab(self, tab_index, tab_key):
        # Show quick loading indicator
        loader = LoadingWidget(self.content_frame)
        loader.show_loading(f"Loading {tab_key.split()[1]}...")
        
        # Update button colors immediately
        for i, btn in enumerate(self.tab_buttons):
            if i == tab_index:
                btn.configure(bg='#1abc9c', relief='flat')
            else:
                btn.configure(bg='#3498db', relief='flat')
        
        self.active_tab = tab_index
        
        # Map tab key to full names
        tab_mapping = {
            "🏠 Home": "Home Page",
            "📦 Products": "View Products", 
            "🛒 Purchase": "Purchase Request",
            "📥 Received": "Material Received",
            "🏢 Suppliers": "Suppliers",
            "📊 Stats": "Statistics"
        }
        
        # Get current subtab or main tab
        current_display = self.tab_config[tab_key]["current"]
        base_tab = tab_key.split()[0] + " " + tab_key.split()[1]
        full_tab_name = tab_mapping.get(base_tab, "Home Page")
        
        # Load tab immediately, then hide loading
        self.parent_frame.after(50, lambda: [
            self.show_tab(full_tab_name, current_display),
            loader.hide_loading()
        ])
    
    def show_subtab_dropdown(self, tab_index, tab_key):
        """Show dropdown menu with subtabs"""
        subtabs = self.tab_config[tab_key]["subtabs"]
        if not subtabs:
            return
        
        dropdown = tk.Toplevel(self.parent_frame)
        dropdown.wm_overrideredirect(True)
        dropdown.configure(bg='white', relief='solid', bd=1)
        
        # Position dropdown under the tab
        btn = self.tab_buttons[tab_index]
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        dropdown.geometry(f"120x{len(subtabs)*25+10}+{x}+{y}")
        
        for subtab in subtabs:
            btn = tk.Button(dropdown, text=subtab, font=('Helvetica', 9),
                          bg='white', fg='#2c3e50', bd=0, padx=10, pady=3,
                          anchor='w', command=lambda st=subtab: self.select_subtab(dropdown, tab_index, tab_key, st))
            btn.pack(fill='x', padx=2, pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#ecf0f1'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='white'))
        
        # Auto-close dropdown
        def close_dropdown(event=None):
            try:
                dropdown.destroy()
            except:
                pass
        
        dropdown.bind("<FocusOut>", close_dropdown)
        dropdown.focus_set()
    
    def select_subtab(self, dropdown, tab_index, tab_key, subtab):
        """Select a subtab and update the tab display"""
        dropdown.destroy()
        
        # Quick loading without threading
        loader = LoadingWidget(self.content_frame)
        loader.show_loading(f"Loading {subtab.split()[1] if len(subtab.split()) > 1 else subtab}...")
        
        # Update the current subtab in config
        self.tab_config[tab_key]["current"] = subtab
        
        # Update the tab button text with splitter icon
        self.tab_buttons[tab_index].configure(text=f"{subtab} ▼")
        
        # Switch tab immediately
        self.parent_frame.after(30, lambda: [
            self.switch_tab(tab_index, tab_key),
            loader.hide_loading()
        ])
    
    def show_dropdown_menu(self):
        dropdown = tk.Toplevel(self.parent_frame)
        dropdown.wm_overrideredirect(True)
        dropdown.configure(bg='white', relief='solid', bd=1)
        
        # Position dropdown
        x = self.parent_frame.winfo_rootx() + self.parent_frame.winfo_width() - 180
        y = self.parent_frame.winfo_rooty() + 120
        dropdown.geometry(f"160x140+{x}+{y}")
        
        # Menu options
        options = [
            ("📤 Export Data", self.export_department_data),
            ("📥 Import Data", self.import_department_data),
            ("⚙️ Settings", self.show_department_settings),
            ("🔄 Refresh All", self.refresh_all_data),
            ("📋 Reports", self.show_reports)
        ]
        
        for text, command in options:
            btn = tk.Button(dropdown, text=text, font=('Helvetica', 9),
                          bg='white', fg='#2c3e50', bd=0, padx=10, pady=4,
                          anchor='w', command=lambda cmd=command: self.execute_dropdown_action(dropdown, cmd))
            btn.pack(fill='x', padx=3, pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#ecf0f1'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='white'))
        
        # Auto-close dropdown
        dropdown.bind("<FocusOut>", lambda e: dropdown.destroy())
        dropdown.focus_set()
    
    def execute_dropdown_action(self, dropdown, command):
        dropdown.destroy()
        command()
    
    # Dropdown action methods
    def export_department_data(self):
        print(f"Exporting {self.department_name} department data...")
    
    def import_department_data(self):
        print(f"Importing data to {self.department_name} department...")
    
    def show_department_settings(self):
        print(f"Opening {self.department_name} department settings...")
    
    def refresh_all_data(self):
        print(f"Refreshing all {self.department_name} department data...")
    
    def show_reports(self):
        print(f"Showing {self.department_name} department reports...")
    
    def show_tab(self, tab_name, current_subtab=None):
        self.clear_content()
        
        # Handle specific subtabs
        if current_subtab == "📋 Inventory":
            # Show InventoryOverview for Inventory subtab
            self.inventory_instance = InventoryOverview(self.content_frame, self.department_name)
            return
        elif current_subtab == "📋 View Details":
            # Show ViewDetails for View Details subtab
            ViewDetails(self.content_frame, self.department_name, include_inventory=True)
            return
        elif current_subtab == "📋 Pending PR'S":
            # Show PendingPRs for Pending PR'S subtab
            PendingPRs(self.content_frame, self.department_name)
            return
        elif current_subtab == "✅ LPO":
            # Show LPO System for LPO subtab
            LPOSystem(self.content_frame, self.department_name)
            return
        elif current_subtab == "💰 Costs":
            # Show Costs management
            Costs(self.content_frame, self.department_name)
            return
        elif current_subtab == "📉 Trends":
            # Show Trends
            Trends(self.content_frame, self.department_name)
            return
        elif current_subtab == "📈 Reports":
            # Show Statistics with specific subtab
            Statistics(self.content_frame, self.department_name, current_subtab)
            return
        elif current_subtab == "📦 Pending":
            # Show Pending Materials for Pending subtab under Received
            PendingMaterials(self.content_frame, self.department_name)
            return
        
        tab_classes = {
            "Home Page": HomePage,
            # Use ViewDetails with embedded inventory for the "View Products" tab
            "View Products": lambda frame, dept: ViewDetails(frame, dept, include_inventory=True),
            "Purchase Request": PurchaseRequest,
            "Material Received": MaterialReceived,
            "Suppliers": Suppliers,
            "Statistics": lambda frame, dept: Statistics(frame, dept, "📈 Reports")
        }
        
        # Handle Purchase subtabs
        if tab_name == "Purchase Request" and current_subtab == "📝 New PR":
            PurchaseRequest(self.content_frame, self.department_name)
            return
        
        if tab_name in tab_classes:
            # Create the main tab content
            tab_instance = tab_classes[tab_name](self.content_frame, self.department_name)
            
            # If there's a current subtab, show subtab info
            if current_subtab and current_subtab != tab_name and current_subtab != "📋 Inventory":
                info_frame = tk.Frame(self.content_frame, bg='#3498db', height=30)
                info_frame.pack(fill='x', pady=(0, 5))
                info_frame.pack_propagate(False)
                
                tk.Label(info_frame, text=f"Current View: {current_subtab}", 
                        font=('Helvetica', 10, 'bold'), bg='#3498db', fg='white').pack(pady=5)

class ElectricalDepartment(BaseDepartment):
    def __init__(self, parent_frame, back_callback):
        super().__init__(parent_frame, back_callback, "Electrical")

class PlumbingDepartment(BaseDepartment):
    def __init__(self, parent_frame, back_callback):
        super().__init__(parent_frame, back_callback, "Plumbing")

class DuctingDepartment(BaseDepartment):
    def __init__(self, parent_frame, back_callback):
        super().__init__(parent_frame, back_callback, "Ducting")

class FirefightingDepartment(BaseDepartment):
    def __init__(self, parent_frame, back_callback):
        super().__init__(parent_frame, back_callback, "Firefighting")

class FireAlarmDepartment(BaseDepartment):
    def __init__(self, parent_frame, back_callback):
        super().__init__(parent_frame, back_callback, "Fire Alarm")