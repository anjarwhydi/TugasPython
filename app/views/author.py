from http import HTTPStatus
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.logs.log import logger
from ..utils import db
from ..models.author import Author

author_ns = Namespace('authors', description='Author operations')

author_model = author_ns.model('Author', {
    'id': fields.Integer(readOnly=True),
    'name': fields.String(required=True),
})

@author_ns.route('')
class AuthorListResource(Resource):
    @author_ns.marshal_list_with(author_model)
    @author_ns.doc(responses={HTTPStatus.OK: 'Success'})
    @author_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self):
        try:
            authors = Author.query.all()
            logger.info(f"Data: {authors}")
            return authors, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Failed to retrieve authors', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @author_ns.expect(author_model, validate=True)
    @author_ns.doc(responses={HTTPStatus.CREATED: 'Created', HTTPStatus.BAD_REQUEST: 'Invalid input'})
    @author_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def post(self):
        try:
            data = request.json
            author = Author(name=data['name'])
            db.session.add(author)
            db.session.commit()
            logger.info(f"Data: {author}")
            return {'message': 'Author created successfully'}, HTTPStatus.CREATED
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to create author', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

@author_ns.route('/<int:id>')
class AuthorResource(Resource):
    @author_ns.marshal_with(author_model)
    @author_ns.doc(responses={HTTPStatus.OK: 'Success', HTTPStatus.NOT_FOUND: 'Author not found'})
    @author_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self, id):
        try:
            author = Author.query.get_or_404(id)
            logger.info(f"Data: {author}")
            return author, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Author not found', 'error': str(e)}, HTTPStatus.NOT_FOUND
    
    @author_ns.expect(author_model)
    @author_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def put(self, id):
        try:
            author = Author.query.get_or_404(id)
            data = request.json
            author.name = data['name']
            db.session.commit()
            logger.info(f"Data: {author}")
            return {'message': 'Author updated successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to update author', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @author_ns.doc(responses={HTTPStatus.NO_CONTENT: 'No Content', HTTPStatus.NOT_FOUND: 'Author not found'})
    @author_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def delete(self, id):
        try:
            author = Author.query.get_or_404(id)
            db.session.delete(author)
            db.session.commit()
            logger.info(f"Data: {author}")
            return {'message': 'Author deleted successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to delete author', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
