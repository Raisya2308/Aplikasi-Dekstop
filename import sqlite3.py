import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox

class ProductApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛍️ Product Management")
        self.root.geometry("700x500")
        self.root.configure(bg="#f9f9f9")

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#3f51b5", foreground="white")
        style.configure("TLabel", background="#f9f9f9", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)

        # DB Setup
        self.conn = sqlite3.connect('products.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL
        )''')
        self.conn.commit()

        # Form Fields
        form_frame = ttk.Frame(root, padding=10)
        form_frame.pack(fill=tk.X)

        ttk.Label(form_frame, text="📦 Product Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form_frame, text="📝 Description:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.description_entry = tk.Text(form_frame, width=40, height=4, font=("Segoe UI", 10))
        self.description_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form_frame, text="💰 Price:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(form_frame, width=40)
        self.price_entry.grid(row=2, column=1, pady=5)

        # Buttons
        button_frame = ttk.Frame(root, padding=10)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="➕ Add", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Update", command=self.update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.delete_product).pack(side=tk.LEFT, padx=5)

        # Table
        table_frame = ttk.Frame(root, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Description", "Price"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Price", text="Price")

        self.tree.column("ID", width=30, anchor=tk.CENTER)
        self.tree.column("Name", width=150)
        self.tree.column("Description", width=250)
        self.tree.column("Price", width=80, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.tree.bind("<ButtonRelease-1>", self.select_item)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Load data
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute("SELECT * FROM products")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def add_product(self):
        name = self.name_entry.get()
        description = self.description_entry.get("1.0", tk.END).strip()
        price = self.price_entry.get()

        if not name or not price:
            messagebox.showerror("Error", "Name and Price are required.")
            return

        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Invalid price format.")
            return

        self.cursor.execute("INSERT INTO products (name, description, price) VALUES (?, ?, ?)", (name, description, price))
        self.conn.commit()
        self.load_data()
        self.clear_fields()
        messagebox.showinfo("Success", "Product added successfully.")

    def update_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a product to update.")
            return

        item_id = self.tree.item(selected, 'values')[0]
        name = self.name_entry.get()
        description = self.description_entry.get("1.0", tk.END).strip()
        price = self.price_entry.get()

        if not name or not price:
            messagebox.showerror("Error", "Name and Price are required.")
            return

        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Invalid price format.")
            return

        self.cursor.execute("UPDATE products SET name=?, description=?, price=? WHERE id=?", (name, description, price, item_id))
        self.conn.commit()
        self.load_data()
        self.clear_fields()
        messagebox.showinfo("Success", "Product updated successfully.")

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a product to delete.")
            return

        item_id = self.tree.item(selected, 'values')[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this product?")
        if confirm:
            self.cursor.execute("DELETE FROM products WHERE id=?", (item_id,))
            self.conn.commit()
            self.load_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Product deleted successfully.")

    def select_item(self, event):
        selected = self.tree.selection()
        if selected:
            product_id, name, description, price = self.tree.item(selected, 'values')
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)
            self.description_entry.delete("1.0", tk.END)
            self.description_entry.insert("1.0", description)
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, price)

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete("1.0", tk.END)
        self.price_entry.delete(0, tk.END)

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()
