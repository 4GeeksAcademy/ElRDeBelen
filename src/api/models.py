from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    
    full_name = db.Column(db.String(260), unique=False, nullable=False)

    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name
            # do not serialize the password, its a security breach
        }

class Author(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=False, nullable=False)
    books = db.relationship("Book", back_populates="author")

    def __repr__(self):
        return f'<Author {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Book(db.Model):

    __tablename__ = 'libros' # para dar nombre a la tabla en psql

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(180), nullable=False)

    # author = Es probable otra table
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship("Author", back_populates='books')

    def __repr__(self):
        return f'<Book {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author.serialize() if self.author != None else "Unknown"
        }