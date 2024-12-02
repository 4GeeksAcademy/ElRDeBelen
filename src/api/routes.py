"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Book, Author
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_jwt_extended import create_access_token

import os
import json

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


# Configuration       
cloudinary.config( 
    cloud_name = "dd0wschpy", 
    api_key = "278174897546864", 
    api_secret = os.getenv("CLOUDINARY_SECRET", ""), # Click 'View API Keys' above to copy your API secret
    secure=True
)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

@api.route('/users', methods=['GET'])
def get_all_users():

    user_list = User.query.all()

    serialized_users = [ item.serialize() for item in user_list ]

    return jsonify(serialized_users), 200

@api.route('/books', methods=['GET'])
def get_all_books():

    book_list = Book.query.order_by(Book.title.asc()).all()

    serialized_books = [ item.serialize() for item in book_list ]

    return jsonify(serialized_books), 200

@api.route('/authors', methods=['GET'])
def get_all_authors():

    authors = Author.query.all()
    serialized_authors = [ item.serialize() for item in authors ]
    return jsonify(serialized_authors), 200


@api.route('/authors/<int:id>', methods=['GET'])
def get_one_author(id):

    searched_author = Author.query.get(id)
    
    if searched_author != None:
        return jsonify(searched_author.serialize()), 200
    
    return jsonify({"error": "Author not found 🥲"}), 404
    
@api.route('/authors', methods=['POST'])
def add_new_author():

    try:
        body = request.json
        name = body.get('name')

        if not name:
            return jsonify({"error": "The 'name' field is required 🦹🏻‍♂️"}), 400

        new_author = Author()

        new_author.name = name
        
        db.session.add(new_author)
        db.session.commit()

        return jsonify(new_author.serialize()), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid JSON data: {str(e)}"}), 400
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

@api.route('/books/<int:id>', methods=['GET'])
def get_one_book(id):

    searched_book = Book.query.get(id) # None (Solo por id)

    if searched_book != None:
        return jsonify(searched_book.serialize()), 200
    
    return jsonify({"error": "Book not found 🥲"}), 404

@api.route('/books', methods=['POST'])
def add_new_book():

    try:

        title = request.form.get('title')
        author_id = request.form.get('author_id')

        if author_id == None:
            return jsonify({ "error" : "falta el campo author_id 🦹🏻‍♂️"}), 400

        searched_author = Author.query.get(author_id)

        if searched_author == None:
            return jsonify({ 
                "error" : f"El author con author_id {author_id} no se encuentra registrado 🦹🏻‍♂️"
            }), 404

        upload_result = None
        file = request.files.get('file')
        if file:
            upload_result = cloudinary.uploader.upload(file)

        else:
            return jsonify({ 
                "error" : f"Not file attached 🦹🏻‍♂️"
            }), 404
        
        new_book = Book(title=title, author=searched_author, image_url=upload_result["secure_url"])

        db.session.add(new_book) # Memoria RAM del server

        db.session.commit() # asigna el id a ese libro y lo guarda SQL
        serialized_book = new_book.serialize()
        
        return jsonify(serialized_book), 200
    
    except ValueError as e:
        # Handle specific ValueError exceptions, e.g., invalid JSON data
        return jsonify({"error": f"Invalid JSON data: {str(e)}"}), 400
    except Exception as e:
        # Log the error for debugging
        print(f"An unexpected error occurred: {str(e)}")
        # Return a generic error message to the user
        return jsonify({"error": "An error occurred while processing your request."}), 500
    

@api.route('/books/<int:book_id>', methods=['DELETE'])
def remove_book(book_id):
    book = Book.query.get(book_id)

    if book == None:
        return jsonify({ 
                "error" : f"El Libro con id {book_id} no se encuentra registrado 🦹🏻‍♂️"
            }), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({ "msg" : "Libro elmiminado con exito"}), 200


@api.route('/books/<int:book_id>', methods=['PUT'])
def edit_book(book_id):

    try:

        book = Book.query.get(book_id)

        if book == None:
            return jsonify({ 
                    "error" : f"El Libro con id {book_id} no se encuentra registrado 🦹🏻‍♂️"
                }), 404

        body = request.json
        new_title = body.get('title')
        
        book.title = new_title
        
        db.session.commit()

        return jsonify(book.serialize()), 200
    
    except Exception as e:
        # Log the error for debugging
        print(f"An unexpected error occurred: {str(e)}")
        # Return a generic error message to the user
        return jsonify({"error": "An error occurred while processing your request."}), 500


@api.route('/login', methods=['POST'])
def login():
    body = request.json
    email = body.get('email')
    password = body.get('password')

    if email == None or password == None:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email, password=password).first()

    if user is None or password != user.password:
        return jsonify({"error": "Invalid email or password"}), 401
    
    access_token = create_access_token(identity=user.email)

    return jsonify({
        "user": user.serialize(),
        "token": access_token
    }), 200