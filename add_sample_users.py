import sqlite3
import random
from rich.console import Console

console = Console()
def add_reviews():
    users = [
        "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Isaac", "Jack",
        "Kelly", "Liam", "Mia", "Nathan", "Olivia", "Peter", "Quinn", "Rachel", "Samuel", "Tina",
        "Umar", "Victoria", "William", "Xander", "Yara", "Zane", "Aaron", "Bianca", "Carter", "Diana",
        "Elliot", "Fiona", "George", "Hazel", "Ian", "Jasmine", "Kevin", "Linda", "Mark", "Nina",
        "Oscar", "Paula", "Quincy", "Rita", "Steve", "Tracy", "Ursula", "Vince", "Wendy", "Xavier"
    ]
    
    media_titles = [
        "Inception", "Interstellar", "The Dark Knight", "Memento", "Titanic", "Avatar", "The Matrix",
        "Shutter Island", "Parasite", "Fight Club", "Breaking Bad", "Game of Thrones", "Friends",
        "Stranger Things", "The Witcher", "Sherlock", "The Office", "Money Heist", "Dark", "The Boys"
    ]
    
    comments = [
        "Amazing movie!", "Must watch!", "Really enjoyed it.", "Could have been better.",
        "One of my favorites!", "Overrated!", "Highly recommended!", "Best of all time!",
        "Would watch again.", "Not my cup of tea.", "Boring!", "Loved it!", "Top-class performance!",
        "Thrilling!", "Mind-blowing!", "Oscar-worthy!", "Underrated masterpiece!", "Just wow!",
        "Great direction!", "Storyline was amazing!"
    ]
    
    conn = sqlite3.connect("media_reviews.db")
    cursor = conn.cursor()
    
    for _ in range(50):
        user = random.choice(users)
        media = random.choice(media_titles)
        rating = random.randint(1, 5)
        comment = random.choice(comments)
        
        cursor.execute("""
            INSERT INTO reviews (user_id, media_id, rating, comment)
            VALUES (
                (SELECT id FROM users WHERE name = ?),
                (SELECT id FROM media WHERE title = ?),
                ?, ?
            )
        """, (user, media, rating, comment))
    
    conn.commit()
    conn.close()
    console.print("[green]50 reviews added successfully![/green]")