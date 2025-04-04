import sqlite3
from rich.console import Console
from rich.table import Table
from db import get_db_connection
from models import User, Media
from threading import *
from redis_cache import redis_client

console = Console()

def add_user(name):
    """Adds a user only if they do not already exist."""
    if not name.strip():
        console.print("[bold red]Error: User name cannot be empty![/bold red]")
        return

    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Check if the user already exists (case-insensitive)
        cursor.execute("SELECT id FROM users WHERE LOWER(name) = LOWER(?)", (name,))
        existing_user = cursor.fetchone()

        if existing_user:
            console.print(f"[bold yellow]Warning: User '{name}' already exists in the database![/bold yellow]")
            return

        # Insert new user
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        console.print(f"[bold green]User '{name}' added successfully![/bold green]")

    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
    finally:
        conn.close()


def add_media(title, media_type):
    """Adds media only if it does not already exist."""
    if not title.strip():
        console.print("[bold red]Error: Media title cannot be empty![/bold red]")
        return

    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Check if media already exists (case-insensitive)
        cursor.execute("SELECT id FROM media WHERE LOWER(title) = LOWER(?)", (title,))
        existing_media = cursor.fetchone()

        if existing_media:
            console.print(f"[bold yellow]Warning: Media '{title}' already exists in the database![/bold yellow]")
            return

        # Insert new media
        cursor.execute("INSERT INTO media (title, type) VALUES (?, ?)", (title, media_type))
        conn.commit()
        console.print(f"[bold green]Media '{title}' added successfully![/bold green]")

    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
    finally:
        conn.close()

def list_users():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users")
        users = cursor.fetchall()
    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
        return
    finally:
        conn.close()

    if not users:
        console.print("[bold yellow]No users found.[/bold yellow]")
        return

    table = Table(title="Users", show_header=True, header_style="bold blue")
    table.add_column("ID", justify="center")
    table.add_column("Name", justify="left")

    for user in users:
        table.add_row(str(user[0]), user[1])

    console.print(table)

def list_media():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, type FROM media")
        media_list = cursor.fetchall()
    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
        return
    finally:
        conn.close()

    if not media_list:
        console.print("[bold yellow]No media found.[/bold yellow]")
        return

    table = Table(title="Media", show_header=True, header_style="bold magenta")
    table.add_column("ID", justify="center")
    table.add_column("Title", justify="left")
    table.add_column("Type", justify="center")

    for media in media_list:
        table.add_row(str(media[0]), media[1], media[2])

    console.print(table)

def search_media(title: str):
    """Search for media by title (case-insensitive)."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        # Case-insensitive search using `LIKE`
        cursor.execute("SELECT id, title, type FROM media WHERE LOWER(title) LIKE LOWER(?)", (f"%{title}%",))
        results = cursor.fetchall()

        if not results:
            console.print(f"[bold yellow]No media found matching '{title}'.[/bold yellow]")
            return
        
        # Display results in a table
        table = Table(title="Search Results")
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Title", style="magenta", justify="left")
        table.add_column("Type", style="green", justify="left")

        for media_id, media_title, media_type in results:
            table.add_row(str(media_id), media_title, media_type)

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
    finally:
        conn.close()

from threading import Thread
console = Console()
review_lock = Lock()

def add_review(user_id: int, media_id: int, rating: int, comment: str):
    """Add a review with locking mechanism and Redis cache invalidation."""
    
    if not comment.strip():
        console.print("[bold red]Error: Comment cannot be empty![/bold red]")
        return

    if rating < 1 or rating > 5:
        console.print("[bold red]Error: Rating must be between 1 and 5.[/bold red]")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        with review_lock:  # Ensure thread-safe insertion
            cursor.execute("INSERT INTO reviews (user_id, media_id, rating, comment) VALUES (?, ?, ?, ?)", 
                           (user_id, media_id, rating, comment))
            conn.commit()
            console.print(f"[bold green]Review added for media ID {media_id} by user ID {user_id}![/bold green]")

        # Invalidate Redis cache
        redis_client.delete("reviews:all")

        review_details = f"User '{user_id}' reviewed '{media_id}' with Rating {rating}: {comment}"

        # Notify subscribers in a separate thread
        notification_thread = Thread(target=notify_subscribers, args=(media_id, review_details))
        notification_thread.start()

    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
    finally:
        conn.close()

def add_reviews_multithreaded(reviews):
    """Add multiple reviews using multi-threading."""
    
    threads = []
    for review in reviews:
        thread = Thread(target=add_review, args=review)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    console.print("[bold blue]All reviews added using multi-threading![/bold blue]")

def list_reviews():
    """Displays unique reviews from the database."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Fetch unique reviews using JOIN to get user names and media titles
        cursor.execute("""
            SELECT  users.name, media.title, reviews.rating, reviews.comment
            FROM reviews
            JOIN users ON reviews.user_id = users.id
            JOIN media ON reviews.media_id = media.id
        """)
        reviews = cursor.fetchall()

        if not reviews:
            console.print("[bold yellow]No reviews found![/bold yellow]")
            return

        table = Table(title="Unique Reviews")
        table.add_column("User", style="cyan", justify="left")
        table.add_column("Media", style="magenta", justify="left")
        table.add_column("Rating", style="green", justify="center")
        table.add_column("Comment", style="yellow", justify="left")

        for user, media, rating, comment in reviews:
            table.add_row(user, media, str(rating), comment)

        console.print(table)

    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
    finally:
        conn.close()




