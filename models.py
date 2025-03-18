class User:
    def __init__(self, name):
        self.name = name

class Media:
    def __init__(self, title, media_type):
        self.title = title
        self.media_type = media_type

class Review:
    def __init__(self, user_id, media_id, rating, comment):
        self.user_id = user_id
        self.media_id = media_id
        self.rating = rating
        self.comment = comment
