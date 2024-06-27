from pymongo import MongoClient

def initialize_database():

    mongo_uri = 'mongodb://root:root@mongo:27017/'
    client = MongoClient(mongo_uri)
    db = client['votes_collectionnn']

  # Check if the collections already exist
    if 'votes_collectionnn' not in db.list_collection_names():
        # Create a collection for votes
        votes_collectionnn = db['votes_collectionnn']

    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()