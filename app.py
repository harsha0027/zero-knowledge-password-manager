from cryptography.fernet import Fernet
import os

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
    print(f"Password for {service} added successfully.")

# View stored passwords
def view_passwords(key):
    if not os.path.exists("passwords.txt"):
        print("No passwords stored yet.")
        return

    with open("passwords.txt", "r") as file:
        for line in file:
            service, username, encrypted_password = line.strip().split(",")
            decrypted_password = decrypt_password(encrypted_password, key)
            print(f"Service: {service}, Username: {username}, Password: {decrypted_password}")

# Delete a password from the manager
def delete_password(service):
    if not os.path.exists("passwords.txt"):
        print("No passwords stored yet.")
        return

    with open("passwords.txt", "r") as file:
        lines = file.readlines()

    with open("passwords.txt", "w") as file:
        deleted = False
        for line in lines:
            if not line.startswith(service + ","):
                file.write(line)
            else:
                deleted = True

    if deleted:
        print(f"Password for {service} deleted successfully.")
    else:
        print(f"No password found for {service}.")

# Main menu
def main():
    key = load_key()

    while True:
        print("\nPassword Manager")
        print("1. Add Password")
        print("2. View Passwords")
        print("3. Delete Password")
        print("4. Exit")

        choice = input("Choose an option: ")
        if choice == "1":
            service = input("Enter the service name: ")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            add_password(service, username, password, key)
        elif choice == "2":
            view_passwords(key)
        elif choice == "3":
            service = input("Enter the service name to delete: ")
            delete_password(service)
        elif choice == "4":
            print("Exiting Password Manager. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
