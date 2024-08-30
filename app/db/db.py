from tinydb import TinyDB, Query

class TinyDBManager:
    def __init__(self, db_path='db.json'):
        """
        Initialize the connection to the TinyDB instance.
        
        :param db_path: Path to the JSON file that stores the TinyDB database.
        """
        self.db = TinyDB(db_path)
    
    def insert(self, document):
        """
        Insert a document into the TinyDB database.
        
        :param document: A dictionary representing the document to be inserted.
        :return: The document ID of the inserted document.
        """
        return self.db.insert(document)
    
    def get_all(self):
        """
        Retrieve all documents from the TinyDB database.
        
        :return: A list of all documents.
        """
        return self.db.all()
    
    def search(self, field, value):
        """
        Search for documents in the TinyDB database based on a specific field and value.
        
        :param field: The field to search on.
        :param value: The value to search for.
        :return: A list of documents that match the search criteria.
        """
        query = Query()
        return self.db.search(query[field] == value)
    
    def update(self, updates, field, value):
        """
        Update documents in the TinyDB database based on a specific field and value.
        
        :param updates: A dictionary representing the fields to update and their new values.
        :param field: The field to search on.
        :param value: The value to search for.
        :return: The number of updated documents.
        """
        query = Query()
        return self.db.update(updates, query[field] == value)
    
    def delete(self, field, value):
        """
        Delete documents from the TinyDB database based on a specific field and value.
        
        :param field: The field to search on.
        :param value: The value to search for.
        :return: The number of deleted documents.
        """
        query = Query()
        return self.db.remove(query[field] == value)
    
    def close(self):
        """
        Close the connection to the TinyDB database.
        """
        self.db.close()

# # Example usage:
# if __name__ == "__main__":
#     db_manager = TinyDBManager('example_db.json')
    
#     # Insert a document
#     doc_id = db_manager.insert({'name': 'John Doe', 'age': 30})
#     print(f"Inserted document ID: {doc_id}")
    
#     # Retrieve all documents
#     all_docs = db_manager.get_all()
#     print(f"All documents: {all_docs}")
    
#     # Search for a document
#     search_result = db_manager.search('name', 'John Doe')
#     print(f"Search result: {search_result}")
    
#     # Update a document
#     db_manager.update({'age': 31}, 'name', 'John Doe')
    
#     # Delete a document
#     db_manager.delete('name', 'John Doe')
    
#     # Close the database
#     db_manager.close()
