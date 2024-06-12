from pymongo import MongoClient

def initialize_database():

    mongo_uri = 'mongodb://root:root@mongo:27017/'
    client = MongoClient(mongo_uri)
    db = client['vote_database']

  # Check if the collections already exist
    if 'vote_database' not in db.list_collection_names():
        # Create a collection for votes
        votes_collection = db['vote_database']

    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()