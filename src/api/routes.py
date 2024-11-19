"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Book
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


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

    book_list = Book.query.all()

    serialized_books = [ item.serialize() for item in book_list ]

    return jsonify(serialized_books), 200

@api.route('/books/<int:id>', methods=['GET'])
def get_one_book(id):

    searched_book = Book.query.get(id) # None (Solo por id)

    if searched_book != None:
        return jsonify(searched_book.serialize()), 200
    
    return jsonify({"error": "Book not found 🥲"}), 404

@api.route('/books', methods=['POST'])
def add_new_book():

    try:

        body = request.json

        new_book = Book()

        new_book.title = body.get('title')

        db.session.add(new_book) # Memoria RAM del server

        db.session.commit() # asigna el id a ese libro y lo guarda SQL
        
        return jsonify(new_book.serialize()), 200
    
    except ValueError:
        
        return jsonify({"error": "Sorry something unexpected happened. 🧟"}), 500
         