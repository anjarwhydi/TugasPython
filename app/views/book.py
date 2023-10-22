from http import HTTPStatus
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.logs.log import logger

from ..utils import db
from ..models.book import Book

book_ns = Namespace('books', description='Book operations')

book_model = book_ns.model('Book', {
    'id': fields.Integer(readOnly=True),
    'title': fields.String(required=True),
    'author_id': fields.Integer(required=True, description='Author ID')
})

@book_ns.route('')
class BookListResource(Resource):
    @book_ns.marshal_list_with(book_model)
    @book_ns.doc(responses={HTTPStatus.OK: 'Success'})
    @book_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self):
        try:
            books = Book.query.all()
            logger.info(f"Data: {books}")
            return books, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Failed to retrieve books', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @book_ns.expect(book_model, validate=True)
    @book_ns.doc(responses={HTTPStatus.CREATED: 'Created', HTTPStatus.BAD_REQUEST: 'Invalid input'})
    @book_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def post(self):
        try:
            data = request.json
            book = Book(title=data['title'], author_id=data['author_id'])
            db.session.add(book)
            db.session.commit()
            logger.info(f"Data: {book}")
            return {'message': 'Book created successfully'}, HTTPStatus.CREATED
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to create book', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

@book_ns.route('/<int:id>')
class BookResource(Resource):
    @book_ns.marshal_with(book_model)
    @book_ns.doc(responses={HTTPStatus.OK: 'Success', HTTPStatus.NOT_FOUND: 'Book not found'})
    @book_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self, id):
        try:
            book = Book.query.get_or_404(id)
            logger.info(f"Data: {book}")
            return book, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Book not found', 'error': str(e)}, HTTPStatus.NOT_FOUND

    @book_ns.expect(book_model)
    @book_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def put(self, id):
        try:
            book = Book.query.get_or_404(id)
            data = request.json
            book.title = data['title']
            book.author_id = data['author_id']
            db.session.commit()
            logger.info(f"Data: {book}")
            return {'message': 'Book updated successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to update book', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @book_ns.doc(responses={HTTPStatus.NO_CONTENT: 'No Content', HTTPStatus.NOT_FOUND: 'Book not found'})
    @book_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def delete(self, id):
        try:
            book = Book.query.get_or_404(id)
            db.session.delete(book)
            db.session.commit()
            logger.info(f"Data: {book}")
            return {'message': 'Book deleted successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to delete book', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
