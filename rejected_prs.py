import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

class RejectedPRs:
    def __init__(self, parent_frame, department_name, pending_prs_callback=None):
        self.parent_frame = parent_frame
        self.department_name = department_name
        self.rejected_file = f"rejected_prs_{department_name.lower().replace(' ', '_')}.json"
        self.pending_prs_callback = pending_prs_callback
    
    def save_rejected_pr(self, pr, reason):
        """Save rejected PR with reason"""
        print(f"DEBUG: Saving rejected PR: {pr.get('pr_number')} with reason: {reason}")
        print(f"DEBUG: Rejected file path: {self.rejected_file}")
        
        # Load existing rejected PRs
        rejected_prs = []
        try:
            if os.path.exists(self.rejected_file):
                with open(self.rejected_file, 'r') as f:
                    rejected_prs = json.load(f)
                print(f"DEBUG: Loaded {len(rejected_prs)} existing rejected PRs")
        except Exception as e:
            print(f"Error loading rejected PRs: {e}")
        
        # Add rejection info
        pr['status'] = 'Rejected'
        pr['rejection_reason'] = reason
        pr['rejection_date'] = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Add to rejected PRs
        rejected_prs.append(pr)
        print(f"DEBUG: Added PR to rejected list. Total rejected PRs: {len(rejected_prs)}")
        
        # Save rejected PRs
        try:
            with open(self.rejected_file, 'w') as f:
                json.dump(rejected_prs, f, indent=2)
            print(f"DEBUG: Successfully saved rejected PRs to {self.rejected_file}")
        except Exception as e:
            print(f"Error saving rejected PRs: {e}")
            import traceback
            traceback.print_exc()
    
    def show_rejected_prs(self):
        """Show rejected PRs in a new window"""
        print(f"DEBUG: Loading rejected PRs from: {self.rejected_file}")
        print(f"DEBUG: File exists: {os.path.exists(self.rejected_file)}")
        
        # Load rejected PRs
        rejected_prs = []
        try:
            if os.path.exists(self.rejected_file):
                with open(self.rejected_file, 'r') as f:
                    rejected_prs = json.load(f)
                print(f"DEBUG: Loaded {len(rejected_prs)} rejected PRs")
            else:
                print("DEBUG: Rejected PRs file does not exist")
        except Exception as e:
            print(f"Error loading rejected PRs: {e}")
            import traceback
            traceback.print_exc()
        
        # Create rejected PRs window
        rejected_window = tk.Toplevel(self.parent_frame)
        rejected_window.title(f"Rejected PRs - {self.department_name}")
        rejected_window.geometry("1000x700")
        rejected_window.configure(bg='#ecf0f1')
        
        # Header
        header_frame = tk.Frame(rejected_window, bg='#e74c3c', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="❌ Rejected Purchase Requests", 
                font=('Segoe UI', 16, 'bold'), bg='#e74c3c', fg='white').pack(pady=15)
        
        # Main content
        if not rejected_prs:
            tk.Label(rejected_window, text="No rejected purchase requests found",
                    font=('Segoe UI', 14), bg='#ecf0f1', fg='#7f8c8d').pack(pady=100)
            return
        
        # Scrollable content
        main_frame = tk.Frame(rejected_window, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame, bg='#ecf0f1', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ecf0f1')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        
        scrollable_frame.bind('<Configure>', 
                             lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Display rejected PRs
        for i, pr in enumerate(rejected_prs):
            self.create_rejected_pr_card(scrollable_frame, pr, i, rejected_window)
    
    def create_rejected_pr_card(self, parent, pr, index, window=None):
        """Create a card for rejected PR"""
        # Main card frame
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.pack(fill='x', padx=10, pady=5)
        
        # Header with PR number and rejection date
        header_frame = tk.Frame(card_frame, bg='#e74c3c', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"📋 {pr.get('pr_number', 'N/A')}", 
                font=('Segoe UI', 12, 'bold'), bg='#e74c3c', fg='white').pack(side='left', padx=10, pady=8)
        
        tk.Label(header_frame, text=f"Rejected: {pr.get('rejection_date', 'N/A')}", 
                font=('Segoe UI', 9, 'bold'), bg='#c0392b', fg='white',
                padx=8, pady=2).pack(side='right', padx=10, pady=8)
        
        # Body with details
        body_frame = tk.Frame(card_frame, bg='white')
        body_frame.pack(fill='x', padx=15, pady=10)
        
        # PR Details row
        details_row = tk.Frame(body_frame, bg='white')
        details_row.pack(fill='x', pady=(0, 10))
        
        tk.Label(details_row, text=f"📅 Request: {pr.get('request_date', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left')
        
        tk.Label(details_row, text=f"⏰ Required: {pr.get('required_date', 'N/A')}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left', padx=(20, 0))
        
        tk.Label(details_row, text=f"📦 Items: {pr.get('items_count', 0)}", 
                font=('Segoe UI', 9), bg='white', fg='#2c3e50').pack(side='left', padx=(20, 0)) 
        
        # Description
        desc_text = pr.get('description', 'No description available')
        if len(desc_text) > 100:
            desc_text = desc_text[:100] + "..."
        
        tk.Label(body_frame, text=f"📝 {desc_text}", 
                font=('Segoe UI', 9), bg='white', fg='#7f8c8d', 
                wraplength=900, justify='left').pack(anchor='w', pady=(0, 10))
        
        # Rejection reason
        reason_frame = tk.LabelFrame(body_frame, text="Rejection Reason", 
                                    font=('Segoe UI', 10, 'bold'), bg='white', fg='#e74c3c')
        reason_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(reason_frame, text=pr.get('rejection_reason', 'No reason provided'), 
                font=('Segoe UI', 10), bg='white', fg='#2c3e50', 
                wraplength=900, justify='left').pack(padx=10, pady=5, anchor='w')
        
        # Action button
        action_frame = tk.Frame(body_frame, bg='white')
        action_frame.pack(fill='x')
        
        tk.Button(action_frame, text="👁️ View Details", bg='#3498db', fg='white',
                 font=('Segoe UI', 9, 'bold'), padx=15, pady=3,
                 command=lambda: self.view_pr_details(pr)).pack(side='left')
        
        tk.Button(action_frame, text="↩️ Undo", bg='#f39c12', fg='white',
                 font=('Segoe UI', 9, 'bold'), padx=15, pady=3,
                 command=lambda: self.undo_rejection(pr, window)).pack(side='right')
    
    def view_pr_details(self, pr):
        """View detailed PR information"""
        # Create popup window for PR details
        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"Rejected PR Details - {pr.get('pr_number', 'N/A')}")
        view_window.geometry("800x600")
        view_window.configure(bg='#ecf0f1')
        
        # Header
        header_frame = tk.Frame(view_window, bg='#e74c3c', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"📋 {pr.get('pr_number', 'N/A')} - Rejected PR Details",
                font=('Segoe UI', 16, 'bold'), bg='#e74c3c', fg='white').pack(pady=15)
        
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
            ("Rejection Date:", pr.get('rejection_date', 'N/A')),
            ("Total Value:", pr.get('total_value', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(info_data):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(info_grid, text=label, font=('Segoe UI', 10, 'bold'),
                    bg='white', fg='#2c3e50').grid(row=row, column=col, sticky='w', padx=(0, 10), pady=5)
            tk.Label(info_grid, text=value, font=('Segoe UI', 10),
                    bg='white', fg='#34495e').grid(row=row, column=col+1, sticky='w', padx=(0, 30), pady=5)
        
        # Rejection reason section
        reason_frame = tk.LabelFrame(main_frame, text="Rejection Reason", font=('Segoe UI', 12, 'bold'),
                                    bg='#ecf0f1', fg='#e74c3c')
        reason_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(reason_frame, text=pr.get('rejection_reason', 'No reason provided'),
                font=('Segoe UI', 11), bg='white', fg='#2c3e50', wraplength=750,
                justify='left').pack(padx=10, pady=10, anchor='w')
        
        # Description
        desc_frame = tk.LabelFrame(main_frame, text="Description", font=('Segoe UI', 12, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50')
        desc_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(desc_frame, text=pr.get('description', 'No description available'),
                font=('Segoe UI', 10), bg='white', fg='#34495e', wraplength=750,
                justify='left').pack(padx=10, pady=10, anchor='w')
        
        # Close button
        button_frame = tk.Frame(view_window, bg='#ecf0f1')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="✖️ Close", bg='#e74c3c', fg='white',
                 font=('Segoe UI', 10, 'bold'), padx=20, pady=5,
                 command=view_window.destroy).pack(side='right')
    
    def undo_rejection(self, pr, window=None):
        """Undo rejection and move PR back to pending"""
        # Confirm undo action
        result = messagebox.askyesno("Undo Rejection", 
                                   f"Are you sure you want to undo the rejection of PR {pr.get('pr_number')}?\n\nThis will move it back to pending status.")
        if not result:
            return
        
        # Remove rejection info and restore to pending status
        pr['status'] = 'Pending Approval'
        if 'rejection_reason' in pr:
            del pr['rejection_reason']
        if 'rejection_date' in pr:
            del pr['rejection_date']
        
        # Remove from rejected PRs file
        try:
            rejected_prs = []
            if os.path.exists(self.rejected_file):
                with open(self.rejected_file, 'r') as f:
                    rejected_prs = json.load(f)
            
            # Remove this PR from rejected list
            rejected_prs = [p for p in rejected_prs if p.get('pr_number') != pr.get('pr_number')]
            
            # Save updated rejected PRs
            with open(self.rejected_file, 'w') as f:
                json.dump(rejected_prs, f, indent=2)
            
            # Add back to pending PRs if callback is available
            if self.pending_prs_callback:
                self.pending_prs_callback(pr)
            
            messagebox.showinfo("Success", f"PR {pr.get('pr_number')} has been moved back to pending status.")
            
            # Close and refresh the rejected PRs window
            if window:
                window.destroy()
            self.show_rejected_prs()
            
        except Exception as e:
            print(f"Error undoing rejection: {e}")
            messagebox.showerror("Error", f"Failed to undo rejection: {str(e)}")