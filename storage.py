import os
import json
# from cryptography.fernet import Fernet
from dotenv import load_dotenv
from tinydb import TinyDB, Query

# Load the environment variables from .env file
load_dotenv()

class SimpleStorage:
    def __init__(self, db_path: str = 'db.json'):
        assert db_path is not None and db_path.endswith('.json'), "db_path must be a valid path to a JSON file"

        if not os.path.exists(db_path):
            self.db = TinyDB(db_path)
        else:
            with open(db_path, 'w'):
                pass  # Just create the file
            self.db = TinyDB(db_path)

    def add_message(self, user_id: int, message: str):
        self.db.insert({'user_id': user_id, 'message': message})

    def get_messages(self, user_id: int):
        return self.db.search(Query().user_id == user_id)

    def clear_messages(self, user_id: int):
        self.db.remove(Query().user_id == user_id)

    def close(self):
        self.db.close()




# secret_key = os.getenv('SECRET_KEY').encode()  # Convert to bytes
# fernet = Fernet(secret_key)
# class EncryptedStorage:
#     def __init__(self, db_path: str = 'db.json'):
#         assert db_path is not None and db_path.endswith('.json'), "db_path must be a valid path to a JSON file"

#         self.db_path = db_path
#         if os.path.exists(db_path):
#             self._load_data()
#         else:
#             self.db = TinyDB(db_path)

#     def _load_data(self):
#         with open(self.db_path, 'rb') as file:
#             encrypted_data = file.read()  # Read the encrypted data
#             decrypted_data = fernet.decrypt(encrypted_data)  # Decrypt it
#             json_data = json.loads(decrypted_data)  # Load as JSON
#             self.db = TinyDB(self.db_path)
#             for item in json_data:
#                 self.db.insert(item)

#     def add_message(self, user_id: int, message: str):
#         self.db.insert({'user_id': user_id, 'message': message})

#     def get_messages(self, user_id: int):
#         return self.db.search(Query().user_id == user_id)

#     def clear_messages(self, user_id: int):
#         self.db.remove(Query().user_id == user_id)

#     def save_data(self):
#         # Save and encrypt the data before closing
#         data = self.db.all()  # Get all records
#         json_data = json.dumps(data, ensure_ascii=False).encode()  # Convert to JSON and encode

#         encrypted_data = fernet.encrypt(json_data)  # Encrypt the JSON data

#         with open(self.db_path, 'wb') as file:
#             file.write(encrypted_data)  # Write the encrypted data

#     def close(self):
#         self.save_data()  # Save changes and encrypt data
#         self.db.close()  # Close the TinyDB instance





# # Example Usage
# if __name__ == "__main__":
#     storage = EncryptedStorage('db.json')
#     storage.add_message(1, "Hello World!")
#     messages = storage.get_messages(1)
#     print(messages)
#     storage.clear_messages(1)
#     storage.close()
