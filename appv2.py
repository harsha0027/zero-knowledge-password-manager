from cryptography.fernet import Fernet
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

# Generate a key (only once, and store it securely)
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Load the key from the key file
def load_key():
    if not os.path.exists("key.key"):
        print("Key not found! Generating a new key.")
        generate_key()
    with open("key.key", "rb") as key_file:
        return key_file.read()

# Encrypt a password
def encrypt_password(password, key):
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

# Decrypt a password
def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

# Add a password to the manager
def add_password(service, username, password, key):
    encrypted_password = encrypt_password(password, key)
    with open("passwords.txt", "a") as file:
        file.write(f"{service},{username},{encrypted_password}\n")

# View stored passwords
def view_passwords(key):
    if not os.path.exists("passwords.txt"):
        return "No passwords stored yet."

    with open("passwords.txt", "r") as file:
        passwords = []
        for line in file:
            service, username, encrypted_password = line.strip().split(",")
            decrypted_password = decrypt_password(encrypted_password, key)
            passwords.append(f"Service: {service}, Username: {username}, Password: {decrypted_password}")
    return "\n".join(passwords)

# Delete a password from the manager
def delete_password(service):
    if not os.path.exists("passwords.txt"):
        return False

    with open("passwords.txt", "r") as file:
        lines = file.readlines()

    with open("passwords.txt", "w") as file:
        deleted = False
        for line in lines:
            if not line.startswith(service + ","):
                file.write(line)
            else:
                deleted = True
    return deleted

# GUI Implementation
def main_gui():
    key = load_key()

    def add_password_gui():
        service = simpledialog.askstring("Add Password", "Enter the service name:")
        if not service:
            return
        username = simpledialog.askstring("Add Password", "Enter the username:")
        if not username:
            return
        password = simpledialog.askstring("Add Password", "Enter the password:", show='*')
        if not password:
            return

        add_password(service, username, password, key)
        messagebox.showinfo("Success", f"Password for {service} added successfully.")

    def view_passwords_gui():
        passwords = view_passwords(key)
        if not passwords:
            messagebox.showinfo("View Passwords", "No passwords stored yet.")
        else:
            top = tk.Toplevel(root)
            top.title("Stored Passwords")
            text = tk.Text(top, wrap=tk.WORD, width=50, height=20)
            text.insert(tk.END, passwords)
            text.config(state=tk.DISABLED)
            text.pack()

    def delete_password_gui():
        service = simpledialog.askstring("Delete Password", "Enter the service name to delete:")
        if not service:
            return

        if delete_password(service):
            messagebox.showinfo("Success", f"Password for {service} deleted successfully.")
        else:
            messagebox.showerror("Error", f"No password found for {service}.")

    # Main window
    root = tk.Tk()
    root.title("Password Manager")

    tk.Label(root, text="Password Manager", font=("Helvetica", 16)).pack(pady=10)

    tk.Button(root, text="Add Password", command=add_password_gui, width=20).pack(pady=5)
    tk.Button(root, text="View Passwords", command=view_passwords_gui, width=20).pack(pady=5)
    tk.Button(root, text="Delete Password", command=delete_password_gui, width=20).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit, width=20).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
