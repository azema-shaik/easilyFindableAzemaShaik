class GenreNotExists(Exception):
    def __init__(self, genre):
        self.genre = genre

    def __str__(self):
        return f'{self.genre} does not exist'

    def __repr__(self):
        return f'GenreNotExists("{self.genre!r} does not exist")'