# mongodb_utils.py - Database functions
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBConnection:
    """MongoDB connection manager"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance
    
    def get_client(self):
        if self._client is None:
            try:
                self._client = MongoClient("mongodb://localhost:27017/")
                # Test connection
                self._client.admin.command('ismaster')
                logger.info("Connected to MongoDB successfully")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        return self._client
    
    def close_connection(self):
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

def get_keywords_by_university(university_name, limit=20):
    """
    Get top keywords for faculty at a specific university
    
    Args:
        university_name (str): Name of the university to search
        limit (int): Maximum number of keywords to return
    
    Returns:
        tuple: (keywords_list, counts_list)
    """
    if not university_name or not university_name.strip():
        return [], []
    
    try:
        connection = MongoDBConnection()
        client = connection.get_client()
        db = client["academicworld"]
        faculty_collection = db["faculty"]
        
        # Use aggregation pipeline for better performance
        pipeline = [
            {
                "$match": {
                    "affiliation.name": {
                        "$regex": university_name.strip(), 
                        "$options": "i"
                    }
                }
            },
            {"$unwind": "$keywords"},
            {
                "$group": {
                    "_id": "$keywords.name",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        results = list(faculty_collection.aggregate(pipeline))
        
        if results:
            keywords = [doc["_id"] for doc in results]
            counts = [doc["count"] for doc in results]
            logger.info(f"Found {len(keywords)} keywords for university: {university_name}")
            return keywords, counts
        else:
            logger.info(f"No keywords found for university: {university_name}")
            return [], []
            
    except Exception as e:
        logger.error(f"Error querying keywords for university {university_name}: {e}")
        return [], []

def get_university_faculty_count(university_name):
    """
    Get the number of faculty members at a university
    
    Args:
        university_name (str): Name of the university
    
    Returns:
        int: Number of faculty members
    """
    try:
        connection = MongoDBConnection()
        client = connection.get_client()
        db = client["academicworld"]
        faculty_collection = db["faculty"]
        
        count = faculty_collection.count_documents({
            "affiliation.name": {
                "$regex": university_name.strip(), 
                "$options": "i"
            }
        })
        
        return count
        
    except Exception as e:
        logger.error(f"Error counting faculty for university {university_name}: {e}")
        return 0

def get_top_keywords(limit=25):
    """
    Return the most common faculty keywords in the MongoDB faculty collection.
    Used by Widget 1.
    """
    try:
        connection = MongoDBConnection()
        client = connection.get_client()
        db = client["academicworld"]
        faculty_collection = db["faculty"]

        pipeline = [
            {"$unwind": "$keywords"},
            {"$group": {"_id": "$keywords.name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]

        results = list(faculty_collection.aggregate(pipeline))
        keywords = [doc["_id"] for doc in results]
        counts = [doc["count"] for doc in results]
        return keywords, counts
    except Exception as e:
        logger.error(f"Error in get_top_keywords: {e}")
        return [], []
