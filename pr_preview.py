import tkinter as tk
from tkinter import ttk

class PRPreview:
    def __init__(self, parent_frame, selected_items, department_name, callback=None):
        self.parent_frame = parent_frame
        self.selected_items = selected_items
        self.department_name = department_name
        self.callback = callback
        self.create_window()
    
    def create_window(self):
        # Create new window
        self.pr_window = tk.Toplevel(self.parent_frame)
        self.pr_window.title(f"Purchase Request Preview - {self.department_name}")
        self.pr_window.geometry("700x500")
        self.pr_window.configure(bg='white')
        
        # Make window modal
        self.pr_window.transient(self.parent_frame.winfo_toplevel())
        self.pr_window.grab_set()
        
        # Main container
        main_container = tk.Frame(self.pr_window)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_container, bg='#ecf0f1')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="Purchase Request Preview", 
                font=('Helvetica', 16, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(side='left', padx=10, pady=10)
        
        tk.Label(header_frame, text=f"Department: {self.department_name}", 
                font=('Helvetica', 12), bg='#ecf0f1', fg='#34495e').pack(side='right', padx=10, pady=10)
        
        # Content area with scrollbar
        content_frame = tk.Frame(main_container, bg='white', relief='solid', bd=1)
        content_frame.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(content_frame, bg='white')
        scrollbar = tk.Scrollbar(content_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        scrollable_frame.bind('<Configure>', configure_scroll_region)
        
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        
        # Create table
        table_frame = tk.Frame(scrollable_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Table headers
        headers = ['S.No', 'Resource Code', 'Item Description', 'Unit']
        header_frame = tk.Frame(table_frame, bg='#3498db')
        header_frame.pack(fill='x')
        
        for col, header in enumerate(headers):
            tk.Label(header_frame, text=header, font=('Arial', 10, 'bold'),
                    bg='#3498db', fg='white', relief='solid', bd=1).grid(
                    row=0, column=col, sticky='nsew', padx=0, pady=0)
        
        # Configure column weights
        header_frame.grid_columnconfigure(0, weight=0, minsize=60)   # S.No
        header_frame.grid_columnconfigure(1, weight=1, minsize=120)  # Resource Code
        header_frame.grid_columnconfigure(2, weight=3, minsize=250)  # Description
        header_frame.grid_columnconfigure(3, weight=0, minsize=80)   # Unit
        
        # Table rows
        for i, item in enumerate(self.selected_items, 1):
            row_frame = tk.Frame(table_frame, bg='white')
            row_frame.pack(fill='x')
            
            # S.No
            tk.Label(row_frame, text=str(i), font=('Arial', 9),
                    bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                    row=0, column=0, sticky='nsew', padx=0, pady=0)
            
            # Resource Code
            tk.Label(row_frame, text=item['resource_code'], font=('Arial', 9),
                    bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                    row=0, column=1, sticky='nsew', padx=0, pady=0)
            
            # Item Description
            tk.Label(row_frame, text=item['item_description'], font=('Arial', 9),
                    bg='white', fg='#2c3e50', relief='solid', bd=1, wraplength=250).grid(
                    row=0, column=2, sticky='nsew', padx=0, pady=0)
            
            # Unit
            tk.Label(row_frame, text=item.get('unit', ''), font=('Arial', 9),
                    bg='white', fg='#2c3e50', relief='solid', bd=1).grid(
                    row=0, column=3, sticky='nsew', padx=0, pady=0)
            
            # Configure column weights for each row
            row_frame.grid_columnconfigure(0, weight=0, minsize=60)
            row_frame.grid_columnconfigure(1, weight=1, minsize=120)
            row_frame.grid_columnconfigure(2, weight=3, minsize=250)
            row_frame.grid_columnconfigure(3, weight=0, minsize=80)
        
        # Action buttons at bottom
        button_frame = tk.Frame(main_container, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Close button
        close_btn = tk.Button(button_frame, text="Close", bg='#95a5a6', fg='white', 
                            font=('Arial', 10, 'bold'), command=self.pr_window.destroy)
        close_btn.pack(side='left', padx=5)
        
        # Next button
        next_btn = tk.Button(button_frame, text="Next", bg='#27ae60', fg='white', 
                              font=('Arial', 10, 'bold'), command=self.submit_pr)
        next_btn.pack(side='right', padx=5)
        
        # Update scroll region
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
        
        # Center the window
        self.pr_window.update_idletasks()
        x = (self.pr_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.pr_window.winfo_screenheight() // 2) - (500 // 2)
        self.pr_window.geometry(f"700x500+{x}+{y}")
    
    def submit_pr(self):
        """Proceed to next step"""
        import tkinter.messagebox as messagebox
        result = messagebox.askyesno("Proceed", 
                                   f"Proceed with {len(self.selected_items)} items?",
                                   parent=self.pr_window)
        if result:
            # Call callback to pass items to PR_rise
            if self.callback:
                self.callback(self.selected_items)
            messagebox.showinfo("Success", "Items added to Purchase Request!", parent=self.pr_window)
            self.pr_window.destroy()