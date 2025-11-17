# mongodb_utils.py - Cloud-safe MongoDB functions
from pymongo import MongoClient
import logging, os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBConnection:
    """MongoDB connection manager with cloud-safe fallback"""
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def get_client(self):
        """Get MongoDB client; return None if unavailable."""
        if self._client is None:
            try:
                # Use environment variable first (Render), fallback to localhost
                mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
                self._client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
                self._client.admin.command("ping")  # test connection
                logger.info("✅ Connected to MongoDB successfully")
            except Exception as e:
                logger.warning(f"⚠️ MongoDB not available: {e}")
                self._client = None
        return self._client

    def close_connection(self):
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

# ---------------- Core query functions ---------------- #

def get_keywords_by_university(university_name, limit=20):
    """Get top keywords for faculty at a specific university."""
    if not university_name or not university_name.strip():
        return [], []

    try:
        connection = MongoDBConnection()
        client = connection.get_client()
        if not client:
            return [], []

        db = client["academicworld"]
        faculty_collection = db["faculty"]

        pipeline = [
            {"$match": {"affiliation.name": {"$regex": university_name.strip(), "$options": "i"}}},
            {"$unwind": "$keywords"},
            {"$group": {"_id": "$keywords.name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]

        results = list(faculty_collection.aggregate(pipeline))
        if results:
            keywords = [doc["_id"] for doc in results]
            counts = [doc["count"] for doc in results]
            logger.info(f"Found {len(keywords)} keywords for {university_name}")
            return keywords, counts
        return [], []
    except Exception as e:
        logger.error(f"Error querying keywords for university {university_name}: {e}")
        return [], []

def get_university_faculty_count(university_name):
    """Get number of faculty members at a university."""
    try:
        connection = MongoDBConnection()
        client = connection.get_client()
        if not client:
            return 0

        db = client["academicworld"]
        faculty_collection = db["faculty"]
        return faculty_collection.count_documents({
            "affiliation.name": {"$regex": university_name.strip(), "$options": "i"}
        })
    except Exception as e:
        logger.error(f"Error counting faculty for {university_name}: {e}")
        return 0

def get_top_keywords(limit=25):
    """Return most common faculty keywords (Widget 1)."""
    try:
        connection = MongoDBConnection()
        client = connection.get_client()
        if not client:
            return [], []

        db = client["academicworld"]
        faculty_collection = db["faculty"]

        pipeline = [
            {"$unwind": "$keywords"},
            {"$group": {"_id": "$keywords.name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        results = list(faculty_collection.aggregate(pipeline))
        return [doc["_id"] for doc in results], [doc["count"] for doc in results]
    except Exception as e:
        logger.error(f"Error in get_top_keywords: {e}")
        return [], []
