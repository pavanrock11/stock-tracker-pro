import tkinter as tk
from tkinter import ttk
import json
import os
from departments import ElectricalDepartment, PlumbingDepartment, DuctingDepartment, FirefightingDepartment, FireAlarmDepartment, BaseDepartment

class MainPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Tracker Pro")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Load custom departments
        self.load_custom_departments()
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.style.configure('Title.TLabel', background='#2c3e50', foreground='#ecf0f1', font=('Helvetica', 24, 'bold'))
        self.style.configure('Subtitle.TLabel', background='#2c3e50', foreground='#bdc3c7', font=('Helvetica', 14))
        self.style.configure('Dept.TButton', font=('Helvetica', 12, 'bold'), padding=15)
        self.style.map('Dept.TButton', background=[('active', '#3498db'), ('!active', '#34495e')], 
                      foreground=[('active', 'white'), ('!active', '#ecf0f1')])
        
        self.main_frame = tk.Frame(root, bg='#2c3e50')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.show_home_page()
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_home_page(self):
        self.clear_frame()
        
        # Header section
        header_frame = tk.Frame(self.main_frame, bg='#34495e', relief='raised', bd=2)
        header_frame.pack(fill='x', pady=(0, 30))
        
        ttk.Label(header_frame, text="🏢 STOCK TRACKER PRO", style='Title.TLabel').pack(pady=20)
        ttk.Label(header_frame, text="Professional Inventory Management System", style='Subtitle.TLabel').pack(pady=(0, 20))
        
        # Content section
        content_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        content_frame.pack(expand=True, fill='both')
        
        ttk.Label(content_frame, text="Select Department", style='Subtitle.TLabel').pack(pady=(20, 30))
        
        # Buttons grid with scrollbar
        canvas_frame = tk.Frame(content_frame, bg='#2c3e50')
        canvas_frame.pack(expand=True, fill='both')
        
        canvas = tk.Canvas(canvas_frame, bg='#2c3e50', highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        button_frame = tk.Frame(canvas, bg='#2c3e50')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window((0, 0), window=button_frame, anchor='nw')
        
        button_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Default departments
        departments = [
            ("⚡ Electrical", "#e74c3c"),
            ("🔧 Plumbing", "#3498db"), 
            ("🌪️ Ducting", "#f39c12"),
            ("🚒 Firefighting", "#e67e22"),
            ("🚨 Fire Alarm", "#9b59b6")
        ]
        
        # Add custom departments
        departments.extend(self.custom_departments)
        
        # Calculate columns (max 6 per column)
        max_per_column = 6
        num_columns = (len(departments) + max_per_column) // max_per_column
        
        # Create column frames
        columns = []
        for col in range(num_columns):
            col_frame = tk.Frame(button_frame, bg='#2c3e50')
            col_frame.grid(row=0, column=col, padx=20, sticky='n')
            columns.append(col_frame)
        
        # Default department names (cannot be deleted)
        default_depts = ["Electrical", "Plumbing", "Ducting", "Firefighting", "Fire Alarm"]
        
        # Distribute departments across columns
        for i, (dept_name, color) in enumerate(departments):
            col_index = i // max_per_column
            dept_clean = dept_name.split(' ', 1)[1]
            is_custom = dept_clean not in default_depts
            
            btn = tk.Button(columns[col_index], text=dept_name, width=25, height=2,
                          font=('Helvetica', 12, 'bold'), bg=color, fg='white',
                          activebackground='#2c3e50', activeforeground='white',
                          relief='raised', bd=3, cursor='hand2',
                          command=lambda d=dept_clean: self.show_department(d))
            btn.pack(pady=8, padx=10)
            
            # Add right-click menu only for custom departments
            if is_custom:
                btn.bind('<Button-3>', lambda e, dn=dept_name, dc=dept_clean: self.show_delete_menu(e, dn, dc))
        
        # Add Department button in last column
        last_col_index = len(departments) // max_per_column
        if last_col_index >= len(columns):
            col_frame = tk.Frame(button_frame, bg='#2c3e50')
            col_frame.grid(row=0, column=last_col_index, padx=20, sticky='n')
            columns.append(col_frame)
        
        add_btn = tk.Button(columns[last_col_index], text="➕ Add Department", width=25, height=2,
                          font=('Helvetica', 12, 'bold'), bg='#27ae60', fg='white',
                          activebackground='#2c3e50', activeforeground='white',
                          relief='raised', bd=3, cursor='hand2',
                          command=self.add_department)
        add_btn.pack(pady=15, padx=10)
    
    def show_department(self, department):
        self.clear_frame()
        
        department_classes = {
            "Electrical": ElectricalDepartment,
            "Plumbing": PlumbingDepartment,
            "Ducting": DuctingDepartment,
            "Firefighting": FirefightingDepartment,
            "Fire Alarm": FireAlarmDepartment
        }
        
        if department in department_classes:
            department_classes[department](self.main_frame, self.show_home_page)
        else:
            # Use BaseDepartment for custom departments
            BaseDepartment(self.main_frame, self.show_home_page, department)
    
    def add_department(self):
        """Add a new department"""
        from tkinter import simpledialog, messagebox
        
        # Get department name
        dept_name = simpledialog.askstring("Add Department", "Enter department name:")
        if not dept_name:
            return
        
        dept_name = dept_name.strip().title()
        if not dept_name:
            return
        
        # Check if department already exists
        existing_depts = ["Electrical", "Plumbing", "Ducting", "Firefighting", "Fire Alarm"]
        custom_dept_names = [dept[0].split(' ', 1)[1] for dept in self.custom_departments]
        
        if dept_name in existing_depts or dept_name in custom_dept_names:
            messagebox.showerror("Error", "Department already exists!")
            return
        
        # Add to custom departments
        emoji = "🏢"  # Default emoji for custom departments
        color = "#8e44ad"  # Default color for custom departments
        
        new_dept = (f"{emoji} {dept_name}", color)
        self.custom_departments.append(new_dept)
        
        # Save to file
        self.save_custom_departments()
        
        # Refresh the page
        self.show_home_page()
        
        messagebox.showinfo("Success", f"Department '{dept_name}' added successfully!")
    
    def load_custom_departments(self):
        """Load custom departments from file"""
        try:
            if os.path.exists('custom_departments.json'):
                with open('custom_departments.json', 'r', encoding='utf-8') as f:
                    self.custom_departments = json.load(f)
            else:
                self.custom_departments = []
        except Exception:
            self.custom_departments = []
    
    def save_custom_departments(self):
        """Save custom departments to file"""
        try:
            with open('custom_departments.json', 'w', encoding='utf-8') as f:
                json.dump(self.custom_departments, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving custom departments: {e}")
    
    def show_delete_menu(self, event, dept_name, dept_clean):
        """Show right-click menu to delete custom department"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"🗑️ Delete {dept_clean}", 
                        command=lambda: self.delete_department(dept_name))
        menu.post(event.x_root, event.y_root)
    
    def delete_department(self, dept_name):
        """Delete a custom department"""
        from tkinter import messagebox
        
        result = messagebox.askyesno("Confirm Delete", 
                                    f"Delete department '{dept_name.split(' ', 1)[1]}'?\n\nThis will remove all associated data.")
        if result:
            # Remove from custom departments
            self.custom_departments = [d for d in self.custom_departments if d[0] != dept_name]
            
            # Save to file
            self.save_custom_departments()
            
            # Refresh the page
            self.show_home_page()
            
            messagebox.showinfo("Success", "Department deleted successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(True, True)  # Allow resizing and maximize
    app = MainPage(root)
    root.mainloop()