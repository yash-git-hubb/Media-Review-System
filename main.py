import typer
from db import initialize_db
from rich.console import Console
from rich.table import Table
import ast
from db import get_reviews 


from logic import (
    add_user,
    add_media,
    list_users,
    list_media,
    add_review,
    list_reviews,
    get_recommendations,
    subscribe_user,
    search_media,
    get_top_rated_media,
    add_reviews_multithreaded,
    
)
app = typer.Typer()
console = Console()



@app.command("init")
def init():
    """Initialize the database"""
    initialize_db()
    typer.echo("Database initialized successfully.")

@app.command()
def create_user(name: str):
    """Add a new user"""
    add_user(name)

@app.command()
def create_media(title: str, media_type: str):
    """Add a new media entry (Movie, WebShow, Song)"""
    add_media(title, media_type)

@app.command("list-users")
def show_users():
    """List all users"""
    list_users()

@app.command("list")
def show_media():
    """List all media"""
    list_media()

@app.command()
def search_media_by_title(title: str):
    """Search for media by title."""
    search_media(title)

@app.command()
def review_media(user_id: int, media_id: int, rating: int, comment: str):
    """Command to allow users to review media based on user ID and media ID"""
    add_review(user_id, media_id, rating, comment)


@app.command()
def show_reviews():
    """List all reviews"""
    list_reviews()

import ast  # To safely parse the tuple string input


@app.command()
def top_rated(limit: int = 5):
    """Get the top-rated media based on reviews."""
    get_top_rated_media(limit)

@app.command()
def subscribe(user_name: str, media_title: str):
    """Subscribe a user to a media for notifications"""
    subscribe_user(user_name, media_title)

@app.command()
def recommend(user_id: int):
    """Get top 5 media recommendations for a user using their ID."""
    get_recommendations(user_id)

@app.command()
def bulk_review(reviews: str):
    """Add multiple reviews using multi-threading."""
    try:
        reviews_list = ast.literal_eval(reviews)  # Convert string input to list
        if not isinstance(reviews_list, list):
            raise ValueError
    except (SyntaxError, ValueError):
        console.print("[bold red]Invalid input format! Please provide a valid list of tuples.[/bold red]")
        return

    add_reviews_multithreaded(reviews_list)

@app.command()
def show_reviews_redis():
    """Fetch reviews using Redis as a cache store"""
    reviews = get_reviews()  # Fetch reviews (Redis or DB)

    table = Table(title="Media Reviews")
    table.add_column("User", style="cyan")
    table.add_column("Media", style="magenta")
    table.add_column("Rating", style="green")
    table.add_column("Comment", style="yellow")

    for user, media, rating, comment in reviews:
        table.add_row(user, media, str(rating), comment)

    console.print(table)

@app.command()
def add_sample_media():
    """Adds predefined media samples to the database."""
    sample_media =[
        ("Inception", "Movie"), ("Interstellar", "Movie"), ("The Dark Knight", "Movie"), 
        ("Memento", "Movie"), ("Titanic", "Movie"), ("Avatar", "Movie"), ("The Matrix", "Movie"),
        ("Shutter Island", "Movie"), ("Parasite", "Movie"), ("Fight Club", "Movie"),
        ("Breaking Bad", "WebShow"), ("Game of Thrones", "WebShow"), ("Friends", "WebShow"),
        ("Stranger Things", "WebShow"), ("The Witcher", "WebShow"), ("Sherlock", "WebShow"),
        ("The Office", "WebShow"), ("Money Heist", "WebShow"), ("Dark", "WebShow"), 
        ("The Boys", "WebShow"), ("Bohemian Rhapsody", "Song"), ("Shape of You", "Song"),
        ("Someone Like You", "Song"), ("Blinding Lights", "Song"), ("Uptown Funk", "Song"),
        ("Rolling in the Deep", "Song"), ("Let It Be", "Song"), ("Yesterday", "Song"),
        ("Hey Jude", "Song"), ("Despacito", "Song"), ("No Time to Die", "Song"),
        ("Havana", "Song"), ("Perfect", "Song"), ("Senorita", "Song"), ("Old Town Road", "Song"),
        ("Lose Yourself", "Song"), ("Rap God", "Song"), ("Smells Like Teen Spirit", "Song"),
        ("Wonderwall", "Song"), ("Bohemian Rhapsody", "Song"), ("Hotel California", "Song"),
        ("Sweet Child O' Mine", "Song"), ("Billie Jean", "Song"), ("Supernatural", "WebShow"),
        ("House of Cards", "WebShow"), ("The Mandalorian", "WebShow"), ("Westworld", "WebShow"),
        ("Black Mirror", "WebShow"), ("Narcos", "WebShow")
    ]

    for title, media_type in sample_media:
        add_media(title, media_type)

    typer.echo("Sample media added successfully!")

