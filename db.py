import sqlite3
import redis
import json
from redis_cache import redis_client

def get_db_connection():
    try:
        return sqlite3.connect("media_reviews.db")
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def initialize_db():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('Movie', 'WebShow', 'Song'))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                media_id INTEGER NOT NULL,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                comment TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (media_id) REFERENCES media(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                media_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (media_id) REFERENCES media(id),
                UNIQUE(user_id, media_id) -- Prevent duplicate subscriptions
            )
        """)

        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()
        
def fetch_reviews_from_db():
    """Fetch reviews from SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT users.name, media.title, reviews.rating, reviews.comment 
        FROM reviews 
        JOIN users ON reviews.user_id = users.id 
        JOIN media ON reviews.media_id = media.id
    """)
    
    reviews = cursor.fetchall()  # List of tuples [(user, media, rating, comment), ...]
    conn.close()
    
    return reviews
def get_reviews():
    """Get reviews from Redis if available, otherwise fetch from DB and cache it"""
    cache_key = "reviews"
    
    # Check if data exists in Redis
    cached_reviews = redis_client.get(cache_key)
    
    if cached_reviews:
        print("Fetching reviews from Redis cache...")
        return json.loads(cached_reviews)
    
    print("Fetching reviews from Database...")
    reviews = fetch_reviews_from_db()
    
    # Store in Redis with an expiry of 1 hour 
    redis_client.setex(cache_key, 3600, json.dumps(reviews))
    
    return reviews