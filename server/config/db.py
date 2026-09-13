import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "test_db")


client=MongoClient(MONGO_URI)
db = client[DB_NAME]

# user collection
users_collection = db["users"]
# document collection
chunk_collection = db["text"]
# chat collection
chat_history_collection = db["chat_history"]
# quiz collection
quizzes_collection = db["quizzes"]
quiz_history = db["history"]