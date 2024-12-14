from cryptography.fernet import Fernet
import logging

# إعداد السجل
LOG_FILE = 'decrypt_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def decrypt_data(encrypted_data, key):
    """فك تشفير البيانات باستخدام Fernet."""
    try:
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        logging.info(f"[INFO] Data decrypted successfully.")
        return decrypted_data
    except Exception as e:
        logging.error(f"[ERROR] Error decrypting data: {e}")
        raise

def main():
    encrypted_data = input("Enter the encrypted data to decrypt: ").encode()
    key = input("Enter the decryption key: ").encode()

    try:
        decrypted_data = decrypt_data(encrypted_data, key)
        print(f"Decrypted Data: {decrypted_data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
