import typer
from db import initialize_db
from rich.console import Console
from rich.table import Table
import ast


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
    get_reviews
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
    """Fetch and display reviews (Uses Redis cache)."""
    reviews = get_reviews()
    
    if not reviews:
        console.print("[bold yellow]No reviews available.[/bold yellow]")
        return

    table = Table(title="Reviews")
    table.add_column("User", style="magenta")
    table.add_column("Media", style="cyan")
    table.add_column("Rating", style="green")
    table.add_column("Comment", style="yellow")

    for user, media, rating, comment in eval(reviews):  # Convert string to list
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
    sample_reviews = [("Alice", "Inception", 5, "Amazing movie!"),
        ("Bob", "Inception", 4, "Pretty good"),
        ("Charlie", "Breaking Bad", 5, "Best TV series ever!"),
        ("David", "The Matrix", 5, "Mind-blowing sci-fi classic!"),
        ("Emma", "Interstellar", 5, "A masterpiece of space and time!"),
        ("Frank", "The Matrix", 4, "Great visuals, complex story."),
        ("Grace", "Inception", 4, "On second watch, still great!"),
        ("Henry", "Breaking Bad", 5, "Brilliant writing and acting!"),
        ("Isabella", "Interstellar", 5, "Emotional and scientifically deep!"),
        ("Jack", "The Matrix", 5, "Revolutionary sci-fi film!"),
        ("Kelly", "Titanic", 5, "A heartbreaking love story."),
        ("Liam", "Avatar", 4, "Visually stunning but predictable plot."),
        ("Mia", "Fight Club", 5, "An absolute cult classic!"),
        ("Nathan", "The Dark Knight", 5, "Best portrayal of Joker ever!"),
        ("Olivia", "The Office", 5, "Funniest show I've ever watched."),
        ("Peter", "Game of Thrones", 4, "Loved it except for the last season."),
        ("Quinn", "Sherlock", 5, "Benedict Cumberbatch nailed it!"),
        ("Rachel", "Friends", 5, "Timeless sitcom, always fun!"),
        ("Samuel", "Money Heist", 4, "Gripping but dragged in later seasons."),
        ("Tina", "Stranger Things", 5, "Superb nostalgia and sci-fi mix."),
        ("Umar", "Dark", 5, "Mind-bending time travel plot!"),
        ("Victoria", "The Boys", 5, "A fresh take on superheroes!"),
        ("William", "Bohemian Rhapsody", 5, "A fitting tribute to Freddie Mercury!"),
        ("Xander", "Shape of You", 4, "Catchy but overplayed."),
        ("Yara", "Someone Like You", 5, "Adele's voice is just magical."),
        ("Zane", "Blinding Lights", 5, "Synthwave perfection."),
        ("Aaron", "Uptown Funk", 4, "Great song to dance to!"),
        ("Bianca", "Rolling in the Deep", 5, "Powerful vocals and deep lyrics."),
        ("Carter", "Let It Be", 5, "Timeless classic."),
        ("Diana", "Hey Jude", 5, "One of The Beatles' best songs."),
        ("Elliot", "Despacito", 4, "Catchy and international hit."),
        ("Fiona", "No Time to Die", 5, "Hauntingly beautiful James Bond theme."),
        ("George", "Havana", 4, "Great Latin pop song."),
        ("Hazel", "Perfect", 5, "A beautiful wedding song."),
        ("Ian", "Senorita", 5, "Shawn and Camila's chemistry is great."),
        ("Jasmine", "Old Town Road", 4, "Weird but surprisingly good!"),
        ("Kevin", "Lose Yourself", 5, "Eminems best track!"),
        ("Linda", "Rap God", 5, "Fastest rap ever, insane flow!"),
        ("Mark", "Smells Like Teen Spirit", 5, "Grunge at its peak."),
        ("Nina", "Wonderwall", 5, "Oasis best song!"),
        ("Oscar", "Bohemian Rhapsody", 5, "A rock opera masterpiece."),
        ("Paula", "Hotel California", 5, "An all-time classic rock song."),
        ("Quincy", "Sweet Child O' Mine", 5, "Slashs guitar solo is legendary."),
        ("Rita", "Billie Jean", 5, "Michael Jackson at his best."),
        ("Steve", "Supernatural", 4, "Great series, but dragged on too long."),
        ("Tracy", "House of Cards", 5, "Brilliant political drama."),
        ("Ursula", "The Mandalorian", 5, "Star Wars done right!"),
        ("Vince", "Westworld", 4, "Intriguing but got too complicated."),
        ("Wendy", "Black Mirror", 5, "Each episode is mind-blowing."),
        ("Xavier", "Narcos", 5, "Pablo Escobars story is gripping!"),
    ]

    for user, media, rating, comment in sample_reviews:
        review_media(user, media, rating, comment)

    typer.echo("Sample reviews added successfully!")


if __name__ == "__main__":
    app()