@app.command()
def add_sample_users():
    """Adds predefined users to the database."""
    sample_users =[
        "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Isaac", "Jack",
        "Kelly", "Liam", "Mia", "Nathan", "Olivia", "Peter", "Quinn", "Rachel", "Samuel", "Tina",
        "Umar", "Victoria", "William", "Xander", "Yara", "Zane", "Aaron", "Bianca", "Carter", "Diana",
        "Elliot", "Fiona", "George", "Hazel", "Ian", "Jasmine", "Kevin", "Linda", "Mark", "Nina",
        "Oscar", "Paula", "Quincy", "Rita", "Steve", "Tracy", "Ursula", "Vince", "Wendy", "Xavier"
    ]

    for name in sample_users:
        add_user(name)

    typer.echo("Sample users added successfully!")

@app.command()
def add_sample_reviews():
    """Adds predefined reviews to the database."""
    sample_reviews = [
    (1, 5, 5, "Absolutely amazing!"),
    (2, 12, 4, "Great movie, really enjoyed it."),
    (3, 8, 3, "It was decent, but not my favorite."),
    (4, 19, 2, "Too slow and boring."),
    (5, 27, 1, "Terrible! Would not recommend."),
    (6, 33, 5, "Loved every moment!"),
    (7, 14, 4, "Solid movie with a great story."),
    (8, 22, 3, "Not bad, but could've been better."),
    (9, 6, 2, "Disappointed, expected more."),
    (10, 41, 1, "Worst movie I've ever seen."),
    (11, 9, 5, "A masterpiece!"),
    (12, 35, 4, "Very entertaining and well-acted."),
    (13, 47, 3, "Average, nothing special."),
    (14, 3, 2, "Felt dragged, not engaging."),
    (15, 17, 1, "Poor execution and bad acting."),
    (16, 24, 5, "Brilliantly done, would watch again!"),
    (17, 28, 4, "Good visuals and story."),
    (18, 7, 3, "Meh, was okay."),
    (19, 39, 2, "Cliché and predictable."),
    (20, 13, 1, "Absolute waste of time."),
    (21, 45, 5, "Emotional and powerful!"),
    (22, 18, 4, "Great soundtrack and cinematography."),
    (23, 31, 3, "Just fine, nothing outstanding."),
    (24, 20, 2, "Characters were flat and uninteresting."),
    (25, 49, 1, "Horrible, regretted watching."),
    (26, 10, 5, "One of the best movies ever!"),
    (27, 21, 4, "Really well made."),
    (28, 40, 3, "Some parts were good, others not so much."),
    (29, 2, 2, "Weak plot, didn't keep me engaged."),
    (30, 15, 1, "Very bad storyline."),
    (31, 23, 5, "Superb acting and direction."),
    (32, 16, 4, "A fun experience!"),
    (33, 26, 3, "Not bad, but wouldn't watch again."),
    (34, 30, 2, "Expected more from this movie."),
    (35, 46, 1, "Ridiculously bad."),
    (36, 50, 5, "A perfect movie!"),
    (37, 48, 4, "Had some flaws, but overall good."),
    (38, 29, 3, "Mediocre at best."),
    (39, 4, 2, "Acting was weak."),
    (40, 42, 1, "A total mess."),
    (41, 34, 5, "So beautiful and touching."),
    (42, 37, 4, "Quite enjoyable!"),
    (43, 43, 3, "Could've been better."),
    (44, 25, 2, "Not my cup of tea."),
    (45, 36, 1, "Horribly written."),
    (46, 11, 5, "Perfect in every way!"),
    (47, 32, 4, "Loved the action scenes."),
    (48, 38, 3, "It was okay, not bad."),
    (49, 44, 2, "Forgettable."),
    (50, 1, 1, "Worst script ever."),
]

    for user, media, rating, comment in sample_reviews:
        review_media(user, media, rating, comment)

    typer.echo("Sample reviews added successfully!")


if __name__ == "__main__":
    app()
