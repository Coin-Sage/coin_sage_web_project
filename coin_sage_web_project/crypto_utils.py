from cryptography.fernet import Fernet
import os


def generate_key():
    return Fernet.generate_key()


def encrypt(data, key):
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data


def decrypt(encrypted_data, key):
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data).decode()
    return decrypted_data


def save_key_to_file(key, filename=".env_key"):
    with open(filename, "wb") as key_file:
        key_file.write(key)


def load_key_from_file(filename=".env_key"):
    if os.path.exists(filename):
        with open(filename, "rb") as key_file:
            key = key_file.read()
            return key
    else:
        raise FileNotFoundError(f"Key file '{filename}' not found.")
