from cryptography.fernet import Fernet


def load_key_from_file(key_path=".env.key"):
    with open(key_path, "rb") as key_file:
        return key_file.read()


def decrypt_data(encrypted_data, key):
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode()


# Load the key
key = load_key_from_file()

# Read the encrypted content
with open(".env.encrypted", "rb") as encrypted_file:
    encrypted_data = encrypted_file.read()

# Decrypt and print the decrypted data
decrypted_data = decrypt_data(encrypted_data, key)
print("Decrypted Data:")
print(decrypted_data)
