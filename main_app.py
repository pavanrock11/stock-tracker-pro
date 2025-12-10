import tkinter as tk
from tkinter import ttk
from home_page import HomePage
from view_products import ViewProducts
from purchase_request import PurchaseRequest
from material_received import MaterialReceived
from suppliers import Suppliers
from statistics import Statistics

class StockTrackerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Tracker - Department Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#ecf0f1')
        
        self.department_name = "IT Department"  # Can be configured
        self.create_main_interface()
    
    def create_main_interface(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tab frames
        self.home_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.products_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.purchase_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.received_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.suppliers_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.stats_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        
        # Add tabs to notebook
        self.notebook.add(self.home_frame, text="🏠 Home")
        self.notebook.add(self.products_frame, text="📦 Products")
        self.notebook.add(self.purchase_frame, text="🛒 Purchase Request")
        self.notebook.add(self.received_frame, text="📥 Material Received")
        self.notebook.add(self.suppliers_frame, text="🏢 Suppliers")
        self.notebook.add(self.stats_frame, text="📊 Statistics")
        
        # Initialize tab content
        self.home_page = HomePage(self.home_frame, self.department_name)
        self.products_page = ViewProducts(self.products_frame, self.department_name)
        self.purchase_page = PurchaseRequest(self.purchase_frame, self.department_name)
        self.received_page = MaterialReceived(self.received_frame, self.department_name)
        self.suppliers_page = Suppliers(self.suppliers_frame, self.department_name)
        self.stats_page = Statistics(self.stats_frame, self.department_name)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StockTrackerApp()
    app.run()