from pymongo import MongoClient
from pymongo.erros import PyMongoError
import config

orders_collection = None
users_collection = None

try:
    client = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')

    db = client[config.DB_NAMENAME]
    orders_collection = db['orders']
    users_collection = db['users']

    users_collection.create_index('email', unique=True)
    users_collection.create_index('phone', unique=True)

    print('Connected to MONGODB')
except PyMongoError as e :
    print('error connecting to MONGODB:', e)