def get_top_rated_media(limit=5):
    """Fetch the top-rated media based on average review ratings."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        # Fetch media with their average rating
        cursor.execute("""
            SELECT media.id, media.title, media.type, 
                   COALESCE(AVG(reviews.rating), 0) AS avg_rating
            FROM media
            LEFT JOIN reviews ON media.id = reviews.media_id
            GROUP BY media.id
            ORDER BY avg_rating DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()

        if not results:
            console.print("[bold yellow]No media found with ratings.[/bold yellow]")
            return

        # Display results in a table
        table = Table(title="Top Rated Media")
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Title", style="magenta", justify="left")
        table.add_column("Type", style="green", justify="left")
        table.add_column("Avg Rating", style="yellow", justify="center")

        for media_id, title, media_type, avg_rating in results:
            table.add_row(str(media_id), title, media_type, f"{avg_rating:.2f}")

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
    finally:
        conn.close()


def subscribe_user(name, title):
    """Function to allow a user to subscribe to a media using names instead of IDs"""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Get user ID from name
        cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        user = cursor.fetchone()
        if not user:
            console.print(f"[bold red]Error: User '{name}' does not exist![/bold red]")
            return
        user_id = user[0]

        # Get media ID from title
        cursor.execute("SELECT id FROM media WHERE title = ?", (title,))
        media = cursor.fetchone()
        if not media:
            console.print(f"[bold red]Error: Media '{title}' does not exist![/bold red]")
            return
        media_id = media[0]

        # Subscribe the user to media
        cursor.execute("INSERT OR IGNORE INTO subscriptions (user_id, media_id) VALUES (?, ?)", 
                       (user_id, media_id))
        conn.commit()
        console.print(f"[bold green]User '{name}' subscribed to '{title}' successfully![/bold green]")

    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
    finally:
        conn.close()

from logger import logger

def notify_subscribers(media_id, review_details):
    """Function to log notifications for users who subscribed to a media"""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        # Get users who subscribed to this media
        cursor.execute("SELECT users.name FROM subscriptions JOIN users ON subscriptions.user_id = users.id WHERE subscriptions.media_id = ?", (media_id,))
        subscribers = cursor.fetchall()

        for subscriber in subscribers:
            user_name = subscriber[0]
            logger.info(f"Notification: User '{user_name}', a new review has been added for Media ID {media_id}.")
            logger.info(f"Review Details: {review_details}")

    except sqlite3.Error as e:
        logger.error(f"Notification Error: {e}")
    finally:
        conn.close()

def get_recommendations(user_id: int):
    """Fetch top 5 media recommendations based on rating and user subscriptions."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            console.print(f"[bold red]Error: User ID '{user_id}' does not exist![/bold red]")
            return
        user_name = user[0]

        # Get top-rated media (average rating)
        cursor.execute("""
            SELECT media.title, media.type, AVG(reviews.rating) as avg_rating
            FROM media
            LEFT JOIN reviews ON media.id = reviews.media_id
            GROUP BY media.id
            ORDER BY avg_rating DESC
            LIMIT 5
        """)
        top_rated = cursor.fetchall()

        # Get media the user is subscribed to
        cursor.execute("""
            SELECT media.title, media.type
            FROM media
            JOIN subscriptions ON media.id = subscriptions.media_id
            WHERE subscriptions.user_id = ?
        """, (user_id,))
        subscribed_media = cursor.fetchall()

        # Exclude media already reviewed by the user
        cursor.execute("""
            SELECT DISTINCT media.title
            FROM reviews
            JOIN media ON reviews.media_id = media.id
            WHERE reviews.user_id = ?
        """, (user_id,))
        reviewed_media = {row[0] for row in cursor.fetchall()}

        # Combine top-rated and subscribed media, removing duplicates
        recommended_media = []
        seen_titles = set()

        # Add top-rated media first
        for title, media_type, avg_rating in top_rated:
            if title not in reviewed_media and title not in seen_titles:
                recommended_media.append((title, media_type, round(avg_rating, 2)))
                seen_titles.add(title)

        # Add subscribed media (if not already in recommendations)
        for title, media_type in subscribed_media:
            if title not in reviewed_media and title not in seen_titles:
                recommended_media.append((title, media_type, None))  # No avg rating for subscribed media
                seen_titles.add(title)

        # Limit to top 5 recommendations
        recommended_media = recommended_media[:5]

        if not recommended_media:
            console.print(f"[bold yellow]No new recommendations for User ID {user_id} ({user_name}).[/bold yellow]")
            return

        # Display recommendations
        table = Table(title=f"Top 5 Recommendations for {user_name} (ID: {user_id})")
        table.add_column("Media", style="magenta", justify="left")
        table.add_column("Type", style="cyan", justify="left")
        table.add_column("Avg Rating", style="green", justify="center")

        for title, media_type, avg_rating in recommended_media:
            rating_display = str(avg_rating) if avg_rating is not None else "N/A"
            table.add_row(title, media_type, rating_display)

        console.print(table)

    except sqlite3.Error as e:
        console.print(f"[bold red]Database Error: {e}[/bold red]")
    finally:
        conn.close()



